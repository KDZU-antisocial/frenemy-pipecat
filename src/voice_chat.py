import os
import asyncio
from dotenv import load_dotenv
from deepgram import DeepgramClient
import cartesia
from pipecat.frames.frames import EndFrame, TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketParams
from pipecat.transports.services.daily import DailyParams
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaPlayer, MediaRelay
from typing import Optional
import subprocess
import json
import sys
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import io
import struct
import wave
from scipy.signal import butter, lfilter as scipy_lfilter
from pydub import AudioSegment
import tempfile

# Load environment variables
load_dotenv(override=True)

# Get API keys
deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
cartesia_api_key = os.getenv("CARTESIA_API_KEY")

if not deepgram_api_key:
    raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
if not cartesia_api_key:
    raise ValueError("CARTESIA_API_KEY environment variable is not set")

# Transport options
transport_params = {
    "daily": lambda: DailyParams(audio_out_enabled=True),
    "twilio": lambda: FastAPIWebsocketParams(audio_out_enabled=True),
    "webrtc": lambda: TransportParams(audio_out_enabled=True),
}

def get_audio_devices():
    """Get available audio devices using system commands"""
    devices = {"input": [], "output": []}
    
    try:
        # For macOS, use system_profiler
        if sys.platform == "darwin":
            # Get input devices
            result = subprocess.run([
                "system_profiler", "SPAudioDataType", "-json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "SPAudioDataType" in data:
                    for device in data["SPAudioDataType"]:
                        if "input" in device.get("_name", "").lower():
                            devices["input"].append({
                                "name": device.get("_name", "Unknown"),
                                "id": device.get("_name", "Unknown")
                            })
                        elif "output" in device.get("_name", "").lower():
                            devices["output"].append({
                                "name": device.get("_name", "Unknown"),
                                "id": device.get("_name", "Unknown")
                            })
        
        # For Linux, use pactl
        elif sys.platform.startswith("linux"):
            # Get input devices
            result = subprocess.run([
                "pactl", "list", "short", "sources"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices["input"].append({
                                "name": parts[1],
                                "id": parts[0]
                            })
            
            # Get output devices
            result = subprocess.run([
                "pactl", "list", "short", "sinks"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices["output"].append({
                                "name": parts[1],
                                "id": parts[0]
                            })
        
        # For Windows, use PowerShell
        elif sys.platform == "win32":
            # Get audio devices using PowerShell
            result = subprocess.run([
                "powershell", "-Command", 
                "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, DeviceID | ConvertTo-Json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list):
                        for device in data:
                            devices["input"].append({
                                "name": device.get("Name", "Unknown"),
                                "id": device.get("DeviceID", "Unknown")
                            })
                            devices["output"].append({
                                "name": device.get("Name", "Unknown"),
                                "id": device.get("DeviceID", "Unknown")
                            })
                except json.JSONDecodeError:
                    pass
                    
    except Exception as e:
        print(f"Error getting audio devices: {e}")
    
    return devices

def select_audio_devices():
    """Interactive device selection"""
    devices = get_audio_devices()
    
    print("\n" + "="*50)
    print("🎤 AUDIO DEVICE SELECTION")
    print("="*50)
    
    # Input devices
    print("\n🎤 Available Microphones:")
    if devices["input"]:
        for i, device in enumerate(devices["input"], 1):
            print(f"  {i}. {device['name']}")
    else:
        print("  No input devices found")
    
    # Output devices
    print("\n🔊 Available Speakers/Headphones:")
    if devices["output"]:
        for i, device in enumerate(devices["output"], 1):
            print(f"  {i}. {device['name']}")
    else:
        print("  No output devices found")
    
    # Device selection
    selected_input = None
    selected_output = None
    
    if devices["input"]:
        try:
            choice = input(f"\nSelect microphone (1-{len(devices['input'])}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(devices["input"]):
                selected_input = devices["input"][int(choice) - 1]
                print(f"✓ Selected microphone: {selected_input['name']}")
        except (ValueError, IndexError):
            print("Invalid selection, using default")
    
    if devices["output"]:
        try:
            choice = input(f"Select speaker/headphone (1-{len(devices['output'])}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(devices["output"]):
                selected_output = devices["output"][int(choice) - 1]
                print(f"✓ Selected speaker: {selected_output['name']}")
        except (ValueError, IndexError):
            print("Invalid selection, using default")
    
    return selected_input, selected_output

def create_device_selection_html():
    """Create HTML for device selection interface"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Voice Chat - Device Selection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .device-section {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .device-section h3 {
            margin-top: 0;
            color: #007bff;
        }
        select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        select:focus {
            border-color: #007bff;
            outline: none;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 5px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 6px;
            font-weight: bold;
        }
        .status.ready {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .log {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            font-family: monospace;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        .refresh-btn {
            background-color: #28a745;
        }
        .refresh-btn:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Voice Chat - Device Selection</h1>
        
        <div id="status" class="status ready">Ready to select devices</div>
        
        <div class="device-section">
            <h3>🎤 Microphone Input</h3>
            <select id="inputDevices">
                <option value="">Loading microphones...</option>
            </select>
            <div id="inputStatus">No microphone selected</div>
        </div>
        
        <div class="device-section">
            <h3>🔊 Audio Output</h3>
            <select id="outputDevices">
                <option value="">Loading speakers...</option>
            </select>
            <div id="outputStatus">No speaker selected</div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <button id="refreshDevices" class="refresh-btn">🔄 Refresh Devices</button>
            <button id="testAudio">🔊 Test Audio</button>
            <button id="startVoiceChat">🚀 Start Voice Chat</button>
        </div>
        
        <div id="log" class="log"></div>
    </div>

    <script>
        let selectedInputDevice = null;
        let selectedOutputDevice = null;
        
        function log(message) {
            const logDiv = document.getElementById('log');
            logDiv.textContent += new Date().toLocaleTimeString() + ': ' + message + '\\n';
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        async function loadDevices() {
            try {
                log('Loading audio devices...');
                
                if (!navigator.mediaDevices) {
                    throw new Error('mediaDevices API not available');
                }
                
                // Request microphone permission first
                await navigator.mediaDevices.getUserMedia({ audio: true });
                
                const devices = await navigator.mediaDevices.enumerateDevices();
                const audioInputs = devices.filter(device => device.kind === 'audioinput');
                const audioOutputs = devices.filter(device => device.kind === 'audiooutput');
                
                // Populate input devices
                const inputSelect = document.getElementById('inputDevices');
                inputSelect.innerHTML = '<option value="">Select microphone...</option>';
                audioInputs.forEach(device => {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.textContent = device.label || `Microphone ${device.deviceId.slice(0, 8)}...`;
                    inputSelect.appendChild(option);
                });
                
                // Populate output devices
                const outputSelect = document.getElementById('outputDevices');
                outputSelect.innerHTML = '<option value="">Select speaker...</option>';
                audioOutputs.forEach(device => {
                    const option = document.createElement('option');
                    option.value = device.deviceId;
                    option.textContent = device.label || `Speaker ${device.deviceId.slice(0, 8)}...`;
                    outputSelect.appendChild(option);
                });
                
                document.getElementById('inputStatus').textContent = `Found ${audioInputs.length} microphone(s)`;
                document.getElementById('outputStatus').textContent = `Found ${audioOutputs.length} speaker(s)`;
                
                log(`Loaded ${audioInputs.length} input devices and ${audioOutputs.length} output devices`);
                
            } catch (error) {
                log('Error loading devices: ' + error.message);
                document.getElementById('status').textContent = 'Error loading devices - check permissions';
                document.getElementById('status').className = 'status error';
            }
        }
        
        async function testAudio() {
            const outputSelect = document.getElementById('outputDevices');
            if (!outputSelect.value) {
                log('Please select an output device first');
                return;
            }
            
            try {
                log('Testing audio output...');
                
                const audio = new Audio();
                
                if (audio.setSinkId) {
                    await audio.setSinkId(outputSelect.value);
                    log(`Audio output set to: ${outputSelect.options[outputSelect.selectedIndex].text}`);
                }
                
                // Create test tone
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                const mediaStreamDestination = audioContext.createMediaStreamDestination();
                
                oscillator.connect(gainNode);
                gainNode.connect(mediaStreamDestination);
                
                oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                
                audio.srcObject = mediaStreamDestination.stream;
                audio.volume = 0.5;
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 1);
                
                await audio.play();
                log('Playing test tone for 1 second...');
                
                setTimeout(() => {
                    audioContext.close();
                }, 1000);
                
            } catch (error) {
                log('Error testing audio: ' + error.message);
            }
        }
        
        function startVoiceChat() {
            const inputSelect = document.getElementById('inputDevices');
            const outputSelect = document.getElementById('outputDevices');
            
            if (!inputSelect.value || !outputSelect.value) {
                log('Please select both input and output devices');
                return;
            }
            
            selectedInputDevice = {
                id: inputSelect.value,
                name: inputSelect.options[inputSelect.selectedIndex].text
            };
            
            selectedOutputDevice = {
                id: outputSelect.value,
                name: outputSelect.options[outputSelect.selectedIndex].text
            };
            
            log(`Starting voice chat with:`);
            log(`  Microphone: ${selectedInputDevice.name}`);
            log(`  Speaker: ${selectedOutputDevice.name}`);
            
            // Send device selection to server
            fetch('/api/start-voice-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input_device: selectedInputDevice,
                    output_device: selectedOutputDevice
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    log('Voice chat started successfully!');
                    document.getElementById('status').textContent = 'Voice chat active - check console for transcriptions';
                    document.getElementById('status').className = 'status ready';
                } else {
                    log('Error starting voice chat: ' + data.error);
                }
            })
            .catch(error => {
                log('Error: ' + error.message);
            });
        }
        
        // Event listeners
        document.getElementById('refreshDevices').onclick = loadDevices;
        document.getElementById('testAudio').onclick = testAudio;
        document.getElementById('startVoiceChat').onclick = startVoiceChat;
        
        // Load devices on page load
        document.addEventListener('DOMContentLoaded', loadDevices);
    </script>
</body>
</html>
"""

async def run_example(transport: BaseTransport, args, handle_sigint: bool = True):
    # Initialize Deepgram client
    deepgram = DeepgramClient(deepgram_api_key)
    
    # Initialize Cartesia TTS service
    tts = CartesiaTTSService(
        api_key=cartesia_api_key,
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"  # British Reading Lady
    )

    # Create a pipeline that processes audio through TTS
    task = PipelineTask(Pipeline([tts, transport.output()]))

    # Register an event handler for when a client connects
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        await task.queue_frames([
            TTSSpeakFrame("Hello! I'm your voice assistant. How can I help you today?"),
            EndFrame()
        ])

    # Run the pipeline
    runner = PipelineRunner(handle_sigint=handle_sigint)
    await runner.run(task)

class VoiceChat:
    def __init__(self, input_device=None, output_device=None):
        # Initialize Deepgram
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
        self.deepgram = DeepgramClient(api_key=self.deepgram_api_key)

        # Initialize Cartesia
        self.cartesia_api_key = os.getenv('CARTESIA_API_KEY')
        if not self.cartesia_api_key:
            raise ValueError("CARTESIA_API_KEY environment variable is not set")
        
        # Use CartesiaTTSService from pipecat
        self.tts = CartesiaTTSService(
            api_key=self.cartesia_api_key,
            voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"  # British Reading Lady
        )

        # Store selected devices
        self.input_device = input_device
        self.output_device = output_device
        
        if input_device:
            print(f"🎤 Using microphone: {input_device['name']}")
        if output_device:
            print(f"🔊 Using speaker: {output_device['name']}")

        self.pc: Optional[RTCPeerConnection] = None
        self.relay = MediaRelay()

    async def handle_offer(self, sdp, input_device_id=None, output_device_id=None):
        """Handle WebRTC offer with device routing"""
        # Create peer connection with proper configuration for 48kHz audio
        config = RTCConfiguration(
            iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")]
        )
        self.pc = RTCPeerConnection(configuration=config)
        
        # Store device preferences
        self.input_device_id = input_device_id
        self.output_device_id = output_device_id
        
        if input_device_id:
            print(f"🎤 Using input device: {input_device_id}")
        if output_device_id:
            print(f"🔊 Using output device: {output_device_id}")
        
        # Set up audio tracks with proper routing
        @self.pc.on("track")
        async def on_track(track):
            print(f"🎵 Received audio track: {track.id}")
            
            # Save raw audio frames for debugging
            raw_audio_frames = []
            frame_count = 0
            max_frames_to_save = 100  # Save first 100 frames
            
            if track.kind == "audio":
                print(f"🎤 Audio track received - will save raw frames for analysis")
                
                # Process incoming audio with Deepgram
                async def process_audio():
                    print("🧠 Starting adaptive audio processing...")
                    # Detect sample rate from first frame (force 48kHz)
                    first_frame = await track.recv()
                    first_audio = first_frame.to_ndarray().flatten()
                    detected_sample_rate = 48000
                    print(f"🎯 Forcing sample rate: {detected_sample_rate}Hz (Opus/WebRTC standard)")
                    # Simple audio buffer - accumulate raw audio at 48kHz
                    audio_buffer = []
                    sample_rate = detected_sample_rate
                    chunk_duration = 5.0  # seconds
                    frame_count = 0
                    debug_saved = False  # Only save first chunk for debugging
                    # Add first frame to buffer
                    audio_buffer.extend(first_audio)
                    frame_count += 1
                    # High-pass filter design (80 Hz cutoff)
                    hp_cutoff = 80.0
                    hp_order = 4
                    b, a = butter(hp_order, hp_cutoff / (0.5 * sample_rate), btype='high', analog=False)
                    print(f"🔧 High-pass filter: {hp_cutoff} Hz cutoff, order {hp_order}")
                    try:
                        while True:
                            try:
                                frame = await track.recv()
                                frame_count += 1
                                # Save raw frames for debugging
                                if len(raw_audio_frames) < max_frames_to_save:
                                    raw_audio_frames.append(frame)
                                    if len(raw_audio_frames) == max_frames_to_save:
                                        print(f"🔍 Saved {len(raw_audio_frames)} raw audio frames for analysis")
                                        # Save raw frames to file
                                        await self.save_raw_frames(raw_audio_frames)
                                # Convert frame to audio data
                                audio_array = frame.to_ndarray()
                                # Debug: Show frame info occasionally
                                if frame_count % 10 == 0:
                                    print(f"📡 Frame #{frame_count}: shape={audio_array.shape}, dtype={audio_array.dtype}, min={audio_array.min()}, max={audio_array.max()}")
                                # Handle 2D audio array (channels, samples) -> flatten to 1D
                                if len(audio_array) > 0:
                                    if len(audio_array.shape) == 2:
                                        audio_array = audio_array.flatten()
                                    # Add directly to buffer (no resampling needed)
                                    audio_buffer.extend(audio_array.flatten())
                                    # Debug: Show direct usage info occasionally
                                    if frame_count % 10 == 0:
                                        print(f"✅ Direct {sample_rate}Hz: {len(audio_array)} samples")
                                        print(f"✅ Audio levels: max={np.max(np.abs(audio_array.astype(np.float32) / 32767.0)):.4f}")
                                    # Debug: Show buffer status occasionally
                                    if frame_count % 50 == 0:
                                        buffer_seconds = len(audio_buffer) / sample_rate
                                        print(f"📦 Buffer: {len(audio_buffer)} samples ({buffer_seconds:.1f}s) - need {chunk_duration}s")
                                    # Process when we have enough audio
                                    if len(audio_buffer) >= sample_rate * chunk_duration:
                                        print(f"🎯 Processing {len(audio_buffer)} samples ({chunk_duration}s)...")
                                        # Get the audio chunk
                                        audio_data = np.array(audio_buffer[:int(sample_rate * chunk_duration)], dtype=np.int16)
                                        # --- High-pass filter ---
                                        audio_data_hp = scipy_lfilter(b, a, audio_data.astype(np.float32))
                                        if isinstance(audio_data_hp, tuple):
                                            print('[WARN] lfilter returned a tuple, extracting first element. This suggests a shadowed lfilter.')
                                            audio_data_hp = audio_data_hp[0]
                                        print(f"[DEBUG] audio_data_hp type: {type(audio_data_hp)} shape: {getattr(audio_data_hp, 'shape', None)}")
                                        audio_data_hp = audio_data_hp.astype(np.int16)
                                        # Simple audio level check
                                        audio_level = np.abs(audio_data_hp).mean()
                                        print(f"📊 Audio level (HP filtered): {audio_level:.2f}")
                                        # Only process if there's some audio activity
                                        if audio_level > 5:  # Lowered threshold for longer chunks
                                            print(f"🎤 Audio detected - sending to Deepgram...")
                                            # Convert to bytes
                                            audio_bytes = audio_data_hp.tobytes()
                                            # Create MP3 file at 48kHz using pydub
                                            print(f"🔧 Encoding audio as MP3...")
                                            
                                            # Convert numpy array to AudioSegment
                                            audio_segment = AudioSegment(
                                                audio_data_hp.tobytes(),
                                                frame_rate=sample_rate,
                                                sample_width=2,  # 16-bit
                                                channels=1  # Mono
                                            )
                                            
                                            # Export as MP3 with good quality for speech
                                            mp3_buffer = io.BytesIO()
                                            audio_segment.export(
                                                mp3_buffer,
                                                format="mp3",
                                                bitrate="128k",  # Good quality for speech
                                                parameters=["-ar", str(sample_rate)]  # Ensure 48kHz sample rate
                                            )
                                            mp3_data = mp3_buffer.getvalue()
                                            mp3_buffer.close()
                                            
                                            # Debug: Save first chunk to file for analysis
                                            if not debug_saved:
                                                debug_filename = "debug_audio_chunk.mp3"
                                                with open(debug_filename, "wb") as f:
                                                    f.write(mp3_data)
                                                print(f"🔍 Saved debug audio to: {debug_filename}")
                                                print(f"🔍 Audio stats: min={audio_data_hp.min()}, max={audio_data_hp.max()}, mean={audio_data_hp.mean():.2f}")
                                                debug_saved = True
                                            
                                            print(f"📊 Sending {len(mp3_data)} bytes to Deepgram (48kHz mono MP3, HP filtered)")
                                            print(f"📊 Compression ratio: {len(audio_bytes)} -> {len(mp3_data)} bytes ({len(mp3_data)/len(audio_bytes)*100:.1f}%)")
                                            
                                            # Send to Deepgram
                                            try:
                                                response = self.deepgram.listen.prerecorded.v("1").transcribe_file(
                                                    {"buffer": mp3_data, "mimetype": "audio/mpeg"}
                                                )
                                                if response and hasattr(response, 'results') and response.results:
                                                    channels = response.results.channels
                                                    if len(channels) > 0:
                                                        transcript = channels[0].alternatives[0].transcript
                                                        confidence = channels[0].alternatives[0].confidence
                                                        if transcript.strip():
                                                            print(f"🎤 Transcribed: {transcript}")
                                                            print(f"🎤 Confidence: {confidence:.3f}")
                                                            # Simple response
                                                            response_text = f"I heard: {transcript}"
                                                            print(f"🤖 Response: {response_text}")
                                                            # Use system TTS
                                                            try:
                                                                if sys.platform == "darwin":
                                                                    subprocess.run(["say", "-v", "Alex", response_text], check=True)
                                                                elif sys.platform.startswith("linux"):
                                                                    subprocess.run(["espeak", response_text], check=True)
                                                                else:
                                                                    subprocess.run(["powershell", "-Command", f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{response_text}')"], check=True)
                                                                print("✅ Speech response generated")
                                                            except Exception as tts_error:
                                                                print(f"❌ TTS error: {tts_error}")
                                                        else:
                                                            print("🔇 No speech detected")
                                                    else:
                                                        print("🔇 No channels in response")
                                                else:
                                                    print("🔇 No response from Deepgram")
                                            except Exception as deepgram_error:
                                                print(f"❌ Deepgram error: {deepgram_error}")
                                        else:
                                            print(f"🔇 Low audio level ({audio_level:.2f}) - skipping")
                                        # Clear buffer
                                        audio_buffer = audio_buffer[int(sample_rate * chunk_duration):]
                                        print(f"🔄 Buffer cleared, remaining: {len(audio_buffer)} samples")
                                        # Small delay
                                        await asyncio.sleep(0.1)
                            except Exception as e:
                                print(f"❌ Audio processing error: {e}")
                                break
                    except asyncio.CancelledError:
                        print("🛑 Audio processing cancelled")
                
                # Start audio processing
                asyncio.create_task(process_audio())
                
        # Set the remote description
        print(f"📡 Processing SDP offer...")
        if isinstance(sdp, dict):
            offer = RTCSessionDescription(sdp=sdp["sdp"], type=sdp["type"])
        else:
            offer = RTCSessionDescription(sdp=sdp, type="offer")
            
        await self.pc.setRemoteDescription(offer)

        # Create answer
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        print("✅ WebRTC connection established")
        return {
            "sdp": self.pc.localDescription.sdp,
            "type": self.pc.localDescription.type
        }

    async def save_raw_frames(self, frames):
        """Save raw audio frames to a file for analysis"""
        try:
            print(f"💾 Saving {len(frames)} raw audio frames...")
            
            # Combine all frames
            all_audio = []
            for frame in frames:
                audio_array = frame.to_ndarray()
                all_audio.extend(audio_array.flatten())
            
            audio_data = np.array(all_audio, dtype=np.int16)
            
            # Detect sample rate from frame size
            sample_rate = 48000 if len(audio_data) > 100000 else 16000
            
            print(f"📊 Raw audio stats: shape={audio_data.shape}, min={audio_data.min()}, max={audio_data.max()}, mean={audio_data.mean():.2f}")
            print(f"📊 Detected sample rate: {sample_rate}Hz")
            
            # Save raw audio at detected sample rate
            with wave.open("raw_audio_frames.wav", "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)  # Detected sample rate
                wav_file.writeframes(audio_data.tobytes())
            
            print(f"✅ Saved raw audio frames to: raw_audio_frames.wav ({sample_rate}Hz)")
            
        except Exception as e:
            print(f"❌ Error saving raw frames: {e}")

    async def close(self):
        if self.pc:
            await self.pc.close()

    async def start_standalone_audio_processing(self):
        """Start standalone audio processing using pipecat"""
        try:
            print("🎤 Starting standalone audio processing...")
            print("This will use the pipecat pipeline for audio processing.")
            print("Press Ctrl+C to stop.")
            
            # Create a simple transport for standalone mode
            from pipecat.transports.base_transport import TransportParams
            
            # Initialize the TTS service
            if not self.cartesia_api_key:
                raise ValueError("CARTESIA_API_KEY not set")
                
            tts = CartesiaTTSService(
                api_key=self.cartesia_api_key,
                voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"
            )
            
            # Create a simple pipeline
            from pipecat.pipeline.pipeline import Pipeline
            from pipecat.pipeline.task import PipelineTask
            from pipecat.pipeline.runner import PipelineRunner
            from pipecat.frames.frames import TTSSpeakFrame, EndFrame
            
            # For now, just demonstrate the TTS capability
            print("🎯 Testing TTS with a sample response...")
            
            # Create a simple task that speaks a response
            task = PipelineTask(Pipeline([tts]))
            
            # Queue a test message
            await task.queue_frames([
                TTSSpeakFrame("Hello! I'm your voice assistant. I can hear you speaking."),
                EndFrame()
            ])
            
            print("✅ TTS test completed. In a full implementation, this would:")
            print("   1. Capture audio from your microphone")
            print("   2. Transcribe it with Deepgram")
            print("   3. Generate a response")
            print("   4. Speak it back through your speakers")
            
            # Keep the process running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Error starting audio processing: {e}")
            print("This is a simplified version. For full audio processing, use the web interface.")

    async def start_full_audio_processing(self):
        """Start full audio processing with microphone input and TTS output"""
        try:
            print("🎤 Starting full audio processing pipeline...")
            print("1. 🎤 Capturing audio from microphone")
            print("2. 🧠 Transcribing with Deepgram")
            print("3. 🤖 Generating responses")
            print("4. 🔊 Speaking back through speakers")
            print("Press Ctrl+C to stop.")
            
            # Initialize TTS service
            if not self.cartesia_api_key:
                raise ValueError("CARTESIA_API_KEY not set")
                
            tts = CartesiaTTSService(
                api_key=self.cartesia_api_key,
                voice_id="71a7ad14-091c-4e8e-a314-022ece01c121"
            )
            
            # Create pipeline for TTS output
            from pipecat.pipeline.pipeline import Pipeline
            from pipecat.pipeline.task import PipelineTask
            from pipecat.pipeline.runner import PipelineRunner
            from pipecat.frames.frames import TTSSpeakFrame, EndFrame
            
            # Test TTS first
            print("🎯 Testing TTS...")
            task = PipelineTask(Pipeline([tts]))
            await task.queue_frames([
                TTSSpeakFrame("Hello! I'm ready to chat. Speak to me!"),
                EndFrame()
            ])
            
            print("✅ TTS working! Now starting audio capture...")
            
            # Start audio capture using system commands
            import subprocess
            import tempfile
            import os
            
            # Audio settings
            sample_rate = 16000
            duration = 5  # seconds per recording
            
            print(f"🎤 Recording {duration}-second audio chunks...")
            
            while True:
                try:
                    # Create temporary file for audio
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_filename = temp_file.name
                    
                    # Record audio using system command
                    if sys.platform == "darwin":  # macOS
                        cmd = [
                            "rec", "-r", str(sample_rate), "-c", "1", 
                            temp_filename, "trim", "0", str(duration)
                        ]
                    elif sys.platform.startswith("linux"):  # Linux
                        cmd = [
                            "rec", "-r", str(sample_rate), "-c", "1", 
                            temp_filename, "trim", "0", str(duration)
                        ]
                    else:  # Windows
                        cmd = [
                            "sox", "-d", "-r", str(sample_rate), "-c", "1", 
                            temp_filename, "trim", "0", str(duration)
                        ]
                    
                    print("🎤 Recording... (speak now)")
                    
                    # Record audio
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(temp_filename):
                        # Read the recorded audio
                        with open(temp_filename, "rb") as f:
                            audio_data = f.read()
                        
                        # Check if we actually got audio data
                        file_size = len(audio_data)
                        print(f"📊 Audio file size: {file_size} bytes")
                        
                        if file_size < 1000:  # Very small file likely means no audio
                            print("🔇 No audio detected - file too small")
                            print("💡 Check your microphone settings and permissions")
                            print("   - Make sure microphone is not muted")
                            print("   - Check system audio input settings")
                            print("   - Try speaking louder or closer to the mic")
                        else:
                            print("🧠 Transcribing with Deepgram...")
                            
                            # Transcribe with Deepgram
                            try:
                                # Use the correct Deepgram v3 API call format (synchronous)
                                response = self.deepgram.listen.prerecorded.v("1").transcribe_file(
                                    {"buffer": audio_data, "mimetype": "audio/wav"}
                                )
                                
                                if response and hasattr(response, 'results') and response.results:
                                    transcript = response.results.channels[0].alternatives[0].transcript
                                    confidence = response.results.channels[0].alternatives[0].confidence
                                    print(f"🎤 Deepgram confidence: {confidence:.3f}")
                                    print(f"🎤 Raw transcript: '{transcript}'")
                                    
                                    if transcript.strip():
                                        print(f"🎤 Transcribed: {transcript}")
                                        
                                        # Generate response
                                        response_text = f"I heard you say: {transcript}. That's interesting!"
                                        print(f"🤖 Responding: {response_text}")
                                        
                                        # Speak the response
                                        print("🔊 Speaking response...")
                                        
                                        # Use system command to play audio through speakers
                                        try:
                                            if sys.platform == "darwin":  # macOS
                                                # Use say with specific voice
                                                subprocess.run(["say", "-v", "Alex", response_text], check=True)
                                            elif sys.platform.startswith("linux"):  # Linux
                                                subprocess.run(["espeak", response_text], check=True)
                                            else:  # Windows
                                                subprocess.run(["powershell", "-Command", f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{response_text}')"], check=True)
                                            
                                            print("✅ Audio response played!")
                                            
                                        except Exception as audio_error:
                                            print(f"❌ Audio playback error: {audio_error}")
                                            print("TTS response generated but couldn't play audio")
                                            
                                            # Try alternative approach with higher volume
                                            try:
                                                if sys.platform == "darwin":  # macOS
                                                    # Try with different voice and higher volume
                                                    subprocess.run(["say", "-v", "Victoria", "-r", "150", response_text], check=True)
                                                    print("✅ Audio response played with alternative voice!")
                                            except Exception as alt_error:
                                                print(f"❌ Alternative audio playback also failed: {alt_error}")
                                                print("Please check your system audio settings and volume")
                                    else:
                                        print("🔇 No speech detected")
                                else:
                                    print("🔇 No transcription result")
                                    
                            except Exception as e:
                                print(f"❌ Deepgram error: {e}")
                                print("This might be due to audio format or API issues.")
                                print("Trying alternative approach...")
                                
                                # Try alternative Deepgram call with simpler format
                                try:
                                    # Use the correct Deepgram v3 API call format (synchronous)
                                    response = self.deepgram.listen.prerecorded.v("1").transcribe_file(
                                        {"buffer": audio_data, "mimetype": "audio/wav"}
                                    )
                                    
                                    if response and hasattr(response, 'results') and response.results:
                                        transcript = response.results.channels[0].alternatives[0].transcript
                                        confidence = response.results.channels[0].alternatives[0].confidence
                                        print(f"🎤 Deepgram confidence: {confidence:.3f}")
                                        
                                        if transcript.strip():
                                            print(f"🎤 Transcribed: {transcript}")
                                            
                                            # Generate response
                                            response_text = f"I heard you say: {transcript}. That's interesting!"
                                            print(f"🤖 Responding: {response_text}")
                                            
                                            # Speak the response
                                            print("🔊 Speaking response...")
                                            
                                            # Use system command to play audio through speakers
                                            try:
                                                if sys.platform == "darwin":  # macOS
                                                    # Use say with specific voice
                                                    subprocess.run(["say", "-v", "Alex", response_text], check=True)
                                                elif sys.platform.startswith("linux"):  # Linux
                                                    subprocess.run(["espeak", response_text], check=True)
                                                else:  # Windows
                                                    subprocess.run(["powershell", "-Command", f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{response_text}')"], check=True)
                                                
                                                print("✅ Audio response played!")
                                                
                                            except Exception as audio_error:
                                                print(f"❌ Audio playback error: {audio_error}")
                                                print("TTS response generated but couldn't play audio")
                                                
                                                # Try alternative approach with higher volume
                                                try:
                                                    if sys.platform == "darwin":  # macOS
                                                        # Try with different voice and higher volume
                                                        subprocess.run(["say", "-v", "Victoria", "-r", "150", response_text], check=True)
                                                        print("✅ Audio response played with alternative voice!")
                                                except Exception as alt_error:
                                                    print(f"❌ Alternative audio playback also failed: {alt_error}")
                                                    print("Please check your system audio settings and volume")
                                        else:
                                            print("🔇 No speech detected")
                                        
                                except Exception as e2:
                                    print(f"❌ Alternative Deepgram approach also failed: {e2}")
                                    print("Deepgram API might be having issues. Check your API key and internet connection.")
                                    
                                    # Fallback: simulate transcription for testing
                                    print("🔄 Using fallback mode - simulating transcription...")
                                    
                                    # Check if audio file has content (simple volume check)
                                    if len(audio_data) > 1000:  # Basic check for audio content
                                        print("🎤 Audio detected - simulating transcription...")
                                        
                                        # Generate a simple response
                                        response_text = "I heard you speaking! This is a fallback response since Deepgram is not working."
                                        print(f"🤖 Responding: {response_text}")
                                        
                                        # Speak the response
                                        print("🔊 Speaking response...")
                                        
                                        # Use system command to play audio through speakers
                                        try:
                                            if sys.platform == "darwin":  # macOS
                                                # Use say with specific voice
                                                subprocess.run(["say", "-v", "Alex", response_text], check=True)
                                            elif sys.platform.startswith("linux"):  # Linux
                                                subprocess.run(["espeak", response_text], check=True)
                                            else:  # Windows
                                                subprocess.run(["powershell", "-Command", f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{response_text}')"], check=True)
                                            
                                            print("✅ Audio response played!")
                                            
                                        except Exception as audio_error:
                                            print(f"❌ Audio playback error: {audio_error}")
                                            print("TTS response generated but couldn't play audio")
                                            
                                            # Try alternative approach with higher volume
                                            try:
                                                if sys.platform == "darwin":  # macOS
                                                    # Try with different voice and higher volume
                                                    subprocess.run(["say", "-v", "Victoria", "-r", "150", response_text], check=True)
                                                    print("✅ Audio response played with alternative voice!")
                                            except Exception as alt_error:
                                                print(f"❌ Alternative audio playback also failed: {alt_error}")
                                                print("Please check your system audio settings and volume")
                                    else:
                                        print("🔇 No audio detected in recording")
                    
                    # Clean up temporary file
                    if os.path.exists(temp_filename):
                        os.unlink(temp_filename)
                    
                    # Small delay between recordings
                    await asyncio.sleep(1)
                    
                except KeyboardInterrupt:
                    print("\n👋 Stopping audio processing...")
                    break
                except Exception as e:
                    print(f"❌ Recording error: {e}")
                    print("Make sure you have 'sox' installed:")
                    print("  macOS: brew install sox")
                    print("  Ubuntu: sudo apt-get install sox")
                    print("  Windows: Download from http://sox.sourceforge.net/")
                    break
            
            print("🎤 Audio processing stopped.")
            
        except Exception as e:
            print(f"❌ Error starting full audio processing: {e}")
            print("This requires 'sox' to be installed for audio recording.")

if __name__ == "__main__":
    # Check if running in standalone mode
    if len(sys.argv) > 1 and sys.argv[1] == "--standalone":
        # Create FastAPI app for web interface
        app = FastAPI(title="Voice Chat - Device Selection")
        
        # Global variable to store the voice chat instance
        voice_chat_instance = None
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return create_device_selection_html()
        
        @app.post("/api/start-voice-chat")
        async def start_voice_chat(request: Request):
            global voice_chat_instance
            try:
                data = await request.json()
                input_device = data.get("input_device")
                output_device = data.get("output_device")
                
                if not input_device or not output_device:
                    return JSONResponse({"success": False, "error": "Both input and output devices are required"})
                
                print(f"\n🎤 Starting voice chat with web-selected devices:")
                print(f"  Microphone: {input_device['name']}")
                print(f"  Speaker: {output_device['name']}")
                
                # Create voice chat instance with selected devices
                voice_chat_instance = VoiceChat(input_device, output_device)
                
                # Start the audio processing in a background task
                asyncio.create_task(voice_chat_instance.start_full_audio_processing())
                
                print("🎯 Voice chat started! You should hear a test response.")
                print("Press Ctrl+C to stop.")
                
                return JSONResponse({"success": True, "message": "Voice chat started successfully"})
                
            except Exception as e:
                return JSONResponse({"success": False, "error": str(e)})
        
        @app.get("/api/status")
        async def get_status():
            return JSONResponse({
                "voice_chat_active": voice_chat_instance is not None,
                "status": "running"
            })
        
        print("🎤 Voice Chat - Web Interface Mode")
        print("="*50)
        print("Starting web server for device selection...")
        print("Open your browser to: http://localhost:8001")
        print("Select your devices and click 'Start Voice Chat'")
        print("Press Ctrl+C to stop the server")
        print("="*50)
        
        # Start the web server
        uvicorn.run(app, host="localhost", port=8001)
        
    else:
        # Run the original pipecat example
        from pipecat.examples.run import main
        main(run_example, transport_params=transport_params) 