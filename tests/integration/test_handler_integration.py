"""
Integration tests for Lambda handler.
Tests the complete end-to-end flow with HTTP-level mocking.
"""
import responses
import pytest
import os
from src.handler import lambda_handler

pytestmark = pytest.mark.integration


@pytest.fixture
def api_event():
    """API Gateway event fixture for integration tests."""
    return {
        "pathParameters": {"dashboard_id": "abc123"},
        "queryStringParameters": {"view": "Prod"},
    }


@pytest.fixture
def api_event_missing_view():
    """API Gateway event without view parameter."""
    return {
        "pathParameters": {"dashboard_id": "abc123"},
        "queryStringParameters": None,
    }


@pytest.fixture(autouse=True)
def setup_environment():
    """Set up environment variables for integration tests."""
    os.environ["DATADOG_API_KEY"] = "test_api_key"
    os.environ["DATADOG_APP_KEY"] = "test_app_key"
    os.environ["DATADOG_SITE"] = "datadoghq.com"


@responses.activate
def test_successful_redirect_integration(api_event):
    """Test successful redirect with valid dashboard and saved view."""
    dashboard_json = {
        "id": "abc123",
        "template_variable_presets": [
            {
                "name": "Prod",
                "template_variables": [
                    {"name": "env", "value": "prod"},
                    {"name": "region", "value": "us-east-1"}
                ]
            }
        ],
    }

    responses.get(
        "https://api.datadoghq.com/api/v1/dashboards/abc123",
        json=dashboard_json,
        status=200,
    )

    result = lambda_handler(api_event, None)

    assert result["statusCode"] == 302
    assert "Location" in result["headers"]
    location = result["headers"]["Location"]
    assert "https://app.datadoghq.com/dashboard/abc123" in location
    assert "tpl_var_env=prod" in location
    assert "tpl_var_region=us-east-1" in location


@responses.activate
def test_saved_view_not_found_integration(api_event):
    """Test 404 when saved view doesn't exist."""
    dashboard_json = {
        "id": "abc123",
        "template_variable_presets": [
            {
                "name": "Different",
                "template_variables": [{"name": "env", "value": "dev"}]
            }
        ],
    }

    responses.get(
        "https://api.datadoghq.com/api/v1/dashboards/abc123",
        json=dashboard_json,
        status=200,
    )

    result = lambda_handler(api_event, None)
    assert result["statusCode"] == 404
    assert "Saved view 'Prod' not found" in result["body"]


@responses.activate
def test_dashboard_not_found_integration(api_event):
    """Test 404 when dashboard doesn't exist."""
    responses.get(
        "https://api.datadoghq.com/api/v1/dashboards/abc123",
        json={"errors": ["Dashboard not found"]},
        status=404,
    )

    result = lambda_handler(api_event, None)
    assert result["statusCode"] == 500
    assert "Internal server error" in result["body"]


@responses.activate
def test_datadog_api_error_integration(api_event):
    """Test 500 when Datadog API returns server error."""
    responses.get(
        "https://api.datadoghq.com/api/v1/dashboards/abc123",
        json={"error": "Internal server error"},
        status=500,
    )

    result = lambda_handler(api_event, None)
    assert result["statusCode"] == 500
    assert "Internal server error" in result["body"]


@responses.activate
def test_missing_view_parameter_integration(api_event_missing_view):
    """Test 400 when view parameter is missing."""
    # No need to mock Datadog API since we should fail before making the call
    result = lambda_handler(api_event_missing_view, None)
    assert result["statusCode"] == 400
    assert "view parameter is required" in result["body"]


@responses.activate
def test_custom_datadog_site_integration():
    """Test integration with custom Datadog site."""
    os.environ["DATADOG_SITE"] = "datadoghq.eu"
    
    api_event = {
        "pathParameters": {"dashboard_id": "abc123"},
        "queryStringParameters": {"view": "Prod"},
    }

    dashboard_json = {
        "id": "abc123",
        "template_variable_presets": [
            {
                "name": "Prod",
                "template_variables": [{"name": "env", "value": "prod"}]
            }
        ],
    }

    responses.get(
        "https://api.datadoghq.eu/api/v1/dashboards/abc123",
        json=dashboard_json,
        status=200,
    )

    result = lambda_handler(api_event, None)

    assert result["statusCode"] == 302
    location = result["headers"]["Location"]
    assert "https://app.datadoghq.eu/dashboard/abc123" in location
    assert "tpl_var_env=prod" in location

    # Reset environment
    os.environ["DATADOG_SITE"] = "datadoghq.com"


@responses.activate
def test_complex_template_variables_integration():
    """Test integration with complex template variables including encoding."""
    api_event = {
        "pathParameters": {"dashboard_id": "xyz456"},
        "queryStringParameters": {"view": "Staging Environment"},
    }

    dashboard_json = {
        "id": "xyz456",
        "template_variable_presets": [
            {
                "name": "Staging Environment",
                "template_variables": [
                    {"name": "service", "value": "api server"},
                    {"name": "version", "value": "v1.2.3"},
                    {"name": "datacenter", "value": "us-west-2"}
                ]
            }
        ],
    }

    responses.get(
        "https://api.datadoghq.com/api/v1/dashboards/xyz456",
        json=dashboard_json,
        status=200,
    )

    result = lambda_handler(api_event, None)

    assert result["statusCode"] == 302
    location = result["headers"]["Location"]
    assert "https://app.datadoghq.com/dashboard/xyz456" in location
    assert "tpl_var_service=api+server" in location  # URL encoded with +
    assert "tpl_var_version=v1.2.3" in location
    assert "tpl_var_datacenter=us-west-2" in location