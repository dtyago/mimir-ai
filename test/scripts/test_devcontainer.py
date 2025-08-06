#!/usr/bin/env python3
"""
DevContainer Environment Test Script
Tests the admin functions and API in the development environment.
"""

import os
import sys
import requests
import json
import time
from pathlib import Path


def check_server_stability():
    """Check if the server is stable (not frequently restarting)"""
    print("\n🔍 Checking Server Stability")
    print("-" * 40)

    # Check if auto-reload is enabled by looking at running processes
    try:
        import subprocess

        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        if "--reload" in result.stdout:
            print("⚠️  Auto-reload detected in server process")
            print("   This can cause intermittent test failures")
            print("   Consider using ./dev-server-stable.sh for testing")
        else:
            print("✅ Server running in stable mode (no auto-reload)")

        # Test server stability with multiple quick requests
        print("   Testing server responsiveness...")
        failures = 0
        for i in range(3):
            try:
                response = requests.get(
                    "http://localhost:8000/health", timeout=3
                )  # Quick 3s timeout
                if response.status_code != 200:
                    failures += 1
            except:
                failures += 1
            time.sleep(0.5)

        if failures == 0:
            print("✅ Server stability check passed")
            return True
        else:
            print(f"⚠️  Server stability issues: {failures}/3 requests failed")
            return False

    except Exception as e:
        print(f"⚠️  Could not check server stability: {e}")
        return False


def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Variables")
    print("-" * 40)

    required_vars = [
        "CHROMADB_LOC",
        "USER_DATA_DIR",
        "TEMP_UPLOAD_DIR",
        "UPLOAD_DIR",
        "FACE_TEMP_DIR",
        "LOG_FILE",
    ]

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False

    return all_set


def test_directory_structure():
    """Test that all data directories exist and are writable"""
    print("\n📁 Testing Directory Structure")
    print("-" * 40)

    dirs_to_test = [
        os.getenv("CHROMADB_LOC"),
        os.getenv("USER_DATA_DIR"),
        os.getenv("TEMP_UPLOAD_DIR"),
        os.getenv("UPLOAD_DIR"),
        os.getenv("FACE_TEMP_DIR"),
        os.path.dirname(os.getenv("LOG_FILE", "")),
    ]

    all_good = True
    for dir_path in dirs_to_test:
        if dir_path:
            path = Path(dir_path)
            if path.exists():
                # Test if writable
                test_file = path / ".test_write"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                    print(f"✅ {dir_path}: Exists and writable")
                except Exception as e:
                    print(f"⚠️  {dir_path}: Exists but not writable: {e}")
                    all_good = False
            else:
                print(f"❌ {dir_path}: Does not exist")
                all_good = False

    return all_good


