# src/llm/llm_client.py

import os
from typing import List

import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    raise RuntimeError("GEMINI_API_KEY non défini dans les variables d'environnement.")

genai.configure(api_key=GEMINI_API_KEY)

#  gemini flash or pro
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)


def generate_answer(context_chunks: List[str], question: str) -> str:
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

    response = model.generate_content(prompt)
    return response.text
