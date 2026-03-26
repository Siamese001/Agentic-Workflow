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

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L2_EXECUTION_DIR,
)
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_guardian_classification_compliance")
# REMOVED: _emit_applies_guardrail("p0", "test_guardian_classification_compliance", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_guardian_classification_compliance", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_guardian_classification_compliance", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_guardian_classification_compliance")
# REMOVED: emit_determinism_digest("p0", "test_guardian_classification_compliance")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_guardian_classification_compliance", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_guardian_classification_compliance", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_guardian_classification_compliance", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_guardian_classification_compliance", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_guardian_classification_compliance", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_guardian_classification_compliance", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_guardian_classification_compliance", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_guardian_classification_compliance", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_guardian_classification_compliance", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_guardian_classification_compliance", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_guardian_classification_compliance", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_guardian_classification_compliance", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_guardian_classification_compliance", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_guardian_classification_compliance", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_guardian_classification_compliance", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_guardian_classification_compliance", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_guardian_classification_compliance", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_guardian_classification_compliance", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_guardian_classification_compliance", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_guardian_classification_compliance", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  # MOVED: from agentic_core.L0_routing.scripts.run_guardian_classification_compliance import (
    GUARDIAN_ID,
    _collect_python_files,
    run_classification_compliance_guardian,
    scan_naming_compliance,
    scan_territory_compliance,
)
#  # MOVED: from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    GuardianStatus,
)
#  # MOVED: from agentic_core.L0_routing.types.guardian_registry_types import get_guardian_by_id
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

# REMOVED: _emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_guardian_classification_compliance", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_guardian_classification_compliance", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_guardian_classification_compliance", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_guardian_classification_compliance", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_guardian_classification_compliance", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_guardian_classification_compliance", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_guardian_classification_compliance", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_guardian_classification_compliance", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_guardian_classification_compliance", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_guardian_classification_compliance", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_guardian_classification_compliance", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_guardian_classification_compliance", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_guardian_classification_compliance", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_guardian_classification_compliance", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_guardian_classification_compliance", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_guardian_classification_compliance", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_guardian_classification_compliance", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_guardian_classification_compliance", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_guardian_classification_compliance", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_guardian_classification_compliance", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_guardian_classification_compliance", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_guardian_classification_compliance", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_guardian_classification_compliance", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_guardian_classification_compliance", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_guardian_classification_compliance", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_classification_compliance", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_guardian_classification_compliance", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_guardian_classification_compliance", "write_through")
# REMOVED: _emit_writes_through("p1", "test_guardian_classification_compliance", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_guardian_classification_compliance", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_guardian_classification_compliance", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_guardian_classification_compliance", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_guardian_classification_compliance", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_guardian_classification_compliance", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_guardian_classification_compliance", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_guardian_classification_compliance", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_guardian_classification_compliance", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_guardian_classification_compliance", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_guardian_classification_compliance", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_guardian_classification_compliance", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_guardian_classification_compliance", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_guardian_classification_compliance", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_guardian_classification_compliance", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_guardian_classification_compliance")
# REMOVED: _emit_gated_by_confidence("p1", "test_guardian_classification_compliance", "confidence_gate")

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
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L0_routing.scripts.run_guardian_classification_compliance import (
                from agentic_core.L0_routing.types.guardian_contract_types import (
                from agentic_core.L0_routing.types.guardian_registry_types import get_guardian_by_id
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                assert real_result.guardian_id == GUARDIAN_ID

        assert real_result.guardian_id == GUARDIAN_ID

    def test_timestamp_injected(self, real_result: GuardianResult) -> None:
        assert real_result.timestamp == FIXED_TIMESTAMP

    def test_status_is_valid(self, real_result: GuardianResult) -> None:
        valid_statuses = {s.value for s in GuardianStatus}
        assert real_result.status in valid_statuses

    def test_checks_nonempty(self, real_result: GuardianResult) -> None:
    """Test checks_nonempty contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
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
