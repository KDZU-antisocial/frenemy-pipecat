#!/usr/bin/env python3
"""
Bicycle Assembly Guide - Custom Pipecat Pipeline Step
Manages conversation state and guides users through bicycle assembly steps.
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AssemblyStep(Enum):
    """Enumeration of bicycle assembly steps"""
    WELCOME = "welcome"
    UNPACK_BOX = "unpack_box"
    ATTACH_WHEELS = "attach_wheels"
    ATTACH_HANDLEBARS = "attach_handlebars"
    ATTACH_SEAT = "attach_seat"
    ATTACH_PEDALS = "attach_pedals"
    TEST_RIDE = "test_ride"
    COMPLETE = "complete"

@dataclass
class AssemblyState:
    """State management for bicycle assembly"""
    current_step: AssemblyStep = AssemblyStep.WELCOME
    step_completed: bool = False
    user_confirmed: bool = False
    step_attempts: int = 0
    total_steps: int = len(AssemblyStep) - 1  # Exclude WELCOME and COMPLETE
    
    def next_step(self):
        """Move to the next assembly step"""
        if self.current_step == AssemblyStep.WELCOME:
            self.current_step = AssemblyStep.UNPACK_BOX
        elif self.current_step == AssemblyStep.UNPACK_BOX:
            self.current_step = AssemblyStep.ATTACH_WHEELS
        elif self.current_step == AssemblyStep.ATTACH_WHEELS:
            self.current_step = AssemblyStep.ATTACH_HANDLEBARS
        elif self.current_step == AssemblyStep.ATTACH_HANDLEBARS:
            self.current_step = AssemblyStep.ATTACH_SEAT
        elif self.current_step == AssemblyStep.ATTACH_SEAT:
            self.current_step = AssemblyStep.ATTACH_PEDALS
        elif self.current_step == AssemblyStep.ATTACH_PEDALS:
            self.current_step = AssemblyStep.TEST_RIDE
        elif self.current_step == AssemblyStep.TEST_RIDE:
            self.current_step = AssemblyStep.COMPLETE
        
        self.step_completed = False
        self.user_confirmed = False
        self.step_attempts = 0

class BicycleAssemblyGuide:
    """Custom Pipecat pipeline step for bicycle assembly guidance"""
    
    def __init__(self):
        self.state = AssemblyState()
        self.step_instructions = {
            AssemblyStep.WELCOME: {
                "message": "Welcome to your bicycle assembly guide! I'll walk you through each step safely and clearly. Are you ready to begin?",
                "keywords": ["ready", "yes", "start", "begin", "okay", "sure"],
                "next_prompt": "Great! Let's start by unpacking your bicycle box."
            },
            AssemblyStep.UNPACK_BOX: {
                "message": "Step 1: Unpacking the Box\n\nFirst, carefully open the bicycle box and remove all contents. You should find:\n- The bicycle frame\n- Two wheels\n- Handlebars\n- Seat and seat post\n- Pedals\n- Assembly tools\n- Instruction manual\n\nPlease confirm when you've unpacked everything and can see all these parts.",
                "keywords": ["unpacked", "done", "finished", "complete", "ready", "yes"],
                "next_prompt": "Perfect! Now let's attach the wheels."
            },
            AssemblyStep.ATTACH_WHEELS: {
                "message": "Step 2: Attaching the Wheels\n\n1. Locate the front wheel and the front fork\n2. Insert the wheel axle into the fork dropouts\n3. Make sure the wheel is centered\n4. Tighten the quick-release lever or nuts securely\n5. Spin the wheel to ensure it rotates freely\n\nRepeat for the rear wheel. Let me know when both wheels are attached and spinning freely.",
                "keywords": ["wheels", "attached", "done", "finished", "complete", "ready"],
                "next_prompt": "Excellent! Now let's attach the handlebars."
            },
            AssemblyStep.ATTACH_HANDLEBARS: {
                "message": "Step 3: Attaching the Handlebars\n\n1. Loosen the stem bolts on the handlebar stem\n2. Insert the handlebars into the stem\n3. Center the handlebars\n4. Tighten the stem bolts evenly and securely\n5. Make sure the handlebars don't move when you apply pressure\n\nConfirm when the handlebars are securely attached.",
                "keywords": ["handlebars", "attached", "done", "finished", "complete", "ready"],
                "next_prompt": "Great! Now let's attach the seat."
            },
            AssemblyStep.ATTACH_SEAT: {
                "message": "Step 4: Attaching the Seat\n\n1. Insert the seat post into the seat tube\n2. Adjust the seat height to a comfortable position\n3. Make sure the seat is level\n4. Tighten the seat clamp securely\n5. Test that the seat doesn't move when you apply pressure\n\nLet me know when the seat is properly attached and adjusted.",
                "keywords": ["seat", "attached", "done", "finished", "complete", "ready"],
                "next_prompt": "Perfect! Now let's attach the pedals."
            },
            AssemblyStep.ATTACH_PEDALS: {
                "message": "Step 5: Attaching the Pedals\n\nIMPORTANT: Pedals are threaded differently!\n\n1. The right pedal has right-hand threads (clockwise to tighten)\n2. The left pedal has left-hand threads (counter-clockwise to tighten)\n3. Apply a small amount of grease to the pedal threads\n4. Screw in the pedals by hand first\n5. Use a pedal wrench to tighten securely\n\nConfirm when both pedals are properly attached.",
                "keywords": ["pedals", "attached", "done", "finished", "complete", "ready"],
                "next_prompt": "Excellent! Now let's do a final safety check and test ride."
            },
            AssemblyStep.TEST_RIDE: {
                "message": "Step 6: Final Safety Check and Test Ride\n\nBefore your first ride, let's do a safety check:\n\n1. Check that all bolts are tight\n2. Ensure wheels spin freely without wobbling\n3. Test the brakes - they should stop the bike smoothly\n4. Make sure the handlebars are secure and straight\n5. Verify the seat is at the right height and secure\n\nTake a short test ride in a safe area. Let me know when you're ready to go!",
                "keywords": ["ready", "done", "finished", "complete", "tested", "safe"],
                "next_prompt": "Congratulations! Your bicycle is assembled and ready to ride."
            },
            AssemblyStep.COMPLETE: {
                "message": "🎉 Congratulations! You've successfully assembled your bicycle!\n\nYour bike is now ready for safe riding. Remember to:\n- Wear a helmet\n- Follow traffic laws\n- Perform regular maintenance\n- Have fun!\n\nIs there anything else you'd like to know about your bicycle?",
                "keywords": ["thanks", "thank you", "goodbye", "bye", "done"],
                "next_prompt": "Happy riding!"
            }
        }
    
    async def process(self, message: str) -> str:
        """Process user input and return appropriate response"""
        message_lower = message.lower().strip()
        
        # Check for help or restart commands
        if any(word in message_lower for word in ["help", "restart", "start over", "begin again"]):
            self.state = AssemblyState()
            return self.step_instructions[AssemblyStep.WELCOME]["message"]
        
        # Check for step confirmation
        current_instruction = self.step_instructions[self.state.current_step]
        keywords = current_instruction["keywords"]
        
        if any(keyword in message_lower for keyword in keywords):
            # User confirmed current step
            self.state.step_completed = True
            self.state.user_confirmed = True
            
            if self.state.current_step == AssemblyStep.COMPLETE:
                return "Thank you for using the bicycle assembly guide! Happy riding! 🚴‍♂️"
            else:
                # Move to next step
                self.state.next_step()
                next_instruction = self.step_instructions[self.state.current_step]
                return next_instruction["message"]
        
        # Check for specific questions or issues
        if any(word in message_lower for word in ["problem", "issue", "stuck", "difficult", "hard"]):
            return self._get_help_for_current_step()
        
        if any(word in message_lower for word in ["what", "how", "where", "when"]):
            return self._get_detailed_help_for_current_step()
        
        # Default response - repeat current step with encouragement
        self.state.step_attempts += 1
        if self.state.step_attempts > 2:
            return f"I understand this step might be challenging. Let me break it down further:\n\n{self._get_detailed_help_for_current_step()}"
        else:
            return f"Let me know when you've completed the current step. You can say 'done', 'finished', or 'ready' when you're ready to move on."
    
    def _get_help_for_current_step(self) -> str:
        """Get help for the current step"""
        step_help = {
            AssemblyStep.UNPACK_BOX: "Make sure you have a clean, well-lit workspace. Take your time to carefully remove all parts and lay them out so you can see everything clearly.",
            AssemblyStep.ATTACH_WHEELS: "If the wheel doesn't fit easily, don't force it. Check that you're using the correct wheel for front/rear. The front wheel usually has a smaller axle.",
            AssemblyStep.ATTACH_HANDLEBARS: "If the handlebars feel loose, make sure all stem bolts are tightened evenly. Don't overtighten - just enough to prevent movement.",
            AssemblyStep.ATTACH_SEAT: "The seat height should allow your leg to be almost straight when the pedal is at the bottom. You should be able to touch the ground with your toes.",
            AssemblyStep.ATTACH_PEDALS: "Remember: right pedal tightens clockwise, left pedal tightens counter-clockwise. If it feels wrong, you might have the pedals switched.",
            AssemblyStep.TEST_RIDE: "Start in a safe, flat area. Test the brakes before going fast. If anything feels loose or wrong, stop and check it before continuing."
        }
        return step_help.get(self.state.current_step, "Take your time and follow the instructions carefully. If you're unsure, you can ask me to explain any part in more detail.")
    
    def _get_detailed_help_for_current_step(self) -> str:
        """Get detailed help for the current step"""
        current_instruction = self.step_instructions[self.state.current_step]
        return f"Here's the current step again:\n\n{current_instruction['message']}\n\nLet me know when you're ready to proceed or if you need more specific help with any part of this step."

# Example usage in a Pipecat pipeline
async def example_pipeline():
    """Example of how to use the BicycleAssemblyGuide in a Pipecat pipeline"""
    
    # Initialize the guide
    guide = BicycleAssemblyGuide()
    
    # Simulate conversation
    print("🤖 Bicycle Assembly Guide")
    print("=" * 50)
    
    # Start with welcome message
    response = guide.step_instructions[AssemblyStep.WELCOME]["message"]
    print(f"🤖: {response}")
    
    # Simulate user responses
    user_responses = [
        "yes, I'm ready",
        "I've unpacked everything",
        "both wheels are attached",
        "handlebars are secure",
        "seat is attached and adjusted",
        "pedals are on",
        "everything looks good, ready to test"
    ]
    
    for user_input in user_responses:
        print(f"\n👤: {user_input}")
        response = await guide.process(user_input)
        print(f"🤖: {response}")
        await asyncio.sleep(1)  # Simulate processing time

if __name__ == "__main__":
    asyncio.run(example_pipeline()) 