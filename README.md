# Workflow Client

Python client for `workflow-datastore` service. Provides a FeignClient-like interface for RAG operations.

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
from workflow_client import DataStoreClient, MetadataFilter

client = DataStoreClient()

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
    project_id="project-456",
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
    filters=MetadataFilter(tenant_id="tenant-123", project_id="project-456")
)
print(context.combined_context)
```

## Configuration

### Service Discovery

The client discovers the datastore service URL in this order:

1. **Consul** (if enabled and available)
2. **Environment variable**: `DATASTORE_SERVICE_URL`
3. **Default**: `http://workflow-datastore:8000`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATASTORE_SERVICE_URL` | `http://workflow-datastore:8000` | Direct service URL |
| `CONSUL_ENABLED` | `true` | Enable Consul discovery |
| `CONSUL_HOST` | `localhost` | Consul host |
| `CONSUL_PORT` | `8500` | Consul port |

### Direct URL

```python
# Bypass service discovery
client = DataStoreClient(base_url="http://localhost:8000")
```

## Data Hierarchy

```
tenant_id      -> Collection isolation
  project_id   -> Metadata filter
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
    project_id,
    kb_id,
    user_id=None,
    chunk_size=1000,
    chunk_overlap=200
)

# Delete
client.delete_documents(
    collection_name,
    tenant_id=None,
    project_id=None,
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
    DataStoreError,
    DataStoreConnectionError,
    DataStoreTimeoutError,
    DataStoreAPIError,
    DataStoreNotFoundError,
    DataStoreValidationError,
)

try:
    client.similarity_search(...)
except DataStoreConnectionError:
    # Service unreachable
except DataStoreTimeoutError:
    # Request timed out
except DataStoreNotFoundError:
    # Collection/resource not found
except DataStoreValidationError:
    # Invalid request
except DataStoreAPIError as e:
    print(e.status_code, e.response_body)
```

## License

MIT
