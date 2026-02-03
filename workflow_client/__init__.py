"""
Knowledge Client

Python client for workflow-knowledge service.
Provides FeignClient-like interface for RAG operations.

Usage:
    from workflow_client import KnowledgeClient, MetadataFilter

    client = KnowledgeClient()

    # Create collection
    client.create_collection(tenant_id="tenant-123", name="my-kb")

    # Add documents
    client.add_documents(
        collection_name="tenant_tenant_123_my_kb",
        documents=[{"content": "Hello world"}],
        tenant_id="tenant-123",
        knowledge_id="kb-789"
    )

    # Search
    results = client.search(
        collection_name="tenant_tenant_123_my_kb",
        query="hello",
        filters=MetadataFilter(tenant_id="tenant-123")
    )

Request Interceptors (similar to Java FeignClient):
    # Auth interceptor
    class AuthInterceptor:
        def __init__(self, token: str):
            self.token = token

        def __call__(self, headers: dict) -> dict:
            headers["Authorization"] = f"Bearer {self.token}"
            return headers

    # Tracing interceptor
    class TracingInterceptor:
        def __call__(self, headers: dict) -> dict:
            headers["X-Trace-Id"] = generate_trace_id()
            return headers

    client = KnowledgeClient(interceptors=[
        AuthInterceptor("my-token"),
        TracingInterceptor()
    ])
"""

from .client import KnowledgeClient, get_knowledge_client, RequestInterceptor
from .models import (
    MetadataFilter,
    CollectionInfo,
    SearchResult,
    RAGContext,
    DocumentChunk,
    DocumentProcessResult,
    ExtractionResult,
    SupportedFormats,
)
from .exceptions import (
    # New names
    KnowledgeError,
    KnowledgeConnectionError,
    KnowledgeTimeoutError,
    KnowledgeAPIError,
    KnowledgeNotFoundError,
    KnowledgeValidationError,
    KnowledgeCircuitBreakerError,
    # Backwards compatibility aliases (deprecated)
    KnowledgeBaseError,
    KnowledgeBaseConnectionError,
    KnowledgeBaseTimeoutError,
    KnowledgeBaseAPIError,
    KnowledgeBaseNotFoundError,
    KnowledgeBaseValidationError,
    KnowledgeBaseCircuitBreakerError,
)

# Consul Client SDK (optional - requires python-consul)
# Import with: from workflow_client import consul_client
# Or: from workflow_client.consul_client import ConsulClient
try:
    from .consul_client import (
        ConsulClient,
        consul_client,
        get_consul_client,
    )
    _consul_available = True
except ImportError:
    _consul_available = False
    ConsulClient = None
    consul_client = None
    get_consul_client = None

# Celery Client SDK (optional - requires celery)
# Import with: from workflow_client.celery_client import CeleryClient
try:
    from .celery_client import (
        CeleryClient,
        CeleryClientConfig,
        celery_client,
        task_method,
        CeleryClientError,
        CeleryTimeoutError,
        CeleryTaskError,
    )
    _celery_available = True
except ImportError:
    _celery_available = False
    CeleryClient = None
    CeleryClientConfig = None
    celery_client = None
    task_method = None
    CeleryClientError = None
    CeleryTimeoutError = None
    CeleryTaskError = None

__version__ = "1.2.3"

__all__ = [
    # Knowledge Client
    "KnowledgeClient",
    "get_knowledge_client",
    "RequestInterceptor",
    # Knowledge Models
    "MetadataFilter",
    "CollectionInfo",
    "SearchResult",
    "RAGContext",
    "DocumentChunk",
    "DocumentProcessResult",
    "ExtractionResult",
    "SupportedFormats",
    # Knowledge Exceptions (new names)
    "KnowledgeError",
    "KnowledgeConnectionError",
    "KnowledgeTimeoutError",
    "KnowledgeAPIError",
    "KnowledgeNotFoundError",
    "KnowledgeValidationError",
    "KnowledgeCircuitBreakerError",
    # Knowledge Exceptions (deprecated aliases)
    "KnowledgeBaseError",
    "KnowledgeBaseConnectionError",
    "KnowledgeBaseTimeoutError",
    "KnowledgeBaseAPIError",
    "KnowledgeBaseNotFoundError",
    "KnowledgeBaseValidationError",
    "KnowledgeBaseCircuitBreakerError",
    # Consul Client
    "ConsulClient",
    "consul_client",
    "get_consul_client",
    # Celery Client
    "CeleryClient",
    "CeleryClientConfig",
    "celery_client",
    "task_method",
    # Celery Exceptions
    "CeleryClientError",
    "CeleryTimeoutError",
    "CeleryTaskError",
]
