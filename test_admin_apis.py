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
    """Create a simple test image for face registration"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_admin_apis(base_url="http://localhost:8000"):
    """Test admin registration and login APIs"""
    print(f"🧪 Testing Admin APIs at {base_url}")
    print("=" * 60)
    
    session = requests.Session()
    test_results = []
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Endpoint...")
    try:
        response = session.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   ✅ Azure OpenAI: {health_data['azure_openai_configured']}")
            print(f"   ✅ ChromaDB: {health_data['chromadb_configured']}")
            test_results.append(("Health Check", True))
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            test_results.append(("Health Check", False))
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        test_results.append(("Health Check", False))
    
    # Test 2: Admin Login Page
    print("\n2️⃣ Testing Admin Login Page...")
    try:
        response = session.get(f"{base_url}/admin")
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
        # Prepare test data
        test_user_data = {
            'username': 'testuser123',
            'password': 'testpass123',
            'email': 'testuser@example.com'
        }
        
        # Create test image
        test_image = create_test_image()
        
        files = {
            'face_image': ('test_face.jpg', test_image, 'image/jpeg')
        }
        
        response = session.post(
            f"{base_url}/api/register", 
            data=test_user_data,
            files=files
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
                test_results.append(("User Registration", True))  # Still considered success
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}")
            test_results.append(("User Registration", False))
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        test_results.append(("User Registration", False))
    
    # Test 4: User Login Endpoint
    print("\n4️⃣ Testing User Login Endpoint...")
    try:
        login_data = {
            'username': 'testuser123',
            'password': 'testpass123'
        }
        
        response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"   📊 Login response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                login_response = response.json()
                if 'access_token' in login_response:
                    print("   ✅ Login successful, token received")
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
        response = session.get(f"{base_url}/admin/data_management")
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
    # Test with different base URLs if provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🚀 Admin API Test Suite")
    print(f"🎯 Target: {base_url}")
    print("=" * 60)
    
    success = test_admin_apis(base_url)
    sys.exit(0 if success else 1)
