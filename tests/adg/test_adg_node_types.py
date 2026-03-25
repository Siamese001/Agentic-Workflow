"""Tests for Phase 2 node type materialization (G7-G11).

Covers:
- G7: Layer nodes get entity_type=layer in builder.py
- G8: Gateway nodes materialized with entity_type=gateway
- G9: Seam modules promoted to entity_type=seam
- G10: Provider SDK symbols get entity_type=provider
- G11: 3 missing LAYER_PREFIXES entries in schema.py
- G2: PromptSlot/PromptTemplate entity_type correctly set
"""

from __future__ import annotations

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_node_types")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_node_types", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_node_types", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_node_types", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_adg_node_types", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_node_types", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_node_types", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_node_types", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_node_types", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_node_types", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_node_types", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_node_types", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_node_types", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_node_types", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_node_types", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_node_types", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_node_types", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_node_types", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_node_types", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_node_types", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_node_types", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_node_types", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_node_types", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_node_types", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_node_types", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_node_types", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_node_types", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_node_types", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_node_types", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_node_types", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_node_types", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_node_types", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_node_types", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_node_types", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_node_types", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_node_types", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_node_types", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_node_types", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_node_types", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_node_types", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_node_types", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_node_types", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_node_types", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_node_types", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_node_types", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_node_types", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_node_types", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_node_types", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_node_types", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_node_types", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_node_types", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_node_types", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_node_types")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_node_types", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_node_types")
# REMOVED: emit_determinism_digest("p0", "test_adg_node_types")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_node_types", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_node_types", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_node_types", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_node_types", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_node_types", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_node_types", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_node_types", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_node_types", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_node_types", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_node_types", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_node_types", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_node_types", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_node_types", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_node_types", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_node_types", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_node_types", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_node_types", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_node_types", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_node_types", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_node_types", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_scan_result_with_edges(edges):
    """Build a minimal ScanResult-like object for builder tests."""
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="test_sha")
    result.edges = edges
    result.modules = []
    result.syntax_errors = []
    result.compute_digest()
    return result


def _make_edge(from_name, relation_type, to_name, edge_kind="import", source_file="test.py", symbol=""):
    from agentic_core.adg.extraction.static_scanner import Edge

    return Edge(
        from_name=from_name,
        relation_type=relation_type,
        to_name=to_name,
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=1,
        symbol=symbol,
    )


def _build_artifact(edges, modules=None):
    from agentic_core.adg.artifact.builder_types import ADGArtifactBuilder

    result = _make_scan_result_with_edges(edges)
    if modules:
        result.modules = modules
    builder = ADGArtifactBuilder(repo_root=ROOT)
    return builder.build(result)


# ---------------------------------------------------------------------------
# G7: Layer nodes entity_type=layer
# ---------------------------------------------------------------------------


class TestG7LayerEntityType:
    def test_layer_node_gets_layer_entity_type(self):
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/L2_execution/UniversalWriteGateway.py",
                "violates",
                "ADG::Layer::L1",
                edge_kind="import",
                symbol="L2->L1",
            )
        ]
        artifact = _build_artifact(edges)
        layer_entities = [e for e in artifact.entities if e.adg_name == "ADG::Layer::L1"]
        assert layer_entities, "ADG::Layer::L1 node should be materialized"
        assert layer_entities[0].entity_type == "layer", (
            f"Layer node entity_type should be 'layer', got '{layer_entities[0].entity_type}'"
        )

    def test_layer_node_has_correct_layer_field(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "violates",
                "ADG::Layer::L3",
                symbol="L0->L3",
            )
        ]
        artifact = _build_artifact(edges)
        layer_entity = next((e for e in artifact.entities if e.adg_name == "ADG::Layer::L3"), None)
        assert layer_entity is not None
        assert layer_entity.layer == "L3"


# ---------------------------------------------------------------------------
# G8: Gateway nodes materialized
# ---------------------------------------------------------------------------


