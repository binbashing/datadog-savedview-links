"""
Lambda handler for Datadog saved view redirects.
Entry point for AWS Lambda function.
"""
import logging
import os

# Handle imports for both Lambda environment and local testing
try:
    # Lambda environment - files are at root level
    from datadog_client import (
        DatadogClient, DatadogAPIError, DashboardNotFound,
        DatadogServerError, DatadogAuthError
    )
    from utils import find_saved_view, build_redirect_url
except ImportError:
    # Local environment - files are in src package
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
    Lambda handler for dashboard redirects.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        HTTP response dict
    """
    logger.info("Lambda handler started")
    
    try:
        # Validate environment variables
        _validate_environment()
        
        # Validate and extract parameters
        result = _validate_parameters(event)
        if len(result) == 3 and result[2] is not None:
            # Error case - return the error response
            return result[2]
        
        dashboard_id, view_name = result[0], result[1]
        
        # Initialize Datadog client
        site = os.getenv("DATADOG_SITE", "datadoghq.com")
        
        client = DatadogClient(
            api_key=os.getenv("DATADOG_API_KEY"),
            app_key=os.getenv("DATADOG_APP_KEY"),
            site=site
        )
        
        # Fetch dashboard configuration
        dashboard = client.get_dashboard(dashboard_id)
        
        # Find the saved view
        saved_view = find_saved_view(dashboard, view_name)
        
        # Extract template variables from saved view
        template_variables = saved_view.get('template_variables', [])
        
        # Build redirect URL
        redirect_url = build_redirect_url(dashboard_id, template_variables, site)
        
        return {
            "statusCode": 302,
            "headers": {
                "Location": redirect_url
            },
            "body": ""
        }
        
    except Exception as e:
        return _handle_exception(e, locals().get('view_name'))
