"""
SQLite compatibility module for ChromaDB.

This module handles the SQLite version compatibility issue with ChromaDB.
ChromaDB requires SQLite >= 3.35.0, but many systems ship with older versions.
"""

import os
import sys
import sqlite3

def setup_sqlite_compatibility():
    """
    Set up SQLite compatibility for ChromaDB.
    
    ChromaDB requires SQLite >= 3.35.0. This function provides information
    about the current SQLite version and suggests solutions.
    """
    # Check if the current SQLite version is sufficient
    current_version = tuple(map(int, sqlite3.sqlite_version.split('.')))
    required_version = (3, 35, 0)
    
    print(f"🔍 SQLite compatibility check:")
    print(f"   Current SQLite version: {sqlite3.sqlite_version}")
    print(f"   Required SQLite version: 3.35.0+")
    
    if current_version >= required_version:
        print(f"✅ SQLite version {sqlite3.sqlite_version} is compatible with ChromaDB")
        return True
    
    print(f"⚠️  SQLite version {sqlite3.sqlite_version} is below required version 3.35.0")
    
    # Set environment variables that may help with development
    os.environ['CHROMADB_ALLOW_RESET'] = 'true'
    
    # Print helpful information
    print("\n📋 Solutions:")
    print("   1. Use Docker/DevContainer with newer SQLite (recommended for production)")
    print("   2. For local development, install a newer SQLite version:")
    print("      - On Ubuntu/Debian: Upgrade to Ubuntu 22.04+ or install from source")
    print("      - On macOS: brew install sqlite")
    print("      - From source: https://docs.trychroma.com/troubleshooting#sqlite")
    print("   3. Consider using alternative vector database (FAISS, Pinecone, etc.)")
    
    return False

def check_chromadb_compatibility():
    """
    Check if ChromaDB can be imported successfully.
    """
    try:
        import chromadb
        print("✅ ChromaDB imported successfully!")
        return True
    except RuntimeError as e:
        if "sqlite3" in str(e).lower():
            print("❌ ChromaDB SQLite compatibility issue detected")
            print(f"   Error: {str(e)}")
            return False
        else:
            raise
    except Exception as e:
        print(f"❌ Unexpected ChromaDB import error: {str(e)}")
        raise

# Call the setup function when this module is imported
if __name__ != "__main__":
    setup_sqlite_compatibility()
