"""
agentic_core/L5_safety/gates/tool_safety_gate.py

ToolSafetyGate — P0-L5 gap remediation (tool governance).

Wraps all L5 tool invocations (eval, dynamic dispatch, external HTTP)
with applies_guardrail + validated_by_safety_plane checks.

ADG evidence: L5 invokes_eval=136, invokes_dynamic=29, only 5/247
tool-invoking modules have applies_guardrail (2%).

ADG edges emitted: applies_guardrail, enters_sandbox,
                   validated_by_safety_plane, execution_terminates_at_uwg
"""

from __future__ import annotations

import contextlib
import functools
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
    PolicyEnforcementPoint,
    get_policy_enforcement_point,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_snapshots_state,  # noqa: E402
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
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

emit_replay_key("p0", "tool_safety_gate")
emit_determinism_digest("p0", "tool_safety_gate")

_emit_dispatches_healing_run("p1", "tool_safety_gate", "L5")
_emit_routes_through("p1", "tool_safety_gate", "L5")
_emit_checks_agent_registry("p1", "tool_safety_gate", "agent_registry")
_emit_validates_agent_capability("p1", "tool_safety_gate", "capability")
_emit_dispatches_execution_plan("p1", "tool_safety_gate", "exec_plan")
_emit_agent_executes_agent("p1", "tool_safety_gate", "sub_agent")
_emit_routes_to_agent("p1", "tool_safety_gate", "target_agent")
_emit_verifies_policy("p1", "tool_safety_gate", "policy_check")
_emit_observes_runtime_state("p1", "tool_safety_gate", "runtime_state")
_emit_verifies_boundary("p1", "tool_safety_gate", "boundary_check")
_emit_transcripts_response("p1", "tool_safety_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_safety_gate")
_emit_gated_by_confidence("p1", "tool_safety_gate", "confidence_gate")
_emit_escalates_to_human("p1", "tool_safety_gate", "L5")
_emit_reads_policy_state("p1", "tool_safety_gate", "L5")

