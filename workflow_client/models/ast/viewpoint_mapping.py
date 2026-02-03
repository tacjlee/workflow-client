"""
AST Model Component 3: Widget-Viewpoint Mapping.

Maps each widget to applicable viewpoints with test data samples.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class TestDataSample(BaseModel):
    """Sample test data for a viewpoint."""
    value: str = Field(..., description="Test data value")
    description: Optional[str] = Field(None, description="Description of what this tests")
    expected_result: Optional[str] = Field(None, description="Expected result for this data")
    is_valid: bool = Field(default=True, description="Whether this is valid input")


class ViewpointMapping(BaseModel):
    """
    Mapping of a viewpoint to a widget with test data samples.
    """
    viewpoint_id: str = Field(..., description="Viewpoint identifier (e.g., 'VP-001')")
    viewpoint_name: str = Field(..., description="Viewpoint name")
    viewpoint_name_vi: Optional[str] = Field(None, description="Viewpoint name in Vietnamese")
    description: Optional[str] = Field(None, description="Viewpoint description")

    recommend: bool = Field(default=False, description="Whether this viewpoint is recommended")
    priority: str = Field(default="medium", description="Testing priority (critical/high/medium/low)")

    test_data_samples: List[TestDataSample] = Field(
        default_factory=list,
        description="Sample test data for this viewpoint"
    )

    procedure_template: Optional[str] = Field(
        None,
        description="Procedure template ID from Knowledge Base"
    )

    message_ref: Optional[str] = Field(
        None,
        description="Message ID reference for expected error/success message"
    )


class WidgetViewpointMapping(BaseModel):
    """
    Component 3: Widget-Viewpoint Mapping

    Maps each widget to applicable viewpoints with test data samples.
    """
    widget_id: str = Field(..., description="Reference to widget in registry")
    widget_name: str = Field(..., description="Widget name for reference")
    viewpoints: List[ViewpointMapping] = Field(default_factory=list)

    def get_recommended_viewpoints(self) -> List[ViewpointMapping]:
        """Get all recommended viewpoints."""
        return [vp for vp in self.viewpoints if vp.recommend]

    def get_viewpoints_by_priority(self, priority: str) -> List[ViewpointMapping]:
        """Get viewpoints filtered by priority."""
        return [vp for vp in self.viewpoints if vp.priority == priority]

    def has_test_data(self) -> bool:
        """Check if any viewpoint has test data samples."""
        return any(vp.test_data_samples for vp in self.viewpoints)
