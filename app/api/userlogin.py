from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException
from ..utils.db import tinydb_helper, chromadb_face_helper
from ..utils.jwt_utils import create_access_token
from ..utils.mm_image_utils import get_user_cropped_image_from_photo
import os
import uuid

router = APIRouter()
L2_FACE_THRESHOLD = 0.85 # distance value closer to 0 =>best match, >1 =>poor match
SESSION_VALIDITY =  24 * 60 # Token expires after 24 hours

async def verify_user_face(file_path: str) -> Optional[dict]:
    # Assuming `get_user_cropped_image_from_photo` returns the cropped face as expected by ChromaDB
    face_img = get_user_cropped_image_from_photo(file_path)
    if face_img is None:
        return None

    # Query the user's face in ChromaDB
    query_results = chromadb_face_helper.query_user_face(face_img)
    if query_results and len(query_results["ids"][0]) > 0:
        
        chromadb_face_helper.print_query_results(query_results)

        # Assuming the first result is the best match
        l2_distance = query_results["distances"][0][0]
        if l2_distance < L2_FACE_THRESHOLD: # l2 distance threshold for top matched face
            user_id = query_results["ids"][0][0]
            metadata = query_results["metadatas"][0][0]
            return {"user_id": user_id, "metadata":metadata}
    return None

@router.post("/user/login")
async def user_login(file: UploadFile = File(...)):
    file_path = f"/workspaces/mimir-api/data/tmp/{uuid.uuid4()}.jpg"  # Generates a unique filename
    try:
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)

        # Perform face verification
        verification_result = await verify_user_face(file_path)
        if verification_result:
            user_id = verification_result["user_id"]
            metadata = verification_result["metadata"]
            # Generate JWT token with user information
            access_token = create_access_token(data={"sub": user_id, "name": metadata["name"], "role": metadata["role"]})

            # Calculate expiration time for the token
            expires_at = (datetime.utcnow() + timedelta(minutes=SESSION_VALIDITY)).isoformat()  # Example expiration time
            
            # Store the token in TinyDB
            tinydb_helper.insert_token(user_id, access_token, expires_at)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user_id,
                "name": metadata["name"],
                "role": metadata["role"]
            }
        else:
            raise HTTPException(status_code=400, detail="Face not recognized")
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
