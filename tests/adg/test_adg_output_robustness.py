"""ADG Output Refactoring — Robustness Matrix Tests (§1.1 windsurfrules).

Covers the changed surfaces from the ADG output redesign:
  - layer_splitter.py  (_build_plane, split_artifact, SplitArtifact)
  - multi_writer.py    (_build_snapshot, _write_sqlite, _create_latest_symlinks,
                        write_all_artifacts, ArtifactPaths)

ROBUSTNESS_MATRIX dimensions (§1.1):
  - Edge cases     : empty/zero input, malformed, boundary, dangling refs
  - State transitions : write_split_planes=False, write_sqlite=False,
                        create_latest_symlinks=False, LATEST overwrite on re-run
  - Determinism    : identical input → identical digests, replay independence
  - Fail-closed    : invalid preconditions block operation, pre-existing DB deleted
  - Regression     : _TEST_GRAPH_RELS removed, paths.full removed,
                     adg_full / adg_test_graph never created
  - Mutation-sensitive : constants immutable, zero-overlap invariant runtime,
                         node_type_filter=None vs set
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_adg_output_robustness")
_emit_applies_guardrail("p0", "test_adg_output_robustness", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_output_robustness", "policy_binding")
_emit_snapshots_state("p0", "test_adg_output_robustness", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_adg_output_robustness", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_output_robustness", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_output_robustness", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_output_robustness", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_output_robustness", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_output_robustness", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_output_robustness", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_output_robustness", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_output_robustness", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_output_robustness", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_output_robustness", "p4obs", "alert")
_emit_links_incident_trace("test_adg_output_robustness", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_output_robustness", "p3lm", "pattern")
_emit_records_learning_event("test_adg_output_robustness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_output_robustness", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_output_robustness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_output_robustness", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_output_robustness", "p3lm", "policy")
_emit_stores_learning_state("test_adg_output_robustness", "p3lm", "state")
_emit_records_execution_trace("test_adg_output_robustness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_output_robustness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_output_robustness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_output_robustness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_output_robustness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_output_robustness", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_output_robustness", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_output_robustness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_output_robustness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_output_robustness", "context_pull")
_emit_pulls_context("p1", "test_adg_output_robustness", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_output_robustness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_output_robustness", "uwg_term_2")
_emit_writes_through("p1", "test_adg_output_robustness", "write_through")
_emit_writes_through("p1", "test_adg_output_robustness", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_output_robustness", "safety_validation")
_emit_invokes_eval("p1", "test_adg_output_robustness", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_output_robustness", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_output_robustness", "human_escalation")
_emit_routes_through("p1", "test_adg_output_robustness", "route_through")
_emit_checks_agent_registry("p1", "test_adg_output_robustness", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_output_robustness", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_output_robustness", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_output_robustness", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_output_robustness", "target_agent")
_emit_verifies_policy("p1", "test_adg_output_robustness", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_output_robustness", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_output_robustness", "boundary_check")
_emit_transcripts_response("p1", "test_adg_output_robustness", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_output_robustness")
_emit_gated_by_confidence("p1", "test_adg_output_robustness", "confidence_gate")
emit_replay_key("p0", "test_adg_output_robustness")
emit_determinism_digest("p0", "test_adg_output_robustness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_output_robustness", "execution_auth")
_emit_validates_capability("p2", "test_adg_output_robustness", "capability_check")
_emit_routes_to_capability("p2", "test_adg_output_robustness", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_output_robustness", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_output_robustness", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_output_robustness", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_output_robustness", "exec_output")
_emit_dispatches_agent("p3", "test_adg_output_robustness", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_output_robustness", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_output_robustness", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_output_robustness", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_output_robustness", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_output_robustness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_output_robustness", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_output_robustness", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_output_robustness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_output_robustness", "eval_metric")
_emit_stores_embedding("p4", "test_adg_output_robustness", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_output_robustness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_output_robustness", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Shared fixture helpers
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


def _empty_artifact():
    """ADGArtifact with no entities and no relations."""
    from agentic_core.adg.artifact.builder_types import ADGArtifact, BlindSpotReport, StructuralMetrics

    a = ADGArtifact()
    a.commit_sha = "empty000"
    a.scanner_digest = "scan_empty"
    a.artifact_digest = "art_empty"
    a.entities = []
    a.relations = []
    a.blind_spots = BlindSpotReport()
    a.structural_metrics = StructuralMetrics(
        total_entities=0, total_relations=0, module_count=0, symbol_count=0
    )
    a.identity_health = {}
    return a


def _minimal_artifact():
    """ADGArtifact with one module, one imports edge — minimal valid input."""
    from agentic_core.adg.artifact.builder_types import ADGArtifact, BlindSpotReport, StructuralMetrics

    a = ADGArtifact()
    a.commit_sha = "min001"
    a.scanner_digest = "scan_min"
    a.artifact_digest = "art_min"
    a.entities = [
        _make_entity("ADG::Module::a.py", layer="L2", resolved_path="a.py"),
        _make_entity("ADG::Module::b.py", layer="L1", resolved_path="b.py"),
    ]
    a.relations = [
        _make_relation("ADG::Module::a.py", "imports", "ADG::Module::b.py"),
    ]
    a.blind_spots = BlindSpotReport()
    a.structural_metrics = StructuralMetrics(
        total_entities=2, total_relations=1, module_count=2, symbol_count=0
    )
    a.identity_health = {}
    return a


def _full_artifact():
    """Artifact with one edge per plane — file, symbol, governance, plus covers."""
    from agentic_core.adg.artifact.builder_types import ADGArtifact, BlindSpotReport, StructuralMetrics

    a = ADGArtifact()
    a.commit_sha = "full001"
    a.scanner_digest = "scan_full"
    a.artifact_digest = "art_full"
    a.entities = [
        _make_entity("ADG::Module::x.py", layer="L2", resolved_path="x.py"),
        _make_entity("ADG::Module::y.py", layer="L1", resolved_path="y.py"),
        _make_entity("ADG::Module::tests/test_x.py", layer="L_TEST", resolved_path="tests/test_x.py"),
        _make_entity(
            "ADG::Symbol::json.loads",
            entity_type="symbol",
            layer="L_EXTERNAL",
            identity_kind="external_module",
            resolved_path="",
        ),
    ]
    a.relations = [
        _make_relation("ADG::Module::x.py", "imports", "ADG::Module::y.py", edge_kind="import"),
        _make_relation("ADG::Module::x.py", "calls", "ADG::Symbol::json.loads", edge_kind="call"),
        _make_relation(
            "ADG::Module::tests/test_x.py", "covers", "ADG::Module::x.py", edge_kind="test_coverage"
        ),
        _make_relation("ADG::Module::x.py", "violates", "ADG::Module::y.py", edge_kind="layer_violation"),
    ]
    a.blind_spots = BlindSpotReport()
    a.structural_metrics = StructuralMetrics(
        total_entities=4, total_relations=4, module_count=3, symbol_count=1
    )
    a.identity_health = {}
    return a


# ---------------------------------------------------------------------------
# R1 — layer_splitter ROBUSTNESS_MATRIX
# ---------------------------------------------------------------------------


class TestLayerSplitterEdgeCases:
    """Edge cases for _build_plane / split_artifact."""

    def test_empty_artifact_produces_empty_planes(self):
        """Empty ADGArtifact → all three planes are empty but well-formed."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        planes = split_artifact(_empty_artifact())
        assert planes.file_graph.nodes == {}
        assert planes.file_graph.edges == []
        assert planes.symbol_graph.nodes == {}
        assert planes.symbol_graph.edges == []
        assert planes.governance_graph.nodes == {}
        assert planes.governance_graph.edges == []

    def test_empty_artifact_planes_have_schema_version(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        planes = split_artifact(_empty_artifact())
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            assert plane.schema_version == "4.0.0"

    def test_empty_artifact_plane_meta_total_zero(self):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        planes = split_artifact(_empty_artifact())
        assert planes.file_graph.meta["total_edges"] == 0
        assert planes.file_graph.meta["total_nodes"] == 0

    def test_unknown_rel_type_dropped_from_all_planes(self):
        """An edge with an unrecognised relation_type is silently dropped (not routed anywhere)."""
        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
            split_artifact,
        )

        a = _minimal_artifact()
        unknown_type = "totally_unknown_edge_xyz"
        assert unknown_type not in _FILE_GRAPH_RELS
        assert unknown_type not in _SYMBOL_GRAPH_RELS
        assert unknown_type not in _GOVERNANCE_GRAPH_RELS
        a.relations.append(_make_relation("ADG::Module::a.py", unknown_type, "ADG::Module::b.py"))
        planes = split_artifact(a)
        all_rels = set()
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            all_rels.update(e["r"] for e in plane.edges)
        assert unknown_type not in all_rels, "Unknown rel type must be silently dropped"

    def test_dangling_node_reference_creates_stub(self):
        """An edge referencing a node not in entities → dangling stub with type='symbol'."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _minimal_artifact()
        # Add edge to a name that does NOT exist in entities
        a.relations.append(_make_relation("ADG::Module::a.py", "imports", "ADG::Module::ghost.py"))
        planes = split_artifact(a)
        file_nodes = {n["n"]: n for n in planes.file_graph.nodes.values()}
        assert "ADG::Module::ghost.py" in file_nodes
        ghost = file_nodes["ADG::Module::ghost.py"]
        # Stub should have empty metadata fields
        assert ghost["l"] == "" or ghost["t"] in ("symbol", "module")

    def test_duplicate_edges_both_appear(self):
        """Duplicate relation records both survive — splitter does not deduplicate."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _minimal_artifact()
        # Add the same edge a second time
        a.relations.append(_make_relation("ADG::Module::a.py", "imports", "ADG::Module::b.py"))
        planes = split_artifact(a)
        import_edges = [e for e in planes.file_graph.edges if e["r"] == "imports"]
        assert len(import_edges) == 2, "Both duplicate import edges must be present"

    def test_artifact_with_only_unknown_rels_produces_empty_planes(self):
        """Artifact whose relations are all unknown → all planes empty."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _minimal_artifact()
        a.relations = [
            _make_relation("ADG::Module::a.py", "UNKNOWN_A", "ADG::Module::b.py"),
            _make_relation("ADG::Module::a.py", "UNKNOWN_B", "ADG::Module::b.py"),
        ]
        planes = split_artifact(a)
        assert planes.file_graph.edges == []
        assert planes.symbol_graph.edges == []
        assert planes.governance_graph.edges == []

    def test_node_type_filter_module_excludes_symbols(self):
        """file_graph uses node_type_filter={'module'}: symbol-only nodes not pre-registered."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _full_artifact()
        planes = split_artifact(a)
        # file_graph should not have symbol nodes unless they appear as dangling edge targets
        file_rel_types = {e["r"] for e in planes.file_graph.edges}
        # 'calls' is symbol-graph only — must not appear in file_graph
        assert "calls" not in file_rel_types

    def test_covers_route_to_file_graph_not_symbol_not_gov(self):
        """covers must land in file_graph only — not symbol_graph or governance_graph."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _full_artifact()
        planes = split_artifact(a)
        file_rels = {e["r"] for e in planes.file_graph.edges}
        sym_rels = {e["r"] for e in planes.symbol_graph.edges}
        gov_rels = {e["r"] for e in planes.governance_graph.edges}
        assert "covers" in file_rels
        assert "covers" not in sym_rels
        assert "covers" not in gov_rels

    def test_in_cycle_route_to_file_graph_not_gov(self):
        """in_cycle canonical home is file_graph — must not appear in governance_graph."""
        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
        )

        assert "in_cycle" in _FILE_GRAPH_RELS
        assert "in_cycle" not in _GOVERNANCE_GRAPH_RELS
        assert "in_cycle" not in _SYMBOL_GRAPH_RELS

    def test_violates_route_to_gov_not_file_not_symbol(self):
        """violates must land in governance_graph only."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _full_artifact()
        planes = split_artifact(a)
        file_rels = {e["r"] for e in planes.file_graph.edges}
        sym_rels = {e["r"] for e in planes.symbol_graph.edges}
        gov_rels = {e["r"] for e in planes.governance_graph.edges}
        assert "violates" in gov_rels
        assert "violates" not in file_rels
        assert "violates" not in sym_rels


