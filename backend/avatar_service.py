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
import re
from typing import Protocol, Optional
from PIL import Image

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, WorkerType, cli, ChatContext
from livekit.plugins import hedra, openai
from openai.types.beta.realtime.session import TurnDetection

# Import your AI chatbot (easily replaceable)
from ai_chatbot import TrilogyAIChatbot

logger = logging.getLogger("avatar-service")
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
        self.wake_word = os.getenv("WAKE_WORD", "wake up")
        self.sleep_word = os.getenv("SLEEP_WORD", "stop talking")
        self.speaking_state = 'agentic'  # 'silent', 'agentic'

    async def start_session(self, ctx: JobContext):
        """Start avatar session with plugged-in AI chatbot"""

        # Get AI chatbot settings
        voice_settings = self.ai_chatbot.get_voice_settings()

        self.session = AgentSession(
            llm=openai.realtime.RealtimeModel(
                voice=voice_settings.get("voice", "ash"),
                speed=voice_settings.get("speed", 1),
                turn_detection=TurnDetection(
                    type="semantic_vad",
                    eagerness="low",
                    create_response=True,
                    interrupt_response=True,
                )
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

        # async def on_user_turn_completed(self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage):
        #     logger.info(f"User turn completed: {new_message.content}")
        #     await self.react_to_message(new_message.content)

        # augmented_agent = Agent(
        #     chat_ctx=initial_ctx,
        #     instructions="ENGLISH ONLY: You are an avatar service loading an AI chatbot. Be brief. Always respond in English, never in Spanish or other languages.",
        # )

        # augmented_agent.on_user_turn_completed = on_user_turn_completed

        await self.session.start(
            agent=Agent(
                chat_ctx=initial_ctx,
                instructions="ENGLISH ONLY: You are an avatar service loading an AI chatbot. Be brief. Always respond in English, never in Spanish or other languages."
            ),
            room=ctx.room,
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

            # Start the monitor agent task
            asyncio.create_task(self.monitor_agent())

            # Announce readiness with AI chatbot's greeting
            self.session.generate_reply(
                instructions=f"Say in English: '{greeting_message}'")
        except Exception as e:
            logger.error(f"Failed to initialize AI chatbot: {e}")
            self.session.generate_reply(
                instructions="Say in English: 'AI chatbot initialization failed. Please try again later.'"
            )

            # Start the interrupt loop
        # asyncio.create_task(self.interrupt_loop())

    def pause_session(self):
        """Pause the avatar session"""
        self.session.interrupt()

    def get_last_user_message(self):
        try:
            messages = self.session.history.items
            if not messages:
                return None

            # find the last message with role "user"
            last_user_message = next(
                (m for m in reversed(messages) if m.role == 'user'), None)

            if not last_user_message or not last_user_message.content:
                return None
            message_content = last_user_message.content[-1]

            return message_content
        except Exception as e:
            logger.error(f"Error in get_last_user_message: {e}")
            return None

    async def monitor_agent(self):
        try:
            while True:
                await asyncio.sleep(0.5)

                message_content = self.get_last_user_message()
                if not message_content:
                    continue

                self.update_speaking_state_if_necessary(message_content)
        except Exception as e:
            logger.error(f"Error in monitor_agent: {e}")

    def set_speaking_state(self, state: str):
        self.speaking_state = state

    def is_silent(self) -> bool:
        return self.speaking_state == 'silent'

    def match_word(self, message: str, word: str, min_partial: int = 3) -> bool:
        """
        Returns True if `message` contains the full word or any
        substring of it of length >= min_partial, treating commas (and other
        punctuation/whitespace) as word-boundaries.
        """
        # 1) Escape any regex-special chars in the wake‐word
        esc = re.escape(word)

        # 2) Build all contiguous substrings of `word` of length >= min_partial
        if len(word) >= min_partial:
            subs = [esc[i:i+min_partial]
                    for i in range(len(esc) - min_partial + 1)]
        else:
            subs = []

        # 3) Combine into one regex: full word OR any of the substrings
        #    and require “boundary” = start, end, whitespace or comma/punct
        boundary = r'(?:^|[\s,.;:!?])'
        body = r'(?:' + esc + ('' if not subs else '|' + '|'.join(subs)) + r')'
        pattern = boundary + body + boundary

        # 4) Search case-insensitively
        return re.search(pattern, message, re.IGNORECASE) is not None

    def update_speaking_state_if_necessary(self, message: str) -> None:
        state = self.session.agent_state
        if state not in ["speaking", "thinking"]:
            return

        # check if the message is a wake word
        if self.match_word(message, self.wake_word) and self.is_silent():
            logger.info(f"Setting speaking state to agentic")
            self.set_speaking_state('agentic')

        # check if the message is a sleep word
        elif self.match_word(message, self.sleep_word):
            self.set_speaking_state('silent')
            self.pause_session()
            logger.info(f"Setting speaking state to silent")

        if self.is_silent():
            self.pause_session()


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
