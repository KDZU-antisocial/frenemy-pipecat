# Frenemy Pipecat 🎤

A real-time voice chat application built with Python, FastAPI, WebRTC, and Pipecat. Features both web-based and terminal interfaces for voice interaction, with a modular pipeline architecture that supports custom conversation flows.

## 🚀 Features

- **Real-time Voice Chat**: WebRTC-based browser interface with device selection
- **Terminal Voice Chat**: Command-line interface for voice interaction
- **Modular Pipeline Architecture**: Easy to extend with custom conversation flows
- **Bicycle Assembly Guide**: Example implementation of step-by-step voice guidance
- **Multiple ASR/TTS Options**: Deepgram, system TTS, and extensible for more services
- **Audio Device Selection**: Interactive device selection for input/output
- **Debug Tools**: Comprehensive audio analysis and testing utilities

## 🏗️ Architecture

### Pipeline Steps

The application uses Pipecat's modular pipeline approach with these core steps:

1. **ASR (Speech-to-Text)** → Converts audio to text using Deepgram
2. **NLU (Natural Language Understanding)** → Processes user intent and manages conversation state
3. **Response Generation** → Generates contextual responses based on current state
4. **TTS (Text-to-Speech)** → Converts responses back to speech using system TTS

### Custom Modules

- **BicycleAssemblyGuide**: Manages step-by-step assembly instructions with state tracking
- **VoiceChat**: Handles WebRTC audio processing and device management
- **TerminalVoiceChat**: Provides command-line voice interaction

## 📁 Project Structure

```
frenemy-pipecat/
├── src/                          # Main application code
│   ├── voice_chat.py            # WebRTC voice chat implementation
│   ├── server.py                # FastAPI server
│   ├── main.py                  # Application entry point
│   └── static/                  # Web interface files
├── bicycle_assembly_guide.py    # Custom pipeline step example
├── bicycle_voice_chat.py        # Voice-enabled assembly guide
├── terminal_voice_chat.py       # Terminal voice chat
├── test_*.py                    # Audio testing and debugging scripts
└── requirements.txt             # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- `uv` package manager (recommended) or `pip`
- `sox` audio tools: `brew install sox` (macOS) or `sudo apt-get install sox` (Linux)
- Microphone and speakers

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd frenemy-pipecat
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   # or with pip:
   # pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.template .env
   # Edit .env with your API keys:
   # DEEPGRAM_API_KEY=your_deepgram_key_here
   # CARTESIA_API_KEY=your_cartesia_key_here
   ```

4. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

## 🎯 Usage

### WebRTC Voice Chat

Start the web server:
```bash
python src/main.py
```

Open your browser to `http://localhost:8000` and:
1. Select your audio input/output devices
2. Click "Connect" to start voice chat
3. Speak naturally - the system will transcribe and respond

### Terminal Voice Chat

For a command-line voice experience:
```bash
python terminal_voice_chat.py
```

Features:
- Interactive device selection
- Audio system testing
- Voice commands: "quit", "help", "devices"

### Bicycle Assembly Guide

Experience a step-by-step voice-guided assembly:
```bash
python bicycle_voice_chat.py
```

This demonstrates:
- **State Management**: Tracks which assembly step you're on
- **Intent Recognition**: Detects keywords like "done", "help", "restart"
- **Contextual Responses**: Provides step-specific guidance
- **Error Handling**: Offers help when users get stuck

## 🔧 Custom Pipeline Development

### Creating Custom Modules

The bicycle assembly guide shows how to create custom Pipecat pipeline steps:

```python
class BicycleAssemblyGuide:
    def __init__(self):
        self.state = AssemblyState()  # Track conversation state
        
    async def process(self, message: str) -> str:
        # Process user input and return appropriate response
        # Handle state transitions, intent recognition, etc.
        pass
```

### Key Components

1. **State Management**: Track where the user is in the process
2. **Intent Recognition**: Detect keywords and user intent
3. **Contextual Responses**: Provide relevant help based on current state
4. **Error Handling**: Gracefully handle unclear input

### Extending the Pipeline

You can easily create similar guides for:
- **IKEA furniture assembly**
- **Recipe cooking instructions**
- **Software installation**
- **Emergency procedures**
- **Educational tutorials**

## 🧪 Testing and Debugging

### Audio System Test
```bash
python test_terminal_voice.py
```

### Audio Analysis
```bash
python test_audio_pipeline.py
python test_webrtc_audio_source.py
```

### Deepgram Integration Test
```bash
python test_deepgram.py
```

## 🔍 Troubleshooting

### Common Issues

1. **"No audio detected"**
   - Check microphone permissions
   - Verify device selection
   - Test with `python test_terminal_voice.py`

2. **"Deepgram error"**
   - Verify API key is set correctly
   - Check internet connection
   - Test with `python test_deepgram.py`

3. **"Recording failed"**
   - Install `sox`: `brew install sox` (macOS) or `sudo apt-get install sox` (Linux)
   - Check microphone is not muted
   - Try different input device

4. **"TTS error"**
   - On macOS: Verify `say` command works
   - On Linux: Install `espeak`: `sudo apt-get install espeak`
   - On Windows: Check Windows TTS is enabled

### Audio Device Issues

If you're having trouble with device selection:
```bash
# List available devices
rec -l

# Test specific device
rec -d "device_name" test.wav trim 0 3
```

## 🏗️ Architecture Deep Dive

### WebRTC Implementation

The web interface uses:
- **FastAPI**: Backend server with WebSocket support
- **aiortc**: WebRTC peer connection handling
- **Deepgram**: Real-time speech-to-text
- **System TTS**: Text-to-speech output

### Terminal Implementation

The terminal version uses:
- **subprocess**: System audio recording/playback
- **Deepgram**: Speech transcription
- **System TTS**: Voice synthesis
- **Custom state management**: Conversation flow control

### Pipeline Flow

```
User Audio → ASR (Deepgram) → NLU (Custom Logic) → Response Generation → TTS (System)
     ↑                                                                        ↓
     └─────────────────────── Audio Output ←────────────────────────────────┘
```

## 🚀 Deployment

### Local Development
```bash
python src/main.py
```

### Production
```bash
# Use a production WSGI server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom pipeline modules
4. Test thoroughly with the provided test scripts
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Pipecat](https://github.com/pipecat-ai/pipecat) for the modular pipeline framework
- [Deepgram](https://deepgram.com/) for speech-to-text capabilities
- [aiortc](https://github.com/aiortc/aiortc) for WebRTC implementation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 🎯 Next Steps

- Add support for more ASR/TTS services
- Implement visual components (web UI improvements)
- Add multi-language support
- Create more specialized conversation modules
- Add real-time audio visualization
- Implement conversation memory and context

---

**Happy voice chatting! 🎤✨** 