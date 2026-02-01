# Workflow Client

Python client for `workflow-knowledge-base` service. Provides a FeignClient-like interface for RAG operations.

## Installation

```bash
# From GitHub
pip install "git+https://github.com/tacjlee/workflow-client.git"

# With Consul support
pip install "workflow-client[consul] @ git+https://github.com/tacjlee/workflow-client.git"
```

**In requirements.txt:**
```
workflow-client @ git+https://github.com/tacjlee/workflow-client.git
```

## Quick Start

```python
from workflow_client import KnowledgeBaseClient, MetadataFilter

client = KnowledgeBaseClient()

# Create a tenant-scoped collection
client.create_collection(tenant_id="tenant-123", name="knowledge-base")
# Creates: tenant_tenant_123_knowledge_base

# Add documents with hierarchy metadata
client.add_documents(
    collection_name="tenant_tenant_123_knowledge_base",
    documents=[
        {"content": "Document content here", "metadata": {"file_name": "doc.pdf"}}
    ],
    tenant_id="tenant-123",
    kb_id="kb-789"
)

# Search with tenant filtering
results = client.similarity_search(
    collection_name="tenant_tenant_123_knowledge_base",
    query="search query",
    top_k=10,
    filters=MetadataFilter(tenant_id="tenant-123")
)

# RAG retrieval
context = client.rag_retrieval(
    collection_name="tenant_tenant_123_knowledge_base",
    query="What is...",
    filters=MetadataFilter(tenant_id="tenant-123", kb_id="kb-789")
)
print(context.combined_context)
```

## Configuration

### Service Discovery

The client discovers the knowledge base service URL in this order:

1. **Consul** (if enabled and available)
2. **Environment variable**: `KNOWLEDGE_BASE_SERVICE_URL`
3. **Default**: `http://workflow-knowledge-base:8000`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KNOWLEDGE_BASE_SERVICE_URL` | `http://workflow-knowledge-base:8000` | Direct service URL |
| `CONSUL_ENABLED` | `true` | Enable Consul discovery |
| `CONSUL_HOST` | `localhost` | Consul host |
| `CONSUL_PORT` | `8500` | Consul port |

### Direct URL

```python
# Bypass service discovery
client = KnowledgeBaseClient(base_url="http://localhost:8000")
```

## Data Hierarchy

```
tenant_id    -> Collection isolation
  kb_id      -> Metadata filter
    doc_id   -> Metadata filter
```

## API Reference

### Collections

```python
# Create
client.create_collection(tenant_id, name, enable_multivector=True, vector_size=1024)

# Get info
client.get_collection_info(collection_name)

# List
client.list_collections(tenant_id=None)

# Delete
client.delete_collection(collection_name, tenant_id=None, force=False)
```

### Documents

```python
# Add (with chunking and embedding)
client.add_documents(
    collection_name,
    documents,
    tenant_id,
    kb_id,
    user_id=None,
    chunk_size=1000,
    chunk_overlap=200
)

# Delete
client.delete_documents(
    collection_name,
    tenant_id=None,
    kb_id=None,
    doc_id=None,
    file_name=None
)
```

### Search

```python
# Similarity search
results = client.similarity_search(
    collection_name,
    query,
    top_k=10,
    filters=MetadataFilter(...),
    score_threshold=None,
    include_embeddings=False
)

# RAG retrieval (ColBERT reranking is automatic for multivector collections)
context = client.rag_retrieval(
    collection_name,
    query,
    top_k=5,
    filters=MetadataFilter(...)
)
```

### Embeddings

```python
embeddings = client.generate_embeddings(texts, batch_size=32)
```

## Error Handling

```python
from workflow_client import (
    KnowledgeBaseError,
    KnowledgeBaseConnectionError,
    KnowledgeBaseTimeoutError,
    KnowledgeBaseAPIError,
    KnowledgeBaseNotFoundError,
    KnowledgeBaseValidationError,
)

try:
    client.similarity_search(...)
except KnowledgeBaseConnectionError:
    # Service unreachable
except KnowledgeBaseTimeoutError:
    # Request timed out
except KnowledgeBaseNotFoundError:
    # Collection/resource not found
except KnowledgeBaseValidationError:
    # Invalid request
except KnowledgeBaseAPIError as e:
    print(e.status_code, e.response_body)
```

## Testing

### Install for Development

```bash
# Clone and install in development mode
git clone https://github.com/tacjlee/workflow-client.git
cd workflow-client
pip install -e ".[dev]"
```

### Run Tests

```bash
# Set service URL (default: http://localhost:8010)
export KNOWLEDGE_BASE_SERVICE_URL=http://localhost:8010

# Run all tests
pytest tests/ -v

# Run unit tests only (no service required)
pytest tests/ -v -k "Unit"

# Run integration tests only (requires running service)
pytest tests/ -v -k "Integration"

# Run comprehensive API coverage test
pytest tests/test_all_apis.py -v -s

# Run specific test file
pytest tests/test_collection_api.py -v
pytest tests/test_document_api.py -v
pytest tests/test_embedding_api.py -v
pytest tests/test_search_api.py -v
pytest tests/test_vector_api.py -v
```

### Test Coverage

| Test File | APIs Covered |
|-----------|--------------|
| `test_collection_api.py` | create_collection, get_collection_info, list_collections, delete_collection |
| `test_document_api.py` | add_documents, delete_documents |
| `test_vector_api.py` | add_vectors, delete_vectors |
| `test_embedding_api.py` | generate_embeddings, health_check |
| `test_search_api.py` | similarity_search, rag_retrieval |
| `test_all_apis.py` | **All APIs** - comprehensive end-to-end workflow |

### Test Types

- **Unit Tests**: Mock HTTP calls, test request/response formats, no service required
- **Integration Tests**: Require running `workflow-knowledge-base` service, test real API calls

## License

MIT
