"""
MindMap Template Constants.

Static templates that define test counts per widget type and mode.
These templates encode human test patterns for deterministic test generation.

Reference: testing/architecture/MindMap_v2.3_Architecture.md
"""
from typing import Dict, List, Set, Union

from .enums import WidgetType, ScreenMode


# =============================================================================
# WIDGET TEST COUNTS - Tests per widget type per trigger button
# =============================================================================

WIDGET_TEST_COUNTS: Dict[str, int] = {
    WidgetType.EMAIL.value: 20,
    WidgetType.TEXT_INPUT.value: 12,
    WidgetType.PASSWORD.value: 12,
    WidgetType.NUMBER.value: 10,
    WidgetType.TEXTAREA.value: 12,
    WidgetType.DROPDOWN.value: 4,
    WidgetType.CHECKBOX.value: 3,
    WidgetType.RADIO.value: 3,
    WidgetType.DATE.value: 8,
    WidgetType.DATETIME.value: 10,
    WidgetType.FILE_UPLOAD.value: 6,
    WidgetType.SEARCH_BOX.value: 16,
    WidgetType.TABLE.value: 10,  # Sort tests per 5 columns
    WidgetType.BUTTON.value: 2,
    WidgetType.LINK.value: 2,
    WidgetType.LABEL.value: 1,
}


# =============================================================================
# WIDGET APPLICABLE MODES - Which modes each widget type applies to
# =============================================================================

