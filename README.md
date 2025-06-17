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

3. Create a `.env` file with your API keys:
```
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

- `src/` - Source code directory
- `requirements.txt` - Project dependencies
- `.env` - Environment variables (create this file with your API keys)

## Usage

Run the main application:
```bash
python src/main.py
``` 