import unittest
import aiounittest

from mock import AsyncMock, Mock
from twilio.http.response import Response
from twilio.rest import Client


class TestAuthenticationPatterns(unittest.TestCase):
    """Test different authentication patterns supported by Twilio Client"""

    def test_account_sid_auth_token_authentication(self):
        """Test Client initialization with Account SID and Auth Token"""
        account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        auth_token = "your_auth_token"
        
        client = Client(account_sid, auth_token)
        
        # Verify client properties are set correctly
        self.assertEqual(client.username, account_sid)
        self.assertEqual(client.password, auth_token)
        self.assertEqual(client.account_sid, account_sid)
        self.assertEqual(client.auth, (account_sid, auth_token))

    def test_api_key_authentication(self):
        """Test Client initialization with API Key, Secret, and Account SID"""
        api_key = "SKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        api_secret = "your_api_secret"
        account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        
        client = Client(api_key, api_secret, account_sid)
        
        # Verify client properties are set correctly for API key auth
        self.assertEqual(client.username, api_key)
        self.assertEqual(client.password, api_secret)
        self.assertEqual(client.account_sid, account_sid)
        self.assertEqual(client.auth, (api_key, api_secret))

    def test_api_key_authentication_pattern_documented_in_readme(self):
        """Test the exact pattern shown in README for API key authentication"""
        # This is the exact pattern from README.md
        api_key = "XXXXXXXXXXXXXXXXX"
        api_secret = "YYYYYYYYYYYYYYYYYY"
        account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        
        client = Client(api_key, api_secret, account_sid)
        
        # Verify this creates a valid client with correct auth setup
        self.assertIsNotNone(client)
        self.assertEqual(client.username, api_key)
        self.assertEqual(client.password, api_secret)
        self.assertEqual(client.account_sid, account_sid)
        
    def test_environment_variable_authentication(self):
        """Test Client initialization with environment variables"""
        import os
        
        # Save original values
        original_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        original_token = os.environ.get("TWILIO_AUTH_TOKEN")
        
        try:
            # Set test environment variables
            os.environ["TWILIO_ACCOUNT_SID"] = "ACTEST_ACCOUNT_SID"
            os.environ["TWILIO_AUTH_TOKEN"] = "test_auth_token"
            
            client = Client()
            
            # Verify environment variables are used
            self.assertEqual(client.username, "ACTEST_ACCOUNT_SID")
            self.assertEqual(client.password, "test_auth_token")
            self.assertEqual(client.account_sid, "ACTEST_ACCOUNT_SID")
            
        finally:
            # Restore original values
            if original_sid is not None:
                os.environ["TWILIO_ACCOUNT_SID"] = original_sid
            else:
                os.environ.pop("TWILIO_ACCOUNT_SID", None)
                
            if original_token is not None:
                os.environ["TWILIO_AUTH_TOKEN"] = original_token  
            else:
                os.environ.pop("TWILIO_AUTH_TOKEN", None)

    def test_api_key_request_includes_correct_auth(self):
        """Test that API key authentication includes correct auth in requests"""
        from twilio.http.http_client import TwilioHttpClient
        
        # Mock HTTP client to capture requests
        mock_http_client = Mock(spec=TwilioHttpClient)
        mock_http_client.request.return_value = Response(200, '{"sid": "test"}')
        
        api_key = "SKTEST_API_KEY"
        api_secret = "test_api_secret"
        account_sid = "ACTEST_ACCOUNT_SID"
        
        client = Client(api_key, api_secret, account_sid, http_client=mock_http_client)
        
        # Make a request
        client.request("GET", "https://api.twilio.com/test")
        
        # Verify the auth tuple was passed correctly
        mock_http_client.request.assert_called_once()
        call_args = mock_http_client.request.call_args
        
        # Check that auth parameter contains the API key and secret
        self.assertEqual(call_args.kwargs.get('auth'), (api_key, api_secret))


