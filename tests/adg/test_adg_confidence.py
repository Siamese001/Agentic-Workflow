"""Tests for Phase 4 confidence scoring and structural integrity (G17).

Covers:
- G17: Evidence-based confidence scoring in builder.py (module=HIGH, external=LOW, unresolved=NONE)
- Structural integrity: no duplicate entities in artifact
- Artifact digest determinism
- Structural metrics correctness with new node types
"""

from __future__ import annotations

import sys
from pathlib import Path

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_confidence")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_confidence", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_confidence", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_confidence", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_confidence", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_confidence", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_confidence", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_confidence", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_confidence", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_confidence", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_confidence", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_confidence", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_confidence", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_confidence", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_confidence", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_confidence", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_confidence", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_confidence", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_confidence", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_confidence", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_confidence", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_confidence", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_confidence", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_confidence", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_confidence", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_confidence", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_confidence", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_confidence", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_confidence", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_confidence", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_confidence", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_confidence", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_confidence", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_confidence", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_confidence", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_confidence", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_confidence", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_confidence", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_confidence", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_confidence", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_confidence", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_confidence", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_confidence", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_confidence", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_confidence", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_confidence", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_confidence", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_confidence", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_confidence", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_confidence", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_confidence", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_confidence", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_confidence")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_confidence", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_confidence")
# REMOVED: emit_determinism_digest("p0", "test_adg_confidence")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_confidence", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_confidence", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_confidence", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_confidence", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_confidence", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_confidence", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_confidence", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_confidence", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_confidence", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_confidence", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_confidence", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_confidence", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_confidence", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_confidence", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_confidence", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_confidence", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_confidence", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_confidence", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_confidence", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_confidence", "exec_snapshot_link")

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


def _build_artifact(edges, modules=None):
    from agentic_core.adg.artifact.builder_types import ADGArtifactBuilder
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="test_sha")
    result.edges = edges
    result.modules = modules or []
    result.syntax_errors = []
    result.compute_digest()
    builder = ADGArtifactBuilder(repo_root=ROOT)
    return builder.build(result)


# ---------------------------------------------------------------------------
# G17: Confidence scoring
# ---------------------------------------------------------------------------


class TestG17ConfidenceScoring:
    def test_repo_module_confidence_is_high(self):
        artifact = _build_artifact(
            edges=[],
            modules=["agentic_core/L2_execution/SomeAgent.py"],
        )
        module_entities = [
            e for e in artifact.entities if e.entity_type == "module" and "SomeAgent.py" in e.adg_name
        ]
        assert module_entities, "Module entity should be materialized"
        assert module_entities[0].confidence == "HIGH"

    def test_layer_node_confidence_is_high(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "violates",
                "ADG::Layer::L2",
                symbol="L0->L2",
            )
        ]
        artifact = _build_artifact(edges)
        layer_ent = next((e for e in artifact.entities if e.adg_name == "ADG::Layer::L2"), None)
        assert layer_ent is not None
        assert layer_ent.confidence == "HIGH"

    def test_gateway_node_confidence_is_high(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "writes_through",
                "ADG::Gateway::UniversalWriteGateway",
                edge_kind="write",
            )
        ]
        artifact = _build_artifact(edges)
        gw = next((e for e in artifact.entities if "ADG::Gateway::" in e.adg_name), None)
        assert gw is not None
        assert gw.confidence == "HIGH"

    def test_prompt_slot_confidence_is_high(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "generates_prompt",
                "ADG::PromptSlot::S0::test.py",
                edge_kind="prompt_generation",
            )
        ]
        artifact = _build_artifact(edges)
        slot = next((e for e in artifact.entities if "ADG::PromptSlot::" in e.adg_name), None)
        assert slot is not None
        assert slot.confidence == "HIGH"

    def test_provider_symbol_confidence_is_high(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "invokes_provider",
                "ADG::Symbol::openai.ChatCompletion",
                edge_kind="network",
                symbol="openai.ChatCompletion",
            )
        ]
        artifact = _build_artifact(edges)
        provider = next((e for e in artifact.entities if "openai.ChatCompletion" in e.adg_name), None)
        assert provider is not None
        assert provider.confidence == "HIGH"


# ---------------------------------------------------------------------------
# Structural integrity: no duplicate entities
# ---------------------------------------------------------------------------


class TestNoDuplicateEntities:
    def test_no_duplicate_adg_names(self):
        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::os.path", symbol="os.path"),
            _make_edge("ADG::Module::b.py", "imports", "ADG::Symbol::os.path", symbol="os.path"),
        ]
        artifact = _build_artifact(edges)
        adg_names = [e.adg_name for e in artifact.entities]
        assert len(adg_names) == len(set(adg_names)), "No two entities should share the same adg_name"

    def test_no_duplicate_module_and_symbol_for_same_name(self):
        # If a module is referenced both from edges (as from_name) and in modules list,
        # it should only appear once.
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/L2_execution/SomeAgent.py",
                "imports",
                "ADG::Symbol::os",
                symbol="os",
            )
        ]
        artifact = _build_artifact(
            edges,
            modules=["agentic_core/L2_execution/SomeAgent.py"],
        )
        agent_entities = [e for e in artifact.entities if "SomeAgent.py" in e.adg_name]
        assert len(agent_entities) == 1, (
            "Module referenced in both edges and modules list should only appear once"
        )

    def test_layer_node_not_duplicated(self):
        edges = [
            _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L1", symbol="L0->L1"),
            _make_edge("ADG::Module::b.py", "violates", "ADG::Layer::L1", symbol="L0->L1"),
        ]
        artifact = _build_artifact(edges)
        l1_entities = [e for e in artifact.entities if e.adg_name == "ADG::Layer::L1"]
        assert len(l1_entities) == 1, "ADG::Layer::L1 should only appear once even with multiple references"