def test_health_endpoint():
    """Test the health endpoint with retry logic for unstable dev server"""
    print("\n🏥 Testing Health Endpoint")
    print("-" * 40)

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"   🔄 Retry attempt {attempt + 1}/{max_retries}...")
                import time

                time.sleep(retry_delay)

            response = requests.get(
                "http://localhost:8000/health", timeout=10
            )  # Reduced from 30s to 10s
            if response.status_code == 200:
                data = response.json()
                print("✅ Health endpoint responded successfully")
                print(f"   Status: {data.get('status')}")
                print(f"   Azure OpenAI: {data.get('azure_openai_configured')}")
                print(f"   ChromaDB: {data.get('chromadb_configured')}")
                return True
            else:
                print(
                    f"⚠️  Health endpoint returned {response.status_code} (attempt {attempt + 1})"
                )
                if attempt == max_retries - 1:
                    print(f"❌ Health endpoint failed after {max_retries} attempts")
                    return False
        except requests.exceptions.ConnectionError:
            print(
                f"⚠️  Connection failed (attempt {attempt + 1}) - server may be restarting..."
            )
            if attempt == max_retries - 1:
                print("❌ Could not connect to server - is it running?")
                print(
                    "💡 Note: DevContainer uses auto-reload which can cause temporary connection issues"
                )
                return False
        except Exception as e:
            print(f"⚠️  Health check error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                print(f"❌ Health check failed after {max_retries} attempts")
                return False

    return False


def test_admin_login():
    """Test admin login page with retry logic"""
    print("\n🔐 Testing Admin Login")
    print("-" * 40)

    max_retries = 2
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"   🔄 Retry attempt {attempt + 1}/{max_retries}...")
                import time

                time.sleep(1)

            response = requests.get("http://localhost:8000/", timeout=30)
            if response.status_code == 200:
                print("✅ Admin login page accessible")
                if "admin" in response.text.lower():
                    print("✅ Login form detected")
                    return True
                else:
                    print("⚠️  Response received but no login form detected")
                    return False
            else:
                print(
                    f"⚠️  Admin login page returned {response.status_code} (attempt {attempt + 1})"
                )
                if attempt == max_retries - 1:
                    print(f"❌ Admin login page failed after {max_retries} attempts")
                    return False
        except requests.exceptions.ConnectionError:
            print(
                f"⚠️  Connection failed (attempt {attempt + 1}) - server may be restarting..."
            )
            if attempt == max_retries - 1:
                print("❌ Could not connect to server")
                return False
        except Exception as e:
            print(f"⚠️  Admin login test error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                print(f"❌ Admin login test failed after {max_retries} attempts")
                return False

    return False


def test_admin_functions():
    """Test admin function imports and basic functionality"""
    print("\n⚙️  Testing Admin Functions")
    print("-" * 40)

    try:
        # Test imports
        sys.path.append("/workspaces/mimir-ai")
        from app.admin import admin_functions as admin

        print("✅ Admin functions imported successfully")

        # Test disk usage function
        disk_usage = admin.get_disk_usage()
        print(f"✅ Disk usage function works: {disk_usage['total']:.1f}MB total")

        # Test environment variable usage
        temp_dir = os.getenv("TEMP_UPLOAD_DIR", "/tmp/uploads")
        print(f"✅ Environment variables accessible: TEMP_UPLOAD_DIR = {temp_dir}")

        return True
    except Exception as e:
        print(f"❌ Admin functions test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 DevContainer Environment Test Suite")
    print("=" * 50)

    # First run environment checks (these are always needed)
    print("Phase 1: Environment Validation")
    print("-" * 30)

    env_test = test_environment_variables()
    dir_test = test_directory_structure()
    admin_test = test_admin_functions()

    # If environment is not set up properly, warn but continue to health check
    if not (env_test and dir_test and admin_test):
        print("\n⚠️  Environment issues detected - but continuing to test API...")

    # Phase 2: Critical API health check (fail-fast)
    print("\nPhase 2: Critical API Health Check")
    print("-" * 30)

    # First check server stability
    stability_test = check_server_stability()
    if not stability_test:
        print("⚠️  Server stability issues detected - tests may be unreliable")

    health_test = test_health_endpoint()
    if not health_test:
        print("\n" + "=" * 50)
        print("🛑 CRITICAL FAILURE: API Health Check Failed")
        print("=" * 50)
        print("❌ Service is not responding - aborting remaining tests")
        print("\n💡 Next Steps:")
        print("1. Check if server is restarting frequently (auto-reload issue)")
        print("2. Try using stable server: ./dev-server-stable.sh")
        print("3. Start the development server: ./start.sh")
        print("4. Verify .env file contains all required credentials")
        print("5. Ensure devcontainer was rebuilt after configuration changes")
        print("6. Check port 8000 is available and not blocked")
        return False

    # Phase 3: Additional API tests (only if health check passed)
    print("\nPhase 3: Additional API Tests")
    print("-" * 30)

    login_test = test_admin_login()

    # Collect all results
    tests = [
        ("Environment Variables", env_test),
        ("Directory Structure", dir_test),
        ("Admin Functions", admin_test),
        ("Health Endpoint", health_test),
        ("Admin Login", login_test),
    ]

    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)

    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False

    print(
        f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
