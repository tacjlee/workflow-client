"""
AST Model Component 1: Screen Classification.

Contains screen metadata, type classification, access control info,
and output file mappings.
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

from .enums import ScreenType
from .test_case_id import TestCaseIdRule


class OutputFileMapping(BaseModel):
    """Mapping of test category to output file."""
    category: str = Field(..., description="Test category (e.g., 'list', 'add', 'edit')")
    file_pattern: str = Field(..., description="Output file pattern (e.g., 'SC011_ListAccount.md')")
    description: Optional[str] = None


class ScreenClassification(BaseModel):
    """
    Component 1: Screen Classification

    Contains screen metadata, type classification, access control info,
    and output file mappings.
    """
    model_config = ConfigDict(use_enum_values=True)

    screen_id: str = Field(..., description="Screen identifier (e.g., 'SC-011')")
    screen_name: str = Field(..., description="Screen name in Japanese")
    screen_name_en: Optional[str] = Field(None, description="Screen name in English")
    screen_type: ScreenType = Field(..., description="Primary screen type")
    secondary_types: List[ScreenType] = Field(default_factory=list, description="Secondary screen types")

    access_control: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Role-based access control (e.g., {'view': ['Operator', 'BackOffice'], 'edit': ['SystemAdmin']})"
    )

    output_files: List[OutputFileMapping] = Field(
        default_factory=list,
        description="Mapping of test categories to output files"
    )

    matched_templates: List[str] = Field(
        default_factory=list,
        description="Matched test templates from Knowledge Base"
    )

    confidence: float = Field(default=0.8, ge=0.0, le=1.0)

    # v2.1: Test case ID generation rule
    test_case_id_rule: Optional[TestCaseIdRule] = Field(
        None,
        description="Rule for generating test case IDs (e.g., [011-01], [011-02]) (v2.1)"
    )
