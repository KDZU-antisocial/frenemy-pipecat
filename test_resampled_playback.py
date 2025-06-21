#!/usr/bin/env python3
"""
Test script to play the resampled raw audio frames
"""

import wave
import numpy as np
import subprocess
import sys
import os

def play_audio_file(filename):
    """Play an audio file and show its properties"""
    try:
        # Check if file exists
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            return False
            
        # Open the WAV file
        with wave.open(filename, 'rb') as wav_file:
            # Get audio properties
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            duration = n_frames / sample_rate
            
            print(f"🔊 Audio file: {filename}")
            print(f"📊 Properties:")
            print(f"   Sample rate: {sample_rate} Hz")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   Channels: {channels}")
            print(f"   Sample width: {sample_width} bytes")
            print(f"   Total frames: {n_frames}")
            
            # Read audio data
            audio_data = wav_file.readframes(n_frames)
            
            # Convert to numpy array for analysis
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            rms_level = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
            max_amplitude = np.max(np.abs(audio_array))
            
            print(f"📊 Audio levels:")
            print(f"   RMS level: {rms_level:.2f}")
            print(f"   Max amplitude: {max_amplitude}")
            
            if rms_level > 1000:
                print("🔊 Audio is loud")
            elif rms_level > 100:
                print("🔊 Audio is moderate")
            else:
                print("🔊 Audio is quiet")
            
            # Play the audio using system command
            print(f"\n🎵 Playing audio file: {filename}")
            print("   Listen carefully - does this sound like your voice at normal pitch?")
            
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["afplay", filename], check=True)
                elif sys.platform.startswith("linux"):  # Linux
                    subprocess.run(["aplay", filename], check=True)
                else:  # Windows
                    subprocess.run(["start", filename], shell=True, check=True)
                
                print("✅ Audio played successfully")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error playing audio: {e}")
                print("💡 Try playing the file manually with your system's audio player")
                return False
            
            print(f"\n🎯 What to listen for:")
            print(f"   1. Is the pitch normal (not deep/low)?")
            print(f"   2. Can you hear your voice clearly?")
            print(f"   3. Is the volume appropriate?")
            print(f"   4. Does it sound like speech or just noise?")
            
            return True
            
    except Exception as e:
        print(f"❌ Error analyzing audio: {e}")
        return False

def main():
    """Main function"""
    print("🔊 Testing resampled audio playback...")
    
    # Test the resampled file
    resampled_file = "raw_audio_frames_resampled.wav"
    
    if os.path.exists(resampled_file):
        print(f"✅ Found resampled file: {resampled_file}")
        success = play_audio_file(resampled_file)
        
        if success:
            print(f"\n🎯 Comparison:")
            print(f"   - raw_audio_frames.wav: 48kHz (should sound deep/low)")
            print(f"   - raw_audio_frames_resampled.wav: 16kHz (should sound normal)")
            print(f"   - debug_audio_chunk.wav: 16kHz (processed audio for Deepgram)")
    else:
        print(f"❌ Resampled file not found: {resampled_file}")
        print(f"💡 Run the server first to generate this file")
        
        # Fall back to testing the original file
        original_file = "raw_audio_frames.wav"
        if os.path.exists(original_file):
            print(f"\n🔊 Testing original file (will sound deep/low):")
            play_audio_file(original_file)

if __name__ == "__main__":
    main() 