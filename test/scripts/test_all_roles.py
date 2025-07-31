#!/usr/bin/env python3
"""
Test script to verify all 4 new roles work correctly
"""

import requests
from io import BytesIO

def load_test_image():
    """Load the test image for facial recognition"""
    with open('/workspaces/mimir-api/test/login-test.jpg', 'rb') as f:
        return BytesIO(f.read())

def test_role_registration(base_url="http://localhost:8000"):
    """Test registration with different roles"""
    
    roles_to_test = [
        "Analyst-Gaming",
        "Analyst-Non-Gaming", 
        "Leadership-Gaming",
        "Leadership-Non-Gaming"
    ]
    
    print("🧪 Testing All 4 New Roles")
    print("=" * 50)
    
    for i, role in enumerate(roles_to_test, 1):
        print(f"\n{i}️⃣ Testing Role: {role}")
        
        try:
            test_image = load_test_image()
            files = {
                'email': (None, f'test_role_{i}@example.com'),
                'name': (None, f'Test User {role}'),
                'role': (None, role),
                'file': ('login-test.jpg', test_image, 'image/jpeg')
            }
            
            response = requests.post(f"{base_url}/admin/register_user", files=files, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ Registration successful for {role}")
                
                # Test login to verify role is stored correctly
                test_image = load_test_image()
                files = {'file': ('login-test.jpg', test_image, 'image/jpeg')}
                login_response = requests.post(f"{base_url}/user/login", files=files, timeout=30)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    stored_role = login_data.get('role')
                    if stored_role == role:
                        print(f"   ✅ Role correctly stored and retrieved: {stored_role}")
                    else:
                        print(f"   ❌ Role mismatch: expected {role}, got {stored_role}")
                else:
                    print(f"   ❌ Login failed for {role}")
            else:
                print(f"   ❌ Registration failed for {role}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing {role}: {e}")
    
    print(f"\n🎯 Role testing completed!")

if __name__ == "__main__":
    test_role_registration()
