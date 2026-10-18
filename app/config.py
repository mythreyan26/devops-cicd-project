"""Application configuration module."""

import os


class Config:
    """Base configuration."""

    APP_NAME: str = os.getenv("APP_NAME", "DevOps-CICD-Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    TESTING: bool = False
    DEBUG: bool = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class TestingConfig(Config):
    """Testing configuration."""

    ENVIRONMENT: str = "testing"
    TESTING: bool = True
    DEBUG: bool = True


class ProductionConfig(Config):
    """Production configuration."""

    ENVIRONMENT: str = "production"
    TESTING: bool = False
    DEBUG: bool = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None) -> type[Config]:
    """Retrieve configuration class based on environment name."""
    if not env_name:
        env_name = os.getenv("ENVIRONMENT", "development").lower()
    return CONFIG_MAP.get(env_name, DevelopmentConfig)
