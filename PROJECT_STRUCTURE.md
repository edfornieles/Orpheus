# Project Structure

```
Orpheus-TTS/
├── docs/                      # Documentation files
│   ├── README.md             # Main documentation
│   ├── QUICK_START.md        # Quick start guide
│   ├── SETUP_GUIDE.md        # Detailed setup instructions
│   └── PUT_DEPLOYMENT_TO_SLEEP.md  # Deployment management
│
├── src/                      # Source code
│   ├── __init__.py          # Package initialization
│   ├── enhanced_voice_server_optimized.py  # Main server
│   ├── launch.py            # Server launcher
│   ├── clean_voice_server.py # Clean server implementation
│   ├── test_*.py            # Test scripts
│   ├── templates/           # HTML templates
│   └── static/              # Static assets
│
├── .env.example             # Example environment variables
├── requirements_optimized.txt # Python dependencies
├── README.md                # Project overview
├── LICENSE                  # MIT License
└── .gitignore              # Git ignore rules
```

## Directory Descriptions

### `docs/`
Contains all project documentation:
- `README.md`: Complete project documentation
- `QUICK_START.md`: Quick setup guide
- `SETUP_GUIDE.md`: Detailed setup instructions
- `PUT_DEPLOYMENT_TO_SLEEP.md`: Deployment management guide

### `src/`
Main source code directory:
- `__init__.py`: Package initialization
- `enhanced_voice_server_optimized.py`: Main server implementation
- `launch.py`: Server launcher script
- `clean_voice_server.py`: Clean server implementation
- `test_*.py`: Various test scripts
- `templates/`: HTML templates for web interface
- `static/`: Static assets (CSS, JS, images)

### Root Directory
- `.env.example`: Example environment variables
- `requirements_optimized.txt`: Python package dependencies
- `README.md`: Project overview and quick links
- `LICENSE`: MIT License file
- `.gitignore`: Git ignore rules

## Key Files

### Server Files
- `src/enhanced_voice_server_optimized.py`: Main server implementation with all features
- `src/launch.py`: Server launcher with command-line options
- `src/clean_voice_server.py`: Simplified server implementation

### Test Files
- `src/test_env_setup.py`: Environment setup verification
- `src/test_openai_connection.py`: OpenAI API connection test
- `src/test_orpheus_connection.py`: Orpheus TTS connection test

### Configuration
- `.env.example`: Template for environment variables
- `requirements_optimized.txt`: Optimized package dependencies

## Development Guidelines

### Adding New Features
1. Create feature branch from `main`
2. Implement changes in `src/`
3. Update documentation in `docs/`
4. Add tests if applicable
5. Submit pull request

### Code Organization
- Keep related functionality together
- Use clear, descriptive names
- Document public interfaces
- Follow PEP 8 style guide

### Testing
- Run all tests before committing
- Add new tests for new features
- Keep test coverage high

### Documentation
- Keep docs up to date
- Use clear, concise language
- Include examples where helpful
- Document all configuration options

# 📁 Project Structure
## Orpheus TTS Enhanced Voice Server

This document provides a comprehensive overview of the project structure and file purposes.

---

## 🏗️ Core Architecture

```
Orpheus-TTS-main/
├── 🚀 LAUNCHERS & SCRIPTS
│   ├── launch.py                          # Primary launcher with interface selection
│   ├── start_server.sh                    # Interactive bash launcher
│   └── enhanced_voice_server_optimized.py # Main Flask server application
│
├── 📱 WEB INTERFACES (/templates/)
│   ├── archetype_voice_tester.html        # ⭐ Main 44-voice testing interface
│   ├── archetype_voices.html              # Alternative archetype interface
│   ├── index_with_stt.html                # Full-featured STT + ChatGPT interface
│   ├── index_ultra_fast.html              # Speed-optimized TTS interface
│   ├── index_fast.html                    # Fast TTS interface
│   ├── index.html                         # Basic TTS interface
│   └── debug_chat.html                    # Technical debugging interface
│
├── 📚 DOCUMENTATION
│   ├── README.md                          # Comprehensive project documentation
│   ├── SETUP_GUIDE.md                    # Detailed installation guide
│   ├── QUICK_START.md                     # 5-minute setup guide
│   ├── CLOUD_DEPLOYMENT.md               # ☁️ Cloud setup (Baseten, AWS, etc.)
│   ├── PROJECT_STRUCTURE.md              # This file
│   └── LICENSE                            # Apache 2.0 license
│
├── ⚙️ CONFIGURATION
│   ├── requirements_optimized.txt         # Python dependencies
│   ├── .env.example                       # Environment variables template
│   ├── .env                              # Your API keys (create from .env.example)
│   └── .gitignore                        # Git ignore rules
│
├── 🧪 TESTING & DIAGNOSTICS
│   ├── test_env_setup.py                 # Environment validation
│   ├── test_openai_connection.py         # OpenAI API testing
│   ├── test_orpheus_connection.py        # 🎭 Orpheus TTS connection test
│   └── clean_voice_server.py             # Legacy voice server
│
├── 📊 DATA & CACHE
│   ├── generated_audio/                  # Audio file cache
│   ├── output/                          # Output directory
│   ├── orpheus_tts.log                  # Application logs
│   └── emotions.txt                     # Available emotions list
│
├── 🛠️ ORIGINAL ORPHEUS FILES
│   ├── additional_inference_options/     # Advanced inference options
│   ├── finetune/                        # Model fine-tuning scripts
│   ├── orpheus_tts_pypi/               # PyPI package files
│   ├── pretrain/                       # Model pre-training scripts
│   ├── realtime_streaming_example/     # Streaming examples
│   └── demo.mp4                        # Demo video
│
├── 🔧 BUILD & DEPLOYMENT
│   ├── baseten_config.json             # Baseten deployment config
│   ├── service-account-key.json        # Service account credentials
│   └── archive/                        # Archived/backup files
│
└── 🐍 PYTHON ENVIRONMENTS
    ├── .venv/                          # Virtual environment (recommended)
    └── .venv310/                       # Alternative virtual environment
```

