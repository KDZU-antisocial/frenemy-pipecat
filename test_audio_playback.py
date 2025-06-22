#!/usr/bin/env python3
"""
Test audio playback to verify the processed audio sounds correct
"""

import wave
import numpy as np
import subprocess
import os

def test_audio_playback():
    """Test playing the processed audio file"""
    
    print("🔊 Testing audio playback...")
    
    # Check if the debug file exists
    debug_file = "debug_audio_chunk.wav"
    if not os.path.exists(debug_file):
        print(f"❌ Debug file not found: {debug_file}")
        return
    
    # Analyze the file
    with wave.open(debug_file, 'rb') as wav:
        sample_rate = wav.getframerate()
        duration = wav.getnframes() / sample_rate
        channels = wav.getnchannels()
        
        print(f"📊 Audio file info:")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Channels: {channels}")
        
        # Read audio data
        audio_data = wav.readframes(wav.getnframes())
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate statistics
        rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
        max_amplitude = np.max(np.abs(audio_array))
        
        print(f"   RMS level: {rms:.2f}")
        print(f"   Max amplitude: {max_amplitude}")
        
        # Check if audio has content
        if rms < 10:
            print("⚠️  Audio is very quiet - might be silence")
        elif rms > 1000:
            print("🔊 Audio is loud")
        else:
            print("🔊 Audio has moderate levels")
    
    # Try to play the audio file
    print(f"\n🎵 Playing audio file: {debug_file}")
    print(f"   Listen carefully - does this sound like your voice at normal pitch?")
    
    try:
        if sys.platform == "darwin":
            # macOS - use afplay
            subprocess.run(["afplay", debug_file], check=True)
            print("✅ Audio played successfully")
        elif sys.platform.startswith("linux"):
            # Linux - use aplay
            subprocess.run(["aplay", debug_file], check=True)
            print("✅ Audio played successfully")
        else:
            # Windows - use start
            subprocess.run(["start", debug_file], shell=True, check=True)
            print("✅ Audio played successfully")
    except Exception as e:
        print(f"❌ Could not play audio: {e}")
        print(f"   Try opening {debug_file} manually in your audio player")
    
    print(f"\n🎯 What to listen for:")
    print(f"   1. Is the pitch normal (not deep/low)?")
    print(f"   2. Can you hear your voice clearly?")
    print(f"   3. Is the volume appropriate?")
    print(f"   4. Does it sound like speech or just noise?")

if __name__ == "__main__":
    import sys
    test_audio_playback() 