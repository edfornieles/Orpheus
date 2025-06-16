# ☁️ Cloud Deployment Guide
## Setting Up Orpheus TTS Online Computing

This guide covers deploying Orpheus TTS on cloud platforms to get the full voice quality and avoid the 404 errors you're seeing.

---

## 🔍 **Current Issue Analysis**

Based on your logs, you're seeing:
```
❌ Orpheus API Error: 404 - {"error": "please check the model_id or environment you provided"}
🔄 Orpheus deployment still waking up - using OpenAI TTS fallback
```

**Root Cause**: Your Baseten deployment is inactive and needs a payment method to activate.

---

## 🚀 **Option 1: Baseten Deployment (Recommended)**

### **Why Baseten?**
- ✅ **Official partner** of Canopy Labs (Orpheus creators)
- ✅ **Optimized performance** for Orpheus TTS
- ✅ **One-click deployment** 
- ✅ **Both FP8 and FP16** precision support
- ✅ **Auto-scaling** and load balancing

### **Step 1: Activate Your Existing Deployment**

Based on your `baseten_config.json`, you already have a deployment that just needs activation:

```json
{
  "deployment_id": "deployment-1",
  "model_version": "w70v863", 
  "api_key": "UPpt0FhL.ttGUuiWb5VvmLBCmcUSsjE92WVnJQaAq",
  "status": "INACTIVE - NEEDS PAYMENT METHOD"
}
```

