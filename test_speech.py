#!/usr/bin/env python3
"""
Test Deepgram with actual speech audio
"""
import os
import subprocess
import tempfile
import wave
import numpy as np
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    print("❌ DEEPGRAM_API_KEY not found in .env file")
    exit(1)

print(f"🔑 Testing Deepgram with actual speech...")

# Create speech audio using system TTS
test_text = "Hello, this is a test of speech recognition."
print(f"🎤 Generating speech: '{test_text}'")

try:
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_filename = temp_file.name
    
    # Generate speech using system TTS
    if os.name == 'posix':  # macOS/Linux
        subprocess.run([
            "say", "-v", "Alex", "-o", temp_filename, test_text
        ], check=True)
    else:  # Windows
        subprocess.run([
            "powershell", "-Command", 
            f"Add-Type -AssemblyName System.Speech; $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synthesizer.SetOutputToWaveFile('{temp_filename}'); $synthesizer.Speak('{test_text}'); $synthesizer.Dispose()"
        ], check=True)
    
    print(f"✅ Generated speech audio: {temp_filename}")
    
    # Read the WAV file
    with wave.open(temp_filename, 'rb') as wav_file:
        wav_data = wav_file.readframes(wav_file.getnframes())
    
    # Clean up temp file
    os.unlink(temp_filename)
    
    print(f"📊 Speech audio: {len(wav_data)} bytes")
    
    # Test Deepgram API
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }
    
    print("🧪 Sending speech to Deepgram...")
    response = requests.post(url, headers=headers, data=wav_data)
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if 'results' in result and result['results']:
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            confidence = result['results']['channels'][0]['alternatives'][0]['confidence']
            print(f"🎤 Deepgram transcript: '{transcript}'")
            print(f"🎤 Confidence: {confidence}")
            
            if confidence > 0.5:
                print("✅ Deepgram is working perfectly!")
            elif confidence > 0:
                print("⚠️ Deepgram detected some speech but with low confidence")
            else:
                print("❌ Deepgram detected no speech in actual speech audio")
        else:
            print("❌ No results in response")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")

print("\n🔍 Speech Test Complete!") 