"""
Lambda handler for Datadog saved view redirects.
Entry point for AWS Lambda function.
"""
import logging
import os
from src.datadog_client import DatadogClient, DatadogAPIError
from src.utils import find_saved_view, build_redirect_url

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        # Extract parameters from API Gateway event
        path_params = event.get("pathParameters", {})
        query_params = event.get("queryStringParameters") or {}

        dashboard_id = path_params.get("dashboard_id")
        view_name = query_params.get("view")

        if not dashboard_id:
            logger.error("Missing dashboard_id parameter")
            return {
                'statusCode': 400,
                'body': 'dashboard_id parameter is required'
            }

        if not view_name:
            logger.error("Missing view parameter")
            return {
                'statusCode': 400,
                'body': 'view parameter is required'
            }

        # Initialize Datadog client
        api_key = os.getenv('DATADOG_API_KEY')
        app_key = os.getenv('DATADOG_APP_KEY')
        site = os.getenv('DATADOG_SITE', 'datadoghq.com')

        if not api_key or not app_key:
            logger.error("Missing Datadog API credentials")
            return {
                'statusCode': 500,
                'body': 'Internal server error'
            }

        client = DatadogClient(api_key, app_key, site)

        # Fetch dashboard data
        dashboard_data = client.get_dashboard(dashboard_id)

        # Find the saved view
        saved_view = find_saved_view(dashboard_data, view_name)

        # Build redirect URL
        template_variables = saved_view.get("template_variables", [])
        redirect_url = build_redirect_url(dashboard_id, template_variables, site)

        logger.info(f"Redirecting to: {redirect_url}")

        return {
            'statusCode': 302,
            'headers': {
                'Location': redirect_url
            },
            'body': ''
        }

    except KeyError as e:
        logger.warning(f"Saved view not found: {e}")
        return {
            'statusCode': 404,
            'body': f'Saved view \'{view_name}\' not found'
        }

    except DatadogAPIError as e:
        logger.error(f"Datadog API error: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }
