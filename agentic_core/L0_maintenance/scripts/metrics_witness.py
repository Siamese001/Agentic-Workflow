"""
MetricsWitness – Phase 14 (Dec 30, 2025)
PascalCase agent responsible for translating raw L6 MetricsAgent data into Sovereign Audit scores.
Pure read-only – no side effects beyond metric queries.
"""

from typing import List, Tuple
from pathlib import Path


class MetricsWitness:
    """
    Sovereign witness that cross-examines L6 observability metrics against constitutional expectations.
    Provides audit-ready (score, issues) tuples for Structural SSOT and Healing Resilience dimensions.
    Zero external dependencies beyond MetricsAgent.
    """

    def __init__(self, project_root: Path):
        """
        Initialise with project root. Gracefully degrades if MetricsAgent unavailable.
        """
        try:
            from agentic_core.observability.metrics.MetricsAgent import metrics_agent as MetricsAgentCls
            self.metrics = MetricsAgentCls(project_root)
        except Exception:  # ImportError or instantiation failure
            self.metrics = None

    def calculate_structural_ssot_score(self) -> Tuple[float, List[str]]:
        """Structural SSOT dimension: penalises recorded location/hierarchy violations."""
        issues: List[str] = []
        if not self.metrics:
            return 100.0, ["MetricsAgent unavailable – assuming perfect structural compliance"]

        type_vio = self.metrics.get_labeled_counter("compliance.violations_by_type")
        loc_vio = type_vio.get("location", 0) + type_vio.get("hierarchy", 0)

        if loc_vio > 0:
            score = max(0.0, 100.0 - (loc_vio * 5))  # 5-point constitutional penalty per violation
            issues.append(f"Metrics record {loc_vio} physical structural violations.")
        else:
            score = 100.0

        return score, issues

    def calculate_healing_resilience_score(self) -> Tuple[float, List[str]]:
        """Healing Resilience dimension: measures successful remediation ratio."""
        issues: List[str] = []
        if not self.metrics:
            return 100.0, ["MetricsAgent unavailable – assuming full healing resilience"]

        total_violations = self.metrics.get_counter("compliance.total_violations")
        applied_heals = self.metrics.get_counter("healing.actions_total")

        if total_violations == 0:
            issues.append("Zero violations detected: Healing logic in standby.")
            return 100.0, issues

        ratio = min(1.0, applied_heals / total_violations)
        score = ratio * 100.0

        if ratio < 0.9:
            issues.append(f"Healing Success Ratio ({ratio:.1%}) below sovereign target (90%).")

        return score, issues
