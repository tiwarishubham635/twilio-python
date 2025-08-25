"""
Example application demonstrating how to use FakeTwilioClient for testing.

This example shows a simple notification service and how to test it effectively
using the fake Twilio client.
"""

# Example application code (what you would test)
class NotificationService:
    """A service for sending notifications via Twilio."""
    
    def __init__(self, twilio_client, default_from_number):
        self.client = twilio_client
        self.default_from = default_from_number
    
    def send_welcome_message(self, user_phone, user_name):
        """Send a welcome message to a new user."""
        try:
            message = self.client.messages.create(
                to=user_phone,
                from_=self.default_from,
                body=f"Welcome to our service, {user_name}! Thanks for signing up."
            )
            return {"success": True, "message_sid": message.sid}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_order_notification(self, user_phone, order_id, status):
        """Send an order status notification."""
        status_messages = {
            "confirmed": "Your order #{order_id} has been confirmed!",
            "shipped": "Your order #{order_id} has shipped and is on its way!",
            "delivered": "Your order #{order_id} has been delivered. Enjoy!"
        }
        
        body = status_messages.get(status, f"Order #{order_id} status: {status}")
        body = body.format(order_id=order_id)
        
        try:
            message = self.client.messages.create(
                to=user_phone,
                from_=self.default_from,
                body=body
            )
            return {"success": True, "message_sid": message.sid}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_bulk_announcement(self, phone_numbers, announcement):
        """Send an announcement to multiple users."""
        results = []
        
        for phone in phone_numbers:
            try:
                message = self.client.messages.create(
                    to=phone,
                    from_=self.default_from,
                    body=announcement
                )
                results.append({
                    "phone": phone,
                    "success": True,
                    "message_sid": message.sid
                })
            except Exception as e:
                results.append({
                    "phone": phone,
                    "success": False,
                    "error": str(e)
                })
        
        return results


# Test code demonstrating FakeTwilioClient usage
import unittest
from twilio.testing import FakeTwilioClient


