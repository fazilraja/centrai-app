import aiohttp
from app.config import settings
from typing import AsyncIterator
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """
    Text-to-Speech service using ElevenLabs.

    Responsibilities:
    - Convert text to speech
    - Stream audio chunks
    - Handle errors and retries
    """

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.api_url = "https://api.elevenlabs.io/v1"

    async def synthesize_stream(
        self,
        text: str,
        voice_id: str
    ) -> AsyncIterator[bytes]:
        """
        Convert text to speech with streaming.

        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID

        Yields:
            Audio chunks (MP3 format)

        Raises:
            ValueError: If text or voice_id is empty
            Exception: If API call fails

        Test Cases:
        - Should stream audio for valid input
        - Should raise ValueError for empty text
        - Should raise ValueError for empty voice_id
        - Should yield multiple chunks
        - Should handle API errors gracefully
        """

        if not text or text.strip() == "":
            raise ValueError("Text cannot be empty")

        if not voice_id or voice_id.strip() == "":
            raise ValueError("Voice ID cannot be empty")

        url = f"{self.api_url}/text-to-speech/{voice_id}/stream"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"TTS API error: {error_text}")

                    # Stream audio chunks
                    chunk_count = 0
                    async for chunk in response.content.iter_chunked(4096):
                        chunk_count += 1
                        yield chunk

                    logger.info(f"TTS streaming complete: {chunk_count} chunks")

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}", exc_info=True)
            raise

    def __repr__(self):
        return "TTSService()"