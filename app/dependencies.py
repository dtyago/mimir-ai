import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import SQLite compatibility fix before ChromaDB
from .utils.sqlite_compat import setup_sqlite_compatibility
import chromadb

from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .admin import admin_functions as admin
from .utils.db import UserFaceEmbeddingFunction,ChromaDBFaceHelper, tinydb_helper
from .utils.jwt_utils import decode_jwt
from .utils.db import ChromaDBFaceHelper
from .utils.chat_rag import AzureOpenAIModelSingleton

# Initialize OAuth2 scheme
oauth2_scheme = HTTPBearer()

# Dependency function to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        token = credentials.credentials
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is valid in TinyDB
        if not tinydb_helper.query_token(user_id, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "name": payload.get("name"),
            "role": payload.get("role")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

app = FastAPI()

CHROMADB_LOC = os.getenv('CHROMADB_LOC')

# Add middleware
# Set all origins to wildcard for simplicity, but we should limit this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persitent storage for chromadb setup in /data volume
ec_client = chromadb.PersistentClient(CHROMADB_LOC)

# The following collection reference is needed for admin function to register face
user_faces_db = ec_client.get_or_create_collection(name="user_faces_db", embedding_function=UserFaceEmbeddingFunction())


@app.on_event("startup")
async def startup_event():
    global chromadb_face_helper
    # Assuming chromadb persistent store client for APIs is in helper
    db_path = CHROMADB_LOC
    chromadb_face_helper = ChromaDBFaceHelper(db_path) # Used by APIs
    
    # Perform any other startup tasks here
    # Preload the Azure OpenAI model
    await AzureOpenAIModelSingleton.get_instance()
    print("Azure OpenAI model loaded and ready.")

    print(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"Azure OpenAI Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2Templates to point to the templates directory
templates = Jinja2Templates(directory="app/admin/templates")

@app.get("/")
async def get_admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
        "chromadb_configured": bool(os.getenv("CHROMADB_LOC"))
    }

# Admin Login Handler
@app.post("/admin/login", response_class=HTMLResponse)
async def handle_admin_login(request: Request, username: str = Form(...), password: str = Form(...)):

    if admin.verify_admin_password(username, password):
        # Redirect to user registration page upon successful login
        return RedirectResponse(url="/admin/register_user", status_code=303)
    else:
        # Reload login page with error message
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid password"})

# To display the register user page
@app.get("/admin/register_user", response_class=HTMLResponse)
async def get_user_registration(request: Request):
    # Render the registration form
    return templates.TemplateResponse("user_registration.html", {"request": request})

# User Registration Handler
@app.post("/admin/register_user", response_class=HTMLResponse)
async def handle_user_registration(request: Request, email: str = Form(...), name: str = Form(...), role: str = Form(...), file: UploadFile = File(...)):
    user_id = await admin.register_user(user_faces_db, email, name, role, file)
    if user_id:
        # Calculate disk usage using environment variable
        disk_usage = admin.get_disk_usage()

        # Redirect or display a success message
        return templates.TemplateResponse("registration_success.html", {
            "request": request,
            "disk_usage": disk_usage 
        })
    else:
        # Reload registration page with error message
        return templates.TemplateResponse("user_registration.html", {"request": request, "error": "Registration failed"})

# To display admin utilities
@app.get("/admin/data_management", response_class=HTMLResponse)
async def get_db_details(request: Request):
    # Render the Chroma DB details
    faces = admin.faces_count(ec_client, user_faces_db)
    return templates.TemplateResponse("data_management.html", {
        "request": request,
        "faces" : faces
    })

@app.post("/admin/delete_faces")
async def delete_faces(request: Request):
    try:
        # Call your function to remove all faces
        success = admin.remove_all_faces(ec_client)
        if success:
            message = "All user data successfully deleted."
            return templates.TemplateResponse("data_management.html", {
                "request": request,
                "success_message": message,
                "faces": {"face_count": 0, "all_faces": {"ids": []}, "all_collections": []}
            })
        else:
            message = "Failed to delete user data."
            try:
                faces_data = admin.faces_count(ec_client, user_faces_db)
            except Exception:
                faces_data = {"face_count": 0, "all_faces": {"ids": []}, "all_collections": []}
            return templates.TemplateResponse("data_management.html", {
                "request": request,
                "error_message": message,
                "faces": faces_data
            })
    except Exception as e:
        error_message = f"Failed to delete user data: {str(e)}"
        try:
            faces_data = admin.faces_count(ec_client, user_faces_db)
        except Exception:
            faces_data = {"face_count": 0, "all_faces": {"ids": []}, "all_collections": []}
        return templates.TemplateResponse("data_management.html", {
            "request": request,
            "error_message": error_message,
            "faces": faces_data
        })

# Import API routers and register them
from .api import userlogin, userlogout, userchat, userupload

app.include_router(userlogin.router)
app.include_router(userlogout.router)
app.include_router(userchat.router)
app.include_router(userupload.router)