---

## 🎯 Quick Navigation

### **🚀 Want to Launch?**
- **Easy**: `python launch.py`
- **Interactive**: `./start_server.sh`
- **Direct**: `python enhanced_voice_server_optimized.py`

### **📖 Need Help?**
- **Quick Setup**: `QUICK_START.md`
- **Detailed Guide**: `SETUP_GUIDE.md`
- **Full Documentation**: `README.md`

### **🎭 Want to Use Interfaces?**
- **Main Interface**: `/archetype-tester` (44 voices)
- **Classic TTS**: `/voices`
- **Chat Mode**: `/chat`
- **Speed Mode**: `/ultra-fast`

### **🔧 Need to Configure?**
- **API Keys**: `.env` (copy from `.env.example`)
- **Voice Settings**: `enhanced_voice_server_optimized.py`
- **Dependencies**: `requirements_optimized.txt`

---

## 📱 Interface Descriptions

### **🎭 Archetype Voice Tester** (`archetype_voice_tester.html`)
**The flagship interface - START HERE!**

**Features:**
- **44 archetype voice cards** in responsive grid
- **FP8/FP16 precision** testing buttons
- **Pre-filled example text** for each archetype
- **Speech-to-Text** input via STT buttons
- **ChatGPT integration** for dynamic conversations
- **Real-time performance metrics**
- **Conversation history** logging

**Use Case:** Primary testing and demonstration interface

### **🎪 Voice Gallery** (`archetype_voices.html`)
**Alternative archetype interface**

**Features:**
- Different layout for archetype testing
- Voice selection and testing
- Custom text input

**Use Case:** Alternative archetype testing layout

### **💬 STT + ChatGPT Interface** (`index_with_stt.html`)
**Full conversational AI interface**

**Features:**
- **Speech-to-Text** recognition
- **ChatGPT conversation** integration
- **Multiple voice selection**
- **Conversation memory**
- **Real-time audio playback**

**Use Case:** Natural voice conversations with AI

### **⚡ Ultra Fast Interface** (`index_ultra_fast.html`)
**Speed-optimized TTS**

**Features:**
- **Minimal latency** design
- **Streamlined controls**
- **Performance monitoring**
- **Quick voice selection**

**Use Case:** Production applications requiring speed

### **🔧 Debug Interface** (`debug_chat.html`)
**Technical diagnostics and debugging**

**Features:**
- **API status monitoring**
- **Error diagnostics**
- **Performance analytics**
- **System health checks**

**Use Case:** Troubleshooting and technical analysis

### **📊 Basic Interfaces** (`index.html`, `index_fast.html`)
**Simple TTS interfaces**

**Features:**
- **Basic text-to-speech**
- **Voice selection**
- **Audio playback**

**Use Case:** Simple TTS without advanced features

---

## 🧠 Core Application Logic

### **`enhanced_voice_server_optimized.py`**
**The heart of the system**

**Key Components:**
- **Flask web server** with CORS support
- **44 archetype voice configurations**
- **Orpheus TTS + OpenAI TTS** integration
- **ChatGPT conversation** handling
- **Audio processing** and caching
- **Error handling** and fallback systems
- **Performance monitoring**

**Key Functions:**
- `generate_speech()`: Main TTS generation
- `apply_archetype_characteristics()`: Voice personality processing
- `/generate`: REST API for TTS
- `/chat`: ChatGPT integration endpoint
- `/archetype-tester`: Main interface route

