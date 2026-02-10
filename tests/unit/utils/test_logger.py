"""Tests for logger utility."""

import pytest
from src.utils.logger import get_logger


class TestLogger:
    """Test suite for logger utility."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")

    def test_logger_info(self):
        """Test logger info method."""
        logger = get_logger("test_module")

        # Should not raise
        logger.info("test_message", key="value")

    def test_logger_debug(self):
        """Test logger debug method."""
        logger = get_logger("test_module")

        # Should not raise
        logger.debug("test_debug", data=123)

    def test_logger_error(self):
        """Test logger error method."""
        logger = get_logger("test_module")

        # Should not raise
        logger.error("test_error", error="something went wrong")

    def test_logger_warning(self):
        """Test logger warning method."""
        logger = get_logger("test_module")

        # Should not raise
        logger.warning("test_warning", status="deprecated")
