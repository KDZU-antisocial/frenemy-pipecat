# FRENEMY Pipecat Operating Manual 🎤

 **⚠️ IMPORTANT: This is NOT a conversational AI system!**

 Frenemy Pipecat is a **voice-controlled tutorial system** that combines:

- **AI-powered speech recognition** (Deepgram Nova-2) for understanding your voice

- **Rule-based tutorial engine** with predefined assembly steps

 **What this means:**

- The AI only converts your speech to text - it doesn't "understand" context

- All responses are predefined and hardcoded

- The system follows a strict step-by-step assembly flow

- Think of it as a "voice-activated PowerPoint presentation" for rover assembly

 **No LLM or conversational AI is involved** - just speech recognition + rule-based logic.


## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Deep Dive](#architecture-deep-dive)
3. [AI vs Step-by-Step Components](#ai-vs-step-by-step-components)
4. [How It Works](#how-it-works)
5. [Technical Implementation](#technical-implementation)
6. [System Flow](#system-flow)
7. [Component Breakdown](#component-breakdown)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## System Overview

Frenemy Pipecat is a **voice-controlled tutorial system** that combines AI-powered speech recognition with rule-based assembly guidance. It's designed to provide hands-free, step-by-step instructions for assembling a rover kit.

### Key Characteristics
- **Voice Interface**: Speak naturally to navigate through assembly steps
- **AI Speech Recognition**: Converts your speech to text using Deepgram's Nova-2 model
- **Rule-Based Logic**: Predefined assembly steps with keyword matching
- **System TTS**: Converts responses back to speech using your operating system's text-to-speech

---

## Architecture Deep Dive

### High-Level Architecture
```
🎤 Voice Input → [AI: Deepgram STT] → 📝 Text → [Rule Engine] → 🤖 Response → [System TTS] → 🔊 Voice Output
```

### Core Components
1. **Audio Capture System** - Records voice input
2. **Speech-to-Text Engine** - Converts speech to text (AI-powered)
3. **Assembly Guide Engine** - Manages tutorial flow (rule-based)
4. **Text-to-Speech Engine** - Converts responses to speech (system TTS)
5. **State Management** - Tracks user progress through assembly steps

---

## AI vs Step-by-Step Components

### 🤖 AI Components (Machine Learning/API-based)

#### 1. Speech-to-Text (Deepgram Nova-2)
- **Location**: `rover_voice_chat.py` lines 220-250
- **Technology**: Deepgram's Nova-2 speech recognition model
- **Purpose**: Converts spoken words to text
- **AI Features**:
  - Handles different accents and dialects
  - Noise reduction and background audio filtering
  - Automatic punctuation and formatting
  - Real-time processing capabilities

```python
# AI Component: Deepgram Nova-2 Speech Recognition
url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"
```

#### 2. Text-to-Speech (System TTS)
- **Location**: `rover_voice_chat.py` lines 251-271
- **Technology**: Operating system speech synthesis
- **Purpose**: Converts text responses to speech
- **Implementation**:
  - **macOS**: `say` command
  - **Linux**: `espeak` command
  - **Windows**: PowerShell System.Speech.Synthesis

### 📋 Step-by-Step Components (Rule-based/Predefined)

#### 1. Assembly Guide Logic
- **Location**: `rover_assembly_guide.py`
- **Technology**: Hardcoded state machine with keyword matching
- **Purpose**: Manages tutorial flow and provides responses
- **Method**: Simple string matching against predefined keywords

#### 2. Audio Device Management
- **Location**: `rover_voice_chat.py` lines 68-143
- **Technology**: System calls to audio tools (`sox`, `rec`, `play`)
- **Purpose**: Handles microphone and speaker selection
- **Method**: Direct system integration, no AI

#### 3. Audio Recording/Playback
- **Location**: `rover_voice_chat.py` lines 187-219
- **Technology**: System audio tools (`rec`, `play`)
- **Purpose**: Records and plays audio
- **Method**: Direct system calls, no AI

---

## How It Works

### The Complete Flow

1. **Voice Input** 🎤
   - User speaks into microphone
   - System records 3-second audio chunks
   - Audio is saved as temporary WAV file

2. **AI Speech Recognition** 🤖
   - Audio sent to Deepgram Nova-2 API
   - Model converts speech to text
   - Returns transcribed text with confidence score

3. **Rule-Based Processing** 📋
   - Text is converted to lowercase
   - System checks for special commands (quit, help, restart)
   - Keywords are matched against current assembly step
   - State machine determines next action

4. **Response Generation** 🤖
   - Predefined response selected based on current step
   - Response text is prepared for speech synthesis

5. **Voice Output** 🔊
   - System TTS converts text to speech
   - Audio is played through selected speakers
   - User hears the response

### State Machine Flow
```
WELCOME → UNPACKING → FRAME_SETUP → WHEELS → ELECTRONICS → BATTERY → TESTING → COMPLETE
```

Each step has:
- **Predefined instructions** (hardcoded text)
- **Keyword triggers** (e.g., "done", "finished", "ready")
- **Next step logic** (automatic progression)

---

## Technical Implementation

### Audio Processing Pipeline

```python
# 1. Audio Recording
cmd = ['rec', '-r', '16000', '-c', '1', temp_file, 'trim', '0', '3']

# 2. Speech Recognition
url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"

# 3. Keyword Matching
if any(keyword in message for keyword in current_content["keywords"]):
    # Advance to next step

# 4. Text-to-Speech
subprocess.run(['say', text], check=True)  # macOS
```

### State Management

```python
@dataclass
class AssemblyState:
    current_step: RoverAssemblyStep = RoverAssemblyStep.WELCOME
    step_completed: bool = False
    user_confirmed: bool = False
    step_attempts: int = 0
    step_data: Dict[str, Any] = field(default_factory=dict)
```

### Predefined Content Structure

```python
self.step_content = {
    RoverAssemblyStep.UNPACKING: {
        "message": "Step 1: Unpacking the Kit\n\nFirst, carefully open...",
        "keywords": ["done", "finished", "complete", "ready", "next"],
        "next_prompt": "Excellent! Now let's set up the rover frame."
    },
    # ... more steps
}
```

---

## System Flow

### Startup Sequence
1. **Environment Check** - Verify API keys and dependencies
2. **Audio Device Selection** - Let user choose microphone/speakers
3. **Audio System Test** - Verify recording and playback work
4. **Welcome Message** - Start the assembly guide
5. **Main Loop** - Begin voice interaction

### Main Interaction Loop
```
while True:
    1. Record audio chunk (3 seconds)
    2. Send to Deepgram for transcription
    3. Process transcribed text
    4. Generate response
    5. Speak response
    6. Check for exit conditions
```

### Error Handling
- **Audio recording fails** → Retry with error message
- **Transcription fails** → Ask user to repeat
- **No keywords matched** → Provide guidance
- **API errors** → Display error and continue

---

## Component Breakdown

### File Structure
```
frenemy-pipecat/
├── rover_voice_chat.py          # Main voice interface
├── rover_assembly_guide.py      # Assembly logic engine
├── terminal_voice_chat.py       # Alternative terminal interface
├── src/                         # Web interface components
└── test_*.py                    # Testing and debugging scripts
```

### Key Classes

#### RoverVoiceChat
- **Purpose**: Main voice interface controller
- **Responsibilities**:
  - Audio device management
  - Speech recognition coordination
  - Text-to-speech coordination
  - User interaction flow

#### RoverAssemblyGuide
- **Purpose**: Assembly tutorial engine
- **Responsibilities**:
  - State management
  - Step progression logic
  - Response generation
  - Keyword matching

#### AssemblyState
- **Purpose**: Track user progress
- **Data**: Current step, completion status, attempts

---

## Troubleshooting Guide

### Common Issues

#### 1. "No audio detected"
**Symptoms**: Recording fails or produces empty files
**Causes**: Microphone permissions, device selection, hardware issues
**Solutions**:
- Check microphone permissions in system settings
- Verify device selection in audio setup
- Test with `python test_terminal_voice.py`

#### 2. "Deepgram error"
**Symptoms**: Transcription fails or returns errors
**Causes**: API key issues, network problems, audio format issues
**Solutions**:
- Verify `DEEPGRAM_API_KEY` is set correctly
- Check internet connection
- Test with `python test_deepgram.py`

#### 3. "TTS error"
**Symptoms**: System doesn't speak responses
**Causes**: Missing TTS tools, system configuration
**Solutions**:
- **macOS**: Verify `say` command works in terminal
- **Linux**: Install `espeak`: `sudo apt-get install espeak`
- **Windows**: Check Windows TTS is enabled

#### 4. "Recording failed"
**Symptoms**: Audio recording commands fail
**Causes**: Missing `sox` tools, device conflicts
**Solutions**:
- Install `sox`: `brew install sox` (macOS) or `sudo apt-get install sox` (Linux)
- Check microphone is not muted
- Try different input device

### Debugging Commands

```bash
# Test audio system
python test_terminal_voice.py

# Test Deepgram integration
python test_deepgram.py

# Test audio pipeline
python test_audio_pipeline.py

# Check environment
make env-check

# Test environment
make test-env
```

### Performance Optimization

#### Audio Quality
- **Sample Rate**: 16kHz (optimized for speech recognition)
- **Chunk Duration**: 3 seconds (balance between responsiveness and accuracy)
- **Format**: WAV (uncompressed for best recognition accuracy)

#### API Usage
- **Deepgram Model**: Nova-2 (latest, most accurate)
- **Features**: Smart formatting, punctuation, noise reduction
- **Rate Limiting**: Built-in delays prevent API overload

---

## Technical Specifications

### System Requirements
- **Python**: 3.11+
- **Audio Tools**: `sox` (for recording/playback)
- **Network**: Internet connection for Deepgram API
- **Hardware**: Microphone and speakers/headphones

### API Dependencies
- **Deepgram**: Speech-to-text transcription
- **System TTS**: Text-to-speech synthesis (no external API needed)

### Performance Metrics
- **Latency**: ~2-3 seconds end-to-end (recording + processing + response)
- **Accuracy**: High (Deepgram Nova-2 model)
- **Reliability**: Robust error handling and retry logic

---

## Summary

Frenemy Pipecat is a **hybrid system** that combines:

- **AI-powered speech recognition** (Deepgram Nova-2) for understanding user input
- **Rule-based tutorial engine** for managing assembly flow
- **System text-to-speech** for voice output

The system is **not** a conversational AI - it's a **voice-controlled tutorial system** that provides hands-free, step-by-step assembly guidance. The AI handles the "understanding" (speech-to-text), while predefined rules handle the "intelligence" (tutorial logic).

This architecture provides:
- **Reliability**: Rule-based logic is predictable and consistent
- **Accuracy**: AI speech recognition handles various accents and conditions
- **Simplicity**: No complex conversational AI required
- **Cost-effectiveness**: Minimal API usage, mostly local processing

The result is a robust, user-friendly system for voice-guided assembly tutorials. 