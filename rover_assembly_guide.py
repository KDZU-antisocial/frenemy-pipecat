#!/usr/bin/env python3
"""
Rover Assembly Guide - Custom Pipecat Pipeline Step
Manages conversation state and guides users through rover assembly steps.
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re

class RoverAssemblyStep(Enum):
    """Enumeration of rover assembly steps"""
    WELCOME = "welcome"
    UNPACKING = "unpacking"
    FRAME_SETUP = "frame_setup"
    WHEELS = "wheels"
    ELECTRONICS = "electronics"
    BATTERY = "battery"
    TESTING = "testing"
    COMPLETE = "complete"

@dataclass
class AssemblyState:
    """State management for rover assembly"""
    current_step: RoverAssemblyStep = RoverAssemblyStep.WELCOME
    step_completed: bool = False
    user_confirmed: bool = False
    step_attempts: int = 0
    total_steps: int = len(RoverAssemblyStep) - 1  # Exclude WELCOME and COMPLETE
    step_data: Dict[str, Any] = field(default_factory=dict)
    user_name: Optional[str] = None
    assembly_started: bool = False
    
    def next_step(self):
        """Move to the next assembly step"""
        if self.current_step == RoverAssemblyStep.WELCOME:
            self.current_step = RoverAssemblyStep.UNPACKING
        elif self.current_step == RoverAssemblyStep.UNPACKING:
            self.current_step = RoverAssemblyStep.FRAME_SETUP
        elif self.current_step == RoverAssemblyStep.FRAME_SETUP:
            self.current_step = RoverAssemblyStep.WHEELS
        elif self.current_step == RoverAssemblyStep.WHEELS:
            self.current_step = RoverAssemblyStep.ELECTRONICS
        elif self.current_step == RoverAssemblyStep.ELECTRONICS:
            self.current_step = RoverAssemblyStep.BATTERY
        elif self.current_step == RoverAssemblyStep.BATTERY:
            self.current_step = RoverAssemblyStep.TESTING
        elif self.current_step == RoverAssemblyStep.TESTING:
            self.current_step = RoverAssemblyStep.COMPLETE
        
        self.step_completed = False
        self.user_confirmed = False
        self.step_attempts = 0

    def advance_step(self):
        """Move to the next assembly step"""
        step_order = [
            RoverAssemblyStep.WELCOME,
            RoverAssemblyStep.UNPACKING,
            RoverAssemblyStep.FRAME_SETUP,
            RoverAssemblyStep.WHEELS,
            RoverAssemblyStep.ELECTRONICS,
            RoverAssemblyStep.BATTERY,
            RoverAssemblyStep.TESTING,
            RoverAssemblyStep.COMPLETE
        ]
        
        current_index = step_order.index(self.current_step)
        if current_index < len(step_order) - 1:
            self.current_step = step_order[current_index + 1]
            return True
        return False
    
    def reset(self):
        """Reset to the beginning"""
        self.current_step = RoverAssemblyStep.WELCOME
        self.step_data = {}
        self.assembly_started = False

class RoverAssemblyGuide:
    """Custom Pipecat pipeline step for rover assembly guidance"""
    
    def __init__(self):
        self.state = AssemblyState()
        self.step_content = {
            RoverAssemblyStep.WELCOME: {
                "message": "Welcome to your rover assembly guide! I'll walk you through each step safely and clearly. Are you ready to begin?",
                "keywords": ["ready", "start", "begin", "yes", "okay"],
                "next_prompt": "Great! Let's start by unpacking your rover kit."
            },
            RoverAssemblyStep.UNPACKING: {
                "message": "Step 1: Unpacking the Kit\n\nFirst, carefully open the rover kit box and remove all contents. You should find:\n- The rover chassis and frame\n- Four wheels with motors\n- Electronic control board\n- Battery pack and charger\n- Remote control\n- Assembly tools\n- Instruction manual\n\nPlease confirm when you've unpacked everything and can see all these parts.",
                "keywords": ["done", "finished", "complete", "ready", "next"],
                "next_prompt": "Excellent! Now let's set up the rover frame."
            },
            RoverAssemblyStep.FRAME_SETUP: {
                "message": "Step 2: Frame Assembly\n\nLet's start with the rover chassis:\n1. Place the main chassis on a flat surface\n2. Attach the front and rear suspension arms\n3. Secure the motor mounts to the frame\n4. Check that all screws are tight\n\nTake your time and let me know when this step is complete.",
                "keywords": ["done", "finished", "complete", "ready", "next"],
                "next_prompt": "Perfect! Now let's install the wheels."
            },
            RoverAssemblyStep.WHEELS: {
                "message": "Step 3: Wheel Installation\n\nNow we'll install the wheels:\n1. Attach the wheel hubs to the motor shafts\n2. Secure the wheels to the hubs\n3. Make sure all wheels spin freely\n4. Check that the wheel alignment is straight\n\nLet me know when the wheels are properly installed.",
                "keywords": ["done", "finished", "complete", "ready", "next"],
                "next_prompt": "Great! Now let's install the electronics."
            },
            RoverAssemblyStep.ELECTRONICS: {
                "message": "Step 4: Electronics Installation\n\nTime to install the control system:\n1. Mount the electronic control board to the chassis\n2. Connect the motor wires to the control board\n3. Install the remote control receiver\n4. Secure all wiring with cable ties\n\nTake care with the electronics and let me know when ready.",
                "keywords": ["done", "finished", "complete", "ready", "next"],
                "next_prompt": "Excellent! Now let's install the battery."
            },
            RoverAssemblyStep.BATTERY: {
                "message": "Step 5: Battery Installation\n\nLet's power up your rover:\n1. Connect the battery pack to the control board\n2. Secure the battery in its compartment\n3. Make sure the power switch is off\n4. Double-check all connections are secure\n\nSafety first! Let me know when the battery is installed.",
                "keywords": ["done", "finished", "complete", "ready", "next"],
                "next_prompt": "Perfect! Now let's test everything."
            },
            RoverAssemblyStep.TESTING: {
                "message": "Step 6: Testing and Calibration\n\nTime to test your rover:\n1. Turn on the power switch\n2. Test the remote control functions\n3. Check that all wheels respond to commands\n4. Test forward, backward, and turning\n5. Calibrate the steering if needed\n\nLet me know how the testing goes!",
                "keywords": ["done", "finished", "complete", "ready", "next", "working", "good"],
                "next_prompt": "Congratulations! Your rover is assembled and ready to explore."
            },
            RoverAssemblyStep.COMPLETE: {
                "message": "🎉 Congratulations! You've successfully assembled your rover!\n\nYour rover is now ready for exploration. Remember to:\n- Charge the battery before first use\n- Test in a safe, open area\n- Follow all safety guidelines\n- Have fun exploring!\n\nIs there anything else you'd like to know about your rover?",
                "keywords": ["help", "restart", "quit", "thanks", "goodbye"],
                "next_prompt": "Thank you for using the rover assembly guide! Happy exploring! 🚗"
            }
        }
    
    async def process(self, message: str) -> str:
        """Process user input and return appropriate response"""
        message = message.lower().strip()
        
        # Handle special commands
        if any(word in message for word in ["quit", "exit", "stop", "bye"]):
            return "Thank you for using the rover assembly guide! Happy exploring! 🚗"
        
        if any(word in message for word in ["help", "what", "how"]):
            return self._get_help_message()
        
        if any(word in message for word in ["restart", "reset", "start over"]):
            self.state.reset()
            return self.step_content[RoverAssemblyStep.WELCOME]["message"]
        
        # Check for step completion keywords
        current_content = self.step_content[self.state.current_step]
        if any(keyword in message for keyword in current_content["keywords"]):
            if self.state.next_step():
                return current_content["next_prompt"] + "\n\n" + self.step_content[self.state.current_step]["message"]
            else:
                return current_content["message"]
        
        # If no keywords matched, provide guidance
        return f"I didn't quite catch that. {current_content['next_prompt']}"
    
    def _get_help_message(self) -> str:
        """Get help message based on current step"""
        step_help = {
            RoverAssemblyStep.WELCOME: "Just say 'ready' or 'start' to begin the assembly!",
            RoverAssemblyStep.UNPACKING: "Make sure you have all the parts listed. Say 'done' when you're ready to continue.",
            RoverAssemblyStep.FRAME_SETUP: "Take your time with the frame assembly. Say 'done' when the frame is complete.",
            RoverAssemblyStep.WHEELS: "Ensure all wheels are properly attached and spin freely. Say 'done' when ready.",
            RoverAssemblyStep.ELECTRONICS: "Be careful with the electronics. Double-check all connections. Say 'done' when complete.",
            RoverAssemblyStep.BATTERY: "Safety first! Make sure the power is off during installation. Say 'done' when ready.",
            RoverAssemblyStep.TESTING: "Test all functions carefully. Say 'done' when testing is complete.",
            RoverAssemblyStep.COMPLETE: "Your rover is ready! You can say 'restart' to begin again or 'quit' to exit."
        }
        return step_help.get(self.state.current_step, "Say 'done' when you're ready to continue to the next step.")

# Example usage in a Pipecat pipeline
async def example_pipeline():
    """Example of how to use the RoverAssemblyGuide in a Pipecat pipeline"""
    
    # Initialize the guide
    guide = RoverAssemblyGuide()
    
    # Simulate conversation
    print("🤖 Rover Assembly Guide")
    print("=" * 50)
    
    # Start with welcome message
    response = guide.step_content[RoverAssemblyStep.WELCOME]["message"]
    print(f"🤖: {response}")
    
    # Simulate user responses
    user_responses = [
        "yes, I'm ready",
        "I've unpacked everything",
        "frame is complete",
        "wheels are installed",
        "electronics are installed",
        "battery is installed",
        "everything looks good, ready to test"
    ]
    
    for user_input in user_responses:
        print(f"\n👤: {user_input}")
        response = await guide.process(user_input)
        print(f"🤖: {response}")
        await asyncio.sleep(1)  # Simulate processing time

if __name__ == "__main__":
    asyncio.run(example_pipeline()) 