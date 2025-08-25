from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from twilio.base.version import Version


class TokenManager:

    def fetch_access_token(self) -> str:
        raise NotImplementedError("Subclasses must implement this method")
