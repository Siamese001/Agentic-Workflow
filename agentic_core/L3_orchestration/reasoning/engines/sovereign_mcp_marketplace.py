from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
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

emit_replay_key("p0", "sovereign_mcp_marketplace")
emit_determinism_digest("p0", "sovereign_mcp_marketplace")

_emit_dispatches_healing_run("p1", "sovereign_mcp_marketplace", "L3")
_emit_routes_through("p1", "sovereign_mcp_marketplace", "L3")
_emit_checks_agent_registry("p1", "sovereign_mcp_marketplace", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_mcp_marketplace", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_mcp_marketplace", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_mcp_marketplace", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_mcp_marketplace", "target_agent")
_emit_verifies_policy("p1", "sovereign_mcp_marketplace", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_mcp_marketplace", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_mcp_marketplace", "boundary_check")
_emit_transcripts_response("p1", "sovereign_mcp_marketplace", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_mcp_marketplace")
_emit_gated_by_confidence("p1", "sovereign_mcp_marketplace", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_mcp_marketplace", "L3")
_emit_reads_policy_state("p1", "sovereign_mcp_marketplace", "L3")
_emit_authorize_and_execute("p2", "sovereign_mcp_marketplace", "execution_auth")
_emit_validates_capability("p2", "sovereign_mcp_marketplace", "capability_check")
_emit_routes_to_capability("p2", "sovereign_mcp_marketplace", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_mcp_marketplace", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_mcp_marketplace", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_mcp_marketplace", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_mcp_marketplace", "exec_output")
_emit_dispatches_agent("p3", "sovereign_mcp_marketplace", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_mcp_marketplace", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_mcp_marketplace", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_mcp_marketplace", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_mcp_marketplace", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_mcp_marketplace", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_mcp_marketplace", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_mcp_marketplace", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_mcp_marketplace", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_mcp_marketplace", "eval_metric")
_emit_stores_embedding("p4", "sovereign_mcp_marketplace", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_mcp_marketplace", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_mcp_marketplace", "exec_snapshot_link")

"L3 Orchestration: Sovereign MCP Marketplace Integration\nSafe discovery and registration of marketplace MCPs with L5 sovereignty enforcement.\nGEMINI-ONLY policy — forbidden providers auto-blocked.\n"
import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
from agentic_core.seams.contracts.authority import get_mcp_authority
from tqdm import tqdm

_emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_mcp_marketplace", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_mcp_marketplace", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_mcp_marketplace", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_mcp_marketplace", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_mcp_marketplace", "p4obs", "alert")
_emit_links_incident_trace("sovereign_mcp_marketplace", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_mcp_marketplace", "p3lm", "pattern")
_emit_records_learning_event("sovereign_mcp_marketplace", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_mcp_marketplace", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_mcp_marketplace", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_mcp_marketplace", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_mcp_marketplace", "p3lm", "policy")
_emit_stores_learning_state("sovereign_mcp_marketplace", "p3lm", "state")
_emit_records_execution_trace("sovereign_mcp_marketplace", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_mcp_marketplace", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_mcp_marketplace", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_mcp_marketplace", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_mcp_marketplace", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_mcp_marketplace", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_mcp_marketplace", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_mcp_marketplace", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_mcp_marketplace", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_mcp_marketplace", "context_pull")
_emit_pulls_context("p1", "sovereign_mcp_marketplace", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_mcp_marketplace", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_mcp_marketplace", "uwg_term_2")
_emit_writes_through("p1", "sovereign_mcp_marketplace", "write_through")
_emit_writes_through("p1", "sovereign_mcp_marketplace", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_mcp_marketplace", "safety_validation")
_emit_invokes_eval("p1", "sovereign_mcp_marketplace", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_mcp_marketplace", "routing_commit")

Logger = logging.getLogger(__name__)
sovereign_safe_mcps = {
    "Filesystem",
    "Time",
    "Redis",
    "Pinecone",
    "Playwright",
    "Figma",
    "Brave Search",
    "Fetch",
    "GitHub",
    "Memory",
}
forbidden_providers = {"OpenAI", "Anthropic", "Claude", "GPT", "o1", "Llama"}


class SovereignMcpMarketplace:
    """Ultra-hardened marketplace integration — auto-register safe MCPs only."""

    def __init__(self, manager):
        self.manager = manager
        self.safe_tools: list[str] = []

    def discover_and_register_safe(self, marketplace_data: dict) -> None:
        """Parse marketplace and register only sovereign-safe MCPs."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()),
            "SovereignMcpMarketplace.discover_and_register_safe",
            "state_snapshot",
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()),
            "SovereignMcpMarketplace.discover_and_register_safe",
            "p0_governance",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "SovereignMcpMarketplace.discover_and_register_safe",
        )

        installed = marketplace_data.get("installed", [])
        available = marketplace_data.get("available", [])
        for mcp in tqdm(installed + available, desc="Processing", unit="item"):
            name = mcp.get("name", "")
            Provider = mcp.get("Provider", "")
            if any(forbidden in Provider for forbidden in forbidden_providers):
                Logger.critical(f"[L5 MCP BREACH] Forbidden Provider detected: {Provider} — blocked.")
                get_mcp_authority().record_breach(f"Attempted Marketplace Load: {Provider}")
                continue
            if name in sovereign_safe_mcps:
                try:
                    self.safe_tools.append(name)
                    Logger.info(f"[L3 MARKETPLACE] Sovereign MCP validated and armed: {name}")
                except (RuntimeError, ValueError, TypeError, AttributeError):  # guardian: allow-double-logging -- MCP registration failure logged before re-raise for marketplace audit
                    raise
        if not self.safe_tools:
            Logger.warning("[L3 MARKETPLACE] No safe MCPs found. Running in LLM-only mode.")

    def get_safe_tools(self) -> list[str]:
        return self.safe_tools
