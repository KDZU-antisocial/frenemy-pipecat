# Frenemy Pipecat 🎤

A real-time voice chat application built with Python, FastAPI, WebRTC, and Pipecat. Features both web-based and terminal interfaces for voice interaction, with a modular pipeline architecture that supports custom conversation flows.

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

- Python 3.11 or higher (tested with Python 3.13)
- uv package manager
- Microphone and speakers for testing
- API keys for Deepgram and Cartesia

### System Dependencies (Required for aiortc and av)

**macOS:**
```bash
brew install opus ffmpeg pkg-config
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libopus-dev ffmpeg pkg-config
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install opus-devel ffmpeg pkg-config
# or for newer versions:
sudo dnf install opus-devel ffmpeg pkg-config
```

**Windows:**
- Install [FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH
- Install [Opus](https://opus-codec.org/downloads/) or use a package manager like Chocolatey:
  ```cmd
  choco install ffmpeg
  ```
- Install [pkg-config](https://sourceforge.net/projects/pkgconfiglite/) for Windows

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone git@github.com:KDZU-antisocial/frenemy-pipecat.git
cd frenemy-pipecat
```

## 🏗️ Architecture

### Pipeline Steps

The application uses Pipecat's modular pipeline approach with these core steps:

1. **ASR (Speech-to-Text)** → Converts audio to text using Deepgram
2. **NLU (Natural Language Understanding)** → Processes user intent and manages conversation state
3. **Response Generation** → Generates contextual responses based on current state
4. **TTS (Text-to-Speech)** → Converts responses back to speech using system TTS

### Custom Modules

- **RoverAssemblyGuide**: Manages step-by-step assembly instructions with state tracking
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
├── rover_assembly_guide.py      # Custom pipeline step example
├── rover_voice_chat.py          # Voice-enabled assembly guide
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

#### Quick Start (Recommended)
```bash
# Clone and setup everything automatically
git clone <repository-url>
cd frenemy-pipecat
make dev-setup
make env-check
```

#### Manual Setup

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
   # Option A: Use Makefile (recommended)
   make env-setup
   
   # Option B: Manual setup
   cp env.template .env
   # Edit .env with your API keys:
   # DEEPGRAM_API_KEY=your_deepgram_key_here
   # CARTESIA_API_KEY=your_cartesia_key_here
   ```

4. **Load environment variables**:
   ```bash
   # Option A: Use Makefile (recommended)
   make env-load
   
   # Option B: Manual export
   export DEEPGRAM_API_KEY=$(grep DEEPGRAM_API_KEY .env | cut -d'=' -f2)
   export CARTESIA_API_KEY=$(grep CARTESIA_API_KEY .env | cut -d'=' -f2)
   
   # Option C: Permanent setup (adds to .zshrc)
   # The .zshrc file is already configured to auto-load .env when in the project directory
   ```

5. **Verify setup**:
   ```bash
   make env-check
   make test-env
   ```

### Environment Variables

The project requires these API keys:

- **DEEPGRAM_API_KEY**: For speech-to-text transcription
- **CARTESIA_API_KEY**: For text-to-speech synthesis (optional)
- **CARTESIA_VOICE_ID**: Voice ID for Cartesia TTS (optional)

#### Automatic Environment Loading

The project provides multiple ways to load environment variables:

1. **Makefile Commands** (Recommended): Use `make env-load` to load variables
2. **Manual Export**: Export variables directly from `.env` file
3. **Project Shell Integration**: The project `.zshrc` includes a `load_env()` function for convenience

#### Environment Management Commands

```bash
# Setup environment file
make env-setup

# Load environment variables
make env-load

# Check environment configuration
make env-check

# Test environment with Deepgram
make test-env
```

#### Manual Environment Loading

If you prefer to load environment variables manually:

```bash
# Export from .env file
export DEEPGRAM_API_KEY=$(grep DEEPGRAM_API_KEY .env | cut -d'=' -f2)
export CARTESIA_API_KEY=$(grep CARTESIA_API_KEY .env | cut -d'=' -f2)

# Or use the project's load_env function (if available)
load_env
```

## 🎯 Usage

### Quick Start Commands

Use these Makefile commands for easy startup:

```bash
# Start web voice chat
make web

# Start terminal voice chat
make terminal

# Start rover assembly guide
make rover
```

### WebRTC Voice Chat

Start the web server:
```bash
# Option A: Use Makefile (recommended)
make web

# Option B: Manual start
python src/main.py
```

Open your browser to `http://localhost:8000` and:
1. Select your audio input/output devices
2. Click "Connect" to start voice chat
3. Speak naturally - the system will transcribe and respond

### Terminal Voice Chat

For a command-line voice experience:
```bash
# Option A: Use Makefile (recommended)
make terminal

# Option B: Manual start
python terminal_voice_chat.py
```

Features:
- Interactive device selection
- Audio system testing
- Voice commands: "quit", "help", "devices"

### Rover Assembly Guide

Experience a step-by-step voice-guided assembly:
```bash
# Option A: Use Makefile (recommended)
make rover

# Option B: Manual start
python rover_voice_chat.py
```

This demonstrates:
- **State Management**: Tracks which assembly step you're on
- **Intent Recognition**: Detects keywords like "done", "help", "restart"
- **Contextual Responses**: Provides step-specific guidance
- **Error Handling**: Offers help when users get stuck

## 🔧 Custom Pipeline Development

### Creating Custom Modules

The rover assembly guide shows how to create custom Pipecat pipeline steps:

```python
class RoverAssemblyGuide:
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

## 🧩 Automated Requirements Check

To verify your environment matches `requirements.txt` and catch any dependency issues, use the automated check:

```bash
make check
```

This will:
- Check for dependency conflicts
- List all installed packages
- Show what would change if you re-applied `requirements.txt` (dry run, no changes made)

**Tip:** Run this before development or submitting a pull request to ensure your environment is up to date!

---

**Happy voice chatting! 🎤✨** 