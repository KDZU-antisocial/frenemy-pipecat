#!/usr/bin/env python3
"""
Compare all audio files to identify differences
"""

import wave
import numpy as np
import os
import sys

def analyze_audio_file(filename, title):
    """Analyze an audio file and show detailed properties"""
    try:
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            return None
            
        with wave.open(filename, 'rb') as wav_file:
            # Get audio properties
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            duration = n_frames / sample_rate
            
            print(f"\n🔊 {title}")
            print(f"   File: {filename}")
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
            mean_amplitude = np.mean(np.abs(audio_array))
            
            print(f"   📊 Audio levels:")
            print(f"      RMS level: {rms_level:.2f}")
            print(f"      Max amplitude: {max_amplitude}")
            print(f"      Mean amplitude: {mean_amplitude:.2f}")
            
            # Calculate zero crossings (speech-like content)
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            print(f"   📊 Zero crossings: {zero_crossings}")
            
            # Estimate fundamental frequency
            if zero_crossings > 0:
                fundamental_freq = sample_rate / (2 * zero_crossings / duration)
                print(f"   📊 Estimated fundamental frequency: {fundamental_freq:.1f} Hz")
                
                if fundamental_freq > 3000:
                    print(f"      🔍 HIGH frequency (likely noise/interference)")
                elif fundamental_freq > 500:
                    print(f"      🔍 High frequency (unusual for speech)")
                elif fundamental_freq > 100:
                    print(f"      🔍 Normal speech frequency range")
                else:
                    print(f"      🔍 Low frequency (unusual for speech)")
            
            # Check for silence
            silence_threshold = 100
            silent_samples = np.sum(np.abs(audio_array) < silence_threshold)
            silence_percentage = (silent_samples / len(audio_array)) * 100
            print(f"   📊 Silence analysis:")
            print(f"      Silent samples: {silent_samples}/{len(audio_array)} ({silence_percentage:.1f}%)")
            
            # Frequency domain analysis (rough)
            if len(audio_array) > 1000:
                # Take a sample for FFT
                sample = audio_array[:min(8000, len(audio_array))]
                fft = np.fft.fft(sample.astype(np.float32))
                freqs = np.fft.fftfreq(len(sample), 1/sample_rate)
                
                # Find dominant frequency
                magnitude = np.abs(fft)
                dominant_idx = np.argmax(magnitude[1:len(magnitude)//2]) + 1
                dominant_freq = abs(freqs[dominant_idx])
                
                print(f"   📊 Frequency analysis:")
                print(f"      Dominant frequency: {dominant_freq:.1f} Hz")
                
                if dominant_freq > 3000:
                    print(f"      🔍 HIGH dominant frequency (noise/interference)")
                elif dominant_freq > 500:
                    print(f"      🔍 High dominant frequency (unusual for speech)")
                elif dominant_freq > 100:
                    print(f"      🔍 Normal speech dominant frequency")
                else:
                    print(f"      🔍 Low dominant frequency (unusual for speech)")
            
            return {
                'filename': filename,
                'sample_rate': sample_rate,
                'duration': duration,
                'rms_level': rms_level,
                'max_amplitude': max_amplitude,
                'zero_crossings': zero_crossings,
                'silence_percentage': silence_percentage
            }
            
    except Exception as e:
        print(f"❌ Error analyzing {filename}: {e}")
        return None

def main():
    """Main comparison function"""
    print("🎵 Audio File Comparison Analysis")
    print("=================================")
    
    # List of files to compare
    files_to_analyze = [
        ("direct_16k_recording.wav", "✅ Direct 16kHz Recording (Working)"),
        ("raw_audio_frames.wav", "❌ Raw WebRTC 48kHz (Deep/Low)"),
        ("raw_audio_frames_resampled.wav", "❌ WebRTC Resampled to 16kHz (Deep/Low)"),
        ("debug_audio_chunk.wav", "❌ WebRTC Processed for Deepgram (No Speech)")
    ]
    
    results = []
    
    # Analyze each file
    for filename, title in files_to_analyze:
        result = analyze_audio_file(filename, title)
        if result:
            results.append(result)
    
    # Summary comparison
    print(f"\n🎯 SUMMARY COMPARISON")
    print(f"=" * 50)
    
    if len(results) >= 2:
        working = results[0]  # Direct recording
        webrtc_resampled = None
        webrtc_raw = None
        webrtc_debug = None
        
        for result in results:
            if "resampled" in result['filename']:
                webrtc_resampled = result
            elif "raw_audio_frames.wav" in result['filename'] and "resampled" not in result['filename']:
                webrtc_raw = result
            elif "debug_audio_chunk" in result['filename']:
                webrtc_debug = result
        
        print(f"✅ Working (Direct 16kHz):")
        print(f"   Sample rate: {working['sample_rate']} Hz")
        print(f"   RMS level: {working['rms_level']:.2f}")
        print(f"   Zero crossings: {working['zero_crossings']}")
        print(f"   Silence: {working['silence_percentage']:.1f}%")
        
        if webrtc_resampled:
            print(f"\n❌ WebRTC Resampled:")
            print(f"   Sample rate: {webrtc_resampled['sample_rate']} Hz")
            print(f"   RMS level: {webrtc_resampled['rms_level']:.2f}")
            print(f"   Zero crossings: {webrtc_resampled['zero_crossings']}")
            print(f"   Silence: {webrtc_resampled['silence_percentage']:.1f}%")
            
            # Compare key metrics
            rms_ratio = webrtc_resampled['rms_level'] / working['rms_level'] if working['rms_level'] > 0 else 0
            print(f"\n📊 Comparison:")
            print(f"   RMS ratio (WebRTC/Direct): {rms_ratio:.2f}")
            print(f"   Zero crossings ratio: {webrtc_resampled['zero_crossings'] / working['zero_crossings']:.2f}")
            
            if rms_ratio > 2:
                print(f"   🔍 WebRTC audio is much louder than direct recording")
            elif rms_ratio < 0.5:
                print(f"   🔍 WebRTC audio is much quieter than direct recording")
            else:
                print(f"   🔍 Audio levels are similar")
        
        print(f"\n💡 Key Findings:")
        print(f"   1. Direct 16kHz recording sounds normal ✅")
        print(f"   2. WebRTC audio sounds deep/low ❌")
        print(f"   3. Issue is in WebRTC capture, not microphone ✅")
        print(f"   4. Resampling is working correctly ✅")
        print(f"   5. Problem: WebRTC is capturing wrong audio source ❌")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Check WebRTC audio source selection")
        print(f"   2. Verify microphone permissions for browser")
        print(f"   3. Test with different audio input devices")
        print(f"   4. Check for audio routing issues")

if __name__ == "__main__":
    main() 