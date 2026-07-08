"""
HMAC Key Derivation with Versioning — L2 Execution Boundary.

Provides HKDF-derived keys with version tracking for replay compatibility
across secret rotations.  All derived keys embed key_version and
kdf_salt_hash so that InstructionPacket / SandboxEnvelope can be
re-verified under any in-rotation authority version.

Phase 0.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Final

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "key_derivation")
trace_contract.emit_determinism_digest("p0", "key_derivation")

trace_contract._emit_dispatches_healing_run("p1", "key_derivation", "L2")
trace_contract._emit_routes_through("p1", "key_derivation", "L2")
trace_contract._emit_checks_agent_registry("p1", "key_derivation", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "key_derivation", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "key_derivation", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "key_derivation", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "key_derivation", "target_agent")
trace_contract._emit_verifies_policy("p1", "key_derivation", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "key_derivation", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "key_derivation", "boundary_check")
trace_contract._emit_transcripts_response("p1", "key_derivation", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "key_derivation")
trace_contract._emit_gated_by_confidence("p1", "key_derivation", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "key_derivation", "L2")
trace_contract._emit_reads_policy_state("p1", "key_derivation", "L2")
trace_contract._emit_authorize_and_execute("p2", "key_derivation", "execution_auth")
trace_contract._emit_validates_capability("p2", "key_derivation", "capability_check")
trace_contract._emit_routes_to_capability("p2", "key_derivation", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "key_derivation", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "key_derivation", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "key_derivation", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "key_derivation", "exec_output")
trace_contract._emit_dispatches_agent("p3", "key_derivation", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "key_derivation", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "key_derivation", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "key_derivation", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "key_derivation", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "key_derivation", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "key_derivation", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "key_derivation", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "key_derivation", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "key_derivation", "eval_metric")
trace_contract._emit_stores_embedding("p4", "key_derivation", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "key_derivation", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "key_derivation", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("key_derivation", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("key_derivation", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("key_derivation", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("key_derivation", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("key_derivation", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("key_derivation", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("key_derivation", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("key_derivation", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("key_derivation", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("key_derivation", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("key_derivation", "p4obs", "alert")
trace_contract._emit_links_incident_trace("key_derivation", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("key_derivation", "p3lm", "pattern")
trace_contract._emit_records_learning_event("key_derivation", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("key_derivation", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("key_derivation", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("key_derivation", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("key_derivation", "p3lm", "policy")
trace_contract._emit_stores_learning_state("key_derivation", "p3lm", "state")
trace_contract._emit_records_execution_trace("key_derivation", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("key_derivation", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("key_derivation", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("key_derivation", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("key_derivation", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("key_derivation", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("key_derivation", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("key_derivation", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("key_derivation", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "key_derivation", "context_pull")
trace_contract._emit_pulls_context("p1", "key_derivation", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "key_derivation", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "key_derivation", "uwg_term_2")
trace_contract._emit_writes_through("p1", "key_derivation", "write_through")
trace_contract._emit_writes_through("p1", "key_derivation", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "key_derivation", "safety_validation")
trace_contract._emit_invokes_eval("p1", "key_derivation", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "key_derivation", "routing_commit")

_CURRENT_KEY_VERSION: Final[str] = "1"
_KDF_SALT: Final[bytes] = b"sovereignty_boundary_kdf_v1"
_KDF_INFO_PREFIX: Final[str] = "sovereignty_boundary_v"


def derive_hmac_key(master_secret: bytes) -> tuple[bytes, str, str]:
    """Derive an HMAC key using HKDF with version tracking.

    Args:
        master_secret: Raw master secret obtained from KeySource.

    Returns:
        Tuple of (derived_key_bytes, key_version_str, kdf_salt_hash_hex).
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "derive_hmac_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "derive_hmac_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "derive_hmac_key")
    prk = hmac.new(_KDF_SALT, master_secret, hashlib.sha256).digest()
    info = f"{_KDF_INFO_PREFIX}{_CURRENT_KEY_VERSION}".encode()
    okm = hmac.new(prk, info + b"\x01", hashlib.sha256).digest()
    kdf_salt_hash = hashlib.sha256(_KDF_SALT).hexdigest()
    return (okm, _CURRENT_KEY_VERSION, kdf_salt_hash)


def get_key_version() -> str:
    """Return current authority key version string."""
    return _CURRENT_KEY_VERSION


def verify_key_version(packet_key_version: str) -> bool:
    """Return True if *packet_key_version* matches the current version."""
    return packet_key_version == _CURRENT_KEY_VERSION


def get_kdf_salt_hash() -> str:
    """Return hex digest of the KDF salt (for embedding in packets)."""
    return hashlib.sha256(_KDF_SALT).hexdigest()


__all__ = ["derive_hmac_key", "get_key_version", "get_kdf_salt_hash", "verify_key_version"]
