# Frenemy Pipecat Project

A real-time voice chat application built with WebRTC, featuring speech-to-text transcription using Deepgram and text-to-speech synthesis using Cartesia. This project demonstrates modern voice AI integration with a clean, web-based interface and comprehensive device management.

## 🚀 Features

- **Real-time Voice Communication**: WebRTC-based audio streaming
- **Speech-to-Text**: Powered by Deepgram for accurate transcription
- **Text-to-Speech**: Natural voice synthesis using Cartesia
- **Device Selection**: Choose specific microphones and speakers/headphones
- **Web Interface**: Clean, responsive HTML client with device pickers
- **Standalone Mode**: Console-based interface with device selection
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Multiple Transport Options**: Support for WebRTC, Daily.co, and Twilio
- **Echo Response**: Demonstrates full voice processing pipeline
- **Virtual Environment**: Automatic activation and prompt customization
- **Audio Testing**: Built-in audio device testing functionality

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **WebRTC**: aiortc for real-time audio communication
- **Speech Recognition**: Deepgram SDK v3
- **Voice Synthesis**: Cartesia API
- **Package Management**: uv for fast dependency resolution
- **Development**: VS Code/Cursor integration with automatic environment activation
- **Audio Processing**: NumPy for audio format conversion

## 📋 Prerequisites

- Python 3.11 or higher
- uv package manager
- Microphone and speakers for testing
- API keys for Deepgram and Cartesia

### System Dependencies (Required for aiortc)

**macOS:**
```bash
brew install opus ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libopus-dev ffmpeg
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install opus-devel ffmpeg
# or for newer versions:
sudo dnf install opus-devel ffmpeg
```

**Windows:**
- Install [FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH
- Install [Opus](https://opus-codec.org/downloads/) or use a package manager like Chocolatey:
  ```cmd
  choco install ffmpeg
  ```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone git@github.com:KDZU-antisocial/frenemy-pipecat.git
cd frenemy-pipecat
```

### 2. Set Up Virtual Environment
```bash
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the template file
cp env.template .env

# Edit .env with your API keys
# You'll need to get API keys from:
# - Deepgram: https://console.deepgram.com/
# - Cartesia: https://cartesia.ai/
```

### 5. Start the Server
```bash
python src/server.py
```

### 6. Test the Application
1. Open your browser to `http://localhost:8000`
2. **Select your microphone** from the dropdown
3. **Select your speakers/headphones** from the dropdown
4. **Test your audio** by clicking "Test Audio"
5. Click "Connect" to establish a WebRTC connection
6. Start speaking - the system will transcribe your speech and echo it back
7. Click "Disconnect" when finished

## 🎤 Device Selection

### Web Interface
The web client automatically detects and lists all available audio devices:
- **🎤 Microphone Input**: Choose which microphone to use for speech input
- **🔊 Audio Output**: Select which speakers/headphones to use for audio output
- **Test Audio**: Verify your device selection with a test tone

### Standalone Mode
Run the application in console mode with device selection:
```bash
python src/voice_chat.py --standalone
```

This will:
1. Scan for available audio devices
2. Present an interactive menu for device selection
3. Show which devices are being used
4. Provide a standalone voice chat experience

## 📁 Project Structure

```
frenemy-pipecat/
├── src/
│   ├── voice_chat.py      # Core voice chat functionality with device selection
│   ├── server.py          # FastAPI web server with device picker integration
│   ├── main.py            # Basic service initialization
│   └── static/
│       └── index.html     # Web client interface with device pickers
├── requirements.txt       # Python dependencies
├── env.template          # Environment variables template
├── .zshrc               # Project-specific shell configuration
├── .vscode/             # VS Code/Cursor settings
└── README.md            # This file
```

## 🎯 Usage Examples

### Web Interface (Recommended)
```bash
# Start the server
python src/server.py

# Open browser to http://localhost:8000
# Select your devices and click Connect
```

### Standalone Console Mode
```bash
# Run with device selection
python src/voice_chat.py --standalone

# Follow the prompts to select your devices
```

### Alternative Transport Options
```bash
# Using the original pipecat example
python 01-say-one-thing.py --transport daily
python 01-say-one-thing.py --transport twilio
python 01-say-one-thing.py --transport webrtc
```

## 🔧 Development

### Environment Setup
The project includes automatic virtual environment activation:
- Virtual environment is automatically activated when opening the project in Cursor/VS Code
- Custom zsh prompt shows project name and git branch
- All dependencies are managed with `uv` for fast resolution

### Audio Device Integration
- **Cross-platform detection**: Automatically detects audio devices on macOS, Linux, and Windows
- **Device selection**: Both web and console interfaces for device management
- **Audio testing**: Built-in functionality to test device selection
- **Error handling**: Graceful handling of device detection and selection errors

### Adding New Features
1. The voice chat pipeline is modular and extensible
2. Easy to add new AI services or modify response logic
3. WebRTC connection can be extended for video or additional audio features
4. Device selection can be extended for additional audio parameters

### Testing
- The web interface includes real-time logging and device information
- Check browser console and server logs for debugging
- Test with different audio inputs and network conditions
- Use the "Test Audio" button to verify device selection

## 🔑 API Keys Required

### Deepgram
- **Purpose**: Speech-to-text transcription
- **Get Key**: https://console.deepgram.com/
- **Usage**: Real-time audio transcription with improved error handling

### Cartesia
- **Purpose**: Text-to-speech synthesis
- **Get Key**: https://cartesia.ai/
- **Usage**: Natural voice response generation

## 🐛 Troubleshooting

### Common Issues
1. **WebRTC Connection Fails**: Check browser permissions for microphone access
2. **API Errors**: Verify your `.env` file has correct API keys
3. **Audio Issues**: Ensure microphone and speakers are working properly
4. **Device Not Detected**: Try refreshing devices or restarting the application
5. **Dependency Conflicts**: Use `uv pip install -r requirements.txt` for clean resolution

### Audio Device Issues
- **No devices shown**: Check system audio settings and permissions
- **Device selection not working**: Try the "Refresh Devices" button
- **Test audio not playing**: Check system volume and browser audio permissions
- **Cross-platform differences**: Device detection varies by operating system

### Debug Mode
- Check browser console for WebRTC connection logs
- Server logs show transcription and processing status
- Enable browser developer tools for detailed error information
- Use the device info logging to troubleshoot device selection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with different devices and platforms
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Deepgram](https://deepgram.com/) for speech recognition
- [Cartesia](https://cartesia.ai/) for voice synthesis
- [aiortc](https://github.com/aiortc/aiortc) for WebRTC implementation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [NumPy](https://numpy.org/) for audio processing 