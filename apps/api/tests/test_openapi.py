"""Unit test for OpenAPI contract generation."""

from hikmah.main import app


def test_openapi_schema_generation() -> None:
    """Ensure OpenAPI 3.x schema exports cleanly with all governance routes."""
    schema = app.openapi()
    assert schema["openapi"].startswith("3.")
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/seats" in schema["paths"]
    assert "/api/v1/rules" in schema["paths"]
    assert "/api/v1/knowledge" in schema["paths"]
    assert "/api/v1/traces" in schema["paths"]
