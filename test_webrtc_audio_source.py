#!/usr/bin/env python3
"""
Test script to analyze WebRTC audio source and determine if we're getting
microphone audio or system audio (which would explain the low pitch).
"""

import asyncio
import numpy as np
import wave
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq
import os

def analyze_audio_file(filename):
    """Analyze an audio file to determine its characteristics"""
    print(f"\n🔍 Analyzing {filename}...")
    
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found")
        return
    
    # Read the audio file
    with wave.open(filename, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frames = wav_file.getnframes()
        duration = frames / sample_rate
        
        print(f"📊 Audio file info:")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Channels: {channels}")
        print(f"  Sample width: {sample_width} bytes")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Total samples: {frames}")
        
        # Read audio data
        audio_data = wav_file.readframes(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        if channels == 2:
            # Convert stereo to mono
            audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
    
    # Analyze frequency content
    print(f"\n📈 Frequency analysis:")
    
    # Calculate FFT
    fft_result = fft(audio_array)
    freqs = fftfreq(len(audio_array), 1/sample_rate)
    
    # Get positive frequencies only
    positive_freqs = freqs[:len(freqs)//2]
    positive_fft = np.abs(fft_result[:len(freqs)//2])
    
    # Find dominant frequencies
    peaks_result = signal.find_peaks(positive_fft, height=np.max(positive_fft)*0.1)
    if len(peaks_result[0]) > 0:
        peak_indices = peaks_result[0]
        peak_freqs = positive_freqs[peak_indices]
        peak_amplitudes = positive_fft[peak_indices]
        
        # Sort by amplitude
        sorted_indices = np.argsort(peak_amplitudes)[::-1]
        top_peaks = peak_freqs[sorted_indices[:10]]
        top_amplitudes = peak_amplitudes[sorted_indices][:10]
        
        print(f"  Top 10 dominant frequencies:")
        for i, (freq, amp) in enumerate(zip(top_peaks, top_amplitudes)):
            print(f"    {i+1:2d}. {freq:6.1f} Hz (amplitude: {amp:.0f})")
        
        # Check for power line noise (50/60 Hz)
        power_line_50 = np.any((top_peaks >= 48) & (top_peaks <= 52))
        power_line_60 = np.any((top_peaks >= 58) & (top_peaks <= 62))
        
        if power_line_50 or power_line_60:
            print(f"  ⚠️  POWER LINE NOISE DETECTED!")
            if power_line_50:
                print(f"     - 50Hz power line noise (Europe/Asia)")
            if power_line_60:
                print(f"     - 60Hz power line noise (North America)")
            print(f"     - This suggests we're getting system audio, not microphone!")
        else:
            print(f"  ✅ No power line noise detected - likely microphone audio")
        
        # Check for speech frequencies (80-8000 Hz)
        speech_mask = (top_peaks >= 80) & (top_peaks <= 8000)
        speech_freqs = top_peaks[speech_mask]
        speech_amplitudes = top_amplitudes[speech_mask]
        
        if len(speech_freqs) > 0:
            print(f"  🎤 Speech frequencies detected:")
            for freq, amp in zip(speech_freqs[:5], speech_amplitudes[:5]):
                print(f"     - {freq:6.1f} Hz (amplitude: {amp:.0f})")
        else:
            print(f"  🔇 No speech frequencies detected")
    else:
        print(f"  🔇 No significant frequency peaks detected")
        top_peaks = np.array([])
        speech_freqs = np.array([])
        power_line_50 = False
        power_line_60 = False
    
    # Analyze audio levels
    rms_level = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
    max_level = np.max(np.abs(audio_array))
    print(f"\n📊 Audio levels:")
    print(f"  RMS level: {rms_level:.1f}")
    print(f"  Max level: {max_level}")
    print(f"  Dynamic range: {20 * np.log10(max_level/rms_level):.1f} dB")
    
    # Determine likely source
    print(f"\n🔍 Audio source analysis:")
    if power_line_50 or power_line_60:
        print(f"  ❌ LIKELY SYSTEM AUDIO (power line noise detected)")
        print(f"     - This explains the low pitch issue")
        print(f"     - WebRTC is capturing system output, not microphone input")
    elif rms_level < 100:
        print(f"  🔇 Very low audio levels - possible microphone issue")
    elif len(speech_freqs) > 0:
        print(f"  ✅ LIKELY MICROPHONE AUDIO (speech frequencies detected)")
    else:
        print(f"  ⚠️  Unknown audio source")
    
    return {
        'sample_rate': sample_rate,
        'duration': duration,
        'rms_level': rms_level,
        'max_level': max_level,
        'dominant_freqs': top_peaks,
        'power_line_noise': power_line_50 or power_line_60,
        'speech_freqs': speech_freqs
    }

def main():
    """Main analysis function"""
    print("🎤 WebRTC Audio Source Analysis")
    print("=" * 50)
    
    # Analyze all available audio files
    audio_files = [
        "raw_audio_frames.wav",
        "debug_audio_chunk.wav", 
        "debug_audio_chunk.mp3"
    ]
    
    results = {}
    
    for filename in audio_files:
        if os.path.exists(filename):
            results[filename] = analyze_audio_file(filename)
        else:
            print(f"\n⚠️  {filename} not found - skipping")
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print("=" * 50)
    
    system_audio_count = 0
    microphone_audio_count = 0
    
    for filename, result in results.items():
        if result:
            if result['power_line_noise']:
                print(f"❌ {filename}: SYSTEM AUDIO (power line noise)")
                system_audio_count += 1
            elif len(result['speech_freqs']) > 0:
                print(f"✅ {filename}: MICROPHONE AUDIO (speech detected)")
                microphone_audio_count += 1
            else:
                print(f"⚠️  {filename}: UNKNOWN SOURCE")
    
    print(f"\n🎯 CONCLUSION:")
    if system_audio_count > 0:
        print(f"❌ PROBLEM IDENTIFIED: WebRTC is capturing system audio instead of microphone!")
        print(f"   - This explains the low pitch issue")
        print(f"   - The audio is being captured from system output, not microphone input")
        print(f"   - Solution: Fix WebRTC constraints to ensure microphone capture")
    elif microphone_audio_count > 0:
        print(f"✅ Audio appears to be from microphone")
        print(f"   - The low pitch issue might be elsewhere in the processing pipeline")
    else:
        print(f"⚠️  Unable to determine audio source")

if __name__ == "__main__":
    main() 