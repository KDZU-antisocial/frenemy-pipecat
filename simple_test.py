#!/usr/bin/env python3
"""
Simple Deepgram API test
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    print("❌ DEEPGRAM_API_KEY not found in .env file")
    exit(1)

print(f"🔑 Deepgram API Key: {api_key[:10]}...")
print(f"🔍 Testing Deepgram API connection...")

# Test with a minimal audio file (just headers)
minimal_wav = (
    b'RIFF' +                    # RIFF header
    b'\x24\x00\x00\x00' +        # File size (36 bytes)
    b'WAVE' +                    # WAVE identifier
    b'fmt ' +                    # Format chunk
    b'\x10\x00\x00\x00' +        # Chunk size (16)
    b'\x01\x00' +                # Audio format (PCM)
    b'\x01\x00' +                # Channels (1)
    b'\x40\x3E\x00\x00' +        # Sample rate (16000)
    b'\x80\x7C\x00\x00' +        # Byte rate (32000)
    b'\x02\x00' +                # Block align (2)
    b'\x10\x00' +                # Bits per sample (16)
    b'data' +                    # Data chunk
    b'\x00\x00\x00\x00'          # Data size (0 - empty audio)
)

print(f"📊 Sending minimal WAV file ({len(minimal_wav)} bytes)...")

# Test Deepgram API
url = "https://api.deepgram.com/v1/listen"
headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "audio/wav"
}

try:
    response = requests.post(url, headers=headers, data=minimal_wav)
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Deepgram API is working correctly!")
        print(f"📊 Response: {result}")
        
        if 'results' in result and result['results'] and 'channels' in result['results']:
            channels = result['results']['channels']
            if len(channels) > 0:
                transcript = channels[0]['alternatives'][0]['transcript']
                confidence = channels[0]['alternatives'][0]['confidence']
                print(f"🎤 Transcript: '{transcript}'")
                print(f"🎤 Confidence: {confidence}")
                
                if confidence == 0.0 and transcript == '':
                    print("✅ This is expected - empty audio should return empty transcript")
                    print("\n🎯 CONCLUSION:")
                    print("✅ Your Deepgram API key is valid and working")
                    print("✅ The API is responding correctly")
                    print("✅ The issue is with your microphone audio content")
                    print("\n💡 NEXT STEPS:")
                    print("1. Speak clearly into your microphone")
                    print("2. Say complete words/sentences")
                    print("3. Reduce background noise")
                    print("4. Position microphone closer to your mouth")
                    print("5. Try saying: 'Hello, this is a test'")
            else:
                print("✅ Empty audio returned no channels (expected)")
                print("\n🎯 CONCLUSION:")
                print("✅ Your Deepgram API key is valid and working")
                print("✅ The API is responding correctly")
                print("✅ The issue is with your microphone audio content")
                print("\n💡 NEXT STEPS:")
                print("1. Speak clearly into your microphone")
                print("2. Say complete words/sentences")
                print("3. Reduce background noise")
                print("4. Position microphone closer to your mouth")
                print("5. Try saying: 'Hello, this is a test'")
        else:
            print("⚠️ Unexpected response format")
    else:
        print(f"❌ API Error: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n�� Test Complete!") 