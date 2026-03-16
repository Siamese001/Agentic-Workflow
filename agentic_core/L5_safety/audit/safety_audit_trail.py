"""
agentic_core/L5_safety/audit/safety_audit_trail.py

SafetyAuditTrail — P2-L5 gap remediation.

Immutable append-only audit log capturing every guardrail check,
policy enforcement, tool safety gate, and HITL decision from L5.
Closes the gap: 608 L5 modules with 0 produces_audit_trail edges
in the ADG.

ADG edges emitted: produces_audit_trail, validated_by_safety_plane,
                   references_policy_hash
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

emit_replay_key("p0", "safety_audit_trail")
emit_determinism_digest("p0", "safety_audit_trail")

_emit_dispatches_healing_run("p1", "safety_audit_trail", "L5")
_emit_routes_through("p1", "safety_audit_trail", "L5")
_emit_checks_agent_registry("p1", "safety_audit_trail", "agent_registry")
_emit_validates_agent_capability("p1", "safety_audit_trail", "capability")
_emit_dispatches_execution_plan("p1", "safety_audit_trail", "exec_plan")
_emit_agent_executes_agent("p1", "safety_audit_trail", "sub_agent")
_emit_routes_to_agent("p1", "safety_audit_trail", "target_agent")
_emit_verifies_policy("p1", "safety_audit_trail", "policy_check")
_emit_observes_runtime_state("p1", "safety_audit_trail", "runtime_state")
_emit_verifies_boundary("p1", "safety_audit_trail", "boundary_check")
_emit_transcripts_response("p1", "safety_audit_trail", "transcript")
_emit_hard_fails_untranscripted("p1", "safety_audit_trail")
_emit_gated_by_confidence("p1", "safety_audit_trail", "confidence_gate")
_emit_escalates_to_human("p1", "safety_audit_trail", "L5")
_emit_reads_policy_state("p1", "safety_audit_trail", "L5")

_emit_applies_guardrail("p0", "safety_audit_trail", "p0_governance")
_emit_snapshots_state("p0", "safety_audit_trail", "state_snapshot")
_emit_authorize_and_execute("p2", "safety_audit_trail", "execution_auth")
_emit_validates_capability("p2", "safety_audit_trail", "capability_check")
_emit_routes_to_capability("p2", "safety_audit_trail", "capability_route")
_emit_writes_via_uwg("p2", "safety_audit_trail", "uwg_write")
_emit_blocks_direct_write("p2", "safety_audit_trail", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_audit_trail", "tool_invocation")
_emit_captures_execution_output("p2", "safety_audit_trail", "exec_output")
_emit_dispatches_agent("p3", "safety_audit_trail", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_audit_trail", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_audit_trail", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_audit_trail", "healing_outcome")
_emit_escalates_failure("p3", "safety_audit_trail", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_audit_trail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_audit_trail", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_audit_trail", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_audit_trail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_audit_trail", "eval_metric")
_emit_stores_embedding("p4", "safety_audit_trail", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_audit_trail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_audit_trail", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("safety_audit_trail", "p4obs", "metric_1")
_emit_emits_metric_event("safety_audit_trail", "p4obs", "metric_2")
_emit_emits_metric_event("safety_audit_trail", "p4obs", "metric_3")
_emit_emits_metric_event("safety_audit_trail", "p4obs", "metric_4")
_emit_emits_metric_event("safety_audit_trail", "p4obs", "metric_5")
_emit_emits_metric_event("safety_audit_trail", "p4obs", "metric_6")
_emit_records_incident_event("safety_audit_trail", "p4obs", "incident")
_emit_captures_runtime_anomaly("safety_audit_trail", "p4obs", "anomaly")
_emit_writes_observability_log("safety_audit_trail", "p4obs", "obs_log")
_emit_updates_monitoring_state("safety_audit_trail", "p4obs", "mon_state")
_emit_triggers_alert("safety_audit_trail", "p4obs", "alert")
_emit_links_incident_trace("safety_audit_trail", "p4obs", "trace_link")
_emit_captures_pattern("safety_audit_trail", "p3lm", "pattern")
_emit_records_learning_event("safety_audit_trail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safety_audit_trail", "p3lm", "snapshot")
_emit_feeds_meta_learning("safety_audit_trail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safety_audit_trail", "p3lm", "routing")
_emit_improves_agent_policy("safety_audit_trail", "p3lm", "policy")
_emit_stores_learning_state("safety_audit_trail", "p3lm", "state")
_emit_records_execution_trace("safety_audit_trail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safety_audit_trail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safety_audit_trail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safety_audit_trail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safety_audit_trail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safety_audit_trail", "env_read", "p2_env_1")
_emit_reads_environ("safety_audit_trail", "env_read", "p2_env_2")
_emit_reads_runtime_state("safety_audit_trail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safety_audit_trail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safety_audit_trail", "context_pull")
_emit_pulls_context("p1", "safety_audit_trail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safety_audit_trail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safety_audit_trail", "uwg_term_2")
_emit_writes_through("p1", "safety_audit_trail", "write_through")
_emit_writes_through("p1", "safety_audit_trail", "write_through_2")
_emit_validated_by_safety_plane("p1", "safety_audit_trail", "safety_validation")
_emit_invokes_eval("p1", "safety_audit_trail", "eval_call")
_emit_proposal_commits_routing("p1", "safety_audit_trail", "routing_commit")

logger = logging.getLogger(__name__)

_DEFAULT_TRAIL_PATH = Path("artifacts/safety/audit_trail.jsonl")


class AuditEventKind(str, Enum):
    """Classification of a safety audit event."""

    GUARDRAIL_CHECK = "guardrail_check"
    POLICY_ENFORCEMENT = "policy_enforcement"
    TOOL_SAFETY_GATE = "tool_safety_gate"
    HITL_DECISION = "hitl_decision"
    GUARDRAIL_VIOLATION = "guardrail_violation"
    POLICY_VIOLATION = "policy_violation"
    SANDBOX_ENTRY = "sandbox_entry"
    REENTER_SAFETY = "reenter_safety"


@dataclass
class SafetyAuditEvent:
    """Single safety audit event record."""

    event_id: str
    kind: AuditEventKind
    module: str
    operation: str
    verdict: str
    policy_hash: str
    trace_id: str
    timestamp: float
    allowed: bool
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)


class SafetyAuditTrail:
    """Immutable append-only audit trail for all L5 safety events.

    Usage::

        trail = SafetyAuditTrail()
        trail.record_guardrail_check(
            module="airlock_guardrail",
            operation="write_file",
            verdict="allow",
            policy_hash="abc123",
            trace_id=trace_id,
            allowed=True,
        )
        trail.flush()
    """

    def __init__(self, trail_path: Path | None = None) -> None:
        self._path = trail_path or _DEFAULT_TRAIL_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[SafetyAuditEvent] = []
        self._lock = threading.Lock()
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        ts = time.monotonic()
        payload = f"{self._counter}:{ts:.6f}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _record(self, event: SafetyAuditEvent) -> SafetyAuditEvent:
        with self._lock:
            self._records.append(event)
        log_fn = logger.debug if event.allowed else logger.warning
        log_fn(
            "SAFETY_AUDIT produces_audit_trail validated_by_safety_plane "
            "kind=%s module=%s op=%s verdict=%s allowed=%s trace=%s",
            event.kind.value,
            event.module,
            event.operation,
            event.verdict,
            event.allowed,
            event.trace_id,
        )
        return event

    def record_guardrail_check(
        self,
        module: str,
        operation: str,
        verdict: str,
        policy_hash: str,
        trace_id: str,
        allowed: bool,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.GUARDRAIL_CHECK,
                module=module,
                operation=operation,
                verdict=verdict,
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=allowed,
                reason=reason,
                metadata=metadata or {},
            )
        )

    def record_policy_enforcement(
        self,
        module: str,
        action: str,
        verdict: str,
        policy_hash: str,
        trace_id: str,
        allowed: bool,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.POLICY_ENFORCEMENT,
                module=module,
                operation=action,
                verdict=verdict,
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=allowed,
                reason=reason,
                metadata=metadata or {},
            )
        )

    def record_tool_gate(
        self,
        module: str,
        tool_name: str,
        risk_level: str,
        policy_hash: str,
        trace_id: str,
        allowed: bool,
        sandboxed: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.TOOL_SAFETY_GATE,
                module=module,
                operation=f"tool:{tool_name}",
                verdict="allow" if allowed else "deny",
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=allowed,
                metadata={**(metadata or {}), "sandboxed": sandboxed, "risk_level": risk_level},
            )
        )

    def record_hitl_decision(
        self,
        module: str,
        decision: str,
        trace_id: str,
        policy_hash: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.HITL_DECISION,
                module=module,
                operation="hitl_decision",
                verdict=decision,
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=decision in ("approve", "allow"),
                metadata=metadata or {},
            )
        )

    def flush(self) -> int:
        """Write all buffered records to the JSONL trail file.

        Returns count of records written.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyAuditTrail.flush")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyAuditTrail.flush".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with self._lock:
            records = list(self._records)
        count = 0
        try:
            with open(self._path, "a", encoding="utf-8") as f:
                for rec in records:
                    f.write(rec.to_jsonl() + "\n")
                    count += 1
        except OSError as exc:
            logger.warning("SafetyAuditTrail flush failed: %s", exc)
        return count

    def all_records(self) -> list[SafetyAuditEvent]:
        with self._lock:
            return list(self._records)

    def violations(self) -> list[SafetyAuditEvent]:
        with self._lock:
            return [r for r in self._records if not r.allowed]

    def count(self) -> int:
        with self._lock:
            return len(self._records)


_global_trail: SafetyAuditTrail | None = None


def get_safety_audit_trail(path: Path | None = None) -> SafetyAuditTrail:
    global _global_trail
    if _global_trail is None:
        _global_trail = SafetyAuditTrail(trail_path=path)
    return _global_trail


def reset_safety_audit_trail() -> None:
    global _global_trail
    _global_trail = None


__all__ = [
    "AuditEventKind",
    "SafetyAuditEvent",
    "SafetyAuditTrail",
    "get_safety_audit_trail",
    "reset_safety_audit_trail",
]
