"""Pytest configuration and shared fixtures for Flask testing."""

import pytest
from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create and configure a Flask app instance in testing mode."""
    application = create_app(config_class=TestingConfig)
    return application


@pytest.fixture
def client(app):
    """Provide a test client for making simulated HTTP requests."""
    return app.test_client()
