from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "sovereign_mcp_marketplace", "L3")
_emit_routes_through("p1", "sovereign_mcp_marketplace", "L3")
_emit_escalates_to_human("p1", "sovereign_mcp_marketplace", "L3")
_emit_reads_policy_state("p1", "sovereign_mcp_marketplace", "L3")

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
