"""Tests for structural conformance query pack."""

from __future__ import annotations

import networkx as nx
import pytest

from tools.graphdb.queries.structural import StructuralQueries
from tests.unit.tools.graphdb.conftest import _make_node, _make_edge


class TestGravityImportViolations:
    def test_no_violations_on_clean_graph(self, clean_graph: nx.DiGraph):
        sq = StructuralQueries(clean_graph)
        violations = sq.gravity_import_violations()
        assert violations == []

    def test_detects_upward_import(self, gravity_violation_graph: nx.DiGraph):
        sq = StructuralQueries(gravity_violation_graph)
        violations = sq.gravity_import_violations()
        assert len(violations) == 1
        v = violations[0]
        assert v["type"] == "gravity_import_violation"
        assert v["from_layer"] == "L0"
        assert v["to_layer"] == "L3"

    def test_returns_list(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).gravity_import_violations()
        assert isinstance(result, list)

    def test_violation_has_required_keys(self, gravity_violation_graph: nx.DiGraph):
        violations = StructuralQueries(gravity_violation_graph).gravity_import_violations()
        v = violations[0]
        assert "type" in v
        assert "from_node" in v
        assert "to_node" in v
        assert "from_layer" in v
        assert "to_layer" in v
        assert "from_level" in v
        assert "to_level" in v
        assert "violation" in v
        assert v["from_layer"] == "L0"
        assert v["to_layer"] == "L3"
        assert v["from_level"] == 0
        assert v["to_level"] == 3
        assert "L0" in v["violation"]
        assert "L3" in v["violation"]

    def test_same_layer_import_is_not_violation(self):
        g = nx.DiGraph()
        _make_node(g, "a", "module", "mod_a", layer="L2")
        _make_node(g, "b", "module", "mod_b", layer="L2")
        _make_edge(g, "a", "b", "imports")
        violations = StructuralQueries(g).gravity_import_violations()
        assert violations == []


class TestIllegalLayerReach:
    def test_no_violations_on_clean_graph(self, clean_graph: nx.DiGraph):
        result = StructuralQueries(clean_graph).illegal_layer_reach()
        assert result == []

    def test_detects_l6_to_l2(self, illegal_reach_graph: nx.DiGraph):
        result = StructuralQueries(illegal_reach_graph).illegal_layer_reach()
        assert len(result) == 1
        assert result[0]["from_layer"] == "L6"
        assert result[0]["to_layer"] == "L2"

    def test_violation_has_reason_field(self, illegal_reach_graph: nx.DiGraph):
        result = StructuralQueries(illegal_reach_graph).illegal_layer_reach()
        assert "reason" in result[0]

    def test_returns_list(self, minimal_graph: nx.DiGraph):
        assert isinstance(StructuralQueries(minimal_graph).illegal_layer_reach(), list)


class TestL2LifecycleConformance:
    def test_returns_dict(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).l2_lifecycle_conformance()
        assert isinstance(result, dict)

    def test_required_keys_present(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).l2_lifecycle_conformance()
        assert "total_l2_modules" in result
        assert "conformance_rate" in result
        assert "conformant_modules" in result
        assert "non_conformant_modules" in result

    def test_conformance_rate_is_float(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).l2_lifecycle_conformance()
        assert isinstance(result["conformance_rate"], float)

    def test_module_with_execute_name_is_conformant(self):
        g = nx.DiGraph()
        _make_node(g, "m", "module", "execute_workflow", layer="L2")
        result = StructuralQueries(g).l2_lifecycle_conformance()
        assert len(result["conformant_modules"]) == 1

    def test_empty_graph_returns_zero_rate(self):
        g = nx.DiGraph()
        result = StructuralQueries(g).l2_lifecycle_conformance()
        assert result["total_l2_modules"] == 0
        assert result["conformance_rate"] == 0.0


class TestUWGDurableWriteConformance:
    def test_detects_bypass(self, uwg_graph: nx.DiGraph):
        violations = StructuralQueries(uwg_graph).uwg_durable_write_conformance()
        assert len(violations) == 1
        assert violations[0]["type"] == "uwg_bypass_violation"

    def test_writes_through_not_violation(self, uwg_graph: nx.DiGraph):
        violations = StructuralQueries(uwg_graph).uwg_durable_write_conformance()
        bad_nodes = [v["from_node"] for v in violations]
        assert "writer_ok" not in bad_nodes

    def test_returns_list(self, minimal_graph: nx.DiGraph):
        assert isinstance(StructuralQueries(minimal_graph).uwg_durable_write_conformance(), list)


class TestAgenticSpineCompleteness:
    def test_spine_complete_on_full_layer_graph(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).agentic_spine_completeness()
        assert isinstance(result, dict)
        assert "spine_complete" in result
        assert "layer_analysis" in result

    def test_empty_graph_has_missing_components(self):
        g = nx.DiGraph()
        result = StructuralQueries(g).agentic_spine_completeness()
        assert not result["spine_complete"]
        assert len(result["missing_components"]) > 0

    def test_layer_analysis_has_all_spine_entries(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).agentic_spine_completeness()
        expected_components = {
            "routing",
            "reasoning",
            "execution",
            "orchestration",
            "state",
            "safety",
            "infrastructure",
        }
        assert expected_components.issubset(result["layer_analysis"].keys())


class TestL0L1L6RolePurity:
    def test_returns_dict(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).l0_l1_l6_role_purity()
        assert isinstance(result, dict)

    def test_required_keys_present(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).l0_l1_l6_role_purity()
        assert "purity_violations" in result
        assert "total_violations" in result
        assert "is_pure" in result

    def test_purity_violations_has_three_layers(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).l0_l1_l6_role_purity()
        assert set(result["purity_violations"].keys()) == {"L0", "L1", "L6"}

    def test_empty_graph_is_pure(self):
        g = nx.DiGraph()
        result = StructuralQueries(g).l0_l1_l6_role_purity()
        assert result["is_pure"] is True
        assert result["total_violations"] == 0


class TestGroundingContractSeparation:
    def test_returns_list(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).grounding_contract_separation()
        assert isinstance(result, list)

    def test_no_violations_on_clean_graph(self, clean_graph: nx.DiGraph):
        result = StructuralQueries(clean_graph).grounding_contract_separation()
        assert result == []


class TestTraceReplayEvalCoverage:
    def test_returns_dict(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).trace_replay_eval_coverage()
        assert isinstance(result, dict)

    def test_required_keys_present(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).trace_replay_eval_coverage()
        required = {
            "trace_components",
            "replay_components",
            "eval_components",
            "execution_components",
            "traced_execution",
            "trace_coverage",
            "coverage_complete",
        }
        assert required.issubset(result.keys())

    def test_coverage_rate_is_float(self, minimal_graph: nx.DiGraph):
        result = StructuralQueries(minimal_graph).trace_replay_eval_coverage()
        assert isinstance(result["trace_coverage"], float)

    def test_empty_graph_zero_coverage(self):
        g = nx.DiGraph()
        result = StructuralQueries(g).trace_replay_eval_coverage()
        assert result["trace_coverage"] == 0.0
        assert result["coverage_complete"] is True
