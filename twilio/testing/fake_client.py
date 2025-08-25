"""
Fake Twilio Client for Testing

This module provides a fake Twilio client that can be used for testing
applications that use Twilio services. The fake client validates parameters
like the real client but returns configurable fake responses without making
actual HTTP requests.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock

from twilio.rest import Client
from twilio.base import values
from twilio.http.response import Response
from twilio.rest.api.v2010.account.message import MessageInstance


class FakeCall:
    """Represents a tracked API call made to the fake client."""
    
    def __init__(self, method: str, resource: str, params: Dict[str, Any]):
        self.method = method
        self.resource = resource
        self.params = params
        self.timestamp = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<FakeCall {self.method} {self.resource} at {self.timestamp}>"


class FakeTwilioClient(Client):
    """
    A fake Twilio client for testing.
    
    This client mimics the behavior of the real Twilio client but returns
    configurable fake responses instead of making actual HTTP requests.
    It validates parameters like the real client would, helping catch
    issues with invalid parameters or function names.
    
    Example usage:
        # Basic usage
        fake_client = FakeTwilioClient()
        message = fake_client.messages.create(
            to="+15551234567",
            from_="+15559876543", 
            body="Test message"
        )
        
        # Configure custom responses
        fake_client.configure_response("messages.create", {
            "sid": "SM123456789",
            "status": "sent",
            "body": "Custom response body"
        })
        
        # Verify calls were made
        calls = fake_client.get_calls()
        assert len(calls) == 1
        assert calls[0].resource == "messages.create"
    """
    
    def __init__(self, account_sid="ACtest123", auth_token="test_token", **kwargs):
        """
        Initialize the fake client.
        
        :param account_sid: Fake account SID (defaults to test value)
        :param auth_token: Fake auth token (defaults to test value)
        :param kwargs: Additional parameters passed to ClientBase
        """
        # Use a mock HTTP client that doesn't make actual requests
        mock_http_client = Mock()
        mock_http_client.is_async = False
        
        super().__init__(
            username=account_sid,
            password=auth_token,
            http_client=mock_http_client,
            **kwargs
        )
        
        self._call_log: List[FakeCall] = []
        self._response_configs: Dict[str, Dict[str, Any]] = {}
        self._default_responses: Dict[str, Dict[str, Any]] = self._get_default_responses()
        
        # Override the HTTP client request method to return fake responses
        self.http_client.request = self._fake_request
    
    def _get_default_responses(self) -> Dict[str, Dict[str, Any]]:
        """Get default fake responses for common Twilio API calls."""
        return {
            "messages.create": {
                "sid": "SMtest123456789",
                "account_sid": self.account_sid,
                "from": "+15551234567",
                "to": "+15559876543",
                "body": "Test message",
                "status": "sent",
                "direction": "outbound-api",
                "date_created": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "date_sent": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "date_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "price": "-0.0075",
                "price_unit": "USD",
                "error_code": None,
                "error_message": None,
                "uri": f"/2010-04-01/Accounts/{self.account_sid}/Messages/SMtest123456789.json",
                "api_version": "2010-04-01",
                "num_segments": "1",
                "num_media": "0",
                "messaging_service_sid": None,
                "subresource_uris": {
                    "media": f"/2010-04-01/Accounts/{self.account_sid}/Messages/SMtest123456789/Media.json",
                    "feedback": f"/2010-04-01/Accounts/{self.account_sid}/Messages/SMtest123456789/Feedback.json"
                }
            },
            "calls.create": {
                "sid": "CAtest123456789",
                "account_sid": self.account_sid,
                "from": "+15551234567",
                "to": "+15559876543",
                "status": "queued",
                "direction": "outbound-api",
                "date_created": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "date_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "price": None,
                "price_unit": "USD",
                "uri": f"/2010-04-01/Accounts/{self.account_sid}/Calls/CAtest123456789.json",
                "api_version": "2010-04-01"
            }
        }
    
    def _fake_request(self, method: str, uri: str, **kwargs) -> Response:
        """
        Handle fake HTTP requests by returning configured responses.
        
        This method is called instead of making actual HTTP requests.
        It validates the request parameters and returns appropriate fake responses.
        """
        # Log the call
        resource_type = self._extract_resource_type(uri, method)
        call = FakeCall(method, resource_type, kwargs)
        self._call_log.append(call)
        
        # Validate required parameters based on the resource type
        self._validate_request(resource_type, kwargs)
        
        # Get configured or default response
        response_data = self._get_response_data(resource_type, kwargs)
        
        # Return fake response
        return Response(200, json.dumps(response_data))
    
    def _extract_resource_type(self, uri: str, method: str) -> str:
        """Extract the resource type from the URI."""
        if "/Messages.json" in uri and method == "POST":
            return "messages.create"
        elif "/Calls.json" in uri and method == "POST":
            return "calls.create"
        elif "/Messages/" in uri and method == "GET":
            return "messages.fetch"
        elif "/Calls/" in uri and method == "GET":
            return "calls.fetch"
        else:
            return "unknown"
    
    def _validate_request(self, resource_type: str, params: Dict[str, Any]):
        """
        Validate request parameters like the real client would.
        
        This helps catch common mistakes in test code.
        """
        data = params.get("data", {})
        
        if resource_type == "messages.create":
            # Validate required parameters for message creation
            if not data.get("To"):
                raise ValueError("To parameter is required for message creation")
            
            # At least one of From, MessagingServiceSid must be provided
            if not data.get("From") and not data.get("MessagingServiceSid"):
                raise ValueError("Either From or MessagingServiceSid must be provided")
            
            # At least one of Body, MediaUrl, ContentSid must be provided
            if not data.get("Body") and not data.get("MediaUrl") and not data.get("ContentSid"):
                raise ValueError("At least one of Body, MediaUrl, or ContentSid must be provided")
        
        elif resource_type == "calls.create":
            # Validate required parameters for call creation
            if not data.get("To"):
                raise ValueError("To parameter is required for call creation")
            if not data.get("From"):
                raise ValueError("From parameter is required for call creation")
            if not data.get("Url") and not data.get("Twiml") and not data.get("ApplicationSid"):
                raise ValueError("Either Url, Twiml, or ApplicationSid must be provided")
    
    def _get_response_data(self, resource_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the response data for the given resource type and parameters."""
        # Use configured response if available
        if resource_type in self._response_configs:
            response = self._response_configs[resource_type].copy()
        else:
            # Use default response
            response = self._default_responses.get(resource_type, {}).copy()
        
        # Update response with data from request parameters if it's a create operation
        if resource_type.endswith(".create"):
            data = params.get("data", {})
            self._update_response_with_request_data(response, data)
        
        return response
    
    def _update_response_with_request_data(self, response: Dict[str, Any], request_data: Dict[str, Any]):
        """Update the response with data from the request."""
        # Map request parameters to response fields
        field_mappings = {
            "To": "to",
            "From": "from",
            "Body": "body",
            "MessagingServiceSid": "messaging_service_sid",
        }
        
        for request_field, response_field in field_mappings.items():
            if request_field in request_data and request_data[request_field] is not None:
                response[response_field] = request_data[request_field]
    
    def configure_response(self, resource_type: str, response_data: Dict[str, Any]):
        """
        Configure a custom response for a specific resource type.
        
        :param resource_type: The type of resource (e.g., "messages.create")
        :param response_data: The response data to return
        """
        self._response_configs[resource_type] = response_data
    
    def get_calls(self) -> List[FakeCall]:
        """
        Get all API calls that have been made to this fake client.
        
        :returns: List of FakeCall objects representing the calls made
        """
        return self._call_log.copy()
    
    def clear_calls(self):
        """Clear the call log."""
        self._call_log.clear()
    
    def get_calls_by_resource(self, resource_type: str) -> List[FakeCall]:
        """
        Get all calls made to a specific resource type.
        
        :param resource_type: The resource type to filter by
        :returns: List of FakeCall objects for the specified resource
        """
        return [call for call in self._call_log if call.resource == resource_type]
    
    def assert_called_with(self, resource_type: str, **expected_params):
        """
        Assert that a call was made with specific parameters.
        
        :param resource_type: The resource type that should have been called
        :param expected_params: Expected parameters in the call
        :raises AssertionError: If no matching call is found
        """
        calls = self.get_calls_by_resource(resource_type)
        if not calls:
            raise AssertionError(f"No calls made to {resource_type}")
        
        for call in calls:
            data = call.params.get("data", {})
            match = True
            for key, expected_value in expected_params.items():
                if data.get(key) != expected_value:
                    match = False
                    break
            if match:
                return  # Found a matching call
        
        raise AssertionError(
            f"No call to {resource_type} found with parameters {expected_params}. "
            f"Actual calls: {[call.params for call in calls]}"
        )