# src/retrieval/qdrant_client.py

from qdrant_client import QdrantClient

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "icaap_rag"  # à changer ici si tu renommes la collection

client = QdrantClient(url=QDRANT_URL)
