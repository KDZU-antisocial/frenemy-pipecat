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
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay
from typing import Optional

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
    def __init__(self):
        # Initialize Deepgram
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
        self.deepgram = DeepgramClient(api_key=self.deepgram_api_key)

        # Initialize Cartesia
        self.cartesia_api_key = os.getenv('CARTESIA_API_KEY')
        if not self.cartesia_api_key:
            raise ValueError("CARTESIA_API_KEY environment variable is not set")
        cartesia.api_key = self.cartesia_api_key

        self.pc: Optional[RTCPeerConnection] = None
        self.relay = MediaRelay()

    async def handle_offer(self, sdp):
        # Create peer connection with proper configuration
        self.pc = RTCPeerConnection()
        
        # Set up audio tracks
        @self.pc.on("track")
        async def on_track(track):
            if track.kind == "audio":
                print(f"Received audio track: {track.id}")
                # Process incoming audio with Deepgram
                async def process_audio():
                    while True:
                        try:
                            frame = await track.recv()
                            # Convert frame to bytes for Deepgram
                            audio_data = frame.to_ndarray().tobytes()
                            
                            # Transcribe audio using Deepgram
                            response = await self.deepgram.listen.prerecorded.v("1").transcribe_file(
                                {"buffer": audio_data, "mimetype": "audio/wav"},
                                {"punctuate": True, "language": "en"}
                            )
                            
                            if response and 'results' in response:
                                transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
                                if transcript.strip():
                                    # Generate response (simple echo for now)
                                    response_text = f"I heard you say: {transcript}"
                                    print(f"Transcription: {transcript}")
                                    
                                    # Convert response to speech using Cartesia
                                    audio_response = cartesia.text_to_speech(response_text)
                                    
                                    # Create audio track from response
                                    audio_track = MediaPlayer(audio_response)
                                    if self.pc:
                                        self.pc.addTrack(audio_track.audio)
                        except Exception as e:
                            print(f"Error processing audio: {e}")
                            break
                
                asyncio.create_task(process_audio())

        # Set the remote description
        print(f"Received SDP: {sdp}")
        if isinstance(sdp, dict):
            offer = RTCSessionDescription(sdp=sdp["sdp"], type=sdp["type"])
        else:
            # If sdp is a string, assume it's the SDP content
            offer = RTCSessionDescription(sdp=sdp, type="offer")
            
        await self.pc.setRemoteDescription(offer)

        # Create answer
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        return {
            "sdp": self.pc.localDescription.sdp,
            "type": self.pc.localDescription.type
        }

    async def close(self):
        if self.pc:
            await self.pc.close()

if __name__ == "__main__":
    from pipecat.examples.run import main
    main(run_example, transport_params=transport_params) 