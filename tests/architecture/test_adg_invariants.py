"""Phase 7.2: ADG invariant tests -- all five governance areas pass on repo.

Markers: architecture, governance, sovereign_hardening
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_invariants")
_emit_applies_guardrail("p0", "test_adg_invariants", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_invariants", "policy_binding")
_emit_snapshots_state("p0", "test_adg_invariants", "state_snapshot")
emit_replay_key("p0", "test_adg_invariants")
emit_determinism_digest("p0", "test_adg_invariants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        from agentic_core.adg.schema import canonical_name

        result = canonical_name("Module", "agentic_core/L0_routing/engines/path_router.py")
        assert result == "ADG::Module::agentic_core/L0_routing/engines/path_router.py"

    def test_canonical_name_layer(self) -> None:
        from agentic_core.adg.schema import canonical_name

        assert canonical_name("Layer", "L2") == "ADG::Layer::L2"

    def test_canonical_name_snapshot(self) -> None:
        from agentic_core.adg.schema import canonical_name

        assert canonical_name("Snapshot", "abc123", "deadbeef") == "ADG::Snapshot::abc123::deadbeef"

    def test_canonical_name_backslash_normalized(self) -> None:
        from agentic_core.adg.schema import canonical_name

        result = canonical_name("Module", "agentic_core\\L0_routing\\path.py")
        assert "\\" not in result

    def test_layer_mapping_l0(self) -> None:
        from agentic_core.adg.schema import module_path_to_layer

        assert module_path_to_layer("agentic_core/L0_routing/engines/path_router.py") == "L0"

    def test_layer_mapping_l2(self) -> None:
        from agentic_core.adg.schema import module_path_to_layer

        assert module_path_to_layer("agentic_core/L2_execution/UniversalWriteGateway.py") == "L2"

    def test_layer_mapping_l5(self) -> None:
        from agentic_core.adg.schema import module_path_to_layer

        assert module_path_to_layer("agentic_core/L5_safety/enforcement/some_guard.py") == "L5"

    def test_layer_mapping_apps(self) -> None:
        from agentic_core.adg.schema import module_path_to_layer

        assert module_path_to_layer("apps_rg/engines/SomeAgent.py") == "L_APP"

    def test_layer_mapping_unknown(self) -> None:
        from agentic_core.adg.schema import module_path_to_layer

        assert module_path_to_layer("random/unknown/path.py") == "L_UNKNOWN"

    def test_allowed_layer_edges_contains_downward(self) -> None:
        from agentic_core.adg.schema import ALLOWED_LAYER_EDGES

        assert ("L2", "L0") in ALLOWED_LAYER_EDGES
        assert ("L5", "L2") in ALLOWED_LAYER_EDGES
        assert ("L6", "L0") in ALLOWED_LAYER_EDGES

    def test_allowed_layer_edges_excludes_upward(self) -> None:
        from agentic_core.adg.schema import ALLOWED_LAYER_EDGES

        assert ("L0", "L2") not in ALLOWED_LAYER_EDGES
        assert ("L1", "L5") not in ALLOWED_LAYER_EDGES


# ---------------------------------------------------------------------------
# MCP client idempotency
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.unit
class TestADGMCPClient:
    def test_upsert_entity_idempotent(self) -> None:
        from agentic_core.adg.client.mcp_client import ADGMCPClient

        client = ADGMCPClient()
        name = "ADG::Module::test/module.py"
        client.upsert_entity(name, "module", ["path:test/module.py"])
        client.upsert_entity(name, "module", ["path:test/module.py"])
        matching = [e for e in client.get_store().get_entities() if e["name"] == name]
        assert len(matching) == 1

    def test_upsert_relation_idempotent(self) -> None:
        from agentic_core.adg.client.mcp_client import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        rels = client.get_store().get_relations()
        matching = [r for r in rels if r["from"] == "ADG::Module::a.py" and r["to"] == "ADG::Symbol::b"]
        assert len(matching) == 1

    def test_add_observation_idempotent(self) -> None:
        from agentic_core.adg.client.mcp_client import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::x.py", "module", ["path:x.py"])
        client.add_observation("ADG::Module::x.py", ["commit:abc123"])
        client.add_observation("ADG::Module::x.py", ["commit:abc123"])
        entities = client.get_store().get_entities()
        e = next(e for e in entities if e["name"] == "ADG::Module::x.py")
        assert len([o for o in e["observations"] if o == "commit:abc123"]) == 1

    def test_search_nodes_returns_matches(self) -> None:
        from agentic_core.adg.client.mcp_client import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::search_target.py", "module", ["path:search_target.py"])
        results = client.search_nodes("search_target")
        assert any("search_target" in r["name"] for r in results)

    def test_open_nodes_returns_relations(self) -> None:
        from agentic_core.adg.client.mcp_client import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::a.py", "module", [])
        client.upsert_entity("ADG::Symbol::b.func", "symbol", [])
        client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b.func")
        nodes = client.open_nodes(["ADG::Module::a.py"])
        assert len(nodes) == 1
        assert "imports" in [r["relationType"] for r in nodes[0]["relations"]]

    def test_bulk_upsert_deterministic_order(self) -> None:
        from agentic_core.adg.client.mcp_client import ADGMCPClient

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
        from agentic_core.adg.ci.invariant_scanner import InvariantScanner
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
        from agentic_core.adg.ci.invariant_scanner import InvariantScanner
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
        from agentic_core.adg.ci.invariant_scanner import InvariantScanner
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test")
        result.compute_digest()
        report = InvariantScanner().scan(result)
        assert report.exit_code() == 0
        assert report.passed

    def test_scan_report_exit_code_fail(self) -> None:
        from agentic_core.adg.ci.invariant_scanner import ScanReport, Violation

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
        from agentic_core.adg.applications.gateway_topology import check_gateway_topology
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-empty")
        result.compute_digest()
        assert check_gateway_topology(result).passed

    def test_gateway_module_itself_is_allowed(self) -> None:
        from agentic_core.adg.applications.gateway_topology import check_gateway_topology
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
        from agentic_core.adg.applications.gateway_topology import check_gateway_topology
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
        from agentic_core.adg.applications.uwg_write_authority import check_uwg_write_authority
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-empty")
        result.compute_digest()
        assert check_uwg_write_authority(result).passed

    def test_uwg_module_itself_is_allowed(self) -> None:
        from agentic_core.adg.applications.uwg_write_authority import check_uwg_write_authority
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
        from agentic_core.adg.applications.rag_sovereignty import check_rag_sovereignty
        from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="test-rag-empty")
        result.compute_digest()
        assert check_rag_sovereignty(result).passed

    def test_rag_module_scan_passes(self) -> None:
        from agentic_core.adg.applications.rag_sovereignty import check_rag_sovereignty
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
        from agentic_core.adg.applications.rag_sovereignty import check_rag_sovereignty
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
        from agentic_core.adg.applications.blast_radius import compute_blast_radius
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
        from agentic_core.adg.applications.blast_radius import compute_blast_radius
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
        from agentic_core.adg.applications.blast_radius import compute_blast_radius
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
        from agentic_core.adg.applications.blast_radius import compute_blast_radius
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
        from agentic_core.adg.client.mcp_client import ADGMCPClient
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
        from agentic_core.adg.client.mcp_client import ADGMCPClient
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
        from agentic_core.adg.client.mcp_client import ADGMCPClient
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
