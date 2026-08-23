import json
import math
import re
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer


PDF_PATH = Path(__file__).resolve().parents[1] / "pneumonia_pdf.pdf"
OCR_DPI = 220
PARENT_CHARS = 1500
CHILD_CHARS = 420
CHILD_OVERLAP = 80
TOP_CANDIDATES = 30


@dataclass
class Chunk:
    chunk_id: str
    text: str
    page: int
    section: str
    parent_id: str


_model = None
_index = None
_chunks = []
_chunk_embeddings = None
_tfidf_vectorizer = None
_tfidf_matrix = None
_bm25_doc_lens = []
_bm25_tf = []
_bm25_df = Counter()
_bm25_avg_len = 0.0
_tokenized_docs = []
_lock = Lock()


def _tokenize(text: str):
    return re.findall(r"[a-z0-9]+", text.lower())


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _is_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 4 or len(line) > 120:
        return False
    if line.endswith("."):
        return False
    if re.search(r"\d{4}", line):
        return False
    alpha = sum(ch.isalpha() for ch in line)
    if alpha < 3:
        return False
    words = line.split()
    title_like = sum(1 for w in words if w[:1].isupper()) >= max(1, len(words) // 2)
    all_caps = line == line.upper()
    return title_like or all_caps


def _split_parent_chunks(text: str):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]
    chunks = []
    current = ""
    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) <= PARENT_CHARS:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(para) <= PARENT_CHARS:
            current = para
        else:
            for i in range(0, len(para), PARENT_CHARS):
                chunks.append(para[i:i + PARENT_CHARS])
            current = ""
    if current:
        chunks.append(current)
    return chunks


def _split_child_chunks(text: str):
    text = _normalize_whitespace(text)
    if not text:
        return []
    result = []
    start = 0
    while start < len(text):
        end = min(len(text), start + CHILD_CHARS)
        chunk = text[start:end]
        # Snap to sentence boundary when possible.
        if end < len(text):
            period = chunk.rfind(".")
            if period > CHILD_CHARS * 0.55:
                end = start + period + 1
                chunk = text[start:end]
        result.append(chunk.strip())
        if end >= len(text):
            break
        start = max(start + 1, end - CHILD_OVERLAP)
    return [c for c in result if c]


def _run_cmd(command):
    return subprocess.run(command, check=True, capture_output=True, text=True)


def _get_page_count(pdf_path: Path) -> int:
    command = [
        "gs",
        "-q",
        "-dNOSAFER",
        "-dNODISPLAY",
        "-c",
        f"({pdf_path}) (r) file runpdfbegin pdfpagecount = quit",
    ]
    out = _run_cmd(command).stdout.strip()
    return int(out)


def _ocr_page(pdf_path: Path, page: int) -> str:
    with tempfile.TemporaryDirectory(prefix="rag_pdf_") as tmp_dir:
        image_path = Path(tmp_dir) / f"page_{page}.png"
        gs_command = [
            "gs",
            "-q",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pnggray",
            f"-r{OCR_DPI}",
            f"-dFirstPage={page}",
            f"-dLastPage={page}",
            f"-sOutputFile={image_path}",
            str(pdf_path),
        ]
        _run_cmd(gs_command)
        tess_command = ["tesseract", str(image_path), "stdout", "--dpi", str(OCR_DPI)]
        text = _run_cmd(tess_command).stdout
    return text


def _load_or_build_page_text(pdf_path: Path):
    cache_file = pdf_path.with_suffix(".ocr_cache.json")
    if cache_file.exists() and cache_file.stat().st_mtime >= pdf_path.stat().st_mtime:
        with cache_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    page_count = _get_page_count(pdf_path)
    pages = []
    current_section = "General"
    for page_num in range(1, page_count + 1):
        raw_text = _ocr_page(pdf_path, page_num)
        raw_text = raw_text.replace("\x0c", " ")
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]

        for line in lines[:3]:
            if _is_heading(line):
                current_section = line
                break

        text = "\n".join(lines)
        pages.append(
            {
                "page": page_num,
                "section": current_section,
                "text": text,
            }
        )

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=True)
    return pages


def _build_chunks(pdf_path: Path):
    pages = _load_or_build_page_text(pdf_path)
    chunks = []
    child_counter = 0
    for page_info in pages:
        page = page_info["page"]
        section = page_info["section"]
        text = page_info["text"]
        if len(text.strip()) < 35:
            continue

        parent_chunks = _split_parent_chunks(text)
        for p_idx, parent_text in enumerate(parent_chunks):
            parent_id = f"p{page}_parent{p_idx}"
            child_chunks = _split_child_chunks(parent_text)
            for child_text in child_chunks:
                chunk = Chunk(
                    chunk_id=f"c{child_counter}",
                    text=child_text,
                    page=page,
                    section=section,
                    parent_id=parent_id,
                )
                chunks.append(chunk)
                child_counter += 1
    return chunks


def _build_bm25_state(chunks):
    global _bm25_doc_lens, _bm25_tf, _bm25_df, _bm25_avg_len, _tokenized_docs
    _bm25_doc_lens = []
    _bm25_tf = []
    _bm25_df = Counter()
    _tokenized_docs = []

    for chunk in chunks:
        tokens = _tokenize(chunk.text)
        tf = Counter(tokens)
        _tokenized_docs.append(tokens)
        _bm25_tf.append(tf)
        _bm25_doc_lens.append(len(tokens))
        for token in tf.keys():
            _bm25_df[token] += 1

    _bm25_avg_len = (sum(_bm25_doc_lens) / len(_bm25_doc_lens)) if _bm25_doc_lens else 0.0


