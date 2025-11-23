# api.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from rag_core import generate_audit_report_from_files

app = FastAPI()

@app.post("/generate_audit_report")
async def generate_audit_report(
    report_files: List[UploadFile] = File(default=[]),
    documentation_files: List[UploadFile] = File(default=[]),
    regtext_files: List[UploadFile] = File(default=[])
):
    # Lire les fichiers par catégorie
    report_bytes = [await f.read() for f in report_files]
    documentation_bytes = [await f.read() for f in documentation_files]
    regtext_bytes = [await f.read() for f in regtext_files]

    # Construire tes tuples EXACTEMENT comme Streamlit
    file_tuples = []

    file_tuples += [(content, "report") for content in report_bytes]
    file_tuples += [(content, "documentation") for content in documentation_bytes]
    file_tuples += [(content, "regtext") for content in regtext_bytes]

    # calling rag_core pipline
    report = generate_audit_report_from_files(
        files=file_tuples
    )

    return JSONResponse(content=report)
