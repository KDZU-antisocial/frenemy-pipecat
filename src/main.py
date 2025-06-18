import os
from dotenv import load_dotenv
import pipecat
from deepgram import DeepgramClient
import openai
import cartesia

# Load environment variables
load_dotenv()

# Get API keys
deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
if not deepgram_api_key:
    raise ValueError("DEEPGRAM_API_KEY environment variable is not set")

# Initialize services
deepgram = DeepgramClient(deepgram_api_key)
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    print("Frenemy Pipecat Project initialized!")
    print("Services configured:")
    print("- WebRTC (via aiortc)")
    print("- Deepgram")
    print("- OpenAI")
    print("- Cartesia")

if __name__ == "__main__":
    main() 