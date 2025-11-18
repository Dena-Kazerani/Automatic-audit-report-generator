# src/main_test_llm.py

from src.retrieval.retriever import retrieve
from src.llm.llm_client import generate_answer

def test_llm():
    # 1. Query pour tester le RAG
    query = "What were the main weaknesses identified in the ICAAP credit risk model in previous years?"

    # 2. Récupération des chunks pertinents
    hits = retrieve(query, top_k=5, category="report")

    print("\n--- Retrieved Chunks ---")
    for h in hits:
        print(f"- {h['doc_id']} [{h['category']}], score={h['score']:.4f}")
        print(h['text'][:200], "...\n")

    # 3. Construction du contexte (uniquement le texte des chunks)
    context_chunks = [h["text"] for h in hits]

    # 4. Appel LLM
    question = (
        "Summarize the weaknesses of the ICAAP credit risk model based only on the provided context. "
        "Write in a concise narrative style, without bullet points."
    )

    answer = generate_answer(context_chunks, question)

    print("\n--- LLM Answer ---\n")
    print(answer)


if __name__ == "__main__":
    test_llm()
