"""
Unit tests for utility functions.
"""
import pytest
from src.utils import build_redirect_url, find_saved_view

pytestmark = pytest.mark.unit


class TestBuildRedirectUrl:
    """Test URL building functionality."""

    def test_build_simple_redirect_url(self):
        """Test building URL with single template variable."""
        dashboard_id = "abc-123"
        template_variables = [
            {"name": "env", "value": "prod"}
        ]

        expected_url = "https://datadoghq.com/dashboard/abc-123?tpl_var_env=prod"
        actual_url = build_redirect_url(dashboard_id, template_variables)

        assert actual_url == expected_url

    def test_build_redirect_url_multiple_variables(self):
        """Test building URL with multiple template variables."""
        dashboard_id = "xyz-456"
        template_variables = [
            {"name": "env", "value": "prod"},
            {"name": "region", "value": "us-east-1"}
        ]

        expected_url = (
            "https://datadoghq.com/dashboard/xyz-456?"
            "tpl_var_env=prod&tpl_var_region=us-east-1"
        )
        actual_url = build_redirect_url(dashboard_id, template_variables)

        assert actual_url == expected_url

    def test_build_redirect_url_custom_site(self):
        """Test building URL with custom Datadog site."""
        dashboard_id = "abc-123"
        template_variables = [{"name": "env", "value": "staging"}]
        site = "datadoghq.eu"

        expected_url = "https://datadoghq.eu/dashboard/abc-123?tpl_var_env=staging"
        actual_url = build_redirect_url(dashboard_id, template_variables, site)

        assert actual_url == expected_url


class TestFindSavedView:
    """Test saved view lookup functionality."""

    def test_find_existing_saved_view(self):
        """Test finding an existing saved view."""
        dashboard_data = {
            "template_variable_presets": [
                {
                    "name": "Production",
                    "template_variables": [
                        {"name": "env", "value": "prod"}
                    ]
                },
                {
                    "name": "Staging",
                    "template_variables": [
                        {"name": "env", "value": "staging"}
                    ]
                }
            ]
        }

        result = find_saved_view(dashboard_data, "Production")

        assert result["name"] == "Production"
        assert result["template_variables"][0]["value"] == "prod"

    def test_find_saved_view_case_sensitive(self):
        """Test that saved view lookup is case sensitive."""
        dashboard_data = {
            "template_variable_presets": [
                {
                    "name": "Production",
                    "template_variables": [{"name": "env", "value": "prod"}]
                }
            ]
        }

        with pytest.raises(KeyError):
            find_saved_view(dashboard_data, "production")  # lowercase should fail

    def test_find_nonexistent_saved_view(self):
        """Test error when saved view doesn't exist."""
        dashboard_data = {
            "template_variable_presets": [
                {
                    "name": "Production",
                    "template_variables": [{"name": "env", "value": "prod"}]
                }
            ]
        }

        with pytest.raises(KeyError):
            find_saved_view(dashboard_data, "Development")
