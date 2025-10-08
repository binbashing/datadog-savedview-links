"""
Unit tests for environment variable handling.
"""
import pytest
import os
from unittest.mock import patch, Mock
from src.handler import lambda_handler

pytestmark = pytest.mark.unit


class TestEnvironmentVariables:
    """Test environment variable validation."""

    def test_missing_datadog_api_key(self):
        """Test handler when DATADOG_API_KEY is missing."""
        event = {
            "pathParameters": {"dashboard_id": "test-123"},
            "queryStringParameters": {"view": "Prod"},
        }

        with patch.dict(os.environ, {}, clear=True):
            # Only set APP_KEY, missing API_KEY
            os.environ["DATADOG_APP_KEY"] = "test_app_key"
            os.environ["DATADOG_SITE"] = "datadoghq.com"

            result = lambda_handler(event, None)

            assert result["statusCode"] == 500
            assert "DATADOG_API_KEY environment variable is required" in result["body"]

    def test_missing_datadog_app_key(self):
        """Test handler when DATADOG_APP_KEY is missing."""
        event = {
            "pathParameters": {"dashboard_id": "test-123"},
            "queryStringParameters": {"view": "Prod"},
        }

        with patch.dict(os.environ, {}, clear=True):
            # Only set API_KEY, missing APP_KEY
            os.environ["DATADOG_API_KEY"] = "test_api_key"
            os.environ["DATADOG_SITE"] = "datadoghq.com"

            result = lambda_handler(event, None)

            assert result["statusCode"] == 500
            assert "DATADOG_APP_KEY environment variable is required" in result["body"]

    def test_missing_both_keys(self):
        """Test handler when both API keys are missing."""
        event = {
            "pathParameters": {"dashboard_id": "test-123"},
            "queryStringParameters": {"view": "Prod"},
        }

        with patch.dict(os.environ, {}, clear=True):
            # Set only SITE, missing both keys
            os.environ["DATADOG_SITE"] = "datadoghq.com"

            result = lambda_handler(event, None)

            assert result["statusCode"] == 500
            # Should return the first missing key error (API_KEY checked first)
            assert "DATADOG_API_KEY environment variable is required" in result["body"]

    def test_datadog_site_defaults_correctly(self):
        """Test that DATADOG_SITE defaults to datadoghq.com when not set."""
        event = {
            "pathParameters": {"dashboard_id": "test-123"},
            "queryStringParameters": {"view": "Prod"},
        }

        with patch.dict(os.environ, {}, clear=True):
            os.environ["DATADOG_API_KEY"] = "test_api_key"
            os.environ["DATADOG_APP_KEY"] = "test_app_key"
            # Don't set DATADOG_SITE to test default
            
            with patch('src.handler.DatadogClient') as mock_client:
                # Mock the client to avoid actual API calls
                mock_instance = Mock()
                mock_client.return_value = mock_instance
                mock_instance.get_dashboard.side_effect = Exception("API call made")
                
                result = lambda_handler(event, None)
                
                # Verify DatadogClient was called with default site
                mock_client.assert_called_once_with(
                    "test_api_key", 
                    "test_app_key", 
                    "datadoghq.com"
                )