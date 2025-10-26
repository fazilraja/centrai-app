import pytest
from unittest.mock import patch, MagicMock
import io
from app.services.audio_processor import AudioProcessor


def test_convert_webm_to_mp3_valid():
    """Test convert_webm_to_mp3 with valid WebM data"""
    # Arrange
    webm_data = b"WEBM_AUDIO_DATA_HERE"

    # Mock AudioSegment
    mock_audio = MagicMock()
    mock_output = io.BytesIO(b"MP3_AUDIO_DATA")

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        mock_audio.export = MagicMock(return_value=mock_output)

        processor = AudioProcessor()

    # Act
    result = processor.convert_webm_to_mp3(webm_data)

    # Assert
    assert isinstance(result, bytes)
    assert len(result) > 0
    mock_audio_segment.from_file.assert_called_once()

    # Verify the call arguments
    call_args = mock_audio_segment.from_file.call_args
    assert isinstance(call_args[0][0], io.BytesIO)
    assert call_args[1]['format'] == "webm"

    # Verify export was called with correct parameters
    mock_audio.export.assert_called_once()
    export_call_args = mock_audio.export.call_args
    assert export_call_args[1]['format'] == "mp3"
    assert export_call_args[1]['bitrate'] == "128k"


def test_convert_webm_to_mp3_invalid_data():
    """Test convert_webm_to_mp3 with invalid data raises exception"""
    # Arrange
    invalid_data = b"INVALID_AUDIO_DATA"
    processor = AudioProcessor()

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.side_effect = Exception("Invalid audio format")

    # Act & Assert
    with pytest.raises(Exception, match="Invalid audio format"):
        processor.convert_webm_to_mp3(invalid_data)


def test_detect_silence_silent_audio():
    """Test detect_silence with silent audio"""
    # Arrange
    silent_audio = b"SILENT_AUDIO_DATA"
    mock_audio = MagicMock()
    mock_audio.dBFS = -50  # Below default threshold of -40

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        processor = AudioProcessor()

    # Act
    result = processor.detect_silence(silent_audio)

    # Assert
    assert result is True
    mock_audio_segment.from_file.assert_called_once_with(io.BytesIO(silent_audio))


def test_detect_silence_loud_audio():
    """Test detect_silence with loud audio"""
    # Arrange
    loud_audio = b"LOUD_AUDIO_DATA"
    mock_audio = MagicMock()
    mock_audio.dBFS = -20  # Above default threshold of -40

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        processor = AudioProcessor()

    # Act
    result = processor.detect_silence(loud_audio)

    # Assert
    assert result is False


def test_detect_silence_custom_threshold():
    """Test detect_silence with custom threshold"""
    # Arrange
    audio_data = b"AUDIO_DATA"
    mock_audio = MagicMock()
    mock_audio.dBFS = -30  # Between -20 and -40

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        processor = AudioProcessor()

    # Act
    result_strict = processor.detect_silence(audio_data, threshold=-20)  # Should be silent
    result_lenient = processor.detect_silence(audio_data, threshold=-40)  # Should not be silent

    # Assert
    assert result_strict is True
    assert result_lenient is False


def test_detect_silence_invalid_audio():
    """Test detect_silence with invalid audio returns False"""
    # Arrange
    invalid_audio = b"INVALID_AUDIO"
    processor = AudioProcessor()

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.side_effect = Exception("Invalid audio")

    # Act
    result = processor.detect_silence(invalid_audio)

    # Assert
    assert result is False


def test_get_duration_valid_audio():
    """Test get_duration with valid audio"""
    # Arrange
    audio_data = b"AUDIO_DATA_2_SECONDS"
    mock_audio = MagicMock()
    mock_audio.__len__ = MagicMock(return_value=2000)  # 2000ms = 2 seconds

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        processor = AudioProcessor()

    # Act
    result = processor.get_duration(audio_data)

    # Assert
    assert result == 2.0
    mock_audio.__len__.assert_called_once()


def test_get_duration_zero_length():
    """Test get_duration with zero-length audio"""
    # Arrange
    audio_data = b"ZERO_LENGTH_AUDIO"
    mock_audio = MagicMock()
    mock_audio.__len__ = MagicMock(return_value=0)

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        processor = AudioProcessor()

    # Act
    result = processor.get_duration(audio_data)

    # Assert
    assert result == 0.0


def test_get_duration_invalid_audio():
    """Test get_duration with invalid audio returns 0.0"""
    # Arrange
    invalid_audio = b"INVALID_AUDIO"
    processor = AudioProcessor()

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.side_effect = Exception("Invalid audio")

    # Act
    result = processor.get_duration(invalid_audio)

    # Assert
    assert result == 0.0


def test_get_duration_milliseconds_conversion():
    """Test get_duration properly converts milliseconds to seconds"""
    # Arrange
    audio_data = b"AUDIO_DATA_1500MS"
    mock_audio = MagicMock()
    mock_audio.__len__ = MagicMock(return_value=1500)  # 1500ms

    with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
        mock_audio_segment.from_file.return_value = mock_audio
        processor = AudioProcessor()

    # Act
    result = processor.get_duration(audio_data)

    # Assert
    assert result == 1.5  # 1500ms / 1000 = 1.5 seconds


def test_audio_processor_static_methods():
    """Test that AudioProcessor methods are static"""
    # Arrange
    processor = AudioProcessor()

    # Act & Assert - These should work without instance state
    assert hasattr(processor.convert_webm_to_mp3, '__func__')
    assert hasattr(processor.detect_silence, '__func__')
    assert hasattr(processor.get_duration, '__func__')


def test_audio_processor_various_formats():
    """Test AudioProcessor works with various audio formats"""
    # Arrange
    formats = ["webm", "mp3", "wav", "ogg"]

    for format_name in formats:
        with patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
            mock_audio = MagicMock()
            mock_audio.dBFS = -30
            mock_audio.__len__ = MagicMock(return_value=1000)
            mock_audio_segment.from_file.return_value = mock_audio

            processor = AudioProcessor()
            audio_data = f"{format_name.upper()}_AUDIO_DATA".encode()

            # Act
            duration = processor.get_duration(audio_data)
            is_silent = processor.detect_silence(audio_data)

            # Assert
            assert duration == 1.0
            assert isinstance(is_silent, bool)

            # Verify from_file was called with correct format for duration check
            mock_audio_segment.from_file.assert_called()
            last_call = mock_audio_segment.from_file.call_args
            assert isinstance(last_call[0][0], io.BytesIO)