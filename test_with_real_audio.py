#!/usr/bin/env python3
"""
Test voice chat system with real speech audio from NASA
"""
import os
import requests
import tempfile
import wave
import numpy as np
from dotenv import load_dotenv
import io
import struct

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    print("❌ DEEPGRAM_API_KEY not found in .env file")
    exit(1)

print("🔍 Testing with real NASA speech audio...")

# Download the NASA WAV file
nasa_wav_url = "https://dpgr.am/spacewalk.wav"
print(f"📥 Downloading: {nasa_wav_url}")

try:
    response = requests.get(nasa_wav_url)
    if response.status_code == 200:
        wav_data = response.content
        print(f"✅ Downloaded: {len(wav_data)} bytes")
        
        # Test Deepgram API with real speech
        print("🧪 Testing Deepgram with NASA speech audio...")
        
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "audio/wav"
        }
        
        response = requests.post(url, headers=headers, data=wav_data)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Deepgram processed NASA audio successfully!")
            
            if 'results' in result and result['results'] and 'channels' in result['results']:
                channels = result['results']['channels']
                if len(channels) > 0:
                    transcript = channels[0]['alternatives'][0]['transcript']
                    confidence = channels[0]['alternatives'][0]['confidence']
                    print(f"🎤 NASA Audio Transcript: '{transcript}'")
                    print(f"🎤 Confidence: {confidence}")
                    
                    if confidence > 0.5:
                        print("✅ Deepgram is working perfectly with real speech!")
                        print("✅ Your API key and setup are correct")
                        print("✅ The issue is with your microphone audio quality")
                    elif confidence > 0:
                        print("⚠️ Deepgram detected some speech but with low confidence")
                        print("✅ Your API key and setup are correct")
                    else:
                        print("❌ Deepgram detected no speech in NASA audio")
                        print("⚠️ This suggests a deeper issue with Deepgram setup")
                else:
                    print("❌ No channels in response")
            else:
                print("❌ Unexpected response format")
        else:
            print(f"❌ API Error: {response.text}")
            
    else:
        print(f"❌ Failed to download: {response.status_code}")
        
except Exception as e:
    print(f"❌ Download failed: {e}")

print("\n🔍 NASA Audio Test Complete!")

# Also test with a chunk of the audio to simulate our buffer processing
print("\n🧪 Testing with audio chunk (simulating our buffer)...")

try:
    # Read the WAV file to get audio data
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(wav_data)
        temp_filename = temp_file.name
    
    with wave.open(temp_filename, 'rb') as wav_file:
        # Get audio parameters
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        n_frames = wav_file.getnframes()
        
        print(f"📊 Audio info: {sample_rate}Hz, {channels} channels, {sample_width} bytes/sample")
        print(f"📊 Duration: {n_frames / sample_rate:.2f} seconds")
        
        # Read all audio data
        audio_data = wav_file.readframes(n_frames)
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Take a 3-second chunk (simulating our buffer)
        chunk_duration = 3.0  # seconds
        chunk_samples = int(sample_rate * chunk_duration)
        
        if len(audio_array) > chunk_samples:
            audio_chunk = audio_array[:chunk_samples]
            print(f"📊 Using {chunk_samples} samples ({chunk_duration}s) of audio")
            
            # Create WAV file for the chunk
            chunk_wav_buffer = io.BytesIO()
            chunk_wav_buffer.write(b'RIFF')
            chunk_wav_buffer.write(struct.pack('<I', 36 + len(audio_chunk.tobytes())))
            chunk_wav_buffer.write(b'WAVE')
            chunk_wav_buffer.write(b'fmt ')
            chunk_wav_buffer.write(struct.pack('<I', 16))
            chunk_wav_buffer.write(struct.pack('<H', 1))
            chunk_wav_buffer.write(struct.pack('<H', 1))
            chunk_wav_buffer.write(struct.pack('<I', sample_rate))
            chunk_wav_buffer.write(struct.pack('<I', sample_rate * 2))
            chunk_wav_buffer.write(struct.pack('<H', 2))
            chunk_wav_buffer.write(struct.pack('<H', 16))
            chunk_wav_buffer.write(b'data')
            chunk_wav_buffer.write(struct.pack('<I', len(audio_chunk.tobytes())))
            chunk_wav_buffer.write(audio_chunk.tobytes())
            chunk_wav_data = chunk_wav_buffer.getvalue()
            chunk_wav_buffer.close()
            
            # Test Deepgram with the chunk
            print("🧪 Testing Deepgram with 3-second chunk...")
            
            response = requests.post(url, headers=headers, data=chunk_wav_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'results' in result and result['results'] and 'channels' in result['results']:
                    channels = result['results']['channels']
                    if len(channels) > 0:
                        transcript = channels[0]['alternatives'][0]['transcript']
                        confidence = channels[0]['alternatives'][0]['confidence']
                        print(f"🎤 Chunk Transcript: '{transcript}'")
                        print(f"🎤 Confidence: {confidence}")
                        
                        if confidence > 0:
                            print("✅ Deepgram works with real speech chunks!")
                            print("✅ Your system should work with proper microphone input")
                        else:
                            print("❌ Deepgram didn't detect speech in the chunk")
                    else:
                        print("❌ No channels in chunk response")
                else:
                    print("❌ Unexpected chunk response format")
            else:
                print(f"❌ Chunk API Error: {response.text}")
        else:
            print(f"⚠️ Audio too short for chunk test ({len(audio_array)} samples)")
    
    # Clean up
    os.unlink(temp_filename)
    
except Exception as e:
    print(f"❌ Chunk test failed: {e}")

print("\n🎯 FINAL CONCLUSION:")
print("If Deepgram works with NASA audio but not your microphone:")
print("1. ✅ Your API key and setup are correct")
print("2. ❌ Your microphone audio quality needs improvement")
print("3. 💡 Try: better mic positioning, reduce noise, speak clearly")
print("\nIf Deepgram doesn't work with NASA audio:")
print("1. ❌ There's an issue with your Deepgram setup")
print("2. 💡 Check: API key, account permissions, service status") 