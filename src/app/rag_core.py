from src.ingestion.ingest_qdrant import ingest_pdf_files
from src.retrieval.retriever import retrieve
from src.llm.llm_client import generate_answer

def generate_audit_report_from_files(files_with_category): 
  ingest_pdf_files(files_with_category)
  query = f"Generate the ICAAP internal audit report for year {year}. Identify weaknesses, improvements, governance issues, data issues. Base ONLY on the context."
  hits = retrieve(query, top_k=20, category=None)
  answer = generate_answer(context, query) 
  return answer
