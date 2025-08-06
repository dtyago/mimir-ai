#!/usr/bin/env python3
"""
Enhanced RAG System Test Suite
Tests the complete enhanced RAG functionality including multiple data sources
"""

import requests
import json
import sys
import os
import time
from io import BytesIO
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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


def create_test_pdf():
    """Create a simple test PDF document"""
    try:
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, "Enhanced RAG Test Document")
        c.drawString(
            100,
            730,
            "This document contains information about business analytics and gaming.",
        )
        c.drawString(
            100,
            710,
            "Gaming Analytics: Track player engagement, retention, and monetization.",
        )
        c.drawString(
            100,
            690,
            "Business Metrics: Revenue, user growth, and market performance indicators.",
        )
        c.drawString(
            100,
            670,
            "Leadership Strategy: Vision, partnerships, and portfolio management.",
        )
        c.drawString(
            100,
            650,
            "Data Analysis: Cohort analysis, A/B testing, and predictive analytics.",
        )
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer
    except ImportError:
        print("⚠️  reportlab not available, skipping PDF creation")
        return None


def load_test_image(role=None):
    """Load the appropriate test image for facial recognition based on role"""
    if role is None:
        image_path = "./test/data/default.jpg"
    else:
        image_path = get_image_path_for_role(role)

    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return BytesIO(f.read())
    else:
        # Try fallback options
        fallback_paths = ["./test/data/default.jpg", "./test/data/login-test.jpg"]
        for fallback in fallback_paths:
            if os.path.exists(fallback):
                print(
                    f"❌ Test image not found at: {image_path}, using fallback: {fallback}"
                )
                with open(fallback, "rb") as f:
                    return BytesIO(f.read())

        print(f"❌ No test images found")
        return None


