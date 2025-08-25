# Twilio Testing Utilities

This document provides examples and guidance for using Twilio's testing utilities to write better tests for applications that use Twilio services.

## Overview

Testing applications that use Twilio services has traditionally been challenging. The common approaches have significant drawbacks:

- **Mocking the entire client** fails to catch problems with invalid parameters or function names
- **Using localhost/mock servers** requires reverse-engineering the Twilio protocol
- **Mocking HTTP requests with `responses`** is brittle and breaks when the client changes
- **Using test credentials** makes tests non-hermetic, slow, and dependent on network connectivity

The `FakeTwilioClient` solves these problems by providing a fake client that:
- ✅ Validates parameters like the real client
- ✅ Returns configurable fake responses
- ✅ Doesn't require network calls
- ✅ Tracks calls for verification in tests
- ✅ Works as a drop-in replacement for the real client

## Quick Start

```python
from twilio.testing import FakeTwilioClient

# Create a fake client
fake_client = FakeTwilioClient()

# Use it just like the real client
message = fake_client.messages.create(
    to="+15551234567",
    from_="+15559876543",
    body="Hello from test!"
)

# Verify the result
assert message.status == "sent"
assert message.body == "Hello from test!"

# Verify the call was made
calls = fake_client.get_calls()
assert len(calls) == 1
assert calls[0].resource == "messages.create"
```

## Basic Usage

### 1. Replace Real Client with Fake Client

```python
import unittest
from twilio.testing import FakeTwilioClient

class TestMyTwilioApp(unittest.TestCase):
    def setUp(self):
        # Use fake client instead of real one
        self.client = FakeTwilioClient()
    
    def test_send_notification(self):
        # Your application code here
        message = self.client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Your order is ready!"
        )
        
        # Assertions work the same way
        self.assertEqual(message.to, "+15551234567")
        self.assertEqual(message.status, "sent")
```

### 2. Parameter Validation

The fake client validates parameters just like the real client:

```python
def test_parameter_validation(self):
    fake_client = FakeTwilioClient()
    
    # Missing required 'to' parameter - raises TypeError
    with self.assertRaises(TypeError):
        fake_client.messages.create(
            from_="+15559876543",
            body="Missing 'to' parameter"
        )
    
    # Missing both 'from' and 'messaging_service_sid' - raises ValueError
    with self.assertRaises(ValueError):
        fake_client.messages.create(
            to="+15551234567",
            body="Missing sender"
        )
    
    # Missing message content - raises ValueError  
    with self.assertRaises(ValueError):
        fake_client.messages.create(
            to="+15551234567",
            from_="+15559876543"
            # No body, media_url, or content_sid
        )
```

## Advanced Features

### 1. Custom Response Configuration

Configure specific responses for different test scenarios:

```python
def test_message_failure_scenario(self):
    fake_client = FakeTwilioClient()
    
    # Configure a failure response
    fake_client.configure_response("messages.create", {
        "sid": "SM123456789",
        "status": "failed",
        "error_code": 21211,
        "error_message": "Invalid phone number format"
    })
    
    message = fake_client.messages.create(
        to="invalid-number",
        from_="+15559876543",
        body="Test message"
    )
    
    # Verify error response
    assert message.status == "failed"
    assert message.error_code == 21211
    assert "Invalid phone number" in message.error_message
```

### 2. Call Tracking and Verification

Track and verify that your code makes the expected API calls:

```python
def test_welcome_workflow(self):
    fake_client = FakeTwilioClient()
    
    # Your application function
    def send_welcome_message(client, user_phone, user_name):
        return client.messages.create(
            to=user_phone,
            from_="+15559876543",
            body=f"Welcome to our service, {user_name}!"
        )
    
    # Call your function
    result = send_welcome_message(fake_client, "+15551234567", "Alice")
    
    # Verify the exact parameters were used
    fake_client.assert_called_with(
        "messages.create",
        To="+15551234567",
        From="+15559876543",
        Body="Welcome to our service, Alice!"
    )
    
    # Verify the result
    assert result.body == "Welcome to our service, Alice!"
```

### 3. Multiple Calls and Call Filtering

```python
def test_bulk_messaging(self):
    fake_client = FakeTwilioClient()
    
    # Send multiple messages
    numbers = ["+15551111111", "+15552222222", "+15553333333"]
    for number in numbers:
        fake_client.messages.create(
            to=number,
            from_="+15559876543",
            body="Bulk message"
        )
    
    # Verify all calls were made
    calls = fake_client.get_calls()
    assert len(calls) == 3
    
    # Filter calls by resource type
    message_calls = fake_client.get_calls_by_resource("messages.create")
    assert len(message_calls) == 3
    
    # Verify specific calls
    for i, call in enumerate(message_calls):
        data = call.params.get("data", {})
        assert data["To"] == numbers[i]
        assert data["Body"] == "Bulk message"
```

