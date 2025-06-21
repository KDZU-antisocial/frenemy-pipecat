#!/usr/bin/env python3
"""
Test the debug audio file with Deepgram
"""

import os
from dotenv import load_dotenv
from deepgram import DeepgramClient
import numpy as np

# Load environment variables
load_dotenv(override=True)

# Get API key
deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
if not deepgram_api_key:
    raise ValueError("DEEPGRAM_API_KEY environment variable is not set")

# Initialize Deepgram
deepgram = DeepgramClient(deepgram_api_key)

def test_debug_audio():
    """Test the debug audio file with Deepgram"""
    
    debug_file = "debug_audio_chunk.wav"
    
    if not os.path.exists(debug_file):
        print(f"❌ Debug file not found: {debug_file}")
        return
    
    print(f"🔍 Testing debug audio file: {debug_file}")
    
    # Get file size
    file_size = os.path.getsize(debug_file)
    print(f"📊 File size: {file_size} bytes")
    
    # Read the file
    with open(debug_file, "rb") as f:
        audio_data = f.read()
    
    print(f"📊 Audio data length: {len(audio_data)} bytes")
    
    # Check WAV header
    print(f"🔍 WAV header: {audio_data[:12].hex()}")
    print(f"🔍 Expected: 52494646 (RIFF)")
    
    # Test with Deepgram
    try:
        print("🎤 Sending to Deepgram...")
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            {"buffer": audio_data, "mimetype": "audio/wav"}
        )
        
        if response and hasattr(response, 'results') and response.results:
            channels = response.results.channels
            if len(channels) > 0:
                transcript = channels[0].alternatives[0].transcript
                confidence = channels[0].alternatives[0].confidence
                
                print(f"🎤 Deepgram response:")
                print(f"   Transcript: '{transcript}'")
                print(f"   Confidence: {confidence:.3f}")
                
                if transcript.strip():
                    print("✅ Speech detected!")
                else:
                    print("🔇 No speech detected in debug audio")
            else:
                print("🔇 No channels in response")
        else:
            print("🔇 No response from Deepgram")
            
    except Exception as e:
        print(f"❌ Deepgram error: {e}")

if __name__ == "__main__":
    test_debug_audio() 