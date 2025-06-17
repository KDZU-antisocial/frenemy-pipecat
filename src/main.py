import os
from dotenv import load_dotenv
import pipecat
from deepgram import Deepgram
import openai
import cartesia

# Load environment variables
load_dotenv()

# Initialize services
deepgram = Deepgram(os.getenv("DEEPGRAM_API_KEY"))
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