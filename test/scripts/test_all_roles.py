#!/usr/bin/env python3
"""
Test script to verify all configured roles work correctly
"""

import os
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_configured_roles():
    """Get roles from environment configuration"""
    roles_env = os.getenv("MIMIR_ROLES", "human")
    default_role = os.getenv("DEFAULT_ROLE", "human")

    # Parse comma-separated roles
    roles = [role.strip() for role in roles_env.split(",") if role.strip()]

    # Ensure default role is included if not already present
    if default_role not in roles:
        roles.append(default_role)

    return roles


def get_image_path_for_role(role):
    """Generate image path for a given role"""
    # Convert role to safe filename (replace special characters)
    safe_role = role.lower().replace("-", "_").replace(" ", "_")

    # Try different extensions
    for ext in [".jpg", ".jpeg", ".png"]:
        image_path = f"./test/data/{safe_role}{ext}"
        if os.path.exists(image_path):
            return image_path

    # Fallback to default image
    for ext in [".jpg", ".jpeg", ".png"]:
        default_path = f"./test/data/default{ext}"
        if os.path.exists(default_path):
            return default_path

    # Final fallback to login-test.jpg for backward compatibility
    return "./test/data/login-test.jpg"


def load_test_image(role=None):
    """Load the appropriate test image for facial recognition based on role"""
    if role is None:
        image_path = "./test/data/default.jpg"
    else:
        image_path = get_image_path_for_role(role)

    try:
        with open(image_path, "rb") as f:
            return BytesIO(f.read())
    except FileNotFoundError:
        # Try fallback options
        fallback_paths = ["./test/data/default.jpg", "./test/data/login-test.jpg"]
        for fallback in fallback_paths:
            try:
                with open(fallback, "rb") as f:
                    print(
                        f"⚠️  Image not found: {image_path}, using fallback: {fallback}"
                    )
                    return BytesIO(f.read())
            except FileNotFoundError:
                continue

        raise FileNotFoundError(
            f"No test images found. Please add test images to ./test/data/"
        )


def test_role_registration(base_url="http://localhost:8000"):
    """Test registration with different roles"""

    roles_to_test = get_configured_roles()

    print(f"🧪 Testing All {len(roles_to_test)} Configured Roles")
    print("=" * 50)
    print(f"📋 Roles from environment: {', '.join(roles_to_test)}")

    for i, role in enumerate(roles_to_test, 1):
        print(f"\n{i}️⃣ Testing Role: {role}")

        try:
            test_image = load_test_image(role)
            # Get the appropriate image filename based on role
            image_path = get_image_path_for_role(role)
            image_filename = os.path.basename(image_path)

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
