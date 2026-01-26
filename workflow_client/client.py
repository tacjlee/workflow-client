"""
DataStoreClient

Synchronous HTTP client for workflow-datastore service.
Similar to Java FeignClient pattern with service discovery and retry logic.

Usage:
    from workflow_client import DataStoreClient, MetadataFilter

    client = DataStoreClient()

    # Create collection (tenant-scoped)
    client.create_collection("tenant-123", "my-collection")
    # Creates: tenant_tenant_123_my_collection

    # Add documents (with full hierarchy)
    result = client.add_documents(
        collection_name="tenant_tenant_123_my_collection",
        documents=[{"content": "Hello world", "metadata": {"file_name": "doc.pdf"}}],
        tenant_id="tenant-123",
        project_id="project-456",
        kb_id="kb-789"
    )

    # Search with tenant filtering
    results = client.similarity_search(
        collection_name="tenant_tenant_123_my_collection",
        query="hello",
        top_k=10,
        filters=MetadataFilter(tenant_id="tenant-123", project_id="project-456")
    )
"""

import time
import logging
from typing import Optional, List, Dict, Any, Callable, Protocol
from functools import wraps

import httpx


class RequestInterceptor(Protocol):
    """
    Request interceptor protocol (similar to Java FeignClient RequestInterceptor).

    Implement this protocol to add headers, modify requests, or add tracing.

    Example:
        class AuthInterceptor:
            def __init__(self, token: str):
                self.token = token

            def __call__(self, headers: Dict[str, str]) -> Dict[str, str]:
                headers["Authorization"] = f"Bearer {self.token}"
                return headers

        client = DataStoreClient(interceptors=[AuthInterceptor("my-token")])
    """
    def __call__(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Intercept and modify request headers.

        Args:
            headers: Current request headers

        Returns:
            Modified headers dict
        """
        ...


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
    DataStoreConnectionError,
    DataStoreTimeoutError,
    DataStoreAPIError,
    DataStoreNotFoundError,
    DataStoreValidationError,
    DataStoreCircuitBreakerError,
)
from .service_discovery import ServiceDiscovery

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except (DataStoreConnectionError, DataStoreTimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class DataStoreClient:
    """
    Synchronous HTTP client for workflow-datastore service.

    Features:
    - Service discovery via Consul with environment fallback
    - Connection pooling
    - Retry with exponential backoff
    - Type-safe request/response models
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        read_timeout: float = 60.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        max_connections_per_route: int = 50,
        max_connections: int = 200,
        interceptors: Optional[List[Callable[[Dict[str, str]], Dict[str, str]]]] = None
    ):
        """
        Initialize DataStoreClient.

        Args:
            base_url: Direct URL override (bypasses service discovery)
            read_timeout: Read timeout in seconds (default: 60, same as Java FeignClient)
            connect_timeout: Connection timeout in seconds (default: 10, same as Java FeignClient)
            max_retries: Maximum retry attempts
            max_connections_per_route: Max keepalive connections per route (default: 50, same as Java FeignClient)
            max_connections: Max total connections (default: 200, same as Java FeignClient)
            interceptors: List of request interceptors (similar to Java FeignClient RequestInterceptor)
        """
        self._service_discovery = ServiceDiscovery()
        self._base_url = base_url
        self._timeout = httpx.Timeout(read_timeout, connect=connect_timeout)
        self._max_retries = max_retries
        self._limits = httpx.Limits(
            max_keepalive_connections=max_connections_per_route,
            max_connections=max_connections
        )
        self._client: Optional[httpx.Client] = None
        self._interceptors: List[Callable[[Dict[str, str]], Dict[str, str]]] = interceptors or []

    @property
    def base_url(self) -> str:
        """Get base URL from service discovery or fallback."""
        if self._base_url:
            return self._base_url
        return self._service_discovery.get_datastore_service_url()

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self._timeout,
                limits=self._limits
            )
        return self._client

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code in (200, 201):
            return response.json()
        elif response.status_code == 404:
            raise DataStoreNotFoundError(f"Resource not found: {response.text}")
        elif response.status_code == 422:
            raise DataStoreValidationError(f"Validation error: {response.text}")
        elif response.status_code == 503:
            raise DataStoreCircuitBreakerError(f"Service unavailable (circuit breaker open): {response.text}")
        elif response.status_code >= 500:
            raise DataStoreAPIError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text
            )
        else:
            raise DataStoreAPIError(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text
            )

    def _apply_interceptors(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Apply all registered interceptors to headers."""
        for interceptor in self._interceptors:
            headers = interceptor(headers)
        return headers

    def add_interceptor(self, interceptor: Callable[[Dict[str, str]], Dict[str, str]]) -> None:
        """
        Add a request interceptor.

        Args:
            interceptor: Callable that takes headers dict and returns modified headers

        Example:
            client.add_interceptor(lambda h: {**h, "X-Trace-Id": "abc123"})
        """
        self._interceptors.append(interceptor)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        try:
            client = self._get_client()

            # Apply interceptors to headers
            headers = {"Content-Type": "application/json"}
            headers = self._apply_interceptors(headers)

            response = client.request(
                method=method,
                url=endpoint,
                json=json,
                params=params,
                headers=headers
            )
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise DataStoreConnectionError(f"Connection failed: {e}")
        except httpx.TimeoutException as e:
            raise DataStoreTimeoutError(f"Request timed out: {e}")

    def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # =========================================================================
    # COLLECTION OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def create_collection(
        self,
        tenant_id: str,
        name: str,
        enable_multivector: bool = True,
        vector_size: int = 1024
    ) -> CollectionInfo:
        """
        Create a new vector collection.

        Args:
            tenant_id: Tenant ID for multi-tenant isolation
            name: Collection name suffix
            enable_multivector: Enable BGE-M3 multi-vector search (dense + sparse + ColBERT)
            vector_size: Vector dimension size (1024 for BGE-M3)

        Returns:
            CollectionInfo with created collection details
        """
        data = self._make_request(
            "POST",
            "/api/datastore/collections",
            json={
                "tenant_id": tenant_id,
                "name": name,
                "enable_multivector": enable_multivector,
                "vector_size": vector_size,
                "distance": "Cosine"
            }
        )
        return CollectionInfo(**data)

    @retry_with_backoff(max_retries=3)
    def get_collection_info(self, collection_name: str) -> CollectionInfo:
        """Get collection information."""
        data = self._make_request("GET", f"/api/datastore/collections/{collection_name}")
        return CollectionInfo(**data)

    @retry_with_backoff(max_retries=3)
    def delete_collection(
        self,
        collection_name: str,
        tenant_id: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """Delete a collection."""
        params = {"force": force}
        if tenant_id:
            params["tenant_id"] = tenant_id

        self._make_request("DELETE", f"/api/datastore/collections/{collection_name}", params=params)
        return True

    @retry_with_backoff(max_retries=3)
    def list_collections(self, tenant_id: Optional[str] = None) -> List[CollectionInfo]:
        """List collections for a tenant."""
        params = {}
        if tenant_id:
            params["tenant_id"] = tenant_id

        data = self._make_request("GET", "/api/datastore/collections", params=params)
        return [CollectionInfo(**c) for c in data.get("collections", [])]

    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def add_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        tenant_id: str,
        project_id: str,
        kb_id: str,
        user_id: Optional[str] = None,
        document_type: str = "document",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> DocumentProcessResult:
        """
        Add documents to collection (with automatic chunking and embedding).

        Hierarchy: tenant_id -> project_id -> kb_id -> doc_id

        Args:
            collection_name: Target collection name
            documents: List of document dicts with 'content' and optional 'metadata'
            tenant_id: Tenant ID (required)
            project_id: Project ID (required)
            kb_id: Knowledge base ID (required)
            user_id: Optional user ID
            document_type: Document type (e.g., document, template, viewpoint, rule)
            chunk_size: Chunk size for text splitting
            chunk_overlap: Overlap between chunks

        Returns:
            DocumentProcessResult with chunking results
        """
        # For now, process each document individually
        # A batch endpoint could be added to the service
        all_chunks = []
        all_vector_ids = []

        for doc in documents:
            content = doc.get("content", "")
            file_name = doc.get("metadata", {}).get("file_name")
            doc_id = doc.get("metadata", {}).get("doc_id")
            # Allow per-document type override from metadata
            doc_type = doc.get("metadata", {}).get("document_type", document_type)

            data = self._make_request(
                "POST",
                "/api/datastore/documents/process",
                json={
                    "collection_name": collection_name,
                    "content": content,
                    "tenant_id": tenant_id,
                    "project_id": project_id,
                    "kb_id": kb_id,
                    "doc_id": doc_id,
                    "file_name": file_name,
                    "user_id": user_id,
                    "document_type": doc_type,
                    "chunk_config": {
                        "strategy": "sentence",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap
                    }
                }
            )

            all_chunks.extend([DocumentChunk(**c) for c in data.get("chunks", [])])
            if data.get("vector_ids"):
                all_vector_ids.extend(data["vector_ids"])

        return DocumentProcessResult(
            document_id=documents[0].get("metadata", {}).get("doc_id", "batch"),
            chunks_count=len(all_chunks),
            chunks=all_chunks,
            vector_ids=all_vector_ids if all_vector_ids else None,
            status="processed"
        )

    @retry_with_backoff(max_retries=3)
    def delete_documents(
        self,
        collection_name: str,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        kb_id: Optional[str] = None,
        doc_id: Optional[str] = None,
        document_type: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> int:
        """
        Delete document vectors from collection.

        At least one filter is required.
        Hierarchy: tenant_id -> project_id -> kb_id -> doc_id
        """
        data = self._make_request(
            "DELETE",
            "/api/datastore/documents",
            json={
                "collection_name": collection_name,
                "tenant_id": tenant_id,
                "project_id": project_id,
                "kb_id": kb_id,
                "doc_id": doc_id,
                "document_type": document_type,
                "file_name": file_name
            }
        )
        return data.get("deleted_count", 0)

    # =========================================================================
    # VECTOR OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def add_vectors(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        auto_embed: bool = True
    ) -> List[str]:
        """
        Add vectors to collection.

        Args:
            collection_name: Collection name
            vectors: List of vector dicts with 'content', optional 'embedding', 'metadata'
            auto_embed: Generate embeddings if not provided

        Returns:
            List of added vector IDs
        """
        # Transform to API format
        api_vectors = []
        for v in vectors:
            vec = {
                "content": v["content"],
                "metadata": v.get("metadata", {})
            }
            if v.get("id"):
                vec["id"] = v["id"]
            if v.get("embedding"):
                vec["embedding"] = v["embedding"]
            api_vectors.append(vec)

        data = self._make_request(
            "POST",
            "/api/datastore/vectors",
            json={
                "collection_name": collection_name,
                "vectors": api_vectors,
                "auto_embed": auto_embed
            }
        )
        return data.get("vector_ids", [])

    @retry_with_backoff(max_retries=3)
    def delete_vectors(
        self,
        collection_name: str,
        vector_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete vectors by IDs or filter."""
        data = self._make_request(
            "DELETE",
            "/api/datastore/vectors",
            json={
                "collection_name": collection_name,
                "vector_ids": vector_ids,
                "filters": filters
            }
        )
        return data.get("deleted_count", 0)

    # =========================================================================
    # EMBEDDING OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        data = self._make_request(
            "POST",
            "/api/datastore/embeddings",
            json={
                "texts": texts,
                "batch_size": batch_size,
                "use_cache": True
            }
        )
        return data.get("embeddings", [])

    # =========================================================================
    # SEARCH OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def similarity_search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 10,
        filters: Optional[MetadataFilter] = None,
        score_threshold: Optional[float] = None,
        include_embeddings: bool = False
    ) -> List[SearchResult]:
        """
        Perform similarity search.

        Args:
            collection_name: Collection to search
            query: Query text
            top_k: Number of results
            filters: Metadata filters
            score_threshold: Minimum similarity score
            include_embeddings: Include embeddings in results

        Returns:
            List of SearchResult
        """
        request_data = {
            "collection_name": collection_name,
            "query": query,
            "top_k": top_k,
            "include_embeddings": include_embeddings
        }
        if filters:
            request_data["filters"] = filters.to_dict() if hasattr(filters, 'to_dict') else filters
        if score_threshold is not None:
            request_data["score_threshold"] = score_threshold

        data = self._make_request("POST", "/api/datastore/search/similarity", json=request_data)
        return [SearchResult(**r) for r in data.get("results", [])]

    @retry_with_backoff(max_retries=3)
    def rag_retrieval(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        filters: Optional[MetadataFilter] = None,
        rerank: bool = False,
        rerank_top_n: int = 3
    ) -> RAGContext:
        """
        RAG retrieval: get relevant chunks for a query.

        Note: External reranker is disabled. For multivector collections,
        ColBERT late-interaction provides built-in reranking via hybrid_search.
        The rerank/rerank_top_n parameters are kept for API compatibility but ignored.

        Args:
            collection_name: Collection to search
            query: Query text
            top_k: Number of chunks to retrieve
            filters: Metadata filters
            rerank: Deprecated - ignored (ColBERT reranking is automatic)
            rerank_top_n: Deprecated - ignored

        Returns:
            RAGContext with chunks and combined context
        """
        request_data = {
            "collection_name": collection_name,
            "query": query,
            "top_k": top_k,
            "rerank": rerank,
            "rerank_top_n": rerank_top_n
        }
        if filters:
            request_data["filters"] = filters.to_dict() if hasattr(filters, 'to_dict') else filters

        data = self._make_request("POST", "/api/datastore/search/rag", json=request_data)

        context_data = data.get("context", {})
        return RAGContext(
            chunks=[SearchResult(**c) for c in context_data.get("chunks", [])],
            combined_context=context_data.get("combined_context", ""),
            source_documents=context_data.get("source_documents", [])
        )

    # =========================================================================
    # TEXT EXTRACTION OPERATIONS
    # =========================================================================

    @retry_with_backoff(max_retries=3)
    def extract_text(
        self,
        file_content: bytes,
        filename: str
    ) -> ExtractionResult:
        """
        Extract text content from a document file.

        Args:
            file_content: File content as bytes
            filename: Original filename (used for format detection)

        Returns:
            ExtractionResult with extracted text content

        Raises:
            DataStoreValidationError: If file format is not supported
            DataStoreAPIError: If extraction fails
        """
        try:
            client = self._get_client()

            # Apply interceptors to headers (without Content-Type for multipart)
            headers = {}
            headers = self._apply_interceptors(headers)

            # Send file as multipart form data
            files = {"file": (filename, file_content)}
            response = client.post(
                "/api/datastore/extraction/extract",
                files=files,
                headers=headers
            )
            data = self._handle_response(response)
            return ExtractionResult(**data)
        except httpx.ConnectError as e:
            raise DataStoreConnectionError(f"Connection failed: {e}")
        except httpx.TimeoutException as e:
            raise DataStoreTimeoutError(f"Request timed out: {e}")

    @retry_with_backoff(max_retries=3)
    def get_supported_formats(self) -> SupportedFormats:
        """
        Get list of supported file formats for text extraction.

        Returns:
            SupportedFormats with list of supported file extensions
        """
        data = self._make_request("GET", "/api/datastore/extraction/formats")
        return SupportedFormats(**data)

    def is_format_supported(self, filename: str) -> bool:
        """
        Check if a file format is supported for text extraction.

        Args:
            filename: Filename to check (only extension is used)

        Returns:
            True if format is supported, False otherwise
        """
        data = self._make_request(
            "POST",
            "/api/datastore/extraction/check-format",
            params={"filename": filename}
        )
        return data.get("supported", False)

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    def health_check(self) -> Dict[str, Any]:
        """Check datastore-service health."""
        try:
            client = self._get_client()
            response = client.get("/health")
            if response.status_code == 200:
                return {"status": "healthy", "data": response.json()}
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Singleton instance
_datastore_client: Optional[DataStoreClient] = None


def get_datastore_client() -> DataStoreClient:
    """Get singleton DataStoreClient instance."""
    global _datastore_client
    if _datastore_client is None:
        _datastore_client = DataStoreClient()
    return _datastore_client
