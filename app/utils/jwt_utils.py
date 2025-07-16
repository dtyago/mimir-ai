from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
from typing import Any, Union
#from tinydb import TinyDB, Query
#from tinydb.storages import MemoryStorage


# Secret key to encode JWT tokens. In production, use a more secure key and keep it secret!
SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # The expiration time for the access token

def encode_jwt(data: dict):
    # Encode a JWT token
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str):
    try:
        # Decode a JWT token
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        # Handle specific JWT errors (e.g., token expired, invalid token)
        raise HTTPException(status_code=401, detail="Token is invalid or expired")
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail="An error occurred while decoding token")

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Creates a JWT access token.

    :param data: A dictionary of claims (e.g., {"sub": user_id}) to include in the token.
    :param expires_delta: A timedelta object representing how long the token is valid.
    :return: A JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Additional functions can be added here for verifying tokens, decoding tokens, etc.