**Immediate Steps:**
1. **Go to [Baseten Dashboard](https://www.baseten.co/dashboard)**
2. **Add Payment Method**: 
   - Navigate to Account → Billing
   - Add credit card or payment method
   - Billing is pay-per-use (around $0.0025 per second of audio)
3. **Activate Deployment**:
   - Go to your deployment (model ID: `w70v863`)
   - Click "Activate" or "Resume"
4. **Test Connection**:
   ```bash
   curl -X POST https://model-w70v863.api.baseten.co/environments/production/predict \
     -H "Authorization: Api-Key UPpt0FhL.ttGUuiWb5VvmLBCmcUSsjE92WVnJQaAq" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello world", "voice": "dan", "max_tokens": 800}'
   ```

### **Step 2: Update Your .env File**

Once activated, update your `.env`:
```env
# Orpheus TTS via Baseten
ORPHEUS_API_KEY=UPpt0FhL.ttGUuiWb5VvmLBCmcUSsjE92WVnJQaAq
ORPHEUS_API_URL=https://model-w70v863.api.baseten.co/environments/production/predict
ORPHEUS_MODEL_ID=w70v863

# OpenAI (still needed for ChatGPT and fallback)
OPENAI_API_KEY=your-openai-key
```

### **Step 3: Verify Setup**

Test your deployment:
```bash
python test_openai_connection.py  # Should show Orpheus working
python launch.py                 # Launch with working Orpheus
```

---

## 🆕 **Option 2: Fresh Baseten Deployment**

If you want to start fresh or need a different model configuration:

### **Step 1: Deploy from Baseten Library**

1. **Visit**: https://www.baseten.co/library/orpheus-tts/
2. **Click**: "Deploy to Baseten"
3. **Choose Options**:
   - **Model**: Orpheus TTS (latest)
   - **Precision**: FP8 (fast) or FP16 (quality)
   - **Instance**: H100MIG:3g (recommended) or larger
4. **Deploy**: Usually takes 5-10 minutes

### **Step 2: Get Configuration**

After deployment:
1. **Copy Model ID** from dashboard (e.g., `abc123def`)
2. **Get API Key** from Account → API Keys
3. **Note the endpoint**: `https://model-{MODEL_ID}.api.baseten.co/environments/production/predict`

### **Step 3: Update Configuration**

```env
ORPHEUS_API_KEY=your-new-api-key
ORPHEUS_API_URL=https://model-abc123def.api.baseten.co/environments/production/predict
ORPHEUS_MODEL_ID=abc123def
```

---

## 💰 **Baseten Pricing & Usage**

### **Cost Structure**
- **Per-second billing**: ~$0.0025/second of generated audio
- **Cold start**: ~$0.01 per deployment wake-up
- **No monthly minimums**: Pay only for usage

### **Cost Examples**
- **1 minute of audio**: ~$0.15
- **10 minutes daily**: ~$45/month
- **100 requests/day (30s each)**: ~$22.50/month

### **Cost Optimization**
- **Use FP8 mode**: 2x faster = 50% cheaper
- **Keep deployment warm**: Reduces cold start costs
- **Batch requests**: When possible
- **Monitor usage**: Baseten dashboard shows real-time costs

---

## 🔄 **Option 3: Alternative Cloud Platforms**

If Baseten doesn't work for you, here are alternatives:

### **A. RunPod**
```bash
# 1. Deploy Orpheus container on RunPod
# 2. Get endpoint URL
# 3. Configure your .env:
ORPHEUS_API_URL=https://your-runpod-endpoint.runpod.net/generate
ORPHEUS_API_KEY=your-runpod-token
```

### **B. Replicate**
```bash
# 1. Check if Orpheus is available on Replicate
# 2. Use Replicate's Python client
pip install replicate
```

### **C. AWS/GCP with Custom Deployment**
```bash
# 1. Deploy using Orpheus Docker container
# 2. Use EC2/Compute Engine with GPU instances
# 3. Set up load balancer and auto-scaling
```

### **D. Local GPU Setup** (Advanced)
```bash
# If you have a powerful GPU (RTX 4090, A100, etc.)
# 1. Install CUDA and dependencies
# 2. Run Orpheus locally
# 3. Expose as local API
```

---

## 🛠️ **Custom Deployment Options**

### **Using Truss (Baseten's Framework)**

1. **Clone Baseten's Example**:
```bash
git clone https://github.com/basetenlabs/truss-examples.git
cd truss-examples/orpheus-best-performance
```

2. **Customize Configuration**:
```python
# config.yaml
model_name: orpheus-custom
python_version: py39
requirements:
  - torch
  - transformers
  - orpheus-tts
resources:
  cpu: 2
  memory: 8Gi
  gpu: nvidia-h100-mig:3g
```

3. **Deploy**:
```bash
truss push
```

---

## 📊 **Performance Comparison**

| Platform | Setup Time | Cost/Min | Latency | Reliability | Support |
|----------|------------|----------|---------|-------------|---------|
| **Baseten** | 5 min | $0.15 | Low | ⭐⭐⭐⭐⭐ | Official |
| **RunPod** | 15 min | $0.12 | Medium | ⭐⭐⭐⭐ | Community |
| **Replicate** | 10 min | $0.18 | Medium | ⭐⭐⭐⭐ | Good |
| **AWS Custom** | 2 hours | $0.25+ | Low | ⭐⭐⭐ | DIY |
| **Local GPU** | 1 hour | Free* | Lowest | ⭐⭐ | DIY |

*Local GPU: Free runtime, but requires powerful hardware ($1000+ GPU)

---

## 🔧 **Configuration for Your Server**

### **Update enhanced_voice_server_optimized.py**

Your server should already support these environment variables:
```python
ORPHEUS_API_KEY = os.getenv('ORPHEUS_API_KEY') or os.getenv('BASETEN_API_KEY')
ORPHEUS_API_URL = os.getenv('ORPHEUS_API_URL') or f"https://model-{MODEL_ID}.api.baseten.co/environments/production/predict"
```

### **Test Connection**

Add this test to verify your deployment:
```python
# test_orpheus_connection.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_orpheus():
    api_key = os.getenv('ORPHEUS_API_KEY')
    api_url = os.getenv('ORPHEUS_API_URL')
    
    if not api_key or not api_url:
        print("❌ Missing Orpheus API configuration")
        return False
    
    payload = {
        "prompt": "Hello, this is a test.",
        "voice": "dan",
        "max_tokens": 800
    }
    
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            print("✅ Orpheus API working!")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_orpheus()
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **404 "model_id or environment" Error**
```bash
# Check model ID and URL
echo $ORPHEUS_MODEL_ID
echo $ORPHEUS_API_URL

# Verify deployment is active in Baseten dashboard
```

#### **Payment Method Required**
```bash
# Add payment method in Baseten dashboard
# Account → Billing → Add Payment Method
```

#### **Cold Start Delays**
```bash
# Keep deployment warm with periodic requests
# Or use Baseten's "always on" feature (higher cost)
```

#### **Rate Limits**
```bash
# Baseten: Usually very high limits
# Monitor in dashboard: Account → Usage
```

### **Fallback Strategy**

Your server already has a good fallback system:
1. **Try Orpheus TTS** first
2. **Fall back to OpenAI TTS** if Orpheus fails
3. **Log errors** for debugging
4. **Continue working** with reduced voice variety

---

## 🎯 **Recommended Setup**

For your 44 archetype voices, I recommend:

### **Production Setup**
```env
# Primary: Baseten for best quality
ORPHEUS_API_KEY=your-baseten-key
ORPHEUS_API_URL=https://model-w70v863.api.baseten.co/environments/production/predict

# Fallback: OpenAI for reliability  
OPENAI_API_KEY=your-openai-key

# Configuration
DEFAULT_ORPHEUS_PRECISION=fp8  # For speed and cost
ENABLE_FALLBACK=true
```

### **Development Setup**
```env
# Development: OpenAI only (cheaper for testing)
OPENAI_API_KEY=your-openai-key
# ORPHEUS_API_KEY=  # Commented out

# Or limited Orpheus for final testing
ORPHEUS_API_KEY=your-baseten-key
MAX_ORPHEUS_REQUESTS_PER_HOUR=100
```

---

## 🎉 **Quick Start for Your Current Setup**

Based on your `baseten_config.json`, here's the fastest path:

1. **Add Payment Method**:
   - Go to https://www.baseten.co/dashboard
   - Account → Billing → Add Payment Method

2. **Activate Deployment**:
   - Find deployment `w70v863`
   - Click "Activate" or "Resume"

3. **Update .env**:
   ```env
   ORPHEUS_API_KEY=UPpt0FhL.ttGUuiWb5VvmLBCmcUSsjE92WVnJQaAq
   ORPHEUS_API_URL=https://model-w70v863.api.baseten.co/environments/production/predict
   ```

4. **Test**:
   ```bash
   python launch.py --interface archetype-tester
   ```

5. **Enjoy 44 High-Quality Voices**! 🎭

---

**💡 Pro Tip**: Start with the existing Baseten deployment since it's already configured. You can always switch to other platforms later if needed.

Need help with any of these steps? The Baseten dashboard has excellent documentation and support chat! 