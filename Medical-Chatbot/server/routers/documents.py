from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("./uploaded_docs")

@router.get("/documents/")
async def list_documents():
    UPLOAD_DIR.mkdir(exist_ok=True)

    documents = [
        file.name
        for file in UPLOAD_DIR.glob("*.pdf")
    ]

    return {"documents": documents}