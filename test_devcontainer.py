#!/usr/bin/env python3
"""
DevContainer Environment Test Script
Tests the admin functions and API in the development environment.
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Variables")
    print("-" * 40)
    
    required_vars = [
        'CHROMADB_LOC',
        'USER_DATA_DIR', 
        'TEMP_UPLOAD_DIR',
        'UPLOAD_DIR',
        'FACE_TEMP_DIR',
        'LOG_FILE'
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
        os.getenv('CHROMADB_LOC'),
        os.getenv('USER_DATA_DIR'),
        os.getenv('TEMP_UPLOAD_DIR'),
        os.getenv('UPLOAD_DIR'),
        os.getenv('FACE_TEMP_DIR'),
        os.path.dirname(os.getenv('LOG_FILE', ''))
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
    """Test the health endpoint"""
    print("\n🏥 Testing Health Endpoint")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint responded successfully")
            print(f"   Status: {data.get('status')}")
            print(f"   Azure OpenAI: {data.get('azure_openai_configured')}")
            print(f"   ChromaDB: {data.get('chromadb_configured')}")
            return True
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server - is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_admin_login():
    """Test admin login page"""
    print("\n🔐 Testing Admin Login")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ Admin login page accessible")
            if "admin" in response.text.lower():
                print("✅ Login form detected")
                return True
            else:
                print("⚠️  Response received but no login form detected")
                return False
        else:
            print(f"❌ Admin login page returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin login test failed: {e}")
        return False

def test_admin_functions():
    """Test admin function imports and basic functionality"""
    print("\n⚙️  Testing Admin Functions")
    print("-" * 40)
    
    try:
        # Test imports
        sys.path.append('/workspaces/mimir-api')
        from app.admin import admin_functions as admin
        print("✅ Admin functions imported successfully")
        
        # Test disk usage function
        disk_usage = admin.get_disk_usage()
        print(f"✅ Disk usage function works: {disk_usage['total']:.1f}MB total")
        
        # Test environment variable usage
        temp_dir = os.getenv('TEMP_UPLOAD_DIR', '/tmp/uploads')
        print(f"✅ Environment variables accessible: TEMP_UPLOAD_DIR = {temp_dir}")
        
        return True
    except Exception as e:
        print(f"❌ Admin functions test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 DevContainer Environment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Directory Structure", test_directory_structure),
        ("Admin Functions", test_admin_functions),
        ("Health Endpoint", test_health_endpoint),
        ("Admin Login", test_admin_login),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\n💡 Next Steps:")
        print("1. Check that the development server is running: ./start.sh")
        print("2. Verify .env file contains all required credentials")
        print("3. Ensure devcontainer was rebuilt after configuration changes")

if __name__ == "__main__":
    main()
