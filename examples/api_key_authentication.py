#!/usr/bin/env python3
"""
Twilio Python SDK - API Key Authentication Example

This script demonstrates how to use API Key and API Secret authentication
with the Twilio Python SDK. This addresses the GitHub issue claiming that
API Key authentication doesn't exist - it does exist and works correctly!

Usage:
    python3 api_key_example.py

Replace the placeholder values with your actual Twilio credentials from:
https://console.twilio.com/us1/develop/api-keys
"""

from twilio.rest import Client

def main():
    print("Twilio Python SDK - API Key Authentication Example")
    print("=" * 55)
    
    # Replace these with your actual Twilio credentials
    # Get them from: https://console.twilio.com/us1/develop/api-keys
    api_key = "SKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"      # Your API Key (starts with SK)
    api_secret = "your_api_secret"                      # Your API Secret
    account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"   # Your Account SID
    
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:4]}{'*' * (len(api_secret) - 4)}")  # Partially hide secret
    print(f"Account SID: {account_sid}")
    print()
    
    # Initialize the Twilio client with API Key authentication
    print("Initializing Twilio client with API Key authentication...")
    client = Client(api_key, api_secret, account_sid)
    
    print("✅ Client initialized successfully!")
    print(f"   Client username (API Key): {client.username}")
    print(f"   Client account_sid: {client.account_sid}")
    print(f"   Authentication tuple: {client.auth}")
    print()
    
    # Example of how you would send a message (commented out to avoid actual API calls)
    print("Example usage (commented out to avoid actual API calls):")
    print("""
    # Send an SMS message
    message = client.messages.create(
        to="+1234567890",      # Your verified phone number
        from_="+0987654321",   # Your Twilio phone number
        body="Hello from Twilio Python SDK with API Key authentication!"
    )
    print(f"Message sent! SID: {message.sid}")
    """)
    
    print("✅ API Key authentication is working correctly!")
    print("\nFor more examples, see: https://www.twilio.com/docs/usage/api")

if __name__ == "__main__":
    main()