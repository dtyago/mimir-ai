#!/usr/bin/env python3
"""
Post-rebuild verification script
Run this immediately after devcontainer rebuild to verify everything works
"""

import os
import subprocess
import sys
from pathlib import Path

def check_permissions():
    """Check if all data directories have correct permissions"""
    print("🔐 Checking Directory Permissions")
    print("-" * 40)
    
    data_dirs = [
        "/workspaces/mimir-api/data/chromadb",
        "/workspaces/mimir-api/data/logs", 
        "/workspaces/mimir-api/data/uploads",
        "/workspaces/mimir-api/data/tmp",
        "/workspaces/mimir-api/data/face_images"
    ]
    
    all_good = True
    for dir_path in data_dirs:
        path = Path(dir_path)
        if path.exists():
            # Check if writable
            test_file = path / ".permission_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                print(f"✅ {dir_path}: Writable")
            except Exception as e:
                print(f"❌ {dir_path}: Not writable - {e}")
                all_good = False
        else:
            print(f"❌ {dir_path}: Does not exist")
            all_good = False
    
    return all_good

def check_environment():
    """Check environment variables"""
    print("\n🌍 Checking Environment Variables")
    print("-" * 40)
    
    required_vars = ['CHROMADB_LOC', 'USER_DATA_DIR', 'TEMP_UPLOAD_DIR']
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    return all_set

def check_user():
    """Check current user and permissions"""
    print("\n👤 Checking User Context")
    print("-" * 40)
    
    try:
        result = subprocess.run(['whoami'], capture_output=True, text=True)
        username = result.stdout.strip()
        print(f"✅ Current user: {username}")
        
        # Check ownership of data directory
        data_dir = Path("/workspaces/mimir-api/data")
        if data_dir.exists():
            stat_info = data_dir.stat()
            print(f"✅ Data directory exists")
            return True
        else:
            print("❌ Data directory missing")
            return False
            
    except Exception as e:
        print(f"❌ User check failed: {e}")
        return False

def main():
    """Run all post-rebuild checks"""
    print("🚀 Post-Rebuild DevContainer Verification")
    print("=" * 50)
    
    checks = [
        ("User Context", check_user),
        ("Environment Variables", check_environment), 
        ("Directory Permissions", check_permissions)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Verification Results")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 DevContainer is ready!")
        print("💡 Next steps:")
        print("   1. Run: ./start.sh")
        print("   2. Test: python3 test_admin_apis.py")
    else:
        print("\n⚠️  Issues found - check the logs above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
