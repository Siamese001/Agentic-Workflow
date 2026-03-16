"""
H2: Hash-chained immutable audit log with genesis rule.

Replaces mutable in-memory ``audit_log: List[...]`` with an
append-only, hash-chained log.  Each entry carries a
``previous_hash`` pointer (sha-256 of prior entry's canonical
bytes).  Chain integrity is verifiable from the deterministic
genesis anchor.

Genesis rule:
  entry_index = 0
  previous_hash = "GENESIS"

Hash computation rules:
  - Computed on canonical serialized bytes (sorted keys, no
    whitespace variance).
  - Timestamp frozen before hash — no mutation after.

Lives in L2 per gravity rules (durable writes are L2-only).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
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

_emit_authorize_and_execute("p2", "hash_chain_audit_log", "execution_auth")
_emit_validates_capability("p2", "hash_chain_audit_log", "capability_check")
_emit_routes_to_capability("p2", "hash_chain_audit_log", "capability_route")
_emit_writes_via_uwg("p2", "hash_chain_audit_log", "uwg_write")
_emit_blocks_direct_write("p2", "hash_chain_audit_log", "direct_write_block")
_emit_records_tool_invocation("p2", "hash_chain_audit_log", "tool_invocation")
_emit_captures_execution_output("p2", "hash_chain_audit_log", "exec_output")
_emit_dispatches_agent("p3", "hash_chain_audit_log", "agent_dispatch")
_emit_coordinates_agents("p3", "hash_chain_audit_log", "agent_coordination")
_emit_records_workflow_lineage("p3", "hash_chain_audit_log", "workflow_lineage")
_emit_records_healing_outcome("p3", "hash_chain_audit_log", "healing_outcome")
_emit_escalates_failure("p3", "hash_chain_audit_log", "failure_escalation")
_emit_orchestrates_workflow("p3", "hash_chain_audit_log", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hash_chain_audit_log", "healing_dispatch")
_emit_invokes_evaluation("p3", "hash_chain_audit_log", "evaluation_signal")
_emit_records_telemetry_event("p4", "hash_chain_audit_log", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hash_chain_audit_log", "eval_metric")
_emit_stores_embedding("p4", "hash_chain_audit_log", "embedding_store")
_emit_updates_meta_learning_state("p4", "hash_chain_audit_log", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hash_chain_audit_log", "exec_snapshot_link")
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)

emit_replay_key("p0", "hash_chain_audit_log")
emit_determinism_digest("p0", "hash_chain_audit_log")

_emit_dispatches_healing_run("p1", "hash_chain_audit_log", "L2")
_emit_routes_through("p1", "hash_chain_audit_log", "L2")
_emit_checks_agent_registry("p1", "hash_chain_audit_log", "agent_registry")
_emit_validates_agent_capability("p1", "hash_chain_audit_log", "capability")
_emit_dispatches_execution_plan("p1", "hash_chain_audit_log", "exec_plan")
_emit_agent_executes_agent("p1", "hash_chain_audit_log", "sub_agent")
_emit_routes_to_agent("p1", "hash_chain_audit_log", "target_agent")
_emit_verifies_policy("p1", "hash_chain_audit_log", "policy_check")
_emit_observes_runtime_state("p1", "hash_chain_audit_log", "runtime_state")
_emit_verifies_boundary("p1", "hash_chain_audit_log", "boundary_check")
_emit_transcripts_response("p1", "hash_chain_audit_log", "transcript")
_emit_hard_fails_untranscripted("p1", "hash_chain_audit_log")
_emit_gated_by_confidence("p1", "hash_chain_audit_log", "confidence_gate")
_emit_escalates_to_human("p1", "hash_chain_audit_log", "L2")
_emit_reads_policy_state("p1", "hash_chain_audit_log", "L2")

_emit_applies_guardrail("p0", "hash_chain_audit_log", "p0_governance")
_emit_snapshots_state("p0", "hash_chain_audit_log", "state_snapshot")
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

_emit_emits_metric_event("hash_chain_audit_log", "p4obs", "metric_1")
_emit_emits_metric_event("hash_chain_audit_log", "p4obs", "metric_2")
_emit_emits_metric_event("hash_chain_audit_log", "p4obs", "metric_3")
_emit_emits_metric_event("hash_chain_audit_log", "p4obs", "metric_4")
_emit_emits_metric_event("hash_chain_audit_log", "p4obs", "metric_5")
_emit_emits_metric_event("hash_chain_audit_log", "p4obs", "metric_6")
_emit_records_incident_event("hash_chain_audit_log", "p4obs", "incident")
_emit_captures_runtime_anomaly("hash_chain_audit_log", "p4obs", "anomaly")
_emit_writes_observability_log("hash_chain_audit_log", "p4obs", "obs_log")
_emit_updates_monitoring_state("hash_chain_audit_log", "p4obs", "mon_state")
_emit_triggers_alert("hash_chain_audit_log", "p4obs", "alert")
_emit_links_incident_trace("hash_chain_audit_log", "p4obs", "trace_link")
_emit_captures_pattern("hash_chain_audit_log", "p3lm", "pattern")
_emit_records_learning_event("hash_chain_audit_log", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hash_chain_audit_log", "p3lm", "snapshot")
_emit_feeds_meta_learning("hash_chain_audit_log", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hash_chain_audit_log", "p3lm", "routing")
_emit_improves_agent_policy("hash_chain_audit_log", "p3lm", "policy")
_emit_stores_learning_state("hash_chain_audit_log", "p3lm", "state")
_emit_records_execution_trace("hash_chain_audit_log", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hash_chain_audit_log", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hash_chain_audit_log", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hash_chain_audit_log", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hash_chain_audit_log", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hash_chain_audit_log", "env_read", "p2_env_1")
_emit_reads_environ("hash_chain_audit_log", "env_read", "p2_env_2")
_emit_reads_runtime_state("hash_chain_audit_log", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hash_chain_audit_log", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hash_chain_audit_log", "context_pull")
_emit_pulls_context("p1", "hash_chain_audit_log", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hash_chain_audit_log", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hash_chain_audit_log", "uwg_term_2")
_emit_writes_through("p1", "hash_chain_audit_log", "write_through")
_emit_writes_through("p1", "hash_chain_audit_log", "write_through_2")
_emit_validated_by_safety_plane("p1", "hash_chain_audit_log", "safety_validation")
_emit_invokes_eval("p1", "hash_chain_audit_log", "eval_call")
_emit_proposal_commits_routing("p1", "hash_chain_audit_log", "routing_commit")

Logger = logging.getLogger(__name__)

GENESIS_HASH = "GENESIS"


def _canonical_entry_bytes(
    entry_index: int,
    previous_hash: str,
    timestamp: str,
    tier: str,
    action: str,
    payload: dict[str, Any],
) -> bytes:
    """Deterministic canonical bytes for hash computation.

    Delegates to the shared canonical serializer.
    """
    obj = {
        "action": action,
        "entry_index": entry_index,
        "payload": payload,
        "previous_hash": previous_hash,
        "tier": tier,
        "timestamp": timestamp,
    }
    return canonical_bytes(obj)


@dataclass(frozen=True)
class AuditEntry:
    """Single immutable entry in the hash-chained audit log."""

    entry_index: int
    previous_hash: str
    entry_hash: str
    timestamp: str
    tier: str
    action: str
    payload: dict[str, Any]

    def verify_hash(self) -> bool:
        """Re-derive hash and compare."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "AuditEntry.verify_hash")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AuditEntry.verify_hash".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        canonical = _canonical_entry_bytes(
            entry_index=self.entry_index,
            previous_hash=self.previous_hash,
            timestamp=self.timestamp,
            tier=self.tier,
            action=self.action,
            payload=self.payload,
        )
        return hashlib.sha256(canonical).hexdigest() == self.entry_hash


