# src/llm/llm_client.py

import os
import requests
from typing import List

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"  # ou pro si tu veux


def generate_answer(context_chunks: List[str], question: str) -> str:
    """
    Construit un prompt RAG simple à partir des chunks + question,
    puis appelle Gemini via l'API REST.
    """

    if GEMINI_API_KEY is None:
        raise RuntimeError("GEMINI_API_KEY non défini dans les variables d'environnement.")

    # Contexte concaténé (tu pourras faire mieux plus tard)
    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""
You are an internal model validation expert for ICAAP.

You receive:
1) Context from previous audit reports, modelling documentation and regulation extracts.
2) A user question.

You must answer ONLY based on the context, in a clear, structured, professional style.

Context:
{context_text}

Question:
{question}

Answer in English, with clear paragraphs and no bullet points unless strictly necessary.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # extraction naïve du texte (tu ajusteras si besoin)
    return data["candidates"][0]["content"]["parts"][0]["text"]
