from abc import ABC, abstractmethod
from typing import Optional

from twilio.base.version import Version


class TokenManager(ABC):

    @abstractmethod
    def fetch_access_token(self, version: Optional[Version] = None) -> str:
        """Fetch an access token. The version parameter is optional for backward compatibility."""
        pass
