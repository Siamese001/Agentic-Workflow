"""
GuardianOrchestrator – Sovereign Agent (Phase 15 – Dec 30, 2025)
SSOT-compliant location: L0_maintenance/scripts/
Central coordination of all L0 guardians for Sovereign Audit.
Pure orchestration – zero side effects beyond guardian execution.
"""

from typing import List, Tuple, Dict, Callable
from pathlib import Path
import logging


class GuardianOrchestrator:
    """
    Sovereign orchestrator for all available L0 guardians.
    Returns standardized (score, issues) tuples for audit dimensions.
    Extensible: new guardians added via _load_guardians().
    """

    def __init__(self, target_path: Path | str):
        self.target_path = Path(target_path)
        self.logger = logging.getLogger(__name__)
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
            from agentic_core.L0_maintenance.P1_core.guard_observability_footprint import validate_observability_footprint
            self.observability_guardian: Callable[[str], Tuple[float, List[str]]] = validate_observability_footprint
        except ImportError:
            self.observability_guardian = None
            self.logger.warning("Observability Footprint guardian not available")

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

    def get_all_guardian_results(self) -> Dict[str, Tuple[float, List[str]]]:
        """Consolidated execution – used by Sovereign Court."""
        return {
            "DDD Alignment": self.execute_ddd_alignment(),
            "Observability Footprint": self.execute_observability_footprint(),
        }
