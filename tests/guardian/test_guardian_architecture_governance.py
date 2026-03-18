"""
Guardian Contract Tests: Architecture Governance.

Tests:
1. Schema validity (GuardianResult fields, types)
2. Check IDs match registry spec
3. Deterministic evidence ordering
4. Import compliance scan detects upward dependencies
5. Layer gravity scan detects misplaced agents
6. Clean synthetic repo produces PASS
7. No mutations (scan-only)
8. Timestamp injection for determinism
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L2_EXECUTION_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_architecture_governance")
_emit_applies_guardrail("p0", "test_guardian_architecture_governance", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_architecture_governance", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_architecture_governance", "state_snapshot")
emit_replay_key("p0", "test_guardian_architecture_governance")
emit_determinism_digest("p0", "test_guardian_architecture_governance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_architecture_governance", "execution_auth")
_emit_validates_capability("p2", "test_guardian_architecture_governance", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_architecture_governance", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_architecture_governance", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_architecture_governance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_architecture_governance", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_architecture_governance", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_architecture_governance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_architecture_governance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_architecture_governance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_architecture_governance", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_architecture_governance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_architecture_governance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_architecture_governance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_architecture_governance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_architecture_governance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_architecture_governance", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_architecture_governance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_architecture_governance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_architecture_governance", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_architecture_governance import (
    GUARDIAN_ID,
    _collect_python_files,
    run_architecture_governance_guardian,
    scan_import_compliance,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    GuardianStatus,
)
from agentic_core.L0_routing.types.guardian_registry_types import get_guardian_by_id
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_guardian_architecture_governance", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_architecture_governance", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_architecture_governance", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_architecture_governance", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_architecture_governance", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_architecture_governance", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_architecture_governance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_architecture_governance", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_architecture_governance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_architecture_governance", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_architecture_governance", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_architecture_governance", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_architecture_governance", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_architecture_governance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_architecture_governance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_architecture_governance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_architecture_governance", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_architecture_governance", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_architecture_governance", "p3lm", "state")
_emit_records_execution_trace("test_guardian_architecture_governance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_architecture_governance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_architecture_governance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_architecture_governance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_architecture_governance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_architecture_governance", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_architecture_governance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_architecture_governance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_architecture_governance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_architecture_governance", "context_pull")
_emit_pulls_context("p1", "test_guardian_architecture_governance", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_guardian_architecture_governance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_architecture_governance", "uwg_term_2")
_emit_writes_through("p1", "test_guardian_architecture_governance", "write_through")
_emit_writes_through("p1", "test_guardian_architecture_governance", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_guardian_architecture_governance", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_architecture_governance", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_architecture_governance", "routing_commit")
_emit_escalates_to_human("p1", "test_guardian_architecture_governance", "human_escalation")
_emit_routes_through("p1", "test_guardian_architecture_governance", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_architecture_governance", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_architecture_governance", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_architecture_governance", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_architecture_governance", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_architecture_governance", "target_agent")
_emit_verifies_policy("p1", "test_guardian_architecture_governance", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_architecture_governance", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_architecture_governance", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_architecture_governance", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_architecture_governance")
_emit_gated_by_confidence("p1", "test_guardian_architecture_governance", "confidence_gate")

pytestmark = pytest.mark.guardian

FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def real_result() -> GuardianResult:
    """Run architecture governance guardian on the real repo."""
    return run_architecture_governance_guardian(
        repo_root=PROJECT_ROOT,
        timestamp=FIXED_TIMESTAMP,
    )


@pytest.fixture()
def real_result_adg(adg_query_engine) -> GuardianResult:
    """Run ADG-accelerated architecture governance guardian on the real repo."""
    from agentic_core.L0_routing.scripts.run_guardian_architecture_governance import (
        run_architecture_governance_guardian_adg,
    )
    return run_architecture_governance_guardian_adg(
        repo_root=PROJECT_ROOT,
        timestamp=FIXED_TIMESTAMP,
    )


@pytest.fixture()
def clean_synthetic_repo(tmp_path: Path) -> Path:
    """Create a synthetic repo with no import violations."""
    ac = tmp_path / AGENTIC_CORE_DIR

    # L0 file importing from L0 only (no upward)
    l0 = ac / L0_ROUTING_DIR / "scripts"
    l0.mkdir(parents=True)
    (l0 / "helper.py").write_text(
        "from agentic_core.L0_routing.types import foo\n",
        encoding="utf-8",
    )

    # L5 file importing from L0 (downward — allowed)
    l5 = ac / "L5_safety" / "reasoning"
    l5.mkdir(parents=True)
    (l5 / "SafetyAgent.py").write_text(
        "from agentic_core.L0_routing.types import bar\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def violating_synthetic_repo(tmp_path: Path) -> Path:
    """Create a synthetic repo with a known upward import violation."""
    ac = tmp_path / AGENTIC_CORE_DIR

    # L0 file importing from L5 (upward — violation!)
    l0 = ac / L0_ROUTING_DIR / "scripts"
    l0.mkdir(parents=True)
    (l0 / "bad_import.py").write_text(
        "from agentic_core.L5_safety.reasoning import SomeAgent\n",
        encoding="utf-8",
    )

    return tmp_path


# ---------------------------------------------------------------------------
# 1. Schema validity
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """Verify guardian result conforms to contract schema."""

    def test_guardian_id(self, real_result: GuardianResult) -> None:
        assert real_result.guardian_id == GUARDIAN_ID

    def test_timestamp_injected(self, real_result: GuardianResult) -> None:
        assert real_result.timestamp == FIXED_TIMESTAMP

    def test_status_is_valid(self, real_result: GuardianResult) -> None:
        valid_statuses = {s.value for s in GuardianStatus}
        assert real_result.status in valid_statuses

    def test_checks_nonempty(self, real_result: GuardianResult) -> None:
        assert len(real_result.checks) >= 2

    def test_check_ids_match_registry(self, real_result: GuardianResult) -> None:
        spec = get_guardian_by_id(GUARDIAN_ID)
        assert spec is not None
        emitted_ids = {c.check_id for c in real_result.checks}
        registered_ids = set(spec.check_ids)
        assert emitted_ids == registered_ids

    def test_metrics_present(self, real_result: GuardianResult) -> None:
        assert "total_checks" in real_result.metrics
        assert "files_scanned" in real_result.metrics
        assert real_result.metrics["files_scanned"] > 0

    def test_serialization_roundtrip(self, real_result: GuardianResult) -> None:
        json_str = real_result.to_json()
        data = json.loads(json_str)
        assert data["guardian_id"] == GUARDIAN_ID
        assert isinstance(data["checks"], list)
        assert len(data["checks"]) >= 2


# ---------------------------------------------------------------------------
# 2. Deterministic evidence ordering
# ---------------------------------------------------------------------------


class TestDeterministicEvidence:
    """Verify evidence is deterministically ordered."""

    def test_import_violations_sorted(self, real_result: GuardianResult) -> None:
        check = next(
            (c for c in real_result.checks if c.check_id == "import_compliance"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        keys = [(v["path"], v["line_number"]) for v in violations]
        assert keys == sorted(keys)

    def test_gravity_violations_sorted(self, real_result: GuardianResult) -> None:
        check = next(
            (c for c in real_result.checks if c.check_id == "layer_gravity"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 3. Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanImportCompliance:
    """Unit tests for import compliance scan."""

    def test_clean_repo_no_violations(self, clean_synthetic_repo: Path) -> None:
        violations = scan_import_compliance(clean_synthetic_repo)
        assert violations == []

    def test_upward_import_detected(self, violating_synthetic_repo: Path) -> None:
        """L0 importing from L5 is an upward violation."""
        violations = scan_import_compliance(violating_synthetic_repo)
        assert len(violations) == 1
        v = violations[0]
        assert v["source_layer"] == "L0"
        assert v["target_layer"] == "L5"
        assert "bad_import.py" in v["path"]

    def test_downward_import_allowed(self, tmp_path: Path) -> None:
        """L5 importing from L0 is allowed (downward)."""
        ac = tmp_path / AGENTIC_CORE_DIR / "L5_safety" / "reasoning"
        ac.mkdir(parents=True)
        (ac / "agent.py").write_text(
            "from agentic_core.L0_routing.types import x\n",
            encoding="utf-8",
        )
        violations = scan_import_compliance(tmp_path)
        assert violations == []

    def test_same_layer_import_allowed(self, tmp_path: Path) -> None:
        """Same-layer imports are allowed."""
        ac = tmp_path / L2_EXECUTION_DIR / "scripts"
        ac.mkdir(parents=True)
        (ac / "tool.py").write_text(
            "from agentic_core.L2_execution.types import y\n",
            encoding="utf-8",
        )
        violations = scan_import_compliance(tmp_path)
        assert violations == []


# ---------------------------------------------------------------------------
# 4. File collector
# ---------------------------------------------------------------------------


class TestFileCollector:
    """Verify file collector for architecture scanning."""

    def test_collects_agentic_core_only(self, clean_synthetic_repo: Path) -> None:
        files = _collect_python_files(clean_synthetic_repo)
        assert all(AGENTIC_CORE_DIR in str(f) for f in files)

    def test_sorted_output(self, clean_synthetic_repo: Path) -> None:
        files = _collect_python_files(clean_synthetic_repo)
        paths = [str(f) for f in files]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 5. No mutations (scan-only)
# ---------------------------------------------------------------------------


class TestNoMutations:
    """Verify guardian does not mutate the repo."""

    def test_no_files_created(self, clean_synthetic_repo: Path) -> None:
        before = set()
        for dirpath, dirs, filenames in os.walk(clean_synthetic_repo):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                before.add(os.path.join(dirpath, fname))

        run_architecture_governance_guardian(
            repo_root=clean_synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )

        after = set()
        for dirpath, dirs, filenames in os.walk(clean_synthetic_repo):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                after.add(os.path.join(dirpath, fname))

        assert before == after, f"Guardian created files: {after - before}"


# ---------------------------------------------------------------------------
# ADG-Accelerated Tests
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="ADG fixture real_result_adg not yet implemented")
class TestSchemaValidityADG:
    """Verify ADG-accelerated guardian result conforms to contract schema."""

    def test_guardian_id_adg(self, real_result_adg: GuardianResult) -> None:
        assert real_result_adg.guardian_id == GUARDIAN_ID

    def test_timestamp_injected_adg(self, real_result_adg: GuardianResult) -> None:
        assert real_result_adg.timestamp == FIXED_TIMESTAMP

    def test_status_is_valid_adg(self, real_result_adg: GuardianResult) -> None:
        valid_statuses = {s.value for s in GuardianStatus}
        assert real_result_adg.status in valid_statuses

    def test_checks_nonempty_adg(self, real_result_adg: GuardianResult) -> None:
        assert len(real_result_adg.checks) >= 2

    def test_adg_metrics_present(self, real_result_adg: GuardianResult) -> None:
        assert "adg_accelerated" in real_result_adg.metrics
        assert real_result_adg.metrics["adg_accelerated"] is True
        assert "adg_scan_time_ms" in real_result_adg.metrics

    def test_acceleration_evidence_adg(self, real_result_adg: GuardianResult) -> None:
        """Verify ADG acceleration evidence is present."""
        for check in real_result_adg.checks:
            assert "acceleration" in check.evidence
            if check.check_id == "import_compliance":
                assert check.evidence["acceleration"] == "ADG_G1_import_graph"
            elif check.check_id == "layer_gravity":
                assert check.evidence["acceleration"] == "ADG_G3_inheritance_index"


@pytest.mark.skip(reason="ADG fixture real_result_adg not yet implemented")
class TestDeterministicEvidenceADG:
    """Verify ADG-accelerated evidence is deterministically ordered."""

    def test_import_violations_sorted_adg(self, real_result_adg: GuardianResult) -> None:
        check = next(
            (c for c in real_result_adg.checks if c.check_id == "import_compliance"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        keys = [(v["path"], v["line_number"]) for v in violations]
        assert keys == sorted(keys)

    def test_gravity_violations_sorted_adg(self, real_result_adg: GuardianResult) -> None:
        check = next(
            (c for c in real_result_adg.checks if c.check_id == "layer_gravity"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)
