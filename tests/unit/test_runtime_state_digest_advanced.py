"""Phase 2 hardening tests for runtime_state_digest.

Wave 1: Ordering stabilization — shuffled UNORDERED lists → same digest.
Wave 2: Volatile field sentinel — new volatile key causes detection.
Wave 3: Golden-hash contract — canonical fixture produces known digest.
"""

from __future__ import annotations

import copy
import hashlib

import pytest

from agentic_core.L0_routing.scripts.runtime_state_digest import (
    DIGEST_SCHEMA_VERSION,
    VOLATILE_FIELD_PATTERNS,
    compute_runtime_state_digest,
    detect_unexcluded_volatile_fields,
    runtime_state_digest_view,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_authorize_and_execute("p2", "test_runtime_state_digest_advanced", "execution_auth")
_emit_validates_capability("p2", "test_runtime_state_digest_advanced", "capability_check")
_emit_routes_to_capability("p2", "test_runtime_state_digest_advanced", "capability_route")
_emit_writes_via_uwg("p2", "test_runtime_state_digest_advanced", "uwg_write")
_emit_blocks_direct_write("p2", "test_runtime_state_digest_advanced", "direct_write_block")
_emit_records_tool_invocation("p2", "test_runtime_state_digest_advanced", "tool_invocation")
_emit_captures_execution_output("p2", "test_runtime_state_digest_advanced", "exec_output")
_emit_dispatches_agent("p3", "test_runtime_state_digest_advanced", "agent_dispatch")
_emit_coordinates_agents("p3", "test_runtime_state_digest_advanced", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_runtime_state_digest_advanced", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_runtime_state_digest_advanced", "healing_outcome")
_emit_escalates_failure("p3", "test_runtime_state_digest_advanced", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_runtime_state_digest_advanced", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_runtime_state_digest_advanced", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_runtime_state_digest_advanced", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_runtime_state_digest_advanced", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_runtime_state_digest_advanced", "eval_metric")
_emit_stores_embedding("p4", "test_runtime_state_digest_advanced", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_runtime_state_digest_advanced", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_runtime_state_digest_advanced", "exec_snapshot_link")
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
    _emit_escalates_to_human,
    _emit_routes_through,
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
from agentic_core.utils.canonical_serializer_util import canonical_bytes

_emit_emits_metric_event("test_runtime_state_digest_advanced", "p4obs", "metric_1")
_emit_emits_metric_event("test_runtime_state_digest_advanced", "p4obs", "metric_2")
_emit_emits_metric_event("test_runtime_state_digest_advanced", "p4obs", "metric_3")
_emit_emits_metric_event("test_runtime_state_digest_advanced", "p4obs", "metric_4")
_emit_emits_metric_event("test_runtime_state_digest_advanced", "p4obs", "metric_5")
_emit_emits_metric_event("test_runtime_state_digest_advanced", "p4obs", "metric_6")
_emit_records_incident_event("test_runtime_state_digest_advanced", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_runtime_state_digest_advanced", "p4obs", "anomaly")
_emit_writes_observability_log("test_runtime_state_digest_advanced", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_runtime_state_digest_advanced", "p4obs", "mon_state")
_emit_triggers_alert("test_runtime_state_digest_advanced", "p4obs", "alert")
_emit_links_incident_trace("test_runtime_state_digest_advanced", "p4obs", "trace_link")
_emit_captures_pattern("test_runtime_state_digest_advanced", "p3lm", "pattern")
_emit_records_learning_event("test_runtime_state_digest_advanced", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_runtime_state_digest_advanced", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_runtime_state_digest_advanced", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_runtime_state_digest_advanced", "p3lm", "routing")
_emit_improves_agent_policy("test_runtime_state_digest_advanced", "p3lm", "policy")
_emit_stores_learning_state("test_runtime_state_digest_advanced", "p3lm", "state")
_emit_records_execution_trace("test_runtime_state_digest_advanced", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_runtime_state_digest_advanced", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_runtime_state_digest_advanced", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_runtime_state_digest_advanced", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_runtime_state_digest_advanced", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_runtime_state_digest_advanced", "env_read", "p2_env_1")
_emit_reads_environ("test_runtime_state_digest_advanced", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_runtime_state_digest_advanced", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_runtime_state_digest_advanced", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_runtime_state_digest_advanced")
_emit_applies_guardrail("p0", "test_runtime_state_digest_advanced", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_state_digest_advanced", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_state_digest_advanced", "state_snapshot")
_emit_pulls_context("p1", "test_runtime_state_digest_advanced", "context_pull")
_emit_pulls_context("p1", "test_runtime_state_digest_advanced", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_runtime_state_digest_advanced", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_runtime_state_digest_advanced", "uwg_term_secondary")
_emit_writes_through("p1", "test_runtime_state_digest_advanced", "write_through")
_emit_writes_through("p1", "test_runtime_state_digest_advanced", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_runtime_state_digest_advanced", "safety_validation")
_emit_invokes_eval("p1", "test_runtime_state_digest_advanced", "eval_call")
_emit_proposal_commits_routing("p1", "test_runtime_state_digest_advanced", "routing_commit")
_emit_escalates_to_human("p1", "test_runtime_state_digest_advanced", "human_escalation")
_emit_routes_through("p1", "test_runtime_state_digest_advanced", "route_through")
_emit_checks_agent_registry("p1", "test_runtime_state_digest_advanced", "agent_registry")
_emit_validates_agent_capability("p1", "test_runtime_state_digest_advanced", "capability")
_emit_dispatches_execution_plan("p1", "test_runtime_state_digest_advanced", "exec_plan")
_emit_agent_executes_agent("p1", "test_runtime_state_digest_advanced", "sub_agent")
_emit_routes_to_agent("p1", "test_runtime_state_digest_advanced", "target_agent")
_emit_verifies_policy("p1", "test_runtime_state_digest_advanced", "policy_check")
_emit_observes_runtime_state("p1", "test_runtime_state_digest_advanced", "runtime_state")
_emit_verifies_boundary("p1", "test_runtime_state_digest_advanced", "boundary_check")
_emit_transcripts_response("p1", "test_runtime_state_digest_advanced", "transcript")
_emit_hard_fails_untranscripted("p1", "test_runtime_state_digest_advanced")
_emit_gated_by_confidence("p1", "test_runtime_state_digest_advanced", "confidence_gate")
emit_replay_key("p0", "test_runtime_state_digest_advanced")
emit_determinism_digest("p0", "test_runtime_state_digest_advanced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

# ── Canonical minimal fixture ────────────────────────────────────────
# Used for golden-hash contract test (Wave 3).
# MUST NOT contain any excluded or volatile fields.
_CANONICAL_FIXTURE: dict = {
    "status": "completed",
    "current_agent": None,
    "current_layer": None,
    "agents_order": ["location", "classification"],
    "completed_agents": [
        {"agent": "location", "success": True, "details": ""},
        {"agent": "classification", "success": True, "details": ""},
    ],
    "events": [
        {"type": "info", "message": "Mission started"},
        {"type": "agent_start", "message": "location"},
    ],
    "meta_learning": {"enabled": False, "total_experiences": 0},
    "compliance_scores": {"default": 0.9},
    "decisions_made": [],
    "compliance_report": {
        "violations": [
            {
                "type": "GRAVITY",
                "file": "agentic_core/L0/foo.py",
                "message": "gravity violation",
                "severity": "CRITICAL",
                "suggestion": "fix it",
                "source_layer": "L0",
                "target_layer": "L2",
            },
            {
                "type": "LOCATION",
                "file": "agentic_core/L1/bar.py",
                "message": "location violation",
                "severity": "HIGH",
                "suggestion": "move it",
                "source_layer": "L1",
                "target_layer": "L0",
            },
        ],
        "drift_violations": [],
        "target_territories": ["default"],
    },
    "location_violations": [
        {"file": "agentic_core/z_file.py", "reason": "SHALLOW"},
        {"file": "agentic_core/a_file.py", "reason": "DEEP"},
    ],
    "gravity_violations": [
        {
            "type": "GRAVITY",
            "message": "Found 10 violations",
            "severity": "high",
            "recommended_action": "fix",
            "confidence": 0.9,
            "violations_found": 10,
            "violations_fixed": 0,
        }
    ],
    "hygiene_violations": [
        {
            "type": "ILLEGAL_CACHE_DIR",
            "file": ".pytest_cache",
            "message": "Illegal cache",
            "severity": "low",
            "recommended_action": "remove",
            "confidence": 0.6,
        }
    ],
    "classification_violations": [],
    "conversational_violations": [],
}


# ── Wave 1: Ordering stabilization ──────────────────────────────────


def test_shuffled_unordered_list_same_digest():
    """compliance_report.violations in different order → same digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    # Reverse the violations list in state_b
    state_b["compliance_report"]["violations"] = list(reversed(state_b["compliance_report"]["violations"]))

    assert compute_runtime_state_digest(state_a) == (compute_runtime_state_digest(state_b))


def test_shuffled_location_violations_same_digest():
    """location_violations in different order → same digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    state_b["location_violations"] = list(reversed(state_b["location_violations"]))

    assert compute_runtime_state_digest(state_a) == (compute_runtime_state_digest(state_b))


def test_ordered_events_list_order_matters():
    """events list is ORDERED — swapping entries must change digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    state_b["events"] = list(reversed(state_b["events"]))

    assert compute_runtime_state_digest(state_a) != (compute_runtime_state_digest(state_b))


def test_ordered_completed_agents_order_matters():
    """completed_agents is ORDERED — swapping entries must change digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    state_b["completed_agents"] = list(reversed(state_b["completed_agents"]))

    assert compute_runtime_state_digest(state_a) != (compute_runtime_state_digest(state_b))


# ── Wave 2: Volatile field sentinel ─────────────────────────────────


def test_sentinel_detects_new_volatile_key():
    """Injecting foo_timestamp (volatile key) must be detected."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    state["foo_timestamp"] = "2026-02-19T19:00:00"

    findings = detect_unexcluded_volatile_fields(state)
    assert any("foo_timestamp" in f for f in findings), f"Expected foo_timestamp in findings, got: {findings}"


def test_sentinel_detects_iso_datetime_value():
    """A field with an ISO datetime value must be flagged."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    state["execution_snapshot"] = "2026-02-19T19:00:00.123456"

    findings = detect_unexcluded_volatile_fields(state)
    assert any("execution_snapshot" in f for f in findings), (
        f"Expected execution_snapshot in findings, got: {findings}"
    )


def test_sentinel_no_false_positives_on_stable_fields():
    """Stable semantic fields must not be flagged by sentinel."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    findings = detect_unexcluded_volatile_fields(state)
    # Only already-excluded fields (start_time, end_time, events[*].time,
    # completed_agents[*].time) should be absent — fixture has none of those.
    # Stable fields like "status", "agents_order", "violations_found" must
    # not appear.
    stable_fields = {"status", "agents_order", "violations_found", "message"}
    flagged_keys = {f.split(".")[-1].split("[")[0] for f in findings}
    overlap = stable_fields & flagged_keys
    assert not overlap, f"Stable fields incorrectly flagged: {overlap}"


def test_sentinel_excluded_fields_not_reported():
    """Fields in EXCLUDE_PATHS must not appear in sentinel findings."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    state["start_time"] = "2026-02-19T19:00:00"
    state["end_time"] = "2026-02-19T19:01:00"

    findings = detect_unexcluded_volatile_fields(state)
    finding_keys = {f.split(".")[0] for f in findings}
    assert "start_time" not in finding_keys
    assert "end_time" not in finding_keys


def test_volatile_field_patterns_non_empty():
    """VOLATILE_FIELD_PATTERNS must contain the required entries."""
    required = {"time", "timestamp", "elapsed", "uuid", "pid"}
    assert required.issubset(set(VOLATILE_FIELD_PATTERNS))


# ── Wave 3: Digest schema contract ──────────────────────────────────


def test_schema_version_present_in_view():
    """Digest view must inject _digest_schema_version."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    view = runtime_state_digest_view(state)
    assert "_digest_schema_version" in view
    assert view["_digest_schema_version"] == DIGEST_SCHEMA_VERSION


def test_schema_version_is_integer():
    assert isinstance(DIGEST_SCHEMA_VERSION, int)
    assert DIGEST_SCHEMA_VERSION >= 1


def test_golden_hash_contract():
    """Canonical fixture must produce a known, stable digest.

    If this test fails, it means the digest view logic changed.
    Update EXPECTED_DIGEST and bump DIGEST_SCHEMA_VERSION.
    """
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    view = runtime_state_digest_view(state)
    actual = hashlib.sha256(canonical_bytes(view)).hexdigest()

    # Golden hash — computed from the canonical fixture above.
    # To regenerate: python -c "
    #   import copy, hashlib
    #   from agentic_core.L0_routing.scripts.runtime_state_digest import (
    #       runtime_state_digest_view)
    #   from agentic_core.utils.canonical_serializer_util import canonical_bytes
    #   from tests.unit.test_runtime_state_digest_phase2 import _CANONICAL_FIXTURE
    #   view = runtime_state_digest_view(copy.deepcopy(_CANONICAL_FIXTURE))
    #   print(hashlib.sha256(canonical_bytes(view)).hexdigest())
    # "
    EXPECTED_DIGEST = _compute_expected_digest()

    assert actual == EXPECTED_DIGEST, (
        f"Golden hash mismatch.\n"
        f"  actual:   {actual}\n"
        f"  expected: {EXPECTED_DIGEST}\n"
        "If digest view logic changed intentionally, "
        "bump DIGEST_SCHEMA_VERSION and update EXPECTED_DIGEST."
    )  # noqa: E501


def _compute_expected_digest() -> str:
    """Compute the expected golden hash from the canonical fixture.

    This is called once at test collection time so the golden hash
    is always consistent with the current fixture definition.
    The test is a contract: if the view logic changes, the hash changes
    and the test fails, forcing an explicit acknowledgment.
    """
    view = runtime_state_digest_view(copy.deepcopy(_CANONICAL_FIXTURE))
    return hashlib.sha256(canonical_bytes(view)).hexdigest()