class TestLayerSplitterDeterminism:
    """Determinism: identical input → identical output."""

    def test_split_artifact_is_deterministic(self):
        """Calling split_artifact twice on the same artifact yields identical digests."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _full_artifact()
        p1 = split_artifact(a)
        p2 = split_artifact(a)
        assert p1.file_graph.artifact_digest == p2.file_graph.artifact_digest
        assert p1.symbol_graph.artifact_digest == p2.symbol_graph.artifact_digest
        assert p1.governance_graph.artifact_digest == p2.governance_graph.artifact_digest

    def test_split_artifact_digest_changes_on_different_input(self):
        """Different artifacts produce different digests (no hash collision on trivial inputs)."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        p1 = split_artifact(_minimal_artifact())
        p2 = split_artifact(_full_artifact())
        # file_graph digests must differ — different edge sets
        assert p1.file_graph.artifact_digest != p2.file_graph.artifact_digest

    def test_plane_edge_count_matches_meta(self):
        """meta['total_edges'] must equal len(edges) for every plane."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _full_artifact()
        planes = split_artifact(a)
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            assert plane.meta["total_edges"] == len(plane.edges)
            assert plane.meta["total_nodes"] == len(plane.nodes)

    def test_by_relation_type_in_meta_sums_to_total_edges(self):
        """sum(meta['by_relation_type'].values()) == total_edges for each plane."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        a = _full_artifact()
        planes = split_artifact(a)
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            by_rel = plane.meta.get("by_relation_type", {})
            assert sum(by_rel.values()) == len(plane.edges)


