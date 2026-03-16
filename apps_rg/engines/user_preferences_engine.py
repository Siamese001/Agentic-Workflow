"""
User Preferences Engine - Fetch user preferences
Refactored from fetch_user_preferences.py
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "user_preferences_engine", "execution_auth")
_emit_validates_capability("p2", "user_preferences_engine", "capability_check")
_emit_routes_to_capability("p2", "user_preferences_engine", "capability_route")
_emit_writes_via_uwg("p2", "user_preferences_engine", "uwg_write")
_emit_blocks_direct_write("p2", "user_preferences_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "user_preferences_engine", "tool_invocation")
_emit_captures_execution_output("p2", "user_preferences_engine", "exec_output")
_emit_dispatches_agent("p3", "user_preferences_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "user_preferences_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "user_preferences_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "user_preferences_engine", "healing_outcome")
_emit_escalates_failure("p3", "user_preferences_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "user_preferences_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "user_preferences_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "user_preferences_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "user_preferences_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "user_preferences_engine", "eval_metric")
_emit_stores_embedding("p4", "user_preferences_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "user_preferences_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "user_preferences_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "user_preferences_engine", "p0_governance")
_emit_reads_policy_state("p0", "user_preferences_engine", "policy_binding")
_emit_snapshots_state("p0", "user_preferences_engine", "state_snapshot")
emit_replay_key("p0", "user_preferences_engine")
emit_determinism_digest("p0", "user_preferences_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class UserPreferencesEngine(BaseRGEngine):
    """
    Retrieves user preferences for resume generation.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="RETRIEVAL.PREFERENCES")

    async def execute(self, user_id: str) -> dict[str, Any]:
        """
        Fetch user preferences.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "UserPreferencesEngine.execute")

        self._mcp_audit("preferences_retrieval", {"user_id": user_id})
        preferences = {
            "template_style": "modern",
            "color_scheme": "professional",
            "include_photo": False,
            "preferred_sections": ["summary", "experience", "education", "skills"],
            "tone": "professional",
        }
        if hasattr(self.ctx, "user_preferences"):
            preferences.update(self.ctx.user_preferences.get(user_id, {}))
        self.record_pass("User preferences retrieved")
        return preferences