class TestG8GatewayNodes:
    def test_gateway_node_gets_gateway_entity_type(self):
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/L2_execution/SomeAgent.py",
                "writes_through",
                "ADG::Gateway::UniversalWriteGateway",
                edge_kind="write",
            )
        ]
        artifact = _build_artifact(edges)
        gw_entities = [e for e in artifact.entities if e.adg_name == "ADG::Gateway::UniversalWriteGateway"]
        assert gw_entities, "ADG::Gateway::UniversalWriteGateway should be materialized"
        assert gw_entities[0].entity_type == "gateway"

    def test_gateway_node_has_resolved_path(self):
        from agentic_core.adg.schema_util import GATEWAY_ALLOWLIST

        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "routes_through",
                "ADG::Gateway::SovereignLLMGateway",
                edge_kind="call",
            )
        ]
        artifact = _build_artifact(edges)
        gw = next((e for e in artifact.entities if "SovereignLLMGateway" in e.adg_name), None)
        assert gw is not None
        expected_path = GATEWAY_ALLOWLIST.get("SovereignLLMGateway", "")
        assert gw.resolved_path == expected_path


# ---------------------------------------------------------------------------
# G9: Seam modules get entity_type=seam
# ---------------------------------------------------------------------------


class TestG9SeamEntityType:
    def test_seam_module_gets_seam_entity_type(self):
        from agentic_core.adg.schema_util import SEAM_MODULE_PATTERNS

        if not SEAM_MODULE_PATTERNS:
            pytest.skip("No SEAM_MODULE_PATTERNS defined")
        seam_path = SEAM_MODULE_PATTERNS[0] + "some_seam.py"
        edges = [
            _make_edge(
                "ADG::Module::some/caller.py",
                "calls",
                f"ADG::Module::{seam_path}",
                edge_kind="call",
            )
        ]
        artifact = _build_artifact(edges)
        seam_entity = next((e for e in artifact.entities if seam_path in e.adg_name), None)
        assert seam_entity is not None, f"Seam module {seam_path} should be materialized"
        assert seam_entity.entity_type == "seam", (
            f"Seam module should have entity_type='seam', got '{seam_entity.entity_type}'"
        )

    def test_non_seam_module_stays_module(self):
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/L2_execution/SomeAgent.py",
                "calls",
                "ADG::Module::agentic_core/L1_cognition/reasoning.py",
                edge_kind="call",
            )
        ]
        artifact = _build_artifact(edges)
        non_seam = next((e for e in artifact.entities if "L1_cognition/reasoning.py" in e.adg_name), None)
        if non_seam:
            assert non_seam.entity_type == "module"

    def test_is_seam_module_helper(self):
        from agentic_core.adg.artifact.builder_types import ADGArtifactBuilder

        assert ADGArtifactBuilder._is_seam_module("agentic_core/L0_routing/seams/some_seam.py")
        assert ADGArtifactBuilder._is_seam_module("agentic_core/seams/my_seam.py")
        assert not ADGArtifactBuilder._is_seam_module("agentic_core/L2_execution/SomeAgent.py")
        assert not ADGArtifactBuilder._is_seam_module("apps_rg/engines/ats_engine.py")


# ---------------------------------------------------------------------------
# G10: Provider SDK symbols get entity_type=provider
# ---------------------------------------------------------------------------


class TestG10ProviderEntityType:
    def test_openai_symbol_gets_provider_entity_type(self):
        edges = [
            _make_edge(
                "ADG::Module::agentic_core/L2_execution/SomeAgent.py",
                "invokes_provider",
                "ADG::Symbol::openai.ChatCompletion",
                edge_kind="network",
                symbol="openai.ChatCompletion",
            )
        ]
        artifact = _build_artifact(edges)
        provider = next((e for e in artifact.entities if "openai.ChatCompletion" in e.adg_name), None)
        assert provider is not None
        assert provider.entity_type == "provider", (
            f"openai symbol should have entity_type='provider', got '{provider.entity_type}'"
        )

    def test_anthropic_symbol_gets_provider_entity_type(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "invokes_provider",
                "ADG::Symbol::anthropic.Anthropic",
                edge_kind="network",
                symbol="anthropic.Anthropic",
            )
        ]
        artifact = _build_artifact(edges)
        provider = next((e for e in artifact.entities if "anthropic.Anthropic" in e.adg_name), None)
        assert provider is not None
        assert provider.entity_type == "provider"

    def test_internal_symbol_stays_symbol(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "calls",
                "ADG::Symbol::agentic_core.some_func",
                edge_kind="call",
                symbol="agentic_core.some_func",
            )
        ]
        artifact = _build_artifact(edges)
        sym = next((e for e in artifact.entities if "agentic_core.some_func" in e.adg_name), None)
        if sym:
            assert sym.entity_type == "symbol"


