from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import asyncio
import os
import signal
import sys
from voice_chat import VoiceChat

app = FastAPI(title="Voice Chat with Device Routing")

# Get the directory where server.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=static_dir)

# Store active voice chat sessions
active_sessions = {}

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    print("\n🛑 Shutting down server gracefully...")
    print("Closing active sessions...")
    for session_id, session in active_sessions.items():
        try:
            asyncio.create_task(session.close())
        except:
            pass
    print("✅ Server shutdown complete")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/offer")
async def handle_offer(request: Request):
    data = await request.json()
    sdp = data.get("sdp")
    input_device_id = data.get("input_device_id")
    output_device_id = data.get("output_device_id")
    
    if not sdp:
        return JSONResponse({"error": "No SDP provided"}, status_code=400)
    
    try:
        print(f"🎤 New WebRTC connection request:")
        print(f"   Input device: {input_device_id or 'Default'}")
        print(f"   Output device: {output_device_id or 'Default'}")
        
        # Create a new voice chat session
        voice_chat = VoiceChat()
        active_sessions[id(voice_chat)] = voice_chat
        
        # Handle the WebRTC offer with device preferences
        answer = await voice_chat.handle_offer(sdp, input_device_id, output_device_id)
        
        print(f"✅ WebRTC connection established successfully")
        return JSONResponse(answer)
    except Exception as e:
        print(f"❌ Error handling offer: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/status")
async def get_status():
    return JSONResponse({
        "active_sessions": len(active_sessions),
        "status": "running"
    })

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 FastAPI shutdown event triggered")
    print("Closing active sessions...")
    for session_id, session in active_sessions.items():
        try:
            await session.close()
        except:
            pass
    print("✅ All sessions closed")

if __name__ == "__main__":
    print("🎤 Voice Chat Server Starting...")
    print("="*50)
    print("Features:")
    print("  ✅ WebRTC audio streaming")
    print("  ✅ Device selection and routing")
    print("  ✅ VU meters for input/output")
    print("  ✅ Deepgram speech-to-text")
    print("  ✅ Cartesia text-to-speech")
    print("="*50)
    print("Open your browser to: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    uvicorn.run(app, host="localhost", port=8000) 