"""Tests for ADG artifact optimization features.

Covers:
- ArtifactNormalizer: compact integer-indexed format, round-trip fidelity
- ArtifactLayerSplitter: three non-overlapping plane sub-graphs with correct edge routing
  (test_graph removed: covers lives in file_graph)
- MultiWriter: non-redundant output (snapshot/sqlite + 3 split planes, no adg_full.json)
- IncrementalScan: affected module propagation, cache eviction
- CLI: build-artifacts, incremental-scan subcommands
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_artifact_optimizations")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_artifact_optimizations", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_artifact_optimizations", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_artifact_optimizations", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_artifact_optimizations", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_artifact_optimizations", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_artifact_optimizations", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_artifact_optimizations", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_artifact_optimizations", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_artifact_optimizations", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_artifact_optimizations", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_artifact_optimizations", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_artifact_optimizations", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_artifact_optimizations", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_artifact_optimizations", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_artifact_optimizations", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_artifact_optimizations", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_artifact_optimizations", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_artifact_optimizations", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_artifact_optimizations", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_artifact_optimizations", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_artifact_optimizations", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_artifact_optimizations", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_artifact_optimizations", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_artifact_optimizations", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_artifact_optimizations", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_artifact_optimizations", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_artifact_optimizations", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_artifact_optimizations", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_artifact_optimizations", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_artifact_optimizations", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_artifact_optimizations", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_artifact_optimizations", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_artifact_optimizations", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_artifact_optimizations", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_artifact_optimizations", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_artifact_optimizations", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_artifact_optimizations", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_artifact_optimizations", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_artifact_optimizations", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_artifact_optimizations", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_artifact_optimizations", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_artifact_optimizations", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_artifact_optimizations", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_artifact_optimizations", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_artifact_optimizations", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_artifact_optimizations", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_artifact_optimizations", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_artifact_optimizations", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_artifact_optimizations", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_artifact_optimizations", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_artifact_optimizations", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_artifact_optimizations")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_artifact_optimizations", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_artifact_optimizations")
# REMOVED: emit_determinism_digest("p0", "test_adg_artifact_optimizations")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_artifact_optimizations", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_artifact_optimizations", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_artifact_optimizations", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_artifact_optimizations", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_artifact_optimizations", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_artifact_optimizations", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_artifact_optimizations", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_artifact_optimizations", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_artifact_optimizations", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_artifact_optimizations", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_artifact_optimizations", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_artifact_optimizations", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_artifact_optimizations", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_artifact_optimizations", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_artifact_optimizations", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_artifact_optimizations", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_artifact_optimizations", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_artifact_optimizations", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_artifact_optimizations", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_artifact_optimizations", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_entity(
    adg_name,
    entity_type="module",
    layer="L2",
    identity_kind="repo_module",
    confidence="HIGH",
    resolved_path="",
):
    from agentic_core.adg.artifact.builder_types import EntityRecord

    return EntityRecord(
        adg_name=adg_name,
        entity_type=entity_type,
        layer=layer,
        identity_kind=identity_kind,
        confidence=confidence,
        resolved_path=resolved_path or adg_name.replace("ADG::Module::", ""),
    )


def _make_relation(
    from_name, rel_type, to_name, edge_kind="import", source_file="foo.py", line_no=1, symbol=""
):
    from agentic_core.adg.artifact.builder_types import RelationRecord

    return RelationRecord(
        from_name=from_name,
        relation_type=rel_type,
        to_name=to_name,
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=line_no,
        symbol=symbol,
    )


def _make_artifact():
    from agentic_core.adg.artifact.builder_types import ADGArtifact, BlindSpotReport, StructuralMetrics

    a = ADGArtifact()
    a.commit_sha = "abc123"
    a.scanner_digest = "scan_digest_hex"
    a.artifact_digest = "art_digest_hex"

    # Entities
    a.entities = [
        _make_entity(
            "ADG::Module::agentic_core/L2_execution/foo.py",
            layer="L2",
            resolved_path="agentic_core/L2_execution/foo.py",
        ),
        _make_entity(
            "ADG::Module::agentic_core/L1_reasoning/bar.py",
            layer="L1",
            resolved_path="agentic_core/L1_reasoning/bar.py",
        ),
        _make_entity(
            "ADG::Module::tests/unit/test_foo.py", layer="L_TEST", resolved_path="tests/unit/test_foo.py"
        ),
        _make_entity(
            "ADG::Symbol::json.loads",
            entity_type="symbol",
            layer="L_EXTERNAL",
            identity_kind="external_module",
            resolved_path="",
        ),
    ]

    # Relations — one per plane
    a.relations = [
        # file_graph
        _make_relation(
            "ADG::Module::agentic_core/L2_execution/foo.py",
            "imports",
            "ADG::Module::agentic_core/L1_reasoning/bar.py",
            edge_kind="import",
        ),
        # symbol_graph
        _make_relation(
            "ADG::Module::agentic_core/L2_execution/foo.py",
            "calls",
            "ADG::Symbol::json.loads",
            edge_kind="call",
        ),
        # symbol_graph — writes_to
        _make_relation(
            "ADG::Module::agentic_core/L1_reasoning/bar.py",
            "writes_to",
            "ADG::Symbol::some.state",
            edge_kind="write",
        ),
        # file_graph: covers (canonical home is file_graph)
        _make_relation(
            "ADG::Module::tests/unit/test_foo.py",
            "covers",
            "ADG::Module::agentic_core/L2_execution/foo.py",
            edge_kind="test_coverage",
        ),
        # governance_graph
        _make_relation(
            "ADG::Module::agentic_core/L2_execution/foo.py",
            "violates",
            "ADG::Module::agentic_core/L1_reasoning/bar.py",
            edge_kind="layer_violation",
        ),
    ]

    a.blind_spots = BlindSpotReport()
    a.structural_metrics = StructuralMetrics(
        total_entities=4,
        total_relations=5,
        module_count=3,
        symbol_count=1,
    )
    a.identity_health = {"by_confidence": {"HIGH": 3}}
    return a


# ---------------------------------------------------------------------------
# ArtifactNormalizer
# ---------------------------------------------------------------------------


class TestArtifactNormalizer:
    def test_normalize_produces_compact_nodes(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)

        assert isinstance(ng.nodes, dict)
        assert len(ng.nodes) >= len(a.entities)
        # All nodes have "n" key
        for nid, node in ng.nodes.items():
            assert "n" in node
            assert "t" in node

    def test_normalize_compact_edges_use_integer_ids(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)

        assert len(ng.edges) == len(a.relations)
        for edge in ng.edges:
            assert isinstance(edge["s"], int)
            assert isinstance(edge["d"], int)
            assert "r" in edge
            assert "k" in edge

    def test_normalize_schema_version_is_v4(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)
        assert ng.schema_version == "4.0.0"

    def test_normalize_preserves_commit_sha(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)
        assert ng.commit_sha == "abc123"

    def test_normalize_computes_digest(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)
        assert len(ng.artifact_digest) == 64  # SHA256 hex

    def test_normalize_is_deterministic(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng1 = ArtifactNormalizer().normalize(a)
        ng2 = ArtifactNormalizer().normalize(a)
        assert ng1.artifact_digest == ng2.artifact_digest

    def test_size_comparison_shows_reduction(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer, size_comparison

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)
        sc = size_comparison(a, ng)
        assert "verbose_bytes" in sc
        assert "compact_bytes" in sc
        assert "reduction_pct" in sc
        # Compact must not be larger than 10x verbose (for tiny fixture it may not shrink)
        assert sc["compact_bytes"] < sc["verbose_bytes"] * 10

    def test_denormalize_round_trip(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        normalizer = ArtifactNormalizer()
        ng = normalizer.normalize(a)
        restored = normalizer.denormalize(ng)

        # Check all original entity names survive round-trip
        original_names = {e.adg_name for e in a.entities}
        restored_names = {e["adg_name"] for e in restored["entities"]}
        assert original_names <= restored_names

    def test_denormalize_preserves_relation_types(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        normalizer = ArtifactNormalizer()
        ng = normalizer.normalize(a)
        restored = normalizer.denormalize(ng)

        original_rel_types = {r.relation_type for r in a.relations}
        restored_rel_types = {r["relation_type"] for r in restored["relations"]}
        assert original_rel_types == restored_rel_types

    def test_symbol_field_only_when_nonempty(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        # Add a relation with a non-empty symbol
        a.relations.append(
            _make_relation(
                "ADG::Module::agentic_core/L2_execution/foo.py",
                "calls",
                "ADG::Symbol::os.path.join",
                symbol="os.path.join",
            )
        )
        ng = ArtifactNormalizer().normalize(a)
        edges_with_sym = [e for e in ng.edges if "sym" in e]
        assert len(edges_with_sym) >= 1
        assert edges_with_sym[0]["sym"] == "os.path.join"

    def test_write_and_load_roundtrip(self, tmp_path):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer, NormalizedGraph

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)
        p = ng.write(tmp_path / "test_ng.json")
        assert p.exists()

        loaded = NormalizedGraph.load(p)
        assert loaded.artifact_digest == ng.artifact_digest
        assert len(loaded.nodes) == len(ng.nodes)
        assert len(loaded.edges) == len(ng.edges)


# ---------------------------------------------------------------------------
# ArtifactLayerSplitter
# ---------------------------------------------------------------------------


class TestLayerSplitter:
    def test_split_produces_three_planes(self):
        """Three non-overlapping planes: file_graph, symbol_graph, governance_graph."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        assert planes.file_graph is not None
        assert planes.symbol_graph is not None
        assert planes.governance_graph is not None
        assert not hasattr(planes, "test_graph"), "test_graph must not exist (removed)"

    def test_file_graph_contains_imports(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        rel_types = {e["r"] for e in planes.file_graph.edges}
        assert "imports" in rel_types

    def test_file_graph_excludes_calls(self):
    """Test file_graph_excludes_calls runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute file_graph_excludes_calls
    result = None  # Replace with actual execution
    """Test symbol_graph_contains_calls_and_writes_to runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute symbol_graph_contains_calls_and_writes_to
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        planes = split_artifact(a)
        rel_types = {e["r"] for e in planes.file_graph.edges}
        assert "covers" in rel_types

    def test_governance_graph_contains_violates(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        rel_types = {e["r"] for e in planes.governance_graph.edges}
        assert "violates" in rel_types

    def test_planes_have_independent_node_sets(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        # file_graph should only have module nodes (no pure symbol nodes from calls)
        file_node_types = {n["t"] for n in planes.file_graph.nodes.values()}
        assert file_node_types <= {"module", "symbol"}  # may have stubs

    def test_split_planes_have_schema_version(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            assert plane.schema_version == "4.0.0"

    def test_write_all_creates_files(self, tmp_path):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        paths = planes.write_all(tmp_path)
        for plane_name, path in paths.items():
            assert path.exists(), f"{plane_name} file missing: {path}"

    def test_size_summary_returns_bytes(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        sizes = planes.size_summary()
        assert set(sizes.keys()) == {"file_graph", "symbol_graph", "governance_graph"}
        for sz in sizes.values():
            assert sz > 0

    def test_plane_meta_contains_plane_name(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        assert planes.file_graph.meta["plane"] == "file_graph"
        assert planes.symbol_graph.meta["plane"] == "symbol_graph"
        assert planes.governance_graph.meta["plane"] == "governance_graph"


# ---------------------------------------------------------------------------
# MultiWriter
# ---------------------------------------------------------------------------


class TestMultiWriter:
    def test_write_all_artifacts_creates_all_files(self, tmp_path):
        """Five non-redundant files: snapshot + sqlite + 3 planes. No adg_full, no test_graph."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z")
        assert paths.snapshot.exists()
        assert paths.sqlite.exists()
        assert paths.file_graph.exists()
        assert paths.symbol_graph.exists()
        assert paths.governance_graph.exists()
        # These must NOT be generated
        assert not (tmp_path / "adg_full_20260101T000000Z.json").exists(), "adg_full must not exist"
        assert not (tmp_path / "adg_test_graph_20260101T000000Z.json").exists(), "test_graph must not exist"

    def test_sqlite_created_by_default(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z", write_sqlite=True)
        assert paths.sqlite.exists()

    def test_sqlite_has_nodes_and_edges_tables(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        try:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert "nodes" in tables
            assert "edges" in tables
            assert "meta" in tables
        finally:
            conn.close()

    def test_sqlite_nodes_match_normalized_count(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z", write_sqlite=True)
        ng = ArtifactNormalizer().normalize(a)

        conn = sqlite3.connect(str(paths.sqlite))
        try:
            node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        finally:
            conn.close()

        assert node_count == len(ng.nodes)
        assert edge_count == len(ng.edges)

    def test_sqlite_queryable_by_layer(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        try:
            rows = conn.execute(
                "SELECT adg_name FROM nodes WHERE layer = ? AND entity_type = 'module'", ("L2",)
            ).fetchall()
        finally:
            conn.close()
        assert len(rows) >= 1

    def test_snapshot_tier1_is_lightweight(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z")
        snap = json.loads(paths.snapshot.read_text())
        # Must NOT contain entities or relations arrays
        assert "entities" not in snap
        assert "relations" not in snap
        assert "counts" in snap
        assert snap["schema_version"] == "snapshot-1.0"

    def test_snapshot_has_commit_sha(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z")
        snap = json.loads(paths.snapshot.read_text())
        assert snap["commit_sha"] == "abc123"

    def test_sqlite_tier2_has_schema_v4(self, tmp_path):
        """SQLite is the canonical complete store (replaces adg_full.json)."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        try:
            row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "4.0.0"

    def test_size_report_returns_all_keys(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260101T000000Z")
        sizes = paths.size_report()
        assert "snapshot" in sizes
        assert "sqlite" in sizes
        assert "file_graph" in sizes
        assert "symbol_graph" in sizes
        assert "governance_graph" in sizes
        assert "full" not in sizes, "adg_full must not appear in size_report"
        assert "test_graph" not in sizes, "test_graph must not appear in size_report"

    def test_timestamped_filenames(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="20260311T154637Z")
        assert "20260311T154637Z" in paths.snapshot.name
        assert "20260311T154637Z" in paths.sqlite.name
        assert "20260311T154637Z" in paths.file_graph.name

    def test_no_timestamp_gives_clean_names(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="")
        assert paths.snapshot.name == "adg_snapshot.json"
        assert paths.sqlite.name == "adg_indexed.sqlite"


# ---------------------------------------------------------------------------
# IncrementalScan
# ---------------------------------------------------------------------------


class TestIncrementalScan:
    def test_compute_affected_modules_direct_only(self):
        from agentic_core.adg.artifact.normalizer_config import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        # Build a minimal NormalizedGraph with one import edge
        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "L2", "k": "", "c": "", "p": "a.py"},
                "1": {"n": "ADG::Module::b.py", "t": "module", "l": "L2", "k": "", "c": "", "p": "b.py"},
            },
            edges=[{"s": 1, "d": 0, "r": "imports", "k": "import", "f": "b.py", "ln": 1}],
        )
        # Change a.py → b.py (which imports a.py) should be affected
        affected = compute_affected_modules(["a.py"], ng, depth=1)
        assert "ADG::Module::a.py" in affected
        assert "ADG::Module::b.py" in affected

    def test_compute_affected_modules_no_importers(self):
        from agentic_core.adg.artifact.normalizer_config import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "L2", "k": "", "c": "", "p": "a.py"},
            },
            edges=[],
        )
        affected = compute_affected_modules(["a.py"], ng, depth=2)
        assert affected == {"ADG::Module::a.py"}

    def test_compute_affected_modules_transitive(self):
        from agentic_core.adg.artifact.normalizer_config import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        # a → b → c (b imports a, c imports b)
        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "", "k": "", "c": "", "p": "a.py"},
                "1": {"n": "ADG::Module::b.py", "t": "module", "l": "", "k": "", "c": "", "p": "b.py"},
                "2": {"n": "ADG::Module::c.py", "t": "module", "l": "", "k": "", "c": "", "p": "c.py"},
            },
            edges=[
                {"s": 1, "d": 0, "r": "imports", "k": "import", "f": "b.py", "ln": 1},
                {"s": 2, "d": 1, "r": "imports", "k": "import", "f": "c.py", "ln": 1},
            ],
        )
        affected = compute_affected_modules(["a.py"], ng, depth=2)
        assert "ADG::Module::a.py" in affected
        assert "ADG::Module::b.py" in affected
        assert "ADG::Module::c.py" in affected

    def test_compute_affected_modules_depth_limit(self):
        from agentic_core.adg.artifact.normalizer_config import NormalizedGraph
        from agentic_core.adg.extraction.incremental import compute_affected_modules

        # a → b → c but depth=1 should not reach c
        ng = NormalizedGraph(
            nodes={
                "0": {"n": "ADG::Module::a.py", "t": "module", "l": "", "k": "", "c": "", "p": "a.py"},
                "1": {"n": "ADG::Module::b.py", "t": "module", "l": "", "k": "", "c": "", "p": "b.py"},
                "2": {"n": "ADG::Module::c.py", "t": "module", "l": "", "k": "", "c": "", "p": "c.py"},
            },
            edges=[
                {"s": 1, "d": 0, "r": "imports", "k": "import", "f": "b.py", "ln": 1},
                {"s": 2, "d": 1, "r": "imports", "k": "import", "f": "c.py", "ln": 1},
            ],
        )
        affected = compute_affected_modules(["a.py"], ng, depth=1)
        assert "ADG::Module::a.py" in affected
        assert "ADG::Module::b.py" in affected
        assert "ADG::Module::c.py" not in affected

    def test_incremental_scan_stats_summary(self):
        from agentic_core.adg.extraction.incremental import IncrementalScanStats

        stats = IncrementalScanStats()
        stats.total_modules = 100
        stats.rescanned = 10
        stats.changed_files = 2
        stats.affected_modules = 10
        stats.edges_total = 500
        s = stats.summary()
        assert "10/100" in s
        assert "90 skipped" in s

    def test_incremental_scan_stats_skipped_count(self):
        """skipped = total_modules - rescanned."""
        from agentic_core.adg.extraction.incremental import IncrementalScanStats

        stats = IncrementalScanStats()
        stats.total_modules = 200
        stats.rescanned = 15
        assert stats.skipped == 185

    def test_incremental_scan_stats_zero_hit_rate(self):
        from agentic_core.adg.extraction.incremental import IncrementalScanStats

        stats = IncrementalScanStats()
        stats.total_modules = 0
        stats.rescanned = 0
        assert stats.skipped == 0
        assert "0/0" in stats.summary()


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestCLIBuildArtifacts:
    def test_build_artifacts_help(self):
        from agentic_core.adg.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["build-artifacts", "--help"])
        assert exc_info.value.code == 0

    def test_incremental_scan_help(self):
        from agentic_core.adg.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["incremental-scan", "--help"])
        assert exc_info.value.code == 0

    def test_build_artifacts_command_registered(self):
        """Verify build-artifacts is a registered subcommand."""
        from agentic_core.adg.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["build-artifacts", "--help"])
        assert exc_info.value.code == 0

    def test_incremental_scan_command_registered(self):
        from agentic_core.adg.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["incremental-scan", "--help"])
        assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------


