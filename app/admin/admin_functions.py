from fastapi import UploadFile, File
import bcrypt
import os
import shutil

from ..utils.chat_rag import sanitize_collection_name
from ..utils.mm_image_utils import get_user_cropped_image_from_photo

# Import vector store for database operations
from langchain_community.vectorstores import Chroma
# Import embeddings module from langchain for vector representations of text
from langchain_huggingface import HuggingFaceEmbeddings

# Registrering a face
async def register_user(db, email: str, name: str, role: str, file: UploadFile = File(...)):
    """
    Processes and stores the image uploaded into vectordb as image embeddings.

    :param db: The vector db collection handle to which the image embedding with email id as key will be upserted
    :param email: The email id of the user being registered, this is assumed to be unique per user record
    :param name: The user name (different from email) for display
    :param role: The role associated with the user, can be Analyst-Gaming, Analyst-Non-Gaming, Leadership-Gaming, or Leadership-Non-Gaming
    :param file: The facial image of the user being registered, the first recognized face image would be used.

    :return: email 
    """
    unique_filename = f"{email}.jpg"  # Use the email as the filename
    # Use environment variable for temp directory, fallback to Azure-compatible path
    temp_dir = os.getenv('TEMP_UPLOAD_DIR', '/tmp/uploads')
    file_path = f"{temp_dir}/{unique_filename}"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Then, proceed to open the file
    with open(file_path, "wb") as buffer:
        contents = await file.read()
        buffer.write(contents)

    # Process the image to extract the face
    cropped_face = get_user_cropped_image_from_photo(file_path)
    
    os.remove(file_path)  # Remove the file after processing, PDPA.

    if cropped_face is not None:
        
        # Here we can store the embeddings along with user details in ChromaDB
        # chroma_db.save_embeddings(user_id, embeddings)
        db.upsert(images=[cropped_face], ids=[email], metadatas=[{"name":name, "role":role}])
        return {"status": "User registered successfully", "image": cropped_face}

    else:
        
        return {"error": "No faces detected"}
    
    
    



# Admin Authentication
def verify_admin_password(submitted_user: str, submitted_password: str) -> bool:
    """
    Verifies the submitted password against the stored hash.

    :param submitted_user: The username submitted by the user.
    :param submitted_password: The password submitted by the user.
    :return: True if the password is correct, False otherwise.
    """
    if submitted_user == "admin":
        # Retrieve the stored hash from environment variable
        stored_password_hash = os.getenv("EC_ADMIN_PWD", "")
        
        # Add validation check
        if not stored_password_hash:
            return False
            
        if len(stored_password_hash) != 60:
            return False
        
        # Encode to bytes for bcrypt
        stored_password_hash_bytes = stored_password_hash.encode('utf-8')
        
        # Directly compare the submitted password with the stored hash
        return bcrypt.checkpw(submitted_password.encode('utf-8'), stored_password_hash_bytes)

    return False

# Get disk usage 
def get_disk_usage(path=None):
    # Use environment variable for data directory, fallback to Azure-compatible path
    if path is None:
        path = os.getenv('USER_DATA_DIR', '/tmp/data')
    total, used, free = shutil.disk_usage(path)
    # Convert bytes to MB by dividing by 2^20
    return {
        "total": total / (2**20),
        "used": used / (2**20),
        "free": free / (2**20)
    }

# Additional Admin Functions
# we could include other administrative functionalities here, such as:
# - Listing all registered users.
# - Moderating chat messages or viewing chat history.
# - Managing system settings or configurations.

# Display all faces in collection
def faces_count(client, db):
    try:
        return {
            "face_count"        : db.count(),
            "all_faces"         : db.get(),
            "all_collections"   : client.list_collections() # List all collections at this location
        }
    except Exception as e:
        print(f"Error getting faces count: {e}")
        return {
            "face_count"        : 0,
            "all_faces"         : {"ids": []},
            "all_collections"   : [] # List all collections at this location
        } 

# Delete all faces in collection
def remove_all_faces(client, user_faces_collection="user_faces_db"):
    try:
        # Get the user_faces_db collection
        collection = client.get_collection(name=user_faces_collection)
        
        # Get all documents in the collection
        all_data = collection.get()
        all_user_ids = all_data['ids'] if all_data and 'ids' in all_data else []
        
        CHROMADB_LOC = os.getenv('CHROMADB_LOC')
        # Loop through all user IDs and delete associated collections
        for user_id in all_user_ids:
            sanitized_collection_name = sanitize_collection_name(user_id)
            try:
                vectordb = Chroma(
                    collection_name=sanitized_collection_name,
                    embedding_function=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2'),
                    persist_directory=f"{CHROMADB_LOC}/{sanitized_collection_name}", # Optional: Separate directory for each user's data
                    )
                # Delete all documents in this user's collection
                user_data = vectordb._collection.get()
                if user_data and 'ids' in user_data and user_data['ids']:
                    vectordb._collection.delete(ids=user_data['ids'])
            except Exception as e:
                print(f"Error deleting collection for user {user_id}: {e}")
        
        # Instead of deleting the collection, just clear all documents from it
        # This preserves the collection reference while removing all data
        if all_user_ids:
            collection.delete(ids=all_user_ids)
            print(f"Cleared {len(all_user_ids)} face records from collection (collection preserved)")
        else:
            print("No face records found to clear")
        
        return True
    except Exception as e:
        print(f"Error in remove_all_faces: {e}")
        return False
