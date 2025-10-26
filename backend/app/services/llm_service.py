from openai import AsyncOpenAI
from app.config import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using OpenAI GPT.

    Responsibilities:
    - Generate conversational responses
    - Maintain conversation context
    - Handle errors and retries
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(
        self,
        message: str,
        agent_prompt: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Get LLM response.

        Args:
            message: User's message
            agent_prompt: System prompt for agent role
            conversation_history: Previous messages (list of dicts)

        Returns:
            LLM response text

        Raises:
            ValueError: If message or agent_prompt is empty
            Exception: If API call fails

        Test Cases:
        - Should generate response for valid input
        - Should raise ValueError for empty message
        - Should raise ValueError for empty agent_prompt
        - Should handle conversation history correctly
        - Should limit response length
        - Should handle API errors gracefully
        """

        if not message or message.strip() == "":
            raise ValueError("Message cannot be empty")

        if not agent_prompt or agent_prompt.strip() == "":
            raise ValueError("Agent prompt cannot be empty")

        try:
            # Build messages
            messages = [
                {"role": "system", "content": agent_prompt}
            ]

            # Add conversation history (limit to last 10 turns)
            if conversation_history:
                # Keep only last 10 messages to avoid token limits
                recent_history = conversation_history[-10:]
                messages.extend(recent_history)

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call GPT API
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=150,  # Keep responses concise for voice
            )

            response_text = response.choices[0].message.content
            logger.info(f"LLM response generated: {len(response_text)} chars")

            return response_text

        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise

    def __repr__(self):
        return "LLMService()"