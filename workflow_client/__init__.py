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

__version__ = "1.3.0"

# AST Model - Shared across PEV microservices
from .models.ast import (
    AstModel,
    ASTv2,  # Backwards compatibility
    create_empty_ast,
    # Enums
    ScreenType,
    WidgetType,
    MessageType,
    DisplayStyle,
    ScenarioCategory,
    # All components
    ScreenClassification,
    OutputFileMapping,
    WidgetRegistry,
    Widget,
    ModeBehavior,
    WidgetViewpointMapping,
    ViewpointMapping,
    TestDataSample,
    TestScenario,
    NavigationStep,
    PreCondition,
    TestGroup,
    DecisionTable,
    DTCondition,
    DTSubTable,
    DTSubTableRow,
    BusinessRules,
    BusinessRule,
    Message,
    SqlVerification,
    ExpectedTestCount,
    CountBreakdown,
    ValidationRule,
)

# MindMap Model - Replaces AST v2.2 with deterministic template-based planning
from .models.mindmap import (
    MindMapModel,
    MindMap,  # Backwards compatibility alias
    create_empty_mindmap,
    create_mindmap_for_crud,
    # Enums (imported with prefixes to avoid AST enum conflicts)
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
    # AST Model
    "AstModel",
    "ASTv2",
    "create_empty_ast",
    # AST Enums
    "ScreenType",
    "WidgetType",
    "MessageType",
    "DisplayStyle",
    "ScenarioCategory",
    # AST Components
    "ScreenClassification",
    "OutputFileMapping",
    "WidgetRegistry",
    "Widget",
    "ModeBehavior",
    "WidgetViewpointMapping",
    "ViewpointMapping",
    "TestDataSample",
    "TestScenario",
    "NavigationStep",
    "PreCondition",
    "TestGroup",
    "DecisionTable",
    "DTCondition",
    "DTSubTable",
    "DTSubTableRow",
    "BusinessRules",
    "BusinessRule",
    "Message",
    "SqlVerification",
    "ExpectedTestCount",
    "CountBreakdown",
    "ValidationRule",
    # MindMap Main Model
    "MindMapModel",
    "MindMap",
    "create_empty_mindmap",
    "create_mindmap_for_crud",
    # MindMap Enums (prefixed to avoid AST conflicts)
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
