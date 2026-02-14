"""
AST Model Component 9: Test Generation Rules.

Defines the formula and rules for how Executor should generate test cases.
This enables Planner to control Executor's generation strategy via AST contract.

Part of PEV Architecture v2.2
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

from .enums import ScenarioCategory


class GenerationStrategy(str, Enum):
    """
    Strategy for generating test cases.

    Defines how test cases are created from widgets, viewpoints, and samples.
    """
    # One test case per widget × viewpoint × test data sample (most granular)
    PER_WIDGET_VIEWPOINT_SAMPLE = "per_widget_viewpoint_sample"

    # One test case per widget × viewpoint (samples become test data table)
    PER_WIDGET_VIEWPOINT = "per_widget_viewpoint"

    # One test case per widget (all viewpoints in one test case)
    PER_WIDGET = "per_widget"

    # One test case per scenario (all widgets consolidated)
    PER_SCENARIO = "per_scenario"

    # Generate only from decision table rows
    FROM_DECISION_TABLE = "from_decision_table"

    # Hybrid: DT rows + one per widget for validation
    DT_PLUS_WIDGET_VALIDATION = "dt_plus_widget_validation"


class ScenarioGenerationRule(BaseModel):
    """
    Generation rule for a specific scenario category.

    Allows Planner to specify different generation strategies
    for different types of scenarios.
    """
    category: str = Field(
        ...,
        description="Scenario category (e.g., 'UI_VERIFICATION', 'INPUT_VALIDATION')"
    )

    strategy: GenerationStrategy = Field(
        ...,
        description="Generation strategy for this category"
    )

    # Source control
    include_dt_tests: bool = Field(
        default=True,
        description="Include test cases from decision tables"
    )
    include_widget_tests: bool = Field(
        default=True,
        description="Include test cases from widget-viewpoint combinations"
    )

    # Consolidation options
    consolidate_samples: bool = Field(
        default=False,
        description="Merge test data samples into one TC with data table"
    )
    consolidate_viewpoints: bool = Field(
        default=False,
        description="Merge viewpoints into one TC per widget"
    )

    # Limits
    max_tests_per_widget: Optional[int] = Field(
        None,
        description="Maximum test cases to generate per widget"
    )
    max_tests_per_scenario: Optional[int] = Field(
        None,
        description="Maximum test cases to generate per scenario"
    )


class FormulaComponent(BaseModel):
    """
    A component of the test count formula.

    Represents one part of the calculation, e.g., "SCN-001: 21 widgets × 1 = 21"
    """
    component_id: str = Field(..., description="Identifier (scenario_id, category, etc.)")
    description: str = Field(..., description="Human-readable description")

    # Input values
    scenarios: int = Field(default=1)
    widgets: int = Field(default=0)
    viewpoints: int = Field(default=0)
    samples: int = Field(default=0)
    dt_rows: int = Field(default=0)

    # Applied strategy
    strategy: GenerationStrategy = Field(
        default=GenerationStrategy.PER_WIDGET_VIEWPOINT_SAMPLE
    )

    # Calculated output
    expected_count: int = Field(default=0, description="Expected TC count for this component")

    # Calculation expression
    formula_expression: Optional[str] = Field(
        None,
        description="e.g., '21 widgets × 3 viewpoints × 1 sample = 63'"
    )


class TestGenerationRules(BaseModel):
    """
    Component 9: Test Generation Rules

    Defines HOW Executor should generate test cases.
    This is the contract between Planner and Executor for test generation.

    Example:
        rules = TestGenerationRules(
            default_strategy=GenerationStrategy.PER_WIDGET_VIEWPOINT,
            category_rules=[
                ScenarioGenerationRule(
                    category="UI_VERIFICATION",
                    strategy=GenerationStrategy.PER_SCENARIO,
                ),
                ScenarioGenerationRule(
                    category="INPUT_VALIDATION",
                    strategy=GenerationStrategy.PER_WIDGET_VIEWPOINT,
                    consolidate_samples=True,
                ),
            ],
            exclude_orphan_tests=True,
        )
    """

    # Default strategy when no category rule matches
    default_strategy: GenerationStrategy = Field(
        default=GenerationStrategy.PER_WIDGET_VIEWPOINT_SAMPLE,
        description="Default generation strategy"
    )

    # Per-category rules (override default)
    category_rules: List[ScenarioGenerationRule] = Field(
        default_factory=list,
        description="Generation rules per scenario category"
    )

    # Human-readable formula
    formula: str = Field(
        default="sum(scenarios × widgets × viewpoints × samples) + dt_rows",
        description="Human-readable formula description"
    )

    # Detailed breakdown by component
    formula_components: List[FormulaComponent] = Field(
        default_factory=list,
        description="Breakdown of expected count by component"
    )

    # Calculated totals
    total_from_formula: int = Field(
        default=0,
        description="Total expected count calculated from formula"
    )

    # Exclusion rules
    exclude_orphan_tests: bool = Field(
        default=False,
        description="Exclude button/edge tests without scenario attribution"
    )
    exclude_button_tests: bool = Field(
        default=False,
        description="Exclude standalone button function tests"
    )
    exclude_edge_case_tests: bool = Field(
        default=False,
        description="Exclude generic edge case tests"
    )

    # Categories to skip entirely
    excluded_categories: List[str] = Field(
        default_factory=list,
        description="Scenario categories to skip test generation"
    )

    def get_rule_for_category(self, category: str) -> Optional[ScenarioGenerationRule]:
        """
        Get the generation rule for a specific category.

        Args:
            category: Scenario category (e.g., "UI_VERIFICATION")

        Returns:
            ScenarioGenerationRule if found, None otherwise
        """
        category_upper = category.upper() if category else ""
        for rule in self.category_rules:
            if rule.category.upper() == category_upper:
                return rule
        return None

    def get_strategy_for_category(self, category: str) -> GenerationStrategy:
        """
        Get the generation strategy for a category.
        Falls back to default_strategy if no specific rule.

        Args:
            category: Scenario category

        Returns:
            GenerationStrategy to use
        """
        rule = self.get_rule_for_category(category)
        if rule:
            return rule.strategy
        return self.default_strategy

    def should_include_category(self, category: str) -> bool:
        """Check if a category should be included in test generation."""
        category_upper = category.upper() if category else ""
        return category_upper not in [c.upper() for c in self.excluded_categories]

    def calculate_total(self) -> int:
        """Calculate total expected count from formula components."""
        return sum(c.expected_count for c in self.formula_components)

    def add_component(
        self,
        component_id: str,
        description: str,
        widgets: int = 0,
        viewpoints: int = 0,
        samples: int = 0,
        dt_rows: int = 0,
        strategy: GenerationStrategy = GenerationStrategy.PER_WIDGET_VIEWPOINT_SAMPLE,
    ) -> FormulaComponent:
        """
        Add a formula component and calculate its expected count.

        Args:
            component_id: Identifier for this component
            description: Human-readable description
            widgets: Number of widgets
            viewpoints: Number of viewpoints
            samples: Number of test data samples
            dt_rows: Number of decision table rows
            strategy: Generation strategy

        Returns:
            The created FormulaComponent
        """
        # Calculate expected count based on strategy
        if strategy == GenerationStrategy.PER_SCENARIO:
            expected = 1
            expr = "1 (consolidated scenario)"
        elif strategy == GenerationStrategy.PER_WIDGET:
            expected = widgets
            expr = f"{widgets} widgets × 1"
        elif strategy == GenerationStrategy.PER_WIDGET_VIEWPOINT:
            expected = widgets * max(viewpoints, 1)
            expr = f"{widgets} widgets × {viewpoints} viewpoints"
        elif strategy == GenerationStrategy.PER_WIDGET_VIEWPOINT_SAMPLE:
            expected = widgets * max(viewpoints, 1) * max(samples, 1)
            expr = f"{widgets} × {viewpoints} × {samples}"
        elif strategy == GenerationStrategy.FROM_DECISION_TABLE:
            expected = dt_rows
            expr = f"{dt_rows} DT rows"
        elif strategy == GenerationStrategy.DT_PLUS_WIDGET_VALIDATION:
            expected = dt_rows + widgets
            expr = f"{dt_rows} DT + {widgets} widget validations"
        else:
            expected = widgets * max(viewpoints, 1) * max(samples, 1)
            expr = f"{widgets} × {viewpoints} × {samples}"

        component = FormulaComponent(
            component_id=component_id,
            description=description,
            widgets=widgets,
            viewpoints=viewpoints,
            samples=samples,
            dt_rows=dt_rows,
            strategy=strategy,
            expected_count=expected,
            formula_expression=f"{expr} = {expected}",
        )

        self.formula_components.append(component)
        self.total_from_formula = self.calculate_total()

        return component

    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the generation rules."""
        return {
            "default_strategy": self.default_strategy.value,
            "category_rules": [
                {"category": r.category, "strategy": r.strategy.value}
                for r in self.category_rules
            ],
            "formula": self.formula,
            "total_expected": self.total_from_formula,
            "components": [
                {"id": c.component_id, "count": c.expected_count, "formula": c.formula_expression}
                for c in self.formula_components
            ],
            "exclusions": {
                "orphan_tests": self.exclude_orphan_tests,
                "button_tests": self.exclude_button_tests,
                "edge_case_tests": self.exclude_edge_case_tests,
            }
        }
