from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from pinecone import Pinecone
from security import get_current_user
import os

router = APIRouter()

UPLOAD_DIR = Path("./uploaded_docs")

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX_NAME"])


@router.get("/documents/")
async def list_documents(
    username: str = Depends(get_current_user)
):
    user_upload_dir = UPLOAD_DIR / username
    
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    user_upload_dir.mkdir(parents=True, exist_ok=True)

    documents = [
        file.name
        for file in user_upload_dir.glob("*.pdf")
    ]

    return {"documents": documents}


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    username: str = Depends(get_current_user)
):
    
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    user_upload_dir = UPLOAD_DIR / username
    file_path = user_upload_dir / filename

    # Delete local PDF
    if file_path.exists():
        file_path.unlink()

    # Delete Pinecone vectors for this user's file
    prefix = f"{username}-{Path(filename).stem}"

    vector_ids = []

    response = index.list(prefix=prefix)

    for ids in response:
        for item in ids:
            vector_ids.append(str(item))

    if vector_ids:
        index.delete(ids=vector_ids)
    return {
        "message": f"{filename} and related vectors deleted successfully for user {username}"
    }