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
)

# AST Model
from .ast import (
    # Main Model
    AstModel,
    ASTv2,  # Backwards compatibility
    create_empty_ast,
    # Enums
    ScreenType,
    WidgetType,
    MessageType,
    DisplayStyle,
    ScenarioCategory,
    # Component 1
    ScreenClassification,
    OutputFileMapping,
    # Component 2
    WidgetRegistry,
    Widget,
    ModeBehavior,
    # Component 3
    WidgetViewpointMapping,
    ViewpointMapping,
    TestDataSample,
    # Component 4
    TestScenario,
    NavigationStep,
    PreCondition,
    TestGroup,
    # Component 5
    DecisionTable,
    DTCondition,
    DTSubTable,
    DTSubTableRow,
    # Component 6
    BusinessRules,
    BusinessRule,
    Message,
    # Component 7
    SqlVerification,
    # Component 8
    ExpectedTestCount,
    CountBreakdown,
    ValidationRule,
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
    # Main Model
    "AstModel",
    "ASTv2",
    "create_empty_ast",
    # Enums
    "ScreenType",
    "WidgetType",
    "MessageType",
    "DisplayStyle",
    "ScenarioCategory",
    # Component 1
    "ScreenClassification",
    "OutputFileMapping",
    # Component 2
    "WidgetRegistry",
    "Widget",
    "ModeBehavior",
    # Component 3
    "WidgetViewpointMapping",
    "ViewpointMapping",
    "TestDataSample",
    # Component 4
    "TestScenario",
    "NavigationStep",
    "PreCondition",
    "TestGroup",
    # Component 5
    "DecisionTable",
    "DTCondition",
    "DTSubTable",
    "DTSubTableRow",
    # Component 6
    "BusinessRules",
    "BusinessRule",
    "Message",
    # Component 7
    "SqlVerification",
    # Component 8
    "ExpectedTestCount",
    "CountBreakdown",
    "ValidationRule",
]
