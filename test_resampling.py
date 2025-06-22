#!/usr/bin/env python3
"""
Test scipy resampling to verify it preserves pitch
"""

import numpy as np
from scipy import signal
import wave

def test_resampling():
    """Test resampling from 48kHz to 16kHz"""
    
    print("🧪 Testing scipy resampling...")
    
    # Create a test signal (1kHz sine wave)
    sample_rate_original = 48000
    duration = 1.0  # 1 second
    frequency = 1000  # 1kHz tone
    
    # Generate test signal
    t = np.linspace(0, duration, int(sample_rate_original * duration), False)
    test_signal = np.sin(2 * np.pi * frequency * t)
    
    # Convert to int16 (like WebRTC audio)
    test_signal_int16 = (test_signal * 32767).astype(np.int16)
    
    print(f"📊 Original signal:")
    print(f"   Sample rate: {sample_rate_original} Hz")
    print(f"   Frequency: {frequency} Hz")
    print(f"   Duration: {duration} s")
    print(f"   Samples: {len(test_signal_int16)}")
    print(f"   Max amplitude: {np.max(np.abs(test_signal_int16))}")
    
    # Test the resampling method we're using
    print(f"\n🔄 Testing resampling (48kHz -> 16kHz)...")
    
    # Convert to float (like our code)
    audio_float = test_signal_int16.astype(np.float32) / 32767.0
    
    # Calculate target samples
    target_samples = int(len(audio_float) * 16000 / 48000)
    
    # Resample using scipy
    resampled = signal.resample(audio_float, target_samples)
    
    # Convert back to int16
    resampled_int16 = (resampled * 32767).astype(np.int16)
    
    print(f"📊 Resampled signal:")
    print(f"   Target samples: {target_samples}")
    print(f"   Actual samples: {len(resampled_int16)}")
    print(f"   Max amplitude: {np.max(np.abs(resampled_int16))}")
    print(f"   Amplitude ratio: {np.max(np.abs(resampled_int16)) / np.max(np.abs(test_signal_int16)):.3f}")
    
    # Check if frequency is preserved
    # Calculate FFT to find the peak frequency
    fft_original = np.fft.fft(test_signal_int16)
    fft_resampled = np.fft.fft(resampled_int16)
    
    freqs_original = np.fft.fftfreq(len(test_signal_int16), 1/sample_rate_original)
    freqs_resampled = np.fft.fftfreq(len(resampled_int16), 1/16000)
    
    peak_idx_original = np.argmax(np.abs(fft_original[:len(fft_original)//2]))
    peak_idx_resampled = np.argmax(np.abs(fft_resampled[:len(fft_resampled)//2]))
    
    peak_freq_original = abs(freqs_original[peak_idx_original])
    peak_freq_resampled = abs(freqs_resampled[peak_idx_resampled])
    
    print(f"📊 Frequency analysis:")
    print(f"   Original peak frequency: {peak_freq_original:.1f} Hz")
    print(f"   Resampled peak frequency: {peak_freq_resampled:.1f} Hz")
    print(f"   Frequency ratio: {peak_freq_resampled / peak_freq_original:.3f}")
    
    if abs(peak_freq_resampled - peak_freq_original) < 10:
        print("✅ Frequency preserved correctly!")
    else:
        print("❌ Frequency changed - pitch issue!")
    
    # Save test files for comparison
    with wave.open("test_original_48k.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_original)
        wav_file.writeframes(test_signal_int16.tobytes())
    
    with wave.open("test_resampled_16k.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(resampled_int16.tobytes())
    
    print(f"\n💾 Saved test files:")
    print(f"   test_original_48k.wav (48kHz)")
    print(f"   test_resampled_16k.wav (16kHz)")
    print(f"   Play both files - they should sound the same pitch!")

if __name__ == "__main__":
    test_resampling() 