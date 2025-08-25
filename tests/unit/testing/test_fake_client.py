"""
Test cases for the FakeTwilioClient testing utility.
"""

import unittest
from twilio.testing import FakeTwilioClient


class TestFakeTwilioClient(unittest.TestCase):
    """Test the FakeTwilioClient functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = FakeTwilioClient()
    
    def test_basic_message_creation(self):
        """Test basic message creation with fake client."""
        # Create a message
        message = self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Hello, World!"
        )
        
        # Verify the response
        self.assertEqual(message.sid, "SMtest123456789")
        self.assertEqual(message.to, "+15551234567")
        self.assertEqual(message.from_, "+15559876543")
        self.assertEqual(message.body, "Hello, World!")
        self.assertEqual(message.status, "sent")
        
        # Verify call was logged
        calls = self.client.get_calls()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].resource, "messages.create")
    
    def test_parameter_validation_missing_to(self):
        """Test that missing 'to' parameter raises an error."""
        with self.assertRaises(TypeError) as context:
            self.client.messages.create(
                from_="+15559876543",
                body="Hello, World!"
            )
        self.assertIn("missing 1 required positional argument: 'to'", str(context.exception))
    
    def test_parameter_validation_missing_from_and_messaging_service(self):
        """Test that missing both 'from' and 'messaging_service_sid' raises an error."""
        with self.assertRaises(ValueError) as context:
            self.client.messages.create(
                to="+15551234567",
                body="Hello, World!"
            )
        self.assertIn("Either From or MessagingServiceSid must be provided", str(context.exception))
    
    def test_parameter_validation_missing_content(self):
        """Test that missing content (body, media, or content_sid) raises an error."""
        with self.assertRaises(ValueError) as context:
            self.client.messages.create(
                to="+15551234567",
                from_="+15559876543"
                # No body, media_url, or content_sid
            )
        self.assertIn("At least one of Body, MediaUrl, or ContentSid must be provided", str(context.exception))
    
    def test_custom_response_configuration(self):
        """Test configuring custom responses."""
        # Configure a custom response
        self.client.configure_response("messages.create", {
            "sid": "SMcustom123",
            "status": "failed",
            "error_code": 21211,
            "error_message": "Invalid phone number"
        })
        
        # Create a message
        message = self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Test message"
        )
        
        # Verify custom response was used
        self.assertEqual(message.sid, "SMcustom123")
        self.assertEqual(message.status, "failed")
        self.assertEqual(message.error_code, 21211)
        self.assertEqual(message.error_message, "Invalid phone number")
    
    def test_call_tracking(self):
        """Test that calls are properly tracked."""
        # Make multiple calls
        self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="First message"
        )
        
        self.client.messages.create(
            to="+15551111111",
            from_="+15559876543",
            body="Second message"
        )
        
        # Check call tracking
        calls = self.client.get_calls()
        self.assertEqual(len(calls), 2)
        
        # Check calls by resource type
        message_calls = self.client.get_calls_by_resource("messages.create")
        self.assertEqual(len(message_calls), 2)
        
        # Check that timestamps are set
        for call in calls:
            self.assertIsNotNone(call.timestamp)
    
    def test_assert_called_with_success(self):
        """Test successful assertion of call parameters."""
        self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Test message"
        )
        
        # This should not raise an error
        self.client.assert_called_with(
            "messages.create",
            To="+15551234567",
            From="+15559876543",
            Body="Test message"
        )
    
    def test_assert_called_with_failure(self):
        """Test failed assertion of call parameters."""
        self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Test message"
        )
        
        # This should raise an AssertionError
        with self.assertRaises(AssertionError):
            self.client.assert_called_with(
                "messages.create",
                To="+15551111111",  # Wrong number
                From="+15559876543",
                Body="Test message"
            )
    
    def test_assert_called_with_no_calls(self):
        """Test assertion when no calls were made."""
        with self.assertRaises(AssertionError) as context:
            self.client.assert_called_with("messages.create", To="+15551234567")
        
        self.assertIn("No calls made to messages.create", str(context.exception))
    
    def test_clear_calls(self):
        """Test clearing the call log."""
        # Make a call
        self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Test message"
        )
        
        # Verify call was logged
        self.assertEqual(len(self.client.get_calls()), 1)
        
        # Clear calls
        self.client.clear_calls()
        
        # Verify calls were cleared
        self.assertEqual(len(self.client.get_calls()), 0)
    
    def test_messaging_service_sid_instead_of_from(self):
        """Test using messaging service SID instead of from number."""
        message = self.client.messages.create(
            to="+15551234567",
            messaging_service_sid="MG123456789",
            body="Test message"
        )
        
        # Should work without error
        self.assertEqual(message.to, "+15551234567")
        self.assertEqual(message.messaging_service_sid, "MG123456789")
        self.assertEqual(message.body, "Test message")
    
    def test_response_includes_request_data(self):
        """Test that response includes data from the request."""
        message = self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Custom message body"
        )
        
        # Response should reflect the request parameters
        self.assertEqual(message.to, "+15551234567")
        self.assertEqual(message.from_, "+15559876543")
        self.assertEqual(message.body, "Custom message body")


class TestFakeTwilioClientUsageExamples(unittest.TestCase):
    """
    Example usage patterns for the FakeTwilioClient.
    
    These tests demonstrate how developers would use the fake client
    in their own test suites.
    """
    
    def test_example_basic_usage(self):
        """Example: Basic usage of the fake client."""
        # Create a fake client
        fake_client = FakeTwilioClient()
        
        # Use it just like the real client
        message = fake_client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Hello from test!"
        )
        
        # Assert expected behavior
        self.assertEqual(message.status, "sent")
        self.assertEqual(message.body, "Hello from test!")
        
        # Verify the call was made
        calls = fake_client.get_calls()
        self.assertEqual(len(calls), 1)
    
    def test_example_custom_responses(self):
        """Example: Configuring custom responses for different test scenarios."""
        fake_client = FakeTwilioClient()
        
        # Test successful message scenario
        fake_client.configure_response("messages.create", {
            "sid": "SM123",
            "status": "sent",
            "body": "Success!"
        })
        
        message = fake_client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Test"
        )
        
        self.assertEqual(message.status, "sent")
        self.assertEqual(message.sid, "SM123")
        
        # Test error scenario
        fake_client.configure_response("messages.create", {
            "sid": "SM456",
            "status": "failed",
            "error_code": 21211,
            "error_message": "Invalid phone number format"
        })
        
        message = fake_client.messages.create(
            to="invalid",
            from_="+15559876543",
            body="Test"
        )
        
        self.assertEqual(message.status, "failed")
        self.assertEqual(message.error_code, 21211)
    
    def test_example_parameter_validation(self):
        """Example: How parameter validation helps catch bugs in tests."""
        fake_client = FakeTwilioClient()
        
        # This would catch a bug where 'to' parameter is missing
        with self.assertRaises(TypeError):
            fake_client.messages.create(
                from_="+15559876543",
                body="Missing 'to' parameter"
            )
        
        # This would catch a bug where no content is provided
        with self.assertRaises(ValueError):
            fake_client.messages.create(
                to="+15551234567",
                from_="+15559876543"
                # Missing body, media_url, or content_sid
            )
    
    def test_example_call_verification(self):
        """Example: Verifying that your code made the expected API calls."""
        fake_client = FakeTwilioClient()
        
        # Simulate your application code
        def send_welcome_message(client, phone_number, name):
            return client.messages.create(
                to=phone_number,
                from_="+15559876543",
                body=f"Welcome, {name}!"
            )
        
        # Call your function with the fake client
        result = send_welcome_message(fake_client, "+15551234567", "Alice")
        
        # Verify the call was made with expected parameters
        fake_client.assert_called_with(
            "messages.create",
            To="+15551234567",
            From="+15559876543", 
            Body="Welcome, Alice!"
        )
        
        # Verify the result
        self.assertEqual(result.body, "Welcome, Alice!")


if __name__ == "__main__":
    unittest.main()