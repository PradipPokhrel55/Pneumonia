from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Basic knowledge base about pneumonia
docs = [
    "Pneumonia is an infection that inflames the air sacs in one or both lungs.",
    "The alveoli may fill with fluid or pus, causing cough, fever, chills, and difficulty breathing.",
    "Bacterial pneumonia is commonly caused by Streptococcus pneumoniae and Haemophilus influenzae.",
    "Viral pneumonia can be caused by influenza virus, RSV, or SARS-CoV-2.",
    "Fungal pneumonia occurs more often in people with weakened immune systems.",
    "Symptoms of pneumonia include cough, fever, chills, chest pain, fatigue, and shortness of breath.",
    "Risk factors include age below 2 or above 65, chronic diseases, smoking, and weak immunity.",
    "Diagnosis involves chest X-ray, blood tests, sputum tests, and physical examination.",
    "Treatment depends on the cause: antibiotics for bacterial, antivirals for viral, and antifungals for fungal pneumonia.",
    "Vaccination, good hygiene, and a healthy lifestyle help prevent pneumonia.",
    "Complications of pneumonia include respiratory failure, sepsis, lung abscess, and pleural effusion."
]

# Encode and store in FAISS
embeddings = model.encode(docs)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

def retrieve(query, k=2):
    """Retrieve top-k relevant docs"""
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k)
    return [docs[i] for i in I[0]]

def generate_answer(query):
    """Simplified RAG: retrieve + concatenate"""
    retrieved_docs = retrieve(query)
    context = " ".join(retrieved_docs)
    return f"Q: {query}\nContext: {context}\nAnswer: (Here an LLM would generate response)"


