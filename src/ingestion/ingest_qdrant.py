# src/ingestion/ingest_qdrant.py

from pathlib import Path
from typing import Dict, Any, List
import json
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
from .load_and_chunk_langchain import load_and_chunk_pdf

_embedder = TextEmbedding()  


CHUNKS_FILE = Path("data/chunks/chunks.jsonl")

QDRANT_URL = "http://localhost:6333"  # to adapt si cloud is used
COLLECTION_NAME = "icaap_rag"
EMBEDDING_DIM = 384  # to adapt if we change embeding model



_embedder = TextEmbedding()   # load model once 

from typing import Union, Sequence

def embed(texts: Union[str, Sequence[str]]):
    if isinstance(texts, str):
        return list(_embedder.embed([texts]))[0]
    else:
        return list(_embedder.embed(list(texts)))

def create_collection_if_needed(client: QdrantClient) -> None:
    existing = client.get_collections()
    names = {c.name for c in existing.collections}

    if COLLECTION_NAME in names:
        print(f"[INFO] Collection '{COLLECTION_NAME}' existe déjà.")
        return

    print(f"[INFO] Création de la collection '{COLLECTION_NAME}'...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,
            distance=Distance.COSINE,
        ),
    )


def ingest_chunks(chunks):
    # 1. Embeddings
    texts = [c["text"] for c in chunks]
    vectors = embed(texts)

    # 2. Préparer les points
    points = []
    for i, chunk in enumerate(chunks):
        points.append(
            PointStruct(
                id=i,
                vector=vectors[i],
                payload=chunk,
            )
        )

    # 3. Envoyer à Qdrant
    try:
        client = QdrantClient(url=QDRANT_URL)
    except:
        client = QdrantClient(":memory:")

    create_collection_if_needed(client)
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
def ingest_pdf_files(files_with_category):
    """
    files_with_category = [
        ("/tmp/Audit_2023.pdf", "report"),
        ("/tmp/Doc_2024.pdf", "documentation"),
        ...
    ]
    """
    all_chunks = []

    for filepath, category in files_with_category:
        print(f"[INFO] Chunking {filepath} ({category})...")
        chunks = load_and_chunk_pdf(filepath, category)
        all_chunks.extend(chunks)

    print(f"[INFO] Total chunks = {len(all_chunks)}")

    print("[INFO] Embedding + sending to Qdrant...")
    ingest_chunks(all_chunks)

    print("[OK] Ingestion completed.")


def main() -> None:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"{CHUNKS_FILE} introuvable. Lance d'abord load_and_chunck_langchain.py.")

    client = QdrantClient(url=QDRANT_URL)
    create_collection_if_needed(client)

    points: List[PointStruct] = []

    with CHUNKS_FILE.open("r", encoding="utf-8") as f_in:
        for line in f_in:
            record: Dict[str, Any] = json.loads(line)
            text = record["text"]
            category = record["category"]
            doc_id = record["doc_id"]
            chunk_id = record["id"]

            # Embedding du chunk
            vector = embed(text)

            payload = {
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "category": category,  # <- ta métadonnée clef
                "text": text,
            }

            point = PointStruct(
                id=str(uuid.uuid4()),  # id Qdrant unique
                vector=vector,
                payload=payload,
            )
            points.append(point)

    # Insertion dans Qdrant (en un batch)
    print(f"[INFO] Upsert de {len(points)} points dans '{COLLECTION_NAME}'...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )

    print("[INFO] Ingestion Qdrant terminée.")


if __name__ == "__main__":
    main()
