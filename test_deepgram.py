#!/usr/bin/env python3
"""
Test Deepgram API key directly
"""
import os
import numpy as np
import io
import struct
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    print("❌ DEEPGRAM_API_KEY not found in .env file")
    exit(1)

print(f"🔑 Testing Deepgram API key: {api_key[:10]}...")

# Create a simple test audio (1 second of silence with a small tone)
sample_rate = 16000
test_samples = int(sample_rate * 1.0)  # 1 second
test_audio = np.zeros(test_samples, dtype=np.int16)
# Add a small tone at the end to make it non-silent
test_audio[-1000:] = 1000

# Create WAV file in memory
wav_buffer = io.BytesIO()
wav_buffer.write(b'RIFF')
wav_buffer.write(struct.pack('<I', 36 + len(test_audio.tobytes())))
wav_buffer.write(b'WAVE')
wav_buffer.write(b'fmt ')
wav_buffer.write(struct.pack('<I', 16))
wav_buffer.write(struct.pack('<H', 1))
wav_buffer.write(struct.pack('<H', 1))
wav_buffer.write(struct.pack('<I', sample_rate))
wav_buffer.write(struct.pack('<I', sample_rate * 2))
wav_buffer.write(struct.pack('<H', 2))
wav_buffer.write(struct.pack('<H', 16))
wav_buffer.write(b'data')
wav_buffer.write(struct.pack('<I', len(test_audio.tobytes())))
wav_buffer.write(test_audio.tobytes())
wav_data = wav_buffer.getvalue()
wav_buffer.close()

print(f"📊 Created test audio: {len(wav_data)} bytes")

# Test Deepgram API directly
url = "https://api.deepgram.com/v1/listen"
headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "audio/wav"
}

try:
    print("🧪 Sending test to Deepgram...")
    response = requests.post(url, headers=headers, data=wav_data)
    
    print(f"📡 Response status: {response.status_code}")
    print(f"📡 Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Response: {result}")
        
        if 'results' in result and result['results']:
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            confidence = result['results']['channels'][0]['alternatives'][0]['confidence']
            print(f"🎤 Transcript: '{transcript}'")
            print(f"🎤 Confidence: {confidence}")
        else:
            print("⚠️ No results in response")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n🔍 API Key Test Complete!") 