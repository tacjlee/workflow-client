"""
AST Model - Main Abstract Syntax Tree Model.

Combines all 8 components into the complete AST structure
that is passed between Planner, Executor, and Validator via Plan Contract.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .screen_classification import ScreenClassification, OutputFileMapping
from .widget_registry import WidgetRegistry, Widget, ModeBehavior
from .viewpoint_mapping import WidgetViewpointMapping, ViewpointMapping, TestDataSample
from .test_scenarios import TestScenario, NavigationStep, ProcedureStep, PreCondition, TestGroup
from .decision_tables import DecisionTable, DTCondition, DTSubTable, DTSubTableRow, ExpansionStep, PostAction
from .business_rules import BusinessRules, BusinessRule, Message
from .sql_verifications import SqlVerification
from .expected_count import ExpectedTestCount, CountBreakdown, ValidationRule
from .enums import ScreenType, WidgetType, MessageType, DisplayStyle, ScenarioCategory
# v2.1 models
from .test_case_id import TestCaseIdRule
from .expected_output import ExpectedOutput, MessageRef, DisplayFormat


class AstModel(BaseModel):
    """
    AST Model - Complete Abstract Syntax Tree for PEV Architecture.

    This is the contract between Planner, Executor, and Validator,
    validated by Plan Contract.

    Components:
    1. screen_classification - Screen metadata and output file mapping
    2. widget_registry - Master widget inventory
    3. widget_viewpoint_mapping - Viewpoints with test data samples
    4. test_scenarios - Scenario definitions
    5. decision_tables - Role/mode combination matrices
    6. business_rules - Rules and MSG-ID message registry
    7. sql_verifications - Database assertion queries
    8. expected_testcase_count - Validation metrics
    """
    model_config = ConfigDict(use_enum_values=True)

    # Metadata
    version: str = Field(default="2.1", description="AST schema version")
    plan_id: str = Field(..., description="Unique plan identifier")
    created_at: Optional[str] = Field(None, description="ISO timestamp")

    # Source document reference
    source_document: Optional[str] = Field(None, description="Source design document path")
    source_document_version: Optional[str] = Field(None, description="Document version")

    # 8 Components
    screen_classification: ScreenClassification
    widget_registry: WidgetRegistry
    widget_viewpoint_mapping: List[WidgetViewpointMapping] = Field(default_factory=list)
    test_scenarios: List[TestScenario] = Field(default_factory=list)
    decision_tables: List[DecisionTable] = Field(default_factory=list)
    business_rules: BusinessRules = Field(default_factory=BusinessRules)
    sql_verifications: List[SqlVerification] = Field(default_factory=list)
    expected_testcase_count: ExpectedTestCount

    # Validation metadata (populated by Plan Contract)
    validation_status: Optional[str] = Field(None, description="Plan Contract validation status")
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)

    # ==================== Widget Methods ====================

    def get_widget(self, widget_id: str) -> Optional[Widget]:
        """Get widget from registry by ID."""
        return self.widget_registry.get_widget(widget_id)

    def get_all_widget_ids(self) -> List[str]:
        """Get all widget IDs from registry."""
        return self.widget_registry.get_widget_ids()

    # ==================== Viewpoint Methods ====================

    def get_viewpoints_for_widget(self, widget_id: str) -> List[ViewpointMapping]:
        """Get all viewpoints mapped to a widget."""
        for mapping in self.widget_viewpoint_mapping:
            if mapping.widget_id == widget_id:
                return mapping.viewpoints
        return []

    def get_widget_viewpoint_mapping(self, widget_id: str) -> Optional[WidgetViewpointMapping]:
        """Get the viewpoint mapping for a widget."""
        for mapping in self.widget_viewpoint_mapping:
            if mapping.widget_id == widget_id:
                return mapping
        return None

    # ==================== Scenario Methods ====================

    def get_scenario(self, scenario_id: str) -> Optional[TestScenario]:
        """Get scenario by ID."""
        for s in self.test_scenarios:
            if s.scenario_id == scenario_id:
                return s
        return None

    def get_scenarios_by_category(self, category: ScenarioCategory) -> List[TestScenario]:
        """Get all scenarios of a specific category."""
        return [s for s in self.test_scenarios if s.category == category]

    # ==================== Decision Table Methods ====================

    def get_decision_table(self, dt_id: str) -> Optional[DecisionTable]:
        """Get decision table by ID."""
        for dt in self.decision_tables:
            if dt.dt_id == dt_id:
                return dt
        return None

    def get_decision_tables_for_scenario(self, scenario_id: str) -> List[DecisionTable]:
        """Get all decision tables that apply to a scenario."""
        return [dt for dt in self.decision_tables if scenario_id in dt.applies_to_scenarios]

    def get_total_dt_combinations(self) -> int:
        """Get total number of decision table combinations (v2.0 behavior: counts rows)."""
        return sum(dt.get_total_combinations() for dt in self.decision_tables)

    def get_total_dt_expanded_count(self) -> int:
        """Get total number of DT test cases after expansion (v2.1)."""
        return sum(dt.get_total_expanded_test_count() for dt in self.decision_tables)

    # ==================== v2.1 Test Case ID Methods ====================

    def get_test_case_id_rule(self) -> Optional[TestCaseIdRule]:
        """Get the test case ID rule from screen classification (v2.1)."""
        return self.screen_classification.test_case_id_rule

    def generate_test_case_id(self, counter: int) -> Optional[str]:
        """
        Generate a test case ID using the configured rule (v2.1).

        Args:
            counter: Counter value for the ID

        Returns:
            Generated ID string or None if no rule configured
        """
        rule = self.get_test_case_id_rule()
        if rule:
            return rule.generate_id(counter)
        return None

    # ==================== Message Methods ====================

    def get_message(self, message_id: str) -> Optional[Message]:
        """Get message from business rules registry."""
        return self.business_rules.get_message(message_id)

    def resolve_message(self, message_ref: Optional[str]) -> Optional[str]:
        """Resolve a message reference to actual text."""
        return self.business_rules.resolve_message_ref(message_ref)

    # ==================== SQL Verification Methods ====================

    def get_sql_verification(self, sql_id: str) -> Optional[SqlVerification]:
        """Get SQL verification by ID."""
        for sql in self.sql_verifications:
            if sql.sql_id == sql_id:
                return sql
        return None

    def get_sql_verifications_for_scenario(self, scenario_id: str) -> List[SqlVerification]:
        """Get all SQL verifications that apply to a scenario."""
        return [sql for sql in self.sql_verifications if scenario_id in sql.applies_to_scenarios]

    # ==================== Validation Methods ====================

    def is_valid(self) -> bool:
        """Check if AST passed Plan Contract validation."""
        return self.validation_status == "VALID"

    def has_errors(self) -> bool:
        """Check if AST has validation errors."""
        return len(self.validation_errors) > 0

    def has_warnings(self) -> bool:
        """Check if AST has validation warnings."""
        return len(self.validation_warnings) > 0

    # ==================== Summary Methods ====================

    def get_summary(self) -> dict:
        """Get a summary of the AST contents."""
        summary = {
            "plan_id": self.plan_id,
            "version": self.version,
            "screen_id": self.screen_classification.screen_id,
            "screen_name": self.screen_classification.screen_name,
            "screen_type": self.screen_classification.screen_type,
            "widget_count": len(self.widget_registry.widgets),
            "viewpoint_mapping_count": len(self.widget_viewpoint_mapping),
            "scenario_count": len(self.test_scenarios),
            "decision_table_count": len(self.decision_tables),
            "dt_combinations": self.get_total_dt_combinations(),
            "business_rule_count": len(self.business_rules.rules),
            "message_count": len(self.business_rules.messages),
            "sql_verification_count": len(self.sql_verifications),
            "expected_test_count": self.expected_testcase_count.total,
            "validation_status": self.validation_status,
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings),
        }
        # v2.1: Add expanded test count if different from combinations
        dt_expanded = self.get_total_dt_expanded_count()
        if dt_expanded != summary["dt_combinations"]:
            summary["dt_expanded_test_count"] = dt_expanded
        # v2.1: Include test case ID rule info
        if self.screen_classification.test_case_id_rule:
            summary["has_test_case_id_rule"] = True
        return summary


# Backwards compatibility alias
ASTv2 = AstModel


def create_empty_ast(plan_id: str, screen_id: str, screen_name: str) -> AstModel:
    """Create an empty AST structure with required fields."""
    return AstModel(
        plan_id=plan_id,
        screen_classification=ScreenClassification(
            screen_id=screen_id,
            screen_name=screen_name,
            screen_type=ScreenType.FORM
        ),
        widget_registry=WidgetRegistry(),
        expected_testcase_count=ExpectedTestCount(total=0)
    )
