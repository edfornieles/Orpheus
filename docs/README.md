# 🎭 Orpheus TTS Documentation

## 📚 Table of Contents

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Features](#features)
4. [Technical Architecture](#technical-architecture)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)

## Project Overview

Orpheus TTS is a comprehensive text-to-speech system that offers 44 distinct archetype voices, each with unique characteristics and emotional intelligence. The system integrates with ChatGPT for dynamic conversations and includes speech-to-text capabilities.

### Key Components

- **Voice Server**: Core TTS processing and voice management
- **Web Interface**: User-friendly testing and interaction
- **API Integration**: OpenAI and Baseten connectivity
- **Performance Monitoring**: Real-time metrics and analysis

## Getting Started

See our [Quick Start Guide](QUICK_START.md) for immediate setup instructions or the [Setup Guide](SETUP_GUIDE.md) for detailed configuration steps.

## Features

### 🎭 44 Archetype Voices

| Archetype | Male Voice | Female Voice | Characteristics |
|-----------|------------|--------------|----------------|
| **Outbackers** | Dan | Tara | Australian warmth, adventure-loving |
| **Rockers** | Dan (Deep) | Jess | Brutal aggressive energy, savage delivery |
| **Clowns** | Leo | Mia | Theatrical joy, playful expressions |
| **Royals** | Leo | Leah | Regal dignity, commanding presence |
| **Beatniks** | Zac | Zoe | Cool philosophical, artistic soul |
| **Mystics** | Leo | Tara | Ethereal wisdom, mystical knowledge |
| **Fortune Tellers** | Tara | Zoe | Mysterious prophetic, otherworldly |
| **Mad Professors** | Dan | Leah | Brilliant eccentric, scientific passion |
| **Angels** | Leo | Leah | Divine overwhelming grace, celestial |
| **Devils** | Dan | Jess | Dark seductive corruption, tempting |
| **School Masters** | Dan | Leah | Authoritative educational, disciplined |
| **Cowboys** | Dan | Tara | Western rugged, frontier spirit |
| **Greek Philosophers** | Leo | Leah | Ancient wisdom, contemplative |
| **Sprites** | Zac | Mia | Playful magical, whimsical nature |
| **Pirates** | Dan | Jess | Swashbuckling adventure, seafaring |
| **Street Urchins** | Zac | Mia | Street-smart survival, urban grit |
| **Hypnotists** | Dan | Tara | Mesmerizing control, hypnotic power |
| **Sports Coaches** | Dan | Jess | Motivational energy, competitive drive |
| **Vampires** | Dan | Jess | Eternal seductive, dark allure |
| **Punks** | Zac | Jess | Rebellious defiance, anti-establishment |
| **Witches/Wizards** | Leo | Tara | Magical wisdom, spellcasting power |
| **Private Investigators** | Dan | Jess | Detective instincts, noir atmosphere |

### 🛠 Advanced Features

- **Real-time Speech-to-Text** with Web Speech API
- **ChatGPT Integration** for dynamic conversations
- **Emotional Intelligence** with context-aware responses
- **Performance Metrics** and audio analysis
- **Conversation History** logging and management
- **Dynamic Precision Switching** (FP8/FP16)

## Technical Architecture

### Voice Processing Pipeline

1. **Text Analysis**: Archetype-specific preprocessing
2. **Voice Selection**: Dynamic voice mapping
3. **Emotional Processing**: Context-aware emotion application
4. **TTS Generation**: Orpheus TTS or OpenAI fallback
5. **Audio Optimization**: Format conversion and enhancement

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Generate TTS audio |
| `/chat` | POST | ChatGPT integration |
| `/voices` | GET | List available voices |
| `/health` | GET | System health check |
| `/archetype-tester` | GET | Main testing interface |

## API Reference

### Environment Variables

```env
OPENAI_API_KEY=your_openai_api_key_here
BASETEN_API_KEY=your_baseten_api_key_here
MODEL_ID=your_model_id_here
PORT=5556
MAX_TOKENS=150
DEFAULT_PRECISION=FP8
```

### API Parameters

#### TTS Generation

```json
{
  "text": "Text to convert to speech",
  "voice": "voice_name",
  "precision": "FP8|FP16",
  "emotion": "optional_emotion"
}
```

#### Chat Integration

```json
{
  "message": "User message",
  "voice": "voice_name",
  "context": "optional_context"
}
```

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify API keys are correctly set in `.env`
   - Check API key permissions and quotas

2. **Server Connection**
   - Ensure port 5556 is available
   - Check firewall settings

3. **Voice Generation**
   - Verify model ID is correct
   - Check precision mode compatibility

### Performance Optimization

- Use FP8 precision for faster generation
- Implement caching for frequently used voices
- Monitor memory usage with large requests

For more detailed troubleshooting, see our [Setup Guide](SETUP_GUIDE.md). 