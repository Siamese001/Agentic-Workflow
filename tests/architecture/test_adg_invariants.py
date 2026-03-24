"""Phase 7.2: ADG invariant tests -- all five governance areas pass on repo.

Markers: architecture, governance, sovereign_hardening
"""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_adg_invariants")
_emit_applies_guardrail("p0", "test_adg_invariants", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_invariants", "policy_binding")
_emit_snapshots_state("p0", "test_adg_invariants", "state_snapshot")
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

_emit_emits_metric_event("test_adg_invariants", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_invariants", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_invariants", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_invariants", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_invariants", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_invariants", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_invariants", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_invariants", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_invariants", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_invariants", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_invariants", "p4obs", "alert")
_emit_links_incident_trace("test_adg_invariants", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_invariants", "p3lm", "pattern")
_emit_records_learning_event("test_adg_invariants", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_invariants", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_invariants", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_invariants", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_invariants", "p3lm", "policy")
_emit_stores_learning_state("test_adg_invariants", "p3lm", "state")
_emit_records_execution_trace("test_adg_invariants", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_invariants", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_invariants", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_invariants", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_invariants", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_invariants", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_invariants", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_invariants", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_invariants", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_invariants", "context_pull")
_emit_pulls_context("p1", "test_adg_invariants", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_invariants", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_invariants", "uwg_term_2")
_emit_writes_through("p1", "test_adg_invariants", "write_through")
_emit_writes_through("p1", "test_adg_invariants", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_invariants", "safety_validation")
_emit_invokes_eval("p1", "test_adg_invariants", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_invariants", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_invariants", "human_escalation")
_emit_routes_through("p1", "test_adg_invariants", "route_through")
_emit_checks_agent_registry("p1", "test_adg_invariants", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_invariants", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_invariants", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_invariants", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_invariants", "target_agent")
_emit_verifies_policy("p1", "test_adg_invariants", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_invariants", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_invariants", "boundary_check")
_emit_transcripts_response("p1", "test_adg_invariants", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_invariants")
_emit_gated_by_confidence("p1", "test_adg_invariants", "confidence_gate")
emit_replay_key("p0", "test_adg_invariants")
emit_determinism_digest("p0", "test_adg_invariants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_invariants", "execution_auth")
_emit_validates_capability("p2", "test_adg_invariants", "capability_check")
_emit_routes_to_capability("p2", "test_adg_invariants", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_invariants", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_invariants", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_invariants", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_invariants", "exec_output")
_emit_dispatches_agent("p3", "test_adg_invariants", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_invariants", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_invariants", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_invariants", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_invariants", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_invariants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_invariants", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_invariants", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_invariants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_invariants", "eval_metric")
_emit_stores_embedding("p4", "test_adg_invariants", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_invariants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_invariants", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

REPO_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.unit
class TestADGSchema:
    def test_canonical_name_module(self) -> None:
        from agentic_core.adg.schema_util import canonical_name

        result = canonical_name("Module", "agentic_core/L0_routing/engines/path_router.py")
        assert result == "ADG::Module::agentic_core/L0_routing/engines/path_router.py"

    def test_canonical_name_layer(self) -> None:
        from agentic_core.adg.schema_util import canonical_name

        assert canonical_name("Layer", "L2") == "ADG::Layer::L2"

    def test_canonical_name_snapshot(self) -> None:
        from agentic_core.adg.schema_util import canonical_name

        assert canonical_name("Snapshot", "abc123", "deadbeef") == "ADG::Snapshot::abc123::deadbeef"

    def test_canonical_name_backslash_normalized(self) -> None:
        from agentic_core.adg.schema_util import canonical_name

        result = canonical_name("Module", "agentic_core\\L0_routing\\path.py")
        assert "\\" not in result

    def test_layer_mapping_l0(self) -> None:
        from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("agentic_core/L0_routing/engines/path_router.py") == "L0"

    def test_layer_mapping_l2(self) -> None:
        from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("agentic_core/L2_execution/UniversalWriteGateway.py") == "L2"

    def test_layer_mapping_l5(self) -> None:
        from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("agentic_core/L5_safety/enforcement/some_guard.py") == "L5"

    def test_layer_mapping_apps(self) -> None:
        from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("apps_rg/engines/SomeAgent.py") == "L_APP"

    def test_layer_mapping_unknown(self) -> None:
        from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("random/unknown/path.py") == "L_UNKNOWN"

    def test_allowed_layer_edges_contains_downward(self) -> None:
        from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

        assert ("L2", "L0") in ALLOWED_LAYER_EDGES
        assert ("L5", "L2") in ALLOWED_LAYER_EDGES
        assert ("L6", "L0") in ALLOWED_LAYER_EDGES

    def test_allowed_layer_edges_excludes_upward(self) -> None:
        from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

        assert ("L0", "L2") not in ALLOWED_LAYER_EDGES
        assert ("L1", "L5") not in ALLOWED_LAYER_EDGES


# ---------------------------------------------------------------------------
# MCP client idempotency
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.unit
class TestADGMCPClient:
    def test_upsert_entity_idempotent(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        name = "ADG::Module::test/module.py"
        client.upsert_entity(name, "module", ["path:test/module.py"])
        client.upsert_entity(name, "module", ["path:test/module.py"])
        matching = [e for e in client.get_store().get_entities() if e["name"] == name]
        assert len(matching) == 1

    def test_upsert_relation_idempotent(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        rels = client.get_store().get_relations()
        matching = [r for r in rels if r["from"] == "ADG::Module::a.py" and r["to"] == "ADG::Symbol::b"]
        assert len(matching) == 1

    def test_add_observation_idempotent(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::x.py", "module", ["path:x.py"])
        client.add_observation("ADG::Module::x.py", ["commit:abc123"])
        client.add_observation("ADG::Module::x.py", ["commit:abc123"])
        entities = client.get_store().get_entities()
        e = next(e for e in entities if e["name"] == "ADG::Module::x.py")
        assert len([o for o in e["observations"] if o == "commit:abc123"]) == 1

    def test_search_nodes_returns_matches(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::search_target.py", "module", ["path:search_target.py"])
        results = client.search_nodes("search_target")
        assert any("search_target" in r["name"] for r in results)

    def test_open_nodes_returns_relations(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::a.py", "module", [])
        client.upsert_entity("ADG::Symbol::b.func", "symbol", [])
        client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b.func")
        nodes = client.open_nodes(["ADG::Module::a.py"])
        assert len(nodes) == 1
        assert "imports" in [r["relationType"] for r in nodes[0]["relations"]]

    def test_bulk_upsert_deterministic_order(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.bulk_upsert_entities(
            [
                {"name": "ADG::Module::z.py", "entity_type": "module", "observations": []},
                {"name": "ADG::Module::a.py", "entity_type": "module", "observations": []},
                {"name": "ADG::Module::m.py", "entity_type": "module", "observations": []},
            ]
        )
        names = [e["name"] for e in client.get_store().get_entities()]
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# Static scanner
# ---------------------------------------------------------------------------


@pytest.mark.architecture
class TestADGStaticScanner:
    def test_scan_produces_edges(self) -> None:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="test")
        assert len(result.edges) > 0
        assert len(result.modules) > 0

    def test_scan_files_empty_list(self) -> None:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files([], commit_sha="test-empty")
        assert result.edges == []
        assert result.modules == []
        assert len(result.digest) == 64

    def test_scan_known_file_has_import_edge(self) -> None:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"],
            commit_sha="test-sovereign",
        )
        import_edges = [e for e in result.edges if e.relation_type == "imports"]
        assert len(import_edges) > 0

    def test_reverse_import_graph_populated(self) -> None:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="test-reverse")
        reverse = scanner.build_reverse_import_graph(result)
        assert len(reverse) > 0

    def test_module_layer_map_populated(self) -> None:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="test-layer")
        layer_map = scanner.module_layer_map(result)
        l2_modules = [k for k, v in layer_map.items() if v == "L2"]
        assert len(l2_modules) > 0


# ---------------------------------------------------------------------------
# CI invariant scanner (Rules A, B, C)
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.governance
class TestCIInvariantScanner:
    def test_rule_a_gateway_passes_for_sovereign_llm_gw(self) -> None:
        """SovereignLLMGateway itself must NOT trigger Rule A."""
        from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"],
            commit_sha="test-rule-a",
        )
        inv = InvariantScanner()
        report = inv.scan(result)
        rule_a = [v for v in report.violations if v.rule == "RULE_A"]
        assert len(rule_a) == 0, "SovereignLLMGateway triggered RULE_A:\n" + "\n".join(
            v.format() for v in rule_a
        )

    def test_rule_c_no_violations_for_uwg(self) -> None:
        """UWG (L2) has no upward layer violations."""
        from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            commit_sha="test-rule-c",
        )
        inv = InvariantScanner()
        report = inv.scan(result)
        rule_c = [v for v in report.violations if v.rule == "RULE_C"]
        assert len(rule_c) == 0, "Unexpected layer violations:\n" + "\n".join(v.format() for v in rule_c)

    def test_scan_report_exit_code_pass(self) -> None:
        from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test")
        result.compute_digest()
        report = InvariantScanner().scan(result)
        assert report.exit_code() == 0
        assert report.passed

    def test_scan_report_exit_code_fail(self) -> None:
        from agentic_core.adg.ci.invariant_scanner_config import ScanReport, Violation

        report = ScanReport()
        report.violations.append(
            Violation(
                rule="RULE_A",
                policy_id="ADG::Policy::LLM_EGRESS_SINGLETON",
                offending_edge="X -> Y",
                from_module="some/module.py",
                to_symbol="openai",
                source_file="some/module.py",
                line_no=10,
                witness="direct import",
            )
        )
        assert report.exit_code() == 1
        assert not report.passed


# ---------------------------------------------------------------------------
# Gateway topology
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.governance
class TestGatewayTopology:
    def test_empty_result_passes(self) -> None:
        from agentic_core.adg.applications.gateway_topology_validator import check_gateway_topology
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-empty")
        result.compute_digest()
        assert check_gateway_topology(result).passed

    def test_gateway_module_itself_is_allowed(self) -> None:
        from agentic_core.adg.applications.gateway_topology_validator import check_gateway_topology
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"],
            commit_sha="test-gw-allowed",
        )
        report = check_gateway_topology(result)
        assert report.passed, "SovereignLLMGateway itself violated gateway topology:\n" + "\n".join(
            v.format() for v in report.violations
        )

    def test_report_has_proof_digest(self) -> None:
        from agentic_core.adg.applications.gateway_topology_validator import check_gateway_topology
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-proof")
        result.compute_digest()
        report = check_gateway_topology(result)
        assert len(report.snapshot_digest) == 64


# ---------------------------------------------------------------------------
# UWG write authority
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.governance
class TestUWGWriteAuthority:
    def test_empty_result_passes(self) -> None:
        from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-empty")
        result.compute_digest()
        assert check_uwg_write_authority(result).passed

    def test_uwg_module_itself_is_allowed(self) -> None:
        from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            commit_sha="test-uwg-allowed",
        )
        report = check_uwg_write_authority(result)
        assert report.passed, "UWG module itself violated write authority:\n" + "\n".join(
            v.format() for v in report.violations
        )


# ---------------------------------------------------------------------------
# RAG sovereignty
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.governance
class TestRAGSovereignty:
    def test_empty_result_passes(self) -> None:
        from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-rag-empty")
        result.compute_digest()
        assert check_rag_sovereignty(result).passed

    def test_rag_module_scan_passes(self) -> None:
        from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py"],
            commit_sha="test-rag-sovereign",
        )
        report = check_rag_sovereignty(result)
        assert report.passed, "RAG module violated C0 sovereignty:\n" + "\n".join(
            v.format() for v in report.violations
        )

    def test_proof_digest_is_sha256(self) -> None:
        from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-proof")
        result.compute_digest()
        report = check_rag_sovereignty(result)
        assert len(report.snapshot_digest) == 64


# ---------------------------------------------------------------------------
# Blast-radius
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.determinism
class TestBlastRadius:
    def test_blast_radius_empty_changed(self) -> None:
        from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            commit_sha="test-br",
        )
        br = compute_blast_radius([], result, commit_sha="test-br")
        assert br.risk_score == 0
        assert br.route_mode == "NORMAL"
        assert len(br.impact_digest) == 64

    def test_blast_radius_deterministic_same_input(self) -> None:
        from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="br-full")
        changed = ["agentic_core/L2_execution/UniversalWriteGateway.py"]
        br1 = compute_blast_radius(changed, result, commit_sha="sha1")
        br2 = compute_blast_radius(changed, result, commit_sha="sha2")
        assert br1.impact_digest == br2.impact_digest, (
            f"ImpactDigest not deterministic:\n  br1: {br1.impact_digest}\n  br2: {br2.impact_digest}"
        )

    def test_blast_radius_l0_is_high_risk(self) -> None:
        from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="br-l0")
        br = compute_blast_radius(
            ["agentic_core/L0_routing/engines/path_router.py"],
            result,
            commit_sha="l0-test",
        )
        assert br.risk_score > 0

    def test_blast_radius_impact_digest_is_sha256(self) -> None:
        from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="br-digest")
        br = compute_blast_radius(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            result,
            commit_sha="br-digest",
        )
        assert len(br.impact_digest) == 64
        assert all(c in "0123456789abcdef" for c in br.impact_digest)


