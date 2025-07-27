#!/usr/bin/env python3
"""
Azure App Service Health Diagnostic Script
Performs comprehensive health checking and debugging for Azure deployment
"""

import requests
import time
import sys
import json

def check_azure_health(base_url, max_attempts=5, wait_time=30):
    """Check Azure App Service health with detailed diagnostics"""
    print(f"🔍 Azure App Service Health Diagnostic")
    print(f"🎯 Target: {base_url}")
    print(f"⏱️  Timeout per request: 15 seconds")
    print(f"🔄 Max attempts: {max_attempts} (waiting {wait_time}s between attempts)")
    print("=" * 60)
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 Attempt {attempt}/{max_attempts}")
        print("-" * 30)
        
        # Test 1: Basic connectivity
        print("1️⃣ Testing basic connectivity...")
        try:
            response = requests.get(base_url, timeout=15)
            print(f"   ✅ Base URL responding: {response.status_code}")
            if response.status_code == 200:
                print(f"   📝 Content length: {len(response.text)} chars")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}...")
        except requests.exceptions.Timeout:
            print("   ❌ Base URL timeout (15s)")
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection error to base URL")
        except Exception as e:
            print(f"   ❌ Base URL error: {e}")
        
        # Test 2: Health endpoint
        print("\n2️⃣ Testing health endpoint...")
        try:
            health_url = f"{base_url}/health"
            response = requests.get(health_url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("   ✅ Health endpoint successful!")
                    print(f"   📊 Status: {data.get('status', 'unknown')}")
                    print(f"   🤖 Azure OpenAI: {data.get('azure_openai_configured', 'unknown')}")
                    print(f"   🗃️  ChromaDB: {data.get('chromadb_configured', 'unknown')}")
                    print(f"   ⏰ Response time: ~{response.elapsed.total_seconds():.2f}s")
                    return True  # Success!
                except json.JSONDecodeError:
                    print(f"   ⚠️  Health responded but invalid JSON: {response.text[:100]}")
            else:
                print(f"   ❌ Health endpoint status: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("   ❌ Health endpoint timeout (15s)")
        except requests.exceptions.ConnectionError:
            print("   ❌ Health endpoint connection error")
        except Exception as e:
            print(f"   ❌ Health endpoint error: {e}")
        
        # Test 3: Container startup diagnostics
        print("\n3️⃣ Container startup analysis...")
        current_time = time.time()
        print(f"   🕐 Current time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
        print(f"   🔄 This is attempt {attempt}/{max_attempts}")
        
        if attempt < max_attempts:
            print(f"\n⏳ Waiting {wait_time} seconds before next attempt...")
            print("   💡 Common Azure startup issues:")
            print("   - Container still initializing (40-60s startup time)")
            print("   - ML model loading (TensorFlow, PyTorch can take 30-60s)")
            print("   - SQLite compilation and ChromaDB initialization")
            print("   - Memory pressure during startup (check if B2 tier sufficient)")
            time.sleep(wait_time)
    
    print(f"\n❌ Health check failed after {max_attempts} attempts")
    print("\n🔧 Troubleshooting Recommendations:")
    print("1. Check Azure portal for container restart events")
    print("2. Access Kudu console: https://mimir-api-prod-bbdadveqe2dha6hp.scm.canadacentral-01.azurewebsites.net")
    print("3. Check container logs in /home/LogFiles/")
    print("4. Verify memory usage (Basic B2: 3.5GB may be insufficient for ML)")
    print("5. Consider upgrading to Basic B3 or Standard S1 tier")
    print("6. Check if container startup timeout needs adjustment")
    
    return False

def main():
    """Run Azure health diagnostics"""
    base_url = "https://mimir-api-prod-bbdadveqe2dha6hp.canadacentral-01.azurewebsites.net"
    
    success = check_azure_health(base_url)
    
    if success:
        print(f"\n🎉 Azure App Service is healthy and responding!")
        print(f"🌐 Ready for production use: {base_url}")
    else:
        print(f"\n⚠️  Azure App Service health check failed")
        print("Check the recommendations above and try again.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
