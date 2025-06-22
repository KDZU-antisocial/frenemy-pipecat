#!/usr/bin/env python3
"""
Terminal-based Voice Chat Application
Uses direct microphone input and system audio output, bypassing WebRTC.
"""

import asyncio
import os
import sys
import tempfile
import subprocess
import time
from typing import Optional
import numpy as np
try:
    from deepgram import DeepgramClient as Deepgram
except ImportError:
    print("❌ Deepgram package not installed. Please install it with: uv pip install deepgram-sdk")
    sys.exit(1)
from pydub import AudioSegment
from pydub.playback import play
import io

class TerminalVoiceChat:
    def __init__(self):
        """Initialize the terminal voice chat application"""
        # Load environment variables
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        self.cartesia_api_key = os.getenv('CARTESIA_API_KEY')
        
        if not self.deepgram_api_key:
            print("❌ DEEPGRAM_API_KEY not set")
            print("Please set your Deepgram API key in the environment")
            sys.exit(1)
        
        # Initialize Deepgram
        self.deepgram = Deepgram(self.deepgram_api_key)
        
        # Audio settings
        self.sample_rate = 16000  # 16kHz for better speech recognition
        self.chunk_duration = 5.0  # seconds per recording
        self.recording_device = None
        self.playback_device = None
        
        print("🎤 Terminal Voice Chat Initialized")
        print("=" * 50)
    
    def get_audio_devices(self):
        """Get available audio input and output devices"""
        print("\n🔍 Scanning for audio devices...")
        
        input_devices = []
        output_devices = []
        
        try:
            if sys.platform == "darwin":  # macOS
                # Use system_profiler to get audio devices
                result = subprocess.run(
                    ["system_profiler", "SPAudioDataType"], 
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    print("📱 Available audio devices:")
                    lines = result.stdout.split('\n')
                    current_device = None
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith(' ') and ':' in line:
                            # This is a device name
                            current_device = line.split(':')[0].strip()
                        elif line and 'Input Source:' in line:
                            # This is an input device
                            source = line.split('Input Source:')[1].strip()
                            if source != 'Default' and current_device:
                                device_name = f"{current_device} - {source}"
                                input_devices.append(device_name)
                                print(f"  🎤 {device_name}")
                        elif line and 'Output Source:' in line:
                            # This is an output device
                            source = line.split('Output Source:')[1].strip()
                            if source != 'Default' and current_device:
                                device_name = f"{current_device} - {source}"
                                output_devices.append(device_name)
                                print(f"  🔊 {device_name}")
                
                # Also try with say to list voices
                print("\n🎤 Available system voices:")
                result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
                if result.returncode == 0:
                    voices = result.stdout.split('\n')[:10]  # Show first 10
                    for voice in voices:
                        if voice.strip():
                            print(f"  {voice.strip()}")
                
            elif sys.platform.startswith("linux"):  # Linux
                # Use pactl to list devices
                result = subprocess.run(["pactl", "list", "short", "sources"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("🎤 Available input devices:")
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            print(f"  {line.strip()}")
                            input_devices.append(line.strip())
                
                result = subprocess.run(["pactl", "list", "short", "sinks"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("🔊 Available output devices:")
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            print(f"  {line.strip()}")
                            output_devices.append(line.strip())
            
            else:  # Windows
                print("🔍 Audio device detection not implemented for Windows")
                print("Using default system devices")
                
        except Exception as e:
            print(f"⚠️ Could not scan audio devices: {e}")
            print("Using default system devices")
        
        return input_devices, output_devices
    
    def select_audio_devices(self):
        """Let user select audio input and output devices"""
        print("\n🎯 Audio Device Selection")
        print("=" * 50)
        
        input_devices, output_devices = self.get_audio_devices()
        
        # Select input device
        print("\n🎤 Select Input Device:")
        if input_devices:
            for i, device in enumerate(input_devices, 1):
                print(f"  {i}. {device}")
            print(f"  {len(input_devices) + 1}. Use default microphone")
            
            while True:
                try:
                    choice = input(f"\nEnter choice (1-{len(input_devices) + 1}): ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(input_devices):
                        self.recording_device = input_devices[choice_num - 1]
                        print(f"✅ Selected input: {self.recording_device}")
                        break
                    elif choice_num == len(input_devices) + 1:
                        self.recording_device = None
                        print("✅ Using default microphone")
                        break
                    else:
                        print("❌ Invalid choice. Please try again.")
                except ValueError:
                    print("❌ Please enter a number.")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    sys.exit(0)
        else:
            print("⚠️ No input devices detected, using default")
            self.recording_device = None
        
        # Select output device (voice)
        print("\n🔊 Select Output Voice:")
        voices = []
        
        if sys.platform == "darwin":
            try:
                result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
                if result.returncode == 0:
                    voice_lines = result.stdout.split('\n')
                    for line in voice_lines:
                        if line.strip() and '#' not in line:
                            voice_name = line.split()[0] if line.split() else line.strip()
                            voices.append(voice_name)
            except Exception as e:
                print(f"⚠️ Could not get voices: {e}")
        
        if voices:
            print("Available voices:")
            for i, voice in enumerate(voices[:20], 1):  # Show first 20
                print(f"  {i}. {voice}")
            print(f"  {len(voices[:20]) + 1}. Use default voice (Alex)")
            
            while True:
                try:
                    choice = input(f"\nEnter choice (1-{len(voices[:20]) + 1}): ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(voices[:20]):
                        self.playback_device = voices[choice_num - 1]
                        print(f"✅ Selected voice: {self.playback_device}")
                        break
                    elif choice_num == len(voices[:20]) + 1:
                        self.playback_device = "Alex"
                        print("✅ Using default voice (Alex)")
                        break
                    else:
                        print("❌ Invalid choice. Please try again.")
                except ValueError:
                    print("❌ Please enter a number.")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    sys.exit(0)
        else:
            print("⚠️ Using default voice")
            self.playback_device = "Alex"
        
        print(f"\n📋 Selected Configuration:")
        print(f"  Input: {self.recording_device or 'Default microphone'}")
        print(f"  Output: {self.playback_device}")
        print("=" * 50)
    
    def record_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """Record audio from microphone"""
        if duration is None:
            duration = self.chunk_duration
        
        print(f"\n🎤 Recording {duration} seconds... (speak now)")
        
        try:
            # Create temporary file for recording
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Record audio using system command with selected device
            if sys.platform == "darwin":  # macOS
                cmd = [
                    "rec", "-r", str(self.sample_rate), "-c", "1", 
                    temp_filename
                ]
                # Add device selection if specified
                if self.recording_device:
                    # Extract device name from the device string
                    device_name = self.recording_device.split('-')[-1].strip()
                    cmd.extend(["-d", device_name])
                # Add duration using trim effect
                cmd.extend(["trim", "0", str(duration)])
            elif sys.platform.startswith("linux"):  # Linux
                cmd = [
                    "rec", "-r", str(self.sample_rate), "-c", "1", 
                    temp_filename
                ]
                # Add device selection if specified
                if self.recording_device:
                    # Extract device ID from the device string
                    device_id = self.recording_device.split()[0]
                    cmd.extend(["-d", device_id])
                # Add duration using trim effect
                cmd.extend(["trim", "0", str(duration)])
            else:  # Windows
                cmd = [
                    "sox", "-d", "-r", str(self.sample_rate), "-c", "1", 
                    temp_filename, "trim", "0", str(duration)
                ]
            
            # Record audio
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_filename):
                # Read the recorded audio
                with open(temp_filename, "rb") as f:
                    audio_data = f.read()
                
                # Clean up temporary file
                os.unlink(temp_filename)
                
                # Check if we actually got audio data
                file_size = len(audio_data)
                print(f"📊 Recorded {file_size} bytes of audio")
                
                if file_size < 1000:  # Very small file likely means no audio
                    print("🔇 No audio detected - file too small")
                    return None
                
                return audio_data
            else:
                print(f"❌ Recording failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Deepgram"""
        try:
            print("🧠 Transcribing with Deepgram...")
            
            # Send to Deepgram
            response = self.deepgram.listen.prerecorded.v("1").transcribe_file(
                {"buffer": audio_data, "mimetype": "audio/wav"}
            )
            
            if response and hasattr(response, 'results') and response.results:
                channels = response.results.channels
                if len(channels) > 0:
                    transcript = channels[0].alternatives[0].transcript
                    confidence = channels[0].alternatives[0].confidence
                    
                    if transcript.strip():
                        print(f"🎤 Transcribed: {transcript}")
                        print(f"🎤 Confidence: {confidence:.3f}")
                        return transcript
                    else:
                        print("🔇 No speech detected")
                        return None
                else:
                    print("🔇 No channels in response")
                    return None
            else:
                print("🔇 No response from Deepgram")
                return None
                
        except Exception as e:
            print(f"❌ Deepgram error: {e}")
            return None
    
    def speak_response(self, text: str):
        """Speak a response using system TTS with selected voice"""
        try:
            print(f"🔊 Speaking: {text}")
            
            if sys.platform == "darwin":  # macOS
                # Use say with selected voice
                voice = self.playback_device or "Alex"
                subprocess.run(["say", "-v", voice, text], check=True)
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run(["espeak", text], check=True)
            else:  # Windows
                subprocess.run([
                    "powershell", "-Command", 
                    f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')"
                ], check=True)
            
            print("✅ Response spoken")
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            print("Response generated but couldn't play audio")
    
    def generate_response(self, transcript: str) -> str:
        """Generate a response to the user's input"""
        # Simple response generation - you can make this more sophisticated
        transcript_lower = transcript.lower()
        
        if "hello" in transcript_lower or "hi" in transcript_lower:
            return "Hello! Nice to meet you. How can I help you today?"
        elif "how are you" in transcript_lower:
            return "I'm doing well, thank you for asking! How about you?"
        elif "bye" in transcript_lower or "goodbye" in transcript_lower:
            return "Goodbye! It was nice chatting with you."
        elif "weather" in transcript_lower:
            return "I can't check the weather, but I hope it's nice where you are!"
        elif "time" in transcript_lower:
            current_time = time.strftime("%H:%M")
            return f"The current time is {current_time}."
        elif "name" in transcript_lower:
            return "My name is Terminal Voice Assistant. What's your name?"
        else:
            return f"I heard you say: '{transcript}'. That's interesting! Tell me more."
    
    async def chat_loop(self):
        """Main chat loop"""
        print("\n🎯 Starting voice chat...")
        print("Commands:")
        print("  'quit' or 'exit' - End the chat")
        print("  'devices' - List audio devices")
        print("  'help' - Show this help")
        print("  Just speak normally to chat!")
        print("=" * 50)
        
        while True:
            try:
                # Record audio
                audio_data = self.record_audio()
                
                if audio_data is None:
                    print("⚠️ No audio recorded, trying again...")
                    continue
                
                # Transcribe audio
                transcript = self.transcribe_audio(audio_data)
                
                if transcript is None:
                    print("⚠️ No speech detected, try speaking louder...")
                    continue
                
                # Check for commands
                transcript_lower = transcript.lower()
                if transcript_lower in ['quit', 'exit', 'stop']:
                    print("👋 Goodbye!")
                    break
                elif transcript_lower == 'devices':
                    self.get_audio_devices()
                    continue
                elif transcript_lower == 'help':
                    print("\n🎯 Commands:")
                    print("  'quit' or 'exit' - End the chat")
                    print("  'devices' - List audio devices")
                    print("  'help' - Show this help")
                    print("  Just speak normally to chat!")
                    continue
                
                # Generate and speak response
                response = self.generate_response(transcript)
                self.speak_response(response)
                
                # Small delay between interactions
                await asyncio.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error in chat loop: {e}")
                print("Continuing...")
                await asyncio.sleep(1)
    
    def test_audio_system(self):
        """Test the audio recording and playback system"""
        print("\n🧪 Testing audio system...")
        
        # Test recording
        print("1. Testing audio recording...")
        audio_data = self.record_audio(3.0)  # 3 second test
        
        if audio_data is None:
            print("❌ Audio recording test failed")
            return False
        
        print("✅ Audio recording test passed")
        
        # Test transcription
        print("2. Testing transcription...")
        transcript = self.transcribe_audio(audio_data)
        
        if transcript is None:
            print("❌ Transcription test failed")
            return False
        
        print("✅ Transcription test passed")
        
        # Test TTS
        print("3. Testing text-to-speech...")
        self.speak_response("Audio system test completed successfully!")
        
        print("✅ All audio system tests passed!")
        return True

async def main():
    """Main function"""
    print("🎤 Terminal Voice Chat")
    print("=" * 50)
    
    # Create voice chat instance
    voice_chat = TerminalVoiceChat()
    
    # Let user select audio devices
    voice_chat.select_audio_devices()
    
    # Test audio system
    print("\n🧪 Would you like to test the audio system? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            if not voice_chat.test_audio_system():
                print("❌ Audio system test failed. Please check your microphone and speakers.")
                return
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return
    
    # Start chat loop
    await voice_chat.chat_loop()

if __name__ == "__main__":
    asyncio.run(main()) 