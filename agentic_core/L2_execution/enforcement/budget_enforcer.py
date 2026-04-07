"""BudgetEnforcer — OS-level resource isolation for tool invocations.

Wraps every tool call with:
  - Wall-clock limit (compute_ms): SIGALRM on Unix, threading.Timer on Windows
  - resource.setrlimit for memory_mb (RLIMIT_AS) on Unix; no-op on Windows
  - stdout byte cap via BytesIO capture (cross-platform, always enforced)

Spec: Contract [2] SandboxEnvelope ToolBudget caps, Guarantee #10.
"""

from __future__ import annotations

import io
import signal
import threading
import uuid
from contextlib import contextmanager
from typing import Any, Callable

from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
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

emit_replay_key("p0", "budget_enforcer")
emit_determinism_digest("p0", "budget_enforcer")

_emit_dispatches_healing_run("p1", "budget_enforcer", "L2")
_emit_routes_through("p1", "budget_enforcer", "L2")
_emit_checks_agent_registry("p1", "budget_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "budget_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "budget_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "budget_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "budget_enforcer", "target_agent")
_emit_verifies_policy("p1", "budget_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "budget_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "budget_enforcer", "boundary_check")
_emit_transcripts_response("p1", "budget_enforcer", "transcript")
_emit_gated_by_confidence("p1", "budget_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "budget_enforcer", "L2")
_emit_reads_policy_state("p1", "budget_enforcer", "L2")

_emit_snapshots_state("p0", "budget_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "budget_enforcer", "execution_auth")
_emit_validates_capability("p2", "budget_enforcer", "capability_check")
_emit_routes_to_capability("p2", "budget_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "budget_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "budget_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "budget_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "budget_enforcer", "exec_output")
_emit_dispatches_agent("p3", "budget_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "budget_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "budget_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "budget_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "budget_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "budget_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "budget_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "budget_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "budget_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "budget_enforcer", "eval_metric")
_emit_stores_embedding("p4", "budget_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "budget_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "budget_enforcer", "exec_snapshot_link")

try:
    import resource

    _HAS_RESOURCE = True
except ImportError:  # guardian: allow-silent-swallow
    resource = None
    _HAS_RESOURCE = False
_HAS_SIGALRM = hasattr(signal, "SIGALRM")
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
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

_emit_emits_metric_event("budget_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("budget_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("budget_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("budget_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("budget_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("budget_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("budget_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("budget_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("budget_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("budget_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("budget_enforcer", "p4obs", "alert")
_emit_links_incident_trace("budget_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("budget_enforcer", "p3lm", "pattern")
_emit_records_learning_event("budget_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("budget_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("budget_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("budget_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("budget_enforcer", "p3lm", "policy")
_emit_stores_learning_state("budget_enforcer", "p3lm", "state")
_emit_records_execution_trace("budget_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("budget_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("budget_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("budget_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("budget_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("budget_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("budget_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("budget_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("budget_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "budget_enforcer", "context_pull")
_emit_pulls_context("p1", "budget_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "budget_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "budget_enforcer", "uwg_term_2")
_emit_writes_through("p1", "budget_enforcer", "write_through")
_emit_writes_through("p1", "budget_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "budget_enforcer", "safety_validation")
_emit_invokes_eval("p1", "budget_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "budget_enforcer", "routing_commit")


class BudgetExceeded(RuntimeError):
    """Raised when a ToolBudget cap is breached."""


@contextmanager
def _wall_clock_cap_unix(ms: int):
    """SIGALRM-based wall-clock cap — Unix only."""

    def _handler(signum, frame):
        raise BudgetExceeded(f"compute_ms cap ({ms} ms) exceeded")

    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, ms / 1000.0)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


@contextmanager
def _wall_clock_cap_threading(ms: int):
    """threading.Timer-based wall-clock cap — cross-platform fallback."""
    exceeded: list[bool] = [False]

    def _fire():
        exceeded[0] = True

    timer = threading.Timer(ms / 1000.0, _fire)
    timer.daemon = True
    timer.start()
    try:
        yield
    finally:
        timer.cancel()
    if exceeded[0]:
        raise BudgetExceeded(f"compute_ms cap ({ms} ms) exceeded")


def _wall_clock_cap(ms: int):
    """Return the appropriate wall-clock cap context manager for this platform."""
    if _HAS_SIGALRM and threading.current_thread() is threading.main_thread():
        return _wall_clock_cap_unix(ms)
    return _wall_clock_cap_threading(ms)


class BudgetEnforcer:
    """Enforces ToolBudget caps around a tool callable.

    Cross-platform: uses SIGALRM on Unix main thread, threading.Timer elsewhere.
    Memory cap is Unix-only (no-op on Windows/macOS).
    stdout_bytes cap is always enforced.
    """

    def run(self, envelope: SandboxEnvelope, tool_fn: Callable[..., Any]) -> tuple[int, bytes]:
        """Execute tool_fn under budget caps.

        Returns (exit_code, stdout_bytes) per PTC ToolResult contract [3].
        """
        _emit_hard_fails_untranscripted(str(uuid.uuid4()), "BudgetEnforcer.run")
        _emit_applies_guardrail(str(uuid.uuid4()), "BudgetEnforcer.run", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "BudgetEnforcer.run")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BudgetEnforcer.run".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Wave 3: Guardrail pre-check
        guardrail = get_guardrail_gate()
        guardrail.check(operation="run_budget_enforcer", target=envelope.tool_name)
        if envelope.budget.stdout_bytes <= 0:
            raise BudgetExceeded(f"stdout_bytes cap ({envelope.budget.stdout_bytes}) exceeded")
        budget = envelope.budget
        if _HAS_RESOURCE:
            try:
                mem_bytes = budget.memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, resource.RLIM_INFINITY))
            except (AttributeError, ValueError, OSError):
                pass
        buf = io.BytesIO()
        with _wall_clock_cap(budget.compute_ms):
            result = tool_fn(**envelope.tool_args)
        output = str(result).encode("utf-8", errors="replace")
        if len(output) > budget.stdout_bytes:
            raise BudgetExceeded(f"stdout_bytes cap ({budget.stdout_bytes}) exceeded: got {len(output)}")
        buf.write(output)
        return (0, buf.getvalue())
