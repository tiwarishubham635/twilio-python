# Testing Your Twilio Integration

The Twilio Python library includes a `FakeTwilioClient` for testing applications that use Twilio services without making actual API calls.

## Quick Start

```python
from twilio.testing import FakeTwilioClient

# Replace your real client with the fake client in tests
fake_client = FakeTwilioClient()

# Use it exactly like the real client
message = fake_client.messages.create(
    to="+15551234567",
    from_="+15559876543", 
    body="Hello from test!"
)

# Verify the result
assert message.status == "sent"
assert message.body == "Hello from test!"

# Verify the API call was made
calls = fake_client.get_calls()
assert len(calls) == 1
```

## Benefits

✅ **Parameter validation** - Catches invalid parameters or function names  
✅ **No network calls** - Tests run fast and don't depend on internet connectivity  
✅ **Configurable responses** - Test different scenarios (success, failure, etc.)  
✅ **Call verification** - Verify your code makes the expected API calls  
✅ **Drop-in replacement** - Works exactly like the real client  

## Key Features

### Parameter Validation
```python
# This catches bugs in your test code
fake_client.messages.create(
    from_="+15559876543",
    body="Missing 'to' parameter"  # Raises TypeError
)
```

### Custom Responses
```python
# Test error scenarios
fake_client.configure_response("messages.create", {
    "sid": "SM123456789",
    "status": "failed", 
    "error_code": 21211,
    "error_message": "Invalid phone number"
})
```

### Call Verification  
```python
# Verify exact parameters were used
fake_client.assert_called_with("messages.create",
    To="+15551234567",
    From="+15559876543",
    Body="Expected message content"
)
```

## Documentation

- **Full Documentation**: [docs/testing.md](docs/testing.md)
- **Complete Example**: [examples/testing_example.py](examples/testing_example.py)

## Migration from Other Testing Approaches

**Before (with mocking):**
```python
@patch('twilio.rest.Client')
def test_send_message(self, mock_client):
    mock_instance = mock_client.return_value
    mock_instance.messages.create.return_value = Mock(sid="SM123")
    # Test doesn't validate parameters
```

**After (with FakeTwilioClient):**
```python
def test_send_message(self):
    fake_client = FakeTwilioClient()
    # Parameters are validated, responses are configurable
```

The fake client provides better test coverage while being easier to use than traditional mocking approaches.