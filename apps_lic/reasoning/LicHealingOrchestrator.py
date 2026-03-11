"""apps_lic/reasoning/LicHealingOrchestrator.py — LIC healing orchestrator.

PHASE 4 META-LEARNING (Feb 2026):
- MetaLearningClient integration for healing pattern memory
- Incident pattern caching and recall
- Recovery playbook optimization via learned patterns
- Healing depth tracking to prevent infinite loops

Refactored: 2026-03-11 (P3-B) — now subclasses BaseHealingOrchestrator.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from apps_shared.reasoning.BaseHealingOrchestrator import BaseHealingOrchestrator

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


@dataclass
class LicHealingOrchestrator(BaseHealingOrchestrator):
    """Sovereign LIC Healing Orchestrator.

    Coordinates domain-specific recovery actions for the LIC ecosystem.

    [PHASE 4] Meta-Learning Integration:
    - Caches successful incident resolutions for future recall
    - Learns optimal recovery playbook selections
    - Tracks healing depth to prevent infinite loops
    - Domain-specific pattern matching (apps_lic)

    Inherits ml_heal_with_learning_enhanced() and orchestrate_healing_cycle()
    from BaseHealingOrchestrator (2026-03-11, P3-B).
    Use orchestrate_healing_cycle() in place of the former orchestrate_incident_recovery().
    """

    # Defensive State Management
    active_incidents: dict[str, Any] = field(default_factory=dict)
    recovery_playbooks: dict[str, str] = field(
        default_factory=lambda: {
            "database_lock": "release_and_retry",
            "api_timeout": "exponential_backoff",
        },
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        # CRITICAL: Trigger Core Lock
        super().__post_init__()
        Logger.debug(f"[{self.__class__.__name__}] Meta-Learning healing orchestrator initialized")

    def assess_system_health(self, telemetry: dict[str, Any]) -> dict[str, str]:
        """
        Evaluate LIC domain health status.
        """
        status = "healthy"
        if telemetry.get("error_rate", 0) > 0.05:
            status = "degraded"
            self._register_incident("high_error_rate")

        return {
            "status": status,
            "orchestrator_id": self.name,
            "active_incidents": str(len(self.active_incidents)),
        }

    def _register_incident(self, incident_type: str) -> None:
        """Internal incident tracking."""
        incident_id = str(uuid.uuid4())
        self.active_incidents[incident_id] = {"type": incident_type, "status": "active"}

    # ==================== PHASE 4: META-LEARNING HEALING ====================

    def ml_heal_incident(
        self,
        incident: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Heal an incident using meta-learning enhanced strategy.

        This method:
        1. Checks healing depth to prevent infinite loops
        2. Attempts to recall a successful resolution pattern
        3. If no pattern found, executes standard healing
        4. Stores successful resolutions for future use

        Args:
            incident: The incident to heal

        Returns:
            Healing result dictionary
        """
        incident_id = incident.get("id", str(uuid.uuid4()))
        incident_type = incident.get("type", "unknown")

        # Step 1: Check healing depth
        if not self.ml_check_healing_depth(incident_id):
            Logger.warning(f"[{self.__class__.__name__}] Healing depth limit for {incident_id}")
            return {
                "status": "skipped",
                "reason": "healing_depth_limit_reached",
                "incident_id": incident_id,
            }

        # Step 2: Increment depth
        self.ml_increment_healing_depth(incident_id)

        try:
            # Step 3: Try to recall a successful resolution pattern
            cached_resolution = self.ml_recall_incident_resolution(incident_type)
            if cached_resolution:
                Logger.info(f"[{self.__class__.__name__}] Using cached resolution for {incident_type}")
                self.ml_reset_healing_depth(incident_id)
                return {
                    **cached_resolution,
                    "source": "meta_learning_cache",
                    "incident_id": incident_id,
                }

            # Step 4: Execute standard healing
            result = self._execute_healing(incident)

            # Step 5: Store successful resolution
            if result.get("status") in ("fixed", "resolved", "success"):
                self.ml_cache_incident_resolution(incident_type, result)
                self.ml_reset_healing_depth(incident_id)

            return result

        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Healing failed: {e}")
            return {
                "status": "error",
                "reason": str(e),
                "incident_id": incident_id,
            }

    def _execute_healing(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Execute domain-specific healing by dispatching to appropriate agents.

        HEAL-GAP-04: Dispatches based on incident.type:
          - structural → ControlPlane.evaluate_input/output()
          - schema/output_contract → HOPPipelineExecutor re-run on failing stage
          - llm_call → re-route via SovereignLLMGateway with corrected model ID
        """
        incident_type = incident.get("type", "unknown")
        playbook = self.recovery_playbooks.get(incident_type, "default_recovery")
        Logger.info(
            "[%s] _execute_healing: incident_type=%s playbook=%s",
            self.__class__.__name__,
            incident_type,
            playbook,
        )

        if incident_type == "structural":
            return self._heal_structural(incident)
        elif incident_type in ("schema", "output_contract"):
            return self._heal_schema(incident)
        elif incident_type in ("llm_call", "api_timeout"):
            return self._heal_llm_call(incident)
        else:
            return {
                "status": "resolved",
                "playbook_used": playbook,
                "incident_type": incident_type,
            }

    def _heal_structural(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Route structural violations through ControlPlane."""
        try:
            from apps_lic.engines.control_plane import ControlPlane

            cp = ControlPlane()
            content = incident.get("content", "")
            decision = cp.evaluate_input(content)
            return {
                "status": "resolved",
                "healer": "ControlPlane",
                "action": decision.action.value,
                "is_safe": decision.is_safe,
                "incident_type": incident.get("type"),
            }
        except Exception as exc:
            Logger.error("[%s] _heal_structural failed: %s", self.__class__.__name__, exc)
            return {"status": "error", "healer": "ControlPlane", "reason": str(exc)}

    def _heal_schema(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Re-run the failing HOP stage via HOPPipelineExecutor."""
        try:
            from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor

            stage_id = incident.get("stage_id", 5)
            executor = HOPPipelineExecutor()
            result = executor.execute_stage(stage_id, incident.get("context", {}))
            return {
                "status": "resolved",
                "healer": "HOPPipelineExecutor",
                "stage_id": stage_id,
                "result": result,
                "incident_type": incident.get("type"),
            }
        except Exception as exc:
            Logger.error("[%s] _heal_schema failed: %s", self.__class__.__name__, exc)
            return {"status": "error", "healer": "HOPPipelineExecutor", "reason": str(exc)}

    def _heal_llm_call(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Re-route LLM call via SovereignLLMGateway with corrected model ID."""
        try:
            import asyncio

            from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway

            gateway = SovereignLLMGateway()
            prompt = incident.get("prompt", incident.get("content", ""))
            request = GenerationRequest(
                agent_id="LicHealingOrchestrator",
                provider="google",
                model="gemini-2.5-pro",
                prompt=prompt,
            )
            loop = asyncio.new_event_loop()
            try:
                response = loop.run_until_complete(gateway.route_generation(request))
            finally:
                loop.close()
            return {
                "status": "resolved",
                "healer": "SovereignLLMGateway",
                "model": "gemini-2.5-pro",
                "content": response.content,
                "incident_type": incident.get("type"),
            }
        except Exception as exc:
            Logger.error("[%s] _heal_llm_call failed: %s", self.__class__.__name__, exc)
            return {"status": "error", "healer": "SovereignLLMGateway", "reason": str(exc)}

    def ml_cache_incident_resolution(
        self,
        incident_type: str,
        resolution: dict[str, Any],
    ) -> bool:
        """
        Cache a successful incident resolution.

        Args:
            incident_type: Type of incident
            resolution: Resolution data

        Returns:
            True if cached successfully
        """
        cache_key = f"incident_resolution:{incident_type}"
        return self.ml_cache_set(cache_key, resolution)

    def ml_recall_incident_resolution(
        self,
        incident_type: str,
    ) -> dict[str, Any] | None:
        """
        Recall a cached incident resolution.

        Args:
            incident_type: Type of incident

        Returns:
            Cached resolution or None
        """
        cache_key = f"incident_resolution:{incident_type}"
        return self.ml_cache_get(cache_key)

    def ml_optimize_playbook_selection(
        self,
        incident_type: str,
        telemetry: dict[str, Any],
    ) -> str:
        """
        Select optimal recovery playbook using meta-learning.

        Args:
            incident_type: Type of incident
            telemetry: Current system telemetry

        Returns:
            Optimal playbook name
        """
        # Try to recall a successful playbook for this incident type
        cache_key = f"optimal_playbook:{incident_type}"
        cached_playbook = self.ml_cache_get(cache_key)

        if cached_playbook:
            return cached_playbook.get("playbook", self.recovery_playbooks.get(incident_type, "default"))

        # Fall back to default playbook
        return self.recovery_playbooks.get(incident_type, "default_recovery")

    def ml_record_playbook_success(
        self,
        incident_type: str,
        playbook: str,
        success_metrics: dict[str, Any],
    ) -> bool:
        """
        Record a successful playbook execution for future optimization.

        Args:
            incident_type: Type of incident
            playbook: Playbook that was used
            success_metrics: Metrics from the successful execution

        Returns:
            True if recorded successfully
        """
        cache_key = f"optimal_playbook:{incident_type}"
        return self.ml_cache_set(
            cache_key,
            {
                "playbook": playbook,
                "metrics": success_metrics,
            },
        )

    def _cycle_results_key(self) -> str:
        """LIC orchestrator uses 'incident_recovery' as pattern cache key."""
        return "incident_recovery"
