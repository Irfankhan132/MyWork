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


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    file_path = UPLOAD_DIR / filename

    if file_path.exists():
        file_path.unlink()
        return {"message": f"{filename} deleted successfully"}

    return {"error": "File not found"}