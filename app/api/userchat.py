from fastapi import APIRouter, Depends, HTTPException, Body
from ..dependencies import get_current_user
from ..utils.chat_rag import llm_infer
from ..utils.chat_rag import sanitize_collection_name
from typing import Any

router = APIRouter()

@router.post("/user/chat")
async def chat_with_llama(user_input: str = Body(..., embed=True), current_user: Any = Depends(get_current_user)):
    # Example logic for model inference (pseudo-code, adjust as necessary)
    try:
        user_id = current_user["user_id"]
        model_response = await llm_infer(user_collection_name=sanitize_collection_name(user_id), prompt=user_input)
        # Optionally, store chat history
        # chromadb_face_helper.store_chat_history(user_id=current_user["user_id"], user_input=user_input, model_response=model_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "ai_response": model_response,
        "user_id": current_user["user_id"],
        "name": current_user["name"],
        "role": current_user["role"]
    }
