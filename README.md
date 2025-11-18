# ICAAP Audit Report Generator

This project is an automated system for generating ICAAP internal audit reports (Year N) based on:
- previous audit reports,
- modelling documentation,
- regulatory texts.

It uses:
- **Streamlit** for the user interface,
- **FastEmbed** for embeddings,
- **Qdrant** as vector database,
- a **local LLM / API LLM client** for text generation,
- **PDF chunking** and semantic search (RAG).

## How to run

```bash
# 1. Create environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py

src/
│── ingestion/
│── retrieval/
│── llm/
data/
app.py



