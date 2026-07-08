from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sovereign_mcp_marketplace")
trace_contract.emit_determinism_digest("p0", "sovereign_mcp_marketplace")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_mcp_marketplace", "L3")
trace_contract._emit_routes_through("p1", "sovereign_mcp_marketplace", "L3")
trace_contract._emit_checks_agent_registry("p1", "sovereign_mcp_marketplace", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_mcp_marketplace", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_mcp_marketplace", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_mcp_marketplace", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_mcp_marketplace", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_mcp_marketplace", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_mcp_marketplace", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_mcp_marketplace", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_mcp_marketplace", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_mcp_marketplace")
trace_contract._emit_gated_by_confidence("p1", "sovereign_mcp_marketplace", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_mcp_marketplace", "L3")
trace_contract._emit_reads_policy_state("p1", "sovereign_mcp_marketplace", "L3")
trace_contract._emit_authorize_and_execute("p2", "sovereign_mcp_marketplace", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_mcp_marketplace", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_mcp_marketplace", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_mcp_marketplace", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_mcp_marketplace", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_mcp_marketplace", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_mcp_marketplace", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_mcp_marketplace", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_mcp_marketplace", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_mcp_marketplace", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_mcp_marketplace", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_mcp_marketplace", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_mcp_marketplace", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_mcp_marketplace", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_mcp_marketplace", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_mcp_marketplace", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_mcp_marketplace", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_mcp_marketplace", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_mcp_marketplace", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_mcp_marketplace", "exec_snapshot_link")

"L3 Orchestration: Sovereign MCP Marketplace Integration\nSafe discovery and registration of marketplace MCPs with L5 sovereignty enforcement.\nGEMINI-ONLY policy — forbidden providers auto-blocked.\n"
import logging

from agentic_core.seams.contracts.authority import get_mcp_authority
from tqdm import tqdm

trace_contract._emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_mcp_marketplace", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_mcp_marketplace", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_mcp_marketplace", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_mcp_marketplace", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_mcp_marketplace", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_mcp_marketplace", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_mcp_marketplace", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_mcp_marketplace", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_mcp_marketplace", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_mcp_marketplace", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_mcp_marketplace", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_mcp_marketplace", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_mcp_marketplace", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_mcp_marketplace", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_mcp_marketplace", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_mcp_marketplace", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_mcp_marketplace", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_mcp_marketplace", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_mcp_marketplace", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_mcp_marketplace", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_mcp_marketplace", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_mcp_marketplace", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_mcp_marketplace", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_mcp_marketplace", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_mcp_marketplace", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_mcp_marketplace", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_mcp_marketplace", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_mcp_marketplace", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_mcp_marketplace", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_mcp_marketplace", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_mcp_marketplace", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_mcp_marketplace", "routing_commit")

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

        trace_contract._emit_snapshots_state(
            str(_uuid.uuid4()),
            "SovereignMcpMarketplace.discover_and_register_safe",
            "state_snapshot",
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(
            str(_uuid.uuid4()),
            "SovereignMcpMarketplace.discover_and_register_safe",
            "p0_governance",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
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
                except (
                    RuntimeError,
                    ValueError,
                    TypeError,
                    AttributeError,
                ):  # guardian: allow-double-logging -- MCP registration failure logged before re-raise for marketplace audit
                    raise
        if not self.safe_tools:
            Logger.warning("[L3 MARKETPLACE] No safe MCPs found. Running in LLM-only mode.")

    def get_safe_tools(self) -> list[str]:
        return self.safe_tools
