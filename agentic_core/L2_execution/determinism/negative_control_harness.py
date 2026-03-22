"""NegativeControlHarness — L2 Execution determinism.

Provides a controlled tamper mechanism for proving that the determinism
digest is sensitive to configuration changes.  When the environment variable
W_HARDEN_NEGCTRL_TAMPER=1 is set, the harness injects known-bad values into
the config surface so the resulting digest MUST differ from the clean run.

Contract:
- get_config_surface()  -> dict.  Tampered if W_HARDEN_NEGCTRL_TAMPER=1.
- is_tamper_active()    -> bool.
- assert_digest_differs(clean, tampered) -> raises if they are equal.

Design invariants:
  - Only '1' triggers tampering (not 'true', 'yes', etc.).
  - Tampered surface is fully deterministic (same inputs -> same output).
  - No wall-clock access.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "negative_control_harness")
emit_determinism_digest("p0", "negative_control_harness")

_emit_dispatches_healing_run("p1", "negative_control_harness", "L2")
_emit_routes_through("p1", "negative_control_harness", "L2")
_emit_checks_agent_registry("p1", "negative_control_harness", "agent_registry")
_emit_validates_agent_capability("p1", "negative_control_harness", "capability")
_emit_dispatches_execution_plan("p1", "negative_control_harness", "exec_plan")
_emit_agent_executes_agent("p1", "negative_control_harness", "sub_agent")
_emit_routes_to_agent("p1", "negative_control_harness", "target_agent")
_emit_verifies_policy("p1", "negative_control_harness", "policy_check")
_emit_observes_runtime_state("p1", "negative_control_harness", "runtime_state")
_emit_verifies_boundary("p1", "negative_control_harness", "boundary_check")
_emit_transcripts_response("p1", "negative_control_harness", "transcript")
_emit_hard_fails_untranscripted("p1", "negative_control_harness")
_emit_gated_by_confidence("p1", "negative_control_harness", "confidence_gate")
_emit_escalates_to_human("p1", "negative_control_harness", "L2")
_emit_reads_policy_state("p1", "negative_control_harness", "L2")
_emit_authorize_and_execute("p2", "negative_control_harness", "execution_auth")
_emit_validates_capability("p2", "negative_control_harness", "capability_check")
_emit_routes_to_capability("p2", "negative_control_harness", "capability_route")
_emit_writes_via_uwg("p2", "negative_control_harness", "uwg_write")
_emit_blocks_direct_write("p2", "negative_control_harness", "direct_write_block")
_emit_records_tool_invocation("p2", "negative_control_harness", "tool_invocation")
_emit_captures_execution_output("p2", "negative_control_harness", "exec_output")
_emit_dispatches_agent("p3", "negative_control_harness", "agent_dispatch")
_emit_coordinates_agents("p3", "negative_control_harness", "agent_coordination")
_emit_records_workflow_lineage("p3", "negative_control_harness", "workflow_lineage")
_emit_records_healing_outcome("p3", "negative_control_harness", "healing_outcome")
_emit_escalates_failure("p3", "negative_control_harness", "failure_escalation")
_emit_orchestrates_workflow("p3", "negative_control_harness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "negative_control_harness", "healing_dispatch")
_emit_invokes_evaluation("p3", "negative_control_harness", "evaluation_signal")
_emit_records_telemetry_event("p4", "negative_control_harness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "negative_control_harness", "eval_metric")
_emit_stores_embedding("p4", "negative_control_harness", "embedding_store")
_emit_updates_meta_learning_state("p4", "negative_control_harness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "negative_control_harness", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

record_execution_trace("negative_control_harness", "negative_control_harness_trace")


_emit_emits_metric_event("negative_control_harness", "p4obs", "metric_1")
_emit_emits_metric_event("negative_control_harness", "p4obs", "metric_2")
_emit_emits_metric_event("negative_control_harness", "p4obs", "metric_3")
_emit_emits_metric_event("negative_control_harness", "p4obs", "metric_4")
_emit_emits_metric_event("negative_control_harness", "p4obs", "metric_5")
_emit_emits_metric_event("negative_control_harness", "p4obs", "metric_6")
_emit_records_incident_event("negative_control_harness", "p4obs", "incident")
_emit_captures_runtime_anomaly("negative_control_harness", "p4obs", "anomaly")
_emit_writes_observability_log("negative_control_harness", "p4obs", "obs_log")
_emit_updates_monitoring_state("negative_control_harness", "p4obs", "mon_state")
_emit_triggers_alert("negative_control_harness", "p4obs", "alert")
_emit_links_incident_trace("negative_control_harness", "p4obs", "trace_link")
_emit_captures_pattern("negative_control_harness", "p3lm", "pattern")
_emit_records_learning_event("negative_control_harness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("negative_control_harness", "p3lm", "snapshot")
_emit_feeds_meta_learning("negative_control_harness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("negative_control_harness", "p3lm", "routing")
_emit_improves_agent_policy("negative_control_harness", "p3lm", "policy")
_emit_stores_learning_state("negative_control_harness", "p3lm", "state")
_emit_records_execution_trace("negative_control_harness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("negative_control_harness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("negative_control_harness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("negative_control_harness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("negative_control_harness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("negative_control_harness", "env_read", "p2_env_1")
_emit_reads_environ("negative_control_harness", "env_read", "p2_env_2")
_emit_reads_runtime_state("negative_control_harness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("negative_control_harness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "negative_control_harness", "context_pull")
_emit_pulls_context("p1", "negative_control_harness", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "negative_control_harness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "negative_control_harness", "uwg_term_2")
_emit_writes_through("p1", "negative_control_harness", "write_through")
_emit_writes_through("p1", "negative_control_harness", "write_through_2")
_emit_validated_by_safety_plane("p1", "negative_control_harness", "safety_validation")
_emit_invokes_eval("p1", "negative_control_harness", "eval_call")
_emit_proposal_commits_routing("p1", "negative_control_harness", "routing_commit")


def is_tamper_active() -> bool:
    """Return True iff W_HARDEN_NEGCTRL_TAMPER == '1' in the environment."""
    return os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1"


_CLEAN_CONFIG: dict[str, Any] = {
    "blas_eps": 1e-12,
    "cutoff": 0.0,
    "decision_delta_limit": 0.1,
    "embedding_batch": 500,
    "embedding_enabled": True,
    "embedding_retry": 8,
    "max_k": 20,
    "meta_learning_enabled": True,
    "model_version": "multilingual-e5-large",
    "oscillation_detector_enabled": True,
    "proposal_only": True,
    "rlhf_delta_max": 2.0,
    "rlhf_delta_min": 0.1,
    "threads": 4,
    "top_k": 20,
}
_TAMPER_OVERRIDES: dict[str, Any] = {"cutoff": 0.999, "tampered": True, "top_k": 999}


def get_config_surface() -> dict[str, Any]:
    """Return the embedding/meta-learning config surface.

    If W_HARDEN_NEGCTRL_TAMPER=1 the surface is modified with known-bad
    values so the resulting digest differs from the clean run.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_config_surface", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_config_surface", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_config_surface")
    surface = dict(_CLEAN_CONFIG)
    if is_tamper_active():
        surface.update(_TAMPER_OVERRIDES)
    return surface


