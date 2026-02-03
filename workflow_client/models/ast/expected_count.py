"""
AST Model Component 8: Expected Test Count.

Validation metrics and thresholds for Validator to check.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class CountBreakdown(BaseModel):
    """Breakdown of expected test counts."""
    by_output_file: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by output file"
    )
    by_scenario: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by scenario ID"
    )
    by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by category"
    )

    def get_total_from_breakdown(self) -> int:
        """Calculate total from by_scenario breakdown."""
        return sum(self.by_scenario.values())

    def get_categories(self) -> List[str]:
        """Get list of categories."""
        return list(self.by_category.keys())

    def get_output_files(self) -> List[str]:
        """Get list of output files."""
        return list(self.by_output_file.keys())


class ValidationRule(BaseModel):
    """Validation rule for test count."""
    rule_id: str
    description: str
    threshold_type: str = Field(..., description="percentage/absolute/range")
    threshold_value: float
    severity: str = Field(default="warning", description="error/warning/info")

    def check(self, expected: int, actual: int) -> bool:
        """
        Check if actual count passes this validation rule.

        Args:
            expected: Expected count
            actual: Actual count

        Returns:
            True if validation passes
        """
        if expected == 0:
            return actual == 0

        if self.threshold_type == "percentage":
            variance = abs(actual - expected) / expected * 100
            return variance <= self.threshold_value

        elif self.threshold_type == "absolute":
            diff = abs(actual - expected)
            return diff <= self.threshold_value

        elif self.threshold_type == "range":
            # threshold_value is percentage, check if within range
            min_val = expected * (1 - self.threshold_value / 100)
            max_val = expected * (1 + self.threshold_value / 100)
            return min_val <= actual <= max_val

        return True

    def get_variance_message(self, expected: int, actual: int) -> str:
        """Get human-readable variance message."""
        if expected == 0:
            return f"Expected 0, got {actual}"

        if self.threshold_type == "percentage":
            variance = abs(actual - expected) / expected * 100
            return f"Variance: {variance:.1f}% (threshold: {self.threshold_value}%)"

        elif self.threshold_type == "absolute":
            diff = abs(actual - expected)
            return f"Difference: {diff} (threshold: {self.threshold_value})"

        return f"Expected: {expected}, Actual: {actual}"


class ExpectedTestCount(BaseModel):
    """
    Component 8: Expected Test Count

    Validation metrics and thresholds for Validator to check.
    """
    total: int = Field(..., description="Total expected test case count")

    breakdown: CountBreakdown = Field(
        default_factory=CountBreakdown,
        description="Breakdown by various dimensions"
    )

    validation_rules: List[ValidationRule] = Field(
        default_factory=list,
        description="Rules for validating actual vs expected count"
    )

    confidence: float = Field(default=0.8, ge=0.0, le=1.0)

    def validate_count(self, actual: int) -> Dict[str, Any]:
        """
        Validate actual count against expected.

        Returns:
            Dict with validation results per rule
        """
        results: Dict[str, Any] = {
            "expected": self.total,
            "actual": actual,
            "passed": True,
            "rules": []
        }

        for rule in self.validation_rules:
            passed = rule.check(self.total, actual)
            rule_result = {
                "rule_id": rule.rule_id,
                "passed": passed,
                "severity": rule.severity,
                "message": rule.get_variance_message(self.total, actual)
            }
            results["rules"].append(rule_result)

            if not passed and rule.severity == "error":
                results["passed"] = False

        return results

    def get_variance_percentage(self, actual: int) -> float:
        """Calculate variance percentage between expected and actual."""
        if self.total == 0:
            return 0.0 if actual == 0 else 100.0
        return abs(actual - self.total) / self.total * 100

    def is_within_threshold(self, actual: int, threshold_percentage: float = 5.0) -> bool:
        """Check if actual count is within threshold percentage of expected."""
        return self.get_variance_percentage(actual) <= threshold_percentage
