import os
from tinydb import TinyDB, Query, where
from tinydb.storages import MemoryStorage
import chromadb
from chromadb.api.types import EmbeddingFunction, Embeddings, Image, Images
from keras_facenet import FaceNet
from typing import Any
from datetime import datetime, timedelta


class TinyDBHelper:
    def __init__(self):
        self.db = TinyDB(storage=MemoryStorage)
        self.tokens_table = self.db.table('tokens')

    def insert_token(self, user_id: str, token: str, expires_at: str):
        self.tokens_table.insert({'user_id': user_id, 'token': token, 'expires_at': expires_at})

    def query_token(self, user_id: str, token: str) -> bool:
        """Query to check if the token exists and is valid."""
        User = Query()
        result = self.tokens_table.search((User.user_id == user_id) & (User.token == token))

        # Check if the result is empty (i.e., no matching token found)
        if not result:
            return False

        # Check if the token is expired
        expires_at = datetime.fromisoformat(result[0]['expires_at'])
        if datetime.utcnow() > expires_at:
            return False
        
        return True

    def remove_token_by_value(self, token: str):
        """Remove a token based on its value."""
        self.tokens_table.remove((where('token') == token))

###### Class implementing Custom Embedding function for chroma db
#
class UserFaceEmbeddingFunction(EmbeddingFunction[Images]):
    def __init__(self):
        # Intitialize the FaceNet model
        self.facenet = FaceNet()

    def __call__(self, input: Images) -> Embeddings:
        # Since the input images are assumed to be `numpy.ndarray` objects already,
        # we can directly use them for embeddings extraction without additional processing.
        # Ensure the input images are pre-cropped face images ready for embedding extraction.

        # Extract embeddings using FaceNet for the pre-cropped face images.
        embeddings_array = self.facenet.embeddings(input)

        # Convert numpy array of embeddings to list of lists, as expected by Chroma.
        return embeddings_array.tolist()


# Usage example:
# user_face_embedding_function = UserFaceEmbeddingFunction()
# Assuming `images` is a list of `numpy.ndarray` objects where each represents a pre-cropped face image ready for embedding extraction.
# embeddings = user_face_embedding_function(images)


class ChromaDBFaceHelper:
    def __init__(self, db_path: str):
        self.client = chromadb.PersistentClient(db_path)
        self.user_faces_db = self.client.get_or_create_collection(name="user_faces_db", embedding_function=UserFaceEmbeddingFunction())

    def query_user_face(self, presented_face: Any, n_results: int = 1):
        return self.user_faces_db.query(query_images=[presented_face], n_results=n_results)
    
    def print_query_results(self, query_results: dict) -> None:
        for id, distance, metadata in zip(query_results["ids"][0], query_results['distances'][0], query_results['metadatas'][0]):
            print(f'id: {id}, distance: {distance}, metadata: {metadata}')


# Initialize these helpers globally if they are to be used across multiple modules
tinydb_helper = TinyDBHelper()
chromadb_face_helper = ChromaDBFaceHelper(os.getenv('CHROMADB_LOC'))  # Initialization requires db_path
