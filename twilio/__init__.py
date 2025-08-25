__version_info__ = ("9", "7", "1")
__version__ = ".".join(__version_info__)

# Import commonly used classes and functions
from twilio.rest import Client
from twilio.request_validator import RequestValidator  
from twilio.base.exceptions import TwilioException, TwilioRestException

# Import testing utilities for convenience
try:
    from twilio.testing import FakeTwilioClient
    __all__ = [
        "__version__", 
        "__version_info__",
        "Client", 
        "RequestValidator", 
        "TwilioException", 
        "TwilioRestException",
        "FakeTwilioClient"
    ]
except ImportError:
    # Testing utilities are optional  
    __all__ = [
        "__version__", 
        "__version_info__",
        "Client", 
        "RequestValidator", 
        "TwilioException", 
        "TwilioRestException"
    ]
