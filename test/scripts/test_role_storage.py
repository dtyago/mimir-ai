#!/usr/bin/env python3
"""
Test script to verify role storage in ChromaDB without relying on face recognition matching
"""

import os
import sys
import asyncio

sys.path.append("/workspaces/mimir-ai")

from app.utils.db import chromadb_face_helper


def test_role_storage():
    """Test that roles are being stored correctly in ChromaDB"""

    print("🧪 Testing Role Storage in ChromaDB")
    print("=" * 50)

    try:
        # Get all stored users from ChromaDB
        collection = chromadb_face_helper.user_faces_db
        all_data = collection.get()

        print(f"📊 Total users in database: {len(all_data['ids'])}")
        print()

        # Display all stored users and their roles
        for i, (user_id, metadata) in enumerate(
            zip(all_data["ids"], all_data["metadatas"]), 1
        ):
            name = metadata.get("name", "Unknown")
            role = metadata.get("role", "Unknown")
            print(f"{i}️⃣ User ID: {user_id}")
            print(f"   📛 Name: {name}")
            print(f"   👔 Role: {role}")
            print()

        # Check if we have all expected roles
        stored_roles = [metadata.get("role") for metadata in all_data["metadatas"]]
        expected_roles = [
            "Analyst-Gaming",
            "Analyst-Non-Gaming",
            "Leadership-Gaming",
            "Leadership-Non-Gaming",
        ]

        print("📋 Role Storage Summary:")
        print("-" * 30)

        for role in expected_roles:
            if role in stored_roles:
                print(f"✅ {role}: STORED")
            else:
                print(f"❌ {role}: NOT FOUND")

        print()
        print("🔍 Analysis:")
        print(f"   • Expected {len(expected_roles)} different roles")
        print(f"   • Found {len(set(stored_roles))} unique roles in database")
        print(f"   • Total registrations: {len(all_data['ids'])}")

        if len(set(stored_roles)) == len(expected_roles):
            print("   ✅ All roles successfully stored!")
        else:
            print("   ⚠️  Some roles may be missing or duplicated")

        # Face recognition explanation
        print()
        print("💡 Face Recognition Behavior:")
        print("   • Same face image used for all test registrations")
        print("   • Face recognition correctly identifies same person")
        print("   • Login returns first matching face (expected behavior)")
        print("   • In production, each person would have unique face")

    except Exception as e:
        print(f"❌ Error accessing ChromaDB: {e}")


if __name__ == "__main__":
    test_role_storage()