def _bm25_scores(query: str):
    if not _chunks:
        return np.array([], dtype=np.float32)
    tokens = _tokenize(query)
    if not tokens:
        return np.zeros(len(_chunks), dtype=np.float32)

    n_docs = len(_chunks)
    k1 = 1.2
    b = 0.75
    scores = np.zeros(n_docs, dtype=np.float32)

    for i, tf_counter in enumerate(_bm25_tf):
        dl = _bm25_doc_lens[i]
        denom_norm = k1 * (1 - b + b * (dl / (_bm25_avg_len + 1e-9)))
        for token in tokens:
            tf = tf_counter.get(token, 0)
            if tf == 0:
                continue
            df = _bm25_df.get(token, 0)
            idf = math.log(1 + ((n_docs - df + 0.5) / (df + 0.5)))
            score = idf * (tf * (k1 + 1)) / (tf + denom_norm)
            scores[i] += score
    return scores


def _ensure_loaded():
    global _model, _index, _chunks, _chunk_embeddings, _tfidf_vectorizer, _tfidf_matrix
    if _chunks and ((_model is not None and _index is not None) or (_tfidf_vectorizer is not None and _tfidf_matrix is not None)):
        return

    with _lock:
        if _chunks and ((_model is not None and _index is not None) or (_tfidf_vectorizer is not None and _tfidf_matrix is not None)):
            return

        if not PDF_PATH.exists():
            raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

        _chunks = _build_chunks(PDF_PATH)
        if not _chunks:
            raise RuntimeError("No chunks were built from the pneumonia PDF.")

        texts = [c.text for c in _chunks]
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            embeddings = _model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            _chunk_embeddings = embeddings.astype(np.float32)

            _index = faiss.IndexFlatL2(_chunk_embeddings.shape[1])
            _index.add(_chunk_embeddings)
        except Exception:
            # Offline fallback when model download is unavailable.
            _model = None
            _index = None
            _chunk_embeddings = None
            _tfidf_vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r"[a-zA-Z0-9]+")
            _tfidf_matrix = _tfidf_vectorizer.fit_transform(texts)

        _build_bm25_state(_chunks)


def retrieve_chunks(query: str, k: int = 6):
    """Hybrid retrieve chunks with citations (page, section)."""
    _ensure_loaded()

    dense_k = min(max(k * 8, 20), len(_chunks))
    dense_rank = {}
    rerank_scores = {}

    if _model is not None and _index is not None and _chunk_embeddings is not None:
        query_vec = _model.encode([query], convert_to_numpy=True).astype(np.float32)
        _, dense_idx = _index.search(query_vec, dense_k)
        for rank, idx in enumerate(dense_idx[0], start=1):
            dense_rank[int(idx)] = rank
    elif _tfidf_vectorizer is not None and _tfidf_matrix is not None:
        tfidf_query = _tfidf_vectorizer.transform([query])
        tfidf_scores = (_tfidf_matrix @ tfidf_query.T).toarray().ravel()
        tfidf_idx = np.argsort(-tfidf_scores)[:dense_k]
        for rank, idx in enumerate(tfidf_idx, start=1):
            dense_rank[int(idx)] = rank
            rerank_scores[int(idx)] = float(tfidf_scores[idx])

    sparse_scores = _bm25_scores(query)
    sparse_idx = np.argsort(-sparse_scores)[:dense_k]
    sparse_rank = {int(idx): rank for rank, idx in enumerate(sparse_idx, start=1)}

    candidates = set(dense_rank.keys()) | set(sparse_rank.keys())
    fused = []
    for idx in candidates:
        rank_dense = dense_rank.get(idx, 10_000)
        rank_sparse = sparse_rank.get(idx, 10_000)
        rrf = (1.0 / (60 + rank_dense)) + (1.0 / (60 + rank_sparse))
        fused.append((idx, rrf))

    fused.sort(key=lambda x: x[1], reverse=True)
    top_candidates = [idx for idx, _ in fused[:TOP_CANDIDATES]]

    if _model is not None and _chunk_embeddings is not None:
        query_vec = _model.encode([query], convert_to_numpy=True).astype(np.float32)
        cand_emb = _chunk_embeddings[top_candidates]
        q = query_vec[0]
        q_norm = np.linalg.norm(q) + 1e-9
        doc_norm = np.linalg.norm(cand_emb, axis=1) + 1e-9
        cos = np.dot(cand_emb, q) / (doc_norm * q_norm)
        reranked = list(zip(top_candidates, cos))
    else:
        reranked = [(idx, rerank_scores.get(idx, 0.0)) for idx in top_candidates]

    reranked.sort(key=lambda x: x[1], reverse=True)

    result = []
    for idx, score in reranked[:k]:
        chunk = _chunks[idx]
        result.append(
            {
                "text": chunk.text,
                "page": chunk.page,
                "section": chunk.section,
                "chunk_id": chunk.chunk_id,
                "parent_id": chunk.parent_id,
                "score": float(score),
            }
        )
    return result


def retrieve_docs(query: str, k: int = 3):
    """Backward-compatible helper that returns only text chunks."""
    return [c["text"] for c in retrieve_chunks(query, k=k)]