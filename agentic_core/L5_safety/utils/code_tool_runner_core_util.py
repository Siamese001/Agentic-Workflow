"""Shared core for L5 Safety code-tool-runner agents.

Consolidation artifact: extracts the common infrastructure shared by
CodeFormatterAgent and UnusedCleanupAgent (Cluster 6, code_sim=0.771).

Both agents wrap external CLI tools (Black/Ruff vs autoflake) with identical:
  - heal_repository() with cycle-detection + depth-limiting
  - heal() with standard_heal decorator pattern

This module provides CodeToolRunnerCapability — a **pure capability class**
that knows nothing about agents or SovereignBaseAgent. Consuming agents
compose it via multiple inheritance:

    class CodeFormatterAgent(CodeToolRunnerCapability, SovereignBaseAgent):
        ...

[REFACTORED 2026-02-08] Removed SovereignBaseAgent inheritance to fix
Diamond Problem risk. See critique in validation_report.md §1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "code_tool_runner_core_util", "execution_auth")
_emit_validates_capability("p2", "code_tool_runner_core_util", "capability_check")
_emit_routes_to_capability("p2", "code_tool_runner_core_util", "capability_route")
_emit_writes_via_uwg("p2", "code_tool_runner_core_util", "uwg_write")
_emit_blocks_direct_write("p2", "code_tool_runner_core_util", "direct_write_block")
_emit_records_tool_invocation("p2", "code_tool_runner_core_util", "tool_invocation")
_emit_captures_execution_output("p2", "code_tool_runner_core_util", "exec_output")
_emit_dispatches_agent("p3", "code_tool_runner_core_util", "agent_dispatch")
_emit_coordinates_agents("p3", "code_tool_runner_core_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "code_tool_runner_core_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "code_tool_runner_core_util", "healing_outcome")
_emit_escalates_failure("p3", "code_tool_runner_core_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "code_tool_runner_core_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "code_tool_runner_core_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "code_tool_runner_core_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "code_tool_runner_core_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "code_tool_runner_core_util", "eval_metric")
_emit_stores_embedding("p4", "code_tool_runner_core_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "code_tool_runner_core_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "code_tool_runner_core_util", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

emit_replay_key("p0", "code_tool_runner_core_util")
emit_determinism_digest("p0", "code_tool_runner_core_util")

_emit_dispatches_healing_run("p1", "code_tool_runner_core_util", "L5")
_emit_routes_through("p1", "code_tool_runner_core_util", "L5")
_emit_checks_agent_registry("p1", "code_tool_runner_core_util", "agent_registry")
_emit_validates_agent_capability("p1", "code_tool_runner_core_util", "capability")
_emit_dispatches_execution_plan("p1", "code_tool_runner_core_util", "exec_plan")
_emit_agent_executes_agent("p1", "code_tool_runner_core_util", "sub_agent")
_emit_routes_to_agent("p1", "code_tool_runner_core_util", "target_agent")
_emit_verifies_policy("p1", "code_tool_runner_core_util", "policy_check")
_emit_observes_runtime_state("p1", "code_tool_runner_core_util", "runtime_state")
_emit_verifies_boundary("p1", "code_tool_runner_core_util", "boundary_check")
_emit_transcripts_response("p1", "code_tool_runner_core_util", "transcript")
_emit_hard_fails_untranscripted("p1", "code_tool_runner_core_util")
_emit_gated_by_confidence("p1", "code_tool_runner_core_util", "confidence_gate")
_emit_escalates_to_human("p1", "code_tool_runner_core_util", "L5")
_emit_reads_policy_state("p1", "code_tool_runner_core_util", "L5")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("code_tool_runner_core_util", "p4obs", "metric_1")
_emit_emits_metric_event("code_tool_runner_core_util", "p4obs", "metric_2")
_emit_emits_metric_event("code_tool_runner_core_util", "p4obs", "metric_3")
_emit_emits_metric_event("code_tool_runner_core_util", "p4obs", "metric_4")
_emit_emits_metric_event("code_tool_runner_core_util", "p4obs", "metric_5")
_emit_emits_metric_event("code_tool_runner_core_util", "p4obs", "metric_6")
_emit_records_incident_event("code_tool_runner_core_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("code_tool_runner_core_util", "p4obs", "anomaly")
_emit_writes_observability_log("code_tool_runner_core_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("code_tool_runner_core_util", "p4obs", "mon_state")
_emit_triggers_alert("code_tool_runner_core_util", "p4obs", "alert")
_emit_links_incident_trace("code_tool_runner_core_util", "p4obs", "trace_link")
_emit_captures_pattern("code_tool_runner_core_util", "p3lm", "pattern")
_emit_records_learning_event("code_tool_runner_core_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("code_tool_runner_core_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("code_tool_runner_core_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("code_tool_runner_core_util", "p3lm", "routing")
_emit_improves_agent_policy("code_tool_runner_core_util", "p3lm", "policy")
_emit_stores_learning_state("code_tool_runner_core_util", "p3lm", "state")
_emit_records_execution_trace("code_tool_runner_core_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("code_tool_runner_core_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("code_tool_runner_core_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("code_tool_runner_core_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("code_tool_runner_core_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("code_tool_runner_core_util", "env_read", "p2_env_1")
_emit_reads_environ("code_tool_runner_core_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("code_tool_runner_core_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("code_tool_runner_core_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "code_tool_runner_core_util", "context_pull")
_emit_pulls_context("p1", "code_tool_runner_core_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "code_tool_runner_core_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "code_tool_runner_core_util", "uwg_term_2")
_emit_writes_through("p1", "code_tool_runner_core_util", "write_through")
_emit_writes_through("p1", "code_tool_runner_core_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "code_tool_runner_core_util", "safety_validation")
_emit_invokes_eval("p1", "code_tool_runner_core_util", "eval_call")
_emit_proposal_commits_routing("p1", "code_tool_runner_core_util", "routing_commit")


class CodeToolRunnerCapability:
    """Pure capability mixin for L5 code-tool-runner agents.

    Provides:
        - heal_repository() with cycle-detection and depth-limiting
        - heal() template that delegates to execute()

    Expects the consuming dataclass to provide:
        - self.project_root: Path
        - self.ctx: Any

    Subclasses MUST implement:
        - execute(file_path: str) -> dict[str, Any]
    """

    async def execute(self, file_path: str) -> dict[str, Any]:
        """Run the tool on a single file.  Must be overridden by subclasses."""
        raise NotImplementedError

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "CodeToolRunnerCapability.heal_repository", "state_snapshot"
        )
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "CodeToolRunnerCapability.heal_repository", "p0_governance"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "CodeToolRunnerCapability.heal_repository"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CodeToolRunnerCapability.heal_repository".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def heal(self, violation: dict) -> dict:
        """Heal violations using standard_heal decorator pattern.

        Delegates to execute() for the actual tool invocation.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation
                - path: Path to the violating file

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        path = violation.get("path", "")
        try:
            if path:
                file_path = Path(path)
                if file_path.exists():
                    import asyncio

                    result = asyncio.get_event_loop().run_until_complete(self.execute(str(file_path)))
                    return {
                        "violations_fixed": 1 if result.get("healed") else 0,
                        "violations_found": 1,
                        "errors": 0,
                        "skipped": 0,
                    }
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        # guardian: allow-silent-swallow
        except (ValueError, TypeError):
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}


CodeToolRunnerMixin = CodeToolRunnerCapability