### **Voice Configuration System**
**VOICE_CONFIGS dictionary structure:**

```python
{
    'archetype_name_gender': {
        'description': 'Human-readable description',
        'type': 'orpheus',
        'orpheus_voice': 'base_voice',  # dan, leah, tara, etc.
        'precision': 'fp8',             # fp8 or fp16
        'max_tokens': 2200,
        'archetype': 'archetype_name',
        'gender': 'male/female',
        'personality_traits': ['trait1', 'trait2'],
        'speaking_patterns': {
            'pace': 1.0,                # Speed multiplier
            'pitch_shift': 0.0,         # Pitch adjustment
            'emphasis_words': ['words'],
            'pause_patterns': ['.', '!'],
            'vocal_characteristics': ['deep', 'soft']
        }
    }
}
```

---

## 🔧 Configuration Files

### **`.env` (Your API Keys)**
**Required environment variables:**
```env
OPENAI_API_KEY=sk-your-key-here     # Required
ORPHEUS_API_KEY=your-key-here       # Optional
ORPHEUS_API_URL=your-url-here       # Optional
DEFAULT_PORT=5556                   # Optional
```

### **`requirements_optimized.txt`**
**Python dependencies:**
- `flask`: Web framework
- `openai`: OpenAI API client
- `requests`: HTTP requests
- `flask-cors`: Cross-origin support
- `python-dotenv`: Environment variable loading

### **`baseten_config.json`**
**Baseten deployment configuration for Orpheus TTS**

---

## 🧪 Testing & Diagnostics

### **`test_env_setup.py`**
**Environment validation script**
- Checks Python version
- Validates dependencies
- Tests imports
- Verifies configuration

### **`test_openai_connection.py`**
**OpenAI API connectivity test**
- Validates API key
- Tests API endpoints
- Checks rate limits
- Measures response times

### **`test_orpheus_connection.py`**
**Orpheus TTS connection test**
- Validates Orpheus TTS connection
- Tests Orpheus TTS functionality
- Checks Orpheus TTS performance

---

## 📊 Data & Logging

### **`generated_audio/`**
**Audio file cache directory**
- Stores generated TTS audio files
- Improves response times for repeated requests
- Organized by voice and content hash

### **`orpheus_tts.log`**
**Application log file**
- Server startup/shutdown events
- API calls and responses
- Error messages and stack traces
- Performance metrics

### **Console Output**
**Real-time logging**
- Request processing status
- API call details
- Error messages
- Performance metrics

---

## 🛠️ Development Files

### **Original Orpheus TTS Components**
- **`additional_inference_options/`**: Advanced inference configurations
- **`finetune/`**: Model fine-tuning utilities
- **`orpheus_tts_pypi/`**: PyPI package components
- **`pretrain/`**: Model pre-training scripts
- **`realtime_streaming_example/`**: Streaming implementation examples

### **Legacy Files**
- **`clean_voice_server.py`**: Previous version of voice server
- **`archive/`**: Backed up or deprecated files

---

## 🚀 Deployment Options

### **Local Development**
```bash
python launch.py                    # Easy launcher
python enhanced_voice_server_optimized.py  # Direct launch
./start_server.sh                   # Interactive launcher
```

### **Production Deployment**
```bash
# With custom configuration
python enhanced_voice_server_optimized.py --port 8080 --host 0.0.0.0

# With environment variables
export FLASK_PORT=8080
export FLASK_HOST=0.0.0.0
python enhanced_voice_server_optimized.py
```

### **Docker Deployment** (potential)
The project structure supports containerization with:
- `requirements_optimized.txt` for dependencies
- Environment variable configuration
- Configurable port and host settings

---

## 🎯 Getting Started Paths

### **🏃‍♂️ I Want to Use It Now**
1. `python launch.py`
2. Visit `http://localhost:5556/archetype-tester`
3. Click FP8 buttons to test voices

### **🔧 I Want to Set It Up Properly**
1. Read `SETUP_GUIDE.md`
2. Configure `.env` file
3. Test with `python test_env_setup.py`
4. Launch with `python launch.py`

### **📚 I Want to Understand Everything**
1. Read `README.md`
2. Explore `PROJECT_STRUCTURE.md` (this file)
3. Review `enhanced_voice_server_optimized.py`
4. Check interface templates in `/templates/`

### **🐛 I'm Having Issues**
1. Check `SETUP_GUIDE.md` troubleshooting section
2. Run `python test_env_setup.py`
3. Check console logs and `orpheus_tts.log`
4. Try different browsers or interfaces

---

**🎭 Ready to explore 44 unique archetype voices? Start with `python launch.py`!** 