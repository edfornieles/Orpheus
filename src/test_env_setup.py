#!/usr/bin/env python3
"""
Test script to verify environment variable setup
"""

import os
from dotenv import load_dotenv

def test_env_setup():
    print("🔍 Testing environment variable setup...")
    print("=" * 50)
    
    # Load environment variables
    try:
        load_dotenv()
        print("✅ .env file loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load .env file: {e}")
        return False
    
    # Test each API key
    api_keys = {
        'OPENAI_API_KEY': 'OpenAI API',
        'EXA_API_KEY': 'Exa API', 
        'HF_TOKEN': 'Hugging Face Token',
        'GOOGLE_CLOUD_KEY': 'Google Cloud API',
        'TAVILY_API_KEY': 'Tavily API'
    }
    
    all_loaded = True
    
    for env_var, description in api_keys.items():
        value = os.getenv(env_var)
        if value:
            print(f"✅ {description}: ...{value[-8:]}")
        else:
            print(f"❌ {description}: Not found")
            all_loaded = False
    
    print("=" * 50)
    
    if all_loaded:
        print("🎉 All environment variables loaded successfully!")
        print("🚀 Your server should work perfectly with ChatGPT integration")
    else:
        print("⚠️ Some environment variables are missing")
        print("💡 Check your .env file")
    
    return all_loaded

if __name__ == "__main__":
    test_env_setup() 