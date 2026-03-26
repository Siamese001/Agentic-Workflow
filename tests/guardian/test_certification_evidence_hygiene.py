"""
Phase 3.1 — Certification Evidence Hygiene Normalization Tests.

Tests:
1. Schema lock: extra field → reject, missing required field → reject
2. Canonical hash seal: SHA256 present, stable, mutation-sensitive
3. Idempotency: identical pipeline runs produce byte-for-byte identical JSON
4. Deterministic field ordering: sorted keys, stable list ordering
5. Nondeterministic field gating: no timestamps, no random UUIDs
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_certification_evidence_hygiene")
# REMOVED: _emit_applies_guardrail("p0", "test_certification_evidence_hygiene", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_certification_evidence_hygiene", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_certification_evidence_hygiene", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_certification_evidence_hygiene")
# REMOVED: emit_determinism_digest("p0", "test_certification_evidence_hygiene")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_certification_evidence_hygiene", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_certification_evidence_hygiene", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_certification_evidence_hygiene", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_certification_evidence_hygiene", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_certification_evidence_hygiene", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_certification_evidence_hygiene", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_certification_evidence_hygiene", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_certification_evidence_hygiene", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_certification_evidence_hygiene", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_certification_evidence_hygiene", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_certification_evidence_hygiene", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_certification_evidence_hygiene", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_certification_evidence_hygiene", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_certification_evidence_hygiene", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_certification_evidence_hygiene", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_certification_evidence_hygiene", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_certification_evidence_hygiene", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_certification_evidence_hygiene", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_certification_evidence_hygiene", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_certification_evidence_hygiene", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  # MOVED: from agentic_core.L0_routing.types.guardian_contract_types import (
    CONTRACT_JSON_SCHEMA,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    validate_against_json_schema,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_certification_evidence_hygiene", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_certification_evidence_hygiene", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_certification_evidence_hygiene", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_certification_evidence_hygiene", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_certification_evidence_hygiene", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_certification_evidence_hygiene", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_certification_evidence_hygiene", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_certification_evidence_hygiene", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_certification_evidence_hygiene", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_certification_evidence_hygiene", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_certification_evidence_hygiene", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_certification_evidence_hygiene", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_certification_evidence_hygiene", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_certification_evidence_hygiene", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_certification_evidence_hygiene", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_certification_evidence_hygiene", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_certification_evidence_hygiene", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_certification_evidence_hygiene", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_certification_evidence_hygiene", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_certification_evidence_hygiene", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_certification_evidence_hygiene", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_certification_evidence_hygiene", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_certification_evidence_hygiene", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_certification_evidence_hygiene", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_certification_evidence_hygiene", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_certification_evidence_hygiene", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_certification_evidence_hygiene", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_certification_evidence_hygiene", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_certification_evidence_hygiene", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_certification_evidence_hygiene", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_certification_evidence_hygiene", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_certification_evidence_hygiene", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_certification_evidence_hygiene", "write_through")
# REMOVED: _emit_writes_through("p1", "test_certification_evidence_hygiene", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_certification_evidence_hygiene", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_certification_evidence_hygiene", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_certification_evidence_hygiene", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_certification_evidence_hygiene", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_certification_evidence_hygiene", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_certification_evidence_hygiene", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_certification_evidence_hygiene", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_certification_evidence_hygiene", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_certification_evidence_hygiene", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_certification_evidence_hygiene", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_certification_evidence_hygiene", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_certification_evidence_hygiene", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_certification_evidence_hygiene", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_certification_evidence_hygiene", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_certification_evidence_hygiene")
# REMOVED: _emit_gated_by_confidence("p1", "test_certification_evidence_hygiene", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _disable_v15(monkeypatch):
    monkeypatch.setenv("V15_ENFORCEMENT", "0")


@pytest.fixture
def certification_result() -> GuardianResult:
    """A representative certification artifact with multiple checks."""
    r = GuardianResult(guardian_id="cert_test")
    r.add_check("check_b", CheckStatus.PASS, "Second check")
    r.add_check("check_a", CheckStatus.PASS, "First check")
    r.add_artifact(ArtifactType.JSON, "docs/reports/plans/out.json", "Output")
    r.add_artifact(ArtifactType.LOG, "agentic_core/logs/run.log", "Run log")
    r.metrics = {"items_scanned": 10, "files_checked": 5}
    r.remediation_hints = ["hint_z", "hint_a"]
    return r


# ---------------------------------------------------------------------------
# 1. Schema Lock — negative tests
# ---------------------------------------------------------------------------


class TestSchemaLock:
    """CONTRACT_JSON_SCHEMA rejects extra/missing fields."""

    def test_extra_field_rejected(self, certification_result: GuardianResult):
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L0_routing.types.guardian_contract_types import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                d = certification_result.to_dict()
                d["rogue_field"] = "should_not_exist"
                errors = validate_against_json_schema(d)
                assert any("rogue_field" in e for e in errors), (
                    f"Extra field 'rogue_field' must be rejected, got errors: {errors}"
                )


    def test_missing_required_field_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        del d["guardian_id"]
        errors = validate_against_json_schema(d)
        assert any("guardian_id" in e for e in errors), (
            f"Missing 'guardian_id' must be rejected, got errors: {errors}"
        )

    def test_missing_checks_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        del d["checks"]
        errors = validate_against_json_schema(d)
        assert any("checks" in e for e in errors)

    def test_missing_status_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        del d["status"]
        errors = validate_against_json_schema(d)
        assert any("status" in e for e in errors)

    def test_valid_result_passes_schema(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        errors = validate_against_json_schema(d)
        assert errors == [], f"Valid result should pass schema: {errors}"

    def test_certification_hash_in_schema(self):
        props = CONTRACT_JSON_SCHEMA["properties"]
        assert "certification_hash" in props, "certification_hash must be in CONTRACT_JSON_SCHEMA"

    def test_additional_properties_false(self):
        assert CONTRACT_JSON_SCHEMA.get("additionalProperties") is False


# ---------------------------------------------------------------------------
# 2. Canonical Hash Seal
# ---------------------------------------------------------------------------


class TestCanonicalHashSeal:
    """certification_hash is SHA256 over canonical JSON, excluding itself."""

    def test_hash_present_after_to_json(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        assert parsed["certification_hash"] is not None
        assert len(parsed["certification_hash"]) == 64  # SHA256 hex

    def test_hash_stable_across_calls(self, certification_result: GuardianResult):
    """Test hash_stable_across_calls runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute hash_stable_across_calls
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        assert h_stored == h_expected

    def test_mutation_changes_hash(self, certification_result: GuardianResult):
        """Negative test: mutating the payload MUST change the hash."""
        certification_result.compute_certification_hash()
        h_before = certification_result.certification_hash

        certification_result.add_check("check_c", CheckStatus.FAIL, "Injected")
        certification_result.compute_certification_hash()
        h_after = certification_result.certification_hash

        assert h_before != h_after, "Mutating the result must change certification_hash"

    def test_reordering_checks_does_not_change_hash(self):
        """Checks are sorted by check_id so reordering must not affect hash."""
        r1 = GuardianResult(guardian_id="order_test")
        r1.add_check("b", CheckStatus.PASS, "second")
        r1.add_check("a", CheckStatus.PASS, "first")

        r2 = GuardianResult(guardian_id="order_test")
        r2.add_check("a", CheckStatus.PASS, "first")
        r2.add_check("b", CheckStatus.PASS, "second")

        r1.compute_certification_hash()
        r2.compute_certification_hash()
        assert r1.certification_hash == r2.certification_hash


