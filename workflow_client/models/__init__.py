"""
Models package for workflow_client.

This package contains shared models used across PEV microservices.
"""

# Knowledge Client Models (for backwards compatibility with models.py)
from .knowledge import (
    MetadataFilter,
    CollectionInfo,
    SearchResult,
    RAGContext,
    DocumentChunk,
    DocumentProcessResult,
    ExtractionResult,
    SupportedFormats,
    # Parent-Child Chunking Models
    ParentChildChunkConfig,
    ParentChildProcessResult,
    ParentResult,
    SearchExpandResult,
    # Similarity API Models
    SimilarityRequest,
    SimilarityResponse,
    BatchSimilarityItem,
    BatchSimilarityRequest,
    BatchSimilarityResult,
    BatchSimilarityResponse,
    # Search Records API Models
    RecordMatch,
    SearchRecordsResponse,
)

# MindMap Model
from .mindmap import (
    # Main Model
    MindMapModel,
    MindMap,  # Backwards compatibility alias
    create_empty_mindmap,
    create_mindmap_for_crud,
    # Enums
    ScreenType,
    ScreenMode,
    WidgetType,
    ButtonType,
    ViewpointCategory,
    WidgetState,
    # Components
    TestItem,
    ViewpointPlan,
    WidgetConstraints,
    WidgetTestPlan,
    ButtonTestPlan,
    DTReference,
    FixedTests,
    ModeTestPlan,
    # Template Constants
    WIDGET_TEST_COUNTS,
    WIDGET_APPLICABLE_MODES,
    LIST_MODE_FIXED_TESTS,
    ADD_MODE_FIXED_TESTS,
    EDIT_MODE_FIXED_TESTS,
    MODE_VALIDATION_TRIGGERS,
    DT_COMBINATIONS,
    DT_ROW_MULTIPLIER,
    # Utility Functions
    get_widget_test_count,
    get_applicable_modes,
    get_mode_fixed_tests,
    get_dt_test_count,
    calculate_trigger_tests,
)

__all__ = [
    # Knowledge Client Models
    "MetadataFilter",
    "CollectionInfo",
    "SearchResult",
    "RAGContext",
    "DocumentChunk",
    "DocumentProcessResult",
    "ExtractionResult",
    "SupportedFormats",
    # Parent-Child Chunking Models
    "ParentChildChunkConfig",
    "ParentChildProcessResult",
    "ParentResult",
    "SearchExpandResult",
    # Similarity API Models
    "SimilarityRequest",
    "SimilarityResponse",
    "BatchSimilarityItem",
    "BatchSimilarityRequest",
    "BatchSimilarityResult",
    "BatchSimilarityResponse",
    # Search Records API Models
    "RecordMatch",
    "SearchRecordsResponse",
    # MindMap Main Model
    "MindMapModel",
    "MindMap",
    "create_empty_mindmap",
    "create_mindmap_for_crud",
    # MindMap Enums
    "ScreenType",
    "ScreenMode",
    "WidgetType",
    "ButtonType",
    "ViewpointCategory",
    "WidgetState",
    # MindMap Components
    "TestItem",
    "ViewpointPlan",
    "WidgetConstraints",
    "WidgetTestPlan",
    "ButtonTestPlan",
    "DTReference",
    "FixedTests",
    "ModeTestPlan",
    # MindMap Template Constants
    "WIDGET_TEST_COUNTS",
    "WIDGET_APPLICABLE_MODES",
    "LIST_MODE_FIXED_TESTS",
    "ADD_MODE_FIXED_TESTS",
    "EDIT_MODE_FIXED_TESTS",
    "MODE_VALIDATION_TRIGGERS",
    "DT_COMBINATIONS",
    "DT_ROW_MULTIPLIER",
    # MindMap Utility Functions
    "get_widget_test_count",
    "get_applicable_modes",
    "get_mode_fixed_tests",
    "get_dt_test_count",
    "calculate_trigger_tests",
]
