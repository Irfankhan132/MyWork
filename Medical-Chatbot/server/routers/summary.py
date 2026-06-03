from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from modules.llm import generate_document_summary
from logger import logger

router = APIRouter()

UPLOAD_DIR = Path("./uploaded_docs")


@router.post("/summary/")
async def summarize_document(
    username: str = Form(...),
    filename: str = Form(...)
):
    try:
        file_path = UPLOAD_DIR / username / filename

        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )

        loader = PyPDFLoader(str(file_path))
        documents = loader.load()

        full_text = "\n".join([doc.page_content for doc in documents])

        # Limit text size to avoid very large prompt
        full_text = full_text[:12000]

        summary = generate_document_summary(full_text, filename)

        return {
            "filename": filename,
            "summary": summary
        }

    except Exception as e:
        logger.exception("Error generating document summary")
        return JSONResponse(status_code=500, content={"error": str(e)})