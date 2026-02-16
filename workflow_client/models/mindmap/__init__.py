"""
MindMap Model - Deterministic Template-Based Test Planning.

This package defines the MindMap structure that replaces AST v2.2
for test case generation in the PEV (Planner-Executor-Validator) architecture.

Key differences from AST v2.2:
- Templates define exact test counts per widget type (deterministic)
- Mode-based organization (LIST, ADD, EDIT) matches human test patterns
- Trigger button duplication creates accurate test counts
- 100% consistent output across sessions

Components:
1. Enums - ScreenType, ScreenMode, WidgetType, ButtonType, ViewpointCategory, WidgetState
2. Templates - Static test count templates and utility functions
3. Components - TestItem, ViewpointPlan, WidgetTestPlan, ButtonTestPlan, etc.
4. MindMapModel - Main model combining all components

SC-011 Verified Test Counts:
- LIST: 79 tests
- ADD: 72 tests
- EDIT: 46 tests
- TOTAL: 197 tests (100% match with human tests)

Usage:
    from workflow_client.models.mindmap import (
        MindMapModel,
        ModeTestPlan,
        WidgetTestPlan,
        ScreenType,
        ScreenMode,
        WidgetType,
        create_empty_mindmap,
        create_mindmap_for_crud,
    )

    # Create a MindMap
    mindmap = create_mindmap_for_crud(
        plan_id="PLAN-001",
        screen_id="SC-011",
        screen_name="アカウント管理"
    )

    # Or create empty and build manually
    mindmap = create_empty_mindmap("PLAN-001", "SC-011", "アカウント管理")
"""

# Enums
from .enums import (
    ScreenType,
    ScreenMode,
    WidgetType,
    ButtonType,
    ViewpointCategory,
    WidgetState,
)

# Template Constants
from .templates import (
    # Test count constants
    WIDGET_TEST_COUNTS,
    WIDGET_APPLICABLE_MODES,
    LIST_MODE_FIXED_TESTS,
    LIST_MODE_TOTAL_FIXED,
    ADD_MODE_FIXED_TESTS,
    ADD_MODE_TOTAL_FIXED,
    EDIT_MODE_FIXED_TESTS,
    EDIT_MODE_TOTAL_FIXED,
    VIEW_MODE_FIXED_TESTS,
    VIEW_MODE_TOTAL_FIXED,
    MODE_VALIDATION_TRIGGERS,
    DT_COMBINATIONS,
    DT_ROW_MULTIPLIER,
    CONSTRAINT_PLACEHOLDERS,
    # Utility functions
    get_widget_test_count,
    get_applicable_modes,
    get_mode_fixed_tests,
    get_dt_test_count,
    calculate_trigger_tests,
)

# Components
from .components import (
    TestItem,
    ViewpointPlan,
    WidgetConstraints,
    WidgetTestPlan,
    ButtonTestPlan,
    DTReference,
    FixedTests,
    ModeTestPlan,
)

# Main MindMap Model
from .mindmap import (
    MindMapModel,
    MindMap,  # Backwards compatibility alias
    create_empty_mindmap,
    create_mindmap_for_crud,
)


__all__ = [
    # Enums
    "ScreenType",
    "ScreenMode",
    "WidgetType",
    "ButtonType",
    "ViewpointCategory",
    "WidgetState",

    # Template Constants
    "WIDGET_TEST_COUNTS",
    "WIDGET_APPLICABLE_MODES",
    "LIST_MODE_FIXED_TESTS",
    "LIST_MODE_TOTAL_FIXED",
    "ADD_MODE_FIXED_TESTS",
    "ADD_MODE_TOTAL_FIXED",
    "EDIT_MODE_FIXED_TESTS",
    "EDIT_MODE_TOTAL_FIXED",
    "VIEW_MODE_FIXED_TESTS",
    "VIEW_MODE_TOTAL_FIXED",
    "MODE_VALIDATION_TRIGGERS",
    "DT_COMBINATIONS",
    "DT_ROW_MULTIPLIER",
    "CONSTRAINT_PLACEHOLDERS",

    # Utility Functions
    "get_widget_test_count",
    "get_applicable_modes",
    "get_mode_fixed_tests",
    "get_dt_test_count",
    "calculate_trigger_tests",

    # Components
    "TestItem",
    "ViewpointPlan",
    "WidgetConstraints",
    "WidgetTestPlan",
    "ButtonTestPlan",
    "DTReference",
    "FixedTests",
    "ModeTestPlan",

    # Main Model
    "MindMapModel",
    "MindMap",  # Backwards compatibility alias
    "create_empty_mindmap",
    "create_mindmap_for_crud",
]
