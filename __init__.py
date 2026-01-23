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
"""

from .client import DataStoreClient, get_datastore_client
from .models import (
    MetadataFilter,
    CollectionInfo,
    SearchResult,
    RAGContext,
    DocumentChunk,
    DocumentProcessResult,
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
    # Models
    "MetadataFilter",
    "CollectionInfo",
    "SearchResult",
    "RAGContext",
    "DocumentChunk",
    "DocumentProcessResult",
    # Exceptions
    "DataStoreError",
    "DataStoreConnectionError",
    "DataStoreTimeoutError",
    "DataStoreAPIError",
    "DataStoreNotFoundError",
    "DataStoreValidationError",
    "DataStoreCircuitBreakerError",
]
