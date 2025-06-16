#!/bin/bash

# 🎭 Orpheus TTS Enhanced Voice Server - Start Script
# ==================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}"
echo "================================================================================"
echo "🎭 ORPHEUS TTS ENHANCED VOICE SERVER"
echo "   44 Archetype Voices • ChatGPT Integration • Speech-to-Text"
echo "================================================================================"
echo -e "${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    echo -e "${YELLOW}💡 Please install Python 3.8+ and try again${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}🔍 Virtual environment found${NC}"
    source .venv/bin/activate
elif [ -d ".venv310" ]; then
    echo -e "${GREEN}🔍 Virtual environment found (.venv310)${NC}"
    source .venv310/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found${NC}"
    echo -e "${YELLOW}💡 Consider creating one: python3 -m venv .venv${NC}"
fi

# Check if requirements are installed
echo -e "${BLUE}🔍 Checking dependencies...${NC}"
if ! python3 -c "import flask, openai, requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Some dependencies missing${NC}"
    echo -e "${BLUE}📦 Installing requirements...${NC}"
    pip install -r requirements_optimized.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo -e "${YELLOW}💡 Create .env file with your OpenAI API key:${NC}"
    echo -e "${YELLOW}   OPENAI_API_KEY=sk-your-key-here${NC}"
    echo -e "${BLUE}🤔 Continue anyway? (y/N): ${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}👋 Setup your .env file and try again${NC}"
        exit 1
    fi
fi

# Display launch options
echo -e "${GREEN}"
echo "🚀 LAUNCH OPTIONS:"
echo "-------------------"
echo "1. 🎭 Archetype Voice Tester (Recommended)"
echo "2. 🎪 Voice Gallery"
echo "3. 💬 Chat Interface"
echo "4. ⚡ Ultra Fast TTS"
echo "5. 🔧 Debug Interface"
echo "6. 📊 Main Dashboard"
echo "7. 🛠️ Custom launch"
echo -e "${NC}"

# Get user choice
echo -e "${BLUE}Choose an interface (1-7, default: 1): ${NC}"
read -r choice

# Set interface based on choice
case $choice in
    1|"") interface="archetype-tester" ;;
    2) interface="voices" ;;
    3) interface="chat" ;;
    4) interface="ultra-fast" ;;
    5) interface="debug" ;;
    6) interface="main" ;;
    7) 
        echo -e "${BLUE}Enter custom port (default: 5556): ${NC}"
        read -r port
        port=${port:-5556}
        echo -e "${BLUE}Enter interface (archetype-tester, voices, chat, ultra-fast, debug, main): ${NC}"
        read -r interface
        interface=${interface:-archetype-tester}
        ;;
    *)
        echo -e "${YELLOW}Invalid choice, using default (archetype-tester)${NC}"
        interface="archetype-tester"
        ;;
esac

# Set default port if not set
port=${port:-5556}

echo -e "${GREEN}"
echo "🎯 LAUNCHING:"
echo "   Interface: $interface"
echo "   Port: $port"
echo "   URL: http://localhost:$port/$interface"
echo -e "${NC}"

# Launch using the Python launcher
echo -e "${BLUE}🚀 Starting server...${NC}"
python3 src/enhanced_voice_server_optimized.py --port "$port"

# If the server fails to start, show error
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Server failed to start${NC}"
    echo -e "${YELLOW}💡 Check the error message above${NC}"
    exit 1
fi 