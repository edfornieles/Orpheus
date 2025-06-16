#!/usr/bin/env python3
"""
Optimized Enhanced Voice Server with Streaming Orpheus TTS
Leverages Baseten's TRT-LLM acceleration and H100 MIG GPU support
Now includes OpenAI ChatGPT integration for real conversations
"""

import os
import time
import tempfile
import base64
import subprocess
import json
import re
import asyncio
import aiohttp
import struct
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import io
import requests  # Keep requests for fallback
from openai import OpenAI
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("🔑 Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

# API Keys Configuration - Load from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EXA_API_KEY = os.getenv('EXA_API_KEY') 
HF_TOKEN = os.getenv('HF_TOKEN')
GOOGLE_CLOUD_KEY = os.getenv('GOOGLE_CLOUD_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Validate required API keys
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not found in environment variables!")
    print("💡 Create a .env file with: OPENAI_API_KEY=your_key_here")
else:
    print(f"✅ OpenAI API key loaded: ...{OPENAI_API_KEY[-8:]}")

# Orpheus TTS Configuration - FORCE ACTIVE DEPLOYMENT
BASETEN_API_KEY = os.getenv('BASETEN_API_KEY')
MODEL_ID = os.getenv('MODEL_ID', 'yqv0epjw')  # Default to your deployment ID
ORPHEUS_ENDPOINT = f"https://model-{MODEL_ID}.api.baseten.co/environments/production/predict"
ORPHEUS_STREAM_ENDPOINT = f"https://model-{MODEL_ID}.api.baseten.co/environments/production/predict_stream"
ORPHEUS_SAMPLE_RATE = 24000

# FORCE ORPHEUS ACTIVE - NO FALLBACKS
ORPHEUS_DEPLOYMENT_STATUS = "ACTIVE"  # FORCE ACTIVE
ORPHEUS_MODEL_AVAILABLE = True  # FORCE AVAILABLE

# NO FALLBACK CONFIGURATION - ORPHEUS ONLY
ENABLE_ORPHEUS_FALLBACK = False  # DISABLED
FALLBACK_TO_SYSTEM_TTS = False   # DISABLED - ORPHEUS ONLY

# Performance optimizations
CHUNK_SIZE = 4096  # Optimal chunk size for streaming
MAX_CONCURRENT_STREAMS = 8  # Based on Baseten's 16+ stream support
TARGET_TOKENS_PER_SEC = 83  # Baseten's real-time target
REQUEST_TIMEOUT = 45  # Extended timeout for quality
CONNECTION_POOL_SIZE = 10

# Voice configurations - ORPHEUS FP8 & FP16 TESTING + ARCHETYPE VOICES
VOICE_CONFIGS = {
    # Orpheus FP8 Voices - Speed Optimized
    'orpheus_leah': {
        'description': 'Orpheus FP8: Warm female voice - 2200 max tokens - no truncation!', 
        'type': 'orpheus', 
        'orpheus_voice': 'leah',
        'precision': 'fp8',   # Speed optimized
        'max_tokens': 2200,
        'emotional_range': ['warm', 'expressive', 'friendly', 'empathetic'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.8, 'expressive': 1.1, 'dramatic': 1.4
        }
    },
    'orpheus_jess': {
        'description': 'Orpheus FP8: Youthful female voice - 2200 max tokens - no truncation!', 
        'type': 'orpheus', 
        'orpheus_voice': 'jess',
        'precision': 'fp8',
        'max_tokens': 2200,
        'emotional_range': ['youthful', 'energetic', 'dynamic', 'playful'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.5, 'natural': 0.9, 'expressive': 1.2, 'dramatic': 1.5
        }
    },
    'orpheus_dan': {
        'description': 'Orpheus FP8: Casual male voice - 2200 max tokens - no truncation!', 
        'type': 'orpheus', 
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'emotional_range': ['casual', 'conversational', 'relaxed', 'friendly'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.8, 'expressive': 1.1, 'dramatic': 1.4
        }
    },
    'orpheus_zac': {
        'description': 'Orpheus FP8: Young male voice - 2200 max tokens - no truncation!', 
        'type': 'orpheus', 
        'orpheus_voice': 'zac',
        'precision': 'fp8',
        'max_tokens': 2200,
        'emotional_range': ['enthusiastic', 'energetic', 'youthful', 'upbeat'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.5, 'natural': 0.9, 'expressive': 1.2, 'dramatic': 1.5
        }
    },
    'orpheus_zoe': {
        'description': 'Orpheus FP8: Gentle female voice - 2200 max tokens - no truncation!', 
        'type': 'orpheus', 
        'orpheus_voice': 'zoe',
        'precision': 'fp8',
        'max_tokens': 2200,
        'emotional_range': ['gentle', 'calming', 'soothing', 'peaceful'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.2, 'natural': 0.6, 'expressive': 0.9, 'dramatic': 1.2
        }
    },
    
    # Orpheus FP16 Voices - Quality Testing
    'orpheus_tara_fp16': {
        'description': 'Orpheus FP16: Professional female voice - 2200 max tokens - quality mode', 
        'type': 'orpheus', 
        'orpheus_voice': 'tara',
        'precision': 'fp16',  # Quality optimized
        'max_tokens': 2200,
        'emotional_range': ['professional', 'clear', 'articulate', 'confident'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.3, 'natural': 0.7, 'expressive': 1.0, 'dramatic': 1.3
        }
    },
    'orpheus_leah_fp16': {
        'description': 'Orpheus FP16: Warm female voice - 2200 max tokens - quality mode', 
        'type': 'orpheus', 
        'orpheus_voice': 'leah',
        'precision': 'fp16',
        'max_tokens': 2200,
        'emotional_range': ['warm', 'expressive', 'friendly', 'empathetic'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.8, 'expressive': 1.1, 'dramatic': 1.4
        }
    },
    'orpheus_leo_fp16': {
        'description': 'Orpheus FP16: Sophisticated male voice - 2200 max tokens - quality mode', 
        'type': 'orpheus', 
        'orpheus_voice': 'leo',
        'precision': 'fp16',
        'max_tokens': 2200,
        'emotional_range': ['sophisticated', 'mature', 'authoritative', 'refined'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.3, 'natural': 0.7, 'expressive': 1.0, 'dramatic': 1.3
        }
    },
    'orpheus_mia_fp16': {
        'description': 'Orpheus FP16: Bright female voice - 2200 max tokens - quality mode', 
        'type': 'orpheus', 
        'orpheus_voice': 'mia',
        'precision': 'fp16',
        'max_tokens': 2200,
        'emotional_range': ['bright', 'cheerful', 'articulate', 'engaging'],
        'supported_emotions': ['<laugh>', '<chuckle>', '<sigh>', '<cough>', '<sniffle>', '<groan>', '<yawn>', '<gasp>'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.8, 'expressive': 1.1, 'dramatic': 1.4
        }
    },

    # ========================================
    # ARCHETYPE VOICES - DISTINCT MALE/FEMALE VARIANTS
    # ========================================
    
    # OUTBACKERS - Rugged, hearty tone with strong Australian accent
    'archetype_outbacker_male': {
        'description': 'Archetype: Male Outbacker - Rugged, commanding presence with Australian grit',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'outbacker',
        'gender': 'male',
        'personality_traits': ['rugged', 'hearty', 'outdoorsy', 'gruff'],
        'speaking_patterns': {
            'pace': 0.85,  # Slightly slower, deliberate pace
            'pitch_shift': -0.2,  # Deeper voice
            'emphasis_words': ['mate', 'crikey', 'fair dinkum'],
            'pause_patterns': ['..', '...'],  # Thoughtful pauses
            'vocal_characteristics': ['gravelly', 'resonant']
        }
    },
    'archetype_outbacker_female': {
        'description': 'Archetype: Female Outbacker - Strong, warm presence with Australian charm',
        'type': 'orpheus',
        'orpheus_voice': 'tara',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'outbacker',
        'gender': 'female',
        'personality_traits': ['confident', 'warm', 'outdoorsy', 'strong'],
        'speaking_patterns': {
            'pace': 0.9,
            'pitch_shift': -0.1,
            'emphasis_words': ['mate', 'beauty', 'too right'],
            'pause_patterns': ['..', '...'],
            'vocal_characteristics': ['warm', 'resonant']
        }
    },

    # ROCKERS - Gritty, rebellious energy
    'archetype_rocker_male': {
        'description': 'Archetype: Male Rocker - Brutally deep, aggressive voice with violent rebellious energy',
        'type': 'orpheus',
        'orpheus_voice': 'dan',  # Changed to Dan for naturally deeper base voice
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'rocker',
        'gender': 'male',
        'personality_traits': ['brutal', 'aggressive', 'violent', 'intense', 'savage', 'raw', 'hostile', 'fierce'],
        'speaking_patterns': {
            'pace': 1.2,  # Faster, more aggressive pace
            'pitch_shift': -1.0,  # Maximum depth, brutally low
            'emphasis_words': ['ROCK', 'RAGE', 'SAVAGE', 'BRUTAL', 'DESTROY', 'ANNIHILATE'],
            'pause_patterns': ['!!', '!!!', '...BRUTAL...'],
            'vocal_characteristics': ['brutally_deep', 'savage_growl', 'aggressive_snarl', 'hostile_intensity']
        }
    },
    'archetype_rocker_female': {
        'description': 'Archetype: Female Rocker - Cool, strong attitude with deep edgy presence',
        'type': 'orpheus',
        'orpheus_voice': 'jess',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'rocker',
        'gender': 'female',
        'personality_traits': ['cool', 'strong', 'rebellious', 'edgy', 'powerful', 'intense'],
        'speaking_patterns': {
            'pace': 1.05,
            'pitch_shift': -0.25,  # Much deeper for female rocker
            'emphasis_words': ['rock', 'wild', 'yeah', 'fierce', 'raw'],
            'pause_patterns': ['!', '...'],
            'vocal_characteristics': ['deep_raspy', 'powerful', 'fierce']
        }
    },

    # CLOWNS - Playful, exaggerated expression
    'archetype_clown_male': {
        'description': 'Archetype: Male Clown - Quirky voice with dramatic vocal shifts',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'clown',
        'gender': 'male',
        'personality_traits': ['quirky', 'playful', 'exaggerated', 'dramatic'],
        'speaking_patterns': {
            'pace': 1.2,
            'pitch_variation': 0.4,
            'emphasis_words': ['ta-da', 'wow', 'amazing'],
            'pause_patterns': ['!', '?!'],
            'vocal_characteristics': ['bouncy', 'animated']
        }
    },
    'archetype_clown_female': {
        'description': 'Archetype: Female Clown - Cheerful, highly expressive voice',
        'type': 'orpheus',
        'orpheus_voice': 'mia',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'clown',
        'gender': 'female',
        'personality_traits': ['cheerful', 'expressive', 'playful', 'energetic'],
        'speaking_patterns': {
            'pace': 1.15,
            'pitch_variation': 0.35,
            'emphasis_words': ['wonderful', 'fantastic', 'amazing'],
            'pause_patterns': ['!', '?!'],
            'vocal_characteristics': ['bubbly', 'dynamic']
        }
    },

    # ROYALS - Elegant, refined speech
    'archetype_royal_male': {
        'description': 'Archetype: Male Royal - Authoritative, poised voice with refined articulation',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'royal',
        'gender': 'male',
        'personality_traits': ['authoritative', 'poised', 'refined', 'dignified'],
        'speaking_patterns': {
            'pace': 0.9,
            'pitch_shift': -0.1,
            'emphasis_words': ['indeed', 'precisely', 'certainly'],
            'pause_patterns': [', ', '; '],
            'vocal_characteristics': ['measured', 'resonant']
        }
    },
    'archetype_royal_female': {
        'description': 'Archetype: Female Royal - Regal, well-enunciated voice with elegant delivery',
        'type': 'orpheus',
        'orpheus_voice': 'leah',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'royal',
        'gender': 'female',
        'personality_traits': ['regal', 'refined', 'elegant', 'composed'],
        'speaking_patterns': {
            'pace': 0.85,
            'pitch_shift': 0.05,
            'emphasis_words': ['indeed', 'quite', 'certainly'],
            'pause_patterns': [', ', '; '],
            'vocal_characteristics': ['clear', 'graceful']
        }
    },

    # BEATNIKS - Relaxed, poetic cadence with deliberate pacing
    'archetype_beatnik_male': {
        'description': 'Archetype: Male Beatnik - Cool, philosophical poet with laid-back wisdom',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'beatnik',
        'gender': 'male',
        'personality_traits': ['philosophical', 'cool', 'artistic', 'contemplative'],
        'vocal_characteristics': ['relaxed_cadence', 'poetic_flow', 'thoughtful_pauses'],
        'emotional_range': ['contemplative', 'artistic', 'philosophical', 'cool'],
        'speaking_patterns': ['deliberate_pacing', 'poetic_rhythm', 'thoughtful_delivery'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.7, 'expressive': 1.0, 'dramatic': 1.3
        }
    },
    'archetype_beatnik_female': {
        'description': 'Archetype: Female Beatnik - Sultry, artistic muse with poetic sensibility',
        'type': 'orpheus',
        'orpheus_voice': 'leah',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'beatnik',
        'gender': 'female',
        'personality_traits': ['sultry', 'artistic', 'poetic', 'introspective'],
        'vocal_characteristics': ['sultry_warmth', 'artistic_flow', 'poetic_grace'],
        'emotional_range': ['introspective', 'artistic', 'passionate', 'thoughtful'],
        'speaking_patterns': ['flowing_poetry', 'intimate_delivery', 'artistic_expression'],
        'temperature_presets': {
            'calm': 0.5, 'natural': 0.8, 'expressive': 1.1, 'dramatic': 1.4
        }
    },

    # MYSTICS - Ethereal, soft-spoken with hypnotic quality
    'archetype_mystic_male': {
        'description': 'Archetype: Male Mystic - Ethereal sage with otherworldly wisdom',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp16',
        'max_tokens': 2200,
        'archetype': 'mystic',
        'gender': 'male',
        'personality_traits': ['ethereal', 'wise', 'otherworldly', 'mystical'],
        'vocal_characteristics': ['flowing_intonation', 'hypnotic_quality', 'ethereal_presence'],
        'emotional_range': ['mystical', 'wise', 'ethereal', 'transcendent'],
        'speaking_patterns': ['flowing_cadence', 'mystical_pauses', 'ethereal_delivery'],
        'temperature_presets': {
            'calm': 0.3, 'natural': 0.6, 'expressive': 0.9, 'dramatic': 1.2
        }
    },
    'archetype_mystic_female': {
        'description': 'Archetype: Female Mystic - Celestial oracle with enchanting wisdom',
        'type': 'orpheus',
        'orpheus_voice': 'zoe',
        'precision': 'fp16',
        'max_tokens': 2200,
        'archetype': 'mystic',
        'gender': 'female',
        'personality_traits': ['celestial', 'enchanting', 'wise', 'mystical'],
        'vocal_characteristics': ['ethereal_softness', 'enchanting_flow', 'celestial_grace'],
        'emotional_range': ['mystical', 'enchanting', 'wise', 'celestial'],
        'speaking_patterns': ['soft_flow', 'mystical_rhythm', 'ethereal_whispers'],
        'temperature_presets': {
            'calm': 0.2, 'natural': 0.5, 'expressive': 0.8, 'dramatic': 1.1
        }
    },

    # FORTUNE TELLERS - Enigmatic, dramatic with varied vocal tension
    'archetype_fortune_teller_male': {
        'description': 'Archetype: Male Fortune Teller - Enigmatic seer with mysterious gravitas',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'fortune_teller',
        'gender': 'male',
        'personality_traits': ['enigmatic', 'mysterious', 'prophetic', 'dramatic'],
        'vocal_characteristics': ['dramatic_pauses', 'varied_tension', 'mysterious_depth'],
        'emotional_range': ['mysterious', 'dramatic', 'prophetic', 'intense'],
        'speaking_patterns': ['dramatic_timing', 'tension_building', 'mysterious_delivery'],
        'temperature_presets': {
            'calm': 0.6, 'natural': 1.0, 'expressive': 1.4, 'dramatic': 1.8
        }
    },
    'archetype_fortune_teller_female': {
        'description': 'Archetype: Female Fortune Teller - Mystical seer with captivating presence',
        'type': 'orpheus',
        'orpheus_voice': 'mia',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'fortune_teller',
        'gender': 'female',
        'personality_traits': ['mystical', 'captivating', 'prophetic', 'alluring'],
        'vocal_characteristics': ['captivating_presence', 'mystical_allure', 'prophetic_intensity'],
        'emotional_range': ['mystical', 'captivating', 'dramatic', 'prophetic'],
        'speaking_patterns': ['entrancing_rhythm', 'dramatic_reveals', 'mystical_intensity'],
        'temperature_presets': {
            'calm': 0.7, 'natural': 1.1, 'expressive': 1.5, 'dramatic': 1.9
        }
    },

    # MAD PROFESSORS - Chaotic energy with brilliant mania
    'archetype_mad_professor_male': {
        'description': 'Archetype: Male Mad Professor - Brilliant scientist with chaotic genius',
        'type': 'orpheus',
        'orpheus_voice': 'zac',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'mad_professor',
        'gender': 'male',
        'personality_traits': ['brilliant', 'chaotic', 'eccentric', 'inventive'],
        'vocal_characteristics': ['chaotic_energy', 'sudden_inflections', 'manic_brilliance'],
        'emotional_range': ['excited', 'manic', 'brilliant', 'chaotic'],
        'speaking_patterns': ['rapid_bursts', 'sudden_pauses', 'excited_delivery'],
        'temperature_presets': {
            'calm': 0.8, 'natural': 1.2, 'expressive': 1.6, 'dramatic': 2.0
        }
    },
    'archetype_mad_professor_female': {
        'description': 'Archetype: Female Mad Professor - Brilliant inventor with delightful chaos',
        'type': 'orpheus',
        'orpheus_voice': 'jess',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'mad_professor',
        'gender': 'female',
        'personality_traits': ['brilliant', 'inventive', 'delightfully_mad', 'eccentric'],
        'vocal_characteristics': ['brilliant_energy', 'delightful_chaos', 'inventive_spirit'],
        'emotional_range': ['excited', 'brilliant', 'inventive', 'chaotic'],
        'speaking_patterns': ['enthusiastic_bursts', 'brilliant_insights', 'chaotic_joy'],
        'temperature_presets': {
            'calm': 0.9, 'natural': 1.3, 'expressive': 1.7, 'dramatic': 2.1
        }
    },

    # ANGELS - Pure, celestial harmonies with commanding presence
    'archetype_angel_male': {
        'description': 'Archetype: Male Angel - Divine messenger with overwhelming celestial authority',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'angel',
        'gender': 'male',
        'personality_traits': ['divine', 'pure', 'commanding', 'celestial', 'transcendent', 'righteous'],
        'speaking_patterns': {
            'pace': 0.7,  # Slower, more deliberate divine speech
            'pitch_shift': 0.25,  # Much higher, ethereal pitch
            'emphasis_words': ['blessed', 'divine', 'holy', 'righteous', 'eternal'],
            'pause_patterns': ['...', '~', '✧'],
            'vocal_characteristics': ['ethereal', 'resonant', 'commanding']
        }
    },
    'archetype_angel_female': {
        'description': 'Archetype: Female Angel - Heavenly presence with pure, overwhelming grace',
        'type': 'orpheus',
        'orpheus_voice': 'leah',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'angel',
        'gender': 'female',
        'personality_traits': ['heavenly', 'pure', 'graceful', 'divine', 'serene', 'transcendent'],
        'speaking_patterns': {
            'pace': 0.65,  # Very slow, flowing celestial speech
            'pitch_shift': 0.3,  # Very high, celestial pitch
            'emphasis_words': ['blessed', 'heavenly', 'divine', 'pure', 'sacred'],
            'pause_patterns': ['...', '~', '✧'],
            'vocal_characteristics': ['ethereal', 'harmonious', 'flowing']
        }
    },

    # DEVILS - Deep, gravelly, mischievous with deliberate pacing
    'archetype_devil_male': {
        'description': 'Archetype: Male Devil - Sinister tempter with overwhelming dark charisma',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'devil',
        'gender': 'male',
        'personality_traits': ['sinister', 'charismatic', 'tempting', 'dark', 'seductive', 'corrupting'],
        'speaking_patterns': {
            'pace': 0.6,  # Very slow, deliberate temptation
            'pitch_shift': -0.4,  # Much deeper, more menacing
            'emphasis_words': ['delicious', 'tempting', 'wicked', 'sinful', 'corrupt'],
            'pause_patterns': ['...', '~', '♦'],
            'vocal_characteristics': ['deep', 'gravelly', 'seductive']
        }
    },
    'archetype_devil_female': {
        'description': 'Archetype: Female Devil - Seductive temptress with overwhelming dark allure',
        'type': 'orpheus',
        'orpheus_voice': 'zoe',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'devil',
        'gender': 'female',
        'personality_traits': ['seductive', 'alluring', 'tempting', 'dangerous', 'corrupting', 'manipulative'],
        'speaking_patterns': {
            'pace': 0.65,  # Slow, sultry temptation
            'pitch_shift': -0.25,  # Lower, more sultry
            'emphasis_words': ['tempting', 'desire', 'wicked', 'sinful', 'delicious'],
            'pause_patterns': ['...', '~', '♦'],
            'vocal_characteristics': ['alluring', 'dark', 'hypnotic']
        }
    },

    # SCHOOL MASTERS - Stern, disciplined yet wise with clipped enunciation
    'archetype_school_master_male': {
        'description': 'Archetype: Male School Master - Distinguished educator with scholarly authority',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp16',
        'max_tokens': 2200,
        'archetype': 'school_master',
        'gender': 'male',
        'personality_traits': ['distinguished', 'scholarly', 'authoritative', 'wise'],
        'vocal_characteristics': ['clipped_enunciation', 'scholarly_precision', 'disciplined_tone'],
        'emotional_range': ['authoritative', 'scholarly', 'disciplined', 'wise'],
        'speaking_patterns': ['precise_delivery', 'educational_rhythm', 'scholarly_pauses'],
        'temperature_presets': {
            'calm': 0.3, 'natural': 0.6, 'expressive': 0.9, 'dramatic': 1.2
        }
    },
    'archetype_school_master_female': {
        'description': 'Archetype: Female School Master - Wise educator with nurturing authority',
        'type': 'orpheus',
        'orpheus_voice': 'tara',
        'precision': 'fp16',
        'max_tokens': 2200,
        'archetype': 'school_master',
        'gender': 'female',
        'personality_traits': ['wise', 'nurturing', 'authoritative', 'scholarly'],
        'vocal_characteristics': ['nurturing_authority', 'wise_guidance', 'scholarly_grace'],
        'emotional_range': ['nurturing', 'wise', 'authoritative', 'encouraging'],
        'speaking_patterns': ['encouraging_tone', 'wise_delivery', 'scholarly_warmth'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.7, 'expressive': 1.0, 'dramatic': 1.3
        }
    },

    # COWBOYS - Laid-back, confident drawl with frontier grit
    'archetype_cowboy_male': {
        'description': 'Archetype: Male Cowboy - Rugged frontiersman with confident drawl',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'cowboy',
        'gender': 'male',
        'personality_traits': ['rugged', 'confident', 'frontier_wise', 'independent'],
        'vocal_characteristics': ['confident_drawl', 'frontier_grit', 'laid_back_rhythm'],
        'emotional_range': ['confident', 'laid_back', 'independent', 'frontier_wise'],
        'speaking_patterns': ['drawling_delivery', 'frontier_pauses', 'confident_cadence'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.8, 'expressive': 1.2, 'dramatic': 1.5
        }
    },
    'archetype_cowboy_female': {
        'description': 'Archetype: Female Cowboy - Strong frontier woman with independent spirit',
        'type': 'orpheus',
        'orpheus_voice': 'leah',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'cowboy',
        'gender': 'female',
        'personality_traits': ['strong', 'independent', 'frontier_smart', 'resilient'],
        'vocal_characteristics': ['strong_drawl', 'independent_spirit', 'frontier_warmth'],
        'emotional_range': ['independent', 'strong', 'resilient', 'frontier_wise'],
        'speaking_patterns': ['confident_drawl', 'frontier_rhythm', 'independent_delivery'],
        'temperature_presets': {
            'calm': 0.5, 'natural': 0.9, 'expressive': 1.3, 'dramatic': 1.6
        }
    },

    # GREEK PHILOSOPHERS - Thoughtful, deliberate pacing
    'archetype_philosopher_male': {
        'description': 'Archetype: Male Philosopher - Timeless voice with deep resonance and wisdom',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'philosopher',
        'gender': 'male',
        'personality_traits': ['wise', 'thoughtful', 'deliberate', 'profound'],
        'speaking_patterns': {
            'pace': 0.7,
            'pitch_shift': -0.1,
            'emphasis_words': ['indeed', 'contemplate', 'wisdom'],
            'pause_patterns': ['...', '; '],
            'vocal_characteristics': ['resonant', 'measured']
        }
    },
    'archetype_philosopher_female': {
        'description': 'Archetype: Female Philosopher - Measured, precise voice with timeless wisdom',
        'type': 'orpheus',
        'orpheus_voice': 'leah',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'philosopher',
        'gender': 'female',
        'personality_traits': ['wise', 'precise', 'thoughtful', 'enlightened'],
        'speaking_patterns': {
            'pace': 0.75,
            'pitch_shift': -0.05,
            'emphasis_words': ['ponder', 'truth', 'wisdom'],
            'pause_patterns': ['...', '; '],
            'vocal_characteristics': ['clear', 'deliberate']
        }
    },

    # SPRITES - Light, quick, whimsical
    'archetype_sprite_male': {
        'description': 'Archetype: Male Sprite - Energetic, unpredictable voice with magical flair',
        'type': 'orpheus',
        'orpheus_voice': 'zac',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'sprite',
        'gender': 'male',
        'personality_traits': ['playful', 'whimsical', 'energetic', 'mischievous'],
        'speaking_patterns': {
            'pace': 1.3,
            'pitch_shift': 0.2,
            'emphasis_words': ['sparkle', 'magic', 'flutter'],
            'pause_patterns': ['!', '~'],
            'vocal_characteristics': ['light', 'quick']
        }
    },
    'archetype_sprite_female': {
        'description': 'Archetype: Female Sprite - Impish, fast voice with magical energy',
        'type': 'orpheus',
        'orpheus_voice': 'mia',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'sprite',
        'gender': 'female',
        'personality_traits': ['impish', 'playful', 'magical', 'quick'],
        'speaking_patterns': {
            'pace': 1.25,
            'pitch_shift': 0.25,
            'emphasis_words': ['twinkle', 'sparkle', 'flutter'],
            'pause_patterns': ['!', '~'],
            'vocal_characteristics': ['airy', 'bright']
        }
    },

    # STREET URCHINS - Fast-paced, cheeky
    'archetype_urchin_male': {
        'description': 'Archetype: Male Street Urchin - Raw, streetwise voice with quick wit',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'urchin',
        'gender': 'male',
        'personality_traits': ['streetwise', 'quick', 'cheeky', 'resourceful'],
        'speaking_patterns': {
            'pace': 1.2,
            'pitch_shift': 0.1,
            'emphasis_words': ['oi', 'quick', 'sharp'],
            'pause_patterns': ['!', '...'],
            'vocal_characteristics': ['raw', 'agile']
        }
    },
    'archetype_urchin_female': {
        'description': 'Archetype: Female Street Urchin - Sharp, mischievous voice with street smarts',
        'type': 'orpheus',
        'orpheus_voice': 'mia',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'urchin',
        'gender': 'female',
        'personality_traits': ['sharp', 'mischievous', 'quick', 'clever'],
        'speaking_patterns': {
            'pace': 1.15,
            'pitch_shift': 0.15,
            'emphasis_words': ['oi', 'quick', 'clever'],
            'pause_patterns': ['!', '...'],
            'vocal_characteristics': ['nimble', 'street-smart']
        }
    },

    # HYPNOTISTS - Deep, entrancing rhythm
    'archetype_hypnotist_male': {
        'description': 'Archetype: Male Hypnotist - Smooth, controlled voice with mesmerizing rhythm',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'hypnotist',
        'gender': 'male',
        'personality_traits': ['mesmerizing', 'controlled', 'mysterious', 'calm'],
        'speaking_patterns': {
            'pace': 0.7,
            'pitch_shift': -0.2,
            'emphasis_words': ['relax', 'deeper', 'sleep'],
            'pause_patterns': ['...', '~'],
            'vocal_characteristics': ['smooth', 'hypnotic']
        }
    },
    'archetype_hypnotist_female': {
        'description': 'Archetype: Female Hypnotist - Mysterious, flowing voice with entrancing quality',
        'type': 'orpheus',
        'orpheus_voice': 'zoe',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'hypnotist',
        'gender': 'female',
        'personality_traits': ['mysterious', 'soothing', 'controlled', 'entrancing'],
        'speaking_patterns': {
            'pace': 0.65,
            'pitch_shift': -0.1,
            'emphasis_words': ['sleep', 'deeper', 'peaceful'],
            'pause_patterns': ['...', '~'],
            'vocal_characteristics': ['flowing', 'mesmerizing']
        }
    },

    # SPORTS COACHES - Loud, motivating
    'archetype_coach_male': {
        'description': 'Archetype: Male Sports Coach - Booming, authoritative voice with motivational energy',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'coach',
        'gender': 'male',
        'personality_traits': ['motivating', 'energetic', 'authoritative', 'passionate'],
        'speaking_patterns': {
            'pace': 1.1,
            'pitch_shift': -0.1,
            'emphasis_words': ['hustle', 'focus', 'team'],
            'pause_patterns': ['!', '!!'],
            'vocal_characteristics': ['booming', 'powerful']
        }
    },
    'archetype_coach_female': {
        'description': 'Archetype: Female Sports Coach - Sharp, energized voice with leadership quality',
        'type': 'orpheus',
        'orpheus_voice': 'jess',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'coach',
        'gender': 'female',
        'personality_traits': ['motivating', 'sharp', 'energetic', 'commanding'],
        'speaking_patterns': {
            'pace': 1.15,
            'pitch_shift': -0.05,
            'emphasis_words': ['focus', 'power', 'drive'],
            'pause_patterns': ['!', '!!'],
            'vocal_characteristics': ['strong', 'dynamic']
        }
    },

    # VAMPIRES - Seductive, calculated
    'archetype_vampire_male': {
        'description': 'Archetype: Male Vampire - Intense whispers with smooth, seductive delivery',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'vampire',
        'gender': 'male',
        'personality_traits': ['seductive', 'mysterious', 'intense', 'calculated'],
        'speaking_patterns': {
            'pace': 0.8,
            'pitch_shift': -0.25,
            'emphasis_words': ['eternal', 'darkness', 'blood'],
            'pause_patterns': ['...', '~'],
            'vocal_characteristics': ['smooth', 'dark']
        }
    },
    'archetype_vampire_female': {
        'description': 'Archetype: Female Vampire - Dangerous, slow-paced voice with dark allure',
        'type': 'orpheus',
        'orpheus_voice': 'zoe',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'vampire',
        'gender': 'female',
        'personality_traits': ['seductive', 'dangerous', 'mysterious', 'elegant'],
        'speaking_patterns': {
            'pace': 0.75,
            'pitch_shift': -0.15,
            'emphasis_words': ['eternal', 'desire', 'darkness'],
            'pause_patterns': ['...', '~'],
            'vocal_characteristics': ['alluring', 'dark']
        }
    },

    # PUNKS - Edgy, rebellious
    'archetype_punk_male': {
        'description': 'Archetype: Male Punk - Fast-paced, aggressive voice with rebellious energy',
        'type': 'orpheus',
        'orpheus_voice': 'zac',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'punk',
        'gender': 'male',
        'personality_traits': ['rebellious', 'aggressive', 'edgy', 'defiant'],
        'speaking_patterns': {
            'pace': 1.2,
            'pitch_shift': -0.1,
            'emphasis_words': ['anarchy', 'rebel', 'chaos'],
            'pause_patterns': ['!', '!!'],
            'vocal_characteristics': ['raw', 'energetic']
        }
    },
    'archetype_punk_female': {
        'description': 'Archetype: Female Punk - Strong attitude with snarky, rebellious delivery',
        'type': 'orpheus',
        'orpheus_voice': 'jess',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'punk',
        'gender': 'female',
        'personality_traits': ['rebellious', 'snarky', 'bold', 'defiant'],
        'speaking_patterns': {
            'pace': 1.15,
            'pitch_shift': -0.05,
            'emphasis_words': ['whatever', 'rebel', 'chaos'],
            'pause_patterns': ['!', '!!'],
            'vocal_characteristics': ['edgy', 'sharp']
        }
    },

    # WITCHES AND WIZARDS - Mystical, deep enunciation
    'archetype_wizard_male': {
        'description': 'Archetype: Male Wizard - Commanding, theatrical voice with mystical gravitas',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'wizard',
        'gender': 'male',
        'personality_traits': ['mystical', 'wise', 'commanding', 'theatrical'],
        'speaking_patterns': {
            'pace': 0.8,
            'pitch_shift': -0.2,
            'emphasis_words': ['behold', 'arcane', 'mystic'],
            'pause_patterns': ['...', '!'],
            'vocal_characteristics': ['deep', 'resonant']
        }
    },
    'archetype_witch_female': {
        'description': 'Archetype: Female Witch - Mysterious, layered voice with magical presence',
        'type': 'orpheus',
        'orpheus_voice': 'leah',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'witch',
        'gender': 'female',
        'personality_traits': ['mysterious', 'powerful', 'wise', 'enchanting'],
        'speaking_patterns': {
            'pace': 0.85,
            'pitch_shift': -0.1,
            'emphasis_words': ['enchant', 'mystic', 'power'],
            'pause_patterns': ['...', '!'],
            'vocal_characteristics': ['mystical', 'layered']
        }
    },

    # PRIVATE INVESTIGATORS - Cool, confident, noir-style
    'archetype_detective_male': {
        'description': 'Archetype: Male Detective - Weighted phrasing with collected, noir-style delivery',
        'type': 'orpheus',
        'orpheus_voice': 'leo',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'detective',
        'gender': 'male',
        'personality_traits': ['cool', 'analytical', 'confident', 'mysterious'],
        'speaking_patterns': {
            'pace': 0.9,
            'pitch_shift': -0.15,
            'emphasis_words': ['case', 'suspect', 'mystery'],
            'pause_patterns': ['...', ', '],
            'vocal_characteristics': ['smooth', 'measured']
        }
    },
    'archetype_detective_female': {
        'description': 'Archetype: Female Detective - Introspective, grounded voice with noir quality',
        'type': 'orpheus',
        'orpheus_voice': 'tara',
        'precision': 'fp8',
        'max_tokens': 2200,
        'archetype': 'detective',
        'gender': 'female',
        'personality_traits': ['sharp', 'analytical', 'confident', 'introspective'],
        'speaking_patterns': {
            'pace': 0.95,
            'pitch_shift': -0.1,
            'emphasis_words': ['case', 'evidence', 'mystery'],
            'pause_patterns': ['...', ', '],
            'vocal_characteristics': ['cool', 'collected']
        }
    },

    # PRIVATE INVESTIGATORS - Cool, confident noir-style with weighted phrasing
    'archetype_private_investigator_male': {
        'description': 'Archetype: Male Private Investigator - Cool detective with noir sophistication',
        'type': 'orpheus',
        'orpheus_voice': 'dan',
        'precision': 'fp16',
        'max_tokens': 2200,
        'archetype': 'private_investigator',
        'gender': 'male',
        'personality_traits': ['cool', 'sophisticated', 'observant', 'noir'],
        'vocal_characteristics': ['cool_confidence', 'noir_style', 'weighted_phrasing'],
        'emotional_range': ['cool', 'confident', 'observant', 'noir'],
        'speaking_patterns': ['slow_weighted', 'noir_delivery', 'confident_cadence'],
        'temperature_presets': {
            'calm': 0.3, 'natural': 0.6, 'expressive': 0.9, 'dramatic': 1.2
        }
    },
    'archetype_private_investigator_female': {
        'description': 'Archetype: Female Private Investigator - Sharp detective with sophisticated edge',
        'type': 'orpheus',
        'orpheus_voice': 'tara',
        'precision': 'fp16',
        'max_tokens': 2200,
        'archetype': 'private_investigator',
        'gender': 'female',
        'personality_traits': ['sharp', 'sophisticated', 'intuitive', 'confident'],
        'vocal_characteristics': ['sharp_intelligence', 'sophisticated_edge', 'confident_precision'],
        'emotional_range': ['sharp', 'sophisticated', 'confident', 'intuitive'],
        'speaking_patterns': ['precise_delivery', 'sophisticated_rhythm', 'confident_flow'],
        'temperature_presets': {
            'calm': 0.4, 'natural': 0.7, 'expressive': 1.0, 'dramatic': 1.3
        }
    },

    'angel': {
        'phrases': {'blessed', 'divine', 'holy', 'righteous', 'eternal', 'sacred', 'heavenly'},
        'style': 'overwhelming_divine_grace',
        'emphasis': 'celestial_delivery',
        'text_transform': lambda text: f"✧ {text.replace('.', '... blessed be...')} ✧"
    },
    'devil': {
        'phrases': {'delicious', 'tempting', 'wicked', 'sinful', 'corrupt', 'desire', 'darkness'},
        'style': 'overwhelming_dark_seduction',
        'emphasis': 'corrupting_delivery',
        'text_transform': lambda text: f"♦ {text.replace('.', '... so tempting...')} ♦"
    }
}

# Global state for performance tracking
active_streams = 0
performance_metrics = {
    'total_requests': 0,
    'avg_generation_time': 0,
    'tokens_per_second': 0,
    'stream_success_rate': 0
}

# Conversation history storage
conversation_sessions = {}

# Set up OpenAI client with the provided API key
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("🤖 OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        openai_client = None
else:
    print("❌ OpenAI client not initialized - no API key found")

# Emotional Analysis Components
class EmotionalState(Enum):
    JOYFUL = "joyful"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CALM = "calm"
    WORRIED = "worried"
    SURPRISED = "surprised"
    CONFIDENT = "confident"
    EMPATHETIC = "empathetic"

class EmotionalIntensity(Enum):
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.9

@dataclass
class EmotionalContext:
    primary_emotion: EmotionalState
    intensity: float
    confidence: float
    triggers: List[str]
    context_words: List[str]

@dataclass
class UserEmotionalProfile:
    current_emotion: EmotionalState
    emotion_history: List[EmotionalContext]
    conversation_sentiment_trend: float
    emotional_volatility: float
    preferred_response_style: str

class EmotionalIntelligenceEngine:
    """
    Advanced emotional intelligence engine that analyzes user input
    and generates appropriate emotional responses
    """
    
    def __init__(self):
        self.emotion_keywords = {
            EmotionalState.JOYFUL: ['happy', 'excited', 'great', 'awesome', 'wonderful', 'love', 'amazing', 'fantastic', 'thrilled', 'delighted'],
            EmotionalState.SAD: ['sad', 'upset', 'down', 'depressed', 'disappointed', 'hurt', 'lonely', 'miserable', 'unhappy'],
            EmotionalState.ANGRY: ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'frustrated', 'pissed', 'rage', 'outraged'],
            EmotionalState.EXCITED: ['excited', 'pumped', 'energetic', 'enthusiastic', 'eager', 'thrilled', 'hyped', 'stoked'],
            EmotionalState.FRUSTRATED: ['frustrated', 'annoyed', 'stuck', 'blocked', 'irritated', 'fed up', 'exasperated'],
            EmotionalState.CALM: ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'composed', 'zen', 'centered'],
            EmotionalState.WORRIED: ['worried', 'anxious', 'concerned', 'nervous', 'stressed', 'troubled', 'uneasy'],
            EmotionalState.SURPRISED: ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'wow', 'incredible'],
            EmotionalState.CONFIDENT: ['confident', 'sure', 'certain', 'determined', 'strong', 'capable', 'ready'],
            EmotionalState.EMPATHETIC: ['understand', 'feel', 'sorry', 'empathize', 'relate', 'compassion', 'care']
        }
        
        self.emotional_response_templates = {
            EmotionalState.JOYFUL: {
                'voice_tone': 'warm',
                'response_style': 'enthusiastic and supportive',
                'conversation_approach': 'share in the excitement, be encouraging'
            },
            EmotionalState.SAD: {
                'voice_tone': 'gentle',
                'response_style': 'compassionate and understanding',
                'conversation_approach': 'offer comfort and support, validate feelings'
            },
            EmotionalState.ANGRY: {
                'voice_tone': 'calm',
                'response_style': 'patient and de-escalating',
                'conversation_approach': 'acknowledge frustration, help find solutions'
            },
            EmotionalState.EXCITED: {
                'voice_tone': 'energetic',
                'response_style': 'match energy level, build on excitement',
                'conversation_approach': 'match energy level, build on excitement'
            },
            EmotionalState.FRUSTRATED: {
                'voice_tone': 'patient',
                'response_style': 'helpful problem-solving approach',
                'conversation_approach': 'focus on solutions, break down problems'
            },
            EmotionalState.CALM: {
                'voice_tone': 'neutral',
                'response_style': 'balanced and informative',
                'conversation_approach': 'respond naturally and supportively'
            },
            EmotionalState.WORRIED: {
                'voice_tone': 'reassuring',
                'response_style': 'calming and supportive',
                'conversation_approach': 'provide reassurance, offer practical help'
            },
            EmotionalState.SURPRISED: {
                'voice_tone': 'engaged',
                'response_style': 'curious and responsive',
                'conversation_approach': 'explore the surprise, ask follow-up questions'
            },
            EmotionalState.CONFIDENT: {
                'voice_tone': 'assured',
                'response_style': 'supportive, reinforce positive feelings',
                'conversation_approach': 'be supportive, reinforce positive feelings'
            },
            EmotionalState.EMPATHETIC: {
                'voice_tone': 'warm',
                'response_style': 'understanding and connecting',
                'conversation_approach': 'validate emotions, create connection'
            }
        }
        
        self.user_profiles = {}
    
    def analyze_user_emotion(self, text: str, user_id: str = "default") -> EmotionalContext:
        """Analyze emotional content of user input"""
        text_lower = text.lower()
        
        # Score each emotion based on keyword presence
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score

        # Default to calm if no strong emotions detected
        if not emotion_scores:
            primary_emotion = EmotionalState.CALM
            intensity = 0.2
            confidence = 0.7
        else:
            # Find dominant emotion
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            max_score = emotion_scores[primary_emotion]
            
            # Calculate intensity and confidence
            intensity = min(max_score * 0.3, 1.0)
            confidence = min(max_score * 0.2 + 0.5, 1.0)

        # Extract context triggers
        triggers = []
        context_words = []
        
        for emotion, keywords in self.emotion_keywords.items():
            found_words = [word for word in keywords if word in text_lower]
            if found_words:
                triggers.extend(found_words)
                if emotion == primary_emotion:
                    context_words = found_words

        return EmotionalContext(
            primary_emotion=primary_emotion,
            intensity=intensity,
            confidence=confidence,
            triggers=triggers,
            context_words=context_words
        )

    def generate_emotionally_aware_response(self, user_input: str, user_id: str = "default") -> Dict:
        """Generate emotionally aware response configuration"""
        
        # Analyze user's emotional state
        emotional_context = self.analyze_user_emotion(user_input, user_id)
        
        # Get or create user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserEmotionalProfile(
                current_emotion=emotional_context.primary_emotion,
                emotion_history=[],
                conversation_sentiment_trend=0.0,
                emotional_volatility=0.0,
                preferred_response_style="balanced"
            )
        
        profile = self.user_profiles[user_id]
        profile.emotion_history.append(emotional_context)
        profile.current_emotion = emotional_context.primary_emotion
        
        # Keep history manageable
        if len(profile.emotion_history) > 10:
            profile.emotion_history = profile.emotion_history[-10:]
        
        # Get response configuration
        response_config = self.emotional_response_templates[emotional_context.primary_emotion]
        
        return {
            'detected_emotion': emotional_context.primary_emotion.value,
            'emotion_intensity': emotional_context.intensity,
            'confidence': emotional_context.confidence,
            'voice_tone': response_config['voice_tone'],
            'response_style': response_config['response_style'],
            'conversation_approach': response_config['conversation_approach'],
            'emotional_subtext': f"{emotional_context.primary_emotion.value} state",
            'response_suggestion': "respond helpfully",
            'user_profile': {
                'current_emotion': profile.current_emotion.value,
                'sentiment_trend': profile.conversation_sentiment_trend,
                'emotional_volatility': profile.emotional_volatility
            }
        }

