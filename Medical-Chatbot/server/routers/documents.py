from fastapi import APIRouter
from pathlib import Path
from pinecone import Pinecone
import os

router = APIRouter()

UPLOAD_DIR = Path("./uploaded_docs")

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX_NAME"])

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

    # delete local PDF
    if file_path.exists():
        file_path.unlink()

    # delete Pinecone vectors
    prefix = Path(filename).stem

    vector_ids = []

    response = index.list(prefix=prefix)

    for ids in response:
        vector_ids.extend(ids)

    if vector_ids:
        index.delete(ids=vector_ids)

    return {
        "message": f"{filename} and related vectors deleted successfully"
    }