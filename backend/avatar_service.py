"""
Generic Avatar Service - Hedra Video Avatar with LiveKit Integration

This service provides a generic avatar interface that can work with ANY AI chatbot.
The AI chatbot just needs to implement the simple interface in ai_chatbot.py

Architecture:
- Avatar Service: Handles video avatar, voice synthesis, LiveKit sessions
- AI Chatbot: Pluggable text-to-text AI (implement AIChatbot interface)
- Communication: Simple text input → text output between services

Usage:
1. Implement your AI chatbot using the AIChatbot interface
2. Pass your chatbot instance to AvatarService
3. Run with: python avatar_service.py start
"""

import logging
import os
import asyncio
from typing import Protocol, Optional
from PIL import Image

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, WorkerType, cli, ChatContext
from livekit.plugins import hedra, openai

# Import your AI chatbot (easily replaceable)
from ai_chatbot import TrilogyAIChatbot

logger = logging.getLogger("avatar-service")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

# ==============================================================================
# AI CHATBOT INTERFACE (Protocol)
# ==============================================================================

class AIChatbot(Protocol):
    """
    Interface that any AI chatbot must implement to work with the avatar service.
    
    This allows easy plugging of different AI systems:
    - OpenAI GPT chatbots
    - Claude chatbots  
    - Local LLMs
    - Custom AI systems
    - Enterprise chatbots
    """
    
    async def initialize(self) -> str:
        """
        Initialize the AI chatbot and return a greeting message.
        
        Returns:
            str: Initial greeting message to be spoken by avatar
        """
        ...
    
    async def get_response(self, user_message: str) -> str:
        """
        Get AI response to user message.
        
        Args:
            user_message: Text input from user (converted from speech)
            
        Returns:
            str: AI response text (will be converted to avatar speech)
        """
        ...
    
    def get_voice_settings(self) -> dict:
        """
        Get voice and avatar settings for this AI chatbot.
        
        Returns:
            dict: Voice settings with keys: voice, speed, avatar_image
        """
        ...

# ==============================================================================
# GENERIC AVATAR SERVICE
# ==============================================================================

class AvatarService:
    """
    Generic avatar service that can work with any AI chatbot implementing AIChatbot interface.
    
    Responsibilities:
    - Manage Hedra avatar sessions
    - Handle LiveKit room connections
    - Convert speech to text (for AI input)
    - Convert AI text responses to avatar speech
    - Provide user feedback during loading
    """
    
    def __init__(self, ai_chatbot: AIChatbot):
        self.ai_chatbot = ai_chatbot
        self.session: Optional[AgentSession] = None
        
    async def start_session(self, ctx: JobContext):
        """Start avatar session with plugged-in AI chatbot"""
        
        # Get AI chatbot settings
        voice_settings = self.ai_chatbot.get_voice_settings()
        
        # Initialize session with AI chatbot's voice preferences
        self.session = AgentSession(
            llm=openai.realtime.RealtimeModel(
                voice=voice_settings.get("voice", "ash"),
                speed=voice_settings.get("speed", 1.2),
            ),
        )

        # Load avatar image
        avatar_image_path = os.path.join(
            os.path.dirname(__file__), 
            voice_settings.get("avatar_image", "assets/stan.png")
        )
        logger.info(f"Loading avatar image: {avatar_image_path}")
        
        avatar_image = Image.open(avatar_image_path)
        if avatar_image.mode == 'RGBA':
            avatar_image = avatar_image.convert('RGB')

        # Start Hedra avatar
        hedra_avatar = hedra.AvatarSession(avatar_image=avatar_image)
        await hedra_avatar.start(self.session, room=ctx.room)

        # Start with basic agent for immediate response
        initial_ctx = ChatContext()
        initial_ctx.add_message(
            role="system",
            content="Avatar service initializing. Please wait while I load the AI chatbot. RESPOND ONLY IN ENGLISH."
        )
        
        await self.session.start(
            agent=Agent(
                chat_ctx=initial_ctx,
                instructions="ENGLISH ONLY: You are an avatar service loading an AI chatbot. Be brief. Always respond in English, never in Spanish or other languages."
            ),
            room=ctx.room,
        )

        # Give session time to start
        await asyncio.sleep(1)
        
        # Initialize AI chatbot and get greeting
        logger.info("Initializing AI chatbot...")
        self.session.generate_reply(
            instructions="Say in English: 'Initializing AI system, please wait...'"
        )
        
        try:
            greeting_message = await self.ai_chatbot.initialize()
            logger.info("AI chatbot initialized successfully")
            
            # Update agent to use AI responses
            enhanced_ctx = ChatContext()
            enhanced_ctx.add_message(
                role="system", 
                content="Avatar service ready. AI chatbot loaded successfully. ALWAYS RESPOND IN ENGLISH ONLY."
            )
            
            # Get the full optimized instructions from the AI chatbot (like original agent_worker.py)
            full_instructions = self.ai_chatbot.get_full_instructions()
            
            # Create agent with the comprehensive instructions (same as original system)
            self.session.update_agent(
                agent=Agent(
                    chat_ctx=enhanced_ctx,
                    instructions=full_instructions
                )
            )
            
            # Announce readiness with AI chatbot's greeting
            self.session.generate_reply(
                instructions=f"Say in English: '{greeting_message}'"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize AI chatbot: {e}")
            self.session.generate_reply(
                instructions="Say in English: 'AI chatbot initialization failed. Please try again later.'"
            )

    def _create_avatar_instructions(self) -> str:
        """Create instructions for the avatar agent to forward messages to AI chatbot"""
        return """ENGLISH ONLY: Always respond in English language only. Never use Spanish or other languages.

You are an avatar service that forwards user messages to an AI chatbot.

CRITICAL: You do NOT generate responses yourself. Instead:
1. Take the user's message
2. Forward it to the AI chatbot system  
3. Speak the AI chatbot's exact response in English only
4. Never add your own commentary or modifications
5. MANDATORY: All speech must be in English language

The AI chatbot handles all intelligence, context, and response generation.
You only handle the voice/video presentation of those responses.
REMINDER: Always speak in English, never in Spanish or other languages."""

# ==============================================================================
# PREWARM AND ENTRY POINT
# ==============================================================================

def prewarm(ctx: JobContext):
    """Prewarm function for LiveKit worker"""
    logger.info("Avatar service prewarming...")
    # Any avatar-specific prewarming can go here
    logger.info("Avatar service prewarm complete")

async def entrypoint(ctx: JobContext):
    """Main entry point - creates avatar service with plugged-in AI chatbot"""
    
    # Create AI chatbot instance (easily replaceable)
    ai_chatbot = TrilogyAIChatbot()
    
    # Create avatar service with the AI chatbot
    avatar_service = AvatarService(ai_chatbot)
    
    # Start the avatar session
    await avatar_service.start_session(ctx)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        worker_type=WorkerType.ROOM
    ))