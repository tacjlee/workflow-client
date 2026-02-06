"""
KnowledgeClient Models

Pydantic models for request/response handling.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class MetadataFilter(BaseModel):
    """
    Metadata filter for search operations.

    Hierarchy: tenant_id -> knowledge_id -> document_id
    """
    tenant_id: Optional[str] = None
    knowledge_id: Optional[str] = None
    knowledge_ids: Optional[List[str]] = None  # Filter by multiple knowledge bases
    document_id: Optional[str] = None
    document_type: Optional[str] = None
    user_ids: Optional[List[str]] = None
    file_name: Optional[str] = None
    custom: Optional[Dict[str, Any]] = None

    # Parent-child chunking filters
    chunk_type: Optional[Literal["flat", "parent", "child"]] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, excluding None values."""
        result = {}
        if self.tenant_id:
            result["tenant_id"] = self.tenant_id
        if self.knowledge_ids:
            result["knowledge_ids"] = self.knowledge_ids
        elif self.knowledge_id:
            result["knowledge_id"] = self.knowledge_id
        if self.document_id:
            result["document_id"] = self.document_id
        if self.document_type:
            result["document_type"] = self.document_type
        if self.user_ids:
            result["user_ids"] = self.user_ids
        if self.file_name:
            result["file_name"] = self.file_name
        if self.custom:
            result["custom"] = self.custom
        # Parent-child filters
        if self.chunk_type:
            result["chunk_type"] = self.chunk_type
        if self.parent_id:
            result["parent_id"] = self.parent_id
        return result


class CollectionInfo(BaseModel):
    """Collection information."""
    name: str
    vectors_count: int
    status: str
    config: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Single search result."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    rerank_score: Optional[float] = None


class RAGContext(BaseModel):
    """RAG retrieval context."""
    chunks: List[SearchResult]
    combined_context: str
    source_documents: List[str]


class DocumentChunk(BaseModel):
    """Document chunk."""
    chunk_id: str
    content: str
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentProcessResult(BaseModel):
    """Document processing result."""
    document_id: str
    chunks_count: int
    chunks: List[DocumentChunk]
    vector_ids: Optional[List[str]] = None
    status: str


class ExtractionResult(BaseModel):
    """Text extraction result."""
    content: str
    file_type: str
    char_count: int
    filename: str


class SupportedFormats(BaseModel):
    """Supported file formats for extraction."""
    extensions: List[str]


# Parent-Child Chunking Models

class ParentChildChunkConfig(BaseModel):
    """Configuration for parent-child chunking strategy."""
    parent_chunk_size: int = 4000
    child_chunk_size: int = 500
    child_chunk_overlap: int = 100


class ParentChildProcessResult(BaseModel):
    """Parent-child document processing result."""
    document_id: str
    parent_count: int
    child_count: int
    parent_ids: List[str]
    child_ids: List[str]
    status: str


class ParentResult(BaseModel):
    """Parent document result with aggregated score."""
    parent_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    matching_children: Optional[List[SearchResult]] = None
    child_count: int = 0


class SearchExpandResult(BaseModel):
    """Search with parent expansion result."""
    parents: List[ParentResult]
    total_parents: int
    total_children_searched: int
    query: str
    execution_time_ms: float
    cached: bool = False
