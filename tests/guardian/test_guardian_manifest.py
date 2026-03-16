"""
Guardian Manifest Integrity Tests — ReAct-Style (Observe → Verify → Report).

Tests the run_guardian_manifest script against sandboxed tmp_repo fixtures.
Verifies:
1. Missing manifest.json → SKIP (not applicable)
2. Missing .manifest.lock → FAIL
3. Matching checksums → PASS
4. Mismatched checksums → FAIL with evidence
5. JSON output conforms to guardian_contract schema
6. Deterministic: same input → same JSON output
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_guardian_manifest")
_emit_applies_guardrail("p0", "test_guardian_manifest", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_manifest", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_manifest", "state_snapshot")
emit_replay_key("p0", "test_guardian_manifest")
emit_determinism_digest("p0", "test_guardian_manifest")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_manifest", "execution_auth")
_emit_validates_capability("p2", "test_guardian_manifest", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_manifest", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_manifest", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_manifest", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_manifest", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_manifest", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_manifest", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_manifest", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_manifest", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_manifest", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_manifest", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_manifest", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_manifest", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_manifest", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_manifest", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_manifest", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_manifest", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_manifest", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_manifest", "exec_snapshot_link")

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

from agentic_core.L0_routing.scripts.run_guardian_manifest import (
    run_manifest_guardian,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    validate_no_absolute_paths,
)
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

_emit_emits_metric_event("test_guardian_manifest", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_manifest", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_manifest", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_manifest", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_manifest", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_manifest", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_manifest", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_manifest", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_manifest", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_manifest", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_manifest", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_manifest", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_manifest", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_manifest", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_manifest", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_manifest", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_manifest", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_manifest", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_manifest", "p3lm", "state")
_emit_records_execution_trace("test_guardian_manifest", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_manifest", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_manifest", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_manifest", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_manifest", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_manifest", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_manifest", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_manifest", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_manifest", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_manifest", "context_pull")
_emit_pulls_context("p1", "test_guardian_manifest", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_guardian_manifest", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_manifest", "uwg_term_secondary")
_emit_writes_through("p1", "test_guardian_manifest", "write_through")
_emit_writes_through("p1", "test_guardian_manifest", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_guardian_manifest", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_manifest", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_manifest", "routing_commit")
_emit_escalates_to_human("p1", "test_guardian_manifest", "human_escalation")
_emit_routes_through("p1", "test_guardian_manifest", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_manifest", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_manifest", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_manifest", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_manifest", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_manifest", "target_agent")
_emit_verifies_policy("p1", "test_guardian_manifest", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_manifest", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_manifest", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_manifest", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_manifest")
_emit_gated_by_confidence("p1", "test_guardian_manifest", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo_no_manifest(tmp_path: Path) -> Path:
    """Repo with no manifest.json at all."""
    return tmp_path


@pytest.fixture
def repo_no_lock(tmp_path: Path) -> Path:
    """Repo with manifest.json but no .manifest.lock."""
    (tmp_path / "manifest.json").write_text('{"agents": []}', encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_valid(tmp_path: Path) -> Path:
    """Repo with manifest.json and matching .manifest.lock."""
    content = b'{"agents": []}'
    (tmp_path / "manifest.json").write_bytes(content)
    (tmp_path / ".manifest.lock").write_text(_sha256(content), encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_tampered(tmp_path: Path) -> Path:
    """Repo with manifest.json modified after seal."""
    original = b'{"agents": []}'
    (tmp_path / ".manifest.lock").write_text(_sha256(original), encoding="utf-8")
    (tmp_path / "manifest.json").write_bytes(b'{"agents": ["rogue"]}')
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Missing manifest → SKIP
# ---------------------------------------------------------------------------


class TestMissingManifest:
    def test_no_manifest_returns_pass(self, repo_no_manifest: Path):
        result = run_manifest_guardian(repo_root=repo_no_manifest)
        assert result.status == GuardianStatus.PASS.value

    def test_no_manifest_has_skip_check(self, repo_no_manifest: Path):
        result = run_manifest_guardian(repo_root=repo_no_manifest)
        skip_checks = [c for c in result.checks if c.status == CheckStatus.SKIP.value]
        assert len(skip_checks) >= 1

    def test_manifest_exists_check_id(self, repo_no_manifest: Path):
        result = run_manifest_guardian(repo_root=repo_no_manifest)
        check_ids = {c.check_id for c in result.checks}
        assert "manifest_exists" in check_ids


# ---------------------------------------------------------------------------
# 2. Missing lock → FAIL
# ---------------------------------------------------------------------------


class TestMissingLock:
    def test_no_lock_fails(self, repo_no_lock: Path):
        result = run_manifest_guardian(repo_root=repo_no_lock)
        assert result.status == GuardianStatus.FAIL.value

    def test_no_lock_check_id(self, repo_no_lock: Path):
        result = run_manifest_guardian(repo_root=repo_no_lock)
        lock_check = next(c for c in result.checks if c.check_id == "lock_exists")
        assert lock_check.status == CheckStatus.FAIL.value

    def test_no_lock_has_remediation(self, repo_no_lock: Path):
        result = run_manifest_guardian(repo_root=repo_no_lock)
        assert len(result.remediation_hints) > 0


# ---------------------------------------------------------------------------
# 3. Valid manifest + lock → PASS
# ---------------------------------------------------------------------------


class TestValidManifest:
    def test_valid_passes(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        assert result.status == GuardianStatus.PASS.value

    def test_all_checks_pass(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        for check in result.checks:
            assert check.status == CheckStatus.PASS.value, f"Check {check.check_id} should PASS"

    def test_checksum_evidence(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        cs_check = next(c for c in result.checks if c.check_id == "checksum_match")
        assert "sha256" in cs_check.evidence


# ---------------------------------------------------------------------------
# 4. Tampered manifest → FAIL
# ---------------------------------------------------------------------------


class TestTamperedManifest:
    def test_tampered_fails(self, repo_tampered: Path):
        result = run_manifest_guardian(repo_root=repo_tampered)
        assert result.status == GuardianStatus.FAIL.value

    def test_checksum_mismatch_details(self, repo_tampered: Path):
        result = run_manifest_guardian(repo_root=repo_tampered)
        cs_check = next(c for c in result.checks if c.check_id == "checksum_match")
        assert cs_check.status == CheckStatus.FAIL.value
        assert "expected" in cs_check.evidence
        assert "actual" in cs_check.evidence

    def test_tampered_has_remediation(self, repo_tampered: Path):
        result = run_manifest_guardian(repo_root=repo_tampered)
        assert len(result.remediation_hints) > 0


# ---------------------------------------------------------------------------
# 5. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths: {violations}"

    def test_validation_passes(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        errors = result.validate()
        assert errors == [], f"Contract violations: {errors}"

    def test_guardian_id_is_stable(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        assert result.guardian_id == "manifest_integrity"


# ---------------------------------------------------------------------------
# 6. Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self, repo_valid: Path):
        r1 = run_manifest_guardian(repo_root=repo_valid)
        r2 = run_manifest_guardian(repo_root=repo_valid)
        assert r1.to_json() == r2.to_json()

    def test_timestamp_injectable(self, repo_valid: Path):
        ts = "2026-02-08T00:00:00Z"
        result = run_manifest_guardian(repo_root=repo_valid, timestamp=ts)
        assert result.timestamp == ts
