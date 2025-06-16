#!/usr/bin/env python3
"""
Clean Orpheus Voice Chat Server
Fixed implementation with working ChatGPT integration and speech-to-text
"""

import json
import requests
import struct
import time
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
import threading
import queue
import concurrent.futures
from pathlib import Path

# Configuration
BASETEN_API_KEY = "UPpt0FhL.ttGUuiWb5VvmLBCmcUSsjE92WVnJQaAq"
ORPHEUS_MODEL_ID = "yqv0epjw"
ORPHEUS_ENDPOINT = f"https://model-{ORPHEUS_MODEL_ID}.api.baseten.co/environments/production/predict"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
SAMPLE_RATE = 24000

# Voice Configurations
VOICE_CONFIGS = {
    # FP8 Voices (Speed Optimized)
    'orpheus_leah': {'name': 'leah', 'precision': 'fp8', 'type': 'FP8 (Speed)', 'target_time': 2.0},
    'orpheus_jess': {'name': 'jess', 'precision': 'fp8', 'type': 'FP8 (Speed)', 'target_time': 2.0},
    'orpheus_dan': {'name': 'dan', 'precision': 'fp8', 'type': 'FP8 (Speed)', 'target_time': 2.0},
    'orpheus_zac': {'name': 'zac', 'precision': 'fp8', 'type': 'FP8 (Speed)', 'target_time': 2.0},
    'orpheus_zoe': {'name': 'zoe', 'precision': 'fp8', 'type': 'FP8 (Speed)', 'target_time': 2.0},
    
    # FP16 Voices (Quality Optimized)
    'orpheus_tara_fp16': {'name': 'tara', 'precision': 'fp16', 'type': 'FP16 (Quality)', 'target_time': 3.0},
    'orpheus_leah_fp16': {'name': 'leah', 'precision': 'fp16', 'type': 'FP16 (Quality)', 'target_time': 3.0},
    'orpheus_leo_fp16': {'name': 'leo', 'precision': 'fp16', 'type': 'FP16 (Quality)', 'target_time': 3.0},
    'orpheus_mia_fp16': {'name': 'mia', 'precision': 'fp16', 'type': 'FP16 (Quality)', 'target_time': 3.0},
}

# Global conversation storage
conversation_sessions = defaultdict(lambda: deque(maxlen=10))

