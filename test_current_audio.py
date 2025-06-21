#!/usr/bin/env python3
"""
Test script to analyze current audio files and understand the low frequency issue
"""

import numpy as np
import wave
from scipy import signal
from scipy.fft import fft, fftfreq
import os

def analyze_audio_file(filename):
    """Analyze audio file with detailed frequency analysis"""
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return
    
    print(f"\n🔊 Analyzing: {filename}")
    print("=" * 50)
    
    with wave.open(filename, 'rb') as wav_file:
        # Get audio properties
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frames = wav_file.getnframes()
        duration = frames / sample_rate
        
        print(f"📊 Audio Properties:")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Channels: {channels}")
        print(f"   Sample width: {sample_width} bytes")
        print(f"   Total frames: {frames}")
        
        # Read audio data
        audio_data = wav_file.readframes(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Convert to float for analysis
        audio_float = audio_array.astype(np.float32) / 32767.0
        
        # Basic statistics
        rms_level = np.sqrt(np.mean(audio_float**2))
        max_amplitude = np.max(np.abs(audio_float))
        mean_amplitude = np.mean(np.abs(audio_float))
        
        print(f"\n📊 Audio Levels:")
        print(f"   RMS level: {rms_level:.4f}")
        print(f"   Max amplitude: {max_amplitude:.4f}")
        print(f"   Mean amplitude: {mean_amplitude:.4f}")
        
        # Zero crossings (speech indicator)
        zero_crossings = np.sum(np.diff(np.sign(audio_float)) != 0)
        print(f"   Zero crossings: {zero_crossings}")
        
        # Silence analysis
        silence_threshold = 0.01
        silent_samples = np.sum(np.abs(audio_float) < silence_threshold)
        silence_percentage = (silent_samples / len(audio_float)) * 100
        print(f"   Silent samples: {silent_samples}/{len(audio_float)} ({silence_percentage:.1f}%)")
        
        # Frequency analysis
        if len(audio_float) > 0:
            # FFT for frequency analysis
            fft_result = fft(audio_float)
            freqs = fftfreq(len(audio_float), 1/sample_rate)
            
            # Get positive frequencies only
            positive_freqs = freqs[:len(freqs)//2]
            positive_fft = np.abs(fft_result[:len(freqs)//2])
            
            # Find dominant frequency
            dominant_idx = np.argmax(positive_fft)
            dominant_freq = positive_freqs[dominant_idx]
            
            # Find fundamental frequency (lowest significant peak)
            significant_peaks = positive_fft > (np.max(positive_fft) * 0.1)
            if np.any(significant_peaks):
                fundamental_indices = np.where(significant_peaks)[0]
                fundamental_idx = fundamental_indices[0]
                fundamental_freq = float(positive_freqs[fundamental_idx])
            else:
                fundamental_freq = float(dominant_freq)
            
            print(f"\n📊 Frequency Analysis:")
            print(f"   Dominant frequency: {dominant_freq:.1f} Hz")
            print(f"   Fundamental frequency: {fundamental_freq:.1f} Hz")
            
            # Check for speech-like characteristics
            if fundamental_freq < 50:
                print(f"   �� Very low frequency (unusual for speech)")
            elif fundamental_freq < 100:
                print(f"   🔍 Low frequency (unusual for speech)")
            elif fundamental_freq < 300:
                print(f"   🔍 Normal speech fundamental frequency")
            else:
                print(f"   🔍 High frequency (unusual for speech)")
            
            # Check for power line noise (50-60 Hz)
            power_line_peaks = []
            for freq in [50, 60]:
                idx = np.argmin(np.abs(positive_freqs - freq))
                if positive_fft[idx] > (np.max(positive_fft) * 0.1):
                    power_line_peaks.append(freq)
            
            if power_line_peaks:
                print(f"   ⚡ Power line noise detected at: {power_line_peaks} Hz")
            
            # Check for speech frequency range (100-8000 Hz)
            speech_range = (positive_freqs >= 100) & (positive_freqs <= 8000)
            speech_energy = np.sum(positive_fft[speech_range])
            total_energy = np.sum(positive_fft)
            speech_ratio = speech_energy / total_energy if total_energy > 0 else 0
            
            print(f"   🗣️ Speech frequency energy ratio: {speech_ratio:.3f}")
            if speech_ratio < 0.1:
                print(f"   🔍 Very low speech energy (likely not speech)")
            elif speech_ratio < 0.3:
                print(f"   🔍 Low speech energy (unusual for speech)")
            else:
                print(f"   🔍 Normal speech energy levels")
            
            # Top 5 frequency peaks
            peak_indices = signal.find_peaks(positive_fft, height=np.max(positive_fft)*0.05)[0]
            if len(peak_indices) > 0:
                top_peaks = sorted(peak_indices, key=lambda i: positive_fft[i], reverse=True)[:5]
                print(f"\n📊 Top 5 Frequency Peaks:")
                for i, peak_idx in enumerate(top_peaks):
                    freq = positive_freqs[peak_idx]
                    magnitude = positive_fft[peak_idx]
                    print(f"   {i+1}. {freq:.1f} Hz (magnitude: {magnitude:.0f})")

def main():
    print("🎵 Current Audio Analysis")
    print("=" * 50)
    
    # Analyze current audio files
    files_to_analyze = [
        "raw_audio_frames.wav",
        "debug_audio_chunk.wav"
    ]
    
    for filename in files_to_analyze:
        analyze_audio_file(filename)
    
    print("\n🎯 Summary:")
    print("=" * 50)
    print("If you see:")
    print("  ✅ Normal speech frequencies (100-300 Hz fundamental)")
    print("  ✅ High speech energy ratio (>0.3)")
    print("  ✅ No power line noise")
    print("  Then the audio capture is working correctly!")
    print("\n  ❌ Low frequencies (<50 Hz)")
    print("  ❌ Power line noise (50-60 Hz)")
    print("  ❌ Low speech energy ratio (<0.1)")
    print("  Then there's still an audio source issue.")

if __name__ == "__main__":
    main() 