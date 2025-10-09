"""
Utility functions for URL building and data processing.
"""
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


def build_redirect_url(
        dashboard_id: str,
        template_variables: list,
        site: str = "datadoghq.com") -> str:
    """
    Build Datadog dashboard URL with template variables.

    Args:
        dashboard_id: Dashboard identifier
        template_variables: List of template variable dicts
        site: Datadog site domain

    Returns:
        Complete dashboard URL with query parameters
    """
    logger.info(f"Building redirect URL for dashboard {dashboard_id}")

    # Build base URL
    base_url = f"https://{site}/dashboard/{dashboard_id}"

    # Build query parameters from template variables
    query_params = {}
    for var in template_variables:
        param_name = f"tpl_var_{var['name']}"
        query_params[param_name] = var['value']

    # Construct final URL with query parameters
    if query_params:
        query_string = urlencode(query_params)
        return f"{base_url}?{query_string}"
    else:
        return base_url


def find_saved_view(dashboard_data: dict, view_name: str) -> dict:
    """
    Find saved view by name in dashboard configuration.

    Args:
        dashboard_data: Dashboard configuration from API
        view_name: Name of saved view to find

    Returns:
        Saved view configuration dict

    Raises:
        KeyError: If saved view not found
    """
    logger.info(f"Looking for saved view: {view_name}")

    # Get template variable presets from dashboard data
    presets = dashboard_data.get("template_variable_presets", [])

    # Search for the saved view by name (case-sensitive)
    for preset in presets:
        if preset.get("name") == view_name:
            logger.info(f"Found saved view: {view_name}")
            return preset

    # If not found, raise KeyError
    logger.warning(f"Saved view '{view_name}' not found")
    raise KeyError(f"Saved view '{view_name}' not found")