class TestNotificationService(unittest.TestCase):
    """Test the NotificationService using FakeTwilioClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fake_client = FakeTwilioClient()
        self.service = NotificationService(
            twilio_client=self.fake_client,
            default_from_number="+15559876543"
        )
    
    def test_send_welcome_message_success(self):
        """Test successful welcome message sending."""
        result = self.service.send_welcome_message("+15551234567", "Alice")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["message_sid"], "SMtest123456789")
        
        # Verify the correct API call was made
        self.fake_client.assert_called_with(
            "messages.create",
            To="+15551234567",
            From="+15559876543",
            Body="Welcome to our service, Alice! Thanks for signing up."
        )
    
    def test_send_welcome_message_with_invalid_phone(self):
        """Test welcome message with invalid phone number."""
        # Configure the fake client to simulate an error
        self.fake_client.configure_response("messages.create", {
            "sid": "SMerror123",
            "status": "failed",
            "error_code": 21211,
            "error_message": "Invalid phone number format"
        })
        
        # The service should handle the error gracefully
        result = self.service.send_welcome_message("invalid-phone", "Bob")
        
        # In this example, the service doesn't actually validate the response
        # but in a real implementation, you might check message.status
        self.assertTrue(result["success"])  # Service returns success based on no exception
        
        # Verify the call was still made (with invalid phone)
        calls = self.fake_client.get_calls()
        self.assertEqual(len(calls), 1)
    
    def test_order_notification_confirmed(self):
        """Test order confirmation notification."""
        result = self.service.send_order_notification("+15551234567", "12345", "confirmed")
        
        self.assertTrue(result["success"])
        
        # Verify the message content
        self.fake_client.assert_called_with(
            "messages.create",
            To="+15551234567",
            From="+15559876543",
            Body="Your order #12345 has been confirmed!"
        )
    
    def test_order_notification_shipped(self):
        """Test order shipped notification."""
        result = self.service.send_order_notification("+15551234567", "67890", "shipped")
        
        self.assertTrue(result["success"])
        
        self.fake_client.assert_called_with(
            "messages.create",
            To="+15551234567",
            From="+15559876543",
            Body="Your order #67890 has shipped and is on its way!"
        )
    
    def test_order_notification_unknown_status(self):
        """Test order notification with unknown status."""
        result = self.service.send_order_notification("+15551234567", "99999", "processing")
        
        self.assertTrue(result["success"])
        
        self.fake_client.assert_called_with(
            "messages.create",
            To="+15551234567",
            From="+15559876543",
            Body="Order #99999 status: processing"
        )
    
    def test_bulk_announcement(self):
        """Test sending bulk announcements."""
        phone_numbers = ["+15551111111", "+15552222222", "+15553333333"]
        announcement = "Special offer: 50% off all items this weekend!"
        
        results = self.service.send_bulk_announcement(phone_numbers, announcement)
        
        # Verify all messages were successful
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result["success"])
        
        # Verify all calls were made
        calls = self.fake_client.get_calls()
        self.assertEqual(len(calls), 3)
        
        # Verify each call had the correct parameters
        for i, call in enumerate(calls):
            data = call.params.get("data", {})
            self.assertEqual(data["To"], phone_numbers[i])
            self.assertEqual(data["From"], "+15559876543")
            self.assertEqual(data["Body"], announcement)
    
    def test_bulk_announcement_with_mixed_results(self):
        """Test bulk announcement where some messages fail."""
        phone_numbers = ["+15551111111", "+15552222222", "+15553333333"]
        
        # Configure the fake client to simulate failure for the second call
        call_count = 0
        original_fake_request = self.fake_client._fake_request
        
        def mock_request_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Second call fails
                raise ValueError("Invalid phone number")
            return original_fake_request(*args, **kwargs)
        
        self.fake_client._fake_request = mock_request_with_failure
        self.fake_client.http_client.request = mock_request_with_failure
        
        results = self.service.send_bulk_announcement(
            phone_numbers, 
            "Test announcement"
        )
        
        # Verify mixed results
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0]["success"])   # First succeeds
        self.assertFalse(results[1]["success"])  # Second fails
        self.assertTrue(results[2]["success"])   # Third succeeds
        
        # Verify error message
        self.assertIn("Invalid phone number", results[1]["error"])
    
    def test_service_parameter_validation(self):
        """Test that the service catches parameter validation errors."""
        # This test shows how parameter validation helps catch bugs
        
        # Create a buggy version of the service that doesn't pass required parameters
        def buggy_send_message():
            # This should raise TypeError due to missing 'to' parameter
            return self.fake_client.messages.create(
                from_="+15559876543",
                body="Missing to parameter"
            )
        
        with self.assertRaises(TypeError):
            buggy_send_message()
    
    def tearDown(self):
        """Clean up after each test."""
        self.fake_client.clear_calls()


# Example of testing with dependency injection
class TestWithDependencyInjection(unittest.TestCase):
    """Example showing how to test with dependency injection patterns."""
    
    def create_service_with_fake_client(self):
        """Factory method to create service with fake client."""
        fake_client = FakeTwilioClient()
        service = NotificationService(fake_client, "+15559876543")
        return service, fake_client
    
    def test_welcome_workflow(self):
        """Test the complete welcome workflow."""
        service, fake_client = self.create_service_with_fake_client()
        
        # Simulate user registration workflow
        user_data = {
            "name": "John Doe",
            "phone": "+15551234567",
            "email": "john@example.com"
        }
        
        # Send welcome message
        result = service.send_welcome_message(
            user_data["phone"], 
            user_data["name"]
        )
        
        # Verify workflow completed successfully
        self.assertTrue(result["success"])
        
        # Verify the exact message content
        calls = fake_client.get_calls()
        self.assertEqual(len(calls), 1)
        
        call_data = calls[0].params.get("data", {})
        expected_body = f"Welcome to our service, {user_data['name']}! Thanks for signing up."
        self.assertEqual(call_data["Body"], expected_body)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)