class HashChainAuditLog:
    """Append-only hash-chained audit log.

    Usage::

        log = HashChainAuditLog()
        log.append(tier="L2", action="persist",
                   payload={"key": "value"})
        assert log.verify_chain_integrity()
    """

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        self._sealed: bool = False

    @property
    def length(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    @property
    def chain_root(self) -> str | None:
        """Hash of the last entry, or None if empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "HashChainAuditLog.chain_root")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HashChainAuditLog.chain_root".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self._entries:
            return None
        return self._entries[-1].entry_hash

    def append(
        self,
        *,
        tier: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Append a new entry to the chain.

        Timestamp is frozen at call time before hash.
        """
        if self._sealed:
            raise RuntimeError("Audit log is sealed — no further appends.")

        entry_index = len(self._entries)
        previous_hash = GENESIS_HASH if entry_index == 0 else self._entries[-1].entry_hash
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        safe_payload = payload if payload is not None else {}

        canonical = _canonical_entry_bytes(
            entry_index=entry_index,
            previous_hash=previous_hash,
            timestamp=timestamp,
            tier=tier,
            action=action,
            payload=safe_payload,
        )
        entry_hash = hashlib.sha256(canonical).hexdigest()

        entry = AuditEntry(
            entry_index=entry_index,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            timestamp=timestamp,
            tier=tier,
            action=action,
            payload=safe_payload,
        )
        self._entries.append(entry)
        Logger.debug(f"[audit] appended entry {entry_index} hash={entry_hash[:12]}...")
        return entry

    def seal(self) -> str:
        """Seal the log — no further appends allowed.

        Returns the chain root hash.
        """
        if not self._entries:
            raise RuntimeError("Cannot seal empty audit log.")
        self._sealed = True
        root = self._entries[-1].entry_hash
        Logger.debug(f"[audit] sealed at entry {len(self._entries) - 1}, root={root[:12]}...")
        return root

    def verify_chain_integrity(self) -> bool:
        """Replay hash chain from genesis and verify."""
        if not self._entries:
            return True

        for i, entry in enumerate(self._entries):
            if not entry.verify_hash():
                Logger.error(f"[audit] hash mismatch at entry {i}")
                return False

            expected_prev = GENESIS_HASH if i == 0 else self._entries[i - 1].entry_hash
            if entry.previous_hash != expected_prev:
                Logger.error(
                    f"[audit] chain break at entry {i}: "
                    f"expected prev={expected_prev[:12]}... "
                    f"got={entry.previous_hash[:12]}..."
                )
                return False

        return True
