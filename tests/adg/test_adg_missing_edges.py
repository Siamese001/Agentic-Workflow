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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_missing_edges")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_missing_edges", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_missing_edges", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_missing_edges", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_missing_edges", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_missing_edges", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_missing_edges", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_missing_edges", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_missing_edges", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_missing_edges", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_missing_edges", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_missing_edges", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_missing_edges", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_missing_edges", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_missing_edges", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_missing_edges", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_missing_edges", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_missing_edges", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_missing_edges", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_missing_edges", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_missing_edges", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_missing_edges", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_missing_edges", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_missing_edges", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_missing_edges", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_missing_edges", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_missing_edges", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_missing_edges", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_missing_edges", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_missing_edges", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_missing_edges", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_missing_edges", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_missing_edges", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_missing_edges", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_missing_edges", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_missing_edges", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_missing_edges", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_missing_edges", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_missing_edges", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_missing_edges", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_missing_edges", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_missing_edges", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_missing_edges", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_missing_edges", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_missing_edges", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_missing_edges", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_missing_edges", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_missing_edges", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_missing_edges", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_missing_edges", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_missing_edges", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_missing_edges", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_missing_edges")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_missing_edges", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_missing_edges")
# REMOVED: emit_determinism_digest("p0", "test_adg_missing_edges")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_missing_edges", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_missing_edges", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_missing_edges", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_missing_edges", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_missing_edges", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_missing_edges", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_missing_edges", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_missing_edges", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_missing_edges", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_missing_edges", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_missing_edges", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_missing_edges", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_missing_edges", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_missing_edges", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_missing_edges", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_missing_edges", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_missing_edges", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_missing_edges", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_missing_edges", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_missing_edges", "exec_snapshot_link")

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