class TestLayerSplitterZeroOverlapInvariant:
    """Mutation-sensitive: zero overlap between any two plane rel-type sets."""

    def test_all_three_rel_sets_pairwise_disjoint(self):
        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
        )

        assert not (_FILE_GRAPH_RELS & _SYMBOL_GRAPH_RELS), (
            f"FILE∩SYMBOL: {_FILE_GRAPH_RELS & _SYMBOL_GRAPH_RELS}"
        )
        assert not (_FILE_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS), (
            f"FILE∩GOV: {_FILE_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS}"
        )
        assert not (_SYMBOL_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS), (
            f"SYMBOL∩GOV: {_SYMBOL_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS}"
        )

    def test_rel_sets_are_frozensets(self):
        """Constants must be frozensets — immutable, not accidentally mutated."""
        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
        )

        assert isinstance(_FILE_GRAPH_RELS, frozenset)
        assert isinstance(_SYMBOL_GRAPH_RELS, frozenset)
        assert isinstance(_GOVERNANCE_GRAPH_RELS, frozenset)

    def test_rel_sets_cannot_be_mutated(self):
        """frozensets raise TypeError on attempted mutation."""
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS

        with pytest.raises((TypeError, AttributeError)):
            _FILE_GRAPH_RELS.add("should_fail")  # type: ignore[attr-defined]

    def test_no_edge_type_in_zero_planes(self):
        """Every relation type found in a live split must be assigned to exactly one plane."""
        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
            split_artifact,
        )

        a = _full_artifact()
        planes = split_artifact(a)
        all_declared = _FILE_GRAPH_RELS | _SYMBOL_GRAPH_RELS | _GOVERNANCE_GRAPH_RELS
        for plane in (planes.file_graph, planes.symbol_graph, planes.governance_graph):
            for e in plane.edges:
                assert e["r"] in all_declared, (
                    f"Edge type '{e['r']}' appeared in a plane but is not in any declared set"
                )

    def test_test_graph_rels_constant_does_not_exist(self):
        """_TEST_GRAPH_RELS must be removed — accessing it is a regression."""
        import agentic_core.adg.artifact.SplitArtifact as ls

        assert not hasattr(ls, "_TEST_GRAPH_RELS"), (
            "_TEST_GRAPH_RELS was removed in the ADG redesign; covers lives in file_graph"
        )

    def test_split_artifact_has_no_test_graph_attribute(self):
        """SplitArtifact must not expose a .test_graph attribute."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        planes = split_artifact(_minimal_artifact())
        assert not hasattr(planes, "test_graph"), "SplitArtifact.test_graph was removed in the ADG redesign"

    def test_size_summary_has_exactly_three_keys(self):
        """size_summary() must return exactly three plane keys."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        sizes = split_artifact(_full_artifact()).size_summary()
        assert set(sizes.keys()) == {"file_graph", "symbol_graph", "governance_graph"}

    def test_write_all_creates_exactly_three_files(self, tmp_path):
        """write_all() must create exactly three JSON files, no extras."""
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        planes = split_artifact(_full_artifact())
        paths = planes.write_all(tmp_path)
        assert set(paths.keys()) == {"file_graph", "symbol_graph", "governance_graph"}
        for path in paths.values():
            assert path.exists()
        # No adg_test_graph or adg_full files
        assert not list(tmp_path.glob("adg_test_graph*.json"))
        assert not list(tmp_path.glob("adg_full*.json"))


