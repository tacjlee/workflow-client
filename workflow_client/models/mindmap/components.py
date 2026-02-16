"""
MindMap Model Components.

Data classes for MindMap structure - test items, viewpoints, widgets,
buttons, decision tables, and mode test plans.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from .enums import (
    ScreenMode,
    WidgetType,
    ButtonType,
    ViewpointCategory,
    WidgetState,
)


# =============================================================================
# TEST ITEM
# =============================================================================

class TestItem(BaseModel):
    """A single test item within a viewpoint."""
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Unique test item identifier")
    item: str = Field(..., description="Test item description")
    procedure: str = Field(default="", description="Test procedure steps")
    expected: str = Field(default="", description="Expected result")
    test_data: str = Field(default="", description="Sample test data")
    priority: str = Field(default="Medium", description="Test priority")


# =============================================================================
# VIEWPOINT PLAN
# =============================================================================

class ViewpointPlan(BaseModel):
    """A viewpoint containing multiple test items."""
    model_config = ConfigDict(use_enum_values=True)

    viewpoint_id: str = Field(..., description="Unique viewpoint identifier")
    name: str = Field(..., description="Viewpoint name")
    category: ViewpointCategory = Field(..., description="Viewpoint category")
    test_items: List[TestItem] = Field(default_factory=list)
    applicable_modes: List[ScreenMode] = Field(default_factory=list)

    @property
    def test_count(self) -> int:
        """Get the number of test items."""
        return len(self.test_items)


# =============================================================================
# WIDGET CONSTRAINTS
# =============================================================================

class WidgetConstraints(BaseModel):
    """Constraints extracted from design document."""
    model_config = ConfigDict(use_enum_values=True)

    max_length: Optional[int] = Field(None, description="Maximum character length")
    min_length: Optional[int] = Field(None, description="Minimum character length")
    required: bool = Field(default=False, description="Whether field is required")
    pattern: Optional[str] = Field(None, description="Regex pattern")
    min_value: Optional[float] = Field(None, description="Minimum numeric value")
    max_value: Optional[float] = Field(None, description="Maximum numeric value")
    allowed_values: List[str] = Field(default_factory=list, description="Allowed values for dropdown/select")
    default_value: Optional[str] = Field(None, description="Default value")
    placeholder: Optional[str] = Field(None, description="Placeholder text")


# =============================================================================
# WIDGET TEST PLAN
# =============================================================================

class WidgetTestPlan(BaseModel):
    """Test plan for a widget - derived from templates."""
    model_config = ConfigDict(use_enum_values=True)

    widget_id: str = Field(..., description="Widget identifier (e.g., WGT-11)")
    widget_type: WidgetType = Field(..., description="Widget type")
    widget_name: str = Field(..., description="Widget name (e.g., email_input)")
    label: str = Field(..., description="Display label (e.g., メールアドレス)")
    constraints: WidgetConstraints = Field(default_factory=WidgetConstraints)
    viewpoints: List[ViewpointPlan] = Field(default_factory=list)
    trigger_buttons: List[str] = Field(default_factory=list, description="Buttons that trigger validation")
    mode_states: Dict[str, WidgetState] = Field(default_factory=dict, description="State per mode")

    @property
    def total_tests(self) -> int:
        """Get total tests from all viewpoints."""
        return sum(vp.test_count for vp in self.viewpoints)


# =============================================================================
# BUTTON TEST PLAN
# =============================================================================

class ButtonTestPlan(BaseModel):
    """Test plan for a button."""
    model_config = ConfigDict(use_enum_values=True)

    button_id: str = Field(..., description="Button identifier")
    button_type: ButtonType = Field(..., description="Button type")
    button_name: str = Field(..., description="Button name")
    label: str = Field(..., description="Display label")
    viewpoints: List[ViewpointPlan] = Field(default_factory=list)

    @property
    def total_tests(self) -> int:
        """Get total tests from all viewpoints."""
        return sum(vp.test_count for vp in self.viewpoints)


# =============================================================================
# DECISION TABLE REFERENCE
# =============================================================================

class DTReference(BaseModel):
    """Reference to a decision table with test count."""
    model_config = ConfigDict(use_enum_values=True)

    dt_id: str = Field(..., description="Decision table identifier")
    name: str = Field(..., description="Decision table name")
    role_context: str = Field(..., description="Role context (e.g., System_Admin)")
    combinations: int = Field(..., description="Number of DT combinations")
    row_multiplier: int = Field(default=2, description="Tests per combination (action + verify)")
    roles: List[str] = Field(default_factory=list, description="Role combinations")

    @property
    def total_tests(self) -> int:
        """Get total tests from DT (combinations × multiplier)."""
        return self.combinations * self.row_multiplier


# =============================================================================
# FIXED TESTS
# =============================================================================

class FixedTests(BaseModel):
    """Fixed tests for a mode (not from widget templates)."""
    model_config = ConfigDict(use_enum_values=True)

    role_access_tests: int = Field(default=0, description="Role access tests")
    search_tests: int = Field(default=0, description="Search function tests")
    pagination_tests: int = Field(default=0, description="Pagination tests")
    sort_tests: int = Field(default=0, description="Sort tests")
    reset_tests: int = Field(default=0, description="Reset button tests")
    export_tests: int = Field(default=0, description="Export button tests")
    screen_transition_tests: int = Field(default=0, description="Screen transition tests")
    concurrent_tests: int = Field(default=0, description="Concurrent edit tests")
    db_error_tests: int = Field(default=0, description="DB error tests")
    double_click_tests: int = Field(default=0, description="Double-click prevention tests")
    gui_tests: int = Field(default=0, description="GUI layout tests")

    @property
    def total(self) -> int:
        """Get total fixed tests."""
        return (
            self.role_access_tests +
            self.search_tests +
            self.pagination_tests +
            self.sort_tests +
            self.reset_tests +
            self.export_tests +
            self.screen_transition_tests +
            self.concurrent_tests +
            self.db_error_tests +
            self.double_click_tests +
            self.gui_tests
        )


# =============================================================================
# MODE TEST PLAN
# =============================================================================

class ModeTestPlan(BaseModel):
    """Test plan for a screen mode (LIST, ADD, EDIT)."""
    model_config = ConfigDict(use_enum_values=True)

    mode: ScreenMode = Field(..., description="Screen mode")
    url_path: str = Field(default="", description="URL path")
    navigation_steps: str = Field(default="", description="Navigation steps to reach mode")
    widgets: List[WidgetTestPlan] = Field(default_factory=list)
    buttons: List[ButtonTestPlan] = Field(default_factory=list)
    decision_tables: List[DTReference] = Field(default_factory=list)
    fixed_tests: FixedTests = Field(default_factory=FixedTests)
    validation_triggers: List[str] = Field(default_factory=list, description="Buttons that trigger validation")

    @property
    def widget_tests(self) -> int:
        """Get total tests from widgets."""
        return sum(w.total_tests for w in self.widgets)

    @property
    def button_tests(self) -> int:
        """Get total tests from buttons."""
        return sum(b.total_tests for b in self.buttons)

    @property
    def dt_tests(self) -> int:
        """Get total tests from decision tables."""
        return sum(dt.total_tests for dt in self.decision_tables)

    @property
    def total_tests(self) -> int:
        """Get total tests for this mode."""
        return (
            self.widget_tests +
            self.button_tests +
            self.dt_tests +
            self.fixed_tests.total
        )

    def get_widget(self, widget_id: str) -> Optional[WidgetTestPlan]:
        """Get widget by ID."""
        for w in self.widgets:
            if w.widget_id == widget_id:
                return w
        return None

    def get_button(self, button_id: str) -> Optional[ButtonTestPlan]:
        """Get button by ID."""
        for b in self.buttons:
            if b.button_id == button_id:
                return b
        return None
