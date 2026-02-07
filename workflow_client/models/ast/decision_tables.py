"""
AST Model Component 5: Decision Tables.

Defines role/mode combination matrices for test case expansion.
"""
from typing import Optional, List, Dict, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .expected_output import ExpectedOutput


class DTCondition(BaseModel):
    """Condition in a decision table."""
    condition_id: str
    condition_name: str
    values: List[str] = Field(..., description="Possible values for this condition")


class ExpansionStep(BaseModel):
    """
    Step in decision table row expansion (v2.1).

    Defines procedure steps for each expanded test case.
    """
    step_number: int = Field(..., description="Step number (1-based)")
    action: str = Field(..., description="Action description")
    action_vi: Optional[str] = Field(None, description="Action in Vietnamese")
    expected_output: Optional[Dict] = Field(
        None,
        description="Expected output for this step (ExpectedOutput dict)"
    )


class PostAction(BaseModel):
    """
    Post-action after decision table row execution (v2.1).

    Common actions like close popup, verify result.
    """
    action: str = Field(..., description="Action description")
    action_vi: Optional[str] = Field(None, description="Action in Vietnamese")
    expected_output: Optional[Dict] = Field(
        None,
        description="Expected output for this action (ExpectedOutput dict)"
    )


class DTSubTableRow(BaseModel):
    """Row in a decision table sub-table."""
    row_id: str
    conditions: Dict[str, str] = Field(..., description="Condition values for this row")
    expected_result: str
    expected_result_vi: Optional[str] = None
    message_ref: Optional[str] = Field(None, description="MSG-ID for expected message")

    # v2.1: Expansion fields for generating multiple test cases per row
    expansion_factor: int = Field(
        default=1,
        ge=1,
        description="Number of test cases to generate from this row (v2.1, default=1 for v2.0 compatibility)"
    )
    expansion_steps: List[ExpansionStep] = Field(
        default_factory=list,
        description="Steps for each expanded test case (v2.1)"
    )

    def get_expanded_test_count(self) -> int:
        """Get number of test cases this row expands to (v2.1)."""
        return self.expansion_factor


class DTSubTable(BaseModel):
    """
    Sub-table in a decision table (DT1, DT2, DT3).

    - DT1: Role combinations
    - DT2: Mode combinations (Create/Edit)
    - DT3: Full matrix (Role x Mode x Widget states)
    """
    sub_table_id: str = Field(..., description="Sub-table ID (e.g., 'DT1', 'DT2', 'DT3')")
    name: str
    description: Optional[str] = None
    rows: List[DTSubTableRow] = Field(default_factory=list)

    def get_row_count(self) -> int:
        """Get number of rows in this sub-table."""
        return len(self.rows)

    def get_unique_conditions(self) -> Dict[str, List[str]]:
        """Get unique condition values across all rows."""
        conditions: Dict[str, List[str]] = {}
        for row in self.rows:
            for cond_id, value in row.conditions.items():
                if cond_id not in conditions:
                    conditions[cond_id] = []
                if value not in conditions[cond_id]:
                    conditions[cond_id].append(value)
        return conditions


class DecisionTable(BaseModel):
    """
    Component 5: Decision Table

    Defines role/mode combination matrices for test case expansion.
    """
    dt_id: str = Field(..., description="Decision table identifier")
    name: str
    description: Optional[str] = None

    conditions: List[DTCondition] = Field(
        default_factory=list,
        description="Conditions (factors) in this decision table"
    )

    sub_tables: List[DTSubTable] = Field(
        default_factory=list,
        description="Sub-tables (DT1, DT2, DT3) with combinations"
    )

    applies_to_scenarios: List[str] = Field(
        default_factory=list,
        description="Scenario IDs this decision table applies to"
    )

    # v2.1: Post-actions common to all combinations
    post_actions: List[PostAction] = Field(
        default_factory=list,
        description="Common actions after each DT row (e.g., close popup, verify) (v2.1)"
    )

    def get_sub_table(self, sub_table_id: str) -> Optional[DTSubTable]:
        """Get sub-table by ID."""
        for st in self.sub_tables:
            if st.sub_table_id == sub_table_id:
                return st
        return None

    def get_total_combinations(self) -> int:
        """Get total number of test combinations across all sub-tables (v2.0 behavior: counts rows)."""
        return sum(st.get_row_count() for st in self.sub_tables)

    def get_total_expanded_test_count(self) -> int:
        """
        Get total number of test cases after expansion (v2.1).

        Accounts for expansion_factor on each row.
        """
        total = 0
        for st in self.sub_tables:
            for row in st.rows:
                total += row.get_expanded_test_count()
        return total

    def get_condition(self, condition_id: str) -> Optional[DTCondition]:
        """Get condition by ID."""
        for c in self.conditions:
            if c.condition_id == condition_id:
                return c
        return None

    def get_dt1(self) -> Optional[DTSubTable]:
        """Get DT1 (role combinations) sub-table."""
        return self.get_sub_table("DT1")

    def get_dt2(self) -> Optional[DTSubTable]:
        """Get DT2 (mode combinations) sub-table."""
        return self.get_sub_table("DT2")

    def get_dt3(self) -> Optional[DTSubTable]:
        """Get DT3 (full matrix) sub-table."""
        return self.get_sub_table("DT3")