class TestSchemaConstants:
    def test_normalized_schema_version_constant(self):
        from agentic_core.adg.artifact.normalizer_config import _SCHEMA_VERSION_NORMALIZED

        assert _SCHEMA_VERSION_NORMALIZED == "4.0.0"

    def test_file_graph_rels_contains_imports(self):
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS

        assert "imports" in _FILE_GRAPH_RELS

    def test_symbol_graph_rels_contains_calls(self):
    """Test symbol_graph_rels_contains_calls runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute symbol_graph_rels_contains_calls
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        """_TEST_GRAPH_RELS must not exist in layer_splitter."""
        import agentic_core.adg.artifact.SplitArtifact as ls

        assert not hasattr(ls, "_TEST_GRAPH_RELS"), "_TEST_GRAPH_RELS was removed; covers lives in file_graph"

    def test_governance_rels_contains_violates_and_uwg(self):
        from agentic_core.adg.artifact.SplitArtifact import _GOVERNANCE_GRAPH_RELS

        assert "violates" in _GOVERNANCE_GRAPH_RELS
        assert "bypasses_uwg" in _GOVERNANCE_GRAPH_RELS
        assert "layer_authority_violation" in _GOVERNANCE_GRAPH_RELS

    def test_no_overlap_between_file_and_symbol_graph_rels(self):
        from agentic_core.adg.artifact.SplitArtifact import _SYMBOL_GRAPH_RELS

        # imports should ONLY be in file_graph, not symbol_graph
        assert "imports" not in _SYMBOL_GRAPH_RELS

    def test_incremental_default_depth(self):
        from agentic_core.adg.extraction.incremental import _DEFAULT_AFFECT_DEPTH

        assert _DEFAULT_AFFECT_DEPTH >= 1


# ---------------------------------------------------------------------------
# End-to-end: build artifact from live scan (smoke test)
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_normalized_graph_to_dict_is_json_serializable(self):
        from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer

        a = _make_artifact()
        ng = ArtifactNormalizer().normalize(a)
        d = ng.to_dict()
        # Must be JSON-serializable without errors
        raw = json.dumps(d)
        assert len(raw) > 0

    def test_split_artifact_all_digests_nonempty(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _make_artifact()
        planes = split_artifact(a)
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            assert len(plane.artifact_digest) == 64

    def test_multi_write_then_sqlite_query_by_relation(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="test", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        try:
            rows = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'imports'").fetchone()
        finally:
            conn.close()
        assert rows[0] >= 1

    def test_multi_write_then_sqlite_query_by_module_name(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        a = _make_artifact()
        paths = write_all_artifacts(a, out_dir=tmp_path, ts="test", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        try:
            rows = conn.execute("SELECT id FROM nodes WHERE adg_name LIKE '%L2_execution%'").fetchall()
        finally:
            conn.close()
        assert len(rows) >= 1