# ---------------------------------------------------------------------------
# Artifact digest determinism
# ---------------------------------------------------------------------------


class TestArtifactDigestDeterminism:
    def test_same_edges_produce_same_digest(self):
        edges = [
            _make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::os", symbol="os"),
            _make_edge("ADG::Module::b.py", "calls", "ADG::Symbol::some_func", symbol="some_func"),
        ]
        a1 = _build_artifact(edges)
        a2 = _build_artifact(edges)
        assert a1.artifact_digest == a2.artifact_digest, (
            "Same ScanResult must always produce the same artifact_digest"
        )

    def test_different_edges_produce_different_digest(self):
        edges1 = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::os", symbol="os")]
        edges2 = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::sys", symbol="sys")]
        a1 = _build_artifact(edges1)
        a2 = _build_artifact(edges2)
        assert a1.artifact_digest != a2.artifact_digest, (
            "Different ScanResults must produce different artifact_digests"
        )

    def test_digest_is_non_empty(self):
        edges = [_make_edge("ADG::Module::a.py", "imports", "ADG::Symbol::os", symbol="os")]
        artifact = _build_artifact(edges)
        assert artifact.artifact_digest, "artifact_digest must not be empty"
        assert len(artifact.artifact_digest) == 64, "SHA256 digest must be 64 hex chars"


# ---------------------------------------------------------------------------
# Structural metrics with new node types
# ---------------------------------------------------------------------------


class TestStructuralMetricsWithNewNodeTypes:
    def test_total_entities_counts_all_types(self):
        edges = [
            _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L1", symbol="L0->L1"),
            _make_edge("ADG::Module::a.py", "writes_through", "ADG::Gateway::UniversalWriteGateway"),
            _make_edge("ADG::Module::a.py", "generates_prompt", "ADG::PromptSlot::S0::a.py"),
        ]
        artifact = _build_artifact(edges, modules=["a.py"])
        assert artifact.structural_metrics.total_entities >= 4, (
            "Total entities should count module + layer + gateway + prompt_slot nodes"
        )

    def test_relation_type_distribution_includes_new_types(self):
        edges = [
            _make_edge("ADG::Module::a.py", "invokes_dynamic", "ADG::Symbol::eval", edge_kind="dynamic_exec"),
            _make_edge("ADG::Module::b.py", "decorated_by", "ADG::Symbol::some_deco", edge_kind="decorator"),
            _make_edge("ADG::Module::c.py", "reads_env", "ADG::Symbol::os.getenv", edge_kind="reads_env"),
        ]
        artifact = _build_artifact(edges)
        by_rel = artifact.structural_metrics.by_relation_type
        assert "invokes_dynamic" in by_rel, "invokes_dynamic should appear in by_relation_type"
        assert "decorated_by" in by_rel, "decorated_by should appear in by_relation_type"
        assert "reads_env" in by_rel, "reads_env should appear in by_relation_type"

    def test_module_count_excludes_layer_gateway_nodes(self):
        edges = [
            _make_edge("ADG::Module::a.py", "violates", "ADG::Layer::L1", symbol="L0->L1"),
        ]
        artifact = _build_artifact(edges, modules=["a.py"])
        # Layer node should not count toward module_count
        assert artifact.structural_metrics.module_count >= 1
        layer_entities = [e for e in artifact.entities if e.entity_type == "layer"]
        assert layer_entities, "Layer entities should exist"
        # module_count counts entity_type==module only
        module_count = sum(1 for e in artifact.entities if e.entity_type == "module")
        assert artifact.structural_metrics.module_count == module_count


# ---------------------------------------------------------------------------
# Integration: scan + build pipeline with new relation types
# ---------------------------------------------------------------------------


class TestIntegrationNewRelationTypes:
    def test_artifact_can_serialize_new_relation_types(self):
        import json

        edges = [
            _make_edge("ADG::Module::a.py", "invokes_dynamic", "ADG::Symbol::eval", edge_kind="dynamic_exec"),
            _make_edge("ADG::Module::a.py", "decorated_by", "ADG::Symbol::deco", edge_kind="decorator"),
            _make_edge("ADG::Module::a.py", "reads_env", "ADG::Symbol::os.getenv", edge_kind="reads_env"),
            _make_edge("ADG::Module::a.py", "seam_bypass", "ADG::Symbol::openai.create", edge_kind="network"),
        ]
        artifact = _build_artifact(edges)
        # Must serialize without error
        d = artifact.to_dict()
        serialized = json.dumps(d)
        assert serialized, "Artifact with new relation types must serialize cleanly"

    def test_artifact_contains_all_new_relation_types(self):
        edges = [
            _make_edge("ADG::Module::a.py", "invokes_dynamic", "ADG::Symbol::eval", edge_kind="dynamic_exec"),
            _make_edge("ADG::Module::a.py", "decorated_by", "ADG::Symbol::deco", edge_kind="decorator"),
            _make_edge("ADG::Module::a.py", "reads_env", "ADG::Symbol::os.getenv", edge_kind="reads_env"),
            _make_edge(
                "ADG::Module::a.py", "reads_secret", "ADG::Symbol::get_secret", edge_kind="reads_secret"
            ),
            _make_edge(
                "ADG::Module::a.py",
                "reads_policy_state",
                "ADG::Symbol::get_policy",
                edge_kind="reads_policy_state",
            ),
        ]
        artifact = _build_artifact(edges)
        rel_types = {r.relation_type for r in artifact.relations}
        assert "invokes_dynamic" in rel_types
        assert "decorated_by" in rel_types
        assert "reads_env" in rel_types
        assert "reads_secret" in rel_types
        assert "reads_policy_state" in rel_types
