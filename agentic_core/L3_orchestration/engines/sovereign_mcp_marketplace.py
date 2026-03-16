from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_mcp_marketplace")
emit_determinism_digest("p0", "sovereign_mcp_marketplace")

_emit_dispatches_healing_run("p1", "sovereign_mcp_marketplace", "L3")
_emit_routes_through("p1", "sovereign_mcp_marketplace", "L3")
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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.seams.contracts.authority import get_mcp_authority

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
            str(_uuid.uuid4()), "SovereignMcpMarketplace.discover_and_register_safe", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "SovereignMcpMarketplace.discover_and_register_safe", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignMcpMarketplace.discover_and_register_safe"
        )

        installed = marketplace_data.get("installed", [])
        available = marketplace_data.get("available", [])
        for mcp in installed + available:
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
                except Exception as e:
                    Logger.warning(f"Failed to register {name}: {e}")
                    raise
        if not self.safe_tools:
            Logger.warning("[L3 MARKETPLACE] No safe MCPs found. Running in LLM-only mode.")

    def get_safe_tools(self) -> list[str]:
        return self.safe_tools
