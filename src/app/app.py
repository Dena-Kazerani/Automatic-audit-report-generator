import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.append(ROOT)

import streamlit as st
import tempfile

from src.ingestion.ingest_qdrant import ingest_pdf_files
from src.retrieval.retriever import retrieve
from src.llm.llm_client import generate_answer

st.set_page_config(page_title="ICAAP Audit Report Generator")

st.title("ICAAP Audit Report Generator")

st.write("Upload audit reports, modelling documentation and regulatory texts. The system will generate the ICAAP audit report for year N.")

# --- UPLOAD ZONE ---
st.subheader("1. Upload documents")

uploaded_reports = st.file_uploader("Upload audit reports (PDF)", type="pdf", accept_multiple_files=True)
uploaded_docs = st.file_uploader("Upload modelling documentation (PDF)", type="pdf", accept_multiple_files=True)
uploaded_reg = st.file_uploader("Upload regulatory texts (PDF)", type="pdf", accept_multiple_files=True)

if st.button("Process documents"):
    all_files = []

    # create temp directory
    tmpdir = tempfile.mkdtemp()

    # Save PDFs locally + record category
    def save_files(uploaded, category):
        saved = []
        if uploaded:
            for f in uploaded:
                path = os.path.join(tmpdir, f.name)
                with open(path, "wb") as fh:
                    fh.write(f.getbuffer())
                saved.append((path, category))
        return saved

    all_files += save_files(uploaded_reports, "report")
    all_files += save_files(uploaded_docs, "documentation")
    all_files += save_files(uploaded_reg, "reg_text")

    if not all_files:
        st.error("Please upload at least one document.")
    else:
        st.info("Processing and ingesting into Qdrant...")
        ingest_pdf_files(all_files)  # tu l’as déjà dans ton ingestion
        st.success("Documents ingested successfully.")

        st.session_state["ready"] = True

# --- GENERATE AUDIT REPORT ---
st.subheader("2. Generate ICAAP Audit Report for year N")

year = st.number_input("Target year", min_value=2000, max_value=2100, value=2025)

if st.button("Generate Audit Report"):

    if "ready" not in st.session_state:
        st.error("Please upload and process documents first.")
    else:
        st.info("Retrieving relevant information...")
        query = f"Generate the ICAAP internal audit report for year {year}. Identify weaknesses, improvements, governance issues, data issues. Base ONLY on the context."

        hits = retrieve(query, top_k=20, category=None)
        context = [h["text"] for h in hits]

        st.info("Calling LLM to generate full report...")
        answer = generate_answer(context, query)

        st.subheader(f"Audit Report {year}")
        st.write(answer)
