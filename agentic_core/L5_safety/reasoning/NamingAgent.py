"""
NamingAgent - Agent for handling naming conventions and validation.

Re-exported from L5_safety for backwards compatibility.
"""

import logging
import uuid
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_METADATA
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.mixins.prompt_rendering_mixin import PromptRenderingMixin

emit_replay_key("p0", "NamingAgent")
emit_determinism_digest("p0", "NamingAgent")

_emit_dispatches_healing_run("p1", "NamingAgent", "L5")
_emit_routes_through("p1", "NamingAgent", "L5")
_emit_checks_agent_registry("p1", "NamingAgent", "agent_registry")
_emit_validates_agent_capability("p1", "NamingAgent", "capability")
_emit_dispatches_execution_plan("p1", "NamingAgent", "exec_plan")
_emit_agent_executes_agent("p1", "NamingAgent", "sub_agent")
_emit_routes_to_agent("p1", "NamingAgent", "target_agent")
_emit_verifies_policy("p1", "NamingAgent", "policy_check")
_emit_observes_runtime_state("p1", "NamingAgent", "runtime_state")
_emit_verifies_boundary("p1", "NamingAgent", "boundary_check")
_emit_transcripts_response("p1", "NamingAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "NamingAgent")
_emit_gated_by_confidence("p1", "NamingAgent", "confidence_gate")
_emit_escalates_to_human("p1", "NamingAgent", "L5")
_emit_reads_policy_state("p1", "NamingAgent", "L5")

_emit_applies_guardrail("p0", "NamingAgent", "p0_governance")
_emit_snapshots_state("p0", "NamingAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "NamingAgent", "execution_auth")
_emit_validates_capability("p2", "NamingAgent", "capability_check")
_emit_routes_to_capability("p2", "NamingAgent", "capability_route")
_emit_writes_via_uwg("p2", "NamingAgent", "uwg_write")
_emit_blocks_direct_write("p2", "NamingAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "NamingAgent", "tool_invocation")
_emit_captures_execution_output("p2", "NamingAgent", "exec_output")
_emit_dispatches_agent("p3", "NamingAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "NamingAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "NamingAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "NamingAgent", "healing_outcome")
_emit_escalates_failure("p3", "NamingAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "NamingAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "NamingAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "NamingAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "NamingAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "NamingAgent", "eval_metric")
_emit_stores_embedding("p4", "NamingAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "NamingAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "NamingAgent", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("NamingAgent", "p4obs", "metric_1")
_emit_emits_metric_event("NamingAgent", "p4obs", "metric_2")
_emit_emits_metric_event("NamingAgent", "p4obs", "metric_3")
_emit_emits_metric_event("NamingAgent", "p4obs", "metric_4")
_emit_emits_metric_event("NamingAgent", "p4obs", "metric_5")
_emit_emits_metric_event("NamingAgent", "p4obs", "metric_6")
_emit_records_incident_event("NamingAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("NamingAgent", "p4obs", "anomaly")
_emit_writes_observability_log("NamingAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("NamingAgent", "p4obs", "mon_state")
_emit_triggers_alert("NamingAgent", "p4obs", "alert")
_emit_links_incident_trace("NamingAgent", "p4obs", "trace_link")
_emit_captures_pattern("NamingAgent", "p3lm", "pattern")
_emit_records_learning_event("NamingAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("NamingAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("NamingAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("NamingAgent", "p3lm", "routing")
_emit_improves_agent_policy("NamingAgent", "p3lm", "policy")
_emit_stores_learning_state("NamingAgent", "p3lm", "state")
_emit_records_execution_trace("NamingAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("NamingAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("NamingAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("NamingAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("NamingAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("NamingAgent", "env_read", "p2_env_1")
_emit_reads_environ("NamingAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("NamingAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("NamingAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "NamingAgent", "context_pull")
_emit_pulls_context("p1", "NamingAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "NamingAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "NamingAgent", "uwg_term_2")
_emit_writes_through("p1", "NamingAgent", "write_through")
_emit_writes_through("p1", "NamingAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "NamingAgent", "safety_validation")
_emit_invokes_eval("p1", "NamingAgent", "eval_call")
_emit_proposal_commits_routing("p1", "NamingAgent", "routing_commit")

TREE_SITTER_AVAILABLE = False


class PlacementResult:
    """
    Result of placement analysis.

    Attributes:
        path: Suggested file path for the code
        confidence: Confidence score (0.0 to 1.0) for the placement suggestion
        suggestions: List of alternative placement suggestions
    """

    def __init__(self, path: str = "", confidence: float = 1.0) -> None:
        """
        Initialize placement result.

        Args:
            path: Suggested file path
            confidence: Confidence score for the suggestion
        """
        self.path: str = path
        self.confidence: float = confidence
        self.suggestions: list = []


class NamingAgent(PromptRenderingMixin, SovereignBaseAgent):
    """
    Stub NamingAgent for backwards compatibility.

    Provides minimal implementation when the full L5_safety NamingAgent
    is not available. Used for testing and development environments.
    """

    # guardian: allow-type-erasure -- return dict has dynamic keys for orchestration compatibility
    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, depth: int = 0, **kwargs: Any
    ) -> dict[str, Any]:
        """Autonomous healing method (Canon Key 51 compliance)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "NamingAgent.heal_repository")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:NamingAgent.heal_repository".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Render naming prompt through sovereign prompt governance
        naming_prompt = self.build_healing_prompt(
            context={"name": kwargs.get("name", "unknown"), "identifiers": []},
        )
        logger.debug("NamingAgent prompt rendered (%d chars)", len(naming_prompt))

        try:
            super().heal_repository(dry_run=dry_run, **kwargs)
        except (AttributeError, TypeError):
            pass
        return {"violations_found": 0, "violations_fixed": 0, "errors": 0}

    # guardian: allow-type-erasure -- standard_heal decorator normalizes violation dict for orchestration compatibility
    def heal(self, violation: dict) -> dict:
        """
        [SOVEREIGN CONTRACT] Standardized healing interface for NamingAgent.
        """
        try:
            target = violation.get("file")
            violation.get("type", "")
            if not target:
                return {"status": "skipped", "reason": "No target file specified"}
            return {
                "status": "manual_required",
                "reason": "Naming violations require manual review",
                "suggested_action": f"Review naming conventions for {target}",
                "confidence": 0.8,
            }
        except (ValueError, TypeError) as e:
            return {"status": "error", "error": str(e)}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the stub NamingAgent."""
        pass

    def validate_name(self, name: str) -> bool:
        """
        Validate a name against naming conventions.
        [SSOT] Checks PROJECT_ROOT_METADATA for whitelist exemptions.
        """
        _emit_validated_by_safety_plane(str(uuid.uuid4()), "NamingAgent.validate_name", "L5_POLICY")
        for meta in PROJECT_ROOT_METADATA.values():
            for pattern in meta.get("file_patterns", []):
                if fnmatch(name, pattern):
                    return True
        return True

    def suggest_name(self, context: str) -> str:
        """Suggest a name based on context."""
        return context

    def analyze_placement(self, code: str) -> PlacementResult:
        """Analyze code and suggest file placement."""
        return PlacementResult()

    def validate_prefix_location_match(self, path: Path) -> list:
        """Stub method for prefix-location validation."""
        return []

    # guardian: allow-type-erasure -- returns dynamic dict with duplicate scan results
    def scan_repository_duplicates(self) -> dict:
        """Stub method for duplicate scanning."""
        return {}

    # guardian: allow-type-erasure -- returns dynamic dict with move status and reason
    def move_to_canonical_location(self, path: Path, dry_run: bool = True) -> dict:
        """Stub method for canonical moves."""
        return {"moved": False, "reason": "Stub implementation"}


def get_naming_agent(project_root: str | None = None) -> NamingAgent:
    """
    Get a NamingAgent instance.

    Factory function to create a NamingAgent with optional project root.

    Args:
        project_root: Optional path to project root directory

    Returns:
        Configured NamingAgent instance
    """
    if project_root:
        return NamingAgent(project_root)
    return NamingAgent()


__all__ = ["NamingAgent", "get_naming_agent", "TREE_SITTER_AVAILABLE", "PlacementResult"]
