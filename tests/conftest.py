"""Test fixtures and configuration"""

import pytest
import os
import sys

# Add src to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set test environment variables
    os.environ["APP_ENV"] = "testing"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["LOG_LEVEL"] = "DEBUG"

    yield

    # Cleanup
    pass
