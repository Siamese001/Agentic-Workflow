"""Addendum 2.2: Ledger Integrity Validator.

Before L4 commit, verify hash chain:
    hash(prev_hash + entry_bytes) == stored_hash

Raises LedgerIntegrityViolation on mismatch.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "integrity_validator")
emit_determinism_digest("p0", "integrity_validator")

_emit_dispatches_healing_run("p1", "integrity_validator", "L4")
_emit_routes_through("p1", "integrity_validator", "L4")
_emit_escalates_to_human("p1", "integrity_validator", "L4")
_emit_reads_policy_state("p1", "integrity_validator", "L4")
_emit_authorize_and_execute("p2", "integrity_validator", "execution_auth")
_emit_validates_capability("p2", "integrity_validator", "capability_check")
_emit_routes_to_capability("p2", "integrity_validator", "capability_route")
_emit_writes_via_uwg("p2", "integrity_validator", "uwg_write")
_emit_blocks_direct_write("p2", "integrity_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "integrity_validator", "tool_invocation")
_emit_captures_execution_output("p2", "integrity_validator", "exec_output")
_emit_dispatches_agent("p3", "integrity_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "integrity_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "integrity_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "integrity_validator", "healing_outcome")
_emit_escalates_failure("p3", "integrity_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "integrity_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "integrity_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "integrity_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "integrity_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "integrity_validator", "eval_metric")
_emit_stores_embedding("p4", "integrity_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "integrity_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "integrity_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_GENESIS_HASH = "0" * 64


def compute_entry_hash(prev_hash: str, entry: dict[str, Any]) -> str:
    """Compute chained SHA256: hash(prev_hash || entry_bytes)."""
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_entry_hash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "compute_entry_hash")
    entry_bytes = json.dumps(entry, sort_keys=True, ensure_ascii=True, default=str).encode()
    payload = (prev_hash + entry_bytes.decode()).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_ledger_chain(entries: list[dict[str, Any]]) -> None:
    """Walk the ledger chain and raise LedgerIntegrityViolation on first broken link.

    Each entry must have a ``_hash`` field computed from the previous hash
    and the entry data (excluding the ``_hash`` field itself).
    """
    _emit_snapshots_state(str(uuid.uuid4()), "Module.validate_ledger_chain", "L4_STATE")
    prev_hash = _GENESIS_HASH
    for idx, entry in enumerate(entries):
        stored_hash = entry.get("_hash")
        if stored_hash is None:
            raise LedgerIntegrityViolation(
                f"Ledger entry {idx} missing '_hash' field — integrity cannot be verified"
            )
        entry_without_hash = {k: v for k, v in entry.items() if k != "_hash"}
        expected_hash = compute_entry_hash(prev_hash, entry_without_hash)
        if expected_hash != stored_hash:
            raise LedgerIntegrityViolation(
                f"Ledger hash mismatch at entry {idx}: expected={expected_hash[:16]}... stored={stored_hash[:16]}..."
            )
        prev_hash = stored_hash


def append_with_hash(entries: list[dict[str, Any]], new_entry: dict[str, Any]) -> dict[str, Any]:
    """Append a new entry to the ledger list, computing its chained hash.

    Returns the entry dict with ``_hash`` set.
    """
    prev_hash = entries[-1]["_hash"] if entries else _GENESIS_HASH
    entry_without_hash = {k: v for k, v in new_entry.items() if k != "_hash"}
    new_hash = compute_entry_hash(prev_hash, entry_without_hash)
    hashed_entry = {**entry_without_hash, "_hash": new_hash}
    entries.append(hashed_entry)
    return hashed_entry


def validate_ledger_file(ledger_path: Path) -> None:
    """Load a JSONL ledger file and validate its hash chain."""
    if not ledger_path.exists():
        return
    entries: list[dict[str, Any]] = []
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    validate_ledger_chain(entries)
    logger.debug("Ledger integrity OK: %d entries in %s", len(entries), ledger_path)


__all__ = ["compute_entry_hash", "validate_ledger_chain", "append_with_hash", "validate_ledger_file"]
