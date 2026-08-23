import re

from ml.rag import retrieve_chunks


def _split_sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _query_terms(query: str):
    return set(re.findall(r"[a-z0-9]+", query.lower()))


def _is_answer_sentence(sentence: str) -> bool:
    normalized = sentence.lower()
    if len(sentence) < 45 or "pico" in normalized:
        return False
    if sentence.endswith("?") or normalized.startswith(("what ", "how ", "which ", "does ", "is ")):
        return False
    return True


def _is_relevant_chunk(query: str, chunk: dict) -> bool:
    query_terms = _query_terms(query)
    section = chunk.get("section", "").lower()
    text = chunk["text"].lower()
    if "pico" in section or "pico question" in text:
        return False
    if "pneumonia" in query_terms:
        if "pneumonia" not in text:
            return False
        if "dysentery" in text or "diarrhoea" in text:
            return False
    return True


def _best_sentences(query: str, chunks, max_sentences: int = 4):
    terms = _query_terms(query)
    meaningful_terms = terms - {"a", "an", "are", "for", "how", "in", "is", "of", "the", "to", "what"}
    candidates = []
    for chunk in chunks:
        if not _is_relevant_chunk(query, chunk):
            continue
        for sentence in _split_sentences(chunk["text"]):
            if not _is_answer_sentence(sentence):
                continue
            sent_terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            meaningful_overlap = len(meaningful_terms & sent_terms)
            if meaningful_overlap < min(2, len(meaningful_terms)):
                continue
            score = meaningful_overlap + (0.3 * chunk.get("score", 0.0))
            if any(term in sentence.lower() for term in ("recommend", "treat", "refer", "antibiotic", "danger sign")):
                score += 1
            candidates.append((score, sentence, chunk))

    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = []
    seen = set()
    for _, sentence, chunk in candidates:
        key = sentence.lower()
        if key in seen:
            continue
        selected.append((sentence, chunk))
        seen.add(key)
        if len(selected) >= max_sentences:
            break
    return selected


def generate_answer_with_sources(query: str):
    chunks = retrieve_chunks(query, k=6)
    if not chunks:
        return {
            "answer": "I could not find relevant evidence in the guideline for that question.",
            "citations": [],
        }

    selected = _best_sentences(query, chunks)
    if selected:
        answer_body = " ".join(sentence for sentence, _ in selected)
    else:
        answer_body = " ".join(chunk["text"] for chunk in chunks[:2])

    answer = f"Based on the WHO pneumonia and diarrhoea guideline: {answer_body}".strip()

    citation_map = {}
    citation_chunks = [chunk for _, chunk in selected] or [
        chunk for chunk in chunks if _is_relevant_chunk(query, chunk)
    ][:2]
    for chunk in citation_chunks:
        key = (chunk["page"], chunk["section"])
        if key in citation_map:
            continue
        citation_map[key] = {
            "page": chunk["page"],
            "section": chunk["section"],
            "snippet": chunk["text"][:220],
        }

    return {
        "answer": answer,
        "citations": list(citation_map.values())[:4],
    }


def generate_answer(query: str) -> str:
    """Backward-compatible API for MCP and existing callers."""
    return generate_answer_with_sources(query)["answer"]


