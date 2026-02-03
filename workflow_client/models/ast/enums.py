"""
AST Model Enumerations.

Common enums used across all AST components.
"""
from enum import Enum


class ScreenType(str, Enum):
    """Screen type classification."""
    LIST = "list"
    FORM = "form"
    DETAIL = "detail"
    DASHBOARD = "dashboard"
    SEARCH = "search"
    LOGIN = "login"
    REGISTRATION = "registration"
    SETTINGS = "settings"
    REPORT = "report"
    WIZARD = "wizard"
    MODAL = "modal"
    MIXED = "mixed"


class WidgetType(str, Enum):
    """Widget type classification."""
    TEXT_INPUT = "text_input"
    TEXT_AREA = "text_area"
    PASSWORD = "password"
    EMAIL = "email"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    BUTTON = "button"
    LINK = "link"
    TABLE = "table"
    LABEL = "label"
    IMAGE = "image"
    FILE_UPLOAD = "file_upload"
    SEARCH_BOX = "search_box"
    TAB = "tab"
    ACCORDION = "accordion"
    MODAL = "modal"
    TOOLTIP = "tooltip"
    ICON = "icon"


class MessageType(str, Enum):
    """Message type classification."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
    CONFIRM = "confirm"


class DisplayStyle(str, Enum):
    """Message display style."""
    INLINE = "inline"
    TOAST = "toast"
    MODAL = "modal"
    BANNER = "banner"


class ScenarioCategory(str, Enum):
    """Test scenario category."""
    UI_VERIFICATION = "UI_VERIFICATION"
    INPUT_VALIDATION = "INPUT_VALIDATION"
    ERROR_HANDLING = "ERROR_HANDLING"
    CREATE_FLOW = "CREATE_FLOW"
    READ_LIST_FLOW = "READ_LIST_FLOW"
    UPDATE_FLOW = "UPDATE_FLOW"
    DELETE_FLOW = "DELETE_FLOW"
    SEARCH_FUNCTION = "SEARCH_FUNCTION"
    FILTER_FUNCTION = "FILTER_FUNCTION"
    SORT_FUNCTION = "SORT_FUNCTION"
    EXPORT_FUNCTION = "EXPORT_FUNCTION"
    IMPORT_FUNCTION = "IMPORT_FUNCTION"
    FILE_UPLOAD = "FILE_UPLOAD"
    FILE_DOWNLOAD = "FILE_DOWNLOAD"
    PERMISSION_CHECK = "PERMISSION_CHECK"
    AUTHENTICATION = "AUTHENTICATION"
    NAVIGATION_FLOW = "NAVIGATION_FLOW"
    PAGINATION = "PAGINATION"
    STATE_TRANSITION = "STATE_TRANSITION"
    WORKFLOW_FLOW = "WORKFLOW_FLOW"
