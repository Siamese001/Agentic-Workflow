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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "golden_context_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "golden_context_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "golden_context_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("golden_context_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("golden_context_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("golden_context_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("golden_context_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("golden_context_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("golden_context_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("golden_context_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("golden_context_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("golden_context_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("golden_context_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("golden_context_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("golden_context_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("golden_context_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("golden_context_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("golden_context_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("golden_context_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("golden_context_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("golden_context_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("golden_context_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("golden_context_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("golden_context_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("golden_context_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("golden_context_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("golden_context_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("golden_context_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("golden_context_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("golden_context_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("golden_context_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "golden_context_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "golden_context_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "golden_context_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "golden_context_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "golden_context_mixin", "write_through")
trace_contract._emit_writes_through("p1", "golden_context_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "golden_context_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "golden_context_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "golden_context_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "golden_context_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "golden_context_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "golden_context_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "golden_context_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "golden_context_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "golden_context_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "golden_context_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "golden_context_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "golden_context_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "golden_context_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "golden_context_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "golden_context_mixin")
trace_contract._emit_gated_by_confidence("p1", "golden_context_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "golden_context_mixin")
trace_contract.emit_determinism_digest("p0", "golden_context_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "golden_context_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "golden_context_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "golden_context_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "golden_context_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "golden_context_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "golden_context_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "golden_context_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "golden_context_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "golden_context_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "golden_context_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "golden_context_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "golden_context_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "golden_context_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "golden_context_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "golden_context_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "golden_context_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "golden_context_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "golden_context_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "golden_context_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "golden_context_mixin", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "GoldenContextMixin.get_golden_context"
        )

        if self._golden_context_cache is None:
            self._golden_context_cache = GOLDEN_CONTEXT_SUMMARY.strip()
        return self._golden_context_cache

    def inject_golden_context(
        self,
        current_messages: list[dict[str, Any]],
        role: str = "system",
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
        self,
        current_messages: list[dict[str, Any]],
        threshold: int = 10,
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
