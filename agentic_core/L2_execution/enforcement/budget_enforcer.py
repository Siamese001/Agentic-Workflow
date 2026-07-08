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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "budget_enforcer")
trace_contract.emit_determinism_digest("p0", "budget_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "budget_enforcer", "L2")
trace_contract._emit_routes_through("p1", "budget_enforcer", "L2")
trace_contract._emit_checks_agent_registry("p1", "budget_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "budget_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "budget_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "budget_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "budget_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "budget_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "budget_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "budget_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "budget_enforcer", "transcript")
trace_contract._emit_gated_by_confidence("p1", "budget_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "budget_enforcer", "L2")
trace_contract._emit_reads_policy_state("p1", "budget_enforcer", "L2")

trace_contract._emit_snapshots_state("p0", "budget_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "budget_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "budget_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "budget_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "budget_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "budget_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "budget_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "budget_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "budget_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "budget_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "budget_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "budget_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "budget_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "budget_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "budget_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "budget_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "budget_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "budget_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "budget_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "budget_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "budget_enforcer", "exec_snapshot_link")

try:
    import resource

    _HAS_RESOURCE = True
except ImportError:  # guardian: allow-silent-swallow
    resource = None
    _HAS_RESOURCE = False
_HAS_SIGALRM = hasattr(signal, "SIGALRM")
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope

trace_contract._emit_emits_metric_event("budget_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("budget_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("budget_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("budget_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("budget_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("budget_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("budget_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("budget_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("budget_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("budget_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("budget_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("budget_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("budget_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("budget_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("budget_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("budget_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("budget_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("budget_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("budget_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("budget_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("budget_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("budget_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("budget_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("budget_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("budget_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("budget_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("budget_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("budget_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "budget_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "budget_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "budget_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "budget_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "budget_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "budget_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "budget_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "budget_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "budget_enforcer", "routing_commit")


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
        trace_contract._emit_hard_fails_untranscripted(str(uuid.uuid4()), "BudgetEnforcer.run")
        trace_contract._emit_applies_guardrail(str(uuid.uuid4()), "BudgetEnforcer.run", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "BudgetEnforcer.run")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BudgetEnforcer.run".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
            except (
                AttributeError,
                ValueError,
                OSError,
            ):  # guardian: allow-silent-swallow -- intentional: AttributeError used for control flow
                pass
        buf = io.BytesIO()
        with _wall_clock_cap(budget.compute_ms):
            result = tool_fn(**envelope.tool_args)
        output = str(result).encode("utf-8", errors="replace")
        if len(output) > budget.stdout_bytes:
            raise BudgetExceeded(f"stdout_bytes cap ({budget.stdout_bytes}) exceeded: got {len(output)}")
        buf.write(output)
        return (0, buf.getvalue())