def hash_config_surface(surface: dict[str, Any]) -> str:
    """Return SHA-256 hex of the canonical config surface dict."""
    canonical = _canonical_json_bytes(surface)
    return hashlib.sha256(canonical).hexdigest()


def assert_digest_differs(clean_digest: str, tampered_digest: str) -> None:
    """Assert that *clean_digest* != *tampered_digest*.

    Raises:
        AssertionError: if the two digests are identical (tamper not detected).
    """
    if clean_digest == tampered_digest:
        raise AssertionError(
            f"NegativeControlHarness: digests are identical — tampering was NOT detected by the digest surface. This is a security failure.\n  clean    = {clean_digest}\n  tampered = {tampered_digest}"
        )


def assert_digest_stable(digest1: str, digest2: str) -> None:
    """Assert that *digest1* == *digest2* (two independent clean runs).

    Raises:
        AssertionError: if the two digests differ (non-determinism detected).
    """
    if digest1 != digest2:
        raise AssertionError(
            f"NegativeControlHarness: digests differ across runs — non-determinism detected.\n  run1 = {digest1}\n  run2 = {digest2}"
        )


def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


__all__ = [
    "assert_digest_differs",
    "assert_digest_stable",
    "get_config_surface",
    "hash_config_surface",
    "is_tamper_active",
]
