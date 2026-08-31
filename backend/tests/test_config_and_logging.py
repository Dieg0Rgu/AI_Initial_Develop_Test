import pytest
import logging
from app.config import Settings
from app.utils.logger import setup_logger, JSONFormatter


def test_settings_validation_and_defaults():
    settings = Settings()
    assert settings.PORT == 8000
    assert settings.SIMILARITY_THRESHOLD == 0.45
    assert settings.LLM_TEMPERATURE == 0.2
    assert settings.CHUNK_OVERLAP < settings.CHUNK_SIZE


def test_settings_invalid_port():
    with pytest.raises(ValueError, match="PORT must be between 1 and 65535"):
        Settings(PORT=70000)


def test_settings_invalid_similarity_threshold():
    with pytest.raises(ValueError, match="SIMILARITY_THRESHOLD must be between 0.0 and 1.0"):
        Settings(SIMILARITY_THRESHOLD=1.5)


def test_settings_invalid_temperature():
    with pytest.raises(ValueError, match="LLM_TEMPERATURE must be between 0.0 and 2.0"):
        Settings(LLM_TEMPERATURE=3.5)


def test_settings_invalid_chunk_overlap():
    with pytest.raises(ValueError, match="CHUNK_OVERLAP must be strictly smaller than CHUNK_SIZE"):
        Settings(CHUNK_SIZE=200, CHUNK_OVERLAP=250)


def test_structured_logger_levels(capsys):
    test_logger = setup_logger("test_custom_logger", level=logging.DEBUG)

    test_logger.debug("Debug message trace")
    test_logger.info("Informative status log")
    test_logger.warning("Warning message")
    test_logger.error("Error event occurred")

    captured = capsys.readouterr()
    assert "Debug message trace" in captured.out
    assert "Informative status log" in captured.out
    assert "Warning message" in captured.out
    assert "Error event occurred" in captured.out


def test_json_log_formatter():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=50,
        msg="Sample JSON test log",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert '"level": "INFO"' in formatted
    assert '"message": "Sample JSON test log"' in formatted
    assert '"timestamp":' in formatted