### 4. Cleaning Up Between Tests

```python
class TestTwilioIntegration(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeTwilioClient()
    
    def tearDown(self):
        # Clear call history between tests
        self.fake_client.clear_calls()
    
    def test_first_feature(self):
        # Test code here
        pass
    
    def test_second_feature(self):
        # Starts with clean call history
        pass
```

## Configuration Options

### Custom Account Details

```python
# Use custom account SID and auth token
fake_client = FakeTwilioClient(
    account_sid="AC1234567890",
    auth_token="custom_token"
)
```

### Response Templates

You can set up reusable response templates:

```python
class TestSMSService(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeTwilioClient()
        
        # Set up common response scenarios
        self.setup_responses()
    
    def setup_responses(self):
        # Success scenario
        self.fake_client.configure_response("messages.create", {
            "sid": "SMsuccess123",
            "status": "sent",
            "to": "+15551234567",
            "from": "+15559876543"
        })
    
    def test_successful_message(self):
        message = self.fake_client.messages.create(
            to="+15551234567",
            from_="+15559876543",
            body="Test"
        )
        
        assert message.sid == "SMsuccess123"
        assert message.status == "sent"
```

## Integration with Testing Frameworks

### pytest

```python
import pytest
from twilio.testing import FakeTwilioClient

@pytest.fixture
def twilio_client():
    return FakeTwilioClient()

def test_notification_service(twilio_client):
    # Use the fixture
    message = twilio_client.messages.create(
        to="+15551234567",
        from_="+15559876543",
        body="pytest test"
    )
    
    assert message.status == "sent"
```

### Django

```python
# In your Django test
from django.test import TestCase
from twilio.testing import FakeTwilioClient
from unittest.mock import patch

class TestNotificationViews(TestCase):
    @patch('myapp.services.get_twilio_client')
    def test_send_notification_view(self, mock_get_client):
        # Replace the real client with fake client
        fake_client = FakeTwilioClient()
        mock_get_client.return_value = fake_client
        
        # Make request to your view
        response = self.client.post('/send-notification/', {
            'phone': '+15551234567',
            'message': 'Test notification'
        })
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify Twilio call was made
        calls = fake_client.get_calls()
        self.assertEqual(len(calls), 1)
```

## Best Practices

1. **Use dependency injection**: Make your Twilio client configurable so you can easily substitute the fake client in tests.

2. **Test both success and failure scenarios**: Use `configure_response()` to test how your application handles Twilio errors.

3. **Verify parameters, not just responses**: Use `assert_called_with()` to ensure your code passes the correct parameters to Twilio.

4. **Keep test data realistic**: Use realistic phone numbers, message content, and SIDs in your tests.

5. **Clean up between tests**: Use `clear_calls()` to start each test with a clean state.

## Migration from Other Testing Approaches

### From Mock/Patch

Before:
```python
@patch('twilio.rest.Client')
def test_send_message(self, mock_client):
    mock_instance = mock_client.return_value
    mock_instance.messages.create.return_value = Mock(sid="SM123")
    
    # Test code
```

After:
```python
def test_send_message(self):
    fake_client = FakeTwilioClient()
    # Test code - no mocking needed
```

### From responses Library

Before:
```python
import responses

@responses.activate
def test_send_message(self):
    responses.add(
        responses.POST,
        "https://api.twilio.com/2010-04-01/Accounts/AC123/Messages.json",
        json={"sid": "SM123", "status": "sent"}
    )
    # Test code
```

After:
```python
def test_send_message(self):
    fake_client = FakeTwilioClient()
    # Works at the client level, no HTTP mocking needed
```

## Troubleshooting

### Common Issues

1. **"AttributeError: 'FakeTwilioClient' object has no attribute 'messages'"**
   - Make sure you're importing from `twilio.testing`, not creating your own fake client

2. **"TypeError: missing required positional argument"**
   - This is expected! The fake client validates parameters just like the real client

3. **"No calls made to messages.create"** 
   - Check that your test actually calls the Twilio client
   - Make sure you're checking the right resource type

### Getting Help

If you encounter issues with the testing utilities:

1. Check that you're using the latest version of the Twilio Python library
2. Verify your test setup matches the examples in this documentation
3. Use `fake_client.get_calls()` to debug what calls are actually being made
4. Check the call parameters with `call.params` to verify the expected data

## Limitations

The fake client currently supports:
- Message creation (`messages.create`)
- Basic call creation (`calls.create`)

Additional Twilio services and operations will be added in future versions. For unsupported operations, the fake client will still track calls but may return generic responses.