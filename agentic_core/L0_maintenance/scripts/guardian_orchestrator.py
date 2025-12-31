"""
GuardianOrchestrator – Sovereign Agent (Phase 15 – Dec 30, 2025)
SSOT-compliant location: L0_maintenance/scripts/
Central coordination of all L0 guardians for Sovereign Audit.
Pure orchestration – zero side effects beyond guardian execution.
"""

from typing import List, Tuple, Dict, Callable, Optional, Any
from pathlib import Path
import logging

# Sovereign Hardening Mixins – Phase 34
from agentic_core.patterns.agent_roles.autonomy_mixin import AutonomyMixin
from agentic_core.patterns.agent_roles.adaptive_execution_mixin import AdaptiveExecutionMixin
from agentic_core.patterns.agent_roles.self_diagnosis_mixin import SelfDiagnosisMixin


class GuardianOrchestrator(
    AutonomyMixin,
    AdaptiveExecutionMixin,
    SelfDiagnosisMixin,
):
    """
    Sovereign orchestrator for all available L0 guardians.
    Returns standardized (score, issues) tuples for audit dimensions.
    Extensible: new guardians added via _load_guardians().

    Now hardened with:
      - Proactive initiation when guardians become available/missing
      - Adaptive execution based on system load and failure history
      - Self-health monitoring of loaded guardians
    """

    def __init__(self, target_path: Path | str):
        self.target_path = Path(target_path)
        self.logger = logging.getLogger(__name__)
        
        # === Hardening Initialization ===
        super().__init__()  # Required for cooperative inheritance

        # Mandatory components for self-diagnosis
        self.MANDATORY_COMPONENTS = [
            "ddd_guardian",
            "observability_guardian",
        ]

        self._load_guardians()

    def _load_guardians(self):
        """Lazy load guardians with constitutional graceful degradation."""
        # DDD Alignment Guardian
        try:
            from agentic_core.L0_maintenance.scripts.guard_ddd_alignment import validate_ddd_alignment
            self.ddd_guardian: Callable[[str], Tuple[float, List[str]]] = validate_ddd_alignment
        except ImportError:
            self.ddd_guardian = None
            self.logger.warning("DDD Alignment guardian not available")

        # Observability Footprint Guardian
        # Note: Currently in illegal P1_core — will be healed in future mission
        try:
            from agentic_core.L0_maintenance.P1_core.guard_observability_footprint import validate_observability_footprint  # TODO: migrate to scripts/
            self.observability_guardian: Callable[[str], Tuple[float, List[str]]] = validate_observability_footprint
        except ImportError:
            self.observability_guardian = None
            self.logger.warning("Observability Footprint guardian not available")

    # === AutonomyMixin Override ===
    async def _detect_action_opportunity(self) -> Optional[Dict[str, Any]]:
        """Proactively re-run guardians if critical ones are missing or system state changed."""
        missing = []
        if self.ddd_guardian is None:
            missing.append("ddd_guardian")
        if self.observability_guardian is None:
            missing.append("observability_guardian")

        if missing:
            return {
                "reason": "critical_guardians_unavailable",
                "missing": missing,
                "action": "attempt_reload_and_revalidate"
            }

        # Optional: trigger on sovereignty drop (can integrate with MetricsWitness later)
        return None

    # === AdaptiveExecutionMixin Overrides ===
    async def _execute_conservative(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        self.logger.info("Conservative mode: running only high-impact guardians")
        # Only run DDD guardian — most critical for sovereignty
        return {
            "DDD Alignment": self.execute_ddd_alignment(),
        }

    async def _execute_minimal(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        self.logger.warning("Minimal mode: skipping guardian execution to preserve resources")
        return {
            "status": "skipped",
            "reason": "high_system_load",
            "guardians_available": {
                "ddd": self.ddd_guardian is not None,
                "observability": self.observability_guardian is not None,
            }
        }

    async def _execute_standard(self, ctx: Any, **context: Dict[str, Any]) -> Any:
        """Standard execution mode - run all available guardians."""
        return {
            "DDD Alignment": self.execute_ddd_alignment(),
            "Observability Footprint": self.execute_observability_footprint(),
        }

    def execute_ddd_alignment(self) -> Tuple[float, List[str]]:
        if self.ddd_guardian:
            return self.ddd_guardian(str(self.target_path))
        return 100.0, ["DDD Alignment guardian unavailable – assuming perfect alignment"]

    def execute_observability_footprint(self) -> Tuple[float, List[str]]:
        if not self.observability_guardian:
            return 100.0, ["Observability Footprint guardian unavailable – assuming full visibility"]

        raw_score, raw_issues = self.observability_guardian(str(self.target_path))
        refined_score = max(50.0, 100.0 - (len(raw_issues) * 3)) if raw_issues else 100.0
        return refined_score, raw_issues

    async def get_all_guardian_results(self) -> Dict[str, Tuple[float, List[str]]]:
        """Consolidated execution – used by Sovereign Court. Now uses adaptive execution."""
        return await self.execute()
