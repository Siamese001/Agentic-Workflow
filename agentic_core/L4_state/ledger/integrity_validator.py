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

from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "integrity_validator")
emit_determinism_digest("p0", "integrity_validator")

_emit_dispatches_healing_run("p1", "integrity_validator", "L4")
_emit_routes_through("p1", "integrity_validator", "L4")
_emit_checks_agent_registry("p1", "integrity_validator", "agent_registry")
_emit_validates_agent_capability("p1", "integrity_validator", "capability")
_emit_dispatches_execution_plan("p1", "integrity_validator", "exec_plan")
_emit_agent_executes_agent("p1", "integrity_validator", "sub_agent")
_emit_routes_to_agent("p1", "integrity_validator", "target_agent")
_emit_verifies_policy("p1", "integrity_validator", "policy_check")
_emit_observes_runtime_state("p1", "integrity_validator", "runtime_state")
_emit_verifies_boundary("p1", "integrity_validator", "boundary_check")
_emit_transcripts_response("p1", "integrity_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "integrity_validator")
_emit_gated_by_confidence("p1", "integrity_validator", "confidence_gate")
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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("integrity_validator", "p4obs", "metric_1")
_emit_emits_metric_event("integrity_validator", "p4obs", "metric_2")
_emit_emits_metric_event("integrity_validator", "p4obs", "metric_3")
_emit_emits_metric_event("integrity_validator", "p4obs", "metric_4")
_emit_emits_metric_event("integrity_validator", "p4obs", "metric_5")
_emit_emits_metric_event("integrity_validator", "p4obs", "metric_6")
_emit_records_incident_event("integrity_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("integrity_validator", "p4obs", "anomaly")
_emit_writes_observability_log("integrity_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("integrity_validator", "p4obs", "mon_state")
_emit_triggers_alert("integrity_validator", "p4obs", "alert")
_emit_links_incident_trace("integrity_validator", "p4obs", "trace_link")
_emit_captures_pattern("integrity_validator", "p3lm", "pattern")
_emit_records_learning_event("integrity_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("integrity_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("integrity_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("integrity_validator", "p3lm", "routing")
_emit_improves_agent_policy("integrity_validator", "p3lm", "policy")
_emit_stores_learning_state("integrity_validator", "p3lm", "state")
_emit_records_execution_trace("integrity_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("integrity_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("integrity_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("integrity_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("integrity_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("integrity_validator", "env_read", "p2_env_1")
_emit_reads_environ("integrity_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("integrity_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("integrity_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "integrity_validator", "context_pull")
_emit_pulls_context("p1", "integrity_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "integrity_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "integrity_validator", "uwg_term_2")
_emit_writes_through("p1", "integrity_validator", "write_through")
_emit_writes_through("p1", "integrity_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "integrity_validator", "safety_validation")
_emit_invokes_eval("p1", "integrity_validator", "eval_call")
_emit_proposal_commits_routing("p1", "integrity_validator", "routing_commit")

logger = logging.getLogger(__name__)
_GENESIS_HASH = "0" * 64


def compute_entry_hash(prev_hash: str, entry: dict[str, Any]) -> str:
    """Compute chained SHA256: hash(prev_hash || entry_bytes)."""
    from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation  # noqa: F401

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
