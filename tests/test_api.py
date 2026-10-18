"""Automated unit and integration tests for the API calculator and error handling."""

import pytest


# -----------------------------------------------------------------------------
# Positive calculation tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "num1, num2, operation, expected",
    [
        (10, 20, "add", 30),
        (50, 15, "subtract", 35),
        (6, 7, "multiply", 42),
        (100, 4, "divide", 25),
        (7, 2, "divide", 3.5),
        (-10, 5, "add", -5),
        (2.5, 3.5, "add", 6),
        (10, 3, "divide", 3.333333),
    ],
)
def test_calculate_operations_success(client, num1, num2, operation, expected):
    """Verify that arithmetic operations calculate expected values correctly."""
    payload = {"num1": num1, "num2": num2, "operation": operation}
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["operation"] == operation
    assert data["result"] == pytest.approx(expected, abs=1e-5)
    assert "timestamp" in data


# -----------------------------------------------------------------------------
# Negative tests & validation handling
# -----------------------------------------------------------------------------
def test_calculate_division_by_zero(client):
    """Verify that division by zero is safely rejected with HTTP 400 Bad Request."""
    payload = {"num1": 42, "num2": 0, "operation": "divide"}
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "Division by zero" in data["message"]


def test_calculate_unsupported_operation(client):
    """Verify that unsupported operations return HTTP 400 Bad Request."""
    payload = {"num1": 10, "num2": 2, "operation": "exponentiate"}
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "Unsupported operation" in data["message"]


@pytest.mark.parametrize(
    "payload, expected_missing",
    [
        ({"num2": 10, "operation": "add"}, "num1"),
        ({"num1": 10, "operation": "add"}, "num2"),
        ({"num1": 10, "num2": 20}, "operation"),
    ],
)
def test_calculate_missing_required_fields(client, payload, expected_missing):
    """Verify that omitting required fields produces an informative HTTP 400 error."""
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert expected_missing in data["message"]


def test_calculate_rejects_boolean_operands(client):
    """Verify that booleans are strictly rejected as numbers even though Python bool inherits int."""
    payload = {"num1": True, "num2": 10, "operation": "add"}
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "cannot be a boolean" in data["message"]


def test_calculate_rejects_non_numeric_string_operands(client):
    """Verify that non-numeric string values return HTTP 400 Bad Request."""
    payload = {"num1": "invalid_number", "num2": 5, "operation": "add"}
    response = client.post("/api/v1/calculate", json=payload)

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "must be a valid number" in data["message"]


def test_calculate_malformed_json_payload(client):
    """Verify that malformed JSON is rejected with HTTP 400 and structured error response."""
    response = client.post(
        "/api/v1/calculate",
        data="{invalid_json_format: true,",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"


def test_calculate_non_json_content_type(client):
    """Verify that requests missing application/json content-type header return HTTP 400."""
    response = client.post(
        "/api/v1/calculate",
        data="num1=10&num2=20&operation=add",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "Content-Type must be application/json" in data["message"]


# -----------------------------------------------------------------------------
# Route & method safety tests
# -----------------------------------------------------------------------------
def test_unknown_route_returns_json_404(client):
    """Verify that navigating to a non-existent route returns consistent JSON 404."""
    response = client.get("/api/v1/non-existent-endpoint")

    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Not Found"
    assert "timestamp" in data


def test_method_not_allowed_returns_json_405(client):
    """Verify that sending an unsupported HTTP method returns consistent JSON 405."""
    response = client.get("/api/v1/calculate")

    assert response.status_code == 405
    assert response.is_json
    data = response.get_json()
    assert data["error"] == "Method Not Allowed"
    assert "timestamp" in data


# -----------------------------------------------------------------------------
# Explicit failure handling demonstration test
# -----------------------------------------------------------------------------
def test_demonstrating_failure_handling_with_hostile_inputs(client):
    """Deliberately supply hostile / erroneous inputs and verify graceful failure handling.

    This test confirms that unusual payloads (nulls, object values, NaN/infinity,
    or SQL injection strings) do not cause 500 errors or expose internal stack traces.
    """
    hostile_cases = [
        {"num1": None, "num2": 10, "operation": "add"},
        {"num1": {"nested": "dict"}, "num2": 10, "operation": "add"},
        {"num1": [1, 2, 3], "num2": 10, "operation": "add"},
        {"num1": "DROP TABLE users;", "num2": 10, "operation": "add"},
        {"num1": float("nan"), "num2": 5, "operation": "add"},
    ]

    for case in hostile_cases:
        response = client.post("/api/v1/calculate", json=case)
        assert response.status_code == 400, f"Expected 400 for input {case}, got {response.status_code}"
        assert response.is_json
        body = response.get_json()
        assert body["error"] == "Bad Request"
        assert "message" in body
        assert "traceback" not in body
