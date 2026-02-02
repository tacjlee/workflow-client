"""
KnowledgeClient Exceptions

Custom exceptions for the knowledge base client.
"""


class KnowledgeBaseError(Exception):
    """Base exception for knowledge base client errors."""
    pass


class KnowledgeBaseConnectionError(KnowledgeBaseError):
    """Raised when connection to knowledge base service fails."""
    pass


class KnowledgeBaseTimeoutError(KnowledgeBaseError):
    """Raised when request to knowledge base service times out."""
    pass


class KnowledgeBaseAPIError(KnowledgeBaseError):
    """Raised when knowledge base service returns an error response."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class KnowledgeBaseNotFoundError(KnowledgeBaseError):
    """Raised when requested resource is not found."""
    pass


class KnowledgeBaseValidationError(KnowledgeBaseError):
    """Raised when request validation fails."""
    pass


class KnowledgeBaseCircuitBreakerError(KnowledgeBaseError):
    """Raised when circuit breaker is open."""
    pass
