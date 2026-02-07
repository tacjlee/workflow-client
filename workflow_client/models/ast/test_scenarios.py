"""
AST Model Component 4: Test Scenarios.

Defines test scenarios with navigation, pre-conditions, and test groups.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .enums import ScenarioCategory


class ProcedureStep(BaseModel):
    """
    Procedure step for test execution.

    Enhanced in v2.1 with sub_steps, expected_intermediate, target_widget, and data_column_ref.
    """
    step_number: int
    action: str = Field(..., description="Action description")
    action_vi: Optional[str] = Field(None, description="Action in Vietnamese")
    target: Optional[str] = Field(None, description="Target element or URL")

    # v2.1: Enhanced procedure step fields
    sub_steps: List[str] = Field(
        default_factory=list,
        description="Nested sub-actions under this step (v2.1)"
    )
    expected_intermediate: Optional[str] = Field(
        None,
        description="Expected result after this step (v2.1)"
    )
    target_widget: Optional[str] = Field(
        None,
        description="Widget ID this step interacts with (v2.1)"
    )
    data_column_ref: Optional[str] = Field(
        None,
        description="Test Data column reference, e.g., 'D' for 'giá trị mô tả cột D' (v2.1)"
    )


# Backward compatibility alias
NavigationStep = ProcedureStep


class PreCondition(BaseModel):
    """Pre-condition for a scenario."""
    condition_id: str
    description: str
    description_vi: Optional[str] = None
    setup_required: Optional[str] = Field(None, description="Setup steps if any")

    # v2.1: Structured pre-condition fields
    role_requirement: Optional[str] = Field(
        None,
        description="Required login role (e.g., 'SystemAdmin', 'BackOffice', 'Operator') (v2.1)"
    )
    system_state: Optional[str] = Field(
        None,
        description="Required UI/system state (e.g., 'popup_open', 'dialog_open') (v2.1)"
    )
    data_setup: Optional[str] = Field(
        None,
        description="Data preconditions (e.g., 'data_not_exists', 'data_exists') (v2.1)"
    )
    applies_to_dt: Optional[str] = Field(
        None,
        description="Link to specific DT sub-table (e.g., 'DT1', 'DT2') (v2.1)"
    )


class TestGroup(BaseModel):
    """Group of related tests within a scenario."""
    group_id: str
    group_name: str
    widgets: List[str] = Field(default_factory=list, description="Widget IDs in this group")
    viewpoint_refs: List[str] = Field(default_factory=list, description="Viewpoint IDs to test")


class TestScenario(BaseModel):
    """
    Component 4: Test Scenario

    Defines a test scenario with navigation, pre-conditions, and test groups.
    """
    model_config = ConfigDict(use_enum_values=True)

    scenario_id: str = Field(..., description="Scenario identifier")
    scenario_name: str = Field(..., description="Scenario name")
    scenario_name_vi: Optional[str] = Field(None, description="Scenario name in Vietnamese")
    description: Optional[str] = None

    category: ScenarioCategory = Field(..., description="Scenario category")
    priority: str = Field(default="medium")

    navigation: List[ProcedureStep] = Field(
        default_factory=list,
        description="Steps to reach this scenario (ProcedureStep in v2.1)"
    )

    pre_conditions: List[PreCondition] = Field(
        default_factory=list,
        description="Required pre-conditions"
    )

    target_widgets: List[str] = Field(
        default_factory=list,
        description="Widget IDs involved in this scenario"
    )

    test_groups: List[TestGroup] = Field(
        default_factory=list,
        description="Groups of tests within this scenario"
    )

    decision_table_refs: List[str] = Field(
        default_factory=list,
        description="References to decision tables for this scenario"
    )

    expected_outcome: Optional[str] = None

    def has_decision_tables(self) -> bool:
        """Check if scenario uses decision tables."""
        return len(self.decision_table_refs) > 0

    def get_all_widget_ids(self) -> List[str]:
        """Get all widget IDs from target_widgets and test_groups."""
        widget_ids = set(self.target_widgets)
        for group in self.test_groups:
            widget_ids.update(group.widgets)
        return list(widget_ids)
