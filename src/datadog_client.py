"""
Datadog API client for fetching dashboard configuration.
"""
import logging
import requests

logger = logging.getLogger(__name__)


class DatadogAPIError(Exception):
    """Base exception for Datadog API errors."""
    pass


class DatadogClient:
    """Client for interacting with Datadog API v1."""

    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        """
        Initialize Datadog client.

        Args:
            api_key: Datadog API key
            app_key: Datadog application key
            site: Datadog site domain
        """
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.base_url = f"https://api.{site}"
        logger.info(f"DatadogClient initialized for site: {site}")

    def get_dashboard(self, dashboard_id: str) -> dict:
        """
        Fetch dashboard configuration from Datadog API.

        Args:
            dashboard_id: Dashboard identifier

        Returns:
            Dashboard configuration dict

        Raises:
            DatadogAPIError: If API request fails
        """
        logger.info(f"Fetching dashboard: {dashboard_id}")

        url = f"{self.base_url}/api/v1/dashboards/{dashboard_id}"
        headers = {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"Successfully fetched dashboard: {dashboard_id}")
                return response.json()
            elif response.status_code == 404:
                logger.error(f"Dashboard not found: {dashboard_id}")
                raise DatadogAPIError(f"Dashboard {dashboard_id} not found")
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                raise DatadogAPIError(
                    f"API request failed with status {
                        response.status_code}")

        except requests.RequestException as e:
            logger.error(f"Request failed for dashboard {dashboard_id}: {e}")
            raise DatadogAPIError(f"Request failed: {e}")
