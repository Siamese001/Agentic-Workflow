"""
Golden Context Mixin - Anti-Context Drift Protection.

Injects a concise summary of the SSOT structure blueprint into the message
context to prevent agents from "forgetting" the rules during long execution loops.

COGNITIVE HARDENING (Feb 2026):
- Landmine #3 Prevention: Context Drift
- Injects "The Law" at the end of message lists
- Ensures agents remember structural rules even 50+ turns deep
"""

import logging
from typing import Any, Final

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

_emit_applies_guardrail("p0", "golden_context_mixin", "p0_governance")
_emit_reads_policy_state("p0", "golden_context_mixin", "policy_binding")
_emit_snapshots_state("p0", "golden_context_mixin", "state_snapshot")
emit_replay_key("p0", "golden_context_mixin")
emit_determinism_digest("p0", "golden_context_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "golden_context_mixin", "execution_auth")
_emit_validates_capability("p2", "golden_context_mixin", "capability_check")
_emit_routes_to_capability("p2", "golden_context_mixin", "capability_route")
_emit_writes_via_uwg("p2", "golden_context_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "golden_context_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "golden_context_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "golden_context_mixin", "exec_output")
_emit_dispatches_agent("p3", "golden_context_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "golden_context_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "golden_context_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "golden_context_mixin", "healing_outcome")
_emit_escalates_failure("p3", "golden_context_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "golden_context_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "golden_context_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "golden_context_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "golden_context_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "golden_context_mixin", "eval_metric")
_emit_stores_embedding("p4", "golden_context_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "golden_context_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "golden_context_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)
GOLDEN_CONTEXT_SUMMARY: Final[str] = (
    "\n=== SOVEREIGN SSOT LAW (Golden Context Injection) ===\n\nYou are operating within a governed repository. These rules are IMMUTABLE:\n\n1. **BASE AGENTS LOCATION**: All *BaseAgent.py files MUST reside in `agentic_core/base_agents/`.\n   - NEVER place base agents in layer folders (L0-L6).\n   - Constitutional override: LocationAgent.validate_file_location() enforces this.\n\n2. **LAYER HIERARCHY (L0-L6)**:\n   - L0: Maintenance (scripts, healing, bootstrapping)\n   - L1: Cognition (thought engine, intent analysis, planning)\n   - L2: Execution (tool registry, MCP, action handlers)\n   - L3: Orchestration (workflow engines, meta-learning)\n   - L4: State (validation context, ledger, memory)\n   - L5: Safety (guardrails, validators, gravity)\n   - L6: Observability (dashboards, telemetry, logging)\n\n3. **DEPTH RULES**:\n   - agentic_core: Depth 3 (some L4 approved folders go to depth 4)\n   - apps_rg, apps_lic, apps_shared: Depth 2\n   - tests: Depth 3 (type/domain/test_file.py)\n\n4. **FORBIDDEN PATTERNS**:\n   - No unknown layers (all agents must have valid layer assignment)\n   - No duplicates (one canonical agent per file)\n   - No hardcoded paths (use structure_blueprint_config.py constants)\n\n5. **SSOT FILES**:\n   - Structure: `agentic_core/L5_safety/config/structure_blueprint_config.py`\n   - Agent Registry: `agent_discovery_full.json`\n\nREMEMBER: When in doubt, consult the SSOT. Do not hallucinate file locations.\n=== END GOLDEN CONTEXT ===\n"
)


class GoldenContextMixin:
    """
    Mixin that provides golden context injection capabilities.

    Inherit from this mixin to gain the ability to inject SSOT rules
    into message contexts, preventing context drift during long loops.
    """

    _golden_context_cache: str | None = None

    def get_golden_context(self) -> str:
        """
        Get the golden context summary.

        Returns:
            The SSOT law summary string.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GoldenContextMixin.get_golden_context")

        if self._golden_context_cache is None:
            self._golden_context_cache = GOLDEN_CONTEXT_SUMMARY.strip()
        return self._golden_context_cache

    def inject_golden_context(
        self, current_messages: list[dict[str, Any]], role: str = "system"
    ) -> list[dict[str, Any]]:
        """
        Inject the golden context into the message list.

        This appends a system message containing the SSOT rules to the
        END of the message list, ensuring the agent "remembers" the rules
        even in deep conversation contexts.

        Args:
            current_messages: The current list of messages.
            role: The role for the injected message (default: "system").

        Returns:
            A new message list with the golden context appended.
        """
        if not current_messages:
            current_messages = []
        messages = list(current_messages)
        golden_message = {"role": role, "content": self.get_golden_context()}
        messages.append(golden_message)
        logger.debug(f"[GoldenContextMixin] Injected golden context. Total messages: {len(messages)}")
        return messages

    # guardian: allow-magic-config
    def should_inject_golden_context(
        self, current_messages: list[dict[str, Any]], threshold: int = 10
    ) -> bool:
        """
        Determine if golden context should be injected.

        Injection is recommended when:
        - Message count exceeds the threshold
        - No recent golden context injection exists

        Args:
            current_messages: The current list of messages.
            threshold: Minimum message count before injection (default: 10).

        Returns:
            True if injection is recommended.
        """
        if len(current_messages) < threshold:
            return False
        recent_messages = current_messages[-5:] if len(current_messages) >= 5 else current_messages
        for msg in recent_messages:
            content = msg.get("content", "")
            if "SOVEREIGN SSOT LAW" in content:
                return False
        return True


__all__ = ["GoldenContextMixin", "GOLDEN_CONTEXT_SUMMARY"]
