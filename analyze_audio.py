#!/usr/bin/env python3
"""
Analyze both audio files to understand the pitch issue
"""

import wave
import numpy as np

def analyze_audio_files():
    """Analyze both raw and processed audio files"""
    
    files = [
        ("raw_audio_frames.wav", "Raw WebRTC Audio"),
        ("debug_audio_chunk.wav", "Processed Audio")
    ]
    
    for filename, description in files:
        print(f"\n{'='*50}")
        print(f"🔍 Analyzing: {filename} ({description})")
        print(f"{'='*50}")
        
        # Open WAV file
        with wave.open(filename, 'rb') as wav:
            # Get audio properties
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            n_frames = wav.getnframes()
            
            print(f"📊 Audio properties:")
            print(f"   Channels: {channels}")
            print(f"   Sample width: {sample_width} bytes")
            print(f"   Frame rate: {frame_rate} Hz")
            print(f"   Number of frames: {n_frames}")
            print(f"   Duration: {n_frames/frame_rate:.2f} seconds")
            
            # Read audio data
            audio_data = wav.readframes(n_frames)
            
            # Convert to numpy array
            if sample_width == 2:  # 16-bit
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            else:
                audio_array = np.frombuffer(audio_data, dtype=np.int8)
            
            print(f"📊 Audio array shape: {audio_array.shape}")
            print(f"📊 Audio array dtype: {audio_array.dtype}")
            
            # Calculate statistics
            min_val = np.min(audio_array)
            max_val = np.max(audio_array)
            mean_val = np.mean(audio_array)
            std_val = np.std(audio_array)
            rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
            
            print(f"📊 Audio statistics:")
            print(f"   Min: {min_val}")
            print(f"   Max: {max_val}")
            print(f"   Mean: {mean_val:.2f}")
            print(f"   Std: {std_val:.2f}")
            print(f"   RMS: {rms:.2f}")
            
            # Check for non-zero samples
            non_zero = np.count_nonzero(audio_array)
            print(f"📊 Non-zero samples: {non_zero}/{len(audio_array)} ({non_zero/len(audio_array)*100:.1f}%)")
            
            # Show first and last few samples
            print(f"📊 First 10 samples: {audio_array[:10]}")
            print(f"📊 Last 10 samples: {audio_array[-10:]}")
            
            # Check for speech-like patterns (zero crossings)
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            print(f"📊 Zero crossings: {zero_crossings}")
            
            # Calculate pitch-related metrics
            if len(audio_array) > 1000:
                # Look for repeating patterns (pitch detection)
                autocorr = np.correlate(audio_array[:1000], audio_array[:1000], mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                
                # Find peaks in autocorrelation
                peaks = []
                for i in range(1, len(autocorr)-1):
                    if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                        peaks.append(i)
                
                if peaks:
                    fundamental_period = peaks[0]
                    fundamental_freq = frame_rate / fundamental_period
                    print(f"📊 Estimated fundamental frequency: {fundamental_freq:.1f} Hz")
                    
                    if fundamental_freq < 50:
                        print("🔍 VERY LOW PITCH DETECTED - This explains the deep voice!")
                    elif fundamental_freq < 100:
                        print("🔍 Low pitch detected")
                    elif fundamental_freq > 300:
                        print("🔍 High pitch detected")
                    else:
                        print("🔍 Normal pitch range")

def explain_pitch_issue():
    """Explain the pitch issue and solution"""
    print(f"\n{'='*60}")
    print(f"🎯 PITCH ISSUE ANALYSIS")
    print(f"{'='*60}")
    print(f"")
    print(f"🔍 The problem is in the downsampling logic:")
    print(f"   - Raw WebRTC audio: 48,000 Hz")
    print(f"   - Target for Deepgram: 16,000 Hz")
    print(f"   - Current method: Taking every 3rd sample (48k/3 = 16k)")
    print(f"")
    print(f"❌ ISSUE: Taking every 3rd sample is WRONG!")
    print(f"   - This creates aliasing and pitch distortion")
    print(f"   - Your voice sounds deep because frequencies are folded")
    print(f"   - Example: 8kHz becomes 8kHz - 16kHz = -8kHz (folded)")
    print(f"")
    print(f"✅ SOLUTION: Use proper resampling")
    print(f"   - Need to use a low-pass filter before downsampling")
    print(f"   - Or use a proper resampling library")
    print(f"   - This will preserve pitch and audio quality")

if __name__ == "__main__":
    analyze_audio_files()
    explain_pitch_issue() 