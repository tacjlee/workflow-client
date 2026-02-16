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

# MindMap Model (replaces AST v2.2)
from .mindmap import (
    # Main Model
    MindMapModel,
    MindMap,  # Backwards compatibility alias
    create_empty_mindmap,
    create_mindmap_for_crud,
    # Enums (use mindmap-specific naming to avoid conflicts)
    ScreenType as MindMapScreenType,
    ScreenMode as MindMapScreenMode,
    WidgetType as MindMapWidgetType,
    ButtonType as MindMapButtonType,
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
    # AST Main Model
    "AstModel",
    "ASTv2",
    "create_empty_ast",
    # AST Enums
    "ScreenType",
    "WidgetType",
    "MessageType",
    "DisplayStyle",
    "ScenarioCategory",
    # AST Component 1
    "ScreenClassification",
    "OutputFileMapping",
    # AST Component 2
    "WidgetRegistry",
    "Widget",
    "ModeBehavior",
    # AST Component 3
    "WidgetViewpointMapping",
    "ViewpointMapping",
    "TestDataSample",
    # AST Component 4
    "TestScenario",
    "NavigationStep",
    "PreCondition",
    "TestGroup",
    # AST Component 5
    "DecisionTable",
    "DTCondition",
    "DTSubTable",
    "DTSubTableRow",
    # AST Component 6
    "BusinessRules",
    "BusinessRule",
    "Message",
    # AST Component 7
    "SqlVerification",
    # AST Component 8
    "ExpectedTestCount",
    "CountBreakdown",
    "ValidationRule",
    # MindMap Main Model
    "MindMapModel",
    "MindMap",
    "create_empty_mindmap",
    "create_mindmap_for_crud",
    # MindMap Enums (prefixed to avoid conflicts)
    "MindMapScreenType",
    "MindMapScreenMode",
    "MindMapWidgetType",
    "MindMapButtonType",
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