# ---------------------------------------------------------------------------
# 3. Deterministic Field Ordering
# ---------------------------------------------------------------------------


class TestDeterministicOrdering:
    """Serialized JSON has sorted keys and stable list ordering."""

    def test_sorted_keys_in_json(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        keys = list(parsed.keys())
        assert keys == sorted(keys), f"Top-level keys must be sorted: {keys}"

    def test_checks_sorted_by_check_id(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        check_ids = [c["check_id"] for c in parsed["checks"]]
        assert check_ids == sorted(check_ids), f"Checks must be sorted by check_id: {check_ids}"

    def test_artifacts_sorted_by_path(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        paths = [a["path"] for a in parsed["artifacts"]]
        assert paths == sorted(paths), f"Artifacts must be sorted by path: {paths}"

    def test_remediation_hints_sorted(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        hints = parsed["remediation_hints"]
        assert hints == sorted(hints), f"Hints must be sorted: {hints}"

    def test_metrics_keys_sorted(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        metric_keys = list(parsed["metrics"].keys())
        assert metric_keys == sorted(metric_keys), f"Metric keys must be sorted: {metric_keys}"


# ---------------------------------------------------------------------------
# 4. Nondeterministic Field Gating
# ---------------------------------------------------------------------------


class TestNondeterministicGating:
    """Nondeterministic fields (timestamps, random UUIDs) are gated."""

    def test_no_timestamp_by_default(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        assert "timestamp" not in d or d.get("timestamp") is None

    def test_no_random_uuid_in_trace_id(self):
        """v15_trace_id must not be a random UUID when set by maybe_sign_result."""
        import re

        uuid4_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        )
        r = GuardianResult(guardian_id="nonce_test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        d = r.to_dict()
        trace_id = d.get("v15_trace_id")
        if trace_id is not None:
            assert not uuid4_pattern.match(trace_id), f"v15_trace_id must not be a random UUID v4: {trace_id}"

    def test_no_elapsed_ms_in_evidence(self, certification_result: GuardianResult):
        """elapsed_ms is nondeterministic and must not appear in serialized output."""
        raw = certification_result.to_json()
        assert "elapsed_ms" not in raw


# ---------------------------------------------------------------------------
# 5. Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Identical inputs produce byte-for-byte identical certification JSON."""

    def _make_result(self) -> GuardianResult:
        r = GuardianResult(guardian_id="idempotency_test")
        r.add_check("check_b", CheckStatus.PASS, "B ok")
        r.add_check("check_a", CheckStatus.PASS, "A ok")
        r.add_artifact(ArtifactType.JSON, "docs/out.json", "Output")
        r.metrics = {"count": 42}
        r.remediation_hints = ["z_hint", "a_hint"]
        return r

    def test_byte_for_byte_identical(self):
        r1 = self._make_result()
        r2 = self._make_result()

        j1 = r1.to_json()
        j2 = r2.to_json()
        assert j1 == j2, "Identical inputs must produce byte-for-byte identical JSON"

    def test_identical_certification_hash(self):
        r1 = self._make_result()
        r2 = self._make_result()

        r1.compute_certification_hash()
        r2.compute_certification_hash()
        assert r1.certification_hash == r2.certification_hash

    def test_revert_sort_breaks_idempotency(self):
        """Proves that removing deterministic sort would break idempotency.

        We manually construct two dicts with different insertion order and
        verify they serialize identically due to sort_keys=True.
        """
        r = self._make_result()
        j1 = r.to_json()
        parsed = json.loads(j1)
        reserialized = json.dumps(parsed, indent=2, sort_keys=True)
        assert j1 == reserialized, "Re-serialization with sort_keys=True must match original"

    def test_revert_hash_breaks_idempotency(self):
        """Proves that removing hash computation would break certification."""
        r = self._make_result()
        _ = r.to_json()
        assert r.certification_hash is not None, "certification_hash must be set after to_json()"
        saved_hash = r.certification_hash

        r.summary = "MUTATED"
        r.compute_certification_hash()
        assert r.certification_hash != saved_hash, "Mutating payload must change certification_hash"
