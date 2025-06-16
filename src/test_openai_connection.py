#!/usr/bin/env python3

import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    print("🔑 Testing OpenAI API connection...")
    print(f"API Key (last 8 chars): ...{os.getenv('OPENAI_API_KEY')[-8:]}")
    
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Hello, this is a test message. Please respond briefly.'}],
        max_tokens=50
    )
    
    print('✅ OpenAI API working successfully!')
    print('📝 Response:', response.choices[0].message.content)
    
except Exception as e:
    print('❌ OpenAI API error:', str(e))
    print('🔍 Error type:', type(e).__name__) 