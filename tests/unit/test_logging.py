import json
import logging

from handwriting.core.logging import JsonFormatter, configure_logging


def test_json_formatter_returns_structured_log():
    record = logging.LogRecord(
        name="handwriting.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatter = JsonFormatter()

    formatted_log = formatter.format(record)
    data = json.loads(formatted_log)

    assert "timestamp" in data
    assert data["level"] == "INFO"
    assert data["logger"] == "handwriting.test"
    assert data["message"] == "Test message"


def test_configure_logging_sets_root_logger():
    configure_logging(level=logging.DEBUG)

    logger = logging.getLogger("handwriting")

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.handlers[0].formatter, JsonFormatter)
    assert logger.propagate is False