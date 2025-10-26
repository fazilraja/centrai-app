from openai import AsyncOpenAI
from app.config import settings
import io
import logging

logger = logging.getLogger(__name__)


class STTService:
    """
    Speech-to-Text service using OpenAI Whisper.

    Responsibilities:
    - Transcribe audio bytes to text
    - Handle audio format conversion
    - Error handling and retries
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_bytes: Raw audio data (WebM, MP3, WAV, etc.)

        Returns:
            Transcribed text

        Raises:
            ValueError: If audio_bytes is empty
            Exception: If API call fails

        Test Cases:
        - Should transcribe valid audio
        - Should raise ValueError for empty audio
        - Should handle API errors gracefully
        - Should return non-empty string
        - Should handle various audio formats
        """

        if not audio_bytes:
            raise ValueError("Audio bytes cannot be empty")

        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"  # Whisper needs a filename

            # Call Whisper API
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",  # Optional: auto-detect if omitted
                response_format="text"
            )

            logger.info(f"Transcription successful: {len(response)} chars")
            return response

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise

    def __repr__(self):
        return "STTService()"