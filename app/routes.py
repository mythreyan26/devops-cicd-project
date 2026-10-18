"""API routes and endpoint definitions for the Flask application."""

import sys
from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import HTTPException

from app.utils import calculate, get_utc_timestamp, validate_operand

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint returning service health status and UTC timestamp."""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": get_utc_timestamp(),
            }
        ),
        200,
    )


@api_bp.route("/api/v1/info", methods=["GET"])
def app_info():
    """Return runtime metadata including app name, version, python version, and environment."""
    return (
        jsonify(
            {
                "app_name": current_app.config.get("APP_NAME", "DevOps-CICD-Service"),
                "version": current_app.config.get("APP_VERSION", "1.0.0"),
                "python_version": sys.version.split()[0],
                "environment": current_app.config.get("ENVIRONMENT", "development"),
                "timestamp": get_utc_timestamp(),
            }
        ),
        200,
    )


@api_bp.route("/api/v1/calculate", methods=["POST"])
def perform_calculation():
    """Execute arithmetic operation on two numeric operands.

    Expected JSON body:
    {
        "operation": "add" | "subtract" | "multiply" | "divide",
        "num1": <number>,
        "num2": <number>
    }
    """
    if not request.is_json:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Content-Type must be application/json.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Invalid or malformed JSON payload.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    # Validate operation field
    if "operation" not in data:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Missing required field: 'operation'.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    operation = data.get("operation")
    if not isinstance(operation, str) or not operation.strip():
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Field 'operation' must be a non-empty string.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    # Extract operands (support num1/num2, operand1/operand2, or a/b)
    val1 = data.get("num1", data.get("operand1", data.get("a")))
    val2 = data.get("num2", data.get("operand2", data.get("b")))

    has_op1 = any(k in data for k in ("num1", "operand1", "a"))
    has_op2 = any(k in data for k in ("num2", "operand2", "b"))

    if not has_op1 or not has_op2:
        missing = []
        if not has_op1:
            missing.append("num1")
        if not has_op2:
            missing.append("num2")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": f"Missing required operand field(s): {', '.join(missing)}.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    # Validate operand 1
    num1, err1 = validate_operand(val1, "num1")
    if err1:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": err1,
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    # Validate operand 2
    num2, err2 = validate_operand(val2, "num2")
    if err2:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": err2,
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    # Perform calculation safely
    result, err_calc = calculate(operation, num1, num2)
    if err_calc:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": err_calc,
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "operation": operation.strip().lower(),
                "num1": num1,
                "num2": num2,
                "result": result,
                "timestamp": get_utc_timestamp(),
            }
        ),
        200,
    )


def register_error_handlers(app):
    """Register custom JSON error handlers for common HTTP status codes and exceptions."""

    @app.errorhandler(400)
    def bad_request(error):
        message = getattr(error, "description", "The request was invalid.")
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": message,
                    "timestamp": get_utc_timestamp(),
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested URL was not found on this server.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "error": "Method Not Allowed",
                    "message": "The method is not allowed for the requested URL.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please contact the administrator.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        if isinstance(error, HTTPException):
            return (
                jsonify(
                    {
                        "error": error.name,
                        "message": error.description,
                        "timestamp": get_utc_timestamp(),
                    }
                ),
                error.code,
            )

        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please contact the administrator.",
                    "timestamp": get_utc_timestamp(),
                }
            ),
            500,
        )
