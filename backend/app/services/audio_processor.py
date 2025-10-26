import io
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Audio format conversion and processing utilities.

    Responsibilities:
    - Convert between audio formats
    - Validate audio data
    - Calculate audio properties
    """

    @staticmethod
    def convert_webm_to_mp3(webm_bytes: bytes) -> bytes:
        """
        Convert WebM to MP3.

        Args:
            webm_bytes: WebM audio data

        Returns:
            MP3 audio data

        Test Cases:
        - Should convert valid WebM to MP3
        - Should raise exception for invalid data
        """

        try:
            # Load WebM
            audio = AudioSegment.from_file(
                io.BytesIO(webm_bytes),
                format="webm"
            )

            # Export as MP3
            output = io.BytesIO()
            audio.export(output, format="mp3", bitrate="128k")

            return output.getvalue()

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise

    @staticmethod
    def detect_silence(audio_bytes: bytes, threshold: int = -40) -> bool:
        """
        Detect if audio is mostly silence.

        Args:
            audio_bytes: Audio data
            threshold: dBFS threshold for silence

        Returns:
            True if audio is silent, False otherwise

        Test Cases:
        - Should detect silence
        - Should detect non-silence
        """

        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            return audio.dBFS < threshold

        except Exception as e:
            logger.error(f"Silence detection failed: {e}")
            return False

    @staticmethod
    def get_duration(audio_bytes: bytes) -> float:
        """
        Get audio duration in seconds.

        Args:
            audio_bytes: Audio data

        Returns:
            Duration in seconds

        Test Cases:
        - Should return correct duration
        - Should handle various formats
        """

        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            return len(audio) / 1000.0  # Convert ms to seconds

        except Exception as e:
            logger.error(f"Duration calculation failed: {e}")
            return 0.0