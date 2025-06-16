# 🚀 Complete Setup Guide
## Orpheus TTS Enhanced Voice Server

This guide provides detailed instructions for setting up the Orpheus TTS server.

---

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.9-3.11 recommended)
- **10GB+ free space** (for dependencies and audio cache)
- **Internet connection** (for API calls)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Microphone** (optional, for speech-to-text features)
- **Git**
- **A Baseten account with API access**
- **An OpenAI API key**

### API Keys Required
- ✅ **OpenAI API Key** (Required) - Get from [OpenAI Platform](https://platform.openai.com/)
- ⚠️ **Orpheus API Key** (Optional) - Get from [Baseten](https://www.baseten.co/)

---

## 🔧 Setup Guide

### Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# API Keys
OPENAI_API_KEY=sk-your-openai-key-here
BASETEN_API_KEY=your-baseten-key-here
MODEL_ID=yqv0epjw

# Server Configuration
PORT=5556
MAX_TOKENS=800
DEFAULT_PRECISION=fp8

# Optional Settings
DEBUG=False
LOG_LEVEL=INFO
CACHE_ENABLED=True
MAX_CACHE_SIZE=1000

# Voice Settings
DEFAULT_VOICE=dan
DEFAULT_EMOTION=neutral
DEFAULT_SPEED=1.0

# Performance Settings
BATCH_SIZE=4
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30

# Storage Settings
AUDIO_OUTPUT_DIR=generated_audio
LOG_FILE=orpheus_tts.log
```

### Required API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to `OPENAI_API_KEY`

#### Baseten API Key
1. Visit [Baseten](https://baseten.co)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key to `BASETEN_API_KEY`

#### Model ID
1. Get your model ID from Baseten
2. Copy it to `MODEL_ID`

### Python Environment Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements_optimized.txt
```

### Server Configuration

#### Port Configuration
By default, the server runs on port 5556. To change this:

1. Add to your `.env` file:
```env
PORT=your_preferred_port
```

2. Or specify when running:
```bash
python enhanced_voice_server_optimized.py --port your_preferred_port
```

#### Performance Settings

**Token Limit:**
Default is 2200 tokens. To change:
```env
MAX_TOKENS=your_preferred_limit
```

**Precision Mode:**
Choose between speed (fp8) and quality (fp16):
```env
DEFAULT_PRECISION=fp8  # or fp16
```

### Testing Your Setup

#### 1. Verify Environment
```bash
python test_env_setup.py
```

#### 2. Check API Connections
```bash
python test_orpheus_connection.py
python test_openai_connection.py
```

#### 3. Launch Server
```bash
python enhanced_voice_server_optimized.py
```

#### 4. Test Interfaces
Visit these URLs in your browser:
- http://localhost:5556/archetype-tester
- http://localhost:5556/voices
- http://localhost:5556/chat

## Troubleshooting

### Common Issues

#### API Key Issues
- Verify keys are correctly copied
- Check for extra spaces
- Ensure keys are active and have proper permissions

#### Port Issues
- Check if port 5556 is available
- Try a different port
- Check firewall settings

#### Python Issues
- Ensure Python 3.8+ is installed
- Verify virtual environment is activated
- Check all dependencies are installed

### Getting Help

If you encounter issues:
1. Check the server console output
2. Review error messages
3. Check the [README.md](README.md)
4. Open an issue on GitHub

## Next Steps

After setup is complete:
1. Explore the archetype voices
2. Test different emotional expressions
3. Try ChatGPT integration
4. Experiment with different precision modes

---

## 🚀 Launch Options

### Option 1: Easy Launcher (Recommended)

```bash
# Basic launch (port 5556, opens archetype tester)
python launch.py

# Custom port
python launch.py --port 8080

# Different interface
python launch.py --interface chat

# No browser auto-open
python launch.py --no-browser

# Help
python launch.py --help
```

### Option 2: Direct Server Launch

```bash
# Basic launch
python enhanced_voice_server_optimized.py

# Custom port
python enhanced_voice_server_optimized.py --port 8080

# Debug mode
python enhanced_voice_server_optimized.py --debug
```

### Option 3: Shell Script (Unix/macOS)

```bash
# Make executable
chmod +x start_server.sh

# Run
./start_server.sh
```

---

## 🌐 Interface Access

Once the server is running, open your browser and visit:

| Interface | URL | Description |
|-----------|-----|-------------|
| 🎭 **Archetype Tester** | `http://localhost:5556/archetype-tester` | **Main interface** - Test all 44 voices |
| 🎪 Voice Gallery | `http://localhost:5556/voices` | Classic TTS interface |
| 💬 Chat Interface | `http://localhost:5556/chat` | ChatGPT conversations |
| ⚡ Ultra Fast | `http://localhost:5556/ultra-fast` | Speed-optimized TTS |
| 🔧 Debug | `http://localhost:5556/debug` | Technical diagnostics |
| 📊 Dashboard | `http://localhost:5556/` | Server overview |

---

## 🎭 Using the Archetype Voice Tester

### Overview
The **Archetype Voice Tester** is the flagship interface featuring all 44 unique character voices.

### Features
- **44 voice cards** organized by archetype
- **FP8/FP16 precision** testing
- **Pre-written examples** for each archetype
- **Speech-to-Text** input
- **ChatGPT integration**
- **Real-time metrics**

### How to Use

1. **Browse Archetypes**: Scroll through the gallery of 44 voices
2. **Test Voices**: Click **FP8** or **FP16** buttons to hear each voice
3. **Custom Text**: Edit the text in each card
4. **Speech Input**: Click **STT** to use voice input
5. **Chat Mode**: Click **ChatGPT** for conversations
6. **Monitor Performance**: Watch the metrics in real-time

### Understanding the Archetypes

Each archetype has unique characteristics:

- **Personality Traits**: Defining character attributes
- **Speaking Patterns**: Pace, pitch, emphasis
- **Voice Base**: Which core voice is used
- **Example Text**: Showcase phrases

---

## 🔧 Configuration

### Voice Customization

Edit `enhanced_voice_server_optimized.py` to customize voices:

```python
VOICE_CONFIGS = {
    'your_custom_voice': {
        'description': 'Your Custom Voice Description',
        'type': 'orpheus',
        'orpheus_voice': 'dan',  # Base voice
        'precision': 'fp8',
        'personality_traits': ['trait1', 'trait2'],
        'speaking_patterns': {
            'pace': 1.0,           # Speaking speed
            'pitch_shift': 0.0,    # Pitch adjustment
            'emphasis_words': ['word1', 'word2'],
            'pause_patterns': ['.', '!'],
        }
    }
}
```

### Server Settings

Key settings you can modify:

```python
# In enhanced_voice_server_optimized.py
DEFAULT_PORT = 5556
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
CORS_ORIGINS = "*"  # Allow all origins

# Audio settings
SAMPLE_RATE = 24000
AUDIO_FORMAT = "wav"
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. **Orpheus API 404 Errors**
```
❌ Orpheus API Error: 404 - {"error": "please check the model_id or environment you provided"}
```
**Solution**: This is normal if you don't have Orpheus API access. The system automatically falls back to OpenAI TTS.

#### 2. **"Module not found" errors**
```bash
# Reinstall dependencies
pip install -r requirements_optimized.txt

# If still failing, try:
pip install --force-reinstall -r requirements_optimized.txt
```

#### 3. **Port already in use**
```
OSError: [Errno 48] Address already in use
```
**Solution**: Use a different port:
```bash
python launch.py --port 8080
```

#### 4. **OpenAI API errors**
```bash
# Test your API key
python test_openai_connection.py

# Check your .env file
cat .env | grep OPENAI_API_KEY
```

#### 5. **Audio not playing**
- Check browser audio permissions
- Try a different browser
- Check system audio settings
- Clear browser cache

#### 6. **Microphone not working**
- Grant browser microphone permissions
- Check system microphone settings
- Try refreshing the page
- Use HTTPS for better browser support

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Launch with debug
python enhanced_voice_server_optimized.py --debug

# Or set in .env
DEBUG_MODE=true
```

### Log Files

Check these for troubleshooting:

- **Console output**: Real-time server logs
- **orpheus_tts.log**: Application logs
- **Browser console**: Frontend errors (F12 → Console)

---

## 📊 Performance Tips

### Optimization Settings

**For Speed (FP8 Mode):**
- Use FP8 precision voices
- Shorter text inputs
- Disable debug mode

**For Quality (FP16 Mode):**
- Use FP16 precision voices
- Allow longer processing time
- Use specific archetype voices

**For Development:**
- Enable debug mode
- Use localhost
- Monitor logs

---

## 🔄 Updates and Maintenance

### Keeping Updated

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements_optimized.txt

# Restart server
```

### Backup

Important files to backup:
- `.env` (your API keys)
- Custom voice configurations
- Generated audio files (optional)
- Conversation logs (optional)

---

## 🆘 Getting Help

### Before Asking for Help

1. ✅ Check this setup guide
2. ✅ Run diagnostic tests (`test_env_setup.py`)
3. ✅ Check the troubleshooting section
4. ✅ Look at server logs and browser console

### Where to Get Help

1. **Check logs**: Console output and `orpheus_tts.log`
2. **Run diagnostics**: `python test_env_setup.py`
3. **Test APIs**: `python test_openai_connection.py`
4. **Try different browsers**: Chrome, Firefox, Safari
5. **Check GitHub issues**: For known problems
6. **Create new issue**: With detailed error information

### Information to Include in Bug Reports

- Operating system and version
- Python version (`python --version`)
- Browser and version
- Error messages (full text)
- Steps to reproduce
- Console output
- Contents of `.env` file (without API keys)

---

## 🎉 Success!

If you see this in your terminal:
```
🎭 ORPHEUS TTS ENHANCED VOICE SERVER
   44 Archetype Voices • ChatGPT Integration • Speech-to-Text
================================================================================

✅ Core dependencies found
✅ Environment configuration found

🌐 AVAILABLE INTERFACES (Server running on port 5556)
------------------------------------------------------------
🎭 Archetype Voice Tester:  http://localhost:5556/archetype-tester
```

**🎊 Congratulations! Your server is ready!**

Visit **http://localhost:5556/archetype-tester** to start exploring all 44 unique archetype voices!

---

*Need help? Check the troubleshooting section above or create an issue with detailed information.* 

## Prerequisites
- Python 3.8 or higher
- Git
- A Baseten account with API access
- An OpenAI API key

## Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/edfornieles/Orpheus.git
cd Orpheus

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Step 2: Install Dependencies
```bash
pip install -r requirements_optimized.txt
```

## Step 3: Configure Environment Variables
Create a `.env` file in the root directory with the following content:
```
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
BASETEN_API_KEY=your-baseten-key-here
MODEL_ID=yqv0epjw

# Optional Settings
PORT=5556
MAX_TOKENS=800
DEFAULT_PRECISION=fp8  # or fp16 for higher quality
```

### Getting Your API Keys:
1. **Baseten API Key**:
   - Log in to [Baseten](https://app.baseten.co)
   - Go to API Keys section
   - Create a new API key
   - Copy it to `BASETEN_API_KEY` in your `.env` file

2. **OpenAI API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com)
   - Go to API Keys section
   - Create a new API key
   - Copy it to `OPENAI_API_KEY` in your `.env` file

## Step 4: Start the Server
```bash
# Make the start script executable
chmod +x start_server.sh

# Run the server
./start_server.sh
```

## Step 5: Access the Interface
Once the server is running, visit:
- Main Interface: http://localhost:5556/
- Archetype Tester: http://localhost:5556/archetype-tester

## Troubleshooting

### Common Issues:

1. **Port Already in Use**
   ```bash
   # Find the process using port 5556
   lsof -i :5556
   # Kill the process
   kill <PID>
   ```

2. **API Key Errors**
   - Double-check your API keys in the `.env` file
   - Ensure there are no extra spaces or line breaks
   - Verify the keys are active in their respective dashboards

3. **Missing Dependencies**
   ```bash
   pip install -r requirements_optimized.txt
   ```

4. **Python Version Issues**
   ```bash
   # Check Python version
   python --version
   # Should be 3.8 or higher
   ```

## Next Steps
- Try the Archetype Tester interface
- Test different voices and precision modes
- Check out the documentation for advanced features

## Support
If you encounter any issues:
1. Check the [FAQ](docs/FAQ.md)
2. Review the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. Open an issue on GitHub 