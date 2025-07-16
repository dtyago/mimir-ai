import os
import chromadb

from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from admin import admin_functions as admin
from utils.db import UserFaceEmbeddingFunction,ChromaDBFaceHelper
from api import userlogin, userlogout, userchat, userupload
from utils.db import ChromaDBFaceHelper
from utils.chat_rag import LlamaModelSingleton

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
    # Preload the LLM model
    await LlamaModelSingleton.get_instance()
    print("LLM model loaded and ready.")

    print(f"MODEL_PATH in main.py = {os.getenv('MODEL_PATH')} ")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2Templates to point to the templates directory
templates = Jinja2Templates(directory="admin/templates")

@app.get("/")
async def get_admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

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
        # Calculate disk usage
        disk_usage = admin.get_disk_usage("/home/user/data")

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
        admin.remove_all_faces(ec_client)
        request.session['flash'] = "All user data successfully deleted."
    except Exception as e:
        request.session['flash'] = f"Failed to delete user data: {str(e)}"
    
    return RedirectResponse(url="/admin/data_management", status_code=303)

app.include_router(userlogin.router)
app.include_router(userlogout.router)
app.include_router(userchat.router)
app.include_router(userupload.router)
