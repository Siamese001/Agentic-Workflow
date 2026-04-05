from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_signs_execution_trace,
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

_GUARDRAIL_LOG = logging.getLogger("adg.applies_guardrail")
_SAFETY_PLANE_LOG = logging.getLogger("adg.validated_by_safety_plane")
_HUMAN_REVIEW_LOG = logging.getLogger("adg.requires_human_review")
_POLICY_HASH_LOG = logging.getLogger("adg.references_policy_hash")


class AirlockProtocol:
    """
    L5 Safety Guardrail: The Execution Airlock.
    Validates tool calls against a mission-specific Permission matrix.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.allowed_tools = config.get("allowed_tools", ["read_file", "search_web", "get_status"])
        self.high_risk_tools = ["run_python", "write_file", "delete_file", "execute_shell"]

    async def acquire_permission(self, tool_name: str, args: dict[str, Any]) -> bool:
        """Determines if a tool execution is safe to proceed under Zero-Trust.

        P1/L5: emits applies_guardrail, validated_by_safety_plane,
        references_policy_hash ADG edges on every tool gate check.
        Emits requires_human_review for high-risk tools.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AirlockProtocol.acquire_permission")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AirlockProtocol.acquire_permission".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # P1/L5: emit governed tool gate ADG edges
        _GUARDRAIL_LOG.debug("applies_guardrail AIRLOCK_PROTOCOL tool=%s", tool_name)
        _SAFETY_PLANE_LOG.debug("validated_by_safety_plane AIRLOCK_PROTOCOL tool=%s", tool_name)
        _POLICY_HASH_LOG.debug("references_policy_hash AIRLOCK_PROTOCOL tool=%s policy=airlock", tool_name)
        if tool_name not in self.allowed_tools and tool_name not in self.high_risk_tools:
            raise PermissionError(f"Airlock Block: Tool '{tool_name}' is not in the Sovereign Registry.")
        if tool_name in self.high_risk_tools:
            logging.info(f"Airlock: Evaluating High-Risk tool '{tool_name}'...")
            # P1/L5: high-risk tools require human review signal
            _HUMAN_REVIEW_LOG.debug("requires_human_review AIRLOCK_PROTOCOL tool=%s", tool_name)
            return self._validate_risk_parameters(tool_name, args)
        return True

    def _validate_risk_parameters(self, tool: str, args: dict) -> bool:
        path = str(args.get("path", "")).lower()
        protected_targets = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
        if any(bad in path for bad in protected_targets):
            logging.error(f"Airlock: Blocked access attempt to protected path: {path}")
            return False
        return True
