#!/usr/bin/env python3
"""
Test script to record audio directly at 16kHz for comparison
"""

import wave
import numpy as np
import subprocess
import sys
import os
import tempfile
import time

def record_audio_direct_16k(duration=5, filename="direct_16k_recording.wav"):
    """Record audio directly at 16kHz using system commands"""
    try:
        print(f"🎤 Recording {duration} seconds of audio directly at 16kHz...")
        print("💡 Speak clearly into your microphone now!")
        
        # Create temporary file for recording
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Record audio using system command
        if sys.platform == "darwin":  # macOS
            cmd = [
                "rec", "-r", "16000", "-c", "1", 
                temp_filename, "trim", "0", str(duration)
            ]
        elif sys.platform.startswith("linux"):  # Linux
            cmd = [
                "rec", "-r", "16000", "-c", "1", 
                temp_filename, "trim", "0", str(duration)
            ]
        else:  # Windows
            cmd = [
                "sox", "-d", "-r", "16000", "-c", "1", 
                temp_filename, "trim", "0", str(duration)
            ]
        
        print("🎤 Recording... (speak now)")
        
        # Record audio
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(temp_filename):
            # Move to final location
            os.rename(temp_filename, filename)
            
            # Analyze the recorded audio
            analyze_audio_file(filename)
            
            return True
        else:
            print(f"❌ Recording failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        return False

def analyze_audio_file(filename):
    """Analyze an audio file and show its properties"""
    try:
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
            
            # Calculate zero crossings (rough estimate of speech-like content)
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            print(f"📊 Zero crossings: {zero_crossings}")
            
            # Estimate fundamental frequency (very rough)
            if zero_crossings > 0:
                fundamental_freq = sample_rate / (2 * zero_crossings / duration)
                print(f"📊 Estimated fundamental frequency: {fundamental_freq:.1f} Hz")
                
                if fundamental_freq > 3000:
                    print("🔍 High frequency detected (likely noise/interference)")
                elif fundamental_freq > 500:
                    print("🔍 High frequency detected (unusual for speech)")
                elif fundamental_freq > 100:
                    print("🔍 Normal speech frequency range")
                else:
                    print("🔍 Low frequency detected (unusual for speech)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error analyzing audio: {e}")
        return False

def play_audio_file(filename):
    """Play an audio file"""
    try:
        print(f"\n🎵 Playing audio file: {filename}")
        print("   Listen carefully - does this sound like your normal voice?")
        
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", filename], check=True)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.run(["aplay", filename], check=True)
        else:  # Windows
            subprocess.run(["start", filename], shell=True, check=True)
        
        print("✅ Audio played successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error playing audio: {e}")
        return False

def test_deepgram_on_file(filename):
    """Test Deepgram transcription on the audio file"""
    try:
        print(f"\n🧠 Testing Deepgram on: {filename}")
        
        # Read the audio file
        with open(filename, "rb") as f:
            audio_data = f.read()
        
        # Import Deepgram
        from deepgram import DeepgramClient as Deepgram
        import os
        
        # Get API key
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            print("❌ DEEPGRAM_API_KEY not set")
            return False
        
        # Initialize Deepgram
        deepgram = Deepgram(api_key)
        
        # Send to Deepgram
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            {"buffer": audio_data, "mimetype": "audio/wav"}
        )
        
        if response and hasattr(response, 'results') and response.results:
            channels = response.results.channels
            if len(channels) > 0:
                transcript = channels[0].alternatives[0].transcript
                confidence = channels[0].alternatives[0].confidence
                
                print(f"🎤 Deepgram results:")
                print(f"   Transcript: '{transcript}'")
                print(f"   Confidence: {confidence:.3f}")
                
                if transcript.strip():
                    print("✅ Speech detected!")
                    return True
                else:
                    print("🔇 No speech detected")
                    return False
            else:
                print("🔇 No channels in response")
                return False
        else:
            print("🔇 No response from Deepgram")
            return False
            
    except Exception as e:
        print(f"❌ Deepgram error: {e}")
        return False

def main():
    """Main function"""
    print("🎤 Direct 16kHz Audio Recording Test")
    print("=====================================")
    
    # Record direct 16kHz audio
    direct_file = "direct_16k_recording.wav"
    success = record_audio_direct_16k(duration=5, filename=direct_file)
    
    if success:
        print(f"\n✅ Direct recording completed: {direct_file}")
        
        # Play the direct recording
        play_audio_file(direct_file)
        
        # Test Deepgram on direct recording
        test_deepgram_on_file(direct_file)
        
        print(f"\n🎯 Comparison:")
        print(f"   - direct_16k_recording.wav: Direct 16kHz recording")
        print(f"   - raw_audio_frames_resampled.wav: WebRTC resampled to 16kHz")
        print(f"   - debug_audio_chunk.wav: WebRTC processed for Deepgram")
        
        print(f"\n💡 Questions:")
        print(f"   1. Does the direct recording sound like your normal voice?")
        print(f"   2. Does it sound different from the resampled WebRTC audio?")
        print(f"   3. Which one sounds more natural?")
        
    else:
        print("❌ Direct recording failed")
        print("💡 Make sure you have 'sox' or 'rec' installed:")
        print("   macOS: brew install sox")
        print("   Linux: sudo apt-get install sox")

if __name__ == "__main__":
    main() 