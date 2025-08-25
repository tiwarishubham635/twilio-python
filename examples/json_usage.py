"""
JSON Payload Usage Examples for Twilio Python SDK

This example demonstrates how to use JSON payloads with Twilio APIs.
Since version 9.0.0, the Twilio Python SDK supports application/json content type.
"""

import os
import json
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient


# Your Account SID and Auth Token from console.twilio.com
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "your_auth_token")


def example_json_with_custom_request():
    """
    Example: Using JSON payload with custom HTTP requests
    
    This shows how to make direct API calls with JSON payloads using
    the underlying HTTP client when you need more control.
    """
    print("=== JSON Payload with Custom HTTP Client ===")
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # Example: Custom API call with JSON payload
    # This is useful for beta APIs or special endpoints that require JSON
    json_payload = {
        "message": "Hello World",
        "priority": "high",
        "metadata": {
            "source": "python_sdk",
            "version": "9.0.0"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Note: This is a demonstration - replace with actual Twilio API endpoint
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/CustomResource.json"
    
    print(f"JSON Payload: {json.dumps(json_payload, indent=2)}")
    print(f"Headers: {headers}")
    print(f"URL: {url}")
    
    # Uncomment below to make actual request (requires valid endpoint):
    # try:
    #     response = client.http_client.request(
    #         method="POST",
    #         url=url,
    #         data=json_payload,
    #         headers=headers
    #     )
    #     print(f"Response: {response.status_code} - {response.text}")
    # except Exception as e:
    #     print(f"Request failed: {e}")


def example_conversations_api_json():
    """
    Example: Using JSON with Conversations API
    
    Some Twilio APIs, like Conversations, may benefit from JSON payloads
    for complex data structures.
    """
    print("\n=== JSON Payload with Conversations API ===")
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # Example: Creating a conversation with JSON metadata
    conversation_data = {
        "friendly_name": "Customer Support Chat",
        "attributes": json.dumps({
            "customer_id": "12345",
            "department": "technical_support",
            "priority": "high",
            "tags": ["bug_report", "urgent"]
        })
    }
    
    print(f"Conversation data: {json.dumps(conversation_data, indent=2)}")
    
    # Uncomment to create actual conversation:
    # try:
    #     conversation = client.conversations.v1.conversations.create(
    #         friendly_name=conversation_data["friendly_name"],
    #         attributes=conversation_data["attributes"]
    #     )
    #     print(f"Created conversation: {conversation.sid}")
    # except Exception as e:
    #     print(f"Failed to create conversation: {e}")


def example_webhook_with_json():
    """
    Example: Webhook configuration with JSON payload
    
    Shows how to configure webhooks that expect JSON responses.
    """
    print("\n=== Webhook Configuration with JSON ===")
    
    # Example webhook URL that expects JSON
    webhook_url = "https://your-app.example.com/webhook"
    
    # JSON payload for webhook configuration
    webhook_config = {
        "url": webhook_url,
        "method": "POST",
        "content_type": "application/json",
        "events": ["message-added", "participant-joined"]
    }
    
    print(f"Webhook configuration: {json.dumps(webhook_config, indent=2)}")
    
    # This would be used when configuring services that support JSON webhooks
    print("Use this configuration when setting up webhooks that need JSON format")


def example_bulk_operations_json():
    """
    Example: Bulk operations with JSON payload
    
    Demonstrates how JSON payloads can be useful for bulk operations
    or complex data structures.
    """
    print("\n=== Bulk Operations with JSON ===")
    
    # Example: Bulk message data
    bulk_messages = {
        "messages": [
            {
                "to": "+1234567890",
                "body": "Hello Alice!",
                "metadata": {"customer_id": "001"}
            },
            {
                "to": "+1987654321", 
                "body": "Hello Bob!",
                "metadata": {"customer_id": "002"}
            }
        ],
        "options": {
            "send_at": "2024-01-01T12:00:00Z",
            "callback_url": "https://example.com/status"
        }
    }
    
    print(f"Bulk operation payload: {json.dumps(bulk_messages, indent=2)}")
    
    # For actual bulk operations, you would typically iterate:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    print("\nProcessing messages individually:")
    for msg_data in bulk_messages["messages"]:
        print(f"Would send: {msg_data['body']} to {msg_data['to']}")
        # Uncomment to send actual messages:
        # try:
        #     message = client.messages.create(
        #         to=msg_data["to"],
        #         from_="+1234567890",  # Your Twilio number
        #         body=msg_data["body"]
        #     )
        #     print(f"Sent message: {message.sid}")
        # except Exception as e:
        #     print(f"Failed to send message: {e}")


async def example_async_json_requests():
    """
    Example: Asynchronous requests with JSON payload
    
    Shows how to use JSON payloads with async HTTP client.
    """
    print("\n=== Async JSON Requests ===")
    
    from twilio.http.async_http_client import AsyncTwilioHttpClient
    
    async_client = Client(
        ACCOUNT_SID, 
        AUTH_TOKEN,
        http_client=AsyncTwilioHttpClient()
    )
    
    # Example async operation with JSON
    json_data = {
        "async_operation": True,
        "data": {
            "priority": "high",
            "process_immediately": True
        }
    }
    
    print(f"Async JSON payload: {json.dumps(json_data, indent=2)}")
    
    # Uncomment for actual async operations:
    # try:
    #     # Example: async message creation
    #     message = await async_client.messages.create_async(
    #         to="+1234567890",
    #         from_="+1987654321",
    #         body="Async message with JSON context"
    #     )
    #     print(f"Async message sent: {message.sid}")
    # except Exception as e:
    #     print(f"Async operation failed: {e}")


def example_api_versioning_with_json():
    """
    Example: API versioning and JSON content negotiation
    
    Shows how to work with different API versions that may require JSON.
    """
    print("\n=== API Versioning with JSON ===")
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # Example: Using specific API version with JSON
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Twilio-API-Version": "2010-04-01"  # Specify API version
    }
    
    api_request = {
        "version": "2010-04-01",
        "features": ["json_support", "bulk_operations"],
        "client_info": {
            "sdk": "twilio-python",
            "version": "9.0.0+",
            "language": "python"
        }
    }
    
    print(f"API request with versioning: {json.dumps(api_request, indent=2)}")
    print(f"Headers: {json.dumps(headers, indent=2)}")


def main():
    """
    Run all JSON usage examples
    """
    print("Twilio Python SDK - JSON Payload Usage Examples")
    print("=" * 50)
    print()
    print("Note: These examples demonstrate JSON payload usage patterns.")
    print("Uncomment the actual API calls to test with your Twilio account.")
    print()
    
    # Run all examples
    example_json_with_custom_request()
    example_conversations_api_json()
    example_webhook_with_json()
    example_bulk_operations_json()
    
    # Note: async example would need to be run in async context
    print("\n=== Async Example (requires async context) ===")
    print("To run async examples, use: asyncio.run(example_async_json_requests())")
    
    example_api_versioning_with_json()
    
    print("\n" + "=" * 50)
    print("JSON Examples Complete!")
    print()
    print("Key points:")
    print("- Set Content-Type header to 'application/json' for JSON payloads")
    print("- Use json.dumps() to serialize Python dicts to JSON strings when needed")
    print("- The SDK automatically handles JSON when the correct headers are set")
    print("- JSON is useful for complex data, bulk operations, and modern APIs")


if __name__ == "__main__":
    main()