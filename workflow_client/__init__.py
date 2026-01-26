"""
DataStore Client

Python client for workflow-datastore service.
Provides FeignClient-like interface for RAG operations.

Usage:
    from workflow_client import DataStoreClient, MetadataFilter

    client = DataStoreClient()

    # Create collection
    client.create_collection(tenant_id="tenant-123", name="my-kb")

    # Add documents
    client.add_documents(
        collection_name="tenant_tenant_123_my_kb",
        documents=[{"content": "Hello world"}],
        tenant_id="tenant-123",
        project_id="project-456",
        kb_id="kb-789"
    )

    # Search
    results = client.similarity_search(
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

    client = DataStoreClient(interceptors=[
        AuthInterceptor("my-token"),
        TracingInterceptor()
    ])
"""

from .client import DataStoreClient, get_datastore_client, RequestInterceptor
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
    DataStoreError,
    DataStoreConnectionError,
    DataStoreTimeoutError,
    DataStoreAPIError,
    DataStoreNotFoundError,
    DataStoreValidationError,
    DataStoreCircuitBreakerError,
)

__version__ = "1.0.0"

__all__ = [
    # Client
    "DataStoreClient",
    "get_datastore_client",
    "RequestInterceptor",
    # Models
    "MetadataFilter",
    "CollectionInfo",
    "SearchResult",
    "RAGContext",
    "DocumentChunk",
    "DocumentProcessResult",
    "ExtractionResult",
    "SupportedFormats",
    # Exceptions
    "DataStoreError",
    "DataStoreConnectionError",
    "DataStoreTimeoutError",
    "DataStoreAPIError",
    "DataStoreNotFoundError",
    "DataStoreValidationError",
    "DataStoreCircuitBreakerError",
]
