"""
MindMap Model Enumerations.

Common enums used across all MindMap components.
These enums are designed for deterministic template-based test planning.
"""
from enum import Enum


class ScreenType(str, Enum):
    """Screen type classification for MindMap."""
    CRUD_MASTER = "CRUD_MASTER"  # Full CRUD with LIST, ADD, EDIT modes
    LIST_ONLY = "LIST_ONLY"      # Only LIST mode (search, view, export)
    FORM_ONLY = "FORM_ONLY"      # Only ADD/EDIT mode (settings, profile)
    WIZARD = "WIZARD"            # Multi-step form
    DASHBOARD = "DASHBOARD"      # Read-only dashboard with charts
    SETTINGS = "SETTINGS"        # System settings


class ScreenMode(str, Enum):
    """Screen modes that organize test plans."""
    LIST = "LIST"
    ADD = "ADD"
    EDIT = "EDIT"
    VIEW = "VIEW"


class WidgetType(str, Enum):
    """Widget types with associated test templates."""
    EMAIL = "EMAIL"
    TEXT_INPUT = "TEXT_INPUT"
    PASSWORD = "PASSWORD"
    NUMBER = "NUMBER"
    TEXTAREA = "TEXTAREA"
    DROPDOWN = "DROPDOWN"
    CHECKBOX = "CHECKBOX"
    RADIO = "RADIO"
    DATE = "DATE"
    DATETIME = "DATETIME"
    FILE_UPLOAD = "FILE_UPLOAD"
    TABLE = "TABLE"
    SEARCH_BOX = "SEARCH_BOX"
    BUTTON = "BUTTON"
    LINK = "LINK"
    LABEL = "LABEL"


class ButtonType(str, Enum):
    """Button types with associated test templates."""
    SAVE = "SAVE"
    CLOSE = "CLOSE"
    CANCEL = "CANCEL"
    SEARCH = "SEARCH"
    RESET = "RESET"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    ADD = "ADD"
    EDIT = "EDIT"
    GENERIC = "GENERIC"


class ViewpointCategory(str, Enum):
    """Categories of test viewpoints."""
    # Validation categories
    REQUIRED = "REQUIRED"
    BOUNDARY = "BOUNDARY"
    FORMAT = "FORMAT"
    CHARACTER_TYPE = "CHARACTER_TYPE"
    SPACE_HANDLING = "SPACE_HANDLING"
    SPECIAL_CHARS = "SPECIAL_CHARS"

    # Widget-specific categories
    DROPDOWN = "DROPDOWN"
    CHECKBOX_STATE = "CHECKBOX_STATE"
    SEARCH = "SEARCH"
    PAGINATION = "PAGINATION"
    TABLE_SORT = "TABLE_SORT"
    EXPORT = "EXPORT"
    RESET = "RESET"

    # Button categories
    BUTTON_BEHAVIOR = "BUTTON_BEHAVIOR"

    # Role/Access categories
    ROLE_ACCESS = "ROLE_ACCESS"

    # GUI category
    GUI_LAYOUT = "GUI_LAYOUT"

    # Other
    CONCURRENT = "CONCURRENT"
    DB_ERROR = "DB_ERROR"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    SCREEN_TRANSITION = "SCREEN_TRANSITION"


class WidgetState(str, Enum):
    """Widget state in a specific mode."""
    EDITABLE = "editable"
    READONLY = "readonly"
    HIDDEN = "hidden"
    DISABLED = "disabled"
    SEARCH = "search"  # For search fields in LIST mode