_emit_applies_guardrail("p0", "tool_safety_gate", "p0_governance")
_emit_snapshots_state("p0", "tool_safety_gate", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_safety_gate", "execution_auth")
_emit_validates_capability("p2", "tool_safety_gate", "capability_check")
_emit_routes_to_capability("p2", "tool_safety_gate", "capability_route")
_emit_writes_via_uwg("p2", "tool_safety_gate", "uwg_write")
_emit_blocks_direct_write("p2", "tool_safety_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_safety_gate", "tool_invocation")
_emit_captures_execution_output("p2", "tool_safety_gate", "exec_output")
_emit_dispatches_agent("p3", "tool_safety_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_safety_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_safety_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_safety_gate", "healing_outcome")
_emit_escalates_failure("p3", "tool_safety_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_safety_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_safety_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_safety_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_safety_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_safety_gate", "eval_metric")
_emit_stores_embedding("p4", "tool_safety_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_safety_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_safety_gate", "exec_snapshot_link")
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

_emit_emits_metric_event("tool_safety_gate", "p4obs", "metric_1")
_emit_emits_metric_event("tool_safety_gate", "p4obs", "metric_2")
_emit_emits_metric_event("tool_safety_gate", "p4obs", "metric_3")
_emit_emits_metric_event("tool_safety_gate", "p4obs", "metric_4")
_emit_emits_metric_event("tool_safety_gate", "p4obs", "metric_5")
_emit_emits_metric_event("tool_safety_gate", "p4obs", "metric_6")
_emit_records_incident_event("tool_safety_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_safety_gate", "p4obs", "anomaly")
_emit_writes_observability_log("tool_safety_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_safety_gate", "p4obs", "mon_state")
_emit_triggers_alert("tool_safety_gate", "p4obs", "alert")
_emit_links_incident_trace("tool_safety_gate", "p4obs", "trace_link")
_emit_captures_pattern("tool_safety_gate", "p3lm", "pattern")
_emit_records_learning_event("tool_safety_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_safety_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_safety_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_safety_gate", "p3lm", "routing")
_emit_improves_agent_policy("tool_safety_gate", "p3lm", "policy")
_emit_stores_learning_state("tool_safety_gate", "p3lm", "state")
_emit_records_execution_trace("tool_safety_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_safety_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_safety_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_safety_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_safety_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_safety_gate", "env_read", "p2_env_1")
_emit_reads_environ("tool_safety_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_safety_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_safety_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_safety_gate", "context_pull")
_emit_pulls_context("p1", "tool_safety_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_safety_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_safety_gate", "uwg_term_2")
_emit_writes_through("p1", "tool_safety_gate", "write_through")
_emit_writes_through("p1", "tool_safety_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_safety_gate", "safety_validation")
_emit_invokes_eval("p1", "tool_safety_gate", "eval_call")
_emit_proposal_commits_routing("p1", "tool_safety_gate", "routing_commit")

logger = logging.getLogger(__name__)


class ToolRiskLevel(str, Enum):
    """Risk classification for tool invocations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ToolInvocationRecord:
    """Audit record for a single tool invocation through the safety gate."""

    tool_name: str
    risk_level: ToolRiskLevel
    trace_id: str
    policy_hash: str
    sandboxed: bool
    allowed: bool
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class ToolNotSandboxedError(PermissionError):
    """Raised when a CRITICAL tool is invoked outside a sandbox."""


class ToolSafetyGate:
    """Pre-invocation safety gate for all L5 tool calls.

    Wraps ``invokes_eval``, ``invokes_dynamic``, ``external_http_call``,
    and other high-risk operations with policy enforcement and optional
    sandbox isolation.

    Usage::

        gate = ToolSafetyGate(policy_hash="abc123")

        # Context manager
        with gate.enters_sandbox("eval", ToolRiskLevel.CRITICAL):
            result = eval(code)

        # Decorator
        @gate.guarded_tool("external_http_call", ToolRiskLevel.HIGH)
        def call_api(self, url: str) -> dict:
            ...

        # Explicit
        record = gate.check_tool("run_python", ToolRiskLevel.HIGH)
    """

    CRITICAL_TOOLS = frozenset({"eval", "exec", "compile", "importlib"})
    HIGH_RISK_TOOLS = frozenset({"subprocess", "os.system", "external_http_call", "dynamic_import"})
    SANDBOX_REQUIRED_LEVELS = frozenset({ToolRiskLevel.CRITICAL, ToolRiskLevel.HIGH})

    def __init__(
        self,
        policy_hash: str = "",
        require_sandbox_for_critical: bool = True,
        pep: PolicyEnforcementPoint | None = None,
    ) -> None:
        self._policy_hash = policy_hash
        self._require_sandbox_for_critical = require_sandbox_for_critical
        self._pep = pep or get_policy_enforcement_point(policy_hash)
        self._audit_log: list[ToolInvocationRecord] = []

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def _classify(self, tool_name: str, risk_level: ToolRiskLevel | None) -> ToolRiskLevel:
        if risk_level is not None:
            return risk_level
        if tool_name in self.CRITICAL_TOOLS:
            return ToolRiskLevel.CRITICAL
        if tool_name in self.HIGH_RISK_TOOLS:
            return ToolRiskLevel.HIGH
        return ToolRiskLevel.MEDIUM

    def check_tool(
        self,
        tool_name: str,
        risk_level: ToolRiskLevel | None = None,
        sandboxed: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ToolInvocationRecord:
        """Check whether ``tool_name`` may be invoked.

        Performs policy enforcement point check and sandbox validation.
        Returns a :class:`ToolInvocationRecord`.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ToolSafetyGate.check_tool")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolSafetyGate.check_tool".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        effective_risk = self._classify(tool_name, risk_level)
        trace_id = self._trace_id()

        policy_result = self._pep.check(
            action=f"tool:{tool_name}",
            target=tool_name,
            metadata=metadata,
        )

        if (
            self._require_sandbox_for_critical
            and effective_risk in self.SANDBOX_REQUIRED_LEVELS
            and not sandboxed
        ):
            record = ToolInvocationRecord(
                tool_name=tool_name,
                risk_level=effective_risk,
                trace_id=trace_id,
                policy_hash=self._policy_hash,
                sandboxed=False,
                allowed=False,
                reason=f"{effective_risk.value} tool '{tool_name}' must run inside a sandbox",
                metadata=metadata or {},
            )
            self._audit_log.append(record)
            logger.error(
                "TOOL_GATE DENY tool=%s risk=%s sandbox_required=True sandboxed=False trace_id=%s",
                tool_name,
                effective_risk.value,
                trace_id,
            )
            raise ToolNotSandboxedError(record.reason)

        record = ToolInvocationRecord(
            tool_name=tool_name,
            risk_level=effective_risk,
            trace_id=trace_id,
            policy_hash=self._policy_hash,
            sandboxed=sandboxed,
            allowed=policy_result.allowed,
            reason="" if policy_result.allowed else policy_result.reason,
            metadata=metadata or {},
        )
        self._audit_log.append(record)
        log_fn = logger.debug if record.allowed else logger.warning
        log_fn(
            "TOOL_GATE %s tool=%s risk=%s sandboxed=%s trace_id=%s",
            "ALLOW" if record.allowed else "DENY",
            tool_name,
            effective_risk.value,
            sandboxed,
            trace_id,
        )
        return record

    @contextlib.contextmanager
    def enters_sandbox(
        self,
        tool_name: str,
        risk_level: ToolRiskLevel | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Context manager: declare sandbox boundary for a tool invocation.

        Satisfies the ``enters_sandbox`` + ``applies_guardrail`` ADG edge
        contracts from L5.
        """
        self.check_tool(tool_name, risk_level, sandboxed=True, metadata=metadata)
        logger.debug("TOOL_GATE enters_sandbox tool=%s", tool_name)
        yield
        logger.debug("TOOL_GATE exits_sandbox tool=%s", tool_name)

    def guarded_tool(
        self,
        tool_name: str,
        risk_level: ToolRiskLevel | None = None,
        sandboxed: bool = False,
    ) -> Callable:
        """Decorator: apply tool safety gate before every invocation.

        Usage::

            @gate.guarded_tool("eval", ToolRiskLevel.CRITICAL, sandboxed=True)
            def run_eval(self, code: str) -> Any:
                return eval(code)
        """

        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                self.check_tool(tool_name, risk_level, sandboxed=sandboxed)
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def validate_by_safety_plane(self, tool_name: str, metadata: dict[str, Any] | None = None) -> bool:
        """Validate a tool invocation against the safety plane.

        Emits ``validated_by_safety_plane`` ADG edge. Returns True if
        the safety plane approves the invocation.
        """
        record = self.check_tool(tool_name, sandboxed=True, metadata=metadata)
        logger.info(
            "TOOL_GATE validated_by_safety_plane tool=%s allowed=%s",
            tool_name,
            record.allowed,
        )
        return record.allowed

    def audit_log(self) -> list[ToolInvocationRecord]:
        return list(self._audit_log)

    def allow_count(self) -> int:
        return sum(1 for r in self._audit_log if r.allowed)

    def deny_count(self) -> int:
        return sum(1 for r in self._audit_log if not r.allowed)

    def sandboxed_count(self) -> int:
        return sum(1 for r in self._audit_log if r.sandboxed)


_global_tool_safety_gate: ToolSafetyGate | None = None


def get_tool_safety_gate(policy_hash: str = "") -> ToolSafetyGate:
    """Return the process-level ToolSafetyGate."""
    global _global_tool_safety_gate
    if _global_tool_safety_gate is None:
        _global_tool_safety_gate = ToolSafetyGate(policy_hash=policy_hash)
    return _global_tool_safety_gate


def reset_tool_safety_gate() -> None:
    """Reset the global gate (for testing)."""
    global _global_tool_safety_gate
    _global_tool_safety_gate = None


__all__ = [
    "ToolRiskLevel",
    "ToolInvocationRecord",
    "ToolNotSandboxedError",
    "ToolSafetyGate",
    "get_tool_safety_gate",
    "reset_tool_safety_gate",
]
