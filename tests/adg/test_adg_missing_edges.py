"""Tests for Phase 3 missing edge extraction (G12-G16).

Covers:
- G12: belongs_to_layer edges emitted in graph_persister.py
- G13: bypasses_uwg edges (rule_id observation attached)
- G14: seam_bypass edge type in schema
- G15: in_cycle edges emitted by _detect_cycles (already works, regression test)
- G16: rule_id observation on violates/bypasses_uwg/seam_bypass edges in graph_persister
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_edge(
    from_name, relation_type, to_name, edge_kind="import", source_file="test.py", line_no=1, symbol=""
):
    from agentic_core.adg.extraction.static_scanner import Edge

    return Edge(
        from_name=from_name,
        relation_type=relation_type,
        to_name=to_name,
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=line_no,
        symbol=symbol,
    )


def _make_scan_result(edges, modules=None):
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="test_sha")
    result.edges = edges
    result.modules = modules or []
    result.syntax_errors = []
    result.compute_digest()
    return result


# ---------------------------------------------------------------------------
# G12: belongs_to_layer edges in graph_persister
# ---------------------------------------------------------------------------


class TestG12BelongsToLayer:
    def test_persist_modules_emits_belongs_to_layer(self):
        from agentic_core.adg.extraction.graph_persister import _persist_modules

        client = MagicMock()
        result = _make_scan_result([], modules=["agentic_core/L2_execution/SomeAgent.py"])
        _persist_modules(result, client, "sha123", "2026-01-01T00:00:00+00:00")

        # Collect all upsert_relation calls
        relation_calls = list(client.upsert_relation.call_args_list)
        belongs_to_layer_calls = [
            c for c in relation_calls if len(c.args) >= 2 and c.args[1] == "belongs_to_layer"
        ]
        assert belongs_to_layer_calls, (
            "belongs_to_layer relation must be emitted for each module in _persist_modules"
        )

    def test_belongs_to_layer_target_is_layer_node(self):
        from agentic_core.adg.extraction.graph_persister import _persist_modules

        client = MagicMock()
        result = _make_scan_result([], modules=["agentic_core/L2_execution/SomeAgent.py"])
        _persist_modules(result, client, "", "2026-01-01T00:00:00+00:00")

        relation_calls = list(client.upsert_relation.call_args_list)
        layer_targets = [
            c.args[2] for c in relation_calls if len(c.args) >= 3 and c.args[1] == "belongs_to_layer"
        ]
        assert layer_targets, "belongs_to_layer call must have a to_name target"
        for target in layer_targets:
            assert target.startswith("ADG::Layer::"), (
                f"belongs_to_layer target must be an ADG::Layer:: node, got {target}"
            )

    def test_ensure_layer_nodes_called_on_persist(self):
        from agentic_core.adg.extraction.graph_persister import persist_scan_result

        client = MagicMock()
        result = _make_scan_result([], modules=[])

        persist_scan_result(result, client)

        # All _LAYER_LABELS should be upserted
        entity_calls = [c.args[0] for c in client.upsert_entity.call_args_list]
        layer_nodes = [n for n in entity_calls if n.startswith("ADG::Layer::")]
        assert layer_nodes, "_ensure_layer_nodes must create ADG::Layer:: nodes"


# ---------------------------------------------------------------------------
# G15: in_cycle edges from _detect_cycles (regression)
# ---------------------------------------------------------------------------


class TestG15InCycleEdges:
    def test_detect_cycles_finds_mutual_import(self):
        from agentic_core.adg.extraction.static_scanner import _detect_cycles

        # A -> B -> A is a cycle
        edges = [
            _make_edge(
                "ADG::Module::pkg/a.py",
                "imports",
                "ADG::Module::pkg/b.py",
                symbol="pkg.b",
            ),
            _make_edge(
                "ADG::Module::pkg/b.py",
                "imports",
                "ADG::Module::pkg/a.py",
                symbol="pkg.a",
            ),
        ]
        result = _make_scan_result(edges)
        cycle_edges = _detect_cycles(result)
        assert cycle_edges, "Mutual import cycle should produce in_cycle edges"
        assert all(e.relation_type == "in_cycle" for e in cycle_edges)

    def test_no_cycle_for_acyclic_graph(self):
        from agentic_core.adg.extraction.static_scanner import _detect_cycles

        edges = [
            _make_edge(
                "ADG::Module::pkg/a.py",
                "imports",
                "ADG::Module::pkg/b.py",
                symbol="pkg.b",
            ),
            _make_edge(
                "ADG::Module::pkg/b.py",
                "imports",
                "ADG::Module::pkg/c.py",
                symbol="pkg.c",
            ),
        ]
        result = _make_scan_result(edges)
        cycle_edges = _detect_cycles(result)
        assert not cycle_edges, "Acyclic graph should produce no in_cycle edges"

    def test_cycle_edges_point_to_adg_cycle_node(self):
        from agentic_core.adg.extraction.static_scanner import _detect_cycles

        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Module::b.py", symbol="b"),
            _make_edge("ADG::Module::b.py", "imports", "ADG::Module::a.py", symbol="a"),
        ]
        result = _make_scan_result(edges)
        cycle_edges = _detect_cycles(result)
        for ce in cycle_edges:
            assert ce.to_name.startswith("ADG::Cycle::"), (
                f"in_cycle edge target must be ADG::Cycle:: node, got {ce.to_name}"
            )

    def test_three_node_cycle_detected(self):
        from agentic_core.adg.extraction.static_scanner import _detect_cycles

        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Module::b.py", symbol="b"),
            _make_edge("ADG::Module::b.py", "imports", "ADG::Module::c.py", symbol="c"),
            _make_edge("ADG::Module::c.py", "imports", "ADG::Module::a.py", symbol="a"),
        ]
        result = _make_scan_result(edges)
        cycle_edges = _detect_cycles(result)
        assert len(cycle_edges) == 3, "Three-node cycle should produce 3 in_cycle edges"


# ---------------------------------------------------------------------------
# G16: rule_id on violation/bypass edges in graph_persister
# ---------------------------------------------------------------------------


class TestG16RuleId:
    def test_violates_edge_gets_rule_id_observation(self):
        from agentic_core.adg.extraction.graph_persister import _derive_rule_id

        rule_id = _derive_rule_id("violates", "L0->L3")
        assert rule_id, "violates relation should produce a rule_id"
        assert "LAYER_GRAVITY" in rule_id

    def test_bypasses_uwg_edge_gets_rule_id_observation(self):
        from agentic_core.adg.extraction.graph_persister import _derive_rule_id

        rule_id = _derive_rule_id("bypasses_uwg", "some_write_call")
        assert rule_id, "bypasses_uwg relation should produce a rule_id"
        assert "UWG_BYPASS" in rule_id

    def test_seam_bypass_edge_gets_rule_id_observation(self):
        from agentic_core.adg.extraction.graph_persister import _derive_rule_id

        rule_id = _derive_rule_id("seam_bypass", "direct_openai_call")
        assert rule_id, "seam_bypass relation should produce a rule_id"
        assert "SEAM_BYPASS" in rule_id

    def test_regular_edge_no_rule_id(self):
        from agentic_core.adg.extraction.graph_persister import _derive_rule_id

        assert _derive_rule_id("imports", "some_module") == ""
        assert _derive_rule_id("calls", "some_func") == ""
        assert _derive_rule_id("reads_env", "os.getenv") == ""

    def test_rule_id_observation_attached_in_persist_edges(self):
        from agentic_core.adg.extraction.graph_persister import _persist_edges

        edges = [
            _make_edge(
                "ADG::Module::agentic_core/L0_routing/router.py",
                "violates",
                "ADG::Layer::L3",
                edge_kind="import",
                symbol="L0->L3",
            )
        ]
        result = _make_scan_result(edges)
        client = MagicMock()
        _persist_edges(result, client, None)

        # Check that upsert_entity was called with rule_id observation
        entity_calls = client.upsert_entity.call_args_list
        rule_id_obs_found = False
        for c in entity_calls:
            obs = c.args[2] if len(c.args) >= 3 else []
            if any("rule_id:LAYER_GRAVITY" in o for o in obs):
                rule_id_obs_found = True
                break
        assert rule_id_obs_found, (
            "violates edge should produce rule_id:LAYER_GRAVITY observation in upsert_entity"
        )

    def test_rule_id_includes_symbol_in_observation(self):
        from agentic_core.adg.extraction.graph_persister import _derive_rule_id

        rule_id = _derive_rule_id("violates", "L0->L3")
        assert "L0->L3" in rule_id, "rule_id should include the symbol value for context"

    def test_rule_id_without_symbol_is_just_prefix(self):
        from agentic_core.adg.extraction.graph_persister import _derive_rule_id

        rule_id = _derive_rule_id("violates", "")
        assert rule_id == "LAYER_GRAVITY"


# ---------------------------------------------------------------------------
# _infer_entity_type coverage (G2 fix in graph_persister)
# ---------------------------------------------------------------------------


class TestInferEntityType:
    def test_layer_prefix_infers_layer(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::Layer::L2") == "layer"

    def test_gateway_prefix_infers_gateway(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::Gateway::UniversalWriteGateway") == "gateway"

    def test_prompt_slot_prefix_infers_prompt_slot(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::PromptSlot::S0::test.py") == "prompt_slot"

    def test_prompt_template_prefix_infers_prompt_template(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::PromptTemplate::CONSTITUTION") == "prompt_template"

    def test_seam_prefix_infers_seam(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::Seam::some_seam") == "seam"

    def test_symbol_prefix_infers_symbol(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::Symbol::some.func") == "symbol"

    def test_unknown_prefix_falls_back_to_symbol(self):
        from agentic_core.adg.extraction.graph_persister import _infer_entity_type

        assert _infer_entity_type("ADG::Unknown::whatever") == "symbol"
