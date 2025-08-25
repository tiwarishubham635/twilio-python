from abc import ABC, abstractmethod
from twilio.auth_strategy.auth_type import AuthType
from twilio.auth_strategy.auth_strategy import AuthStrategy


class CredentialProvider(ABC):
    def __init__(self, auth_type: AuthType) -> None:
        self._auth_type = auth_type

    @property
    def auth_type(self) -> AuthType:
        return self._auth_type

    @abstractmethod
    def to_auth_strategy(self) -> AuthStrategy:
        """Convert this credential provider to an auth strategy."""
        pass
