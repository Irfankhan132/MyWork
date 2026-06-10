from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from security import get_current_user
from typing import List
from modules.load_vectorstore import load_vectorstore
from fastapi.responses import JSONResponse
from logger import logger

router = APIRouter()


@router.post("/upload_pdfs/")
async def uplaod_pdfs(
    files: List[UploadFile] = File(...),
    username: str = Depends(get_current_user)
):
    
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    try:
        logger.info(f"Received uploaded files from user: {username}")
        await load_vectorstore(files, username)
        logger.info("Documents added to vectorstore")
        return {"message": "Files processed and vectorstore updated"}
    except Exception as e:
        logger.exception("Error during PDF upload")
        return JSONResponse(status_code=500, content={"error": str(e)})