"""
Twilio Testing Utilities

This module provides utilities for testing applications that use Twilio services
without making actual HTTP requests to the Twilio API.
"""

from .fake_client import FakeTwilioClient

__all__ = ["FakeTwilioClient"]