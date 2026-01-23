"""
DataStoreClient Exceptions

Custom exceptions for the datastore client.
"""


class DataStoreError(Exception):
    """Base exception for datastore client errors."""
    pass


class DataStoreConnectionError(DataStoreError):
    """Raised when connection to datastore service fails."""
    pass


class DataStoreTimeoutError(DataStoreError):
    """Raised when request to datastore service times out."""
    pass


class DataStoreAPIError(DataStoreError):
    """Raised when datastore service returns an error response."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class DataStoreNotFoundError(DataStoreError):
    """Raised when requested resource is not found."""
    pass


class DataStoreValidationError(DataStoreError):
    """Raised when request validation fails."""
    pass


class DataStoreCircuitBreakerError(DataStoreError):
    """Raised when circuit breaker is open."""
    pass
