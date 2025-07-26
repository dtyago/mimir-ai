from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
from ..dependencies import get_current_user
# Assuming a utility for processing PDFs and generating embeddings
from ..utils.doc_ingest import ingest_document
from ..utils.chat_rag import sanitize_collection_name

router = APIRouter()

@router.post("/user/upload")
async def upload_file(file: UploadFile = File(...), current_user: Any = Depends(get_current_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF.")
    
    upload_dir = os.getenv('UPLOAD_DIR', '/tmp/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as buffer:
        contents = await file.read()
        buffer.write(contents)
    
    try:
        # Process PDF and store embeddings 
        ingest_document(file_location, sanitize_collection_name(current_user["user_id"]))
    except Exception as e:
        # If processing fails, attempt to clean up the file before re-raising the error
        os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

    # Clean up file in uploads directory after successful processing
    os.remove(file_location)

    return {
        "status": "File uploaded and processed successfully.",
        "user_id": current_user["user_id"],
        "name": current_user["name"],
        "role": current_user["role"]
    }
