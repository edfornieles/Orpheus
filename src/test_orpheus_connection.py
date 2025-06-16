#!/usr/bin/env python3
"""
🎭 Orpheus TTS Connection Test
============================

Test script to verify Orpheus TTS API connection and diagnose issues.
"""

import requests
import os
import json
import time
from dotenv import load_dotenv

def print_header():
    """Print test header"""
    print("\n" + "="*60)
    print("🎭 ORPHEUS TTS CONNECTION TEST")
    print("="*60)

def load_config():
    """Load configuration from environment"""
    load_dotenv()
    
    config = {
        'api_key': os.getenv('ORPHEUS_API_KEY') or os.getenv('BASETEN_API_KEY'),
        'api_url': os.getenv('ORPHEUS_API_URL'),
        'model_id': os.getenv('ORPHEUS_MODEL_ID'),
        'openai_key': os.getenv('OPENAI_API_KEY')
    }
    
    return config

def check_baseten_config():
    """Check baseten_config.json for deployment info"""
    try:
        with open('baseten_config.json', 'r') as f:
            config = json.load(f)
            deployment_info = config.get('baseten_deployment_info', {})
            api_config = deployment_info.get('api_configuration', {})
            
            print("\n📋 BASETEN DEPLOYMENT INFO:")
            print(f"   Status: {deployment_info.get('deployment_status', 'Unknown')}")
            print(f"   Model ID: {api_config.get('model_id', 'Not found')}")
            print(f"   API Key: {api_config.get('api_key', 'Not found')[:20]}...")
            print(f"   Billing: {deployment_info.get('billing', {}).get('status', 'Unknown')}")
            
            return api_config
    except FileNotFoundError:
        print("\n⚠️  baseten_config.json not found")
        return {}
    except Exception as e:
        print(f"\n❌ Error reading baseten_config.json: {e}")
        return {}

