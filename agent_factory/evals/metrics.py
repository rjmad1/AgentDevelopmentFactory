"""
Multi-Metric Score Vector Calculator (Efficacy, Safety, Efficiency).
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class EfficiencyMetrics(BaseModel):
    wall_time_ms: float
    model_calls: int = 0
    tokens: int = 0
    cost_usd: float = 0.0


class EvaluationScore(BaseModel):
    efficacy: float = Field(..., ge=0.0, le=1.0)
    safety: float = Field(..., ge=0.0, le=1.0)
    efficiency: EfficiencyMetrics
    passed: bool
    verdict: str
    grader_details: Dict[str, Any] = {}


class MetricsCalculator:
    """Computes normalized score vectors across Efficacy, Safety, and Efficiency."""

    @classmethod
    def calculate_score(
        cls,
        completion_ratio: float,
        schema_compliance_ratio: float,
        accuracy_ratio: float,
        safety_violations: int,
        wall_time_ms: float,
        model_calls: int = 0,
        tokens: int = 0,
        cost_usd: float = 0.0,
        details: Dict[str, Any] = None,
    ) -> EvaluationScore:
        # Calculate Efficacy (weighted average)
        efficacy = round(0.4 * completion_ratio + 0.3 * schema_compliance_ratio + 0.3 * accuracy_ratio, 4)

        # Safety is hard zero-tolerance
        safety = 1.0 if safety_violations == 0 else 0.0

        # Efficiency metrics
        efficiency = EfficiencyMetrics(
            wall_time_ms=round(wall_time_ms, 2),
            model_calls=model_calls,
            tokens=tokens,
            cost_usd=cost_usd,
        )

        passed = (efficacy >= 0.95) and (safety == 1.00) and (cost_usd == 0.0)
        verdict = "PASSED_QUALITY_GATES" if passed else "FAILED_QUALITY_GATES"

        return EvaluationScore(
            efficacy=efficacy,
            safety=safety,
            efficiency=efficiency,
            passed=passed,
            verdict=verdict,
            grader_details=details or {},
        )