WIDGET_APPLICABLE_MODES: Dict[str, List[str]] = {
    WidgetType.EMAIL.value: [ScreenMode.ADD.value],
    WidgetType.TEXT_INPUT.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.PASSWORD.value: [ScreenMode.ADD.value],
    WidgetType.NUMBER.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.TEXTAREA.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.DROPDOWN.value: [ScreenMode.LIST.value, ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.CHECKBOX.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.RADIO.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.DATE.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.DATETIME.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.FILE_UPLOAD.value: [ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.SEARCH_BOX.value: [ScreenMode.LIST.value],
    WidgetType.TABLE.value: [ScreenMode.LIST.value],
    WidgetType.BUTTON.value: [ScreenMode.LIST.value, ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.LINK.value: [ScreenMode.LIST.value, ScreenMode.ADD.value, ScreenMode.EDIT.value],
    WidgetType.LABEL.value: [ScreenMode.LIST.value, ScreenMode.ADD.value, ScreenMode.EDIT.value, ScreenMode.VIEW.value],
}


# =============================================================================
# MODE FIXED TESTS - Fixed test counts not from widget templates
# =============================================================================

# Fixed tests for LIST mode (keys match FixedTests model fields)
LIST_MODE_FIXED_TESTS: Dict[str, int] = {
    "role_access_tests": 4,       # 4 roles tested
    "search_tests": 15,           # Search function tests
    "pagination_tests": 14,       # Pagination tests
    "sort_tests": 10,             # 5 columns × 2 clicks
    "reset_tests": 6,             # Reset button tests
    "export_tests": 11,           # Export button tests
    "screen_transition_tests": 1, # Browser back/forward
    "gui_tests": 2,               # Layout tests
}
LIST_MODE_TOTAL_FIXED = sum(LIST_MODE_FIXED_TESTS.values())  # 63

# Fixed tests for ADD mode (keys match FixedTests model fields)
ADD_MODE_FIXED_TESTS: Dict[str, int] = {
    "concurrent_tests": 1,        # Concurrent edit test
    "db_error_tests": 1,          # DB error test
    "double_click_tests": 2,      # Double-click prevention
    "gui_tests": 1,               # Layout test
}
ADD_MODE_TOTAL_FIXED = sum(ADD_MODE_FIXED_TESTS.values())  # 5

# Fixed tests for EDIT mode (keys match FixedTests model fields)
EDIT_MODE_FIXED_TESTS: Dict[str, int] = {
    "concurrent_tests": 1,        # Concurrent edit test
    "db_error_tests": 1,          # DB error test
    "double_click_tests": 1,      # Double-click prevention
    "gui_tests": 1,               # Layout test
}
EDIT_MODE_TOTAL_FIXED = sum(EDIT_MODE_FIXED_TESTS.values())  # 4

# Fixed tests for VIEW mode (keys match FixedTests model fields)
VIEW_MODE_FIXED_TESTS: Dict[str, int] = {
    "gui_tests": 1,               # Layout test
}
VIEW_MODE_TOTAL_FIXED = sum(VIEW_MODE_FIXED_TESTS.values())  # 1


# =============================================================================
# MODE VALIDATION TRIGGERS - Which buttons trigger validation per mode
# =============================================================================

MODE_VALIDATION_TRIGGERS: Dict[str, List[str]] = {
    ScreenMode.LIST.value: [],                    # No validation in LIST mode
    ScreenMode.ADD.value: ["Search", "Save"],     # CRITICAL: duplicate validation
    ScreenMode.EDIT.value: [],                    # No validation in EDIT (readonly)
    ScreenMode.VIEW.value: [],                    # No validation in VIEW
}


# =============================================================================
# DECISION TABLE COMBINATIONS - DT test counts by role context
# =============================================================================

# DT combinations by mode and role context (each combination = 2 test rows)
DT_COMBINATIONS: Dict[str, Dict[str, int]] = {
    "ADD": {
        "System_Admin": 6,   # 6 × 2 = 12 tests
        "Backoffice": 4,     # 4 × 2 = 8 tests
        "Operator": 2,       # 2 × 2 = 4 tests
    },
    "EDIT": {
        "System_Admin": 10,  # 10 × 2 = 20 tests
        "Backoffice": 8,     # 8 × 2 = 16 tests
        "Operator": 1,       # 1 × 2 = 2 tests
    },
}

# Row multiplier: each DT combination = 2 test rows (action + verify)
DT_ROW_MULTIPLIER = 2


# =============================================================================
# CONSTRAINT PLACEHOLDERS - Template substitution placeholders
# =============================================================================

CONSTRAINT_PLACEHOLDERS: Set[str] = {
    "{max_length}",
    "{min_length}",
    "{label}",
    "{widget_name}",
    "{trigger_button}",
    "{button_name}",
    "{column}",
    "{screen_id}",
    "{screen_name}",
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_widget_test_count(widget_type: Union[WidgetType, str]) -> int:
    """Get the expected test count for a widget type."""
    key = widget_type.value if isinstance(widget_type, WidgetType) else widget_type
    return WIDGET_TEST_COUNTS.get(key, 0)


def get_applicable_modes(widget_type: Union[WidgetType, str]) -> List[ScreenMode]:
    """Get the applicable modes for a widget type."""
    key = widget_type.value if isinstance(widget_type, WidgetType) else widget_type
    mode_values = WIDGET_APPLICABLE_MODES.get(key, [])
    return [ScreenMode(v) for v in mode_values]


def get_mode_fixed_tests(mode: Union[ScreenMode, str]) -> Dict[str, int]:
    """Get the fixed test counts for a mode."""
    mode_value = mode.value if isinstance(mode, ScreenMode) else mode
    if mode_value == ScreenMode.LIST.value:
        return LIST_MODE_FIXED_TESTS.copy()
    elif mode_value == ScreenMode.ADD.value:
        return ADD_MODE_FIXED_TESTS.copy()
    elif mode_value == ScreenMode.EDIT.value:
        return EDIT_MODE_FIXED_TESTS.copy()
    elif mode_value == ScreenMode.VIEW.value:
        return VIEW_MODE_FIXED_TESTS.copy()
    return {}


def get_dt_test_count(mode: Union[ScreenMode, str], role_context: str) -> int:
    """Get the decision table test count for a mode and role context."""
    mode_value = mode.value if isinstance(mode, ScreenMode) else mode
    mode_dts = DT_COMBINATIONS.get(mode_value, {})
    combinations = mode_dts.get(role_context, 0)
    return combinations * DT_ROW_MULTIPLIER


def calculate_trigger_tests(
    widget_type: Union[WidgetType, str],
    trigger_buttons: List[str],
    mode: Union[ScreenMode, str]
) -> int:
    """
    Calculate total tests for a widget based on trigger buttons.

    In ADD mode, validation tests are duplicated for each trigger button.
    This is the critical pattern that AST v2.2 missed.
    """
    base_tests = get_widget_test_count(widget_type)
    mode_value = mode.value if isinstance(mode, ScreenMode) else mode
    mode_triggers = MODE_VALIDATION_TRIGGERS.get(mode_value, [])

    # Count applicable triggers
    applicable_triggers = [t for t in mode_triggers if t in trigger_buttons]

    if not applicable_triggers:
        return 0  # No validation for this mode

    return base_tests * len(applicable_triggers)
