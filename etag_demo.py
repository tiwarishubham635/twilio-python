#!/usr/bin/env python3
"""
ETag Support Demonstration

This script demonstrates how the new ETag support in the Twilio Python SDK
enables optimistic concurrency control for API resources.
"""

from unittest.mock import Mock
from twilio.rest.messaging.v1.domain_config import DomainConfigInstance, DomainConfigContext
from twilio.base.version import Version
from twilio.http.response import Response
from twilio.base.page import Page


def demonstrate_instance_etag():
    """Demonstrate ETag access on instance resources"""
    print("=== Instance Resource ETag Support ===")
    
    # Mock version object
    version = Mock(spec=Version)
    
    # Simulate response headers with ETag
    headers = {
        "ETag": '"W/test-etag-12345"',
        "Content-Type": "application/json",
        "Last-Modified": "Wed, 21 Oct 2023 07:28:00 GMT"
    }
    
    # Create instance with headers
    payload = {"domain_sid": "DM123", "config_sid": "CK456", "fallback_url": "https://example.com"}
    instance = DomainConfigInstance(version, payload, domain_sid="DM123", headers=headers)
    
    print(f"Instance SID: {instance.domain_sid}")
    print(f"ETag: {instance.etag}")
    print(f"Available for conditional updates: {instance.etag is not None}")
    print()


def demonstrate_page_headers():
    """Demonstrate header preservation in Page objects"""
    print("=== Page Header Support ===")
    
    version = Mock(spec=Version)
    
    # Simulate page response with headers
    response_headers = {
        "ETag": '"page-etag-67890"',
        "X-Total-Count": "42",
        "Content-Type": "application/json"
    }
    
    response_body = '{"domain_configs": [], "meta": {"page": 0, "page_size": 50, "key": "domain_configs"}}'
    response = Response(200, response_body, headers=response_headers)
    
    # Create page - headers are now preserved
    page = Page(version, response)
    
    print(f"Page headers available: {bool(page.headers)}")
    print(f"Page ETag: {page.headers.get('ETag')}")
    print(f"Total count: {page.headers.get('X-Total-Count')}")
    print()


def demonstrate_optimistic_concurrency():
    """Demonstrate how ETag enables optimistic concurrency control"""
    print("=== Optimistic Concurrency Control ===")
    
    version = Mock(spec=Version)
    
    # Step 1: Fetch resource and get ETag
    print("1. Fetching resource...")
    headers = {"ETag": '"original-etag"'}
    payload = {"domain_sid": "DM123", "config_sid": "CK456", "fallback_url": "https://old.com"}
    
    # Mock the fetch_with_headers method to return our test data
    version.fetch_with_headers.return_value = (payload, headers)
    
    context = DomainConfigContext(version, domain_sid="DM123")
    instance = context.fetch()
    
    print(f"   Got ETag: {instance.etag}")
    print(f"   Current fallback URL: {instance.fallback_url}")
    
    # Step 2: Prepare conditional update using ETag
    print("\n2. Preparing conditional update...")
    print(f"   Using ETag for if_match: {instance.etag}")
    print("   This ETag can now be used with update operations that support if_match")
    print("   to ensure the resource hasn't changed since last fetch.")
    
    # Step 3: Show how the updated resource would have new ETag
    print("\n3. After successful update...")
    new_headers = {"ETag": '"new-etag-after-update"'}
    new_payload = {"domain_sid": "DM123", "config_sid": "CK456", "fallback_url": "https://new.com"}
    
    version.update_with_headers.return_value = (new_payload, new_headers)
    updated_instance = context.update(fallback_url="https://new.com")
    
    print(f"   New ETag: {updated_instance.etag}")
    print(f"   Updated fallback URL: {updated_instance.fallback_url}")
    print()


def demonstrate_taskrouter_integration():
    """Show how this integrates with existing if_match support"""
    print("=== TaskRouter Integration Example ===")
    print("TaskRouter tasks already support if_match parameter.")
    print("With ETag support, you can now:")
    print()
    print("# Fetch a task and get its ETag")
    print("task = client.taskrouter.workspaces('WS123').tasks('TK456').fetch()")
    print("etag = task.etag  # Now available!")
    print()
    print("# Use ETag for conditional update to avoid conflicts")
    print("updated_task = task.update(")
    print("    if_match=etag,")
    print("    assignment_status='completed',")
    print("    reason='Customer request completed'")
    print(")")
    print()
    print("# The updated task will have a new ETag")
    print("new_etag = updated_task.etag")
    print()


if __name__ == "__main__":
    print("Twilio Python SDK - ETag Support Demonstration")
    print("=" * 50)
    print()
    
    demonstrate_instance_etag()
    demonstrate_page_headers()
    demonstrate_optimistic_concurrency()
    demonstrate_taskrouter_integration()
    
    print("Key Benefits:")
    print("- ETags are automatically captured from API responses")
    print("- Available on all Instance resources via the .etag property")
    print("- Compatible with existing if_match parameters")
    print("- Enables proper optimistic concurrency control")
    print("- Backward compatible - no breaking changes")