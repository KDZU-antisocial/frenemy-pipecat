# Frenemy Pipecat Project

A real-time voice chat application built with WebRTC, featuring speech-to-text transcription using Deepgram and text-to-speech synthesis using Cartesia. This project demonstrates modern voice AI integration with a clean, web-based interface.

## 🚀 Features

- **Real-time Voice Communication**: WebRTC-based audio streaming
- **Speech-to-Text**: Powered by Deepgram for accurate transcription
- **Text-to-Speech**: Natural voice synthesis using Cartesia
- **Web Interface**: Clean, responsive HTML client for easy testing
- **Multiple Transport Options**: Support for WebRTC, Daily.co, and Twilio
- **Echo Response**: Demonstrates full voice processing pipeline
- **Virtual Environment**: Automatic activation and prompt customization

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **WebRTC**: aiortc for real-time audio communication
- **Speech Recognition**: Deepgram SDK v3
- **Voice Synthesis**: Cartesia API
- **Package Management**: uv for fast dependency resolution
- **Development**: VS Code/Cursor integration with automatic environment activation

## 📋 Prerequisites

- Python 3.11 or higher
- uv package manager
- Microphone and speakers for testing
- API keys for Deepgram and Cartesia

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
2. Click "Connect" to establish a WebRTC connection
3. Start speaking - the system will transcribe your speech and echo it back
4. Click "Disconnect" when finished

## 📁 Project Structure

```
frenemy-pipecat/
├── src/
│   ├── voice_chat.py      # Core voice chat functionality
│   ├── server.py          # FastAPI web server
│   ├── main.py            # Basic service initialization
│   └── static/
│       └── index.html     # Web client interface
├── requirements.txt       # Python dependencies
├── env.template          # Environment variables template
├── .zshrc               # Project-specific shell configuration
├── .vscode/             # VS Code/Cursor settings
└── README.md            # This file
```

## 🎯 Usage Examples

### Basic Voice Chat
```bash
# Start the server
python src/server.py

# Open browser to http://localhost:8000
# Click Connect and start speaking
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

### Adding New Features
1. The voice chat pipeline is modular and extensible
2. Easy to add new AI services or modify response logic
3. WebRTC connection can be extended for video or additional audio features

### Testing
- The web interface includes real-time logging
- Check browser console and server logs for debugging
- Test with different audio inputs and network conditions

## 🔑 API Keys Required

### Deepgram
- **Purpose**: Speech-to-text transcription
- **Get Key**: https://console.deepgram.com/
- **Usage**: Real-time audio transcription

### Cartesia
- **Purpose**: Text-to-speech synthesis
- **Get Key**: https://cartesia.ai/
- **Usage**: Natural voice response generation

## 🐛 Troubleshooting

### Common Issues
1. **WebRTC Connection Fails**: Check browser permissions for microphone access
2. **API Errors**: Verify your `.env` file has correct API keys
3. **Audio Issues**: Ensure microphone and speakers are working properly
4. **Dependency Conflicts**: Use `uv pip install -r requirements.txt` for clean resolution

### Debug Mode
- Check browser console for WebRTC connection logs
- Server logs show transcription and processing status
- Enable browser developer tools for detailed error information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Deepgram](https://deepgram.com/) for speech recognition
- [Cartesia](https://cartesia.ai/) for voice synthesis
- [aiortc](https://github.com/aiortc/aiortc) for WebRTC implementation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework 