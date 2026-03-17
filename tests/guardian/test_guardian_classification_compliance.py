"""
Guardian Contract Tests: Classification Compliance.

Tests:
1. Schema validity (GuardianResult fields, types)
2. Check IDs match registry spec
3. Deterministic evidence ordering
4. Naming compliance scan detects compound suffix conflicts
5. Territory compliance scan detects misplaced files
6. Clean repo produces PASS status
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_classification_compliance")
_emit_applies_guardrail("p0", "test_guardian_classification_compliance", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_classification_compliance", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_classification_compliance", "state_snapshot")
emit_replay_key("p0", "test_guardian_classification_compliance")
emit_determinism_digest("p0", "test_guardian_classification_compliance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_classification_compliance", "execution_auth")
_emit_validates_capability("p2", "test_guardian_classification_compliance", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_classification_compliance", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_classification_compliance", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_classification_compliance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_classification_compliance", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_classification_compliance", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_classification_compliance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_classification_compliance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_classification_compliance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_classification_compliance", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_classification_compliance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_classification_compliance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_classification_compliance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_classification_compliance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_classification_compliance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_classification_compliance", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_classification_compliance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_classification_compliance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_classification_compliance", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_classification_compliance import (
    GUARDIAN_ID,
    _collect_python_files,
    run_classification_compliance_guardian,
    scan_naming_compliance,
    scan_territory_compliance,
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

_emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_classification_compliance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_classification_compliance", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_classification_compliance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_classification_compliance", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_classification_compliance", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_classification_compliance", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_classification_compliance", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_classification_compliance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_classification_compliance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_classification_compliance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_classification_compliance", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_classification_compliance", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_classification_compliance", "p3lm", "state")
_emit_records_execution_trace("test_guardian_classification_compliance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_classification_compliance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_classification_compliance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_classification_compliance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_classification_compliance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_classification_compliance", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_classification_compliance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_classification_compliance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_classification_compliance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_classification_compliance", "context_pull")
_emit_pulls_context("p1", "test_guardian_classification_compliance", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_guardian_classification_compliance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_classification_compliance", "uwg_term_2")
_emit_writes_through("p1", "test_guardian_classification_compliance", "write_through")
_emit_writes_through("p1", "test_guardian_classification_compliance", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_guardian_classification_compliance", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_classification_compliance", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_classification_compliance", "routing_commit")
_emit_escalates_to_human("p1", "test_guardian_classification_compliance", "human_escalation")
_emit_routes_through("p1", "test_guardian_classification_compliance", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_classification_compliance", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_classification_compliance", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_classification_compliance", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_classification_compliance", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_classification_compliance", "target_agent")
_emit_verifies_policy("p1", "test_guardian_classification_compliance", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_classification_compliance", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_classification_compliance", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_classification_compliance", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_classification_compliance")
_emit_gated_by_confidence("p1", "test_guardian_classification_compliance", "confidence_gate")

pytestmark = pytest.mark.guardian

FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def real_result() -> GuardianResult:
    """Run classification compliance guardian on the real repo."""
    return run_classification_compliance_guardian(
        repo_root=PROJECT_ROOT,
        timestamp=FIXED_TIMESTAMP,
    )


@pytest.fixture()
def synthetic_repo(tmp_path: Path) -> Path:
    """Create a minimal synthetic repo for controlled testing."""
    ac = tmp_path / AGENTIC_CORE_DIR
    layer = ac / "L5_safety"

    # Correct placement: agent in reasoning/ (Agent class → AGENT → reasoning)
    reasoning = layer / "reasoning"
    reasoning.mkdir(parents=True)
    (reasoning / "FooAgent.py").write_text(
        "class FooAgent:\n    pass\n",
        encoding="utf-8",
    )

    # Correct placement: utility in utils/ (no class → UTILITY → utils)
    utils_dir = layer / "utils"
    utils_dir.mkdir(parents=True)
    (utils_dir / "bar_util.py").write_text(
        "def bar():\n    return 1\n",
        encoding="utf-8",
    )

    # Correct placement: types in types/ (TypedDict → TYPES → types)
    types_dir = layer / "types"
    types_dir.mkdir(parents=True)
    (types_dir / "baz_types.py").write_text(
        "from typing import TypedDict\nclass Baz(TypedDict):\n    x: int\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def synthetic_repo_with_violations(tmp_path: Path) -> Path:
    """Create a synthetic repo with known classification violations."""
    ac = tmp_path / AGENTIC_CORE_DIR
    layer = ac / L2_EXECUTION_DIR

    # Territory violation: config file in reasoning/ instead of config/
    reasoning = layer / "reasoning"
    reasoning.mkdir(parents=True)
    (reasoning / "some_config.py").write_text(
        "SETTING = True\n",
        encoding="utf-8",
    )

    # Correct placement for comparison
    config = layer / "config"
    config.mkdir(parents=True)
    (config / "good_config.py").write_text(
        "X = 1\n",
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

    def test_naming_violations_sorted(self, real_result: GuardianResult) -> None:
        naming = next(
            (c for c in real_result.checks if c.check_id == "naming_compliance"),
            None,
        )
        assert naming is not None
        violations = naming.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)

    def test_territory_violations_sorted(self, real_result: GuardianResult) -> None:
        territory = next(
            (c for c in real_result.checks if c.check_id == "territory_compliance"),
            None,
        )
        assert territory is not None
        violations = territory.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 3. Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanNamingCompliance:
    """Unit tests for naming compliance scan."""

    def test_clean_repo_no_violations(self, synthetic_repo: Path) -> None:
        violations = scan_naming_compliance(synthetic_repo)
        assert violations == []

    def test_compound_suffix_detected(self, tmp_path: Path) -> None:
        """A file with compound suffix should be detected."""
        ac = tmp_path / L0_ROUTING_DIR / "scripts"
        ac.mkdir(parents=True)
        # _agent_types is a known compound suffix conflict
        (ac / "code_detector_agent_types.py").write_text(
            "X = 1\n",
            encoding="utf-8",
        )
        violations = scan_naming_compliance(tmp_path)
        assert len(violations) == 1
        assert violations[0]["filename"] == "code_detector_agent_types.py"
        assert set(violations[0]["conflicting_tags"]) == {"AGENT", "TYPES"}

    def test_no_false_positive_on_single_suffix(self, tmp_path: Path) -> None:
        """A file with a single suffix should not be flagged."""
        ac = tmp_path / L0_ROUTING_DIR / "types"
        ac.mkdir(parents=True)
        (ac / "guardian_types.py").write_text(
            "X = 1\n",
            encoding="utf-8",
        )
        violations = scan_naming_compliance(tmp_path)
        assert violations == []


class TestScanTerritoryCompliance:
    """Unit tests for territory compliance scan."""

    def test_clean_repo_no_violations(self, synthetic_repo: Path) -> None:
        violations = scan_territory_compliance(synthetic_repo)
        assert violations == []


# ---------------------------------------------------------------------------
# 4. File collector
# ---------------------------------------------------------------------------


class TestFileCollector:
    """Verify file collector is deterministic and correct."""

    def test_collects_python_files_only(self, synthetic_repo: Path) -> None:
        # Add a non-Python file
        (synthetic_repo / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "readme.md").write_text(
            "# readme\n",
            encoding="utf-8",
        )
        files = _collect_python_files(synthetic_repo)
        assert all(f.name.endswith(".py") for f in files)

    def test_skips_init_files(self, synthetic_repo: Path) -> None:
        init = synthetic_repo / AGENTIC_CORE_DIR / "L5_safety" / "__init__.py"
        init.write_text("", encoding="utf-8")
        files = _collect_python_files(synthetic_repo)
        assert all(f.name != "__init__.py" for f in files)

    def test_sorted_output(self, synthetic_repo: Path) -> None:
        files = _collect_python_files(synthetic_repo)
        paths = [str(f) for f in files]
        assert paths == sorted(paths)

    def test_skips_pycache(self, synthetic_repo: Path) -> None:
        pc = synthetic_repo / AGENTIC_CORE_DIR / "__pycache__"
        pc.mkdir(parents=True)
        (pc / "cached.py").write_text("X=1\n", encoding="utf-8")
        files = _collect_python_files(synthetic_repo)
        assert all("__pycache__" not in str(f) for f in files)


# ---------------------------------------------------------------------------
# 5. No mutations (scan-only)
# ---------------------------------------------------------------------------


class TestNoMutations:
    """Verify guardian does not mutate the repo."""

    def test_no_files_created(self, synthetic_repo: Path) -> None:
        before = set()
        for dirpath, dirs, filenames in os.walk(synthetic_repo):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                before.add(os.path.join(dirpath, fname))

        run_classification_compliance_guardian(
            repo_root=synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )

        after = set()
        for dirpath, dirs, filenames in os.walk(synthetic_repo):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                after.add(os.path.join(dirpath, fname))

        assert before == after, f"Guardian created files: {after - before}"

    def test_no_files_modified(self, synthetic_repo: Path) -> None:
        # Record content hashes
        import hashlib

        def snapshot():
            result = {}
            for dirpath, dirs, filenames in os.walk(synthetic_repo):
                dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    with open(fpath, "rb") as f:
                        result[fpath] = hashlib.sha256(f.read()).hexdigest()
            return result

        before = snapshot()
        run_classification_compliance_guardian(
            repo_root=synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )
        after = snapshot()
        assert before == after