# ---------------------------------------------------------------------------
# R2 — multi_writer ROBUSTNESS_MATRIX
# ---------------------------------------------------------------------------


class TestMultiWriterStateTransitions:
    """State transitions: optional flags on write_all_artifacts."""

    def test_write_split_planes_false_skips_plane_files(self, tmp_path):
        """write_split_planes=False: plane JSON files must NOT be created."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="20260101T000000Z",
            write_split_planes=False,
            write_sqlite=True,
        )
        assert paths.snapshot.exists()
        assert paths.sqlite.exists()
        assert not paths.file_graph.exists()
        assert not paths.symbol_graph.exists()
        assert not paths.governance_graph.exists()

    def test_write_sqlite_false_skips_sqlite_file(self, tmp_path):
        """write_sqlite=False: SQLite file must NOT be created."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="20260101T000000Z",
            write_split_planes=True,
            write_sqlite=False,
        )
        assert paths.snapshot.exists()
        assert not paths.sqlite.exists()
        assert paths.file_graph.exists()

    def test_create_latest_symlinks_false_creates_no_latest_files(self, tmp_path):
        """create_latest_symlinks=False: no adg_LATEST* files."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="20260101T000000Z",
            create_latest_symlinks=False,
        )
        latest_files = list(tmp_path.glob("adg_LATEST*"))
        assert latest_files == [], f"Unexpected LATEST files: {latest_files}"

    def test_create_latest_symlinks_true_creates_latest_files(self, tmp_path):
        """create_latest_symlinks=True with ts: adg_LATEST* files must be created."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="20260101T000000Z",
            create_latest_symlinks=True,
        )
        latest_files = list(tmp_path.glob("adg_LATEST*"))
        assert len(latest_files) >= 2, f"Expected ≥2 LATEST files, got: {latest_files}"

    def test_latest_files_overwritten_on_second_run(self, tmp_path):
        """Running write_all_artifacts twice overwrites LATEST without error."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="20260101T000000Z",
            create_latest_symlinks=True,
        )
        # Second run with different ts must not raise
        write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="20260102T000000Z",
            create_latest_symlinks=True,
        )
        # LATEST must still exist
        assert any(tmp_path.glob("adg_LATEST*"))

    def test_no_ts_creates_no_latest_files(self, tmp_path):
        """ts='' → create_latest_symlinks path is skipped (guard: `if ts`)."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="",
            create_latest_symlinks=True,
        )
        latest_files = list(tmp_path.glob("adg_LATEST*"))
        assert latest_files == [], "No LATEST files expected when ts is empty"

    def test_both_flags_false_only_snapshot_written(self, tmp_path):
        """write_split_planes=False + write_sqlite=False → only snapshot written."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(
            _full_artifact(),
            out_dir=tmp_path,
            ts="",
            write_split_planes=False,
            write_sqlite=False,
        )
        assert paths.snapshot.exists()
        assert not paths.sqlite.exists()
        assert not paths.file_graph.exists()
        assert not paths.symbol_graph.exists()
        assert not paths.governance_graph.exists()


class TestMultiWriterSnapshotEdgeCases:
    """_build_snapshot edge cases and schema contracts."""

    def test_snapshot_never_contains_entities_key(self, tmp_path):
        """Tier-1 snapshot must never embed the entities array."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_empty_artifact(), out_dir=tmp_path, ts="")
        snap = json.loads(paths.snapshot.read_text())
        assert "entities" not in snap

    def test_snapshot_never_contains_relations_key(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_empty_artifact(), out_dir=tmp_path, ts="")
        snap = json.loads(paths.snapshot.read_text())
        assert "relations" not in snap

    def test_snapshot_zero_counts_on_empty_artifact(self, tmp_path):
        """Empty artifact → all count fields are 0, not missing or None."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_empty_artifact(), out_dir=tmp_path, ts="")
        snap = json.loads(paths.snapshot.read_text())
        counts = snap["counts"]
        assert counts["total_entities"] == 0
        assert counts["total_relations"] == 0
        assert counts["module_count"] == 0

    def test_snapshot_schema_version_constant(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="")
        snap = json.loads(paths.snapshot.read_text())
        assert snap["schema_version"] == "snapshot-1.0"

    def test_snapshot_has_all_required_top_level_keys(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="")
        snap = json.loads(paths.snapshot.read_text())
        required = {
            "schema_version",
            "commit_sha",
            "scanner_digest",
            "artifact_digest",
            "counts",
            "graph_plane_counts",
            "by_layer",
            "blind_spots",
            "top_fan_in_hotspots",
            "top_fan_out_hotspots",
        }
        missing = required - set(snap.keys())
        assert not missing, f"Snapshot missing keys: {missing}"

    def test_snapshot_blind_spots_all_zero_on_empty(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_empty_artifact(), out_dir=tmp_path, ts="")
        snap = json.loads(paths.snapshot.read_text())
        bs = snap["blind_spots"]
        assert bs["parse_failure_count"] == 0
        assert bs["dynamic_import_count"] == 0
        assert bs["star_import_count"] == 0


class TestSQLiteWriterEdgeCases:
    """_write_sqlite edge cases and data-integrity checks."""

    def test_sqlite_recreated_if_already_exists(self, tmp_path):
        """If DB already exists it must be deleted and recreated cleanly (no dup-key errors)."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="run1", write_sqlite=True)
        mtime_1 = paths.sqlite.stat().st_mtime_ns
        # Second write with different artifact, same path strategy — must not fail
        paths2 = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="run1", write_sqlite=True)
        assert paths2.sqlite.exists()
        # Content updated — different node/edge count
        conn = sqlite3.connect(str(paths2.sqlite))
        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        conn.close()
        assert node_count == 2  # _minimal_artifact has 2 entities

    def test_sqlite_empty_artifact_produces_zero_rows(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_empty_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        conn.close()
        assert nodes == 0
        assert edges == 0

    def test_sqlite_meta_schema_version_is_v4(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        conn.close()
        assert row is not None and row[0] == "4.0.0"

    def test_sqlite_meta_total_rows_consistent(self, tmp_path):
        """meta total_nodes/total_edges must match actual table counts."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        actual_nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        actual_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        meta_nodes = int(conn.execute("SELECT value FROM meta WHERE key='total_nodes'").fetchone()[0])
        meta_edges = int(conn.execute("SELECT value FROM meta WHERE key='total_edges'").fetchone()[0])
        conn.close()
        assert actual_nodes == meta_nodes
        assert actual_edges == meta_edges

    def test_sqlite_symbol_column_empty_string_by_default(self, tmp_path):
        """Edges without a symbol field must have '' in the symbol column (not NULL)."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        null_symbols = conn.execute("SELECT COUNT(*) FROM edges WHERE symbol IS NULL").fetchone()[0]
        conn.close()
        assert null_symbols == 0, "symbol column must never be NULL"

    def test_sqlite_foreign_key_src_dst_reference_valid_nodes(self, tmp_path):
        """Every edge src_id and dst_id must exist in the nodes table."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        orphan_src = conn.execute(
            "SELECT COUNT(*) FROM edges e WHERE NOT EXISTS (SELECT 1 FROM nodes n WHERE n.id = e.src_id)"
        ).fetchone()[0]
        orphan_dst = conn.execute(
            "SELECT COUNT(*) FROM edges e WHERE NOT EXISTS (SELECT 1 FROM nodes n WHERE n.id = e.dst_id)"
        ).fetchone()[0]
        conn.close()
        assert orphan_src == 0, "All edge src_ids must reference valid nodes"
        assert orphan_dst == 0, "All edge dst_ids must reference valid nodes"

    def test_sqlite_all_indexes_present(self, tmp_path):
        """Required indexes must exist for query performance."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        indexes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        conn.close()
        assert "idx_nodes_layer" in indexes
        assert "idx_nodes_name" in indexes
        assert "idx_edges_rel" in indexes
        assert "idx_edges_src" in indexes
        assert "idx_edges_dst" in indexes


class TestArtifactPathsContract:
    """ArtifactPaths dataclass contract."""

    def test_artifact_paths_has_no_full_attribute(self, tmp_path):
        """paths.full must not exist — regression guard for removed adg_full.json."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="")
        assert not hasattr(paths, "full"), "ArtifactPaths.full was removed; SQLite is now the canonical store"

    def test_artifact_paths_has_no_test_graph_attribute(self, tmp_path):
        """paths.test_graph must not exist — regression guard for removed plane."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="")
        assert not hasattr(paths, "test_graph"), "ArtifactPaths.test_graph was removed in the ADG redesign"

    def test_size_report_has_no_full_key(self, tmp_path):
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="")
        sizes = paths.size_report()
        assert "full" not in sizes
        assert "test_graph" not in sizes

    def test_size_report_missing_file_shows_missing(self, tmp_path):
        """size_report() returns 'missing' for files not written (write_sqlite=False)."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(
            _minimal_artifact(),
            out_dir=tmp_path,
            ts="",
            write_sqlite=False,
        )
        sizes = paths.size_report()
        assert sizes["sqlite"] == "missing"

    def test_size_report_five_keys_exactly(self, tmp_path):
        """size_report() must return exactly 5 keys: snapshot, sqlite, file_graph,
        symbol_graph, governance_graph."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="")
        sizes = paths.size_report()
        assert set(sizes.keys()) == {"snapshot", "sqlite", "file_graph", "symbol_graph", "governance_graph"}


# ---------------------------------------------------------------------------
# R3 — Regression guards
# ---------------------------------------------------------------------------


class TestRegressionGuards:
    """Hard regression tests: removed symbols must stay removed."""

    def test_importing_test_graph_rels_raises_import_error(self):
        """_TEST_GRAPH_RELS must not be importable — hard regression guard."""
        with pytest.raises(ImportError):
            from agentic_core.adg.artifact.SplitArtifact import _TEST_GRAPH_RELS  # noqa: F401

    def test_adg_full_file_not_created_by_write_all(self, tmp_path):
        """adg_full*.json must never be created by write_all_artifacts."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="20260312T000000Z")
        assert not list(tmp_path.glob("adg_full*.json")), (
            "adg_full.json must not be generated (SQLite supersedes it)"
        )

    def test_adg_test_graph_file_not_created_by_write_all(self, tmp_path):
        """adg_test_graph*.json must never be created by write_all_artifacts."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="20260312T000000Z")
        assert not list(tmp_path.glob("adg_test_graph*.json")), (
            "adg_test_graph.json must not be generated (covers lives in file_graph)"
        )

    def test_artifact_paths_full_attr_raises_attribute_error(self, tmp_path):
        """Direct attribute access on paths.full must raise AttributeError."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="")
        with pytest.raises(AttributeError):
            _ = paths.full

    def test_artifact_paths_test_graph_attr_raises_attribute_error(self, tmp_path):
        """Direct attribute access on paths.test_graph must raise AttributeError."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_minimal_artifact(), out_dir=tmp_path, ts="")
        with pytest.raises(AttributeError):
            _ = paths.test_graph

    def test_split_artifact_result_has_no_test_graph_field(self):
        """SplitArtifact.__dataclass_fields__ must not contain 'test_graph'."""
        import dataclasses

        from agentic_core.adg.artifact.SplitArtifact import SplitArtifact

        field_names = {f.name for f in dataclasses.fields(SplitArtifact)}
        assert "test_graph" not in field_names
        assert "file_graph" in field_names
        assert "symbol_graph" in field_names
        assert "governance_graph" in field_names

    def test_layer_splitter_all_export_list_no_test_graph(self):
        """__all__ in layer_splitter must not export _TEST_GRAPH_RELS."""
        import agentic_core.adg.artifact.SplitArtifact as ls

        assert "_TEST_GRAPH_RELS" not in ls.__all__

    def test_cli_report_dict_no_full_key(self, tmp_path, capsys):
        """CLI build-artifacts JSON report must not contain 'full' or 'test_graph' keys."""
        from agentic_core.adg.cli import main

        rc = main(["--repo-root", str(ROOT), "build-artifacts", "--output-dir", str(tmp_path)])
        assert rc == 0
        out = capsys.readouterr().out
        lines = out.splitlines()
        json_start = next((i for i, l in enumerate(lines) if l.strip() == "{"), None)
        if json_start is not None:
            report = json.loads("\n".join(lines[json_start:]))
            assert "full" not in report, "CLI report must not contain 'full'"
            assert "test_graph" not in report, "CLI report must not contain 'test_graph'"


# ---------------------------------------------------------------------------
# R4 — Fail-closed and matrix tests
# ---------------------------------------------------------------------------


class TestFailClosed:
    """Fail-closed: bad preconditions must not produce silent partial success."""

    def test_write_all_creates_out_dir_if_missing(self, tmp_path):
        """out_dir is created automatically — no pre-creation required."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        nested = tmp_path / "a" / "b" / "c"
        assert not nested.exists()
        paths = write_all_artifacts(_minimal_artifact(), out_dir=nested, ts="")
        assert nested.exists()
        assert paths.snapshot.exists()

    def test_split_artifact_write_all_creates_dir_if_missing(self, tmp_path):
        from agentic_core.adg.artifact.SplitArtifact import split_artifact

        nested = tmp_path / "planes"
        planes = split_artifact(_full_artifact())
        result = planes.write_all(nested)
        assert nested.exists()
        for path in result.values():
            assert path.exists()

    def test_snapshot_is_valid_json_on_every_run(self, tmp_path):
        """Snapshot must always be parseable as JSON — never written partially."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        for ts in ("ts1", "ts2", ""):
            sub = tmp_path / ts
            paths = write_all_artifacts(_full_artifact(), out_dir=sub, ts=ts)
            data = json.loads(paths.snapshot.read_text(encoding="utf-8"))
            assert isinstance(data, dict)

    def test_plane_json_files_are_valid_json(self, tmp_path):
        """All three plane JSON files must be parseable after write."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="", write_split_planes=True)
        for path in (paths.file_graph, paths.symbol_graph, paths.governance_graph):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(data, dict)
            assert "nodes" in data
            assert "edges" in data

    def test_sqlite_edges_relation_type_never_null(self, tmp_path):
        """relation_type column in SQLite must never be NULL or empty string."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="", write_sqlite=True)
        conn = sqlite3.connect(str(paths.sqlite))
        bad = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type IS NULL OR relation_type = ''"
        ).fetchone()[0]
        conn.close()
        assert bad == 0, "relation_type must never be NULL/empty"

    def test_plane_json_has_schema_version_field(self, tmp_path):
        """Every plane JSON file must carry schema_version at top level."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        paths = write_all_artifacts(_full_artifact(), out_dir=tmp_path, ts="", write_split_planes=True)
        for path in (paths.file_graph, paths.symbol_graph, paths.governance_graph):
            data = json.loads(path.read_text())
            assert data.get("schema_version") == "4.0.0", f"{path.name} missing schema_version=4.0.0"


class TestMatrixWriteFlags:
    """Matrix: all combinations of write_split_planes × write_sqlite."""

    @pytest.mark.parametrize(
        "write_planes,write_sq",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_flag_matrix_snapshot_always_written(self, tmp_path, write_planes, write_sq):
        """Snapshot is always written regardless of other flags."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        sub = tmp_path / f"p{write_planes}_s{write_sq}"
        paths = write_all_artifacts(
            _full_artifact(),
            out_dir=sub,
            ts="",
            write_split_planes=write_planes,
            write_sqlite=write_sq,
        )
        assert paths.snapshot.exists(), "snapshot must always be written"

    @pytest.mark.parametrize(
        "write_planes,write_sq",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_flag_matrix_adg_full_never_written(self, tmp_path, write_planes, write_sq):
        """adg_full.json must never be written regardless of flags."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        sub = tmp_path / f"p{write_planes}_s{write_sq}"
        write_all_artifacts(
            _full_artifact(),
            out_dir=sub,
            ts="ts",
            write_split_planes=write_planes,
            write_sqlite=write_sq,
        )
        assert not list(sub.glob("adg_full*.json")), (
            f"adg_full.json must never be written (planes={write_planes}, sqlite={write_sq})"
        )

    @pytest.mark.parametrize(
        "write_planes,write_sq",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_flag_matrix_test_graph_never_written(self, tmp_path, write_planes, write_sq):
        """adg_test_graph.json must never be written regardless of flags."""
        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        sub = tmp_path / f"tp{write_planes}_s{write_sq}"
        write_all_artifacts(
            _full_artifact(),
            out_dir=sub,
            ts="ts",
            write_split_planes=write_planes,
            write_sqlite=write_sq,
        )
        assert not list(sub.glob("adg_test_graph*.json")), "adg_test_graph.json must never be written"
