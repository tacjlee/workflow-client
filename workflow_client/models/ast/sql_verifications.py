"""
AST Model Component 7: SQL Verifications.

Database assertion queries for test case verification.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import re


class SqlVerification(BaseModel):
    """
    Component 7: SQL Verification

    Database assertion query for test case verification.
    """
    sql_id: str = Field(..., description="SQL verification identifier")
    name: str
    description: Optional[str] = None

    query: str = Field(..., description="SQL query with {{placeholders}}")

    expected_for_pass: str = Field(
        ...,
        description="Expected result description for pass (e.g., 'row_count = 1')"
    )

    output_format: str = Field(
        default="table",
        description="Output format (table/scalar/boolean)"
    )

    applies_to_scenarios: List[str] = Field(
        default_factory=list,
        description="Scenario IDs this verification applies to"
    )

    parameters: List[str] = Field(
        default_factory=list,
        description="Parameter names used in the query"
    )

    def get_placeholders(self) -> List[str]:
        """Extract placeholder names from the query."""
        pattern = r'\{\{(\w+)\}\}'
        return re.findall(pattern, self.query)

    def substitute_parameters(self, values: Dict[str, Any]) -> str:
        """
        Substitute parameters in the query with actual values.

        Args:
            values: Dict mapping parameter names to values

        Returns:
            Query string with placeholders replaced
        """
        result = self.query
        for param, value in values.items():
            placeholder = f"{{{{{param}}}}}"
            # Escape string values for SQL
            if isinstance(value, str):
                safe_value = f"'{value}'"
            elif value is None:
                safe_value = "NULL"
            else:
                safe_value = str(value)
            result = result.replace(placeholder, safe_value)
        return result

    def validate_parameters(self, values: Dict[str, Any]) -> List[str]:
        """
        Validate that all required parameters are provided.

        Returns:
            List of missing parameter names
        """
        placeholders = set(self.get_placeholders())
        provided = set(values.keys())
        missing = placeholders - provided
        return list(missing)

    def is_scalar_query(self) -> bool:
        """Check if this is a scalar (single value) query."""
        return self.output_format == "scalar"

    def is_boolean_query(self) -> bool:
        """Check if this is a boolean query."""
        return self.output_format == "boolean"
