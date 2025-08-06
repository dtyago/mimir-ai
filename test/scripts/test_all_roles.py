#!/usr/bin/env python3
"""
Test script to verify all 4 new roles work correctly
"""

import requests
from io import BytesIO


def load_test_image(role=None):
    """Load the appropriate test image for facial recognition based on role"""
    # Map roles to their corresponding image files
    role_image_map = {
        "Analyst-Gaming": "./test/data/analyst-gaming.jpg",
        "Analyst-Non-Gaming": "./test/data/analyst-non-gaming.jpeg",
        "Leadership-Gaming": "./test/data/leadership-gaming.jpeg",
        "Leadership-Non-Gaming": "./test/data/leadership-non-gaming.jpeg",
    }

    # Use role-specific image if role is provided, otherwise use default
    image_path = role_image_map.get(role, "./test/data/login-test.jpg")

    try:
        with open(image_path, "rb") as f:
            return BytesIO(f.read())
    except FileNotFoundError:
        print(f"⚠️  Image not found: {image_path}, using default")
        with open("./test/data/login-test.jpg", "rb") as f:
            return BytesIO(f.read())


def test_role_registration(base_url="http://localhost:8000"):
    """Test registration with different roles"""

    roles_to_test = [
        "Analyst-Gaming",
        "Analyst-Non-Gaming",
        "Leadership-Gaming",
        "Leadership-Non-Gaming",
    ]

    print("🧪 Testing All 4 New Roles")
    print("=" * 50)

    for i, role in enumerate(roles_to_test, 1):
        print(f"\n{i}️⃣ Testing Role: {role}")

        try:
            test_image = load_test_image(role)
            # Get the appropriate image filename based on role
            role_image_filenames = {
                "Analyst-Gaming": "analyst-gaming.jpg",
                "Analyst-Non-Gaming": "analyst-non-gaming.jpeg",
                "Leadership-Gaming": "leadership-gaming.jpeg",
                "Leadership-Non-Gaming": "leadership-non-gaming.jpeg",
            }
            image_filename = role_image_filenames.get(role, "login-test.jpg")

            files = {
                "email": (None, f"test_role_{i}@example.com"),
                "name": (None, f"Test User {role}"),
                "role": (None, role),
                "file": (image_filename, test_image, "image/jpeg"),
            }

            response = requests.post(
                f"{base_url}/admin/register_user", files=files, timeout=30
            )

            if response.status_code == 200:
                print(f"   ✅ Registration successful for {role}")

                # Test login to verify role is stored correctly
                test_image = load_test_image(role)
                files = {"file": (image_filename, test_image, "image/jpeg")}
                login_response = requests.post(
                    f"{base_url}/user/login", files=files, timeout=30
                )

                if login_response.status_code == 200:
                    login_data = login_response.json()
                    stored_role = login_data.get("role")
                    if stored_role == role:
                        print(
                            f"   ✅ Role correctly stored and retrieved: {stored_role}"
                        )
                    else:
                        print(
                            f"   ❌ Role mismatch: expected {role}, got {stored_role}"
                        )
                else:
                    print(f"   ❌ Login failed for {role}")
            else:
                print(f"   ❌ Registration failed for {role}: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error testing {role}: {e}")

    print(f"\n🎯 Role testing completed!")


if __name__ == "__main__":
    test_role_registration()
