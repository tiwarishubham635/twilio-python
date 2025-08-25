from typing import Optional
from twilio.auth_strategy.auth_type import AuthType


class CredentialProvider:
    def __init__(self, auth_type: AuthType) -> None:
        self._auth_type = auth_type

    @property
    def auth_type(self) -> AuthType:
        return self._auth_type

    def to_auth_strategy(self) -> "AuthStrategy":  # type: ignore
        raise NotImplementedError("Subclasses must implement this method")
