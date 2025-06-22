#!/usr/bin/env python3
"""
Test script to verify the audio processing pipeline and identify
where the pitch shift is occurring.
"""

import numpy as np
import wave
import io
from pydub import AudioSegment
from scipy import signal
from scipy.signal import butter, lfilter as scipy_lfilter

def test_audio_processing():
    """Test the audio processing pipeline step by step"""
    print("🎤 Testing Audio Processing Pipeline")
    print("=" * 50)
    
    # Load the raw audio file
    print("📁 Loading raw audio file...")
    with wave.open("raw_audio_frames.wav", "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        frames = wav_file.getnframes()
        audio_data = wav_file.readframes(frames)
    
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    print(f"📊 Raw audio: {len(audio_array)} samples at {sample_rate}Hz")
    print(f"📊 Audio range: {audio_array.min()} to {audio_array.max()}")
    
    # Test 1: Check if the raw audio is already pitch-shifted
    print(f"\n🔍 Test 1: Analyzing raw audio frequencies...")
    
    # Calculate FFT of raw audio
    fft_result = np.fft.fft(audio_array)
    freqs = np.fft.fftfreq(len(audio_array), 1/sample_rate)
    
    # Get positive frequencies only
    positive_freqs = freqs[:len(freqs)//2]
    positive_fft = np.abs(fft_result[:len(freqs)//2])
    
    # Find dominant frequencies
    peak_indices = signal.find_peaks(positive_fft, height=np.max(positive_fft)*0.1)[0]
    if len(peak_indices) > 0:
        peak_freqs = positive_freqs[peak_indices]
        peak_amplitudes = positive_fft[peak_indices]
        
        # Sort by amplitude
        sorted_indices = np.argsort(peak_amplitudes)[::-1]
        top_peaks = peak_freqs[sorted_indices[:5]]
        top_amplitudes = peak_amplitudes[sorted_indices][:5]
        
        print(f"  Top 5 dominant frequencies in raw audio:")
        for i, (freq, amp) in enumerate(zip(top_peaks, top_amplitudes)):
            print(f"    {i+1}. {freq:6.1f} Hz (amplitude: {amp:.0f})")
        
        # Check if these are normal speech frequencies
        normal_speech = np.any((top_peaks >= 80) & (top_peaks <= 8000))
        if normal_speech:
            # Check if the dominant frequency is in the normal speech range
            dominant_freq = top_peaks[0]
            if 1000 <= dominant_freq <= 3000:
                print(f"  ✅ Raw audio has normal speech frequencies")
            else:
                print(f"  ❌ Raw audio has abnormal dominant frequency: {dominant_freq:.1f} Hz")
                print(f"     - Should be 1000-3000 Hz for normal speech")
                print(f"     - This suggests the audio is pitch-shifted")
        else:
            print(f"  ❌ Raw audio has abnormal frequencies (likely pitch-shifted)")
    
    # Test 2: Apply the same processing as the backend
    print(f"\n🔍 Test 2: Applying backend processing...")
    
    # Use available audio data (4 seconds)
    chunk_size = min(5 * sample_rate, len(audio_array))
    audio_chunk = audio_array[:chunk_size]
    print(f"  Processing {len(audio_chunk)} samples ({len(audio_chunk)/sample_rate:.1f}s)")
    
    # Apply high-pass filter (same as backend)
    hp_cutoff = 80.0
    hp_order = 4
    b, a = butter(hp_order, hp_cutoff / (0.5 * sample_rate), btype='high', analog=False)
    print(f"  Applying {hp_cutoff}Hz high-pass filter...")
    
    audio_hp = scipy_lfilter(b, a, audio_chunk.astype(np.float32))
    audio_hp = audio_hp.astype(np.int16)
    
    # Check frequencies after high-pass filter
    fft_hp = np.fft.fft(audio_hp)
    freqs_hp = np.fft.fftfreq(len(audio_hp), 1/sample_rate)
    positive_freqs_hp = freqs_hp[:len(freqs_hp)//2]
    positive_fft_hp = np.abs(fft_hp[:len(freqs_hp)//2])
    
    peak_indices_hp = signal.find_peaks(positive_fft_hp, height=np.max(positive_fft_hp)*0.1)[0]
    if len(peak_indices_hp) > 0:
        peak_freqs_hp = positive_freqs_hp[peak_indices_hp]
        peak_amplitudes_hp = positive_fft_hp[peak_indices_hp]
        
        sorted_indices_hp = np.argsort(peak_amplitudes_hp)[::-1]
        top_peaks_hp = peak_freqs_hp[sorted_indices_hp][:5]
        top_amplitudes_hp = peak_amplitudes_hp[sorted_indices_hp][:5]
        
        print(f"  Top 5 frequencies after high-pass filter:")
        for i, (freq, amp) in enumerate(zip(top_peaks_hp, top_amplitudes_hp)):
            print(f"    {i+1}. {freq:6.1f} Hz (amplitude: {amp:.0f})")
    
    # Test 3: Create MP3 (same as backend)
    print(f"\n🔍 Test 3: Creating MP3...")
    
    # Convert to AudioSegment
    audio_segment = AudioSegment(
        audio_hp.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,  # 16-bit
        channels=1  # Mono
    )
    
    # Export as MP3
    mp3_buffer = io.BytesIO()
    audio_segment.export(
        mp3_buffer,
        format="mp3",
        bitrate="128k",
        parameters=["-ar", str(sample_rate)]
    )
    mp3_data = mp3_buffer.getvalue()
    mp3_buffer.close()
    
    print(f"  MP3 created: {len(mp3_data)} bytes")
    print(f"  Compression ratio: {len(audio_hp.tobytes())} -> {len(mp3_data)} bytes ({len(mp3_data)/len(audio_hp.tobytes())*100:.1f}%)")
    
    # Save the processed MP3 for analysis
    with open("test_processed_audio.mp3", "wb") as f:
        f.write(mp3_data)
    print(f"  ✅ Saved processed audio as: test_processed_audio.mp3")
    
    # Test 4: Load and analyze the MP3
    print(f"\n🔍 Test 4: Analyzing processed MP3...")
    
    # Load the MP3 back
    loaded_audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
    mp3_samples = np.array(loaded_audio.get_array_of_samples())
    
    print(f"  MP3 loaded: {len(mp3_samples)} samples at {loaded_audio.frame_rate}Hz")
    
    # Check if sample rate changed
    if loaded_audio.frame_rate != sample_rate:
        print(f"  ⚠️  Sample rate changed: {sample_rate}Hz -> {loaded_audio.frame_rate}Hz")
    
    # Analyze frequencies in MP3
    fft_mp3 = np.fft.fft(mp3_samples)
    freqs_mp3 = np.fft.fftfreq(len(mp3_samples), 1/loaded_audio.frame_rate)
    positive_freqs_mp3 = freqs_mp3[:len(freqs_mp3)//2]
    positive_fft_mp3 = np.abs(fft_mp3[:len(freqs_mp3)//2])
    
    peak_indices_mp3 = signal.find_peaks(positive_fft_mp3, height=np.max(positive_fft_mp3)*0.1)[0]
    if len(peak_indices_mp3) > 0:
        peak_freqs_mp3 = positive_freqs_mp3[peak_indices_mp3]
        peak_amplitudes_mp3 = positive_fft_mp3[peak_indices_mp3]
        
        sorted_indices_mp3 = np.argsort(peak_amplitudes_mp3)[::-1]
        top_peaks_mp3 = peak_freqs_mp3[sorted_indices_mp3][:5]
        top_amplitudes_mp3 = peak_amplitudes_mp3[sorted_indices_mp3][:5]
        
        print(f"  Top 5 frequencies in MP3:")
        for i, (freq, amp) in enumerate(zip(top_peaks_mp3, top_amplitudes_mp3)):
            print(f"    {i+1}. {freq:6.1f} Hz (amplitude: {amp:.0f})")
    
    print(f"\n📋 SUMMARY:")
    print("=" * 50)
    print(f"Raw audio dominant frequency: {top_peaks[0]:.1f} Hz")
    print(f"After high-pass filter: {top_peaks_hp[0]:.1f} Hz")
    print(f"In MP3: {top_peaks_mp3[0]:.1f} Hz")
    
    # Check if frequencies are consistent
    freq_diff_raw_hp = abs(top_peaks[0] - top_peaks_hp[0])
    freq_diff_hp_mp3 = abs(top_peaks_hp[0] - top_peaks_mp3[0])
    
    if freq_diff_raw_hp < 10:
        print(f"✅ High-pass filter preserves frequency")
    else:
        print(f"❌ High-pass filter changes frequency by {freq_diff_raw_hp:.1f} Hz")
    
    if freq_diff_hp_mp3 < 10:
        print(f"✅ MP3 encoding preserves frequency")
    else:
        print(f"❌ MP3 encoding changes frequency by {freq_diff_hp_mp3:.1f} Hz")
    
    # Conclusion
    if top_peaks[0] < 300:
        print(f"\n🎯 CONCLUSION:")
        print(f"❌ The audio is already pitch-shifted in the raw WebRTC capture!")
        print(f"   - Dominant frequency: {top_peaks[0]:.1f} Hz (should be 1000-3000 Hz for speech)")
        print(f"   - This suggests the issue is in the WebRTC audio capture, not processing")
        print(f"   - The audio is being captured at the wrong pitch from the start")
    else:
        print(f"\n🎯 CONCLUSION:")
        print(f"✅ Raw audio has normal frequencies")
        print(f"   - The pitch shift must be happening elsewhere")

if __name__ == "__main__":
    test_audio_processing() 