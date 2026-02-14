"""
AST Model - Abstract Syntax Tree for PEV Architecture.

This package defines the 9-component Abstract Syntax Tree (AST) structure
that the Planner generates and passes to Executor and Validator via Plan Contract.

Components:
1. ScreenClassification - Screen metadata and output file mapping
2. WidgetRegistry - Master widget inventory with constraints
3. WidgetViewpointMapping - Viewpoints with test data samples
4. TestScenarios - Scenario definitions with navigation and groups
5. DecisionTables - Role/mode combination matrices
6. BusinessRules - Rules and MSG-ID message registry
7. SqlVerifications - Database assertion queries
8. ExpectedTestCount - Validation metrics and thresholds
9. TestGenerationRules - Formula and rules for test case generation (v2.2)

v2.1 Enhancements:
- TestCaseIdRule - Test case ID generation pattern ([011-XX])
- ExpectedOutput - Composite model for MSG + SQL + display format
- ExpansionStep, PostAction - Decision table row expansion
- ViewpointMapping.viewpoint_category, recommend_items
- ProcedureStep (enhanced NavigationStep) with sub_steps
- PreCondition with role_requirement, system_state, data_setup
- Message with display_color, display_position

v2.2 Enhancements:
- TestGenerationRules - How Executor should generate test cases
- GenerationStrategy - Strategy enum (PER_WIDGET, PER_SCENARIO, etc.)
- ScenarioGenerationRule - Per-category generation rules
- FormulaComponent - Breakdown of expected count calculation

Usage:
    from workflow_client.models.ast import AstModel, ScreenClassification, WidgetRegistry

    # Create an AST
    ast = AstModel(
        plan_id="PLAN-001",
        screen_classification=ScreenClassification(...),
        widget_registry=WidgetRegistry(...),
        expected_testcase_count=ExpectedTestCount(total=50)
    )

    # Or use the factory function
    ast = create_empty_ast("PLAN-001", "SC-011", "アカウント管理")
"""

# Enums
from .enums import (
    ScreenType,
    ScreenMode,
    WidgetType,
    MessageType,
    DisplayStyle,
    ScenarioCategory,
)

# Component 1: Screen Classification
from .screen_classification import (
    ScreenClassification,
    OutputFileMapping,
)

# Component 2: Widget Registry
from .widget_registry import (
    WidgetRegistry,
    Widget,
    ModeBehavior,
)

# Component 3: Widget-Viewpoint Mapping
from .viewpoint_mapping import (
    WidgetViewpointMapping,
    ViewpointMapping,
    TestDataSample,
)

# Component 4: Test Scenarios
from .test_scenarios import (
    TestScenario,
    NavigationStep,
    ProcedureStep,  # v2.1: Enhanced NavigationStep
    PreCondition,
    TestGroup,
)

# Component 5: Decision Tables
from .decision_tables import (
    DecisionTable,
    DTCondition,
    DTSubTable,
    DTSubTableRow,
    ExpansionStep,  # v2.1
    PostAction,  # v2.1
)

# Component 6: Business Rules
from .business_rules import (
    BusinessRules,
    BusinessRule,
    Message,
)

# Component 7: SQL Verifications
from .sql_verifications import (
    SqlVerification,
)

# Component 8: Expected Test Count
from .expected_count import (
    ExpectedTestCount,
    CountBreakdown,
    ValidationRule,
)

# v2.1: Test Case ID Rule
from .test_case_id import (
    TestCaseIdRule,
)

# v2.1: Expected Output Models
from .expected_output import (
    ExpectedOutput,
    MessageRef,
    DisplayFormat,
)

# v2.2: Component 9 - Test Generation Rules
from .test_generation_rules import (
    TestGenerationRules,
    GenerationStrategy,
    ScenarioGenerationRule,
    FormulaComponent,
)

# Main AST Model
from .ast import (
    AstModel,
    ASTv2,  # Backwards compatibility alias
    create_empty_ast,
)

__all__ = [
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
    "ProcedureStep",  # v2.1: Enhanced NavigationStep
    "PreCondition",
    "TestGroup",

    # Component 5
    "DecisionTable",
    "DTCondition",
    "DTSubTable",
    "DTSubTableRow",
    "ExpansionStep",  # v2.1
    "PostAction",  # v2.1

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

    # v2.1: Test Case ID Rule
    "TestCaseIdRule",

    # v2.1: Expected Output Models
    "ExpectedOutput",
    "MessageRef",
    "DisplayFormat",

    # v2.2: Component 9 - Test Generation Rules
    "TestGenerationRules",
    "GenerationStrategy",
    "ScenarioGenerationRule",
    "FormulaComponent",

    # Main AST
    "AstModel",
    "ASTv2",  # Backwards compatibility
    "create_empty_ast",
]
