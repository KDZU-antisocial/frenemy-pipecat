#!/usr/bin/env python3
"""
Simple test script for terminal voice chat functionality
"""

import asyncio
import os
import sys
import tempfile
import subprocess
import time

class SimpleTerminalVoiceChat:
    def __init__(self):
        """Initialize the simple terminal voice chat"""
        self.sample_rate = 16000
        self.chunk_duration = 5.0
        
        print("🎤 Simple Terminal Voice Chat")
        print("=" * 50)
    
    def test_recording(self):
        """Test audio recording"""
        print("\n🎤 Testing audio recording...")
        print("Please speak for 3 seconds when prompted...")
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Record audio
            if sys.platform == "darwin":  # macOS
                cmd = ["rec", "-r", str(self.sample_rate), "-c", "1", temp_filename, "trim", "0", "3"]
            elif sys.platform.startswith("linux"):  # Linux
                cmd = ["rec", "-r", str(self.sample_rate), "-c", "1", temp_filename, "trim", "0", "3"]
            else:  # Windows
                cmd = ["sox", "-d", "-r", str(self.sample_rate), "-c", "1", temp_filename, "trim", "0", "3"]
            
            print("🎤 Recording 3 seconds... (speak now)")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_filename):
                # Get file size
                file_size = os.path.getsize(temp_filename)
                print(f"✅ Recording successful: {file_size} bytes")
                
                # Clean up
                os.unlink(temp_filename)
                return True
            else:
                print(f"❌ Recording failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return False
    
    def test_playback(self):
        """Test audio playback"""
        print("\n🔊 Testing audio playback...")
        
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["say", "-v", "Alex", "Audio playback test successful!"], check=True)
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run(["espeak", "Audio playback test successful!"], check=True)
            else:  # Windows
                subprocess.run([
                    "powershell", "-Command", 
                    "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('Audio playback test successful!')"
                ], check=True)
            
            print("✅ Audio playback test successful!")
            return True
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("\n🔍 Checking dependencies...")
        
        # Check for recording tools
        recording_tools = ["rec", "sox"]
        recording_available = False
        
        for tool in recording_tools:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool} is available")
                    recording_available = True
                    break
            except FileNotFoundError:
                print(f"❌ {tool} not found")
        
        if not recording_available:
            print("❌ No recording tool found. Please install sox:")
            if sys.platform == "darwin":
                print("  brew install sox")
            elif sys.platform.startswith("linux"):
                print("  sudo apt-get install sox")
            else:
                print("  Download from: https://sox.sourceforge.net/")
            return False
        
        # Check for TTS tools
        tts_available = False
        
        if sys.platform == "darwin":
            try:
                result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ macOS 'say' command available")
                    tts_available = True
            except FileNotFoundError:
                print("❌ macOS 'say' command not found")
        elif sys.platform.startswith("linux"):
            try:
                result = subprocess.run(["espeak", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ espeak available")
                    tts_available = True
            except FileNotFoundError:
                print("❌ espeak not found. Install with: sudo apt-get install espeak")
        else:
            print("✅ Windows TTS should be available")
            tts_available = True
        
        return recording_available and tts_available
    
    def run_tests(self):
        """Run all tests"""
        print("🧪 Running terminal voice chat tests...")
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependencies not met. Please install required tools.")
            return False
        
        # Test recording
        if not self.test_recording():
            print("❌ Recording test failed.")
            return False
        
        # Test playback
        if not self.test_playback():
            print("❌ Playback test failed.")
            return False
        
        print("\n✅ All tests passed! Terminal voice chat should work.")
        return True

def main():
    """Main function"""
    voice_chat = SimpleTerminalVoiceChat()
    success = voice_chat.run_tests()
    
    if success:
        print("\n🎯 To run the full terminal voice chat:")
        print("1. Set your DEEPGRAM_API_KEY environment variable")
        print("2. Run: python terminal_voice_chat.py")
    else:
        print("\n❌ Tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main() 