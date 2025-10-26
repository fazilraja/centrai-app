import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from app.services.tts_service import TTSService


@pytest.mark.asyncio
async def test_synthesize_stream_yields_chunks():
    """Test that synthesize_stream() yields audio chunks"""
    # Arrange
    async def mock_stream():
        yield b"audio_chunk_1"
        yield b"audio_chunk_2"
        yield b"audio_chunk_3"

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_chunked = AsyncMock(return_value=mock_stream())

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act
    chunks = []
    async for chunk in service.synthesize_stream(
        text="Hello world",
        voice_id="test_voice_id"
    ):
        chunks.append(chunk)

    # Assert
    assert len(chunks) == 3
    assert chunks[0] == b"audio_chunk_1"
    assert chunks[1] == b"audio_chunk_2"
    assert chunks[2] == b"audio_chunk_3"


@pytest.mark.asyncio
async def test_synthesize_stream_empty_text_raises_error():
    """Test that empty text raises ValueError"""
    # Arrange
    with patch('app.services.tts_service.settings') as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_api_key"
        service = TTSService()

    # Act & Assert
    with pytest.raises(ValueError, match="Text cannot be empty"):
        async for chunk in service.synthesize_stream(text="", voice_id="test_voice"):
            pass


@pytest.mark.asyncio
async def test_synthesize_stream_whitespace_text_raises_error():
    """Test that whitespace-only text raises ValueError"""
    # Arrange
    with patch('app.services.tts_service.settings') as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_api_key"
        service = TTSService()

    # Act & Assert
    with pytest.raises(ValueError, match="Text cannot be empty"):
        async for chunk in service.synthesize_stream(text="   ", voice_id="test_voice"):
            pass


@pytest.mark.asyncio
async def test_synthesize_stream_empty_voice_id_raises_error():
    """Test that empty voice_id raises ValueError"""
    # Arrange
    with patch('app.services.tts_service.settings') as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_api_key"
        service = TTSService()

    # Act & Assert
    with pytest.raises(ValueError, match="Voice ID cannot be empty"):
        async for chunk in service.synthesize_stream(text="Hello", voice_id=""):
            pass


@pytest.mark.asyncio
async def test_synthesize_stream_uses_correct_url():
    """Test that synthesize_stream() uses correct API URL"""
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_chunked = AsyncMock(
        return_value=iter([b"chunk"])
    )

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act
    async for chunk in service.synthesize_stream(
        text="Hello",
        voice_id="test_voice_id"
    ):
        pass

    # Assert
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    expected_url = f"{service.api_url}/text-to-speech/test_voice_id/stream"
    assert call_args[0][0] == expected_url


@pytest.mark.asyncio
async def test_synthesize_stream_sends_correct_data():
    """Test that synthesize_stream() sends correct request data"""
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_chunked = AsyncMock(
        return_value=iter([b"chunk"])
    )

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act
    async for chunk in service.synthesize_stream(
        text="Hello world",
        voice_id="test_voice_id"
    ):
        pass

    # Assert
    call_args = mock_session.post.call_args
    json_data = call_args[1]['json']

    assert json_data['text'] == "Hello world"
    assert json_data['model_id'] == "eleven_monolingual_v1"
    assert 'voice_settings' in json_data
    assert json_data['voice_settings']['stability'] == 0.5
    assert json_data['voice_settings']['similarity_boost'] == 0.75


@pytest.mark.asyncio
async def test_synthesize_stream_sends_correct_headers():
    """Test that synthesize_stream() sends correct headers"""
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_chunked = AsyncMock(
        return_value=iter([b"chunk"])
    )

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act
    async for chunk in service.synthesize_stream(
        text="Hello",
        voice_id="test_voice_id"
    ):
        pass

    # Assert
    call_args = mock_session.post.call_args
    headers = call_args[1]['headers']

    assert headers["xi-api-key"] == "test_api_key"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_synthesize_stream_handles_api_error():
    """Test that synthesize_stream() handles API errors"""
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.text = AsyncMock(return_value="Bad Request: Invalid voice ID")

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act & Assert
    with pytest.raises(Exception, match="TTS API error: Bad Request: Invalid voice ID"):
        async for chunk in service.synthesize_stream(
            text="Hello",
            voice_id="invalid_voice_id"
        ):
            pass


@pytest.mark.asyncio
async def test_synthesize_stream_handles_network_error():
    """Test that synthesize_stream() handles network errors"""
    # Arrange
    mock_session = AsyncMock()
    mock_session.post = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act & Assert
    with pytest.raises(aiohttp.ClientError, match="Network error"):
        async for chunk in service.synthesize_stream(
            text="Hello",
            voice_id="test_voice_id"
        ):
            pass


@pytest.mark.asyncio
async def test_tts_service_initialization():
    """Test TTSService initialization"""
    # Arrange
    with patch('app.services.tts_service.settings') as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_api_key"

        # Act
        service = TTSService()

        # Assert
        assert service.api_key == "test_api_key"
        assert service.api_url == "https://api.elevenlabs.io/v1"


def test_tts_service_repr():
    """Test TTSService string representation"""
    # Arrange
    with patch('app.services.tts_service.settings') as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_api_key"
        service = TTSService()

    # Act & Assert
    repr_str = repr(service)
    assert "TTSService" in repr_str


@pytest.mark.asyncio
async def test_synthesize_stream_long_text():
    """Test synthesize_stream with longer text"""
    # Arrange
    long_text = "This is a longer piece of text that should be synthesized to speech. " * 5

    async def mock_stream():
        for i in range(10):
            yield f"chunk_{i}".encode()

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_chunked = AsyncMock(return_value=mock_stream())

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        with patch('app.services.tts_service.settings') as mock_settings:
            mock_settings.ELEVENLABS_API_KEY = "test_api_key"
            service = TTSService()

    # Act
    chunks = []
    async for chunk in service.synthesize_stream(
        text=long_text,
        voice_id="test_voice_id"
    ):
        chunks.append(chunk)

    # Assert
    assert len(chunks) == 10
    assert chunks[0] == b"chunk_0"
    assert chunks[-1] == b"chunk_9"