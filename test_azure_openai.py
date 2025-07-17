#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI configuration
Run this after updating your .env file with actual credentials
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_openai():
    """Test Azure OpenAI connection"""
    
    # Check if all required environment variables are set
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_API_VERSION',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    print("🔍 Checking environment variables...")
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value in ['your-api-key-here', 'your-resource-name.openai.azure.com']:
            missing_vars.append(var)
            print(f"❌ {var}: Not set or using placeholder")
        else:
            print(f"✅ {var}: Configured")
    
    if missing_vars:
        print(f"\n❌ Missing or placeholder values: {', '.join(missing_vars)}")
        print("Please update your .env file with actual Azure OpenAI credentials")
        return False
    
    print("\n🚀 Testing Azure OpenAI connection...")
    
    try:
        from langchain_openai import AzureChatOpenAI
        
        # Initialize Azure OpenAI
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            temperature=0.1,
            max_tokens=100
        )
        
        # Test with a simple prompt
        response = llm.invoke("Hello! Please respond with 'Azure OpenAI is working correctly.'")
        print(f"✅ Success! Response: {response.content}")
        return True
        
    except ImportError:
        print("❌ Missing required packages. Run: pip install langchain-openai")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nCommon issues:")
        print("1. Check your API key is correct")
        print("2. Verify your endpoint URL format")
        print("3. Ensure your deployment name matches exactly")
        print("4. Check your Azure OpenAI resource has the model deployed")
        return False

if __name__ == "__main__":
    test_azure_openai()
