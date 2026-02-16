"""
MindMap Model - Main Mind Map Model for PEV Architecture.

Replaces AST v2.2 with deterministic template-based test planning.
This is the contract between Planner, Executor, and Validator.

Key differences from AST v2.2:
- Templates define exact test counts per widget type
- Mode-based organization matches human test patterns
- Trigger button duplication creates accurate test counts
- 100% deterministic output (same input = same output always)

Reference: testing/architecture/MindMap_v2.3_Architecture.md
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from .enums import ScreenType, ScreenMode, WidgetType
from .components import (
    ModeTestPlan,
    WidgetTestPlan,
    ButtonTestPlan,
    DTReference,
    FixedTests,
    ViewpointPlan,
    TestItem,
    WidgetConstraints,
)
from .templates import (
    MODE_VALIDATION_TRIGGERS,
    LIST_MODE_FIXED_TESTS,
    ADD_MODE_FIXED_TESTS,
    EDIT_MODE_FIXED_TESTS,
)


class MindMapModel(BaseModel):
    """
    MindMap Model - Deterministic Test Plan for PEV Architecture.

    This replaces AST v2.2 for test case generation. It is the contract
    between Planner, Executor, and Validator services.

    Key Features:
    - Mode-based organization (LIST, ADD, EDIT)
    - Template-driven test counts
    - Trigger button duplication for validation tests
    - 100% deterministic output
    """
    model_config = ConfigDict(use_enum_values=True)

    # Metadata
    version: str = Field(default="2.3", description="MindMap schema version")
    plan_id: str = Field(..., description="Unique plan identifier")
    created_at: Optional[str] = Field(None, description="ISO timestamp")
    generation_method: str = Field(default="MIND_MAP_TEMPLATE", description="Generation method")

    # Source document reference
    source_document: Optional[str] = Field(None, description="Source design document path")
    source_document_version: Optional[str] = Field(None, description="Document version")

    # Screen identification
    screen_id: str = Field(..., description="Screen identifier (e.g., SC-011)")
    screen_name: str = Field(..., description="Screen name")
    screen_name_en: Optional[str] = Field(None, description="Screen name in English")
    screen_type: ScreenType = Field(..., description="Screen type")

    # Mode-organized test plans (matches human organization)
    modes: List[ModeTestPlan] = Field(default_factory=list)

    # Validation metadata (populated by Plan Contract)
    validation_status: Optional[str] = Field(None, description="Plan Contract validation status")
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)

    # ==================== Computed Properties ====================

    @property
    def total_widgets(self) -> int:
        """Get total number of widgets across all modes."""
        return sum(len(mode.widgets) for mode in self.modes)

    @property
    def total_buttons(self) -> int:
        """Get total number of buttons across all modes."""
        return sum(len(mode.buttons) for mode in self.modes)

    @property
    def total_viewpoints(self) -> int:
        """Get total number of viewpoints across all modes."""
        total = 0
        for mode in self.modes:
            for widget in mode.widgets:
                total += len(widget.viewpoints)
            for button in mode.buttons:
                total += len(button.viewpoints)
        return total

    @property
    def total_expected_tests(self) -> int:
        """Get total expected tests (deterministic from templates)."""
        return sum(mode.total_tests for mode in self.modes)

    # ==================== Mode Methods ====================

    def get_mode(self, mode: ScreenMode) -> Optional[ModeTestPlan]:
        """Get a specific mode's test plan."""
        for m in self.modes:
            if m.mode == mode:
                return m
        return None

    def has_mode(self, mode: ScreenMode) -> bool:
        """Check if a mode exists."""
        return self.get_mode(mode) is not None

    def get_mode_names(self) -> List[str]:
        """Get list of mode names."""
        return [m.mode.value if isinstance(m.mode, ScreenMode) else m.mode for m in self.modes]

    # ==================== Widget Methods ====================

    def get_widget(self, widget_id: str) -> Optional[WidgetTestPlan]:
        """Get widget by ID across all modes."""
        for mode in self.modes:
            widget = mode.get_widget(widget_id)
            if widget:
                return widget
        return None

    def get_all_widget_ids(self) -> List[str]:
        """Get all widget IDs across all modes."""
        ids = []
        for mode in self.modes:
            ids.extend([w.widget_id for w in mode.widgets])
        return list(set(ids))  # Remove duplicates

    def get_widgets_by_type(self, widget_type: WidgetType) -> List[WidgetTestPlan]:
        """Get all widgets of a specific type."""
        widgets = []
        for mode in self.modes:
            for w in mode.widgets:
                if w.widget_type == widget_type:
                    widgets.append(w)
        return widgets

    # ==================== Breakdown Methods ====================

    def get_breakdown(self) -> Dict[str, Any]:
        """Get test count breakdown by mode."""
        breakdown = {}
        for mode in self.modes:
            mode_name = mode.mode.value if isinstance(mode.mode, ScreenMode) else mode.mode
            breakdown[mode_name] = {
                "widget_tests": mode.widget_tests,
                "button_tests": mode.button_tests,
                "dt_tests": mode.dt_tests,
                "fixed_tests": mode.fixed_tests.total,
                "total": mode.total_tests,
            }
        breakdown["grand_total"] = self.total_expected_tests
        return breakdown

    def get_detailed_breakdown(self) -> Dict[str, Any]:
        """Get detailed test count breakdown."""
        breakdown = {
            "screen_id": self.screen_id,
            "screen_name": self.screen_name,
            "screen_type": self.screen_type.value if isinstance(self.screen_type, ScreenType) else self.screen_type,
            "version": self.version,
            "modes": {},
            "totals": {
                "widgets": self.total_widgets,
                "buttons": self.total_buttons,
                "viewpoints": self.total_viewpoints,
                "expected_tests": self.total_expected_tests,
            }
        }

        for mode in self.modes:
            mode_breakdown = {
                "widgets": [
                    {
                        "widget_id": w.widget_id,
                        "widget_type": w.widget_type.value if isinstance(w.widget_type, WidgetType) else w.widget_type,
                        "label": w.label,
                        "tests": w.total_tests,
                    }
                    for w in mode.widgets
                ],
                "buttons": [
                    {
                        "button_id": b.button_id,
                        "label": b.label,
                        "tests": b.total_tests,
                    }
                    for b in mode.buttons
                ],
                "decision_tables": [
                    {
                        "dt_id": dt.dt_id,
                        "role_context": dt.role_context,
                        "combinations": dt.combinations,
                        "tests": dt.total_tests,
                    }
                    for dt in mode.decision_tables
                ],
                "fixed_tests": mode.fixed_tests.model_dump(),
                "subtotals": {
                    "widget_tests": mode.widget_tests,
                    "button_tests": mode.button_tests,
                    "dt_tests": mode.dt_tests,
                    "fixed_tests": mode.fixed_tests.total,
                    "total": mode.total_tests,
                }
            }
            mode_name = mode.mode.value if isinstance(mode.mode, ScreenMode) else mode.mode
            breakdown["modes"][mode_name] = mode_breakdown

        return breakdown

    # ==================== Validation Methods ====================

    def validate(self) -> List[str]:
        """
        Validate the MindMap structure.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate required fields
        if not self.plan_id:
            errors.append("plan_id is required")
        if not self.screen_id:
            errors.append("screen_id is required")
        if not self.screen_name:
            errors.append("screen_name is required")

        # Validate modes
        if not self.modes:
            errors.append("At least one mode is required")

        mode_names = set()
        for mode in self.modes:
            mode_name = mode.mode.value if isinstance(mode.mode, ScreenMode) else mode.mode
            if mode_name in mode_names:
                errors.append(f"Duplicate mode: {mode_name}")
            mode_names.add(mode_name)

            # Validate mode contents
            mode_errors = self._validate_mode(mode)
            errors.extend(mode_errors)

        return errors

    def _validate_mode(self, mode: ModeTestPlan) -> List[str]:
        """Validate a single mode's test plan."""
        errors = []
        mode_name = mode.mode.value if isinstance(mode.mode, ScreenMode) else mode.mode
        prefix = f"Mode {mode_name}: "

        # Check widget IDs are unique within mode
        widget_ids = set()
        for widget in mode.widgets:
            if widget.widget_id in widget_ids:
                errors.append(f"{prefix}Duplicate widget_id: {widget.widget_id}")
            widget_ids.add(widget.widget_id)

        # Check button IDs are unique within mode
        button_ids = set()
        for button in mode.buttons:
            if button.button_id in button_ids:
                errors.append(f"{prefix}Duplicate button_id: {button.button_id}")
            button_ids.add(button.button_id)

        return errors

    def is_valid(self) -> bool:
        """Check if the MindMap is valid."""
        return len(self.validate()) == 0

    def has_errors(self) -> bool:
        """Check if MindMap has validation errors."""
        return len(self.validation_errors) > 0

    def has_warnings(self) -> bool:
        """Check if MindMap has validation warnings."""
        return len(self.validation_warnings) > 0

    # ==================== Summary Methods ====================

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the MindMap contents."""
        summary = {
            "plan_id": self.plan_id,
            "version": self.version,
            "screen_id": self.screen_id,
            "screen_name": self.screen_name,
            "screen_type": self.screen_type.value if isinstance(self.screen_type, ScreenType) else self.screen_type,
            "mode_count": len(self.modes),
            "modes": self.get_mode_names(),
            "widget_count": self.total_widgets,
            "button_count": self.total_buttons,
            "viewpoint_count": self.total_viewpoints,
            "expected_test_count": self.total_expected_tests,
            "validation_status": self.validation_status,
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings),
            "breakdown": self.get_breakdown(),
        }
        return summary

    def get_summary_text(self) -> str:
        """Get a human-readable summary of the MindMap."""
        lines = [
            f"MindMap: {self.screen_id} - {self.screen_name}",
            f"Type: {self.screen_type.value if isinstance(self.screen_type, ScreenType) else self.screen_type}",
            f"Version: {self.version}",
            f"Total Widgets: {self.total_widgets}",
            f"Total Viewpoints: {self.total_viewpoints}",
            f"Total Expected Tests: {self.total_expected_tests}",
            "",
            "Breakdown by Mode:",
        ]

        for mode in self.modes:
            mode_name = mode.mode.value if isinstance(mode.mode, ScreenMode) else mode.mode
            lines.append(f"  {mode_name}:")
            lines.append(f"    Widgets: {len(mode.widgets)} ({mode.widget_tests} tests)")
            lines.append(f"    Buttons: {len(mode.buttons)} ({mode.button_tests} tests)")
            lines.append(f"    Decision Tables: {len(mode.decision_tables)} ({mode.dt_tests} tests)")
            lines.append(f"    Fixed Tests: {mode.fixed_tests.total}")
            lines.append(f"    Total: {mode.total_tests}")

        return "\n".join(lines)


# Backwards compatibility alias
MindMap = MindMapModel


def create_empty_mindmap(plan_id: str, screen_id: str, screen_name: str) -> MindMapModel:
    """Create an empty MindMap structure with required fields."""
    return MindMapModel(
        plan_id=plan_id,
        screen_id=screen_id,
        screen_name=screen_name,
        screen_type=ScreenType.CRUD_MASTER,
    )


def create_mindmap_for_crud(
    plan_id: str,
    screen_id: str,
    screen_name: str,
    include_list: bool = True,
    include_add: bool = True,
    include_edit: bool = True,
) -> MindMapModel:
    """
    Create a MindMap structure for a CRUD screen with default fixed tests.

    Args:
        plan_id: Unique plan identifier
        screen_id: Screen identifier
        screen_name: Screen name
        include_list: Include LIST mode
        include_add: Include ADD mode
        include_edit: Include EDIT mode

    Returns:
        MindMapModel with modes and default fixed tests
    """
    modes = []

    if include_list:
        modes.append(ModeTestPlan(
            mode=ScreenMode.LIST,
            validation_triggers=MODE_VALIDATION_TRIGGERS[ScreenMode.LIST.value],
            fixed_tests=FixedTests(**LIST_MODE_FIXED_TESTS),
        ))

    if include_add:
        modes.append(ModeTestPlan(
            mode=ScreenMode.ADD,
            validation_triggers=MODE_VALIDATION_TRIGGERS[ScreenMode.ADD.value],
            fixed_tests=FixedTests(**ADD_MODE_FIXED_TESTS),
        ))

    if include_edit:
        modes.append(ModeTestPlan(
            mode=ScreenMode.EDIT,
            validation_triggers=MODE_VALIDATION_TRIGGERS[ScreenMode.EDIT.value],
            fixed_tests=FixedTests(**EDIT_MODE_FIXED_TESTS),
        ))

    return MindMapModel(
        plan_id=plan_id,
        screen_id=screen_id,
        screen_name=screen_name,
        screen_type=ScreenType.CRUD_MASTER,
        modes=modes,
    )
