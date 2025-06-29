#!/usr/bin/env python3
"""
Rover Assembly Voice Chat
Integrates the rover assembly guide with terminal voice chat.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Optional, List, Dict, Any
import wave
import numpy as np
try:
    from deepgram import DeepgramClient as Deepgram
except ImportError:
    print("❌ Deepgram package not installed. Please install it with: uv pip install deepgram-sdk")
    sys.exit(1)
from pydub import AudioSegment
from pydub.playback import play
import io

# Import the rover assembly guide
from rover_assembly_guide import RoverAssemblyGuide

class RoverVoiceChat:
    """Voice chat interface for rover assembly guidance"""
    
    def __init__(self):
        """Initialize the rover assembly voice chat"""
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        if not self.deepgram_api_key:
            print("❌ Error: DEEPGRAM_API_KEY environment variable not set")
            print("Please set your Deepgram API key:")
            print("export DEEPGRAM_API_KEY=your_api_key_here")
            sys.exit(1)
        
        # Initialize rover assembly guide
        self.assembly_guide = RoverAssemblyGuide()
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_duration = 3  # seconds
        self.chunk_size = self.sample_rate * self.chunk_duration
        
        # Device settings
        self.input_device = None
        self.output_device = None
        
        # State
        self.is_recording = False
        self.is_playing = False
        
        print("🚗 Rover Assembly Voice Guide")
        print("=" * 50)
    
    def print_banner(self):
        """Print the application banner"""
        print("\n" + "="*60)
        print("🚗 Rover Assembly Voice Guide")
        print("="*60)
        print("Voice-enabled assembly guide for your rover kit")
        print("Speak naturally to get step-by-step instructions")
        print("="*60)
    
    def list_audio_devices(self) -> Dict[str, List[str]]:
        """List available audio input and output devices"""
        devices = {"input": [], "output": []}
        
        try:
            # Use sox to list devices
            result = subprocess.run(['rec', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Parse sox device list format
                        parts = line.split()
                        if len(parts) >= 2:
                            device_name = ' '.join(parts[1:])
                            if 'input' in line.lower() or 'mic' in line.lower():
                                devices["input"].append(device_name)
                            elif 'output' in line.lower() or 'speaker' in line.lower():
                                devices["output"].append(device_name)
        except FileNotFoundError:
            print("⚠️  Warning: 'sox' not found. Install it for device listing:")
            print("   macOS: brew install sox")
            print("   Ubuntu: sudo apt-get install sox")
            print("   Using default devices...")
            
        return devices
    
    def select_audio_devices(self):
        """Let user select audio input and output devices"""
        print("\n🎤 Audio Device Selection")
        print("-" * 30)
        
        devices = self.list_audio_devices()
        
        # Input device selection
        if devices["input"]:
            print("\nAvailable input devices:")
            for i, device in enumerate(devices["input"], 1):
                print(f"  {i}. {device}")
            
            while True:
                try:
                    choice = input(f"\nSelect input device (1-{len(devices['input'])}): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(devices["input"]):
                        self.input_device = devices["input"][int(choice) - 1]
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except KeyboardInterrupt:
                    print("\nExiting...")
                    sys.exit(0)
        else:
            print("No input devices found. Using default.")
            self.input_device = None
        
        # Output device selection
        if devices["output"]:
            print("\nAvailable output devices:")
            for i, device in enumerate(devices["output"], 1):
                print(f"  {i}. {device}")
            
            while True:
                try:
                    choice = input(f"\nSelect output device (1-{len(devices['output'])}): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(devices["output"]):
                        self.output_device = devices["output"][int(choice) - 1]
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except KeyboardInterrupt:
                    print("\nExiting...")
                    sys.exit(0)
        else:
            print("No output devices found. Using default.")
            self.output_device = None
    
    def test_audio_system(self):
        """Test the audio input and output system"""
        print("\n🔊 Audio System Test")
        print("-" * 20)
        
        # Test recording
        print("Testing microphone...")
        print("Please speak for 3 seconds...")
        
        try:
            # Record test audio
            test_file = "test_recording.wav"
            cmd = ['rec', '-r', str(self.sample_rate), '-c', '1', test_file, 'trim', '0', '3']
            if self.input_device:
                cmd.extend(['-d', self.input_device])
            
            subprocess.run(cmd, check=True)
            print("✅ Recording test successful")
            
            # Test playback
            print("Playing back recording...")
            play_cmd = ['play', test_file]
            if self.output_device:
                play_cmd.extend(['-d', self.output_device])
            
            subprocess.run(play_cmd, check=True)
            print("✅ Playback test successful")
            
            # Clean up
            os.remove(test_file)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Audio test failed: {e}")
            return False
        except FileNotFoundError:
            print("❌ Error: 'sox' not found. Please install sox for audio testing.")
            print("   macOS: brew install sox")
            print("   Ubuntu: sudo apt-get install sox")
            return False
        
        return True
    
    async def record_audio_chunk(self) -> Optional[bytes]:
        """Record a chunk of audio"""
        try:
            # Create temporary file for recording
            temp_file = f"temp_recording_{int(time.time())}.wav"
            
            # Build recording command
            cmd = [
                'rec', '-r', str(self.sample_rate), '-c', '1', 
                temp_file, 'trim', '0', str(self.chunk_duration)
            ]
            
            if self.input_device:
                cmd.extend(['-d', self.input_device])
            
            # Record audio
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Read the recorded audio
            with wave.open(temp_file, 'rb') as wav_file:
                audio_data = wav_file.readframes(wav_file.getnframes())
            
            # Clean up
            os.remove(temp_file)
            
            return audio_data
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Recording failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            return None
    
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Deepgram"""
        try:
            import aiohttp
            
            # Prepare the request
            url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "audio/wav"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=audio_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'results' in result and 'channels' in result['results']:
                            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
                            return transcript.strip()
                    else:
                        error_text = await response.text()
                        print(f"❌ Deepgram API error: {response.status} - {error_text}")
                        return None
                        
        except ImportError:
            print("❌ Error: aiohttp not installed. Install with: pip install aiohttp")
            return None
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def speak_text(self, text: str):
        """Convert text to speech and play it"""
        try:
            # Use system TTS
            if sys.platform == "darwin":  # macOS
                subprocess.run(['say', text], check=True)
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run(['espeak', text], check=True)
            elif sys.platform == "win32":  # Windows
                # Use Windows TTS via PowerShell
                ps_script = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'
                subprocess.run(['powershell', '-Command', ps_script], check=True)
            else:
                print(f"🤖 {text}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ TTS error: {e}")
            print(f"🤖 {text}")
        except FileNotFoundError:
            print(f"🤖 {text}")
    
    def print_help(self):
        """Print help information"""
        print("\n🎤 Voice Commands:")
        print("  - Speak naturally to get assembly instructions")
        print("  - Say 'done' or 'finished' to complete a step")
        print("  - Say 'help' for assistance")
        print("  - Say 'restart' to start over")
        print("  - Say 'quit' or 'exit' to end")
        print("\n🎯 Tips:")
        print("  - Speak clearly and at a normal volume")
        print("  - Wait for the system to finish speaking")
        print("  - Confirm each step before moving to the next")
    
    async def process_voice_input(self, transcript: str) -> str:
        """Process voice input and return response"""
        print(f"🎤 You said: {transcript}")
        
        # Check for special commands
        if any(word in transcript.lower() for word in ["quit", "exit", "stop", "bye", "goodbye"]):
            return "Thank you for using the rover assembly guide! Happy exploring! 🚗"
        
        if any(word in transcript.lower() for word in ["help", "what", "how"]):
            self.print_help()
            return "I'm here to help! Just speak naturally and I'll guide you through each step."
        
        if any(word in transcript.lower() for word in ["restart", "reset", "start over", "begin again"]):
            self.assembly_guide.state.reset()
            return "Starting over! Let's begin the rover assembly from the beginning."
        
        # Process with assembly guide
        response = await self.assembly_guide.process(transcript)
        return response
    
    async def voice_chat_loop(self):
        """Main chat loop for rover assembly"""
        print("\n🚗 Starting Rover Assembly Guide...")
        print("Speak naturally to get step-by-step instructions!")
        print("Say 'help' for voice commands, 'quit' to exit.")
        print("-" * 50)
        
        # Start with welcome message
        welcome_response = await self.assembly_guide.process("start")
        print(f"🤖 {welcome_response}")
        self.speak_text(welcome_response)
        
        while True:
            try:
                print("\n🎤 Listening... (speak now)")
                
                # Record audio chunk
                audio_data = await self.record_audio_chunk()
                if not audio_data:
                    print("❌ Failed to record audio. Please try again.")
                    continue
                
                # Transcribe audio
                transcript = await self.transcribe_audio(audio_data)
                if not transcript:
                    print("❌ Could not understand audio. Please try again.")
                    continue
                
                if transcript.strip():
                    # Process the input
                    response = await self.process_voice_input(transcript)
                    
                    # Speak the response
                    print(f"🤖 {response}")
                    self.speak_text(response)
                    
                    # Check if we should exit
                    if "thank you for using" in response.lower():
                        break
                        
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the rover assembly guide!")
                break
            except Exception as e:
                print(f"❌ Error in voice chat loop: {e}")
                continue
    
    async def run(self):
        """Main run method"""
        self.print_banner()
        
        # Select audio devices
        self.select_audio_devices()
        
        # Test audio system
        if not self.test_audio_system():
            print("❌ Audio system test failed. Please check your microphone and speakers.")
            return
        
        # Start voice chat
        await self.voice_chat_loop()

async def main():
    """Main entry point"""
    try:
        voice_chat = RoverVoiceChat()
        await voice_chat.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 