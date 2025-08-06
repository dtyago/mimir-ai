#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Mimir API
Tests all core functionality: registration, login, document upload, and chat
"""

import requests
import json
import sys
import os
import time
from io import BytesIO
from pathlib import Path


def create_test_pdf():
    """Create a simple test PDF document"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, "Test Document for Mimir API")
        c.drawString(100, 730, "This is a test document containing sample information.")
        c.drawString(
            100, 710, "The AI should be able to answer questions about this content."
        )
        c.drawString(100, 690, "Test question: What is this document about?")
        c.drawString(
            100, 670, "Answer: This is a test document for the Mimir API system."
        )
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer
    except ImportError:
        print("⚠️  reportlab not available, skipping PDF upload test")
        return None


def load_test_image():
    """Load the test image for facial recognition"""
    test_image_path = "./test/data/login-test.jpg"
    if os.path.exists(test_image_path):
        print(
            f"   📸 Using facial recognition test image: {os.path.basename(test_image_path)}"
        )
        with open(test_image_path, "rb") as f:
            return BytesIO(f.read())
    else:
        print(f"❌ Test image not found at: {test_image_path}")
        return None


def test_comprehensive_apis(base_url="http://localhost:8000"):
    """Test complete API workflow"""
    print(f"🧪 Comprehensive API Test Suite")
    print(f"🎯 Target: {base_url}")
    print("=" * 60)

    session = requests.Session()
    test_results = []

    # Test 1: Health Check
    print("1️⃣ Testing Health Endpoint...")
    try:
        response = session.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   ✅ Azure OpenAI: {health_data['azure_openai_configured']}")
            print(f"   ✅ ChromaDB: {health_data['chromadb_configured']}")
            test_results.append(("Health Check", True))
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            test_results.append(("Health Check", False))
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        test_results.append(("Health Check", False))
        return False

    # Test 2: User Registration
    print("\n2️⃣ Testing User Registration...")
    try:
        test_image = load_test_image()
        if test_image:
            files = {
                "email": (None, "test_user_comprehensive@example.com"),
                "name": (None, "Test User Comprehensive"),
                "role": (None, "Analyst-Gaming"),
                "file": ("login-test.jpg", test_image, "image/jpeg"),
            }
            response = session.post(
                f"{base_url}/admin/register_user", files=files, timeout=30
            )

            if response.status_code == 200:
                print("   ✅ User registration successful")
                test_results.append(("User Registration", True))
            else:
                print(f"   ❌ Registration failed: {response.status_code}")
                if response.text:
                    print(f"   📄 Response: {response.text[:200]}")
                test_results.append(("User Registration", False))
        else:
            print("   ❌ No test image available")
            test_results.append(("User Registration", False))
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        test_results.append(("User Registration", False))

    # Test 3: User Login
    print("\n3️⃣ Testing User Login...")
    auth_token = None
    try:
        test_image = load_test_image()
        if test_image:
            files = {"file": ("login-test.jpg", test_image, "image/jpeg")}
            response = session.post(f"{base_url}/user/login", files=files, timeout=30)

            if response.status_code == 200:
                try:
                    login_data = response.json()
                    auth_token = login_data.get("access_token")
                    username = login_data.get("username", "Unknown")
                    print(f"   ✅ Login successful, token received")
                    print(f"   👤 User: {username}")
                    test_results.append(("User Login", True))
                except:
                    print("   ⚠️  Login response not JSON, but status 200")
                    test_results.append(("User Login", True))
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                test_results.append(("User Login", False))
        else:
            print("   ❌ No test image available")
            test_results.append(("User Login", False))
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        test_results.append(("User Login", False))

    # Test 4: Document Upload (if we have auth token)
    print("\n4️⃣ Testing Document Upload...")
    if auth_token:
        try:
            test_pdf = create_test_pdf()
            if test_pdf:
                headers = {"Authorization": f"Bearer {auth_token}"}
                files = {"file": ("test_document.pdf", test_pdf, "application/pdf")}
                response = session.post(
                    f"{base_url}/user/upload", files=files, headers=headers, timeout=30
                )

                if response.status_code == 200:
                    print("   ✅ Document upload successful")
                    test_results.append(("Document Upload", True))
                else:
                    print(f"   ❌ Upload failed: {response.status_code}")
                    if response.text:
                        print(f"   📄 Response: {response.text[:200]}")
                    test_results.append(("Document Upload", False))
            else:
                print("   ⚠️  PDF creation not available, skipping upload test")
                test_results.append(("Document Upload", "Skipped"))
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            test_results.append(("Document Upload", False))
    else:
        print("   ⚠️  No auth token, skipping upload test")
        test_results.append(("Document Upload", "Skipped"))

    # Test 5: Chat Functionality (if we have auth token)
    print("\n5️⃣ Testing Chat Functionality...")
    if auth_token:
        try:
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json",
            }
            chat_data = {"user_input": "What is this document about?"}
            response = session.post(
                f"{base_url}/user/chat", json=chat_data, headers=headers, timeout=30
            )

            if response.status_code == 200:
                try:
                    chat_response = response.json()
                    ai_response = chat_response.get("ai_response", "No response")
                    print(f"   ✅ Chat successful")
                    print(f"   🤖 AI Response: {ai_response[:100]}...")
                    test_results.append(("Chat Functionality", True))
                except:
                    print("   ⚠️  Chat response not JSON, but status 200")
                    test_results.append(("Chat Functionality", True))
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
                if response.text:
                    print(f"   📄 Response: {response.text[:200]}")
                test_results.append(("Chat Functionality", False))
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
            test_results.append(("Chat Functionality", False))
    else:
        print("   ⚠️  No auth token, skipping chat test")
        test_results.append(("Chat Functionality", "Skipped"))

    # Test 6: Admin Data Management
    print("\n6️⃣ Testing Admin Data Management...")
    try:
        response = session.get(f"{base_url}/admin/data_management", timeout=30)
        if response.status_code == 200:
            print("   ✅ Admin data management accessible")
            test_results.append(("Admin Functions", True))
        else:
            print(f"   ❌ Admin functions failed: {response.status_code}")
            test_results.append(("Admin Functions", False))
    except Exception as e:
        print(f"   ❌ Admin functions error: {e}")
        test_results.append(("Admin Functions", False))

    # Results Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)

    passed_tests = 0
    total_tests = 0

    for test_name, result in test_results:
        if result == "Skipped":
            status = "⏭️  SKIP"
        elif result:
            status = "✅ PASS"
            passed_tests += 1
        else:
            status = "❌ FAIL"

        if result != "Skipped":
            total_tests += 1

        print(f"{status} {test_name}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(
        f"\n🎯 Success Rate: {passed_tests}/{total_tests} tests ({success_rate:.1f}%)"
    )

    if success_rate >= 80:
        print("🎉 COMPREHENSIVE TESTS PASSED!")
        return True
    else:
        print("⚠️  SOME COMPREHENSIVE TESTS FAILED")
        return False


if __name__ == "__main__":
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print("🚀 Mimir API Comprehensive Test Suite")
    print(f"🎯 Testing complete workflow at: {base_url}")
    print(f"⏱️  This may take 2-3 minutes due to AI processing")
    print("=" * 60)

    success = test_comprehensive_apis(base_url)
    sys.exit(0 if success else 1)