def test_enhanced_rag_system(base_url="http://localhost:8000"):
    """Test the enhanced RAG system with multiple data sources"""
    print(f"🧠 Enhanced RAG System Test Suite")
    print(f"🎯 Target: {base_url}")
    print("=" * 80)

    session = requests.Session()
    test_results = []

    # Test 1: Health Check
    print("1️⃣ Testing System Health...")
    try:
        response = session.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ System Status: {health_data['status']}")
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

    # Test 2: Setup Enhanced RAG Data
    print("\n2️⃣ Setting up Enhanced RAG Data...")
    try:
        # Populate sample data
        response = session.post(
            f"{base_url}/admin/rag/populate_sample_data", timeout=30
        )
        if response.status_code == 200:
            print("   ✅ Sample data populated successfully")
            test_results.append(("RAG Data Setup", True))
        else:
            print(f"   ❌ Sample data setup failed: {response.status_code}")
            test_results.append(("RAG Data Setup", False))
    except Exception as e:
        print(f"   ❌ RAG data setup error: {e}")
        test_results.append(("RAG Data Setup", False))

    # Test 3: Check RAG Collection Status
    print("\n3️⃣ Checking RAG Collection Status...")
    try:
        response = session.get(f"{base_url}/admin/rag/collection_status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(
                f"   ✅ Common Knowledge: {status_data['common_knowledge']['document_count']} docs"
            )
            print(f"   ✅ Data Mart: {status_data['data_mart']['document_count']} docs")
            print(
                f"   ✅ Role Collections: {len(status_data['role_collections'])} collections"
            )
            test_results.append(("Collection Status", True))
        else:
            print(f"   ❌ Collection status check failed: {response.status_code}")
            test_results.append(("Collection Status", False))
    except Exception as e:
        print(f"   ❌ Collection status error: {e}")
        test_results.append(("Collection Status", False))

    # Test 4: User Registration and Login for each role
    roles_to_test = get_configured_roles()
    auth_tokens = {}

    for i, role in enumerate(roles_to_test, 1):
        print(f"\n4.{i} Testing Role: {role}")

        # Register user
        try:
            test_image = load_test_image(role)
            if test_image:
                # Get the appropriate image filename based on role
                image_path = get_image_path_for_role(role)
                image_filename = os.path.basename(image_path)

                files = {
                    "email": (
                        None,
                        f'test_{role.lower().replace("-", "_")}@example.com',
                    ),
                    "name": (None, f"Test User {role}"),
                    "role": (None, role),
                    "file": (image_filename, test_image, "image/jpeg"),
                }
                response = session.post(
                    f"{base_url}/admin/register_user", files=files, timeout=30
                )

                if response.status_code == 200:
                    print(f"     ✅ Registration successful for {role}")

                    # Login user
                    test_image = load_test_image(role)
                    files = {"file": (image_filename, test_image, "image/jpeg")}
                    login_response = session.post(
                        f"{base_url}/user/login", files=files, timeout=30
                    )

                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        auth_tokens[role] = login_data.get("access_token")
                        print(f"     ✅ Login successful for {role}")
                        test_results.append((f"Auth Setup - {role}", True))
                    else:
                        print(f"     ❌ Login failed for {role}")
                        test_results.append((f"Auth Setup - {role}", False))
                else:
                    print(f"     ❌ Registration failed for {role}")
                    test_results.append((f"Auth Setup - {role}", False))
            else:
                print(f"     ❌ No test image available for {role}")
                test_results.append((f"Auth Setup - {role}", False))
        except Exception as e:
            print(f"     ❌ Error with {role}: {e}")
            test_results.append((f"Auth Setup - {role}", False))

    # Test 5: Enhanced Chat with Different Data Sources
    print("\n5️⃣ Testing Enhanced Chat Functionality...")

    test_queries = [
        {
            "query": "What are our current business metrics and revenue performance?",
            "expected_context": ["business_metrics", "revenue", "performance"],
            "description": "Business Metrics Query",
        },
        {
            "query": "How can we improve gaming user engagement and retention?",
            "expected_context": ["gaming", "engagement", "retention"],
            "description": "Gaming Strategy Query",
        },
        {
            "query": "What analytics best practices should I follow for data analysis?",
            "expected_context": ["analytics", "best practices", "analysis"],
            "description": "Analytics Guidelines Query",
        },
        {
            "query": "What leadership strategies are recommended for gaming portfolio management?",
            "expected_context": ["leadership", "strategy", "portfolio"],
            "description": "Leadership Strategy Query",
        },
    ]

    for role, token in auth_tokens.items():
        if not token:
            continue

        print(f"\n   📊 Testing Enhanced Chat for {role}:")

        for query_test in test_queries:
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }

                chat_data = {
                    "user_input": query_test["query"],
                    "use_enhanced_rag": True,
                }

                response = session.post(
                    f"{base_url}/user/chat", json=chat_data, headers=headers, timeout=45
                )

                if response.status_code == 200:
                    chat_response = response.json()
                    ai_response = chat_response.get("ai_response", "No response")
                    enhanced_rag_used = chat_response.get("enhanced_rag_used", False)
                    data_sources_used = chat_response.get("data_sources_used", [])

                    print(
                        f"     ✅ {query_test['description']}: Enhanced RAG = {enhanced_rag_used}"
                    )
                    print(f"        📁 Data Sources: {', '.join(data_sources_used)}")
                    print(f"        🤖 Response Preview: {ai_response[:100]}...")

                    # Check if expected context appears in response
                    context_found = any(
                        ctx.lower() in ai_response.lower()
                        for ctx in query_test["expected_context"]
                    )

                    test_results.append(
                        (f"Enhanced Chat - {role} - {query_test['description']}", True)
                    )

                else:
                    print(
                        f"     ❌ {query_test['description']} failed: {response.status_code}"
                    )
                    test_results.append(
                        (f"Enhanced Chat - {role} - {query_test['description']}", False)
                    )

            except Exception as e:
                print(f"     ❌ {query_test['description']} error: {e}")
                test_results.append(
                    (f"Enhanced Chat - {role} - {query_test['description']}", False)
                )

    # Test 6: Data Source Availability
    print("\n6️⃣ Testing Data Source Availability...")

    for role, token in auth_tokens.items():
        if not token:
            continue

        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = session.post(
                f"{base_url}/user/chat/data-sources", headers=headers, timeout=10
            )

            if response.status_code == 200:
                sources_data = response.json()
                available_sources = sources_data.get("available_sources", [])
                print(f"   ✅ {role}: {len(available_sources)} data sources available")

                source_names = [
                    src["name"] for src in available_sources if src["enabled"]
                ]
                print(f"      📁 Sources: {', '.join(source_names)}")

                test_results.append((f"Data Sources - {role}", True))
            else:
                print(
                    f"   ❌ Data sources check failed for {role}: {response.status_code}"
                )
                test_results.append((f"Data Sources - {role}", False))

        except Exception as e:
            print(f"   ❌ Data sources error for {role}: {e}")
            test_results.append((f"Data Sources - {role}", False))

    # Test 7: Traditional vs Enhanced RAG Comparison
    print("\n7️⃣ Testing Traditional vs Enhanced RAG...")

    if auth_tokens:
        sample_role = list(auth_tokens.keys())[0]
        sample_token = auth_tokens[sample_role]

        if sample_token:
            test_query = "What should I know about user analytics and engagement?"

            try:
                headers = {
                    "Authorization": f"Bearer {sample_token}",
                    "Content-Type": "application/json",
                }

                # Test traditional RAG
                traditional_data = {"user_input": test_query, "use_enhanced_rag": False}

                print(f"   🔄 Testing Traditional RAG...")
                trad_response = session.post(
                    f"{base_url}/user/chat",
                    json=traditional_data,
                    headers=headers,
                    timeout=30,
                )

                # Test enhanced RAG
                enhanced_data = {"user_input": test_query, "use_enhanced_rag": True}

                print(f"   🔄 Testing Enhanced RAG...")
                enhanced_response = session.post(
                    f"{base_url}/user/chat",
                    json=enhanced_data,
                    headers=headers,
                    timeout=30,
                )

                if (
                    trad_response.status_code == 200
                    and enhanced_response.status_code == 200
                ):
                    trad_data = trad_response.json()
                    enh_data = enhanced_response.json()

                    print(
                        f"   ✅ Traditional RAG: {len(trad_data.get('ai_response', ''))} chars"
                    )
                    print(
                        f"   ✅ Enhanced RAG: {len(enh_data.get('ai_response', ''))} chars"
                    )
                    print(
                        f"   📁 Enhanced used sources: {', '.join(enh_data.get('data_sources_used', []))}"
                    )

                    test_results.append(("RAG Comparison", True))
                else:
                    print(f"   ❌ RAG comparison failed")
                    test_results.append(("RAG Comparison", False))

            except Exception as e:
                print(f"   ❌ RAG comparison error: {e}")
                test_results.append(("RAG Comparison", False))

    # Results Summary
    print("\n" + "=" * 80)
    print("📊 ENHANCED RAG SYSTEM TEST RESULTS")
    print("=" * 80)

    passed_tests = 0
    total_tests = 0

    for test_name, result in test_results:
        if result:
            status = "✅ PASS"
            passed_tests += 1
        else:
            status = "❌ FAIL"

        total_tests += 1
        print(f"{status} {test_name}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(
        f"\n🎯 Success Rate: {passed_tests}/{total_tests} tests ({success_rate:.1f}%)"
    )

    if success_rate >= 80:
        print("🎉 ENHANCED RAG SYSTEM TESTS PASSED!")
        print("\n🚀 System Ready for Multi-Source RAG Operations!")
        return True
    else:
        print("⚠️  SOME ENHANCED RAG TESTS FAILED")
        return False


if __name__ == "__main__":
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print("🧠 Mimir Enhanced RAG System Test Suite")
    print(f"🎯 Testing multi-source RAG capabilities at: {base_url}")
    print(f"⏱️  This comprehensive test may take 5-10 minutes")
    print("=" * 80)

    success = test_enhanced_rag_system(base_url)
    sys.exit(0 if success else 1)
