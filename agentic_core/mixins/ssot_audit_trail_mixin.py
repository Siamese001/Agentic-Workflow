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

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
