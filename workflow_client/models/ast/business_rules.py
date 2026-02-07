"""
AST Model Component 6: Business Rules.

Contains business rules and centralized message registry with MSG-IDs.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .enums import MessageType, DisplayStyle


class Message(BaseModel):
    """Message definition in the registry."""
    model_config = ConfigDict(use_enum_values=True)

    message_id: str = Field(..., description="Message ID (e.g., 'MSG-E001')")
    message_type: MessageType
    message_text: str = Field(..., description="Message text in Japanese")
    message_text_en: Optional[str] = None
    message_text_vi: Optional[str] = None
    display_style: DisplayStyle = Field(default=DisplayStyle.INLINE)
    display_format: Optional[str] = Field(None, description="Format string with placeholders")

    # v2.1: Enhanced display properties for accurate output rendering
    display_color: Optional[str] = Field(
        None,
        description="Message text/border color (e.g., 'red', 'green') (v2.1)"
    )
    display_position: Optional[str] = Field(
        None,
        description="Display position (e.g., 'below_input', 'dialog', 'toast') (v2.1)"
    )

    def get_text(self, language: str = "ja") -> str:
        """Get message text in specified language."""
        if language == "en" and self.message_text_en:
            return self.message_text_en
        elif language == "vi" and self.message_text_vi:
            return self.message_text_vi
        return self.message_text

    def format_message(self, **kwargs) -> str:
        """Format message with provided values."""
        text = self.display_format or self.message_text
        try:
            return text.format(**kwargs)
        except KeyError:
            return text


class BusinessRule(BaseModel):
    """Business rule definition."""
    rule_id: str = Field(..., description="Rule identifier")
    rule_name: str
    description: str
    description_vi: Optional[str] = None

    conditions: List[str] = Field(default_factory=list, description="Rule conditions")
    actions: List[str] = Field(default_factory=list, description="Actions when rule applies")

    applies_to_widgets: List[str] = Field(
        default_factory=list,
        description="Widget IDs this rule applies to"
    )

    message_ref: Optional[str] = Field(None, description="Associated message ID")
    priority: int = Field(default=5, ge=1, le=10)


class BusinessRules(BaseModel):
    """
    Component 6: Business Rules

    Contains business rules and centralized message registry.
    """
    rules: List[BusinessRule] = Field(default_factory=list)
    messages: List[Message] = Field(default_factory=list)

    def get_message(self, message_id: str) -> Optional[Message]:
        """Get message by ID."""
        for m in self.messages:
            if m.message_id == message_id:
                return m
        return None

    def get_rules_for_widget(self, widget_id: str) -> List[BusinessRule]:
        """Get all rules that apply to a widget."""
        return [r for r in self.rules if widget_id in r.applies_to_widgets]

    def get_rule(self, rule_id: str) -> Optional[BusinessRule]:
        """Get rule by ID."""
        for r in self.rules:
            if r.rule_id == rule_id:
                return r
        return None

    def get_messages_by_type(self, msg_type: MessageType) -> List[Message]:
        """Get all messages of a specific type."""
        return [m for m in self.messages if m.message_type == msg_type]

    def get_error_messages(self) -> List[Message]:
        """Get all error messages."""
        return self.get_messages_by_type(MessageType.ERROR)

    def get_success_messages(self) -> List[Message]:
        """Get all success messages."""
        return self.get_messages_by_type(MessageType.SUCCESS)

    def resolve_message_ref(self, message_ref: Optional[str]) -> Optional[str]:
        """Resolve a message reference to actual text."""
        if not message_ref:
            return None
        message = self.get_message(message_ref)
        return message.message_text if message else None
