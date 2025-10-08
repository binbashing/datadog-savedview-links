"""
Shared pytest fixtures and configuration.
"""
import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables for all tests."""
    # Ensure we have test environment variables set
    test_env = {
        "DATADOG_API_KEY": "test_api_key",
        "DATADOG_APP_KEY": "test_app_key", 
        "DATADOG_SITE": "datadoghq.com",
        "LOG_LEVEL": "INFO"
    }
    
    for key, value in test_env.items():
        if key not in os.environ:
            os.environ[key] = value