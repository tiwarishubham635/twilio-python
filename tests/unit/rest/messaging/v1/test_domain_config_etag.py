import unittest
from unittest.mock import Mock

from twilio.rest.messaging.v1.domain_config import DomainConfigInstance, DomainConfigContext
from twilio.base.version import Version
from twilio.http.response import Response


class DomainConfigETagTest(unittest.TestCase):
    def setUp(self):
        self.version = Mock(spec=Version)

    def test_domain_config_instance_with_etag(self):
        """Test that DomainConfigInstance can store and access ETag from response headers"""
        headers = {"ETag": '"domain-config-etag"', "Content-Type": "application/json"}
        payload = {"domain_sid": "DM123", "config_sid": "CK456"}
        
        instance = DomainConfigInstance(self.version, payload, domain_sid="DM123", headers=headers)
        
        self.assertEqual(instance.etag, '"domain-config-etag"')
        self.assertEqual(instance.domain_sid, "DM123")
        self.assertEqual(instance.config_sid, "CK456")

    def test_domain_config_context_fetch_with_etag(self):
        """Test that DomainConfigContext fetch method preserves ETag from response"""
        # Setup mock response
        payload = {"domain_sid": "DM123", "config_sid": "CK456"}
        headers = {"ETag": '"fetched-etag"', "Content-Type": "application/json"}
        
        # Configure the mock to return the expected tuple
        self.version.fetch_with_headers.return_value = (payload, headers)
        
        # Create context and fetch
        context = DomainConfigContext(self.version, domain_sid="DM123")
        instance = context.fetch()
        
        # Verify fetch was called with correct parameters
        self.version.fetch_with_headers.assert_called_once()
        
        # Verify instance has ETag
        self.assertEqual(instance.etag, '"fetched-etag"')

    def test_domain_config_context_update_with_etag(self):
        """Test that DomainConfigContext update method preserves ETag from response"""
        # Setup mock response
        payload = {"domain_sid": "DM123", "config_sid": "CK456", "fallback_url": "https://example.com"}
        headers = {"ETag": '"updated-etag"', "Content-Type": "application/json"}
        
        # Configure the mock to return the expected tuple
        self.version.update_with_headers.return_value = (payload, headers)
        
        # Create context and update
        context = DomainConfigContext(self.version, domain_sid="DM123")
        instance = context.update(fallback_url="https://example.com")
        
        # Verify update was called with correct parameters
        self.version.update_with_headers.assert_called_once()
        
        # Verify instance has ETag
        self.assertEqual(instance.etag, '"updated-etag"')

    def test_domain_config_instance_no_etag(self):
        """Test that DomainConfigInstance handles absence of ETag gracefully"""
        headers = {"Content-Type": "application/json"}
        payload = {"domain_sid": "DM123", "config_sid": "CK456"}
        
        instance = DomainConfigInstance(self.version, payload, domain_sid="DM123", headers=headers)
        
        self.assertIsNone(instance.etag)

if __name__ == "__main__":
    unittest.main()