# 🎭 Orpheus TTS

A comprehensive text-to-speech system featuring 44 distinct archetype voices, emotional intelligence, ChatGPT integration, and speech-to-text capabilities.

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get started in minutes
- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup instructions
- [API Reference](docs/API_REFERENCE.md) - API documentation
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [FAQ](docs/FAQ.md) - Frequently asked questions
- [Deployment Guide](docs/PUT_DEPLOYMENT_TO_SLEEP.md) - Deployment management
- [Project Structure](PROJECT_STRUCTURE.md) - Code organization
- [Main Documentation](docs/README.md) - Complete project documentation

## 🚀 Quick Start

1. Clone the repository
2. Set up your environment (see [Quick Start Guide](docs/QUICK_START.md))
3. Launch the server
4. Visit http://localhost:5556/archetype-tester

## 🌟 Features

- 44 unique archetype voices
- Real-time speech-to-text
- ChatGPT integration
- Multiple precision modes (FP8/FP16)
- Emotional intelligence
- Performance metrics

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 🎨 Archetype Characteristics

### **Voice Modulations**
Each archetype features unique vocal characteristics:

- **Pitch Shifts**: From +0.3 (Angels) to -1.0 (Brutal Rockers)
- **Speaking Pace**: From 0.6 (Devils) to 1.2 (Aggressive Rockers)
- **Emphasis Patterns**: Archetype-specific keyword emphasis
- **Emotional Tags**: Custom emotional expressions per archetype

### **Text Processing**
Archetype-specific text transformations:

- **Angels**: ✧ Divine pauses and sacred emphasis ✧
- **Devils**: ♦ Tempting interruptions and seductive emphasis ♦
- **Rockers**: 🔥💀 ALL CAPS BRUTAL DELIVERY 💀🔥
- **Outbackers**: Mate! Fair dinkum Australian expressions
- **Mystics**: ~*~ Ethereal wisdom and mystical knowledge ~*~

## 🚨 Troubleshooting

### **Common Issues**

#### **Orpheus API 404 Errors**
```
❌ Orpheus API Error: 404 - {"error": "please check the model_id or environment you provided"}
```
**Solution**: This usually means your Orpheus deployment is inactive or needs a payment method. The system automatically falls back to OpenAI TTS. 

**For full Orpheus setup**: See `CLOUD_DEPLOYMENT.md` for detailed cloud deployment instructions.

**Quick fix**: Run `python test_orpheus_connection.py` for diagnosis and next steps.

#### **Missing Dependencies**
```bash
pip install -r requirements_optimized.txt
```

#### **Port Already in Use**
```bash
# Use a different port
python launch.py --port 8080
```

#### **Audio Not Playing**
- Check browser audio permissions
- Verify HTTPS/HTTP settings
- Clear browser cache

### **Environment Variables**
Ensure these are set in your `.env` file:
```env
OPENAI_API_KEY=sk-...                # Required
ORPHEUS_API_KEY=...                  # Optional (for best quality)
ORPHEUS_API_URL=...                  # Optional (for Orpheus TTS)
```

### **Testing Setup**
Run diagnostic tests:
```bash
python test_env_setup.py              # Basic environment check
python test_openai_connection.py      # OpenAI API test
python test_orpheus_connection.py     # Orpheus TTS connection test
```

### **Cloud Deployment**
For setting up Orpheus TTS on cloud platforms (Baseten, AWS, etc.):
- **See**: `CLOUD_DEPLOYMENT.md` for comprehensive cloud setup
- **Quick start**: Your `baseten_config.json` shows an existing deployment
- **Action needed**: Add payment method to activate Baseten deployment

## 📊 Performance Monitoring

The system provides real-time metrics:

- **Generation Time**: Audio creation speed
- **Audio Duration**: Length of generated speech
- **API Response**: Server response times
- **Error Rates**: Success/failure tracking
- **Precision Modes**: FP8 vs FP16 performance

## 🔄 Updates and Maintenance

### **Regular Updates**
- Monitor API status and health
- Update dependencies regularly
- Check for new Orpheus TTS features
- Backup conversation histories

### **Logging**
Logs are stored in:
- `orpheus_tts.log`: System operations
- Console output: Real-time status
- Browser console: Frontend debugging

## 📝 Development

### **Adding New Archetypes**
1. Define voice configuration in `VOICE_CONFIGS`
2. Add archetype processing in `apply_archetype_characteristics()`
3. Update the frontend interface
4. Test with both FP8 and FP16 modes

### **Customizing Interfaces**
Templates are in `/templates/`:
- `archetype_voice_tester.html`: Main testing interface
- `index.html`: Basic TTS interface
- `chat.html`: ChatGPT integration
- `ultra-fast.html`: Optimized interface

## 📞 Support

- [GitHub Issues](https://github.com/edfornieles/Orpheus/issues)
- [Documentation](docs/README.md)
- [FAQ](docs/FAQ.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

**🎭 Ready to explore 44 unique voices? Launch the server and visit http://localhost:5556/archetype-tester to begin!** 