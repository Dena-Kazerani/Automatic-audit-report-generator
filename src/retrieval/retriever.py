# src/retrieval/retriever.py

from typing import List, Optional, Dict, Any

from fastembed import TextEmbedding
from qdrant_client.models import Filter, FieldCondition, MatchValue

from .qdrant_connection import client, COLLECTION_NAME

# même modèle que pour l'ingestion
_embedder = TextEmbedding()  # modèle par défaut (384 dims)


def embed(text: str) -> List[float]:
    # fastembed renvoie un générateur -> on prend le premier vecteur
    return list(_embedder.embed([text]))[0]


def build_filter(category: Optional[str] = None) -> Optional[Filter]:
    """
    Construit un filtre Qdrant sur la métadonnée 'category' si demandé.
    category ∈ {"report", "documentation", "reg_text"} ou None.
    """
    if category is None:
        return None

    return Filter(
        must=[
            FieldCondition(
                key="category",
                match=MatchValue(value=category),
            )
        ]
    )


def retrieve(
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query_vector = embed(query)
    q_filter = build_filter(category)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        query_filter=q_filter,
        with_payload=True,
        with_vectors=False,
    )

    out = []
    for r in results.points:
        out.append(
            {
                "score": r.score,
                "text": r.payload.get("text", ""),
                "doc_id": r.payload.get("doc_id", ""),
                "category": r.payload.get("category", ""),
                "chunk_id": r.payload.get("chunk_id", ""),
            }
        )
    return out


    # On standardise un peu la sortie
    out = []
    for r in results:
        out.append(
            {
                "score": r.score,
                "text": r.payload.get("text", ""),
                "doc_id": r.payload.get("doc_id", ""),
                "category": r.payload.get("category", ""),
                "chunk_id": r.payload.get("chunk_id", ""),
            }
        )
    return out


if __name__ == "__main__":
    # petit test manuel
    query = "Key weaknesses identified in the 2023 ICAAP credit risk model"
    hits = retrieve(query, top_k=3, category="report")
    for h in hits:
        print("---")
        print(f"[score={h['score']:.4f}] {h['category']} / {h['doc_id']}")
        print(h["text"][:300], "...")
