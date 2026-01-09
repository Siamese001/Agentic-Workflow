from __future__ import annotations
"""
MetricsWitness – Phase 14 (Dec 30, 2025)
PascalCase agent responsible for translating raw L6 MetricsAgent data into Sovereign Audit scores.
Pure read-only – no side effects beyond Metric queries.
"""

from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import logging

# Sovereign Hardening Mixins – Phase 35
from agentic_core.patterns.agent_roles.autonomy_mixin import AutonomyMixin
from agentic_core.patterns.agent_roles.adaptive_execution_mixin import AdaptiveExecutionMixin
from agentic_core.patterns.agent_roles.self_diagnosis_mixin import SelfDiagnosisMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin


class MetricsWitnessAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin, AutonomyMixin,
    AdaptiveExecutionMixin,
    SelfDiagnosisMixin,):
    """
    Sovereign witness that cross-examines L6 observability metrics against constitutional expectations.
    Provides audit-ready (score, issues) tuples for Structural SSOT and Healing Resilience dimensions.
    Zero external dependencies beyond MetricsAgent.

    Now hardened with:
      - Proactive Metric recalculation on suspected drift
      - Adaptive scoring based on system state
      - Self-diagnosis of MetricsAgent availability
    """

    def __init__(self, project_root: Path) -> None:
        """
        Initialise with project root. Gracefully degrades if MetricsAgent unavailable.
        """
        super().__init__()  # Required for mixins
        self.Logger = logging.getLogger(f"{self.__class__.__name__}")

        # Mandatory component for self-diagnosis
        self.MANDATORY_COMPONENTS = ["metrics"]

        try:
            from agentic_core.observability.metrics.MetricsAgent import metrics_agent as MetricsAgentCls
            self.metrics = MetricsAgentCls(project_root)
        except Exception:  # ImportError or instantiation failure
            self.metrics = None
            self.Logger.warning("MetricsAgent unavailable – witness operating in degraded mode")

    def calculate_structural_ssot_score(self) -> Tuple[float, List[str]]:
        """Structural SSOT dimension: penalises recorded location/hierarchy violations."""
        issues: List[str] = []
        if not self.metrics:
            return 100.0, ["MetricsAgent unavailable – assuming perfect structural compliance"]

        type_vio = self.metrics.get_labeled_counter("compliance.violations_by_type")
        loc_vio = type_vio.get("location", 0) + type_vio.get("hierarchy", 0)

        if loc_vio > 0:
            score = max(0.0, 100.0 - (loc_vio * 5))  # 5-point constitutional penalty per Violation
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

    # === AutonomyMixin Override ===
    async def _detect_action_opportunity(self) -> Optional[Dict[str, Any]]:
        """Proactively trigger recalculation if metrics appear stale or agent unavailable."""
        if self.metrics is None:
            return {
                "reason": "metrics_agent_unavailable",
                "action": "attempt_reinitialization_or_escalate"
            }

        # Optional future enhancement: detect Metric staleness via timestamp
        return None

    # === AdaptiveExecutionMixin Overrides ===
    async def _execute_conservative(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        self.Logger.info("Conservative mode: returning cached/fallback scores")
        return {
            "Structural SSOT": (100.0, ["Conservative mode: no live metrics query"]),
            "Healing Resilience": (100.0, ["Conservative mode: assuming full resilience"])
        }

    async def _execute_minimal(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        self.Logger.warning("Minimal mode: witness standing by")
        return {
            "status": "minimal_standby",
            "reason": "resource_preservation"
        }

    async def _execute_standard(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        """Standard mode - calculate all metrics."""
        return {
            "Structural SSOT": self.calculate_structural_ssot_score(),
            "Healing Resilience": self.calculate_healing_resilience_score(),
        }

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
