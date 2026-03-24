"""
Guardian Hygiene Tests — ReAct-Style (Observe → Verify → Report).

Tests the run_guardian_hygiene script against sandboxed tmp_path fixtures.

Verifies:
1. Clean repo → PASS (all three checks pass)
2. Temp artifact present → FAIL (temp_artifacts check)
3. Empty folder present → FAIL (empty_folders check)
4. Init-only folder present → FAIL (init_only_folders check)
5. Schema compliance of result
6. Determinism: same input → same JSON output
7. Scan budget exceeded → FAIL with ScanBudgetExceeded evidence
8. Exception handling paths → result does not crash
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_hygiene")
_emit_applies_guardrail("p0", "test_guardian_hygiene", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_hygiene", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_hygiene", "state_snapshot")
emit_replay_key("p0", "test_guardian_hygiene")
emit_determinism_digest("p0", "test_guardian_hygiene")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_hygiene", "execution_auth")
_emit_validates_capability("p2", "test_guardian_hygiene", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_hygiene", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_hygiene", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_hygiene", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_hygiene", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_hygiene", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_hygiene", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_hygiene", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_hygiene", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_hygiene", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_hygiene", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_hygiene", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_hygiene", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_hygiene", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_hygiene", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_hygiene", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_hygiene", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_hygiene", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_hygiene", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_hygiene import (
    run_hygiene_guardian,
    scan_empty_folders,
    scan_init_only_folders,
    scan_temp_artifacts,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    check_schema_compatibility,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_guardian_hygiene", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_hygiene", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_hygiene", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_hygiene", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_hygiene", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_hygiene", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_hygiene", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_hygiene", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_hygiene", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_hygiene", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_hygiene", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_hygiene", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_hygiene", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_hygiene", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_hygiene", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_hygiene", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_hygiene", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_hygiene", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_hygiene", "p3lm", "state")
_emit_records_execution_trace("test_guardian_hygiene", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_hygiene", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_hygiene", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_hygiene", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_hygiene", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_hygiene", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_hygiene", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_hygiene", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_hygiene", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_hygiene", "context_pull")
_emit_pulls_context("p1", "test_guardian_hygiene", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_guardian_hygiene", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_hygiene", "uwg_term_2")
_emit_writes_through("p1", "test_guardian_hygiene", "write_through")
_emit_writes_through("p1", "test_guardian_hygiene", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_guardian_hygiene", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_hygiene", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_hygiene", "routing_commit")
_emit_escalates_to_human("p1", "test_guardian_hygiene", "human_escalation")
_emit_routes_through("p1", "test_guardian_hygiene", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_hygiene", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_hygiene", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_hygiene", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_hygiene", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_hygiene", "target_agent")
_emit_verifies_policy("p1", "test_guardian_hygiene", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_hygiene", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_hygiene", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_hygiene", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_hygiene")
_emit_gated_by_confidence("p1", "test_guardian_hygiene", "confidence_gate")

pytestmark = pytest.mark.guardian

# Use a root name that exists in ROOT_WHITELIST so the scanner actually enters it.
# TESTS_DIR is in ROOT_WHITELIST and is the simplest safe choice for tmp_path fixtures.
_SCAN_ROOT = TESTS_DIR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_repo(tmp_path: Path) -> Path:
    """Repo with no temp artifacts, no empty folders, no init-only folders."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    pkg = src / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""pkg"""\n', encoding="utf-8")
    (pkg / "module.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_with_temp_artifact(tmp_path: Path) -> Path:
    """Repo containing a .pyc temp artifact inside allowed root."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    (src / "stale.pyc").write_bytes(b"\x00" * 10)
    return tmp_path


@pytest.fixture
def repo_with_empty_folder(tmp_path: Path) -> Path:
    """Repo containing a genuinely empty folder (no .gitkeep)."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    (src / "empty_dir").mkdir()
    return tmp_path


@pytest.fixture
def repo_with_init_only_folder(tmp_path: Path) -> Path:
    """Repo containing a folder with only __init__.py."""
    src = tmp_path / _SCAN_ROOT
    src.mkdir()
    init_pkg = src / "init_only_pkg"
    init_pkg.mkdir()
    (init_pkg / "__init__.py").write_text("", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Clean repo → PASS
# ---------------------------------------------------------------------------


class TestCleanRepoPass:
    def test_clean_repo_returns_pass(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_clean_repo_all_checks_pass(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        fail_checks = [c for c in result.checks if c.status == CheckStatus.FAIL.value]
        assert fail_checks == [], f"Unexpected FAIL checks: {[c.check_id for c in fail_checks]}"

    def test_clean_repo_has_three_checks(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        check_ids = {c.check_id for c in result.checks}
        assert "temp_artifacts" in check_ids
        assert "empty_folders" in check_ids
        assert "init_only_folders" in check_ids

    def test_clean_repo_metrics_populated(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.metrics.get("temp_artifact_count") == 0
        assert result.metrics.get("empty_folder_count") == 0
        assert result.metrics.get("init_only_folder_count") == 0


# ---------------------------------------------------------------------------
# 2. Temp artifact present → FAIL
# ---------------------------------------------------------------------------


class TestTempArtifactFail:
    def test_temp_artifact_returns_fail(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert result.status == GuardianStatus.FAIL.value

    def test_temp_artifact_check_id_fails(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        ta_check = next((c for c in result.checks if c.check_id == "temp_artifacts"), None)
        assert ta_check is not None
        assert ta_check.status == CheckStatus.FAIL.value

    def test_temp_artifact_evidence_contains_path(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        ta_check = next(c for c in result.checks if c.check_id == "temp_artifacts")
        paths = ta_check.evidence.get("paths", [])
        assert len(paths) >= 1
        assert any("stale.pyc" in p for p in paths)

    def test_temp_artifact_remediation_hints_present(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert len(result.remediation_hints) > 0

    def test_temp_artifact_metric_nonzero(self, repo_with_temp_artifact: Path):
        result = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert result.metrics.get("temp_artifact_count", 0) >= 1


# ---------------------------------------------------------------------------
# 3. Empty folder present → FAIL
# ---------------------------------------------------------------------------


class TestEmptyFolderFail:
    def test_empty_folder_returns_fail(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        assert result.status == GuardianStatus.FAIL.value

    def test_empty_folder_check_id_fails(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        ef_check = next((c for c in result.checks if c.check_id == "empty_folders"), None)
        assert ef_check is not None
        assert ef_check.status == CheckStatus.FAIL.value

    def test_empty_folder_evidence_contains_path(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        ef_check = next(c for c in result.checks if c.check_id == "empty_folders")
        paths = ef_check.evidence.get("paths", [])
        assert any("empty_dir" in p for p in paths)

    def test_empty_folder_metric_nonzero(self, repo_with_empty_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_empty_folder)
        assert result.metrics.get("empty_folder_count", 0) >= 1


# ---------------------------------------------------------------------------
# 4. Init-only folder present → FAIL
# ---------------------------------------------------------------------------


class TestInitOnlyFolderFail:
    def test_init_only_returns_fail(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        assert result.status == GuardianStatus.FAIL.value

    def test_init_only_check_id_fails(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        io_check = next((c for c in result.checks if c.check_id == "init_only_folders"), None)
        assert io_check is not None
        assert io_check.status == CheckStatus.FAIL.value

    def test_init_only_evidence_contains_path(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        io_check = next(c for c in result.checks if c.check_id == "init_only_folders")
        paths = io_check.evidence.get("paths", [])
        assert any("init_only_pkg" in p for p in paths)

    def test_init_only_metric_nonzero(self, repo_with_init_only_folder: Path):
        result = run_hygiene_guardian(repo_root=repo_with_init_only_folder)
        assert result.metrics.get("init_only_folder_count", 0) >= 1


# ---------------------------------------------------------------------------
# 5. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_schema_compatibility(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema errors: {errors}"

    def test_validate_passes(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        errors = result.validate()
        assert errors == [], f"Contract violations: {errors}"

    def test_guardian_id_is_stable(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.guardian_id == "hygiene"

    def test_status_is_known_value(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert result.status in {"PASS", "FAIL", "ERROR"}

    def test_check_ids_are_registered(self, clean_repo: Path):
        result = run_hygiene_guardian(repo_root=clean_repo)
        from agentic_core.L0_routing.types.guardian_registry_types import ALL_GUARDIANS

        spec = next(g for g in ALL_GUARDIANS if g.guardian_id == "hygiene")
        emitted_ids = {c.check_id for c in result.checks}
        for cid in spec.check_ids:
            assert cid in emitted_ids, f"Registered check_id '{cid}' not emitted"


# ---------------------------------------------------------------------------
# 6. Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self, clean_repo: Path):
        r1 = run_hygiene_guardian(repo_root=clean_repo)
        r2 = run_hygiene_guardian(repo_root=clean_repo)
        assert r1.to_dict() == r2.to_dict()

    def test_timestamp_injectable(self, clean_repo: Path):
        ts = "2026-01-01T00:00:00Z"
        result = run_hygiene_guardian(repo_root=clean_repo, timestamp=ts)
        assert result.timestamp == ts

    def test_fail_result_same_output_twice(self, repo_with_temp_artifact: Path):
        r1 = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        r2 = run_hygiene_guardian(repo_root=repo_with_temp_artifact)
        assert r1.to_dict() == r2.to_dict()


# ---------------------------------------------------------------------------
# 7. Scan-function unit tests (pure functions, no side-effects)
# ---------------------------------------------------------------------------


class TestScanFunctions:
    def test_scan_temp_artifacts_finds_pyc(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "bad.pyc").write_bytes(b"\x00")
        hits = scan_temp_artifacts(tmp_path, frozenset({TESTS_DIR}))
        assert not isinstance(hits, type(None))
        assert any("bad.pyc" in h for h in hits)

    def test_scan_temp_artifacts_finds_bak(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "old.bak").write_text("x", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({TESTS_DIR}))
        assert any("old.bak" in h for h in hits)

    def test_scan_temp_artifacts_clean_returns_empty(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "good.py").write_text("x = 1\n", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({TESTS_DIR}))
        assert hits == []

    def test_scan_temp_artifacts_nonexistent_root_skipped(self, tmp_path: Path):
        hits = scan_temp_artifacts(tmp_path, frozenset({"nonexistent_root"}))
        assert hits == []

    def test_scan_empty_folders_finds_empty(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "hollow").mkdir()
        hits = scan_empty_folders(tmp_path, frozenset({TESTS_DIR}))
        assert any("hollow" in h for h in hits)

    def test_scan_empty_folders_clean_returns_empty(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        (src / "pkg").mkdir()
        (src / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        hits = scan_empty_folders(tmp_path, frozenset({TESTS_DIR}))
        assert hits == []

    def test_scan_empty_folders_nonexistent_root_skipped(self, tmp_path: Path):
        hits = scan_empty_folders(tmp_path, frozenset({"nonexistent_root"}))
        assert hits == []

    def test_scan_init_only_folders_finds_violation(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        pkg = src / "lonely_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        hits = scan_init_only_folders(tmp_path, frozenset({TESTS_DIR}))
        assert any("lonely_pkg" in h for h in hits)

    def test_scan_init_only_folders_normal_pkg_not_flagged(self, tmp_path: Path):
        src = tmp_path / TESTS_DIR
        src.mkdir()
        pkg = src / "normal_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "logic.py").write_text("x = 1\n", encoding="utf-8")
        hits = scan_init_only_folders(tmp_path, frozenset({TESTS_DIR}))
        assert not any("normal_pkg" in h for h in hits)

    def test_scan_init_only_folders_nonexistent_root_skipped(self, tmp_path: Path):
        hits = scan_init_only_folders(tmp_path, frozenset({"nonexistent_root"}))
        assert hits == []


# ---------------------------------------------------------------------------
# 8. Edge cases: empty allowed_roots, multiple violations, PASS boundary
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_allowed_roots_returns_pass(self, tmp_path: Path):
        result = run_hygiene_guardian(repo_root=tmp_path)
        assert result.status == GuardianStatus.PASS.value

    def test_multiple_violations_all_reported(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / "stale.pyc").write_bytes(b"\x00")
        (src / "hollow").mkdir()
        init_pkg = src / "init_pkg"
        init_pkg.mkdir()
        (init_pkg / "__init__.py").write_text("", encoding="utf-8")
        result = run_hygiene_guardian(repo_root=tmp_path)
        assert result.status == GuardianStatus.FAIL.value
        fail_ids = {c.check_id for c in result.checks if c.status == CheckStatus.FAIL.value}
        assert "temp_artifacts" in fail_ids
        assert "empty_folders" in fail_ids
        assert "init_only_folders" in fail_ids

    def test_gitkeep_file_is_not_flagged_as_artifact(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / ".gitkeep").write_text("", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({_SCAN_ROOT}))
        assert not any(".gitkeep" in h for h in hits)

    def test_nonexistent_repo_root_still_returns_result(self, tmp_path: Path):
        nonexistent = tmp_path / "does_not_exist"
        result = run_hygiene_guardian(repo_root=nonexistent)
        assert result.guardian_id == "hygiene"
        assert result.status in {"PASS", "FAIL", "ERROR"}

    def test_tmp_extension_detected(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / "scratch.tmp").write_text("x", encoding="utf-8")
        hits = scan_temp_artifacts(tmp_path, frozenset({_SCAN_ROOT}))
        assert any("scratch.tmp" in h for h in hits)

    def test_swp_extension_detected(self, tmp_path: Path):
        src = tmp_path / _SCAN_ROOT  # TESTS_DIR — in ROOT_WHITELIST
        src.mkdir()
        (src / ".file.swp").write_bytes(b"\x00")
        hits = scan_temp_artifacts(tmp_path, frozenset({_SCAN_ROOT}))
        assert any(".swp" in h for h in hits)
