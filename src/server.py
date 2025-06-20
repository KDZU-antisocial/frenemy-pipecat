from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import asyncio
from voice_chat import VoiceChat

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/static")

# Store active voice chat sessions
active_sessions = {}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/offer")
async def handle_offer(request: Request):
    data = await request.json()
    sdp = data.get("sdp")
    
    if not sdp:
        return JSONResponse({"error": "No SDP provided"}, status_code=400)
    
    try:
        # Create a new voice chat session
        voice_chat = VoiceChat()
        active_sessions[id(voice_chat)] = voice_chat
        
        # Handle the WebRTC offer
        answer = await voice_chat.handle_offer(sdp)
        
        return JSONResponse(answer)
    except Exception as e:
        print(f"Error handling offer: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000) 