class TestRegionEdgeClients(unittest.TestCase):
    def setUp(self):
        self.client = Client("username", "password")

    def test_set_client_edge_default_region(self):
        self.client.edge = "edge"
        self.assertEqual(
            self.client.get_hostname("https://api.twilio.com"),
            "https://api.edge.us1.twilio.com",
        )

    def test_set_client_region(self):
        self.client.region = "region"
        self.assertEqual(
            self.client.get_hostname("https://api.twilio.com"),
            "https://api.region.twilio.com",
        )

    def test_set_uri_region(self):
        self.assertEqual(
            self.client.get_hostname("https://api.region.twilio.com"),
            "https://api.region.twilio.com",
        )

    def test_set_client_edge_region(self):
        self.client.edge = "edge"
        self.client.region = "region"
        self.assertEqual(
            self.client.get_hostname("https://api.twilio.com"),
            "https://api.edge.region.twilio.com",
        )

    def test_set_client_edge_uri_region(self):
        self.client.edge = "edge"
        self.assertEqual(
            self.client.get_hostname("https://api.region.twilio.com"),
            "https://api.edge.region.twilio.com",
        )

    def test_set_client_region_uri_edge_region(self):
        self.client.region = "region"
        self.assertEqual(
            self.client.get_hostname("https://api.edge.uriRegion.twilio.com"),
            "https://api.edge.region.twilio.com",
        )

    def test_set_client_edge_uri_edge_region(self):
        self.client.edge = "edge"
        self.assertEqual(
            self.client.get_hostname("https://api.uriEdge.region.twilio.com"),
            "https://api.edge.region.twilio.com",
        )

    def test_set_uri_edge_region(self):
        self.assertEqual(
            self.client.get_hostname("https://api.edge.region.twilio.com"),
            "https://api.edge.region.twilio.com",
        )

    def test_periods_in_query(self):
        self.client.region = "region"
        self.client.edge = "edge"
        self.assertEqual(
            self.client.get_hostname(
                "https://api.twilio.com/path/to/something.json?foo=12.34"
            ),
            "https://api.edge.region.twilio.com/path/to/something.json?foo=12.34",
        )


class TestUserAgentClients(unittest.TestCase):
    def setUp(self):
        self.client = Client("username", "password")

    def tearDown(self):
        self.client.http_client.session.close()

    def test_set_default_user_agent(self):
        self.client.request("GET", "https://api.twilio.com/")
        request_header = self.client.http_client._test_only_last_request.headers[
            "User-Agent"
        ]
        self.assertRegex(
            request_header,
            r"^twilio-python\/[0-9.]+(-rc\.[0-9]+)?\s\(\w+\s\w+\)\sPython\/[^\s]+$",
        )

    def test_set_user_agent_extensions(self):
        expected_user_agent_extensions = ["twilio-run/2.0.0-test", "flex-plugin/3.4.0"]
        self.client.user_agent_extensions = expected_user_agent_extensions
        self.client.request("GET", "https://api.twilio.com/")
        user_agent_headers = self.client.http_client._test_only_last_request.headers[
            "User-Agent"
        ]
        user_agent_extensions = user_agent_headers.split(" ")[
            -len(expected_user_agent_extensions) :
        ]
        self.assertEqual(user_agent_extensions, expected_user_agent_extensions)


class TestClientAsyncRequest(aiounittest.AsyncTestCase):
    def setUp(self):
        self.mock_async_http_client = AsyncMock()
        self.mock_async_http_client.request.return_value = Response(200, "test")
        self.mock_async_http_client.is_async = True
        self.client = Client(
            "username", "password", http_client=self.mock_async_http_client
        )

    async def test_raise_error_if_client_not_marked_async(self):
        mock_http_client = Mock()
        mock_http_client.request.return_value = Response(200, "doesnt matter")
        mock_http_client.is_async = None

        client = Client("username", "password", http_client=mock_http_client)
        with self.assertRaises(RuntimeError):
            await client.request_async("doesnt matter", "doesnt matter")

    async def test_raise_error_if_client_is_not_async(self):
        mock_http_client = Mock()
        mock_http_client.request.return_value = Response(200, "doesnt matter")
        mock_http_client.is_async = False

        client = Client("username", "password", http_client=mock_http_client)
        with self.assertRaises(RuntimeError):
            await client.request_async("doesnt matter", "doesnt matter")

    async def test_request_async_called_with_method_and_url(self):
        await self.client.request_async("GET", "http://mock.twilio.com")
        self.assertEqual(self.mock_async_http_client.request.call_args.args[0], "GET")
        self.assertEqual(
            self.mock_async_http_client.request.call_args.args[1],
            "http://mock.twilio.com",
        )
