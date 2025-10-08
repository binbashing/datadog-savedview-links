"""
Lambda handler for Datadog saved view redirects.
Entry point for AWS Lambda function.
"""
import logging
import os
from src.datadog_client import (
    DatadogClient, DatadogAPIError, DashboardNotFound,
    DatadogServerError, DatadogAuthError
)
from src.utils import find_saved_view, build_redirect_url

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _validate_parameters(event):
    """Validate and extract parameters from API Gateway event."""
    path_params = event.get("pathParameters", {})
    query_params = event.get("queryStringParameters") or {}

    dashboard_id = path_params.get("dashboard_id")
    view_name = query_params.get("view")

    if not dashboard_id:
        logger.error("Missing dashboard_id parameter")
        return None, None, {
            'statusCode': 400,
            'body': 'dashboard_id parameter is required'
        }

    if not view_name:
        logger.error("Missing view parameter")
        return None, None, {
            'statusCode': 400,
            'body': 'view parameter is required'
        }

    return dashboard_id, view_name, None


def _validate_environment():
    """Validate required environment variables."""
    api_key = os.getenv('DATADOG_API_KEY')
    app_key = os.getenv('DATADOG_APP_KEY')
    site = os.getenv('DATADOG_SITE', 'datadoghq.com')

    if not api_key:
        logger.error("Missing DATADOG_API_KEY environment variable")
        return None, None, None, {
            'statusCode': 500,
            'body': 'DATADOG_API_KEY environment variable is required'
        }

    if not app_key:
        logger.error("Missing DATADOG_APP_KEY environment variable")
        return None, None, None, {
            'statusCode': 500,
            'body': 'DATADOG_APP_KEY environment variable is required'
        }

    return api_key, app_key, site, None


def _handle_exception(e, view_name=None):
    """Handle different exception types and return appropriate responses."""
    if isinstance(e, KeyError):
        logger.warning(f"Saved view not found: {e}")
        return {
            'statusCode': 404,
            'body': f'Saved view \'{view_name}\' not found'
        }
    elif isinstance(e, DashboardNotFound):
        logger.error(f"Dashboard not found: {e}")
        return {
            'statusCode': 404,
            'body': 'Dashboard not found'
        }
    elif isinstance(e, DatadogAuthError):
        logger.error(f"Datadog authentication error: {e}")
        return {
            'statusCode': 401,
            'body': 'Authentication failed'
        }
    elif isinstance(e, DatadogServerError):
        logger.error(f"Datadog server error: {e}")
        return {
            'statusCode': 502,
            'body': 'Upstream service error'
        }
    elif isinstance(e, DatadogAPIError):
        logger.error(f"Datadog API error: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }
    else:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler for dashboard redirect requests.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        HTTP response with redirect or error
    """
    logger.info("Processing dashboard redirect request")

    try:
        # Validate parameters
        dashboard_id, view_name, param_error = _validate_parameters(event)
        if param_error:
            return param_error

        # Validate environment
        api_key, app_key, site, env_error = _validate_environment()
        if env_error:
            return env_error

        # Process request
        client = DatadogClient(api_key, app_key, site)
        dashboard_data = client.get_dashboard(dashboard_id)
        saved_view = find_saved_view(dashboard_data, view_name)
        template_variables = saved_view.get("template_variables", [])
        redirect_url = build_redirect_url(dashboard_id, template_variables, site)

        logger.info(f"Redirecting to: {redirect_url}")
        return {
            'statusCode': 302,
            'headers': {'Location': redirect_url},
            'body': ''
        }

    except Exception as e:
        return _handle_exception(e, locals().get('view_name'))