def generate_chatgpt_response(user_input: str, session_id: str = "default") -> str:
    """Generate ChatGPT response using requests (sync)"""
    try:
        # Get conversation history
        history = list(conversation_sessions[session_id])
        
        # Build messages
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Keep responses conversational and under 150 words."}
        ]
        
        # Add recent history
        for entry in history[-6:]:  # Last 3 exchanges
            messages.append({"role": "user", "content": entry['user']})
            messages.append({"role": "assistant", "content": entry['assistant']})
        
        # Add current message
        messages.append({"role": "user", "content": user_input})
        
        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        start_time = time.time()
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=6
        )
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            
            # Store in conversation history
            conversation_sessions[session_id].append({
                'user': user_input,
                'assistant': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ ChatGPT response ({generation_time:.2f}s): {ai_response[:60]}...")
            return ai_response
        else:
            print(f"❌ ChatGPT API Error: {response.status_code} - {response.text}")
            return "I'm having trouble connecting right now. Please try again."
            
    except Exception as e:
        print(f"❌ ChatGPT Error: {e}")
        return "I'm having trouble connecting right now. Please try again."

def create_orpheus_wav(raw_audio_data):
    """Convert raw Orpheus audio to proper WAV format"""
    data_size = len(raw_audio_data)
    file_size = data_size + 36
    byte_rate = SAMPLE_RATE * 1 * 16 // 8
    block_align = 1 * 16 // 8
    
    header = b'RIFF'
    header += struct.pack('<I', file_size)
    header += b'WAVE'
    header += b'fmt '
    header += struct.pack('<I', 16)
    header += struct.pack('<H', 1)
    header += struct.pack('<H', 1)
    header += struct.pack('<I', SAMPLE_RATE)
    header += struct.pack('<I', byte_rate)
    header += struct.pack('<H', block_align)
    header += struct.pack('<H', 16)
    header += b'data'
    header += struct.pack('<I', data_size)
    
    return header + raw_audio_data

def generate_orpheus_audio(text: str, voice_config: dict) -> Tuple[bytes, float, dict]:
    """Generate audio using Orpheus TTS"""
    headers = {
        "Authorization": f"Api-Key {BASETEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Calculate max tokens based on text length
    word_count = len(text.split())
    if voice_config['precision'] == 'fp8':
        max_tokens = min(max(word_count * 12, 800), 2200)
    else:  # fp16
        max_tokens = min(max(word_count * 15, 800), 2500)
    
    payload = {
        "voice": voice_config['name'],
        "prompt": text,
        "max_tokens": max_tokens
    }
    
    start_time = time.time()
    try:
        response = requests.post(ORPHEUS_ENDPOINT, headers=headers, json=payload, timeout=30)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            audio_size = len(response.content)
            wav_data = create_orpheus_wav(response.content)
            
            metrics = {
                'generation_time': generation_time,
                'audio_size': audio_size,
                'max_tokens': max_tokens,
                'target_time': voice_config['target_time'],
                'precision': voice_config['precision'],
                'voice_name': voice_config['name']
            }
            
            print(f"✅ Generated {audio_size:,} bytes in {generation_time:.2f}s using {voice_config['name']} ({voice_config['precision'].upper()})")
            return wav_data, generation_time, metrics
        else:
            error_msg = f"Orpheus API Error: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    except Exception as e:
        print(f"❌ Orpheus Error: {e}")
        raise e

class VoiceChatHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/':
            self.serve_main_page()
        elif path == '/health':
            self.serve_health()
        elif path == '/voices':
            self.serve_voices()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        if path == '/generate':
            self.handle_manual_generation()
        elif path == '/conversation/respond':
            self.handle_conversation()
        else:
            self.send_error(404, "Not Found")

    def serve_main_page(self):
        """Serve the main web interface"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎤 Orpheus Voice Chat</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .voice-selector {
            margin-bottom: 15px;
        }
        select, input, textarea, button {
            width: 100%;
            padding: 12px;
            margin: 5px 0;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }
        button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        button:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }
        .speech-button {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
        }
        .metrics {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: monospace;
        }
        .conversation-history {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background: rgba(102, 126, 234, 0.3);
            text-align: right;
        }
        .ai-message {
            background: rgba(255, 255, 255, 0.1);
        }
        .status {
            text-align: center;
            padding: 10px;
            margin: 10px 0;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
        }
        audio {
            width: 100%;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Orpheus Voice Chat</h1>
        
        <!-- Voice Selection -->
        <div class="section">
            <h3>🎭 Voice Selection</h3>
            <div class="voice-selector">
                <select id="voiceSelect">
                    <option value="">Loading voices...</option>
                </select>
            </div>
            <div id="voiceInfo" class="status"></div>
        </div>

        <!-- Manual Text Testing -->
        <div class="section">
            <h3>⚡ Manual Voice Testing</h3>
            <textarea id="manualText" placeholder="Type any text to hear it spoken..." rows="3"></textarea>
            <button onclick="generateManualAudio()">🔊 Generate Audio</button>
            <div id="manualMetrics" class="metrics" style="display: none;"></div>
            <audio id="manualAudio" controls style="display: none;"></audio>
        </div>

        <!-- Live ChatGPT Conversations -->
        <div class="section">
            <h3>🧠 Live ChatGPT Conversations</h3>
            
            <!-- Text Input -->
            <textarea id="conversationText" placeholder="Type your question or message..." rows="2"></textarea>
            <button onclick="sendTextMessage()">💬 Send Text Message</button>
            
            <!-- Speech Input -->
            <button id="speechButton" class="speech-button" onclick="toggleSpeechRecognition()">
                🎤 Hold to Speak
            </button>
            
            <div id="speechStatus" class="status" style="display: none;"></div>
            <div id="conversationMetrics" class="metrics" style="display: none;"></div>
            <audio id="conversationAudio" controls style="display: none;"></audio>
            
            <!-- Conversation History -->
            <div id="conversationHistory" class="conversation-history"></div>
        </div>

        <!-- Performance Metrics -->
        <div class="section">
            <h3>📊 Performance Metrics</h3>
            <div id="performanceMetrics" class="metrics">
                Waiting for first audio generation...
            </div>
        </div>
    </div>

    <script>
        let voices = [];
        let currentVoice = 'orpheus_leah';
        let recognition = null;
        let isRecording = false;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadVoices();
            initializeSpeechRecognition();
        });

        // Load available voices
        async function loadVoices() {
            try {
                const response = await fetch('/voices');
                voices = await response.json();
                
                const select = document.getElementById('voiceSelect');
                select.innerHTML = '';
                
                voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = `${voice.name} (${voice.type})`;
                    select.appendChild(option);
                });
                
                select.value = 'orpheus_leah';
                currentVoice = 'orpheus_leah';
                updateVoiceInfo();
                
                select.addEventListener('change', function() {
                    currentVoice = this.value;
                    updateVoiceInfo();
                });
                
            } catch (error) {
                console.error('Error loading voices:', error);
                document.getElementById('voiceSelect').innerHTML = '<option>Error loading voices</option>';
            }
        }

        function updateVoiceInfo() {
            const voice = voices.find(v => v.id === currentVoice);
            if (voice) {
                document.getElementById('voiceInfo').innerHTML = 
                    `Selected: <strong>${voice.name}</strong> | ${voice.type} | Target: ${voice.target_time}s`;
            }
        }

        // Manual audio generation
        async function generateManualAudio() {
            const text = document.getElementById('manualText').value.trim();
            if (!text) {
                alert('Please enter some text to generate audio.');
                return;
            }

            const button = event.target;
            button.disabled = true;
            button.textContent = '🔄 Generating...';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice: currentVoice })
                });

                if (response.ok) {
                    const audioBlob = await response.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    const audio = document.getElementById('manualAudio');
                    audio.src = audioUrl;
                    audio.style.display = 'block';
                    audio.play();

                    // Show metrics (would need to be returned in headers or separate call)
                    showManualMetrics(text, audioBlob.size);
                } else {
                    const error = await response.text();
                    alert(`Error: ${error}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to generate audio. Please try again.');
            } finally {
                button.disabled = false;
                button.textContent = '🔊 Generate Audio';
            }
        }

        function showManualMetrics(text, audioSize) {
            const metrics = document.getElementById('manualMetrics');
            metrics.innerHTML = `
                📝 Text: ${text.split(' ').length} words<br>
                🎵 Audio: ${(audioSize / 1024).toFixed(1)} KB<br>
                🎭 Voice: ${currentVoice}<br>
                ⏱️ Generated: ${new Date().toLocaleTimeString()}
            `;
            metrics.style.display = 'block';
        }

        // Conversation functions
        async function sendTextMessage() {
            const text = document.getElementById('conversationText').value.trim();
            if (!text) {
                alert('Please enter a message.');
                return;
            }

            await sendConversationMessage(text);
            document.getElementById('conversationText').value = '';
        }

        async function sendConversationMessage(text) {
            const button = event.target;
            if (button) {
                button.disabled = true;
                button.textContent = '🔄 Processing...';
            }

            // Add user message to history
            addMessageToHistory('user', text);

            try {
                const response = await fetch('/conversation/respond', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        text, 
                        voice: currentVoice,
                        session_id: 'web_session'
                    })
                });

                if (response.ok) {
                    const audioBlob = await response.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    const audio = document.getElementById('conversationAudio');
                    audio.src = audioUrl;
                    audio.style.display = 'block';
                    audio.play();

                    // Add AI response to history (would need the text response)
                    addMessageToHistory('ai', 'AI response (audio generated)');
                    
                    showConversationMetrics();
                } else {
                    const error = await response.text();
                    alert(`Error: ${error}`);
                    addMessageToHistory('error', `Error: ${error}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to process conversation. Please try again.');
                addMessageToHistory('error', 'Failed to process message');
            } finally {
                if (button) {
                    button.disabled = false;
                    button.textContent = '💬 Send Text Message';
                }
            }
        }

        function addMessageToHistory(type, text) {
            const history = document.getElementById('conversationHistory');
            const message = document.createElement('div');
            message.className = `message ${type}-message`;
            message.innerHTML = `
                <strong>${type === 'user' ? 'You' : type === 'ai' ? 'AI' : 'System'}:</strong><br>
                ${text}<br>
                <small>${new Date().toLocaleTimeString()}</small>
            `;
            history.appendChild(message);
            history.scrollTop = history.scrollHeight;
        }

        function showConversationMetrics() {
            const metrics = document.getElementById('conversationMetrics');
            metrics.innerHTML = `
                🎭 Voice: ${currentVoice}<br>
                ⏱️ Processed: ${new Date().toLocaleTimeString()}<br>
                🔊 Audio ready for playback
            `;
            metrics.style.display = 'block';
        }

        // Speech recognition
        function initializeSpeechRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';

                recognition.onstart = function() {
                    isRecording = true;
                    document.getElementById('speechStatus').innerHTML = '🎤 Listening... Speak now!';
                    document.getElementById('speechStatus').style.display = 'block';
                    document.getElementById('speechButton').textContent = '🔴 Recording...';
                };

                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('speechStatus').innerHTML = `Heard: "${transcript}"`;
                    sendConversationMessage(transcript);
                };

                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                    document.getElementById('speechStatus').innerHTML = `❌ Error: ${event.error}`;
                    isRecording = false;
                    document.getElementById('speechButton').textContent = '🎤 Hold to Speak';
                };

                recognition.onend = function() {
                    isRecording = false;
                    document.getElementById('speechButton').textContent = '🎤 Hold to Speak';
                    setTimeout(() => {
                        document.getElementById('speechStatus').style.display = 'none';
                    }, 3000);
                };
            } else {
                document.getElementById('speechButton').textContent = '❌ Speech not supported';
                document.getElementById('speechButton').disabled = true;
            }
        }

        function toggleSpeechRecognition() {
            if (!recognition) return;

            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_health(self):
        """Health check endpoint"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": "Orpheus Voice Chat",
            "voices_available": len(VOICE_CONFIGS),
            "endpoints": ["/", "/health", "/voices", "/generate", "/conversation/respond"]
        }
        self.send_json_response(health_data)

    def serve_voices(self):
        """Return available voices"""
        voices_list = []
        for voice_id, config in VOICE_CONFIGS.items():
            voices_list.append({
                "id": voice_id,
                "name": config['name'],
                "precision": config['precision'],
                "type": config['type'],
                "target_time": config['target_time']
            })
        self.send_json_response(voices_list)

    def handle_manual_generation(self):
        """Handle manual text-to-speech generation"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '').strip()
            voice_id = data.get('voice', 'orpheus_leah')
            
            if not text:
                self.send_error_response('No text provided', 400)
                return
            
            if voice_id not in VOICE_CONFIGS:
                self.send_error_response(f'Unknown voice: {voice_id}', 400)
                return
            
            voice_config = VOICE_CONFIGS[voice_id]
            
            print(f"🎤 Manual generation: {voice_id} - {text[:50]}...")
            
            # Generate audio
            wav_data, generation_time, metrics = generate_orpheus_audio(text, voice_config)
            
            # Send audio response
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('X-Generation-Time', str(generation_time))
            self.send_header('X-Voice-Type', voice_config['type'])
            self.end_headers()
            self.wfile.write(wav_data)
            
        except Exception as e:
            print(f"❌ Manual generation error: {e}")
            self.send_error_response(f'Generation failed: {e}', 500)

    def handle_conversation(self):
        """Handle ChatGPT conversation with voice response"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_input = data.get('text', '').strip()
            voice_id = data.get('voice', 'orpheus_leah')
            session_id = data.get('session_id', 'default')
            
            if not user_input:
                self.send_error_response('No text provided', 400)
                return
            
            if voice_id not in VOICE_CONFIGS:
                self.send_error_response(f'Unknown voice: {voice_id}', 400)
                return
            
            voice_config = VOICE_CONFIGS[voice_id]
            
            print(f"🧠 Conversation: {user_input[:50]}...")
            
            # Get ChatGPT response
            chatgpt_start = time.time()
            ai_response = generate_chatgpt_response(user_input, session_id)
            chatgpt_time = time.time() - chatgpt_start
            
            # Generate voice response
            audio_start = time.time()
            wav_data, audio_time, audio_metrics = generate_orpheus_audio(ai_response, voice_config)
            total_time = time.time() - chatgpt_start
            
            print(f"🎭 Conversation complete: {total_time:.2f}s (ChatGPT: {chatgpt_time:.2f}s, Audio: {audio_time:.2f}s)")
            
            # Send audio response
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('X-ChatGPT-Time', str(chatgpt_time))
            self.send_header('X-Audio-Time', str(audio_time))
            self.send_header('X-Total-Time', str(total_time))
            self.send_header('X-AI-Response', ai_response[:100])
            self.end_headers()
            self.wfile.write(wav_data)
            
        except Exception as e:
            print(f"❌ Conversation error: {e}")
            self.send_error_response(f'Conversation failed: {e}', 500)

    def send_json_response(self, data):
        """Send JSON response"""
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def send_error_response(self, message, status_code=500):
        """Send error response"""
        error_data = {
            "error": message,
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code
        }
        response = json.dumps(error_data)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Override to reduce noise"""
        return

def run_server():
    """Run the voice chat server"""
    server_address = ('', 5556)
    httpd = HTTPServer(server_address, VoiceChatHandler)
    
    print("🚀 Starting Clean Orpheus Voice Chat Server on port 5556")
    print("🌐 Voice Chat Interface: http://localhost:5556/")
    print("⚡ FP8 Orpheus voices (speed): orpheus_leah, orpheus_jess, orpheus_dan, orpheus_zac, orpheus_zoe")
    print("🎯 FP16 Orpheus voices (quality): orpheus_tara_fp16, orpheus_leah_fp16, orpheus_leo_fp16, orpheus_mia_fp16")
    print("🧠 AI: ChatGPT-3.5-turbo for intelligent conversations")
    print("✨ Features: Manual Testing, Live Conversations, Speech-to-Text, Performance Metrics")
    print("=" * 90)
    print("✅ Clean server ready! Visit http://localhost:5556/ for voice conversations!")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    run_server() 