def test_orpheus_connection(config):
    """Test Orpheus TTS API connection"""
    api_key = config.get('api_key')
    api_url = config.get('api_url')
    
    if not api_key:
        print("\n❌ ORPHEUS API KEY MISSING")
        print("   Add to .env: ORPHEUS_API_KEY=your-key-here")
        return False
    
    if not api_url:
        print("\n❌ ORPHEUS API URL MISSING")
        print("   Add to .env: ORPHEUS_API_URL=your-url-here")
        return False
    
    print(f"\n🔍 TESTING ORPHEUS CONNECTION:")
    print(f"   URL: {api_url}")
    print(f"   API Key: {api_key[:20]}...")
    
    payload = {
        "prompt": "Hello, this is a connection test.",
        "voice": "dan",
        "max_tokens": 800,
        "precision": "fp8"
    }
    
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("   🚀 Sending test request...")
        start_time = time.time()
        
        response = requests.post(
            api_url, 
            json=payload, 
            headers=headers, 
            timeout=60
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS! ({duration:.1f}s)")
            
            # Check if response contains audio data
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            print(f"   📊 Response: {content_length} bytes, {content_type}")
            
            if content_length > 1000:  # Reasonable audio file size
                print("   🎵 Audio data received!")
                return True
            else:
                print("   ⚠️  Response too small for audio data")
                print(f"   Response: {response.text[:200]}")
                return False
                
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            
            if response.status_code == 404:
                print("   💡 This usually means:")
                print("      - Deployment is inactive (needs payment method)")
                print("      - Wrong model ID or environment")
                print("      - Deployment not found")
            elif response.status_code == 401:
                print("   💡 Authentication failed - check API key")
            elif response.status_code == 403:
                print("   💡 Access denied - check permissions")
            elif response.status_code >= 500:
                print("   💡 Server error - try again later")
                
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ REQUEST TIMEOUT (>60s)")
        print("   💡 Deployment might be cold-starting")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ CONNECTION ERROR")
        print("   💡 Check URL and internet connection")
        return False
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
        return False

def test_openai_fallback(config):
    """Test OpenAI TTS fallback"""
    api_key = config.get('openai_key')
    
    if not api_key:
        print("\n❌ OPENAI API KEY MISSING")
        print("   Add to .env: OPENAI_API_KEY=sk-your-key-here")
        return False
    
    print(f"\n🔍 TESTING OPENAI TTS FALLBACK:")
    print(f"   API Key: {api_key[:20]}...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("   🚀 Sending test request...")
        start_time = time.time()
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="This is a test of the OpenAI TTS fallback system."
        )
        
        duration = time.time() - start_time
        audio_content = response.content
        
        print(f"   ✅ SUCCESS! ({duration:.1f}s)")
        print(f"   📊 Audio: {len(audio_content)} bytes")
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def provide_recommendations(orpheus_working, openai_working, config):
    """Provide recommendations based on test results"""
    print("\n" + "="*60)
    print("📋 RECOMMENDATIONS:")
    print("="*60)
    
    if orpheus_working and openai_working:
        print("🎉 PERFECT SETUP!")
        print("   ✅ Orpheus TTS working (high-quality voices)")
        print("   ✅ OpenAI TTS working (reliable fallback)")
        print("   🎭 Ready to enjoy all 44 archetype voices!")
        
    elif not orpheus_working and openai_working:
        print("⚠️  PARTIAL SETUP (OpenAI only)")
        print("   ❌ Orpheus TTS not working")
        print("   ✅ OpenAI TTS working (fallback active)")
        print("\n💡 TO FIX ORPHEUS:")
        
        baseten_config = check_baseten_config()
        if baseten_config:
            print("   1. Go to https://www.baseten.co/dashboard")
            print("   2. Add payment method (Account → Billing)")
            print("   3. Activate deployment w70v863")
            print("   4. Update .env with Orpheus credentials")
        else:
            print("   1. Visit: https://www.baseten.co/library/orpheus-tts/")
            print("   2. Deploy Orpheus TTS (one-click)")
            print("   3. Add payment method")
            print("   4. Configure .env with API credentials")
        
        print("   5. Run this test again")
        
    elif orpheus_working and not openai_working:
        print("⚠️  ORPHEUS ONLY")
        print("   ✅ Orpheus TTS working")
        print("   ❌ OpenAI TTS not working")
        print("\n💡 TO FIX OPENAI:")
        print("   1. Get API key from https://platform.openai.com/")
        print("   2. Add to .env: OPENAI_API_KEY=sk-your-key")
        print("   3. Test again")
        
    else:
        print("❌ SETUP ISSUES")
        print("   ❌ Orpheus TTS not working")
        print("   ❌ OpenAI TTS not working")
        print("\n💡 IMMEDIATE STEPS:")
        print("   1. Add OpenAI API key to .env (required)")
        print("   2. Test again with: python test_orpheus_connection.py")
        print("   3. Follow CLOUD_DEPLOYMENT.md for Orpheus setup")

def main():
    """Main test function"""
    print_header()
    
    # Load configuration
    config = load_config()
    
    print("\n🔍 CONFIGURATION CHECK:")
    print(f"   Orpheus API Key: {'✅ Set' if config['api_key'] else '❌ Missing'}")
    print(f"   Orpheus API URL: {'✅ Set' if config['api_url'] else '❌ Missing'}")
    print(f"   OpenAI API Key: {'✅ Set' if config['openai_key'] else '❌ Missing'}")
    
    # Check baseten config
    check_baseten_config()
    
    # Test connections
    orpheus_working = False
    openai_working = False
    
    if config['api_key'] and config['api_url']:
        orpheus_working = test_orpheus_connection(config)
    else:
        print("\n⏭️  SKIPPING ORPHEUS TEST (missing configuration)")
    
    if config['openai_key']:
        openai_working = test_openai_fallback(config)
    else:
        print("\n⏭️  SKIPPING OPENAI TEST (missing API key)")
    
    # Provide recommendations
    provide_recommendations(orpheus_working, openai_working, config)
    
    print(f"\n📋 SUMMARY:")
    print(f"   Orpheus TTS: {'✅ Working' if orpheus_working else '❌ Not Working'}")
    print(f"   OpenAI TTS: {'✅ Working' if openai_working else '❌ Not Working'}")
    
    if orpheus_working or openai_working:
        print(f"\n🚀 READY TO LAUNCH:")
        print(f"   python launch.py --interface archetype-tester")
    else:
        print(f"\n🔧 SETUP NEEDED:")
        print(f"   See CLOUD_DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main() 