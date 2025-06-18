# Frenemy Pipecat Project

This project uses Pipecat with WebRTC, Deepgram, OpenAI, and Cartesia integration.

## Setup

1. Create and activate the virtual environment:
```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the template file
cp env.template .env

# Edit .env with your API keys
# You'll need to get API keys from:
# - Deepgram: https://console.deepgram.com/
# - OpenAI: https://platform.openai.com/api-keys
# - Cartesia: https://cartesia.ai/
```

## Project Structure

- `src/` - Source code directory
  - `main.py` - Basic service initialization
  - `voice_chat.py` - Voice chat example with TTS and STT
- `requirements.txt` - Project dependencies
- `env.template` - Template for environment variables
- `.env` - Environment variables (create this file with your API keys)

## Usage

### Basic Service Check
Run the main application to verify all services are configured:
```bash
python src/main.py
```

### Voice Chat Example
Run the voice chat example with different transport options:

```bash
# Using WebRTC (default)
python src/voice_chat.py

# Using Daily.co
python src/voice_chat.py --transport daily

# Using Twilio
python src/voice_chat.py --transport twilio
```

The voice chat example:
- Uses Cartesia for text-to-speech with a British voice
- Integrates with Deepgram for speech-to-text
- Supports multiple transport options (WebRTC, Daily.co, Twilio)
- Greets users when they connect
- Provides a foundation for building voice-enabled applications

## Features
- WebRTC integration for real-time audio
- Deepgram for accurate speech-to-text
- Cartesia for natural text-to-speech
- Multiple transport options for different use cases
- Easy-to-use pipeline architecture 