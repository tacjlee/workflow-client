"""
AST Model v2.1: Test Case ID Generation Rule.

Defines the pattern for generating test case IDs in output files.
"""
from typing import Optional
from pydantic import BaseModel, Field


class TestCaseIdRule(BaseModel):
    """
    Rule for generating test case IDs.

    Example: For screen SC-011, generates IDs like [011-01], [011-02], etc.

    Attributes:
        prefix: ID prefix extracted from screen_id (e.g., "011" from "SC-011")
        format_pattern: Format string for ID generation
        counter_start: Starting counter value (default 1)
        section_reset: Whether to reset counter per section (Role, Validate, Function, GUI)
    """
    prefix: str = Field(..., description="ID prefix (e.g., '011' from screen_id 'SC-011')")
    format_pattern: str = Field(
        default="[{prefix}-{counter:02d}]",
        description="Format pattern for ID generation"
    )
    counter_start: int = Field(default=1, ge=1, description="Starting counter value")
    section_reset: bool = Field(
        default=True,
        description="Reset counter per section (Role, Validate, Function, GUI)"
    )

    def generate_id(self, counter: int) -> str:
        """
        Generate a test case ID with the given counter.

        Args:
            counter: The counter value to use

        Returns:
            Formatted ID string (e.g., "[011-01]")
        """
        return self.format_pattern.format(prefix=self.prefix, counter=counter)

    @classmethod
    def from_screen_id(cls, screen_id: str) -> "TestCaseIdRule":
        """
        Create a TestCaseIdRule from a screen ID.

        Args:
            screen_id: Screen identifier (e.g., "SC-011")

        Returns:
            TestCaseIdRule with prefix extracted from screen_id
        """
        # Extract numeric prefix from screen_id (e.g., "SC-011" -> "011")
        prefix = screen_id.replace("SC-", "").replace("sc-", "")
        return cls(prefix=prefix)
