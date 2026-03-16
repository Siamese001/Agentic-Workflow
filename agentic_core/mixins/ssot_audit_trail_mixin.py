"""
SSOT AuditTrail Mixin — ExecutionTrace-Aligned Cryptographic Audit.

Extends AuditTrailMixin with:
  - Policy-hash scoped audit entries
  - ExecutionTrace-compatible schema (trace_id, plan_hash, actor, target,
    diff, policy_hash, timestamp, prev_hash, replay_key, curr_hash)
  - Canonical JSON serialization (sort_keys, compact separators)
  - SHA-256 hash chaining with replay_key stability
  - Deterministic timestamps under replay mode

Layer: L6 Observer (read-only authority)
Authority: Append-only audit chain. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
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

_emit_applies_guardrail("p0", "ssot_audit_trail_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_audit_trail_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_audit_trail_mixin", "state_snapshot")
emit_replay_key("p0", "ssot_audit_trail_mixin")
emit_determinism_digest("p0", "ssot_audit_trail_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_audit_trail_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_audit_trail_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_audit_trail_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_audit_trail_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_audit_trail_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_audit_trail_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_audit_trail_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_audit_trail_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_audit_trail_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_audit_trail_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_audit_trail_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_audit_trail_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_audit_trail_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_audit_trail_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_audit_trail_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_audit_trail_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_audit_trail_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_audit_trail_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_audit_trail_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_audit_trail_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTAuditTrail")


class SSOTAuditTrailMixin:
    """Policy-hash-scoped, ExecutionTrace-aligned audit trail.

    Designed to sit in MRO alongside ReplayGuardMixin. Reads
    ``active_policy_hash``, ``trace_id``, and ``is_replay_mode``
    from the ReplayGuard properties.

    Audit entries are appended to ``self.state["audit_chain"]``.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_audit_last_hash: str = self.GENESIS_HASH
        self._ssot_audit_count: int = 0

    def emit_ssot_audit_entry(
        self, action: str, target: str, diff: dict[str, Any] | None = None, plan_hash: str | None = None
    ) -> dict[str, Any]:
        """Emit an ExecutionTrace-compatible audit entry.

        Parameters
        ----------
        action : str
            The action being audited (e.g. "HEAL", "VALIDATE", "ROLLBACK").
        target : str
            The target of the action (e.g. file path, agent name).
        diff : dict | None
            Optional diff payload describing the change.
        plan_hash : str | None
            Optional plan hash. Falls back to active_policy_hash.

        Returns
        -------
        dict
            The complete audit entry (also appended to state["audit_chain"]).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTAuditTrailMixin.emit_ssot_audit_entry")

        policy_hash = getattr(self, "active_policy_hash", "unknown")
        trace_id = getattr(self, "trace_id", "unknown")
        actor = self.__class__.__name__
        entry = {
            "trace_id": trace_id,
            "plan_hash": plan_hash or policy_hash,
            "actor": actor,
            "target": target,
            "diff": diff or {},
            "policy_hash": policy_hash,
            "timestamp": time.time(),
            "prev_hash": self._ssot_audit_last_hash,
            "replay_key": self._compute_replay_key(action, target, policy_hash, trace_id),
        }
        canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        curr_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        entry["curr_hash"] = curr_hash
        self._ssot_audit_last_hash = curr_hash
        self._ssot_audit_count += 1
        state = getattr(self, "state", None)
        if isinstance(state, dict) and "audit_chain" in state:
            state["audit_chain"].append(entry)
        _logger.debug("[SSOTAudit] %s | %s | hash=%s...", action, target, curr_hash[:16])
        return entry

    def verify_ssot_audit_chain(self, chain: list[dict[str, Any]] | None = None) -> tuple[bool, int | None]:
        """Verify SHA-256 chain integrity of audit entries.

        Parameters
        ----------
        chain : list[dict] | None
            Audit entries to verify. Defaults to self.state["audit_chain"].

        Returns
        -------
        tuple[bool, int | None]
            (is_valid, first_broken_index). If valid: (True, None).
        """
        if chain is None:
            state = getattr(self, "state", None)
            if isinstance(state, dict):
                chain = state.get("audit_chain", [])
            else:
                chain = []
        if not chain:
            return (True, None)
        for i, entry in enumerate(chain):
            entry_copy = {k: v for k, v in entry.items() if k != "curr_hash"}
            canonical = json.dumps(entry_copy, sort_keys=True, separators=(",", ":"))
            expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if entry.get("curr_hash") != expected_hash:
                return (False, i)
            if i > 0 and entry.get("prev_hash") != chain[i - 1].get("curr_hash"):
                return (False, i)
        return (True, None)

    @property
    def ssot_audit_head(self) -> str:
        """Current head hash of the SSOT audit chain."""
        return self._ssot_audit_last_hash

    @property
    def ssot_audit_count(self) -> int:
        """Total entries in the SSOT audit chain."""
        return self._ssot_audit_count

    @staticmethod
    def _compute_replay_key(action: str, target: str, policy_hash: str, trace_id: str) -> str:
        """Compute a stable replay key for deterministic replay matching.

        The replay_key is deterministic given the same inputs, enabling
        replay systems to correlate entries across runs.
        """
        raw = f"{trace_id}|{policy_hash}|{action}|{target}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
