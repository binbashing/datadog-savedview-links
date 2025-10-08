"""
Unit tests for Datadog API client.
"""
import pytest
import responses
from src.datadog_client import (
    DatadogClient, DashboardNotFound, DatadogServerError, DatadogAuthError
)

pytestmark = pytest.mark.unit


class TestDatadogClient:
    """Test Datadog API client functionality."""

    @responses.activate
    def test_get_dashboard_success(self):
        """Test successful dashboard retrieval."""
        # Mock Datadog API response
        dashboard_id = "abc-123"
        mock_response = {
            "id": dashboard_id,
            "title": "Test Dashboard",
            "template_variable_presets": [
                {
                    "name": "Production",
                    "template_variables": [
                        {"name": "env", "value": "prod"}
                    ]
                }
            ]
        }

        responses.add(
            responses.GET,
            f"https://api.datadoghq.com/api/v1/dashboards/{dashboard_id}",
            json=mock_response,
            status=200
        )

        # Test client
        client = DatadogClient("fake-api-key", "fake-app-key")
        result = client.get_dashboard(dashboard_id)

        assert result == mock_response
        assert result["id"] == dashboard_id

    @responses.activate
    def test_get_dashboard_custom_site(self):
        """Test dashboard retrieval with custom site."""
        dashboard_id = "xyz-789"
        site = "datadoghq.eu"
        mock_response = {"id": dashboard_id, "title": "EU Dashboard"}

        responses.add(
            responses.GET,
            f"https://api.{site}/api/v1/dashboards/{dashboard_id}",
            json=mock_response,
            status=200
        )

        client = DatadogClient("fake-api-key", "fake-app-key", site)
        result = client.get_dashboard(dashboard_id)

        assert result == mock_response

    @responses.activate
    def test_get_dashboard_404_error(self):
        """Test handling of 404 dashboard not found."""
        dashboard_id = "nonexistent"

        responses.add(
            responses.GET,
            f"https://api.datadoghq.com/api/v1/dashboards/{dashboard_id}",
            json={"error": "Dashboard not found"},
            status=404
        )

        client = DatadogClient("fake-api-key", "fake-app-key")

        with pytest.raises(Exception):  # Will be more specific in implementation
            client.get_dashboard(dashboard_id)

    @responses.activate
    def test_get_dashboard_api_error(self):
        """Test handling of API errors."""
        dashboard_id = "error-case"

        responses.add(
            responses.GET,
            f"https://api.datadoghq.com/api/v1/dashboards/{dashboard_id}",
            json={"error": "Internal server error"},
            status=500
        )

        client = DatadogClient("fake-api-key", "fake-app-key")

        with pytest.raises(DatadogServerError):
            client.get_dashboard(dashboard_id)

    @responses.activate
    def test_get_dashboard_not_found(self):
        """Test handling of dashboard not found errors."""
        dashboard_id = "not-found"

        responses.add(
            responses.GET,
            f"https://api.datadoghq.com/api/v1/dashboards/{dashboard_id}",
            json={"errors": ["Dashboard not found"]},
            status=404
        )

        client = DatadogClient("fake-api-key", "fake-app-key")

        with pytest.raises(DashboardNotFound):
            client.get_dashboard(dashboard_id)

    @responses.activate
    def test_get_dashboard_auth_error(self):
        """Test handling of authentication errors."""
        dashboard_id = "auth-fail"

        responses.add(
            responses.GET,
            f"https://api.datadoghq.com/api/v1/dashboards/{dashboard_id}",
            json={"errors": ["Authentication failed"]},
            status=403
        )

        client = DatadogClient("fake-api-key", "fake-app-key")

        with pytest.raises(DatadogAuthError):
            client.get_dashboard(dashboard_id)
