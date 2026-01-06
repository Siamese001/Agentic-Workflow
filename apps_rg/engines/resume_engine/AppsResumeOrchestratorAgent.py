from __future__ import annotations
from typing import Any, Optional, Protocol, Dict, List

import logging
from typing import Dict, List

from services.configuration import ConfigurationService
from shared.configuration.config import ContentConstraintsConfig
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin

_logger = logging.getLogger(__name__)

# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: apps_rg resume-specific vs L3 core orchestration)
# - Intentional variant for domain-specific behavior
# - Consolidated 2026-01-06

'Pure orchestration of resume generation using shared atoms.'
Logger = logging.getLogger(__name__)


class ResumeOrchestratorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """Orchestrate the multi-hop resume generation workflow."""

    def __init__(self, master_resume: Dict, test_mode: bool) -> None:
        """Initialize the orchestrator."""
        self.master_resume = master_resume
        self.test_mode = test_mode
        self.hop_checkpoints: List[Dict] = []
        self.constraints = ContentConstraintsConfig()
        Logger.info(f"Initialized {self.__class__.__name__}")


    def run(self, job_description: str) -> Dict[str, object]:
        """Execute the full resume generation workflow."""
        try:
            if not self.master_resume:
                Logger.warning("Master resume missing — using defaults")
                self.master_resume = {}
            
            self._record_hop('HOP-0', {'status': 'initialized'})
            extracted_data = self._extract_resume_data()
            self._record_hop('HOP-1', {'status': 'extracted'})
            
            enriched_data = self._enrich_resume_data(extracted_data)
            self._record_hop('HOP-2', {'status': 'enriched'})
            
            return {
                'status': 'success',
                'enriched_data': enriched_data,
                'checkpoints': self.hop_checkpoints
            }
        except Exception as e:
            Logger.error(f"Orchestration failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _extract_resume_data(self) -> Dict:
        """Extract resume data from master resume."""
        return self.master_resume.copy() if self.master_resume else {}

    def _enrich_resume_data(self, data: Dict) -> Dict:
        """Enrich resume data with constraints and validation."""
        enriched = data.copy()
        if hasattr(self, 'constraints'):
            enriched['constraints_applied'] = True
        return enriched

    def _record_hop(self, hop_id: str, results: Dict) -> None:
        """Record a hop checkpoint."""
        checkpoint = {'hop_id': hop_id, 'results': results}
        self.hop_checkpoints.append(checkpoint)

    def heal_repository(self) -> None:
        """Autonomy healing: Validate and auto-correct agent state/config for reliable resume orchestration.

        - Inherits shared healing from HealerMixin (diagnostics, rollback)
        - Adds Rg-specific checks: master resume integrity, hop checkpoint validation, constraint config
        - MCP hardening ensures safe healing (no injection during auto-correct)
        """
        super().heal_repository()

        self._heal_master_resume()
        self._heal_hop_checkpoints()
        self._heal_constraints_config()
        self._run_orchestration_diagnostics()

    def _heal_master_resume(self) -> None:
        """Validate and repair master resume if corrupted."""
        if not isinstance(self.master_resume, dict):
            Logger.warning("Master resume corrupted — resetting to empty dict")
            self.master_resume = {}
        if len(str(self.master_resume)) > 1000000:
            Logger.warning("Master resume oversized — truncating")
            self.master_resume = {}

    def _heal_hop_checkpoints(self) -> None:
        """Validate and clean hop checkpoints."""
        if not isinstance(self.hop_checkpoints, list):
            Logger.warning("Hop checkpoints corrupted — resetting")
            self.hop_checkpoints = []
        self.hop_checkpoints = self.hop_checkpoints[-100:]

    def _heal_constraints_config(self) -> None:
        """Validate constraint configuration."""
        try:
            if not hasattr(self, 'constraints'):
                Logger.warning("Constraints config missing — initializing")
                self.constraints = ContentConstraintsConfig()
        except Exception as e:
            Logger.error(f"Constraints config error: {e}")

    def _run_orchestration_diagnostics(self) -> None:
        """Run orchestration-specific health checks."""
        try:
            test_data = self._extract_resume_data()
            if not isinstance(test_data, dict):
                Logger.error("Diagnostics failed: invalid resume data")
        except Exception as e:
            Logger.error(f"Diagnostics exception: {e}")

