from typing import Optional
from twilio.base.version import Version


class InstanceResource(object):
    def __init__(self, version: Version, headers: Optional[dict] = None):
        self._version = version
        self._headers = headers or {}
        
    @property
    def etag(self) -> Optional[str]:
        """
        Returns the ETag header value from the last HTTP response, if available.
        This can be used for optimistic concurrency control with if_match parameters.
        
        :returns: ETag value or None if not available
        """
        if self._headers:
            return self._headers.get('ETag') or self._headers.get('etag')
        return None
