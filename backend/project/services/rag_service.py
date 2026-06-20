from ml.rag import retrieve_docs
from transformers import pipeline
from threading import Lock


_qa_pipeline = None
_qa_lock = Lock()

def _get_pipeline():
    global _qa_pipeline
    if _qa_pipeline is not None:
        return _qa_pipeline
    with _qa_lock:
        if _qa_pipeline is not None:
            return _qa_pipeline
        _qa_pipeline = pipeline("text-generation", model="gpt2")
        return _qa_pipeline


def _extract_answer(prompt: str, generated_text: str) -> str:
    if generated_text.startswith(prompt):
        answer = generated_text[len(prompt):].strip()
    else:
        answer = generated_text.split("Answer:")[-1].strip()

    clean_lines = [
        line for line in answer.splitlines()
        if not line.strip().startswith(("Q:", "Context:", "Answer:"))
    ]
    return " ".join(clean_lines).strip()


def generate_answer(query: str) -> str:
    docs = retrieve_docs(query)
    context = " ".join(docs)
    prompt = f"""
Q: {query}
Context: {context}
Answer:
"""
    pipe = _get_pipeline()
    generated_text = pipe(prompt, max_new_tokens=150)[0]["generated_text"]
    return _extract_answer(prompt, generated_text)


