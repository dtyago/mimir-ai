from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from ..utils.db import tinydb_helper  # Ensure this import is correct based on our project structure
from ..dependencies import get_current_user, oauth2_scheme

router = APIRouter()

@router.post("/user/logout")
async def user_logout(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), current_user: Any = Depends(get_current_user)):
    try:
        # Extract the token string from credentials
        token = credentials.credentials
        # Assuming `get_current_user` now also ensures and returns the full payload including `user_id`
        user_id = current_user["user_id"]
        # Invalidate the token by removing it from the database
        if not tinydb_helper.query_token(user_id, token):
            raise HTTPException(status_code=404, detail="Token not found.")
        tinydb_helper.remove_token_by_value(token)
        if tinydb_helper.query_token(user_id, token):
            raise HTTPException(status_code=404, detail="Logout unsuccessful.")
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during logout: {str(e)}")
