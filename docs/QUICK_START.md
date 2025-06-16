# Quick Start Guide

Get Orpheus TTS up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key
- Baseten API key
- Model ID from Baseten

## Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/edfornieles/Orpheus.git
cd Orpheus
```

2. **Set up Python environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements_optimized.txt
```

3. **Configure API keys**
Create `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key_here
BASETEN_API_KEY=your_baseten_api_key_here
MODEL_ID=your_model_id_here
```

4. **Launch the server**
```bash
python src/launch.py
```

5. **Access the interface**
Open your browser and visit:
http://localhost:5556/archetype-tester

## Quick Test

1. Select a voice from the 44 archetypes
2. Enter some text
3. Click "Generate" to hear the result

## Need Help?

- Check the [Setup Guide](SETUP_GUIDE.md) for detailed instructions
- Review [Troubleshooting](TROUBLESHOOTING.md) for common issues
- Create an issue on GitHub for support

## Next Steps

- Explore all 44 archetype voices
- Try different emotional variations
- Test the chat interface
- Customize voice settings

Happy voice generation! 🎭 