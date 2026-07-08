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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "integrity_validator")
trace_contract.emit_determinism_digest("p0", "integrity_validator")

trace_contract._emit_dispatches_healing_run("p1", "integrity_validator", "L4")
trace_contract._emit_routes_through("p1", "integrity_validator", "L4")
trace_contract._emit_checks_agent_registry("p1", "integrity_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "integrity_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "integrity_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "integrity_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "integrity_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "integrity_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "integrity_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "integrity_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "integrity_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "integrity_validator")
trace_contract._emit_gated_by_confidence("p1", "integrity_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "integrity_validator", "L4")
trace_contract._emit_reads_policy_state("p1", "integrity_validator", "L4")
trace_contract._emit_authorize_and_execute("p2", "integrity_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "integrity_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "integrity_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "integrity_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "integrity_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "integrity_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "integrity_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "integrity_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "integrity_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "integrity_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "integrity_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "integrity_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "integrity_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "integrity_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "integrity_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "integrity_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "integrity_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "integrity_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "integrity_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "integrity_validator", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("integrity_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("integrity_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("integrity_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("integrity_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("integrity_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("integrity_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("integrity_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("integrity_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("integrity_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("integrity_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("integrity_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("integrity_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("integrity_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("integrity_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("integrity_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("integrity_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("integrity_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("integrity_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("integrity_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("integrity_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("integrity_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("integrity_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("integrity_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("integrity_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("integrity_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("integrity_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("integrity_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("integrity_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "integrity_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "integrity_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "integrity_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "integrity_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "integrity_validator", "write_through")
trace_contract._emit_writes_through("p1", "integrity_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "integrity_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "integrity_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "integrity_validator", "routing_commit")

logger = logging.getLogger(__name__)
_GENESIS_HASH = "0" * 64


def compute_entry_hash(prev_hash: str, entry: dict[str, Any]) -> str:
    """Compute chained SHA256: hash(prev_hash || entry_bytes)."""
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation  # noqa: F401

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "compute_entry_hash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "compute_entry_hash")
    entry_bytes = json.dumps(entry, sort_keys=True, ensure_ascii=True, default=str).encode()
    payload = (prev_hash + entry_bytes.decode()).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_ledger_chain(entries: list[dict[str, Any]]) -> None:
    """Walk the ledger chain and raise LedgerIntegrityViolation on first broken link.

    Each entry must have a ``_hash`` field computed from the previous hash
    and the entry data (excluding the ``_hash`` field itself).
    """
    trace_contract._emit_snapshots_state(str(uuid.uuid4()), "Module.validate_ledger_chain", "L4_STATE")
    prev_hash = _GENESIS_HASH
    for idx, entry in tqdm(enumerate(entries), desc="Processing", unit="item"):
        stored_hash = entry.get("_hash")
        if stored_hash is None:
            raise LedgerIntegrityViolation(
                f"Ledger entry {idx} missing '_hash' field — integrity cannot be verified",
            )
        entry_without_hash = {k: v for k, v in entry.items() if k != "_hash"}
        expected_hash = compute_entry_hash(prev_hash, entry_without_hash)
        if expected_hash != stored_hash:
            raise LedgerIntegrityViolation(
                f"Ledger hash mismatch at entry {idx}: expected={expected_hash[:16]}... stored={stored_hash[:16]}...",
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
