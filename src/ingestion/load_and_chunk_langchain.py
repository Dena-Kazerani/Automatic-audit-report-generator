# src/ingestion/load_and_chunk_langchain.py

from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_chunk_pdf(pdf_path: Path, category: str) -> List[Dict]:
    """Charge 1 PDF, ajoute les métadonnées + génère les chunks avec overlap."""
    
    # 1. PDF -> documents (1 par page)
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    pdf_path = Path(pdf_path)
    doc_id = pdf_path.stem

    # ajouter les métadonnées
    for d in docs:
        d.metadata = d.metadata or {}
        d.metadata["doc_id"] = doc_id
        d.metadata["category"] = category
        d.metadata["source_path"] = str(pdf_path)

    # 2. Splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )

    chunk_docs = splitter.split_documents(docs)

    # 3. Conversion en dict utilisable par ton ingestor
    chunks = []
    for i, d in enumerate(chunk_docs):
        chunks.append({
            "id": f"{doc_id}_{i:04d}",
            "doc_id": doc_id,
            "source_path": d.metadata.get("source_path", ""),
            "category": category,
            "chunk_index": i,
            "text": d.page_content,
        })

    return chunks
