#!/usr/bin/env python3
"""
🎭 Orpheus TTS Enhanced Voice Server Launcher
===========================================

Easy launcher for the Orpheus TTS Enhanced Voice Server with 44 archetype voices.

Usage:
    python launch.py                    # Default launch (port 5556)
    python launch.py --port 8080       # Custom port
    python launch.py --help            # Show help
"""

import argparse
import os
import sys
import webbrowser
import time
import subprocess
from pathlib import Path

def print_header():
    """Print the application header"""
    print("\n" + "="*80)
    print("🎭 ORPHEUS TTS ENHANCED VOICE SERVER")
    print("   44 Archetype Voices • ChatGPT Integration • Speech-to-Text")
    print("="*80)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import flask
        import openai
        import requests
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements_optimized.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\n🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("💡 Create .env file with your API keys:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        print("   ORPHEUS_API_KEY=your_orpheus_api_key_here (optional)")
        return False
    
    # Read .env file and check for OpenAI key
    with open(env_file, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY=' in content and 'sk-' in content:
            print("✅ Environment configuration found")
            return True
        else:
            print("⚠️  OpenAI API key not found in .env file")
            print("💡 Add: OPENAI_API_KEY=your_openai_api_key_here")
            return False

def display_interfaces(port):
    """Display available interfaces"""
    base_url = f"http://localhost:{port}"
    
    print(f"\n🌐 AVAILABLE INTERFACES (Server running on port {port})")
    print("-" * 60)
    print(f"🎭 Archetype Voice Tester:  {base_url}/archetype-tester")
    print(f"🎪 Voice Gallery:           {base_url}/voices")
    print(f"💬 Chat Interface:          {base_url}/chat")
    print(f"⚡ Ultra Fast TTS:          {base_url}/ultra-fast")
    print(f"🔧 Debug Interface:         {base_url}/debug")
    print(f"📊 Main Dashboard:          {base_url}/")
    print("-" * 60)
    print("\n🎯 FEATURED: Try the Archetype Voice Tester for all 44 voices!")

def start_server(port):
    """Start the Enhanced Voice Server"""
    print(f"\n🚀 Starting Enhanced Voice Server on port {port}...")
    
    try:
        # Import and run the server
        os.environ['FLASK_PORT'] = str(port)
        
        # Run the server script
        subprocess.run([sys.executable, 'enhanced_voice_server_optimized.py', '--port', str(port)])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Check that the port is not already in use")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="🎭 Orpheus TTS Enhanced Voice Server Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py                    # Default launch (port 5556)
  python launch.py --port 8080       # Custom port
  python launch.py --no-browser      # Don't open browser
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5556,
        help='Port to run the server on (default: 5556)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    
    parser.add_argument(
        '--interface',
        choices=['archetype-tester', 'voices', 'chat', 'ultra-fast', 'debug', 'main'],
        default='archetype-tester',
        help='Which interface to open in browser (default: archetype-tester)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env_file():
        print("\n⚠️  Warning: Server may not work properly without API keys")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Display interface information
    display_interfaces(args.port)
    
    # Open browser if requested
    if not args.no_browser:
        interface_map = {
            'archetype-tester': '/archetype-tester',
            'voices': '/voices',
            'chat': '/chat',
            'ultra-fast': '/ultra-fast',
            'debug': '/debug',
            'main': '/'
        }
        
        url = f"http://localhost:{args.port}{interface_map[args.interface]}"
        print(f"\n🌐 Opening {args.interface} interface in browser...")
        
        # Delay browser opening to let server start
        def open_browser():
            time.sleep(3)  # Wait for server to start
            webbrowser.open(url)
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # Start the server
    start_server(args.port)

if __name__ == "__main__":
    main() 