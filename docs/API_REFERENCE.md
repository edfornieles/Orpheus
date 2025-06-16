# API Reference

## Endpoints

### TTS Generation

#### Generate Speech
```http
POST /generate
```

**Request Body:**
```json
{
  "text": "Text to convert to speech",
  "voice": "voice_name",
  "precision": "FP8|FP16",
  "emotion": "optional_emotion",
  "speed": 1.0
}
```

**Response:**
```json
{
  "audio_url": "path/to/audio.mp3",
  "duration": 2.5,
  "text": "processed_text",
  "voice": "voice_name",
  "precision": "FP8"
}
```

### Chat Integration

#### Send Message
```http
POST /chat
```

**Request Body:**
```json
{
  "message": "User message",
  "voice": "voice_name",
  "context": "optional_context",
  "emotion": "optional_emotion"
}
```

**Response:**
```json
{
  "response": "AI response text",
  "audio_url": "path/to/audio.mp3",
  "duration": 2.5,
  "voice": "voice_name"
}
```

### Voice Management

#### List Voices
```http
GET /voices
```

**Response:**
```json
{
  "voices": [
    {
      "name": "voice_name",
      "gender": "male|female",
      "archetype": "archetype_name",
      "characteristics": ["char1", "char2"]
    }
  ]
}
```

#### Get Voice Details
```http
GET /voices/{voice_name}
```

**Response:**
```json
{
  "name": "voice_name",
  "gender": "male|female",
  "archetype": "archetype_name",
  "characteristics": ["char1", "char2"],
  "example_text": "Example text",
  "supported_emotions": ["emotion1", "emotion2"]
}
```

### System Management

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "api_status": {
    "openai": "connected",
    "baseten": "connected"
  }
}
```

#### System Status
```http
GET /status
```

**Response:**
```json
{
  "active_requests": 5,
  "cache_size": 100,
  "memory_usage": "500MB",
  "cpu_usage": "25%",
  "api_usage": {
    "openai": {
      "requests": 100,
      "tokens": 5000
    },
    "baseten": {
      "requests": 50,
      "tokens": 2500
    }
  }
}
```

## Error Responses

### Common Error Codes

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  }
}
```

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Error Examples

#### Invalid API Key
```json
{
  "error": {
    "code": "AUTH_ERROR",
    "message": "Invalid API key",
    "details": {
      "service": "openai"
    }
  }
}
```

#### Rate Limit Exceeded
```json
{
  "error": {
    "code": "RATE_LIMIT",
    "message": "Rate limit exceeded",
    "details": {
      "retry_after": 60
    }
  }
}
```

## Authentication

### API Key Authentication
Add your API keys to the request headers:
```http
X-OpenAI-Key: your_openai_api_key
X-Baseten-Key: your_baseten_api_key
```

### Environment Variables
Alternatively, set API keys in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
BASETEN_API_KEY=your_baseten_api_key
MODEL_ID=your_model_id
```

## Rate Limits

### OpenAI API
- 3 requests per second
- 200,000 tokens per minute
- 3,000 requests per minute

### Baseten API
- 10 requests per second
- 1,000 requests per minute
- 100,000 tokens per hour

## Best Practices

1. **Error Handling**
   - Implement exponential backoff
   - Handle rate limits gracefully
   - Log errors for debugging

2. **Performance**
   - Use FP8 for faster generation
   - Implement caching
   - Batch requests when possible

3. **Security**
   - Keep API keys secure
   - Use HTTPS
   - Validate input data

4. **Monitoring**
   - Track API usage
   - Monitor response times
   - Log important events 