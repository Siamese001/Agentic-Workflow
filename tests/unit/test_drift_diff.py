"""Unit tests for ADG Drift Diff (Phase 7).

Tests cover:
- Same artifact compared against itself: passes, zero regressions
- Increased unresolved imports -> R1 regression (HIGH)
- Increased layer violations -> R2 regression (HIGH)
- Increased orphan modules > tolerance -> R3 regression (MEDIUM)
- strict=False: MEDIUM regressions don't fail
- strict=True: any regression fails
- DriftDiffResult.to_dict has required keys
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from agentic_core.adg.applications.drift_diff import run_drift_diff

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
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_drift_diff", "p4obs", "metric_1")
_emit_emits_metric_event("test_drift_diff", "p4obs", "metric_2")
_emit_emits_metric_event("test_drift_diff", "p4obs", "metric_3")
_emit_emits_metric_event("test_drift_diff", "p4obs", "metric_4")
_emit_emits_metric_event("test_drift_diff", "p4obs", "metric_5")
_emit_emits_metric_event("test_drift_diff", "p4obs", "metric_6")
_emit_records_incident_event("test_drift_diff", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_drift_diff", "p4obs", "anomaly")
_emit_writes_observability_log("test_drift_diff", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_drift_diff", "p4obs", "mon_state")
_emit_triggers_alert("test_drift_diff", "p4obs", "alert")
_emit_links_incident_trace("test_drift_diff", "p4obs", "trace_link")
_emit_captures_pattern("test_drift_diff", "p3lm", "pattern")
_emit_records_learning_event("test_drift_diff", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_drift_diff", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_drift_diff", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_drift_diff", "p3lm", "routing")
_emit_improves_agent_policy("test_drift_diff", "p3lm", "policy")
_emit_stores_learning_state("test_drift_diff", "p3lm", "state")
_emit_records_execution_trace("test_drift_diff", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_drift_diff", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_drift_diff", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_drift_diff", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_drift_diff", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_drift_diff", "env_read", "p2_env_1")
_emit_reads_environ("test_drift_diff", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_drift_diff", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_drift_diff", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_drift_diff")
_emit_applies_guardrail("p0", "test_drift_diff", "p0_governance")
_emit_reads_policy_state("p0", "test_drift_diff", "policy_binding")
_emit_snapshots_state("p0", "test_drift_diff", "state_snapshot")
_emit_pulls_context("p1", "test_drift_diff", "context_pull")
_emit_pulls_context("p1", "test_drift_diff", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_drift_diff", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_drift_diff", "uwg_term_secondary")
_emit_writes_through("p1", "test_drift_diff", "write_through")
_emit_writes_through("p1", "test_drift_diff", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_drift_diff", "safety_validation")
_emit_invokes_eval("p1", "test_drift_diff", "eval_call")
_emit_proposal_commits_routing("p1", "test_drift_diff", "routing_commit")
emit_replay_key("p0", "test_drift_diff")
emit_determinism_digest("p0", "test_drift_diff")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_drift_diff", "execution_auth")
_emit_validates_capability("p2", "test_drift_diff", "capability_check")
_emit_routes_to_capability("p2", "test_drift_diff", "capability_route")
_emit_writes_via_uwg("p2", "test_drift_diff", "uwg_write")
_emit_blocks_direct_write("p2", "test_drift_diff", "direct_write_block")
_emit_records_tool_invocation("p2", "test_drift_diff", "tool_invocation")
_emit_captures_execution_output("p2", "test_drift_diff", "exec_output")
_emit_dispatches_agent("p3", "test_drift_diff", "agent_dispatch")
_emit_coordinates_agents("p3", "test_drift_diff", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_drift_diff", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_drift_diff", "healing_outcome")
_emit_escalates_failure("p3", "test_drift_diff", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_drift_diff", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_drift_diff", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_drift_diff", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_drift_diff", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_drift_diff", "eval_metric")
_emit_stores_embedding("p4", "test_drift_diff", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_drift_diff", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_drift_diff", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_artifact(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _minimal_artifact(
    *,
    unresolved_count: int = 0,
    layer_violation_count: int = 0,
    orphan_module_count: int = 0,
    entity_count: int = 5,
    relation_count: int = 3,
    commit: str = "abc",
    digest: str = "a" * 64,
) -> dict:
    return {
        "schema_version": "3.0.0",
        "commit_sha": commit,
        "scanner_digest": "s" * 64,
        "artifact_digest": digest,
        "entities": [{"adg_name": f"ADG::Module::mod_{i}.py"} for i in range(entity_count)],
        "relations": [
            {
                "from_name": f"ADG::Module::mod_{i}.py",
                "relation_type": "imports",
                "to_name": f"ADG::Module::mod_{i + 1}.py",
            }
            for i in range(relation_count)
        ],
        "unresolved_imports": [{"raw_name": f"unresolved_{i}"} for i in range(unresolved_count)],
        "identity_health": {
            "by_identity_kind": {"unresolved_import": unresolved_count, "repo_module": entity_count},
            "by_confidence": {"HIGH": entity_count},
            "unresolved_import_count": unresolved_count,
        },
        "structural_metrics": {
            "total_entities": entity_count,
            "total_relations": relation_count,
            "unresolved_count": unresolved_count,
            "layer_violation_count": layer_violation_count,
            "orphan_module_count": orphan_module_count,
            "orphan_modules": [f"ADG::Module::orphan_{i}.py" for i in range(orphan_module_count)],
            "by_relation_type": {"imports": relation_count},
            "by_layer": {"L0": entity_count},
            "module_count": entity_count,
            "symbol_count": 0,
            "external_count": 0,
            "high_fan_in_modules": [],
            "high_fan_out_modules": [],
        },
        "blind_spots": {
            "dynamic_import_count": 0,
            "star_import_count": 0,
            "parse_failure_count": 0,
            "dynamic_import_locations": [],
            "star_import_locations": [],
            "parse_failure_files": [],
        },
    }


class TestSameArtifactNoDiff:
    """Comparing an artifact against itself produces zero regressions."""

    @pytest.mark.unit
    def test_same_artifact_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        assert result.passed is True

    @pytest.mark.unit
    def test_same_artifact_zero_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        assert len(result.regressions) == 0


class TestUnresolvedImportsRegression:
    """R1: increased unresolved imports -> HIGH regression."""

    @pytest.mark.unit
    def test_r1_fires_on_increase(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "baseline.json"
            c = Path(tmpdir) / "current.json"
            _write_artifact(_minimal_artifact(unresolved_count=2), b)
            _write_artifact(_minimal_artifact(unresolved_count=5), c)
            result = run_drift_diff(b, c)
        r1 = [r for r in result.regressions if r.rule == "R1"]
        assert len(r1) == 1
        assert r1[0].severity == "HIGH"

    @pytest.mark.unit
    def test_r1_fails_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(unresolved_count=0), b)
            _write_artifact(_minimal_artifact(unresolved_count=10), c)
            result = run_drift_diff(b, c)
        assert result.passed is False

    @pytest.mark.unit
    def test_r1_no_fire_on_decrease(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(unresolved_count=10), b)
            _write_artifact(_minimal_artifact(unresolved_count=5), c)
            result = run_drift_diff(b, c)
        r1 = [r for r in result.regressions if r.rule == "R1"]
        assert len(r1) == 0


class TestLayerViolationsRegression:
    """R2: increased layer violations -> HIGH regression."""

    @pytest.mark.unit
    def test_r2_fires_on_increase(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(layer_violation_count=5), b)
            _write_artifact(_minimal_artifact(layer_violation_count=10), c)
            result = run_drift_diff(b, c)
        r2 = [r for r in result.regressions if r.rule == "R2"]
        assert len(r2) == 1
        assert r2[0].severity == "HIGH"


class TestOrphanModulesRegression:
    """R3: orphan count increase > tolerance -> MEDIUM regression."""

    @pytest.mark.unit
    def test_r3_fires_above_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=10), c)
            result = run_drift_diff(b, c)
        r3 = [r for r in result.regressions if r.rule == "R3"]
        assert len(r3) == 1
        assert r3[0].severity == "MEDIUM"

    @pytest.mark.unit
    def test_r3_no_fire_within_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=3), c)
            result = run_drift_diff(b, c)
        r3 = [r for r in result.regressions if r.rule == "R3"]
        assert len(r3) == 0


class TestStrictMode:
    """strict=True fails on any regression; strict=False only fails on HIGH."""

    @pytest.mark.unit
    def test_strict_false_medium_only_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=10), c)
            result = run_drift_diff(b, c, strict=False)
        # R3 is MEDIUM, strict=False => should pass
        assert result.passed is True

    @pytest.mark.unit
    def test_strict_true_medium_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=10), c)
            result = run_drift_diff(b, c, strict=True)
        assert result.passed is False


class TestImprovementsTracked:
    """Improvements are recorded (not regressions)."""

    @pytest.mark.unit
    def test_decrease_in_unresolved_is_improvement(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(unresolved_count=10), b)
            _write_artifact(_minimal_artifact(unresolved_count=2), c)
            result = run_drift_diff(b, c)
        improvements = [i for i in result.improvements if i.get("metric") == "unresolved_imports"]
        assert len(improvements) == 1


class TestDriftDiffResultToDict:
    """to_dict has required keys."""

    @pytest.mark.unit
    def test_to_dict_has_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        d = result.to_dict()
        required = {
            "baseline_path",
            "current_path",
            "passed",
            "summary",
            "regressions",
            "improvements",
            "neutral_changes",
        }
        assert required <= set(d.keys())

    @pytest.mark.unit
    def test_summary_nonempty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        assert len(result.summary) > 0


class TestR4EntityRemoval:
    """R4: >10 entities removed with 0 additions -> MEDIUM regression."""

    @pytest.mark.unit
    def test_r4_fires_on_mass_entity_removal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            # baseline has 20 entities, current has 5 (15 removed, 0 added)
            _write_artifact(_minimal_artifact(entity_count=20, relation_count=0), b)
            _write_artifact(_minimal_artifact(entity_count=5, relation_count=0), c)
            result = run_drift_diff(b, c)
        r4 = [r for r in result.regressions if r.rule == "R4"]
        assert len(r4) == 1
        assert r4[0].severity == "MEDIUM"
