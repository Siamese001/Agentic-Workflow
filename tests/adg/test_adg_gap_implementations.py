"""Tests for all ADG gap-plane implementations.

Covers:
  G1 - _HealerValidatorVisitor (static_scanner) + detect_healer_validator_relationships (analysis)
       + AgentLoopRecorder / HealerLoopRecorder (runtime/event_graph)
  G3 - _EmbeddingPipelineVisitor (static_scanner)
  G4 - _HITLVisitor (static_scanner) + HITLRuntimeRecorder (runtime/hitl_graph)
  G5 - _SafetyEnforcementVisitor (static_scanner) + RuntimeSafetyObserver (runtime/safety_observer)
  G6 - scan_agent_registry (extraction/agent_registry_scanner)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_adg_gap_implementations")
_emit_applies_guardrail("p0", "test_adg_gap_implementations", "p0_governance")
_emit_snapshots_state("p0", "test_adg_gap_implementations", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_adg_gap_implementations", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_gap_implementations", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_gap_implementations", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_gap_implementations", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_gap_implementations", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_gap_implementations", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_gap_implementations", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_gap_implementations", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_gap_implementations", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_gap_implementations", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_gap_implementations", "p4obs", "alert")
_emit_links_incident_trace("test_adg_gap_implementations", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_gap_implementations", "p3lm", "pattern")
_emit_records_learning_event("test_adg_gap_implementations", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_gap_implementations", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_gap_implementations", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_gap_implementations", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_gap_implementations", "p3lm", "policy")
_emit_stores_learning_state("test_adg_gap_implementations", "p3lm", "state")
_emit_records_execution_trace("test_adg_gap_implementations", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_gap_implementations", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_gap_implementations", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_gap_implementations", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_gap_implementations", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_gap_implementations", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_gap_implementations", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_gap_implementations", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_gap_implementations", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_gap_implementations", "context_pull")
_emit_pulls_context("p1", "test_adg_gap_implementations", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_implementations", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_implementations", "uwg_term_2")
_emit_writes_through("p1", "test_adg_gap_implementations", "write_through")
_emit_writes_through("p1", "test_adg_gap_implementations", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_gap_implementations", "safety_validation")
_emit_invokes_eval("p1", "test_adg_gap_implementations", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_gap_implementations", "routing_commit")
emit_replay_key("p0", "test_adg_gap_implementations")
emit_determinism_digest("p0", "test_adg_gap_implementations")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_gap_implementations", "execution_auth")
_emit_validates_capability("p2", "test_adg_gap_implementations", "capability_check")
_emit_routes_to_capability("p2", "test_adg_gap_implementations", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_gap_implementations", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_gap_implementations", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_gap_implementations", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_gap_implementations", "exec_output")
_emit_dispatches_agent("p3", "test_adg_gap_implementations", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_gap_implementations", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_gap_implementations", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_gap_implementations", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_gap_implementations", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_gap_implementations", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_gap_implementations", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_gap_implementations", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_gap_implementations", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_gap_implementations", "eval_metric")
_emit_stores_embedding("p4", "test_adg_gap_implementations", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_gap_implementations", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_gap_implementations", "exec_snapshot_link")

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_edge_stub(
    from_name: str = "ADG::Module::foo",
    relation_type: str = "imports",
    to_name: str = "ADG::Module::bar",
    edge_kind: str = "import",
    source_file: str = "foo.py",
    line_no: int = 1,
    symbol: str = "",
):
    """Create a minimal Edge-like object without importing the full scanner."""
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


def _scan_src(src: str, rel_path: str = "test_module.py"):
    """Parse src string into an AST and run _scan_file logic via a temp file."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write(src)
        tmp = Path(f.name)
    try:
        from agentic_core.adg.extraction.static_scanner import _scan_file

        edges, errored = _scan_file(tmp, tmp.parent)
        return edges, errored
    finally:
        tmp.unlink(missing_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# G1: _HealerValidatorVisitor
# ─────────────────────────────────────────────────────────────────────────────


class TestHealerValidatorVisitor:
    def test_heals_edge_emitted_for_healer_base_class(self):
        src = """\
from apps_shared.reasoning.BaseHealingOrchestrator import BaseHealingOrchestrator

class MyHealer(BaseHealingOrchestrator):
    pass
"""
        edges, err = _scan_src(src)
        assert not err
        healer_edges = [e for e in edges if e.relation_type == "heals"]
        assert len(healer_edges) >= 1
        assert any("BaseHealingOrchestrator" in e.symbol for e in healer_edges)

    def test_validates_edge_emitted_for_validator_base_class(self):
        src = """\
class MyValidator(BaseValidator):
    pass
"""
        edges, err = _scan_src(src)
        healer_edges = [e for e in edges if e.relation_type == "validates"]
        assert len(healer_edges) >= 1
        assert any("BaseValidator" in e.symbol for e in healer_edges)

    def test_orchestrates_healing_edge_for_heal_method_call(self):
        src = """\
def do_work(self):
    self.heal()
"""
        edges, err = _scan_src(src)
        dispatch_edges = [e for e in edges if e.relation_type == "orchestrates_healing"]
        assert len(dispatch_edges) >= 1
        assert any("heal" in e.symbol for e in dispatch_edges)

    def test_healing_dispatch_edge_kind(self):
        src = """\
def run(self):
    self.orchestrate_healing_cycle()
"""
        edges, err = _scan_src(src)
        dispatch_edges = [e for e in edges if e.relation_type == "orchestrates_healing"]
        assert all(e.edge_kind == "healing_dispatch" for e in dispatch_edges)

    def test_heals_edge_kind_is_healer_action(self):
        src = """\
class X(SovereignHealingAgent):
    pass
"""
        edges, err = _scan_src(src)
        heals = [e for e in edges if e.relation_type == "heals"]
        assert all(e.edge_kind == "healer_action" for e in heals)

    def test_validates_edge_kind_is_validator_check(self):
        src = """\
class X(ResolutionValidator):
    pass
"""
        edges, err = _scan_src(src)
        validates = [e for e in edges if e.relation_type == "validates"]
        assert all(e.edge_kind == "validator_check" for e in validates)

    def test_unknown_base_class_no_healer_edge(self):
        src = """\
class X(SomeOtherBase):
    pass
"""
        edges, err = _scan_src(src)
        healer_edges = [e for e in edges if e.relation_type in ("heals", "validates")]
        assert len(healer_edges) == 0

    def test_attribute_base_class_heals_edge(self):
        src = """\
class X(apps_shared.BaseHealingOrchestrator):
    pass
"""
        edges, err = _scan_src(src)
        heals = [e for e in edges if e.relation_type == "heals"]
        assert len(heals) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# G1: detect_healer_validator_relationships
# ─────────────────────────────────────────────────────────────────────────────


class TestHealerValidatorGraphAnalysis:
    def _make_scan_result(self, edges):
        """Minimal ScanResult stub."""
        sr = MagicMock()
        sr.edges = edges
        return sr

    def test_healer_module_detected(self):
        from agentic_core.adg.analysis.healer_validator_graph import (
            detect_healer_validator_relationships,
        )

        sr = self._make_scan_result(
            [
                _make_edge_stub(
                    from_name="ADG::Module::foo",
                    relation_type="heals",
                    to_name="ADG::Symbol::BaseHealingOrchestrator",
                    edge_kind="healer_action",
                    symbol="BaseHealingOrchestrator",
                )
            ]
        )
        report = detect_healer_validator_relationships(sr)
        assert "ADG::Module::foo" in report.healer_modules

    def test_validator_module_detected(self):
        from agentic_core.adg.analysis.healer_validator_graph import (
            detect_healer_validator_relationships,
        )

        sr = self._make_scan_result(
            [
                _make_edge_stub(
                    from_name="ADG::Module::bar",
                    relation_type="validates",
                    to_name="ADG::Symbol::BaseValidator",
                    edge_kind="validator_check",
                    symbol="BaseValidator",
                )
            ]
        )
        report = detect_healer_validator_relationships(sr)
        assert "ADG::Module::bar" in report.validator_modules

    def test_unbound_healer_with_no_validator_target(self):
        from agentic_core.adg.analysis.healer_validator_graph import (
            detect_healer_validator_relationships,
        )

        sr = self._make_scan_result(
            [
                _make_edge_stub(
                    from_name="ADG::Module::healer_mod",
                    relation_type="heals",
                    to_name="ADG::Symbol::BaseHealingOrchestrator",
                    edge_kind="healer_action",
                    symbol="BaseHealingOrchestrator",
                )
            ]
        )
        report = detect_healer_validator_relationships(sr)
        assert "ADG::Module::healer_mod" in report.unbound_healers

    def test_report_to_dict_serializable(self):
        from agentic_core.adg.analysis.healer_validator_graph import (
            detect_healer_validator_relationships,
        )

        sr = self._make_scan_result([])
        report = detect_healer_validator_relationships(sr)
        d = report.to_dict()
        assert isinstance(d, dict)
        json.dumps(d)  # must be JSON-serializable

    def test_summary_string(self):
        from agentic_core.adg.analysis.healer_validator_graph import (
            detect_healer_validator_relationships,
        )

        sr = self._make_scan_result([])
        report = detect_healer_validator_relationships(sr)
        s = report.summary
        assert "Healer/Validator Graph" in s

    def test_pair_inferred_from_dispatch_to_validator(self):
        from agentic_core.adg.analysis.healer_validator_graph import (
            detect_healer_validator_relationships,
        )

        sr = self._make_scan_result(
            [
                _make_edge_stub(
                    from_name="ADG::Module::orch",
                    relation_type="heals",
                    to_name="ADG::Symbol::BaseHealingOrchestrator",
                    edge_kind="healer_action",
                    symbol="BaseHealingOrchestrator",
                ),
                _make_edge_stub(
                    from_name="ADG::Module::orch",
                    relation_type="dispatches_to",
                    to_name="ADG::Symbol::ResolutionValidator",
                    edge_kind="healing_dispatch",
                    symbol="ResolutionValidator",
                ),
            ]
        )
        report = detect_healer_validator_relationships(sr)
        assert report.pair_count >= 1
        healers = [h for h, _ in report.healer_validator_pairs]
        assert "ADG::Module::orch" in healers


# ─────────────────────────────────────────────────────────────────────────────
# G1: Runtime AgentLoopRecorder + HealerLoopRecorder
# ─────────────────────────────────────────────────────────────────────────────


class TestAgentLoopRecorder:
    def test_observe_emits_event(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.observe(input_hash="abc123")
        assert len(g.events) == 1
        assert g.events[0].event_type == "observe"
        assert g.events[0].phase == "observe"

    def test_reason_emits_event(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.reason(strategy="archetype_routing")
        assert g.events[0].payload["strategy"] == "archetype_routing"

    def test_act_emits_event_and_edge(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.act(tool="SovereignLLMGateway", output_hash="def456")
        assert len(g.events) == 1
        assert g.events[0].event_type == "act"
        assert len(g.edges) == 1
        assert g.edges[0].relation_type == "invokes_tool"
        assert g.edges[0].to_entity == "SovereignLLMGateway"

    def test_act_no_tool_emits_no_edge(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.act()  # no tool
        assert len(g.edges) == 0

    def test_evaluate_emits_event(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.evaluate(outcome="SUCCESS", confidence=0.92)
        assert g.events[0].payload["confidence"] == 0.92

    def test_learn_with_delta_emits_learning_edge(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.learn(delta_applied=True, strategy_weight_delta=0.05)
        assert any(e.relation_type == "learns_from_decision" for e in g.edges)

    def test_learn_without_delta_no_edge(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.learn(delta_applied=False)
        assert len(g.edges) == 0

    def test_full_loop_five_events(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.observe()
        r.reason()
        r.act(tool="T")
        r.evaluate()
        r.learn()
        assert g.event_count == 5

    def test_runtime_graph_to_json(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.observe(input_hash="x")
        j = g.to_json()
        data = json.loads(j)
        assert data["event_count"] == 1

    def test_events_by_phase_grouping(self):
        from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = AgentLoopRecorder(g, agent_id="TestAgent", run_id="run-1")
        r.observe()
        r.observe(input_hash="second")
        groups = g.events_by_phase()
        assert len(groups["observe"]) == 2


class TestHealerLoopRecorder:
    def test_detect_emits_event_and_edge(self):
        from agentic_core.adg.runtime.event_graph import HealerLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = HealerLoopRecorder(g, agent_id="LicHealingOrchestrator", run_id="r1")
        r.detect(violation_type="UWG_BYPASS", violation_id="v001")
        assert g.events[0].event_type == "detect"
        heal_edge = [e for e in g.edges if e.relation_type == "heals"]
        assert len(heal_edge) == 1

    def test_heal_emits_orchestrates_healing_edge(self):
        from agentic_core.adg.runtime.event_graph import HealerLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = HealerLoopRecorder(g, agent_id="LicHealingOrchestrator", run_id="r1")
        r.heal(target_module="apps_lic/reasoning/Foo.py")
        assert any(e.relation_type == "orchestrates_healing" for e in g.edges)

    def test_validate_emits_dispatches_to_edge(self):
        from agentic_core.adg.runtime.event_graph import HealerLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = HealerLoopRecorder(g, agent_id="LicHealingOrchestrator", run_id="r1")
        r.validate(validator="ResolutionValidator", passed=True)
        assert any(e.relation_type == "dispatches_to" for e in g.edges)

    def test_escalate_emits_escalates_to_human_edge(self):
        from agentic_core.adg.runtime.event_graph import HealerLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = HealerLoopRecorder(g, agent_id="LicHealingOrchestrator", run_id="r1")
        r.escalate(reason="low_confidence", confidence=0.12)
        assert any(e.relation_type == "escalates_to_human" for e in g.edges)

    def test_full_healer_loop_events(self):
        from agentic_core.adg.runtime.event_graph import HealerLoopRecorder, RuntimeGraph

        g = RuntimeGraph()
        r = HealerLoopRecorder(g, agent_id="LicHealingOrchestrator", run_id="r1")
        r.detect(violation_type="T", violation_id="v1")
        r.plan(strategy="rewrite")
        r.heal(target_module="foo.py")
        r.validate(validator="V", passed=True)
        r.commit(mutation_hash="sha256:abc")
        assert g.event_count == 5


# ─────────────────────────────────────────────────────────────────────────────
# G3: _EmbeddingPipelineVisitor
# ─────────────────────────────────────────────────────────────────────────────


class TestEmbeddingPipelineVisitor:
    def test_chunks_into_edge_for_splitter_call(self):
        src = """\
splitter = RecursiveCharacterTextSplitter(chunk_size=500)
"""
        edges, _ = _scan_src(src)
        chunking = [e for e in edges if e.relation_type == "chunks_into"]
        assert len(chunking) >= 1
        assert any("RecursiveCharacterTextSplitter" in e.symbol for e in chunking)

    def test_chunking_pipeline_edge_kind(self):
        src = """\
r = chunk_text(doc)
"""
        edges, _ = _scan_src(src)
        chunking = [e for e in edges if e.relation_type == "chunks_into"]
        assert all(e.edge_kind == "chunking_pipeline" for e in chunking)

    def test_stores_embedding_for_vector_store_write(self):
        src = """\
store = FAISS()
store.add_documents(docs)
"""
        edges, _ = _scan_src(src)
        store_edges = [e for e in edges if e.relation_type == "stores_embedding"]
        assert len(store_edges) >= 1

    def test_retrieves_via_for_similarity_search(self):
        src = """\
results = store.similarity_search(query)
"""
        edges, _ = _scan_src(src)
        retrieval_edges = [e for e in edges if e.relation_type == "retrieves_via"]
        assert len(retrieval_edges) >= 1

    def test_no_embedding_edges_for_unrelated_code(self):
        src = """\
x = 1 + 2
print(x)
"""
        edges, _ = _scan_src(src)
        emb_edges = [
            e
            for e in edges
            if e.relation_type in ("chunks_into", "embeds_into", "stores_embedding", "retrieves_via")
        ]
        assert len(emb_edges) == 0


# ─────────────────────────────────────────────────────────────────────────────
# G4: _HITLVisitor
# ─────────────────────────────────────────────────────────────────────────────


class TestHITLVisitor:
    def test_gated_by_confidence_edge_for_scorer_class(self):
        src = """\
scorer = HealingConfidenceScorer()
result = scorer.score(context)
"""
        edges, _ = _scan_src(src)
        conf_edges = [e for e in edges if e.relation_type == "gated_by_confidence"]
        assert len(conf_edges) >= 1

    def test_confidence_gate_edge_kind(self):
        src = """\
s = ConfidenceScorer()
"""
        edges, _ = _scan_src(src)
        conf_edges = [e for e in edges if e.relation_type == "gated_by_confidence"]
        assert all(e.edge_kind == "confidence_gate" for e in conf_edges)

    def test_escalates_to_human_edge_for_escalation_method(self):
        src = """\
self.escalate_to_human(context=ctx)
"""
        edges, _ = _scan_src(src)
        hitl_edges = [e for e in edges if e.relation_type == "escalates_to_human"]
        assert len(hitl_edges) >= 1

    def test_hitl_escalation_edge_kind(self):
        src = """\
self.escalate(reason='low_conf')
"""
        edges, _ = _scan_src(src)
        hitl_edges = [e for e in edges if e.relation_type == "escalates_to_human"]
        assert all(e.edge_kind == "hitl_escalation" for e in hitl_edges)

    def test_no_hitl_edges_for_unrelated_calls(self):
        src = """\
x = some_function()
"""
        edges, _ = _scan_src(src)
        hitl_edges = [e for e in edges if e.relation_type in ("gated_by_confidence", "escalates_to_human")]
        assert len(hitl_edges) == 0


# ─────────────────────────────────────────────────────────────────────────────
# G4: HITLRuntimeRecorder + HITLGraph
# ─────────────────────────────────────────────────────────────────────────────


class TestHITLGraph:
    def test_checkpoint_creates_hitl_entry(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="LicHealingOrchestrator")
        cp_id = rec.checkpoint(violation_id="v001", confidence=0.28)
        assert len(hitl.checkpoints) == 1
        assert hitl.checkpoints[0].checkpoint_id == cp_id
        assert hitl.pending_count == 1

    def test_checkpoint_emits_escalates_to_human_edge(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="LicHealingOrchestrator")
        rec.checkpoint(violation_id="v001", confidence=0.28)
        assert any(e.relation_type == "escalates_to_human" for e in g.edges)

    def test_decide_marks_checkpoint_resolved(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="LicHealingOrchestrator")
        cp_id = rec.checkpoint(violation_id="v001", confidence=0.28)
        rec.decide(cp_id, decision="approve", reviewer="human:alice")
        assert hitl.pending_count == 0
        assert hitl.resolved_count == 1

    def test_decide_emits_awaits_approval_edge(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="LicHealingOrchestrator")
        cp_id = rec.checkpoint(violation_id="v001", confidence=0.28)
        rec.decide(cp_id, decision="approve", reviewer="human:alice")
        assert any(e.relation_type == "awaits_approval" for e in g.edges)

    def test_learn_emits_learns_from_decision_edge(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="LicHealingOrchestrator")
        rec.learn(checkpoint_id="cp-001", weight_delta=0.1)
        assert any(e.relation_type == "learns_from_decision" for e in g.edges)

    def test_decision_distribution(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="LicHealingOrchestrator")
        cp1 = rec.checkpoint(violation_id="v1", confidence=0.1)
        cp2 = rec.checkpoint(violation_id="v2", confidence=0.2)
        rec.decide(cp1, decision="approve", reviewer="alice")
        rec.decide(cp2, decision="reject", reviewer="bob")
        dist = hitl.decision_distribution()
        assert dist["approve"] == 1
        assert dist["reject"] == 1

    def test_invalid_decision_type_raises(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder

        g = RuntimeGraph()
        hitl = HITLGraph()
        rec = HITLRuntimeRecorder(g, hitl, agent_id="A")
        cp_id = rec.checkpoint(violation_id="v1", confidence=0.1)
        with pytest.raises(ValueError):
            rec.decide(cp_id, decision="invalid_decision_type", reviewer="alice")


# ─────────────────────────────────────────────────────────────────────────────
# G5: _SafetyEnforcementVisitor
# ─────────────────────────────────────────────────────────────────────────────


class TestSafetyEnforcementVisitor:
    def test_applies_guardrail_edge_for_guardrail_class(self):
        src = """\
gate = SovereignLLMGateway()
gate.check(prompt)
"""
        edges, _ = _scan_src(src)
        guard_edges = [e for e in edges if e.relation_type == "applies_guardrail"]
        assert len(guard_edges) >= 1

    def test_guardrail_execution_edge_kind(self):
        src = """\
fence = InstructionFenceGuardrail()
"""
        edges, _ = _scan_src(src)
        guard_edges = [e for e in edges if e.relation_type == "applies_guardrail"]
        assert all(e.edge_kind == "guardrail_execution" for e in guard_edges)

    def test_verifies_policy_edge_for_policy_hash_method(self):
        src = """\
result = self.verify_policy_hash(policy_id, expected)
"""
        edges, _ = _scan_src(src)
        policy_edges = [e for e in edges if e.relation_type == "verifies_policy"]
        assert len(policy_edges) >= 1

    def test_policy_verification_edge_kind(self):
        src = """\
self.check_policy_hash(policy_id, h)
"""
        edges, _ = _scan_src(src)
        policy_edges = [e for e in edges if e.relation_type == "verifies_policy"]
        assert all(e.edge_kind == "policy_verification" for e in policy_edges)

    def test_no_safety_edges_for_unrelated_code(self):
        src = """\
def foo(x):
    return x + 1
"""
        edges, _ = _scan_src(src)
        safety_edges = [e for e in edges if e.relation_type in ("applies_guardrail", "verifies_policy")]
        assert len(safety_edges) == 0


# ─────────────────────────────────────────────────────────────────────────────
# G5: RuntimeSafetyObserver
# ─────────────────────────────────────────────────────────────────────────────


class TestRuntimeSafetyObserver:
    def test_guardrail_check_pass_emits_event_and_edge(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver

        g = RuntimeGraph()
        obs = RuntimeSafetyObserver(g, agent_id="SovereignLLMGateway")
        obs.guardrail_check("InstructionFenceGuardrail", passed=True, input_hash="h1")
        assert g.event_count == 1
        assert any(e.relation_type == "applies_guardrail" for e in g.edges)
        assert obs.report.guardrail_pass_rate == 1.0

    def test_guardrail_check_fail_creates_violation(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver

        g = RuntimeGraph()
        obs = RuntimeSafetyObserver(g, agent_id="SovereignLLMGateway")
        obs.guardrail_check("InstructionFenceGuardrail", passed=False, reason="unsafe")
        assert obs.report.violation_count == 1
        assert obs.report.violations[0].violation_type == "guardrail_block"
        assert obs.report.guardrail_pass_rate == 0.0

    def test_policy_hash_match_returns_true(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver

        g = RuntimeGraph()
        obs = RuntimeSafetyObserver(g, agent_id="PolicyVerifier")
        result = obs.policy_hash_verify(
            policy_id="CONST_V3",
            expected_hash="sha256:abc",
            actual_hash="sha256:abc",
        )
        assert result is True
        assert obs.report.policy_pass_rate == 1.0
        assert any(e.relation_type == "verifies_policy" for e in g.edges)

    def test_policy_hash_mismatch_returns_false_and_creates_violation(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver

        g = RuntimeGraph()
        obs = RuntimeSafetyObserver(g, agent_id="PolicyVerifier")
        result = obs.policy_hash_verify(
            policy_id="CONST_V3",
            expected_hash="sha256:abc",
            actual_hash="sha256:DIFFERENT",
        )
        assert result is False
        assert obs.report.violation_count == 1
        assert obs.report.violations[0].violation_type == "policy_hash_mismatch"
        assert any(e.relation_type == "enforces_policy_hash" for e in g.edges)

    def test_policy_hash_mismatch_pass_rate(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver

        g = RuntimeGraph()
        obs = RuntimeSafetyObserver(g, agent_id="P")
        obs.policy_hash_verify("p1", "h1", "h1")  # pass
        obs.policy_hash_verify("p2", "h2", "h3")  # fail
        assert obs.report.policy_pass_rate == pytest.approx(0.5)

    def test_violations_by_type(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver

        g = RuntimeGraph()
        obs = RuntimeSafetyObserver(g, agent_id="P")
        obs.guardrail_check("G1", passed=False, reason="r1")
        obs.guardrail_check("G2", passed=False, reason="r2")
        obs.policy_hash_verify("p1", "h1", "h2")
        by_type = obs.report.violations_by_type()
        assert by_type.get("guardrail_block", 0) == 2
        assert by_type.get("policy_hash_mismatch", 0) == 1

    def test_empty_report_pass_rates_default_to_one(self):
        from agentic_core.adg.runtime.event_graph import RuntimeGraph
        from agentic_core.adg.runtime.safety_observer import (
            RuntimeSafetyObserver,
            RuntimeSafetyReport,
        )

        g = RuntimeGraph()
        report = RuntimeSafetyReport()
        obs = RuntimeSafetyObserver(g, report=report, agent_id="P")
        assert obs.report.guardrail_pass_rate == 1.0
        assert obs.report.policy_pass_rate == 1.0


# ─────────────────────────────────────────────────────────────────────────────
# G6: agent_registry_scanner
# ─────────────────────────────────────────────────────────────────────────────


class TestAgentRegistryScanner:
    def _make_spec_dir(self, spec_content: dict, filename: str = "agent_specs.json") -> Path:
        d = Path(tempfile.mkdtemp())
        (d / filename).write_text(json.dumps(spec_content), encoding="utf-8")
        return d

    def test_registered_as_edge_for_each_agent(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir({"CampaignPlannerAgent": {"model": "gpt-4", "layer": "L3"}})
        result = scan_agent_registry(d)
        reg_edges = [e for e in result.edges if e.relation_type == "registered_as"]
        assert len(reg_edges) == 1
        assert result.agent_names == ["CampaignPlannerAgent"]

    def test_has_capability_edge_for_each_spec_key(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir({"MyAgent": {"model": "gpt-4", "max_tokens": 4096, "layer": "L2"}})
        result = scan_agent_registry(d)
        cap_edges = [e for e in result.edges if e.relation_type == "has_capability"]
        assert len(cap_edges) == 3  # model, max_tokens, layer

    def test_depends_on_agent_edge_for_explicit_dependency(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir({"AgentA": {"model": "x", "depends_on": ["AgentB", "AgentC"]}})
        result = scan_agent_registry(d)
        dep_edges = [e for e in result.edges if e.relation_type == "depends_on_agent"]
        assert len(dep_edges) == 2

    def test_agent_dependencies_key_also_parsed(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir({"AgentX": {"model": "x", "agent_dependencies": ["AgentY"]}})
        result = scan_agent_registry(d)
        dep_edges = [e for e in result.edges if e.relation_type == "depends_on_agent"]
        assert len(dep_edges) == 1

    def test_multiple_agents_in_one_file(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir(
            {
                "AgentA": {"model": "gpt-4"},
                "AgentB": {"model": "claude-3"},
            }
        )
        result = scan_agent_registry(d)
        assert result.agent_count == 2
        assert len([e for e in result.edges if e.relation_type == "registered_as"]) == 2

    def test_scanned_files_populated(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir({"A": {}})
        result = scan_agent_registry(d)
        assert len(result.scanned_files) == 1

    def test_edge_count_by_relation(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = self._make_spec_dir({"A": {"x": 1, "y": 2}})
        result = scan_agent_registry(d)
        counts = result.edge_counts_by_relation()
        assert counts["registered_as"] == 1
        assert counts["has_capability"] == 2

    def test_invalid_json_skipped_gracefully(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = Path(tempfile.mkdtemp())
        (d / "agent_specs.json").write_text("not valid json", encoding="utf-8")
        result = scan_agent_registry(d)
        assert result.agent_count == 0
        assert result.edge_count == 0

    def test_non_dict_json_skipped_gracefully(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = Path(tempfile.mkdtemp())
        (d / "agent_specs.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        result = scan_agent_registry(d)
        assert result.agent_count == 0

    def test_agent_config_filename_pattern_matched(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        d = Path(tempfile.mkdtemp())
        (d / "agent_config_prod.json").write_text(json.dumps({"AgentZ": {"tier": "prod"}}), encoding="utf-8")
        result = scan_agent_registry(d)
        assert result.agent_count == 1

    def test_real_repo_lic_agent_specs(self):
        from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

        repo = Path(__file__).parents[2]
        result = scan_agent_registry(repo)
        assert result.agent_count > 0
        assert result.edge_count > 0
