#!/usr/bin/env python3
"""
Debug registration process step by step
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app to the path
sys.path.append("/workspaces/mimir-ai")


async def debug_registration():
    """Debug the registration process step by step"""
    print("🔍 Debugging Registration Process")
    print("=" * 50)

    try:
        # Test 1: Import dependencies
        print("1️⃣ Testing imports...")
        from app.dependencies import user_faces_db
        from app.admin import admin_functions as admin
        from app.utils.mm_image_utils import get_user_cropped_image_from_photo
        from fastapi import UploadFile

        print("   ✅ All imports successful")

        # Test 2: Check temp directory
        print("\n2️⃣ Testing temp directory...")
        temp_dir = os.getenv("TEMP_UPLOAD_DIR", "/tmp/uploads")
        print(f"   📁 Temp dir: {temp_dir}")
        os.makedirs(temp_dir, exist_ok=True)
        print("   ✅ Temp directory ready")

        # Test 3: Check test image
        print("\n3️⃣ Testing image file...")
        test_image_path = "./test/data/login-test.jpg"
        if os.path.exists(test_image_path):
            print(f"   ✅ Test image exists: {test_image_path}")
            print(f"   📊 File size: {os.path.getsize(test_image_path)} bytes")
        else:
            print(f"   ❌ Test image not found: {test_image_path}")
            return

        # Test 4: Test face processing directly
        print("\n4️⃣ Testing face processing...")
        try:
            cropped_face = get_user_cropped_image_from_photo(test_image_path)
            if cropped_face is not None:
                print("   ✅ Face detection successful")
                print(f"   📊 Cropped face type: {type(cropped_face)}")
            else:
                print("   ❌ No face detected in image")
                return
        except Exception as e:
            print(f"   ❌ Face processing error: {e}")
            import traceback

            traceback.print_exc()
            return

        # Test 5: Test database connection
        print("\n5️⃣ Testing database connection...")
        try:
            # Test basic DB operations
            result = user_faces_db.get()
            print(f"   ✅ Database accessible, current users: {len(result['ids'])}")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return

        # Test 6: Test full registration (mock)
        print("\n6️⃣ Testing registration flow...")
        try:
            # Mock the UploadFile for testing
            class MockUploadFile:
                def __init__(self, file_path):
                    self.file_path = file_path

                async def read(self):
                    with open(self.file_path, "rb") as f:
                        return f.read()

            mock_file = MockUploadFile(test_image_path)
            result = await admin.register_user(
                db=user_faces_db,
                email="debug@test.com",
                name="Debug User",
                role="Analyst-Gaming",
                file=mock_file,
            )
            print(f"   ✅ Registration successful: {result['status']}")

        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            import traceback

            traceback.print_exc()

        print("\n" + "=" * 50)
        print("🎯 Debug completed")

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_registration())
