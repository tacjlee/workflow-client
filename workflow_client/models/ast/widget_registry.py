"""
AST Model Component 2: Widget Registry.

Master inventory of all widgets with their constraints and behaviors.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .enums import WidgetType


class ModeBehavior(BaseModel):
    """Widget behavior in different modes."""
    create: Optional[str] = Field(None, description="Behavior in create mode (visible/hidden/disabled/readonly)")
    edit: Optional[str] = Field(None, description="Behavior in edit mode")
    view: Optional[str] = Field(None, description="Behavior in view mode")


class Widget(BaseModel):
    """
    Individual widget definition in the registry.
    """
    model_config = ConfigDict(use_enum_values=True)

    widget_id: str = Field(..., description="Widget identifier (e.g., 'WGT-1')")
    widget_name: str = Field(..., description="Widget name in Japanese")
    widget_name_en: Optional[str] = Field(None, description="Widget name in English")
    widget_type: WidgetType = Field(..., description="Widget type classification")

    # Constraints
    mandatory: bool = Field(default=False, description="Whether field is required")
    max_length: Optional[int] = Field(None, description="Maximum character length")
    min_length: Optional[int] = Field(None, description="Minimum character length")
    pattern: Optional[str] = Field(None, description="Validation regex pattern")
    min_value: Optional[float] = Field(None, description="Minimum numeric value")
    max_value: Optional[float] = Field(None, description="Maximum numeric value")

    # Mode behavior
    mode_behavior: Optional[ModeBehavior] = Field(None, description="Behavior in different modes")

    # Access control
    permission_required: Optional[List[str]] = Field(None, description="Roles that can access this widget")

    # Additional metadata
    default_value: Optional[str] = Field(None, description="Default value")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    options: Optional[List[Dict[str, str]]] = Field(None, description="Options for select/radio widgets")


class WidgetRegistry(BaseModel):
    """
    Component 2: Widget Registry

    Master inventory of all widgets with their constraints and behaviors.
    """
    widgets: List[Widget] = Field(default_factory=list)
    total_count: int = Field(default=0)

    @field_validator('total_count', mode='before')
    @classmethod
    def set_total_count(cls, v, info):
        if 'widgets' in info.data:
            return len(info.data['widgets'])
        return v

    def get_widget(self, widget_id: str) -> Optional[Widget]:
        """Get widget by ID."""
        for w in self.widgets:
            if w.widget_id == widget_id:
                return w
        return None

    def get_widgets_by_type(self, widget_type: WidgetType) -> List[Widget]:
        """Get all widgets of a specific type."""
        return [w for w in self.widgets if w.widget_type == widget_type]

    def get_mandatory_widgets(self) -> List[Widget]:
        """Get all mandatory widgets."""
        return [w for w in self.widgets if w.mandatory]

    def get_widget_ids(self) -> List[str]:
        """Get all widget IDs."""
        return [w.widget_id for w in self.widgets]
