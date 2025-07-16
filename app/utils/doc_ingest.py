# utils/doc_ingest.py
from .chat_rag import pdf_to_vec

def ingest_document(file_location: str, collection_name: str):
    """
    Process and ingest a document into a user-specific vector database.
    
    :param file_location: The location of the uploaded file on the server.
    :param collection_name: The collection name unique for each user uploading the document.
    """
   
    try:
        vectordb = pdf_to_vec(file_location, collection_name)
        print("Document processed and ingested successfully into user-specific collection.")
    except Exception as e:
        print(f"Error processing document for collection {collection_name}: {e}")
        raise
