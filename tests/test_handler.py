"""
Integration tests for Lambda handler.
"""
import json
import pytest
from unittest.mock import Mock, patch
from src.handler import lambda_handler


class TestLambdaHandler:
    """Test Lambda handler integration."""
    
    def test_lambda_handler_successful_redirect(self):
        """Test successful redirect flow."""
        # Mock API Gateway event
        event = {
            "pathParameters": {"dashboard_id": "abc-123"},
            "queryStringParameters": {"view": "Production"}
        }
        context = Mock()
        
        # Mock environment variables and DatadogClient
        with patch.dict('os.environ', {
            'DATADOG_API_KEY': 'test-api-key',
            'DATADOG_APP_KEY': 'test-app-key',
            'DATADOG_SITE': 'datadoghq.com'
        }):
            with patch('src.handler.DatadogClient') as mock_client:
                mock_instance = mock_client.return_value
                mock_instance.get_dashboard.return_value = {
                    "template_variable_presets": [
                        {
                            "name": "Production",
                            "template_variables": [{"name": "env", "value": "prod"}]
                        }
                    ]
                }
                
                response = lambda_handler(event, context)
                
                assert response["statusCode"] == 302
                assert "Location" in response["headers"]
                assert "abc-123" in response["headers"]["Location"]
    
    def test_lambda_handler_saved_view_not_found(self):
        """Test 404 when saved view doesn't exist."""
        event = {
            "pathParameters": {"dashboard_id": "abc-123"},
            "queryStringParameters": {"view": "NonExistent"}
        }
        context = Mock()
        
        with patch.dict('os.environ', {
            'DATADOG_API_KEY': 'test-api-key',
            'DATADOG_APP_KEY': 'test-app-key'
        }):
            with patch('src.handler.DatadogClient') as mock_client:
                mock_instance = mock_client.return_value
                mock_instance.get_dashboard.return_value = {
                    "template_variable_presets": [
                        {"name": "Production", "template_variables": []}
                    ]
                }
                
                response = lambda_handler(event, context)
                
                assert response["statusCode"] == 404
                assert "Saved view 'NonExistent' not found" in response["body"]
    
    def test_lambda_handler_missing_view_parameter(self):
        """Test handling missing view parameter."""
        event = {
            "pathParameters": {"dashboard_id": "abc-123"},
            "queryStringParameters": {}
        }
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 400
        assert "view parameter is required" in response["body"]
    
    def test_lambda_handler_datadog_api_error(self):
        """Test handling Datadog API errors."""
        event = {
            "pathParameters": {"dashboard_id": "abc-123"},
            "queryStringParameters": {"view": "Production"}
        }
        context = Mock()
        
        with patch.dict('os.environ', {
            'DATADOG_API_KEY': 'test-api-key',
            'DATADOG_APP_KEY': 'test-app-key'
        }):
            with patch('src.handler.DatadogClient') as mock_client:
                mock_instance = mock_client.return_value
                mock_instance.get_dashboard.side_effect = Exception("API Error")
                
                response = lambda_handler(event, context)
                
                assert response["statusCode"] == 500
                assert "Internal server error" in response["body"]