import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import io
from app.services.stt_service import STTService


@pytest.mark.asyncio
async def test_transcribe_valid_audio():
    """Test transcription with valid audio"""
    # Arrange
    mock_client = AsyncMock()
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value="Hello, this is a test transcription"
    )

    with patch('app.services.stt_service.AsyncOpenAI', return_value=mock_client):
        service = STTService()
        audio_bytes = b"fake_audio_data"

    # Act
    result = await service.transcribe(audio_bytes)

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0
    assert result == "Hello, this is a test transcription"
    mock_client.audio.transcriptions.create.assert_called_once()

    # Verify the call arguments
    call_args = mock_client.audio.transcriptions.create.call_args
    assert call_args[1]['model'] == "whisper-1"
    assert call_args[1]['language'] == "en"
    assert call_args[1]['response_format'] == "text"
    assert isinstance(call_args[1]['file'], io.BytesIO)


@pytest.mark.asyncio
async def test_transcribe_empty_audio_raises_error():
    """Test that empty audio raises ValueError"""
    # Arrange
    service = STTService()

    # Act & Assert
    with pytest.raises(ValueError, match="Audio bytes cannot be empty"):
        await service.transcribe(b"")


@pytest.mark.asyncio
async def test_transcribe_none_audio_raises_error():
    """Test that None audio raises ValueError"""
    # Arrange
    service = STTService()

    # Act & Assert
    with pytest.raises(ValueError, match="Audio bytes cannot be empty"):
        await service.transcribe(None)


@pytest.mark.asyncio
async def test_transcribe_api_error():
    """Test that API errors are properly raised"""
    # Arrange
    mock_client = AsyncMock()
    mock_client.audio.transcriptions.create = AsyncMock(
        side_effect=Exception("API Error: Rate limit exceeded")
    )

    with patch('app.services.stt_service.AsyncOpenAI', return_value=mock_client):
        service = STTService()
        audio_bytes = b"fake_audio_data"

    # Act & Assert
    with pytest.raises(Exception, match="API Error: Rate limit exceeded"):
        await service.transcribe(audio_bytes)


@pytest.mark.asyncio
async def test_transcribe_uses_correct_model():
    """Test that the correct model is used"""
    # Arrange
    mock_client = AsyncMock()
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value="Test result"
    )

    with patch('app.services.stt_service.AsyncOpenAI', return_value=mock_client):
        service = STTService()
        audio_bytes = b"fake_audio_data"

    # Act
    await service.transcribe(audio_bytes)

    # Assert
    call_args = mock_client.audio.transcriptions.create.call_args
    assert call_args[1]['model'] == "whisper-1"


@pytest.mark.asyncio
async def test_transcribe_sets_file_name():
    """Test that the audio file is given a proper name"""
    # Arrange
    mock_client = AsyncMock()
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value="Test result"
    )

    with patch('app.services.stt_service.AsyncOpenAI', return_value=mock_client):
        service = STTService()
        audio_bytes = b"fake_audio_data"

    # Act
    await service.transcribe(audio_bytes)

    # Assert
    call_args = mock_client.audio.transcriptions.create.call_args
    audio_file = call_args[1]['file']
    assert audio_file.name == "audio.webm"


@pytest.mark.asyncio
async def test_transcribe_with_different_audio_formats():
    """Test transcription works with different audio data"""
    # Arrange
    mock_client = AsyncMock()
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value="Different format transcription"
    )

    with patch('app.services.stt_service.AsyncOpenAI', return_value=mock_client):
        service = STTService()
        webm_audio = b"WEBM_AUDIO_DATA"
        mp3_audio = b"MP3_AUDIO_DATA"
        wav_audio = b"WAV_AUDIO_DATA"

    # Act & Assert - All should work
    result1 = await service.transcribe(webm_audio)
    result2 = await service.transcribe(mp3_audio)
    result3 = await service.transcribe(wav_audio)

    assert result1 == "Different format transcription"
    assert result2 == "Different format transcription"
    assert result3 == "Different format transcription"
    assert mock_client.audio.transcriptions.create.call_count == 3


@pytest.mark.asyncio
async def test_stt_service_initialization():
    """Test STTService initialization"""
    # Arrange
    with patch('app.services.stt_service.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test_api_key"

        # Act
        service = STTService()

        # Assert
        assert service.client is not None


def test_stt_service_repr():
    """Test STTService string representation"""
    # Arrange
    with patch('app.services.stt_service.settings'):
        service = STTService()

    # Act & Assert
    repr_str = repr(service)
    assert "STTService" in repr_str