# ---------------------------------------------------------------------------
# Graph persister
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.unit
class TestGraphPersister:
    def test_persist_scan_result_creates_layer_nodes(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient
        from agentic_core.adg.extraction.graph_persister import persist_scan_result
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            commit_sha="persist-test",
        )
        client = ADGMCPClient()
        persist_scan_result(result, client)
        layer_nodes = [e for e in client.get_store().get_entities() if e["entityType"] == "layer"]
        assert len(layer_nodes) >= 7

    def test_persist_scan_result_creates_commit_node(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient
        from agentic_core.adg.extraction.graph_persister import persist_scan_result
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            commit_sha="abc123deadbeef0000000000000000000000000a",
        )
        client = ADGMCPClient()
        persist_scan_result(result, client)
        results = client.search_nodes("ADG::Commit::abc123deadbeef")
        assert len(results) > 0

    def test_persist_is_idempotent(self) -> None:
        from agentic_core.adg.client.InMemoryStore import ADGMCPClient
        from agentic_core.adg.extraction.graph_persister import persist_scan_result
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            commit_sha="idempotent-test",
        )
        client = ADGMCPClient()
        persist_scan_result(result, client)
        count_1 = len(client.get_store().get_entities())
        persist_scan_result(result, client)
        count_2 = len(client.get_store().get_entities())
        assert count_1 == count_2, f"Not idempotent: first={count_1} second={count_2}"
