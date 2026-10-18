"""Flask application factory."""

from flask import Flask

from app.config import Config, get_config
from app.routes import api_bp, register_error_handlers


def create_app(config_class: type[Config] | None = None) -> Flask:
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    if config_class is None:
        config_class = get_config()

    app.config.from_object(config_class)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Register global JSON error handlers
    register_error_handlers(app)

    return app
