#!/usr/bin/env python3
"""
Test script for admin APIs in both devcontainer and Azure environments
"""

import requests
import json
import sys
import os
from io import BytesIO
from PIL import Image


def create_test_image():
    """Use the real test image from the test folder"""
    test_image_path = "./test/data/login-test.jpg"
    if os.path.exists(test_image_path):
        with open(test_image_path, "rb") as f:
            return BytesIO(f.read())
    else:
        # Fallback to creating a simple test image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return img_bytes


def test_admin_apis(base_url="http://localhost:8000"):
    """Test admin registration and login APIs"""
    print(f"🧪 Testing Admin APIs at {base_url}")
    print("=" * 60)

    session = requests.Session()
    test_results = []

    # Test 1: Health Check - CRITICAL TEST
    print("1️⃣ Testing Health Endpoint...")
    try:
        response = session.get(
            f"{base_url}/health", timeout=10
        )  # Reduced from 30s to 10s
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   ✅ Azure OpenAI: {health_data['azure_openai_configured']}")
            print(f"   ✅ ChromaDB: {health_data['chromadb_configured']}")
            test_results.append(("Health Check", True))
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            print(f"   🛑 CRITICAL FAILURE: Service not responding properly")

            # Different recommendations based on environment
            if "localhost" in base_url:
                print(f"   🔄 DevContainer Recommendations:")
                print(
                    f"      - Server may be auto-restarting (use ./dev-server-stable.sh)"
                )
                print(f"      - Check if development server is running (./start.sh)")
                print(f"      - Verify port 8000 is available")
            else:
                print(f"   🔄 Azure App Service Recommendations:")
                print(f"      - Check Azure App Service status in portal")
                print(f"      - Verify App Service Plan has sufficient resources")
                print(f"      - Review application logs for worker timeout issues")
                print(f"      - Consider scaling up if using Basic B1 tier")

            test_results.append(("Health Check", False))
            return False  # Fail fast - no point continuing
    except requests.exceptions.Timeout:
        print(f"   ❌ Health check timeout (10s)")
        print(f"   🛑 CRITICAL FAILURE: Service taking too long to respond")

        if "localhost" in base_url:
            print(f"   🔄 Local server may be overloaded or stuck")
        else:
            print(f"   🔄 Azure App Service may be under resource pressure")
            print(
                f"      - Check if Basic B1 tier has sufficient memory for ML workloads"
            )
            print(f"      - Consider upgrading to B2 or higher tier")

        test_results.append(("Health Check", False))
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Health check connection error")
        print(f"   🛑 CRITICAL FAILURE: Cannot connect to service")

        if "localhost" in base_url:
            print(f"   🔄 DevContainer Recommendations:")
            print(f"      - Check if development server is running")
            print(f"      - Server may be restarting (auto-reload issue)")
        else:
            print(f"   🔄 Azure App Service Recommendations:")
            print(f"      - Verify service URL is correct")
            print(f"      - Check if App Service is running in Azure portal")
            print(f"      - Verify deployment was successful")

        test_results.append(("Health Check", False))
        return False  # Fail fast - no point continuing
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        print(f"   🛑 CRITICAL FAILURE: Unexpected error during health check")
        test_results.append(("Health Check", False))
        return False  # Fail fast - no point continuing

    # Test 2: Admin Login Page
    print("\n2️⃣ Testing Admin Login Page...")
    try:
        response = session.get(f"{base_url}/", timeout=30)
        if response.status_code == 200 and "login" in response.text.lower():
            print("   ✅ Admin login page accessible")
            test_results.append(("Admin Login Page", True))
        else:
            print(f"   ❌ Admin login page failed: {response.status_code}")
            test_results.append(("Admin Login Page", False))
    except Exception as e:
        print(f"   ❌ Admin login page error: {e}")
        test_results.append(("Admin Login Page", False))

    # Test 3: User Registration Endpoint
    print("\n3️⃣ Testing User Registration Endpoint...")
    try:
        # Prepare test data with correct field names based on admin_functions.py
        test_user_data = {
            "name": "Test User 123",
            "email": "testuser123@example.com",
            "role": "Analyst-Gaming",  # Must be one of the 4 available roles
        }

        # Create test image using real test file
        test_image = create_test_image()

        files = {"file": ("login-test.jpg", test_image, "image/jpeg")}

        response = session.post(
            f"{base_url}/admin/register_user",
            data=test_user_data,
            files=files,
            timeout=30,
        )

        print(f"   📊 Registration response: {response.status_code}")
        if response.status_code in [200, 201, 409]:  # 409 if user already exists
            try:
                response_data = response.json()
                print(f"   📝 Response: {response_data}")
                if response.status_code == 409:
                    print("   ℹ️  User already exists (expected in repeated tests)")
                test_results.append(("User Registration", True))
            except json.JSONDecodeError:
                print(f"   ⚠️  Non-JSON response: {response.text[:100]}")
                test_results.append(
                    ("User Registration", True)
                )  # Still considered success
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}")
            test_results.append(("User Registration", False))

    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        test_results.append(("User Registration", False))

    # Test 4: User Login Endpoint (Face-based login)
    print("\n4️⃣ Testing User Login Endpoint...")
    try:
        # User login requires a face image file, not username/password
        test_image = create_test_image()

        files = {"file": ("login-test.jpg", test_image, "image/jpeg")}

        response = session.post(f"{base_url}/user/login", files=files, timeout=30)
        print(f"   📊 Login response: {response.status_code}")

        if response.status_code == 200:
            try:
                login_response = response.json()
                if "access_token" in login_response:
                    print("   ✅ Login successful, token received")
                    print(f"   👤 User: {login_response.get('user_name', 'Unknown')}")
                    test_results.append(("User Login", True))
                else:
                    print(f"   ⚠️  Login response: {login_response}")
                    test_results.append(("User Login", False))
            except json.JSONDecodeError:
                print(f"   ⚠️  Non-JSON login response: {response.text[:100]}")
                test_results.append(("User Login", False))
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error: {error_data}")
            except:
                print(f"   📝 Response: {response.text[:200]}")
            test_results.append(("User Login", False))

    except Exception as e:
        print(f"   ❌ Login error: {e}")
        test_results.append(("User Login", False))

    # Test 5: Disk Usage (Admin Function)
    print("\n5️⃣ Testing Admin Functions (Disk Usage)...")
    try:
        # This would require admin authentication in a real scenario
        # For now, we test if the endpoint exists
        response = session.get(f"{base_url}/admin/data_management", timeout=30)
        if response.status_code in [200, 302, 401, 403]:  # Various expected responses
            print("   ✅ Admin data management endpoint exists")
            test_results.append(("Admin Functions", True))
        else:
            print(f"   ❌ Admin functions test failed: {response.status_code}")
            test_results.append(("Admin Functions", False))
    except Exception as e:
        print(f"   ❌ Admin functions error: {e}")
        test_results.append(("Admin Functions", False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    # Determine base URL and environment
    base_url = (
        "https://mimir-api-prod-bbdadveqe2dha6hp.canadacentral-01.azurewebsites.net"
    )
    environment_type = "Azure Production"

    if len(sys.argv) > 1 and sys.argv[1].lower() == "local":
        base_url = "http://localhost:8000"
        environment_type = "Local DevContainer"
    elif len(sys.argv) > 1:
        base_url = sys.argv[1]
        environment_type = "Custom"

    print(f"🚀 Admin API Test Suite")
    print(f"🎯 Target: {base_url}")
    print(f"🏷️  Environment: {environment_type}")
    print(f"⏱️  Health check timeout: 10 seconds (fail-fast)")
    print(f"⏱️  Other requests timeout: 30 seconds")

    # Environment-specific warnings
    if "localhost" in base_url:
        print("⚠️  DevContainer Note: Auto-reload may cause connection issues")
        print("   Consider using ./dev-server-stable.sh for more reliable testing")
    else:
        print("🔍 Azure Note: Testing against production service")
        print("   Failures may indicate resource constraints or deployment issues")

    print("=" * 60)

    success = test_admin_apis(base_url)

    if not success:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED")
        print("=" * 60)
        print("💡 Environment-Specific Troubleshooting:")

        if "localhost" in base_url:
            print("   DevContainer Issues:")
            print("   1. Check if auto-reload is causing restarts")
            print("   2. Use stable server: ./dev-server-stable.sh")
            print("   3. Verify .env file is properly configured")
            print("   4. Ensure all dependencies are installed")
        else:
            print("   Azure App Service Issues:")
            print("   1. Check App Service status in Azure portal")
            print("   2. Review application logs for errors")
            print("   3. Verify App Service Plan tier (B2+ recommended for ML)")
            print("   4. Check recent deployments for issues")
            print("   5. Consider scaling up if using Basic B1 tier")

    sys.exit(0 if success else 1)