# Global emotional intelligence engine
emotional_engine = EmotionalIntelligenceEngine()

def generate_fast_chatgpt_response(user_input: str, session_id: str = "default") -> str:
    """
    SPEED OPTIMIZED: Fast ChatGPT response without heavy emotional processing
    Target: <3 seconds total response time
    """
    if not OPENAI_API_KEY:
        return "I'm here to help! What can I do for you?"
    
    try:
        # Get conversation history for context
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
        
        conversation_history = conversation_sessions[session_id]
        
        # Build simple, fast prompt - no complex emotional analysis
        messages = [
            {"role": "system", "content": "You are a helpful, friendly AI assistant. Keep responses concise and natural. Respond in 1-2 sentences when possible."}
        ]
        
        # Add recent context (last 3 exchanges only for speed)
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        for msg in recent_history:
            if msg.get("user"):
                messages.append({"role": "user", "content": msg["user"]})
            if msg.get("assistant"):
                messages.append({"role": "assistant", "content": msg["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Fast ChatGPT call with speed optimizations
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",  # Faster than GPT-4
            "messages": messages,
            "max_tokens": 150,  # Limit response length for speed
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=6  # 6 second total timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content'].strip()
            
            # Update conversation history (keep last 10 exchanges only)
            conversation_sessions[session_id].append({
                "user": user_input,
                "assistant": ai_response,
                "timestamp": time.time()
            })
            
            # Keep history manageable for speed
            if len(conversation_sessions[session_id]) > 10:
                conversation_sessions[session_id] = conversation_sessions[session_id][-10:]
            
            return ai_response
        else:
            print(f"❌ ChatGPT API Error: {response.status_code} - {response.text}")
            return "I'm here to help! What would you like to know?"
        
    except requests.exceptions.Timeout:
        return "I'm thinking as fast as I can! Could you try again?"
    except Exception as e:
        print(f"⚡ Fast ChatGPT error: {e}")
        return "I'm here to help! What can I do for you?"

def generate_emotionally_aware_chatgpt_response(user_input: str, session_id: str) -> str:
    """
    Generate ChatGPT response that's emotionally aware and appropriate
    """
    if not OPENAI_API_KEY:
        return "I understand your feelings. I'm here to help you with whatever you need."
    
    try:
        # Get emotional analysis
        emotional_analysis = emotional_engine.generate_emotionally_aware_response(user_input, session_id)
        
        # Create emotionally-aware system prompt
        emotional_prompt = f"""
        You are an emotionally intelligent AI assistant. Based on analysis of the user's message:
        
        DETECTED EMOTION: {emotional_analysis['detected_emotion']} (intensity: {emotional_analysis['emotion_intensity']:.2f})
        EMOTIONAL CONTEXT: {emotional_analysis['emotional_subtext']}
        
        RESPONSE GUIDELINES:
        - Style: {emotional_analysis['response_style']}
        - Approach: {emotional_analysis['conversation_approach']}
        - Voice should be: {emotional_analysis['voice_tone']}
        
        Respond to the user's message with appropriate emotional intelligence. Match their emotional state appropriately - don't ignore their feelings, but help guide them toward a positive resolution if needed.
        
        Keep your response conversational, empathetic, and under 150 words.
        """
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": emotional_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content'].strip()
            
            # Store conversation context
            if session_id not in conversation_sessions:
                conversation_sessions[session_id] = []
            
            conversation_sessions[session_id].append({
                'user_input': user_input,
                'ai_response': ai_response,
                'emotional_analysis': emotional_analysis,
                'timestamp': time.time()
            })
            
            return ai_response
        else:
            print(f"❌ ChatGPT API Error: {response.status_code} - {response.text}")
            return f"I understand you're feeling {emotional_analysis['detected_emotion']}. I'm here to help you with whatever you need."
        
    except Exception as e:
        print(f"Error generating emotionally aware response: {e}")
        return "I understand your feelings. I'm here to help you with whatever you need."

def create_orpheus_wav(raw_audio_data):
    """Convert raw Orpheus audio to proper WAV format with optimizations"""
    data_size = len(raw_audio_data)
    file_size = data_size + 36
    byte_rate = ORPHEUS_SAMPLE_RATE * 1 * 16 // 8
    block_align = 1 * 16 // 8
    
    header = b'RIFF'
    header += struct.pack('<I', file_size)
    header += b'WAVE'
    header += b'fmt '
    header += struct.pack('<I', 16)
    header += struct.pack('<H', 1)
    header += struct.pack('<H', 1)
    header += struct.pack('<I', ORPHEUS_SAMPLE_RATE)
    header += struct.pack('<I', byte_rate)
    header += struct.pack('<H', block_align)
    header += struct.pack('<H', 16)
    header += b'data'
    header += struct.pack('<I', data_size)
    
    return header + raw_audio_data

def generate_orpheus_tts_optimized(text, voice_config, use_streaming=False, emotion_mode='natural', add_emotion_tags=True):
    """Generate audio using Orpheus TTS with performance optimizations and emotional controls"""
    global active_streams, performance_metrics, ORPHEUS_MODEL_AVAILABLE, ORPHEUS_DEPLOYMENT_STATUS
    
    try:
        start_time = time.time()
        active_streams += 1
        
        # Optimize text and parameters
        word_count = len(text.split())
        estimated_tokens = word_count * 15  # More generous estimate for complex speech
        base_max_tokens = voice_config.get('max_tokens', 2200)
        
        # For conversation responses, be more generous with tokens
        if word_count > 30:  # Longer responses (typical ChatGPT)
            min_tokens = max(1200, estimated_tokens)  # Ensure minimum for full response
        else:
            min_tokens = max(800, estimated_tokens)   # Shorter responses
            
        optimized_max_tokens = min(min_tokens, base_max_tokens)
        
        # Clean up text
        optimized_text = re.sub(r'[.]{3,}', '...', text)
        optimized_text = re.sub(r'[!]{2,}', '!', optimized_text)
        optimized_text = re.sub(r'[?]{2,}', '?', optimized_text)
        optimized_text = re.sub(r'\s+', ' ', optimized_text).strip()
        
        # EMOTIONAL ENHANCEMENT
        # Get temperature based on emotion mode
        temperature_presets = voice_config.get('temperature_presets', {
            'calm': 0.3, 'natural': 0.7, 'expressive': 1.0, 'dramatic': 1.3
        })
        base_temperature = temperature_presets.get(emotion_mode, 0.7)
        
        # Add contextual emotion tags if enabled
        if add_emotion_tags:
            optimized_text = enhance_text_with_emotions(optimized_text, voice_config)
        
        payload = {
            "voice": voice_config['orpheus_voice'],
            "prompt": optimized_text,
            "max_tokens": optimized_max_tokens,
            "temperature": base_temperature,  # Dynamic temperature based on emotion
            "repetition_penalty": 1.1  # Stable generation
        }
        
        # Add performance optimizations if supported by API
        precision = voice_config.get('precision', 'fp8')
        
        headers = {
            "Authorization": f"Api-Key {BASETEN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print(f"🚀 Calling Optimized Orpheus API - Voice: {voice_config['orpheus_voice']}, Precision: {precision}, Tokens: {optimized_max_tokens}, Emotion: {emotion_mode}")
        
        # Use standard requests for stability
        response = requests.post(ORPHEUS_ENDPOINT, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            raw_audio_data = response.content
            wav_data = create_orpheus_wav(raw_audio_data)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(wav_data)
                temp_path = temp_file.name
            
            # Calculate metrics
            audio_size = len(raw_audio_data)
            duration = max(0.1, audio_size / (ORPHEUS_SAMPLE_RATE * 2))
            generation_time = time.time() - start_time
            
            # Update global status
            ORPHEUS_MODEL_AVAILABLE = True
            ORPHEUS_DEPLOYMENT_STATUS = "ACTIVE"
            
            # Update performance metrics
            performance_metrics['total_requests'] += 1
            performance_metrics['avg_generation_time'] = (
                (performance_metrics['avg_generation_time'] * (performance_metrics['total_requests'] - 1) + generation_time) 
                / performance_metrics['total_requests']
            )
            
            # Estimate tokens per second
            estimated_tokens = audio_size // 100
            if generation_time > 0:
                tokens_per_sec = estimated_tokens / generation_time
                performance_metrics['tokens_per_second'] = (
                    (performance_metrics['tokens_per_second'] * (performance_metrics['total_requests'] - 1) + tokens_per_sec)
                    / performance_metrics['total_requests']
                )
            
            # Performance warnings
            if generation_time > 5.0:
                print(f"⚠️ Slow generation: {generation_time:.1f}s (target: <3s)")
            
            return {
                'success': True,
                'file_path': temp_path,
                'duration': duration,
                'generation_time': generation_time,
                'file_size': len(wav_data),
                'raw_audio_size': audio_size,
                'streaming': False,  # Using standard for stability
                'emotion_mode': emotion_mode,
                'temperature_used': base_temperature,
                'fallback_used': None,
                'performance': {
                    'tokens_per_second': performance_metrics['tokens_per_second'],
                    'avg_generation_time': performance_metrics['avg_generation_time'],
                    'precision': precision,
                    'optimized_tokens': optimized_max_tokens,
                    'emotion_enhanced': add_emotion_tags
                }
            }
        else:
            # Handle specific error cases
            error_text = response.text
            print(f"❌ Orpheus API Error: {response.status_code} - {error_text}")
            
            # Check for deployment waking up or model not found
            if response.status_code == 404 or "model_id" in error_text.lower():
                print(f"🔄 Orpheus deployment still waking up - using OpenAI TTS fallback")
                return generate_openai_tts_fallback(text, voice_config, emotion_mode)
                
            # Check for deactivation error
            if "deactivated" in error_text.lower() or "needs to be activated" in error_text.lower():
                ORPHEUS_DEPLOYMENT_STATUS = "INACTIVE"
                ORPHEUS_MODEL_AVAILABLE = False
                print(f"🚨 Orpheus deployment detected as INACTIVE - using OpenAI TTS fallback")
                return generate_openai_tts_fallback(text, voice_config, emotion_mode)
                
            return {
                'success': False,
                'error': f'Orpheus API error: {response.status_code} - {response.text}',
                'fallback_used': None
            }
            
    except requests.exceptions.Timeout:
        print(f"⏰ Orpheus API timeout - using OpenAI TTS fallback")
        return generate_openai_tts_fallback(text, voice_config, emotion_mode)
    except Exception as e:
        print(f"💥 Orpheus TTS error: {str(e)} - using OpenAI TTS fallback")
        return generate_openai_tts_fallback(text, voice_config, emotion_mode)
    finally:
        active_streams = max(0, active_streams - 1)

def generate_openai_tts_fallback(text, voice_config, emotion_mode='natural'):
    """Fallback TTS using OpenAI when Orpheus is unavailable"""
    try:
        start_time = time.time()
        print(f"🔄 Using OpenAI TTS fallback for: {text[:50]}...")
        
        # Map Orpheus voices to OpenAI voices
        orpheus_to_openai_voice = {
            'leah': 'nova',
            'jess': 'shimmer', 
            'dan': 'onyx',
            'zac': 'fable',
            'zoe': 'nova',
            'tara': 'alloy',
            'leo': 'echo',
            'mia': 'shimmer'
        }
        
        orpheus_voice = voice_config.get('orpheus_voice', 'leah')
        openai_voice = orpheus_to_openai_voice.get(orpheus_voice, 'nova')
        
        # Initialize OpenAI client
        if not OPENAI_API_KEY:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'fallback_used': 'openai_tts'
            }
            
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice=openai_voice,
            input=text
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            response.stream_to_file(temp_file.name)
            temp_path = temp_file.name
        
        generation_time = time.time() - start_time
        
        # Estimate duration (rough calculation)
        word_count = len(text.split())
        estimated_duration = word_count * 0.6  # ~0.6 seconds per word average
        
        print(f"✅ OpenAI TTS generated in {generation_time:.1f}s using voice '{openai_voice}'")
        
        return {
            'success': True,
            'file_path': temp_path,
            'duration': estimated_duration,
            'generation_time': generation_time,
            'file_size': 0,  # Unknown for streaming
            'raw_audio_size': 0,
            'streaming': False,
            'emotion_mode': emotion_mode,
            'temperature_used': 0.7,
            'fallback_used': 'openai_tts',
            'openai_voice_used': openai_voice,
            'performance': {
                'tokens_per_second': 0,
                'avg_generation_time': generation_time,
                'precision': 'openai_standard',
                'optimized_tokens': 0,
                'emotion_enhanced': False
            }
        }
        
    except Exception as e:
        print(f"❌ OpenAI TTS fallback failed: {str(e)}")
        return {
            'success': False,
            'error': f'OpenAI TTS fallback error: {str(e)}',
            'fallback_used': 'openai_tts'
        }

def get_fastest_voice_for_conversation(requested_voice=None):
    """
    Get the fastest available voice for conversation responses.
    Prioritizes FP8 voices for speed, but respects user's FP16 choice if specified.
    """
    # If user specifically requested a voice and it exists, use it
    if requested_voice and requested_voice in VOICE_CONFIGS:
        return requested_voice
    
    # Get FP8 voices (fastest)
    fp8_voices = [k for k, v in VOICE_CONFIGS.items() if v.get('precision') == 'fp8']
    
    # Prefer specific fast voices in order
    speed_priority = ['orpheus_leah', 'orpheus_jess', 'orpheus_dan', 'orpheus_zac', 'orpheus_zoe']
    
    for voice in speed_priority:
        if voice in fp8_voices:
            return voice
    
    # Fallback to any FP8 voice
    if fp8_voices:
        return fp8_voices[0]
    
    # Ultimate fallback
    return 'orpheus_leah'

def enhance_text_with_emotions(text, voice_config):
    """Enhanced text processing with archetype-specific characteristics and emotions"""
    if not text or not voice_config:
        return text
    
    # Get voice configuration details
    emotional_range = voice_config.get('emotional_range', [])
    personality_traits = voice_config.get('personality_traits', [])
    vocal_characteristics = voice_config.get('vocal_characteristics', [])
    speaking_patterns = voice_config.get('speaking_patterns', [])
    archetype = voice_config.get('archetype', None)
    gender = voice_config.get('gender', None)
    
    enhanced_text = text
    
    # Apply archetype-specific text modifications
    if archetype:
        enhanced_text = apply_archetype_characteristics(enhanced_text, archetype, gender, personality_traits, speaking_patterns)
    
    # Add appropriate emotional tags based on voice characteristics
    if 'expressive' in emotional_range or 'dramatic' in personality_traits:
        # Add emotional expressiveness for dramatic archetypes
        enhanced_text = add_emotional_expression_tags(enhanced_text, voice_config)
    
    # Apply speaking pattern modifications
    if speaking_patterns:
        enhanced_text = apply_speaking_patterns(enhanced_text, speaking_patterns, archetype)
    
    # Add vocal characteristic tags for Orpheus processing
    if vocal_characteristics:
        enhanced_text = add_vocal_characteristic_tags(enhanced_text, vocal_characteristics)
    
    return enhanced_text

def apply_archetype_characteristics(text, archetype, gender, personality_traits, speaking_patterns):
    """Apply archetype-specific text modifications"""
    enhanced_text = text
    
    # Archetype-specific text processing
    archetype_modifiers = {
        'outbacker': {
            'phrases': {'mate', 'fair dinkum', 'right-o', 'crikey'},
            'style': 'australian_warmth',
            'emphasis': 'hearty_delivery'
        },
        'rocker': {
            'phrases': {'ROCK', 'RAGE', 'SAVAGE', 'BRUTAL', 'DESTROY', 'ANNIHILATE', 'VIOLENT', 'FIERCE'},
            'style': 'brutal_aggressive_energy',
            'emphasis': 'savage_delivery'
        },
        'clown': {
            'phrases': {'ta-da', 'whoopee', 'ha-ha', 'surprise'},
            'style': 'theatrical_joy',
            'emphasis': 'exaggerated_delivery'
        },
        'royal': {
            'phrases': {'indeed', 'certainly', 'one must', 'properly'},
            'style': 'elegant_authority',
            'emphasis': 'regal_delivery'
        },
        'beatnik': {
            'phrases': {'dig it', 'cool', 'far out', 'zen'},
            'style': 'poetic_flow',
            'emphasis': 'contemplative_delivery'
        },
        'mystic': {
            'phrases': {'the universe', 'energy', 'transcend', 'enlighten'},
            'style': 'ethereal_wisdom',
            'emphasis': 'mystical_delivery'
        },
        'fortune_teller': {
            'phrases': {'I see', 'the cards reveal', 'destiny', 'future'},
            'style': 'mysterious_insight',
            'emphasis': 'prophetic_delivery'
        },
        'mad_professor': {
            'phrases': {'eureka', 'fascinating', 'experiment', 'brilliant'},
            'style': 'chaotic_genius',
            'emphasis': 'manic_delivery'
        },
        'angel': {
            'phrases': {'blessed', 'divine', 'holy', 'righteous', 'eternal', 'sacred', 'heavenly'},
            'style': 'overwhelming_divine_grace',
            'emphasis': 'celestial_delivery'
        },
        'devil': {
            'phrases': {'delicious', 'tempting', 'wicked', 'sinful', 'corrupt', 'desire', 'darkness'},
            'style': 'overwhelming_dark_seduction',
            'emphasis': 'corrupting_delivery'
        },
        'school_master': {
            'phrases': {'precisely', 'attention', 'learn', 'knowledge'},
            'style': 'scholarly_authority',
            'emphasis': 'educational_delivery'
        },
        'cowboy': {
            'phrases': {'partner', 'reckon', 'howdy', 'frontier'},
            'style': 'frontier_wisdom',
            'emphasis': 'drawling_delivery'
        },
        'philosopher': {
            'phrases': {'ponder', 'wisdom', 'truth', 'existence'},
            'style': 'ancient_wisdom',
            'emphasis': 'thoughtful_delivery'
        },
        'sprite': {
            'phrases': {'magical', 'sparkle', 'whimsical', 'enchant'},
            'style': 'magical_energy',
            'emphasis': 'playful_delivery'
        },
        'pirate': {
            'phrases': {'ahoy', 'matey', 'treasure', 'adventure'},
            'style': 'seafaring_boldness',
            'emphasis': 'commanding_delivery'
        },
        'street_urchin': {
            'phrases': {'street smart', 'savvy', 'hustle', 'clever'},
            'style': 'streetwise_energy',
            'emphasis': 'quick_delivery'
        },
        'hypnotist': {
            'phrases': {'relax', 'focus', 'deeper', 'surrender'},
            'style': 'entrancing_control',
            'emphasis': 'hypnotic_delivery'
        },
        'sports_coach': {
            'phrases': {'champion', 'victory', 'team', 'push harder'},
            'style': 'motivating_energy',
            'emphasis': 'powerful_delivery'
        },
        'vampire': {
            'phrases': {'eternal', 'blood', 'midnight', 'immortal'},
            'style': 'seductive_darkness',
            'emphasis': 'intense_delivery'
        },
        'punk': {
            'phrases': {'rebel', 'fight', 'anarchist', 'raw'},
            'style': 'rebellious_edge',
            'emphasis': 'defiant_delivery'
        },
        'wizard': {
            'phrases': {'magic', 'spell', 'ancient', 'power'},
            'style': 'mystical_authority',
            'emphasis': 'theatrical_delivery'
        },
        'witch': {
            'phrases': {'enchant', 'potion', 'mystical', 'wisdom'},
            'style': 'enchanting_power',
            'emphasis': 'magical_delivery'
        },
        'private_investigator': {
            'phrases': {'investigate', 'clues', 'mystery', 'case'},
            'style': 'noir_sophistication',
            'emphasis': 'confident_delivery'
        }
    }
    
    # Apply extreme transformations for devils and angels
    if archetype == 'angel':
        # Make angelic speech more extreme with divine pauses and sacred emphasis
        enhanced_text = enhanced_text.replace('.', '... blessed be... ')
        enhanced_text = enhanced_text.replace('!', '... divine grace!')
        enhanced_text = f"✧ {enhanced_text.strip()} ✧"
        
    elif archetype == 'devil':
        # Make devilish speech more extreme with tempting pauses and seductive emphasis
        enhanced_text = enhanced_text.replace('.', '... so tempting... ')
        enhanced_text = enhanced_text.replace('!', '... wickedly delicious!')
        enhanced_text = f"♦ {enhanced_text.strip()} ♦"
    
    elif archetype == 'rocker' and gender == 'male':
        # Make male rocker speech brutally aggressive and intense
        enhanced_text = enhanced_text.upper()  # ALL CAPS for aggression
        enhanced_text = enhanced_text.replace('.', '... BRUTAL RAGE... ')
        enhanced_text = enhanced_text.replace('!', '!!! SAVAGE DESTROY!!!')
        enhanced_text = f"🔥💀 {enhanced_text.strip()} 💀🔥"
    
    return enhanced_text

def apply_speaking_patterns(text, speaking_patterns, archetype):
    """Apply speaking pattern modifications based on archetype"""
    enhanced_text = text
    
    # Pattern-specific modifications
    if 'deliberate_pacing' in speaking_patterns:
        # Add pauses for deliberate delivery
        enhanced_text = enhanced_text.replace('.', '... ')
        enhanced_text = enhanced_text.replace(',', ', ')
    
    if 'rapid_delivery' in speaking_patterns or 'fast_paced' in speaking_patterns:
        # Remove some pauses for faster delivery
        enhanced_text = enhanced_text.replace('...', '.')
        enhanced_text = enhanced_text.replace(', ', ',')
    
    if 'theatrical_delivery' in speaking_patterns:
        # Add dramatic emphasis
        enhanced_text = enhanced_text.replace('!', '!')
        enhanced_text = enhanced_text.replace('?', '?')
    
    if 'drawling_delivery' in speaking_patterns:
        # Cowboy-style drawl modifications
        enhanced_text = enhanced_text.replace('ing', "in'")
        
    if 'hypnotic_rhythm' in speaking_patterns:
        # Add hypnotic pauses
        enhanced_text = enhanced_text.replace('.', '... ')
        
    return enhanced_text

def add_emotional_expression_tags(text, voice_config):
    """Add emotional expression tags for dramatic archetypes"""
    archetype = voice_config.get('archetype', '')
    emotional_range = voice_config.get('emotional_range', [])
    
    # Add emotional tags based on archetype characteristics
    if archetype in ['clown', 'sprite', 'mad_professor']:
        # Playful archetypes get laughter
        if any(word in text.lower() for word in ['funny', 'joke', 'amusing', 'silly']):
            text = text + ' <laugh>'
    
    if archetype in ['mystic', 'fortune_teller', 'wizard', 'witch']:
        # Mystical archetypes get thoughtful pauses
        if any(word in text.lower() for word in ['ancient', 'mystical', 'power', 'magic']):
            text = '<sigh> ' + text
    
    if archetype in ['vampire', 'devil']:
        # Dark archetypes get seductive breathing
        if any(word in text.lower() for word in ['tempting', 'desire', 'want']):
            text = text + ' <gasp>'
    
    return text

def add_vocal_characteristic_tags(text, vocal_characteristics):
    """Add vocal characteristic tags for Orpheus processing"""
    enhanced_text = text
    
    # Map vocal characteristics to Orpheus tags
    characteristic_tags = {
        'raspy_edge': '<groan>',
        'ethereal_softness': '<sigh>',
        'commanding_presence': '',  # Use natural authority
        'playful_energy': '<chuckle>',
        'seductive_warmth': '<gasp>',
        'theatrical_projection': '',  # Use natural projection
        'hypnotic_quality': '<yawn>',
        'mysterious_depth': '<sigh>'
    }
    
    # Apply relevant tags based on characteristics
    for characteristic in vocal_characteristics:
        if characteristic in characteristic_tags and characteristic_tags[characteristic]:
            tag = characteristic_tags[characteristic]
            # Add tag occasionally, not to every sentence
            if len(enhanced_text.split('.')) > 1:
                sentences = enhanced_text.split('.')
                if len(sentences) > 1:
                    sentences[1] = tag + ' ' + sentences[1]
                    enhanced_text = '.'.join(sentences)
    
    return enhanced_text

class OptimizedVoiceRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests with enhanced routing"""
        path = urlparse(self.path).path
        
        if path == '/':
            self.serve_voice_chat()
        elif path == '/archetype-tester':
            self.serve_archetype_tester()
        elif path == '/health':
            self.send_health_response()
        elif path == '/voices':
            self.send_voices_response()
        elif path == '/metrics':
            self.send_metrics_response()
        elif path == '/conversation/history':
            self.send_conversation_history()
        elif path == '/debug':
            self.debug_interface()
        elif path == '/archetypes':
            self.serve_archetype_gallery()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/generate':
            self.handle_generate()
        elif self.path == '/conversation/respond':
            self.handle_conversation_respond()
        elif self.path == '/conversation/clear':
            self.handle_clear_conversation()
        elif self.path == '/conversation/respond_emotional':
            self.handle_conversation_respond_emotional()
        else:
            self.send_error(404, "Not Found")

    def serve_voice_chat(self):
        """Serve the enhanced voice chat interface with STT"""
        try:
            with open('templates/index_with_stt.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error_response('Voice chat interface not found', 404)
        except Exception as e:
            self.send_error_response(f'Error serving interface: {e}', 500)

    def serve_archetype_gallery(self):
        """Serve the archetype voice gallery interface"""
        try:
            with open('templates/archetype_voices.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error_response('Archetype gallery not found', 404)
        except Exception as e:
            self.send_error_response(f'Error serving archetype gallery: {e}', 500)

    def serve_archetype_tester(self):
        """Serve the comprehensive archetype voice tester interface"""
        try:
            with open('templates/archetype_voice_tester.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error_response('Archetype voice tester not found', 404)
        except Exception as e:
            self.send_error_response(f'Error serving archetype tester: {e}', 500)

    def send_health_response(self):
        """Send health check response"""
        response = {
            'status': 'healthy',
            'model_status': 'loaded',
            'features': {
                'text_to_speech': True,
                'speech_to_text': True,
                'conversation': True,
                'chatgpt_integration': True,
                'loop_prevention': True,
                'orpheus_tts': True,
                'orpheus_streaming': False,  # Disabled for stability
                'system_tts': False,
                'persistent_connections': False,  # Using requests for stability
                'performance_optimization': True
            },
            'performance': performance_metrics,
            'active_streams': active_streams,
            'max_concurrent_streams': MAX_CONCURRENT_STREAMS,
            'available_voices': list(VOICE_CONFIGS.keys()),
            'api_status': {
                'openai_configured': bool(OPENAI_API_KEY),
                'orpheus_configured': bool(BASETEN_API_KEY),
                'total_conversations': len(conversation_sessions)
            },
            'timestamp': time.time(),
            'message': 'Optimized voice server with ChatGPT + Orpheus TTS'
        }
        self.send_json_response(response)

    def send_voices_response(self):
        """Send available voices with performance information"""
        voices_with_perf = {}
        for voice_id, config in VOICE_CONFIGS.items():
            voices_with_perf[voice_id] = config.copy()
            if config['type'] == 'orpheus':
                voices_with_perf[voice_id]['performance_profile'] = {
                    'precision': config.get('precision', 'fp8'),
                    'max_tokens': config.get('max_tokens', 1800),
                    'streaming_compatible': False,  # Disabled for now
                    'target_latency': '1-3s' if config.get('precision') == 'fp8' else '2-4s'
                }
        
        response = {
            'voices': voices_with_perf,
            'count': len(VOICE_CONFIGS),
            'capabilities': {
                'real_time_generation': True,
                'orpheus_ai_voices': True,
                'streaming_audio': False,  # Disabled for stability
                'system_voices': False,
                'emotion_support': True,
                'performance_optimization': True,
                'chatgpt_conversations': True,
                'multiple_languages': False,
                'voice_cloning': False
            },
            'performance_info': {
                'target_tokens_per_sec': TARGET_TOKENS_PER_SEC,
                'chunk_size': CHUNK_SIZE,
                'max_concurrent_streams': MAX_CONCURRENT_STREAMS
            }
        }
        self.send_json_response(response)

    def send_metrics_response(self):
        """Send performance metrics"""
        response = {
            'performance_metrics': performance_metrics,
            'active_streams': active_streams,
            'max_concurrent_streams': MAX_CONCURRENT_STREAMS,
            'conversation_stats': {
                'active_sessions': len(conversation_sessions),
                'total_messages': sum(len(session) for session in conversation_sessions.values())
            },
            'target_metrics': {
                'tokens_per_second': TARGET_TOKENS_PER_SEC,
                'max_generation_time': 3.0,
                'stream_success_rate': 0.95
            },
            'timestamp': time.time()
        }
        self.send_json_response(response)

    def handle_generate(self):
        """Handle speech generation with optimized Orpheus and emotional controls"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '').strip()
            voice = data.get('voice', '').strip()
            context = data.get('context', 'manual')
            emotion_mode = data.get('emotion_mode', 'natural')  # NEW: emotion control
            add_emotion_tags = data.get('add_emotion_tags', True)  # NEW: emotion tags
            
            if not text:
                self.send_error_response('Text is required', 400)
                return
                
            if not voice or voice not in VOICE_CONFIGS:
                voice = 'orpheus_leah'  # Default to optimized Orpheus voice
            
            voice_config = VOICE_CONFIGS[voice].copy()  # Make a copy to avoid modifying original
            voice_type = voice_config['type']
            
            # Handle dynamic precision switching for archetype voices
            if voice.endswith('_fp16') and voice.replace('_fp16', '') in VOICE_CONFIGS:
                # User specifically requested FP16 - update precision
                base_voice = voice.replace('_fp16', '')
                voice_config = VOICE_CONFIGS[base_voice].copy()
                voice_config['precision'] = 'fp16'
                voice = base_voice  # Use base voice name for API
            elif '_fp16' not in voice and voice + '_fp16' not in VOICE_CONFIGS:
                # Regular archetype voice - ensure FP8 for speed
                if voice.startswith('archetype_'):
                    voice_config['precision'] = 'fp8'
            
            print(f"🎤 Generating {context} audio using ORPHEUS for voice '{voice}' ({voice_config.get('precision', 'fp8')}) with emotion '{emotion_mode}': {text[:50]}...")
            
            # Generate audio using Orpheus TTS with emotion controls
            result = generate_orpheus_tts_optimized(text, voice_config, emotion_mode=emotion_mode, add_emotion_tags=add_emotion_tags)
            
            if result['success']:
                # Read audio file and encode as base64
                with open(result['file_path'], 'rb') as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Clean up temp file
                os.unlink(result['file_path'])
                
                word_count = len(text.split())
                rtf = result['generation_time'] / result['duration'] if result['duration'] > 0 else 0
                
                response = {
                    'success': True,
                    'audio_base64': audio_base64,
                    'metrics': {
                        'generation_time': round(result['generation_time'], 2),
                        'audio_duration': round(result['duration'], 2),
                        'rtf': round(rtf, 3),
                        'sample_rate': ORPHEUS_SAMPLE_RATE if voice_type == 'orpheus' else 24000,
                        'word_count': word_count,
                        'voice': voice,
                        'voice_type': voice_type,
                        'context': context,
                        'method': f'{voice_type}_tts_optimized',
                        'streaming_used': result.get('streaming', False),
                        'emotion_mode': result.get('emotion_mode', 'natural'),
                        'temperature_used': result.get('temperature_used', 0.7),
                        'performance': result.get('performance', {}),
                        'emotion_enhanced': result.get('emotion_enhanced', False),
                        'precision': voice_config.get('precision', 'fp8')
                    },
                    'original_text': text
                }
                
                precision = voice_config.get('precision', 'fp8')
                perf_indicator = f"⚡ {precision.upper()} ({emotion_mode.upper()})"
                print(f"✅ Generated {result['duration']:.1f}s audio in {result['generation_time']:.1f}s using {voice_type.upper()} {perf_indicator}")
                self.send_json_response(response)
            else:
                self.send_error_response(f'Audio generation failed: {result["error"]}', 500)
                
        except Exception as e:
            print(f"❌ Generation error: {e}")
            self.send_error_response(str(e), 500)

    def handle_conversation_respond(self):
        """Handle fast conversation generation (optimized for speed)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_input = data.get('text', '').strip()
            voice = data.get('voice', 'orpheus_leah')  # Default to fast FP8 voice
            session_id = data.get('session_id', 'default')
            
            if not user_input:
                self.send_error_response('No text provided', 400)
                return
            
            # Get voice configuration
            voice_config = VOICE_CONFIGS.get(voice, VOICE_CONFIGS['orpheus_leah'])
            precision = voice_config.get('precision', 'fp8')
            
            print(f"⚡ FAST conversation for: {user_input[:50]}...")
            print(f"🎯 Using voice: {voice} ({precision})")
            
            start_time = time.time()
            
            # Fast ChatGPT response (no async needed - already sync)
            ai_response = generate_fast_chatgpt_response(user_input, session_id)
            chatgpt_time = time.time() - start_time
            
            # Generate audio using optimized path
            audio_start_time = time.time()
            audio_result = generate_orpheus_tts_optimized(
                ai_response, 
                voice_config, 
                use_streaming=False,
                emotion_mode='natural',
                add_emotion_tags=False  # Skip emotion processing for speed
            )
            audio_time = time.time() - audio_start_time
            total_time = time.time() - start_time
            
            if audio_result['success']:
                # Read and encode audio
                with open(audio_result['file_path'], 'rb') as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Clean up
                os.unlink(audio_result['file_path'])
                
                response_data = {
                    'success': True,
                    'ai_response': ai_response,
                    'audio_base64': audio_base64,
                    'voice_used': voice,
                    'precision_used': precision,
                    'mode': 'fast',
                    'metrics': {
                        'chatgpt_time': round(chatgpt_time, 2),
                        'audio_time': round(audio_time, 2),
                        'total_time': round(total_time, 2),
                        'audio_duration': round(audio_result.get('duration', 0), 2),
                        'words': len(ai_response.split()),
                        'voice': voice,
                        'precision': precision
                    }
                }
                
                # Fast mode logging
                print(f"🚀 FAST Response Generated:")
                print(f"   Voice: {voice} ({precision.upper()})")
                print(f"   Total: {total_time:.2f}s (ChatGPT: {chatgpt_time:.2f}s, Audio: {audio_time:.2f}s)")
                
            else:
                response_data = {
                    'success': False,
                    'error': audio_result.get('error', 'Audio generation failed'),
                    'ai_response': ai_response,
                    'voice_used': voice,
                    'mode': 'fast'
                }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"❌ Fast conversation error: {e}")
            self.send_error_response(f'Fast conversation error: {str(e)}', 500)

    def handle_conversation_respond_emotional(self):
        """Handle emotional conversation generation (advanced features)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_input = data.get('text', '').strip()
            voice = data.get('voice', 'orpheus_tara_fp16')  # Default to quality voice for emotional mode
            session_id = data.get('session_id', 'default')
            
            if not user_input:
                self.send_error_response('No text provided', 400)
                return
            
            # Get voice configuration
            voice_config = VOICE_CONFIGS.get(voice, VOICE_CONFIGS['orpheus_tara_fp16'])
            precision = voice_config.get('precision', 'fp16')
            
            print(f"🧠 Generating emotionally aware response for: {user_input[:50]}...")
            print(f"🎯 Using voice: {voice} ({precision})")
            
            start_time = time.time()
            
            # Get emotional analysis
            emotional_analysis = emotional_engine.generate_emotionally_aware_response(user_input, session_id)
            
            # Generate emotionally aware ChatGPT response (no async needed - already sync)
            ai_response = generate_emotionally_aware_chatgpt_response(user_input, session_id)
            chatgpt_time = time.time() - start_time
            
            # Apply emotional adjustments to voice generation
            emotion_mode = emotional_analysis.get('voice_tone', 'natural')
            
            # Generate with emotional processing
            audio_start_time = time.time()
            audio_result = generate_orpheus_tts_optimized(
                ai_response, 
                voice_config, 
                use_streaming=False,
                emotion_mode=emotion_mode,
                add_emotion_tags=True
            )
            audio_time = time.time() - audio_start_time
            total_time = time.time() - start_time
            
            if audio_result['success']:
                # Read and encode audio
                with open(audio_result['file_path'], 'rb') as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Clean up
                os.unlink(audio_result['file_path'])
                
                response_data = {
                    'success': True,
                    'ai_response': ai_response,
                    'audio_base64': audio_base64,
                    'voice_used': voice,
                    'precision_used': precision,
                    'mode': 'emotional',
                    'emotional_analysis': {
                        'detected_emotion': str(emotional_analysis['detected_emotion']),
                        'emotion_intensity': emotional_analysis['emotion_intensity'],
                        'response_style': str(emotional_analysis['response_style']),
                        'voice_tone': emotion_mode,
                        'conversation_approach': str(emotional_analysis['conversation_approach'])
                    },
                    'metrics': {
                        'chatgpt_time': round(chatgpt_time, 2),
                        'audio_time': round(audio_time, 2),
                        'total_time': round(total_time, 2),
                        'audio_duration': round(audio_result.get('duration', 0), 2),
                        'words': len(ai_response.split()),
                        'voice': voice,
                        'precision': precision
                    }
                }
                
                # Emotional logging
                print(f"🎭 Emotional Response Generated:")
                print(f"   User emotion: {emotional_analysis['detected_emotion']} ({emotional_analysis['emotion_intensity']:.2f})")
                print(f"   AI approach: {emotional_analysis['conversation_approach']}")
                print(f"   Voice: {voice} ({precision.upper()})")
                print(f"   Voice tone: {emotion_mode}")
                print(f"   Total time: {total_time:.2f}s (ChatGPT: {chatgpt_time:.2f}s, Audio: {audio_time:.2f}s)")
                
            else:
                response_data = {
                    'success': False,
                    'error': audio_result.get('error', 'Audio generation failed'),
                    'ai_response': ai_response,
                    'voice_used': voice,
                    'mode': 'emotional'
                }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"❌ Emotional conversation error: {e}")
            self.send_error_response(f'Emotional conversation error: {str(e)}', 500)

    def handle_clear_conversation(self):
        """Handle clearing conversation history"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                session_id = data.get('session_id', 'default')
            else:
                session_id = 'default'
            
            if session_id in conversation_sessions:
                del conversation_sessions[session_id]
            
            response = {
                'success': True,
                'message': f'Conversation history cleared for session {session_id}',
                'session_id': session_id,
                'timestamp': time.time()
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_error_response(str(e), 500)

    def send_conversation_history(self):
        """Send conversation history"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            session_id = query_params.get('session_id', ['default'])[0]
            
            history = conversation_sessions.get(session_id, [])
            
            response = {
                'history': history,
                'total_messages': len(history),
                'session_id': session_id,
                'active_sessions': list(conversation_sessions.keys()),
                'message': f'Conversation history for session {session_id}'
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_error_response(str(e), 500)

    def debug_interface(self):
        """Debug chat interface for testing STT + ChatGPT"""
        try:
            with open('templates/debug_chat.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error loading debug interface: {str(e)}")

    def send_json_response(self, data):
        """Send JSON response with proper headers"""
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        response_bytes = response_json.encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)

    def send_error_response(self, message, status_code=500):
        """Send error response"""
        error_data = {
            'success': False,
            'error': message,
            'timestamp': time.time(),
            'status_code': status_code
        }
        
        response_json = json.dumps(error_data)
        response_bytes = response_json.encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format, *args):
        """Custom logging to reduce noise"""
        if 'GET' in format and ('/health' in format or '/favicon' in format):
            return
        super().log_message(format, *args)

def run_optimized_server():
    """Run the optimized voice server"""
    port = int(os.environ.get('PORT', 5556))  # Use different port to avoid conflicts
    server_address = ('', port)
    
    fp8_voices = [k for k, v in VOICE_CONFIGS.items() if v.get('precision') == 'fp8']
    fp16_voices = [k for k, v in VOICE_CONFIGS.items() if v.get('precision') == 'fp16']
    archetype_count = len([k for k in VOICE_CONFIGS.keys() if k.startswith('archetype_')])
    
    print(f"🚀 Starting ORPHEUS Voice Server with 44 Archetype Voices on port {port}")
    print(f"🌐 Main Interface: http://localhost:{port}/")
    print(f"🎭 Archetype Tester: http://localhost:{port}/archetype-tester")
    print(f"⚡ FP8 voices (speed): {len(fp8_voices)} voices")
    print(f"🎯 FP16 voices (quality): {len(fp16_voices)} voices")
    print(f"🎪 Archetype voices: {archetype_count} distinct character voices")
    print(f"🔧 Performance: Dynamic FP8/FP16 precision switching")
    print(f"🧠 AI: ChatGPT-4 with Real-time Emotional Intelligence")
    print(f"🎤 Features: Speech-to-Text, Archetype Testing, Voice Comparison")
    print("=" * 100)
    
    try:
        httpd = HTTPServer(server_address, OptimizedVoiceRequestHandler)
        print(f"✅ Orpheus server ready!")
        print(f"🎭 Visit http://localhost:{port}/archetype-tester to test all 44 archetype voices!")
        print(f"🎯 Test both FP8 (speed) and FP16 (quality) modes for each character!")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    run_optimized_server() 