# ---------------------------------------------------------------------------
# G2: PromptSlot / PromptTemplate entity_type
# ---------------------------------------------------------------------------


class TestG2PromptEntityTypes:
    def test_prompt_slot_gets_correct_entity_type(self):
        edges = [
            _make_edge(
                "ADG::Module::apps_rg/reasoning/SomeAgent.py",
                "generates_prompt",
                "ADG::PromptSlot::S0::apps_rg/reasoning/SomeAgent.py",
                edge_kind="prompt_generation",
                symbol="S0:s0_system",
            )
        ]
        artifact = _build_artifact(edges)
        slot = next((e for e in artifact.entities if "ADG::PromptSlot::" in e.adg_name), None)
        assert slot is not None, "PromptSlot node should be materialized"
        assert slot.entity_type == "prompt_slot", (
            f"PromptSlot should have entity_type='prompt_slot', got '{slot.entity_type}'"
        )

    def test_prompt_template_gets_correct_entity_type(self):
        edges = [
            _make_edge(
                "ADG::Module::apps_rg/reasoning/SomeAgent.py",
                "consumes_prompt",
                "ADG::PromptTemplate::CONSTITUTION",
                edge_kind="prompt_consumption",
                symbol="CONSTITUTION",
            )
        ]
        artifact = _build_artifact(edges)
        tmpl = next((e for e in artifact.entities if "ADG::PromptTemplate::" in e.adg_name), None)
        assert tmpl is not None, "PromptTemplate node should be materialized"
        assert tmpl.entity_type == "prompt_template", (
            f"PromptTemplate should have entity_type='prompt_template', got '{tmpl.entity_type}'"
        )

    def test_prompt_slot_layer_is_l_pg(self):
        edges = [
            _make_edge(
                "ADG::Module::test.py",
                "generates_prompt",
                "ADG::PromptSlot::D0::test.py",
                edge_kind="prompt_generation",
            )
        ]
        artifact = _build_artifact(edges)
        slot = next((e for e in artifact.entities if "ADG::PromptSlot::" in e.adg_name), None)
        assert slot is not None
        assert slot.layer == "L_PG"


# ---------------------------------------------------------------------------
# G11: LAYER_PREFIXES has all required entries
# ---------------------------------------------------------------------------


class TestG11LayerPrefixes:
    def test_compat_dir_mapped(self):
        from agentic_core.adg.schema_util import LAYER_PREFIXES

        assert "agentic_core/_compat" in LAYER_PREFIXES, (
            "agentic_core/_compat must be in LAYER_PREFIXES (G11)"
        )

    def test_embeddings_dir_mapped(self):
        from agentic_core.adg.schema_util import LAYER_PREFIXES

        assert "agentic_core/embeddings" in LAYER_PREFIXES, (
            "agentic_core/embeddings must be in LAYER_PREFIXES (G11)"
        )

    def test_enforcement_dir_mapped(self):
        from agentic_core.adg.schema_util import LAYER_PREFIXES

        assert "agentic_core/enforcement" in LAYER_PREFIXES, (
            "agentic_core/enforcement must be in LAYER_PREFIXES (G11)"
        )

    def test_new_entries_map_to_l_shared(self):
        from agentic_core.adg.schema_util import LAYER_PREFIXES

        for key in ("agentic_core/_compat", "agentic_core/embeddings", "agentic_core/enforcement"):
            assert LAYER_PREFIXES.get(key) == "L_SHARED", f"{key} should map to L_SHARED in LAYER_PREFIXES"

    def test_module_path_to_layer_resolves_new_entries(self):
        from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("agentic_core/_compat/some_module.py") == "L_SHARED"
        assert module_path_to_layer("agentic_core/embeddings/vertex.py") == "L_SHARED"
        assert module_path_to_layer("agentic_core/enforcement/rules.py") == "L_SHARED"
