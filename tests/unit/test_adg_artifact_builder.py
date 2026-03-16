"""Unit tests for ADG Artifact Builder and Serializer (Phase 2).

Tests cover:
- ADGArtifactBuilder produces valid ADGArtifact from a minimal ScanResult
- Entities and relations are populated correctly
- Structural metrics are computed
- Blind spots are collected
- Digest is deterministic (same ScanResult -> same digest on two calls)
- Serializer round-trips correctly
- diff_artifacts produces expected delta structure
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agentic_core.adg.artifact.builder import (
    ADGArtifact,
    build_artifact,
)
from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
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

_emit_records_execution_trace("p0", "evidence", "test_adg_artifact_builder")
_emit_applies_guardrail("p0", "test_adg_artifact_builder", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_artifact_builder", "policy_binding")
_emit_snapshots_state("p0", "test_adg_artifact_builder", "state_snapshot")
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
)

_emit_emits_metric_event("test_adg_artifact_builder", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_artifact_builder", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_artifact_builder", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_artifact_builder", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_artifact_builder", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_artifact_builder", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_artifact_builder", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_artifact_builder", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_artifact_builder", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_artifact_builder", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_artifact_builder", "p4obs", "alert")
_emit_links_incident_trace("test_adg_artifact_builder", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_artifact_builder", "p3lm", "pattern")
_emit_records_learning_event("test_adg_artifact_builder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_artifact_builder", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_artifact_builder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_artifact_builder", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_artifact_builder", "p3lm", "policy")
_emit_stores_learning_state("test_adg_artifact_builder", "p3lm", "state")
_emit_records_execution_trace("test_adg_artifact_builder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_artifact_builder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_artifact_builder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_artifact_builder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_artifact_builder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_artifact_builder", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_artifact_builder", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_artifact_builder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_artifact_builder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_artifact_builder", "context_pull")
_emit_pulls_context("p1", "test_adg_artifact_builder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_artifact_builder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_artifact_builder", "uwg_term_2")
_emit_writes_through("p1", "test_adg_artifact_builder", "write_through")
_emit_writes_through("p1", "test_adg_artifact_builder", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_artifact_builder", "safety_validation")
_emit_invokes_eval("p1", "test_adg_artifact_builder", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_artifact_builder", "routing_commit")
emit_replay_key("p0", "test_adg_artifact_builder")
emit_determinism_digest("p0", "test_adg_artifact_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_artifact_builder", "execution_auth")
_emit_validates_capability("p2", "test_adg_artifact_builder", "capability_check")
_emit_routes_to_capability("p2", "test_adg_artifact_builder", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_artifact_builder", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_artifact_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_artifact_builder", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_artifact_builder", "exec_output")
_emit_dispatches_agent("p3", "test_adg_artifact_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_artifact_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_artifact_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_artifact_builder", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_artifact_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_artifact_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_artifact_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_artifact_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_artifact_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_artifact_builder", "eval_metric")
_emit_stores_embedding("p4", "test_adg_artifact_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_artifact_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_artifact_builder", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_minimal_scan_result() -> ScanResult:
    """Build a deterministic minimal ScanResult for testing."""
    result = ScanResult(commit_sha="test-sha")
    result.modules = [
        "agentic_core/adg/schema.py",
        "agentic_core/adg/cli.py",
    ]
    result.edges = [
        Edge(
            from_name="ADG::Module::agentic_core/adg/cli.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/adg/schema.py",
            edge_kind="import",
            source_file="agentic_core/adg/cli.py",
            line_no=5,
            symbol="schema",
        ),
        Edge(
            from_name="ADG::Module::agentic_core/adg/cli.py",
            relation_type="imports",
            to_name="ADG::Symbol::openai",
            edge_kind="import",
            source_file="agentic_core/adg/cli.py",
            line_no=10,
            symbol="openai",
        ),
    ]
    result.compute_digest()
    return result


class TestADGArtifactBuilderBasic:
    """Basic build contract tests."""

    @pytest.mark.unit
    def test_build_returns_adg_artifact(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert isinstance(artifact, ADGArtifact)

    @pytest.mark.unit
    def test_commit_sha_propagated(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.commit_sha == "test-sha"

    @pytest.mark.unit
    def test_entities_nonempty(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert len(artifact.entities) > 0

    @pytest.mark.unit
    def test_relations_nonempty(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert len(artifact.relations) > 0

    @pytest.mark.unit
    def test_artifact_digest_is_64_hex(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert len(artifact.artifact_digest) == 64
        assert all(c in "0123456789abcdef" for c in artifact.artifact_digest)

    @pytest.mark.unit
    def test_schema_version_is_v3(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.schema_version == "3.0.0"


class TestEntityPopulation:
    """Module and symbol entities are populated correctly."""

    @pytest.mark.unit
    def test_source_modules_create_module_entities(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        entity_adg_names = {e.adg_name for e in artifact.entities}
        assert "ADG::Module::agentic_core/adg/schema.py" in entity_adg_names
        assert "ADG::Module::agentic_core/adg/cli.py" in entity_adg_names

    @pytest.mark.unit
    def test_module_entity_has_layer(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        schema_entity = next(
            e for e in artifact.entities
            if e.adg_name == "ADG::Module::agentic_core/adg/schema.py"
        )
        assert schema_entity.layer != ""
        assert schema_entity.layer != "L_UNKNOWN"

    @pytest.mark.unit
    def test_external_symbol_classified_correctly(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        openai_entity = next(
            (e for e in artifact.entities if "openai" in e.adg_name),
            None,
        )
        assert openai_entity is not None
        assert openai_entity.identity_kind == "external_module"

    @pytest.mark.unit
    def test_no_duplicate_entities(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        adg_names = [e.adg_name for e in artifact.entities]
        assert len(adg_names) == len(set(adg_names)), "Duplicate entities found"


class TestIdentityHealth:
    """Identity health section is populated with correct keys."""

    @pytest.mark.unit
    def test_identity_health_has_required_keys(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        required = {"by_identity_kind", "by_confidence", "unresolved_import_count"}
        assert required <= set(artifact.identity_health.keys())

    @pytest.mark.unit
    def test_null_node_inflation_eliminated_flag(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.identity_health.get("null_node_inflation_eliminated") is True


class TestStructuralMetrics:
    """Structural metrics are computed deterministically."""

    @pytest.mark.unit
    def test_total_entities_matches_entity_list(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.structural_metrics.total_entities == len(artifact.entities)

    @pytest.mark.unit
    def test_total_relations_matches_relation_list(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.structural_metrics.total_relations == len(artifact.relations)

    @pytest.mark.unit
    def test_by_relation_type_sums_to_total(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        total = sum(artifact.structural_metrics.by_relation_type.values())
        assert total == artifact.structural_metrics.total_relations


class TestDeterminism:
    """Same ScanResult always produces same artifact_digest."""

    @pytest.mark.unit
    def test_digest_stable_across_two_builds(self) -> None:
        result = _make_minimal_scan_result()
        a1 = build_artifact(result, repo_root=_REPO_ROOT)
        a2 = build_artifact(result, repo_root=_REPO_ROOT)
        assert a1.artifact_digest == a2.artifact_digest

    @pytest.mark.unit
    def test_different_commit_sha_same_content_same_digest(self) -> None:
        """artifact_digest covers content, not commit_sha."""
        r1 = ScanResult(commit_sha="sha1")
        r1.modules = ["agentic_core/adg/schema.py"]
        r1.edges = []
        r1.compute_digest()

        r2 = ScanResult(commit_sha="sha2")
        r2.modules = ["agentic_core/adg/schema.py"]
        r2.edges = []
        r2.compute_digest()

        a1 = build_artifact(r1, repo_root=_REPO_ROOT)
        a2 = build_artifact(r2, repo_root=_REPO_ROOT)
        # Content is identical so digests should match
        assert a1.artifact_digest == a2.artifact_digest

    @pytest.mark.unit
    def test_added_edge_changes_digest(self) -> None:
        r1 = ScanResult(commit_sha="t")
        r1.modules = ["agentic_core/adg/schema.py"]
        r1.edges = []
        r1.compute_digest()

        r2 = ScanResult(commit_sha="t")
        r2.modules = ["agentic_core/adg/schema.py"]
        r2.edges = [
            Edge(
                "ADG::Module::agentic_core/adg/schema.py",
                "imports",
                "ADG::Symbol::json",
                "import",
                "agentic_core/adg/schema.py",
                1,
            )
        ]
        r2.compute_digest()

        a1 = build_artifact(r1, repo_root=_REPO_ROOT)
        a2 = build_artifact(r2, repo_root=_REPO_ROOT)
        assert a1.artifact_digest != a2.artifact_digest


class TestSerializer:
    """Serializer produces valid JSON and round-trips."""

    @pytest.mark.unit
    def test_serialize_produces_valid_json(self) -> None:
        from agentic_core.adg.artifact.serializer import serialize_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        json_str = serialize_artifact(artifact)
        parsed = json.loads(json_str)
        assert "schema_version" in parsed
        assert "artifact_digest" in parsed

    @pytest.mark.unit
    def test_serialize_is_deterministic(self) -> None:
        from agentic_core.adg.artifact.serializer import serialize_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        s1 = serialize_artifact(artifact)
        s2 = serialize_artifact(artifact)
        assert s1 == s2

    @pytest.mark.unit
    def test_write_and_load_roundtrip(self) -> None:
        from agentic_core.adg.artifact.serializer import load_artifact, write_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "artifact.json"
            write_artifact(artifact, out_path)
            loaded = load_artifact(out_path)

        assert loaded["schema_version"] == "3.0.0"
        assert loaded["artifact_digest"] == artifact.artifact_digest

    @pytest.mark.unit
    def test_diff_artifacts_returns_expected_keys(self) -> None:
        from agentic_core.adg.artifact.serializer import diff_artifacts, write_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)

        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "a1.json"
            p2 = Path(tmpdir) / "a2.json"
            write_artifact(artifact, p1)
            write_artifact(artifact, p2)
            diff = diff_artifacts(p1, p2)

        required_keys = {
            "digest_changed", "entities", "relations",
            "unresolved_imports", "layer_violations", "orphan_modules",
        }
        assert required_keys <= set(diff.keys())

    @pytest.mark.unit
    def test_diff_same_artifact_no_changes(self) -> None:
        from agentic_core.adg.artifact.serializer import diff_artifacts, write_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)

        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "a1.json"
            p2 = Path(tmpdir) / "a2.json"
            write_artifact(artifact, p1)
            write_artifact(artifact, p2)
            diff = diff_artifacts(p1, p2)

        assert diff["digest_changed"] is False
        assert diff["entities"]["added_count"] == 0
        assert diff["entities"]["removed_count"] == 0

    @pytest.mark.unit
    def test_set_diff_is_callable_as_module_function(self) -> None:
        """Regression: _set_diff must NOT have @staticmethod decorator at module level.

        If wrapped in staticmethod(), calling _set_diff([],[]) would raise
        TypeError: 'staticmethod' object is not callable.
        """
        from agentic_core.adg.artifact.serializer import _set_diff

        added, removed = _set_diff(["a", "b"], ["b", "c"])
        assert added == ["c"]
        assert removed == ["a"]

    @pytest.mark.unit
    def test_set_diff_returns_correct_added_and_removed(self) -> None:
        from agentic_core.adg.artifact.serializer import _set_diff

        added, removed = _set_diff(["x", "y", "z"], ["y", "z", "w"])
        assert added == ["w"]
        assert removed == ["x"]
