import unittest
from unittest.mock import Mock

from twilio.base.instance_resource import InstanceResource
from twilio.base.page import Page
from twilio.base.version import Version
from twilio.http.response import Response


class ETagSupportTest(unittest.TestCase):
    def setUp(self):
        self.version = Mock(spec=Version)

    def test_instance_resource_stores_headers(self):
        """Test that InstanceResource can store and access headers"""
        headers = {"ETag": '"test-etag-value"', "Content-Type": "application/json"}
        instance = InstanceResource(self.version, headers=headers)
        
        self.assertEqual(instance.etag, '"test-etag-value"')
        self.assertEqual(instance._headers, headers)

    def test_instance_resource_etag_case_insensitive(self):
        """Test that etag property handles case-insensitive headers"""
        headers = {"etag": '"lower-case-etag"'}
        instance = InstanceResource(self.version, headers=headers)
        
        self.assertEqual(instance.etag, '"lower-case-etag"')

    def test_instance_resource_no_etag(self):
        """Test that etag returns None when not present"""
        headers = {"Content-Type": "application/json"}
        instance = InstanceResource(self.version, headers=headers)
        
        self.assertIsNone(instance.etag)

    def test_instance_resource_no_headers(self):
        """Test that etag returns None when no headers provided"""
        instance = InstanceResource(self.version)
        
        self.assertIsNone(instance.etag)

    def test_page_stores_headers(self):
        """Test that Page objects store headers from Response"""
        response_headers = {"ETag": '"page-etag"', "Content-Type": "application/json"}
        response = Response(200, '{"key": []}', headers=response_headers)
        
        page = Page(self.version, response)
        
        self.assertEqual(page.headers, response_headers)

    def test_version_parse_fetch_with_headers(self):
        """Test that Version._parse_fetch_with_headers returns both payload and headers"""
        version = Version(Mock(), "v1")
        response_headers = {"ETag": '"resource-etag"'}
        response = Response(200, '{"test": "data"}', headers=response_headers)
        
        payload, headers = version._parse_fetch_with_headers("GET", "/test", response)
        
        self.assertEqual(payload, {"test": "data"})
        self.assertEqual(headers, response_headers)

    def test_version_parse_update_with_headers(self):
        """Test that Version._parse_update_with_headers returns both payload and headers"""
        version = Version(Mock(), "v1")
        response_headers = {"ETag": '"updated-etag"'}
        response = Response(200, '{"updated": "data"}', headers=response_headers)
        
        payload, headers = version._parse_update_with_headers("POST", "/test", response)
        
        self.assertEqual(payload, {"updated": "data"})
        self.assertEqual(headers, response_headers)

    def test_version_parse_create_with_headers(self):
        """Test that Version._parse_create_with_headers returns both payload and headers"""
        version = Version(Mock(), "v1")
        response_headers = {"ETag": '"created-etag"'}
        response = Response(201, '{"created": "data"}', headers=response_headers)
        
        payload, headers = version._parse_create_with_headers("POST", "/test", response)
        
        self.assertEqual(payload, {"created": "data"})
        self.assertEqual(headers, response_headers)


if __name__ == "__main__":
    unittest.main()