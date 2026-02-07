"""
AST Model v2.1: Expected Output Models.

Composite model for combining description, message references, SQL references,
and display format into unified expected output.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class MessageRef(BaseModel):
    """
    Reference to a message in the business rules registry.

    Attributes:
        msg_id: Message ID (e.g., "MSG-044")
        action: Action type (display, validate, confirm)
    """
    msg_id: str = Field(..., description="Message ID (e.g., 'MSG-044')")
    action: str = Field(default="display", description="Action type: display, validate, confirm")


class DisplayFormat(BaseModel):
    """
    Display formatting options for expected output.

    Attributes:
        color: Text/border color (e.g., "red", "green")
        position: Display position (e.g., "below_input", "dialog", "toast")
        style: Display style (e.g., "inline", "modal", "banner")
    """
    color: Optional[str] = Field(None, description="Text/border color (red, green, blue, orange)")
    position: Optional[str] = Field(None, description="Display position (below_input, dialog, toast, banner)")
    style: Optional[str] = Field(None, description="Display style (inline, modal, banner)")


class ExpectedOutput(BaseModel):
    """
    Composite model for expected output in test cases.

    Combines description, message references, SQL references, and display format
    into a unified structure that the Executor can render.

    Example output rendering:
    - "Search thành công giá trị được nhập trong textbox Thỏa mãn [SQL SC011.SQL3] = null"
    - "Hiển thị Msg màu đỏ:「入力形式が正しくありません。」bên dưới ô input"

    Attributes:
        description: Narrative description of expected result
        message_refs: References to messages in business rules
        sql_refs: SQL verification IDs (e.g., ["SQL3", "SQL4"])
        display_format: Display formatting options
        visual_indicators: Visual UI changes (e.g., ["border_red", "input_disabled"])
    """
    description: Optional[str] = Field(None, description="Narrative expected behavior")
    message_refs: List[MessageRef] = Field(
        default_factory=list,
        description="References to messages in business rules"
    )
    sql_refs: List[str] = Field(
        default_factory=list,
        description="SQL verification IDs (e.g., ['SQL3', 'SQL4'])"
    )
    display_format: Optional[DisplayFormat] = Field(
        None,
        description="Display formatting options"
    )
    visual_indicators: List[str] = Field(
        default_factory=list,
        description="Visual UI changes (e.g., ['border_red', 'input_disabled'])"
    )

    def has_messages(self) -> bool:
        """Check if there are message references."""
        return len(self.message_refs) > 0

    def has_sql_refs(self) -> bool:
        """Check if there are SQL references."""
        return len(self.sql_refs) > 0

    def get_message_ids(self) -> List[str]:
        """Get list of message IDs."""
        return [ref.msg_id for ref in self.message_refs]

    @classmethod
    def from_description(cls, description: str) -> "ExpectedOutput":
        """Create an ExpectedOutput with just a description."""
        return cls(description=description)

    @classmethod
    def from_message(cls, msg_id: str, action: str = "display") -> "ExpectedOutput":
        """Create an ExpectedOutput with a single message reference."""
        return cls(message_refs=[MessageRef(msg_id=msg_id, action=action)])

    @classmethod
    def with_error_display(
        cls,
        msg_id: str,
        color: str = "red",
        position: str = "below_input"
    ) -> "ExpectedOutput":
        """
        Create an ExpectedOutput for an error message display.

        Args:
            msg_id: Message ID
            color: Display color (default "red")
            position: Display position (default "below_input")

        Returns:
            ExpectedOutput configured for error display
        """
        return cls(
            message_refs=[MessageRef(msg_id=msg_id, action="display")],
            display_format=DisplayFormat(color=color, position=position),
            visual_indicators=["border_red"] if color == "red" else []
        )
