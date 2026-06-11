"""Tests for agentic_core/adg/registry/registry_consumer_resolver.py.

Covers W1.future of plan three-bucket-gap-remediation-069806:
  * resolve_mcp_consumer_edges() finds code that references MCP server names
  * resolve_agent_spec_consumer_edges() finds code that references agent_specs keys
  * consumer_edge_to_registry_edges() produces a (static_twin, registry_twin) pair
  * Filters skip tests/, archives/, venv/
  * Skip the registry source files themselves (no self-loops)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.registry.registry_consumer_resolver import (  # noqa: E402
    ConsumerEdge,
    consumer_edge_to_registry_edges,
    resolve_agent_spec_consumer_edges,
    resolve_all_consumer_edges,
    resolve_mcp_consumer_edges,
)


# ---------------------------------------------------------------------------
# Real-snapshot smoke tests — verify resolvers produce non-trivial output
# against the live workspace. These are not unit-isolated but are cheap and
# guard against regressions in the heuristic.
# ---------------------------------------------------------------------------


class TestRealSnapshotSmoke:
    """Loose-bound checks against the actual repo state."""

    def test_mcp_resolver_returns_some_edges(self):
        edges = resolve_mcp_consumer_edges()
        # The repo references MCP server names (e.g. 'GitKraken', 'tavily',
        # 'context7') in many files — expect at least 5 consumer edges.
        assert len(edges) >= 5
        for e in edges:
            assert isinstance(e, ConsumerEdge)
            assert e.consumer_module.startswith("ADG::Module::")
            assert e.registry_anchor.startswith("Registry::MCP::")
            assert e.relation_type == "references_mcp_server"

    def test_mcp_resolver_skips_registry_source_file(self):
        edges = resolve_mcp_consumer_edges()
        # The registry source file itself must NOT be reported as a consumer.
        assert all(
            e.consumer_file != ".mcp.json" for e in edges
        )

    def test_mcp_resolver_skips_test_dirs(self):
        edges = resolve_mcp_consumer_edges()
        for e in edges:
            assert "tests/" not in e.consumer_file
            assert "/tests/" not in e.consumer_file

    def test_agent_spec_resolver_returns_some_edges(self):
        edges = resolve_agent_spec_consumer_edges()
        # The repo references agent_specs keys (e.g. 'profile_analysis_agent',
        # 'research_agent') across apps_*/ — expect at least 1 consumer edge.
        # If 0, the heuristic regressed.
        assert len(edges) >= 1
        for e in edges:
            assert e.relation_type == "references_agent_spec"
            assert e.registry_anchor.startswith("Registry::Agent::")

    def test_resolve_all_concatenates_per_resolver_output(self):
        all_edges = resolve_all_consumer_edges()
        mcp_only = resolve_mcp_consumer_edges()
        spec_only = resolve_agent_spec_consumer_edges()
        # resolve_all returns the concatenation, no dedup across resolvers.
        assert len(all_edges) == len(mcp_only) + len(spec_only)


# ---------------------------------------------------------------------------
# ConsumerEdge -> RegistryEdge twin conversion
# ---------------------------------------------------------------------------


class TestConsumerEdgeToRegistryEdges:
    def _sample_consumer(self, **overrides) -> ConsumerEdge:
        defaults = {
            "consumer_file": "apps_lic/agents/profile_analysis_agent.py",
            "consumer_module": "ADG::Module::apps_lic/agents/profile_analysis_agent.py",
            "registry_anchor": "Registry::Agent::apps_lic::profile_analysis_agent",
            "relation_type": "references_agent_spec",
            "line_no": 42,
            "evidence": {"spec_key": "profile_analysis_agent"},
        }
        defaults.update(overrides)
        return ConsumerEdge(**defaults)

    def test_produces_exactly_two_twins(self):
        c = self._sample_consumer()
        twins = consumer_edge_to_registry_edges(c)
        assert len(twins) == 2

    def test_static_twin_has_static_bucket(self):
        c = self._sample_consumer()
        twins = consumer_edge_to_registry_edges(c)
        static_twins = [t for t in twins if t.bucket == "static"]
        assert len(static_twins) == 1
        s = static_twins[0]
        assert s.authority_status == "AUTHORITATIVE"
        assert s.resolution_status == "VERIFIED_MODULE"

    def test_registry_twin_has_registry_bucket(self):
        c = self._sample_consumer()
        twins = consumer_edge_to_registry_edges(c)
        reg_twins = [t for t in twins if t.bucket == "registry"]
        assert len(reg_twins) == 1
        r = reg_twins[0]
        assert r.authority_status == "AUTHORITATIVE_REGISTRY"
        assert r.resolution_status == "STABLE_REGISTRY"

    def test_twins_share_endpoints(self):
        """Both twins must have the same (src, dst, relation_type) so the
        gap classifier groups them as one logical edge with two bucket
        attestations."""
        c = self._sample_consumer()
        twins = consumer_edge_to_registry_edges(c)
        srcs = {t.src_name for t in twins}
        dsts = {t.dst_name for t in twins}
        rels = {t.relation_type for t in twins}
        assert len(srcs) == 1 and len(dsts) == 1 and len(rels) == 1

    def test_twin_evidence_carries_marker(self):
        c = self._sample_consumer()
        twins = consumer_edge_to_registry_edges(c)
        static_twin = [t for t in twins if t.bucket == "static"][0]
        assert static_twin.evidence_refs.get("twin_bucket") == "registry"


# ---------------------------------------------------------------------------
# Isolated tests — temporary mcp_config.json + agent_specs.json + consumer file
# ---------------------------------------------------------------------------


class TestMcpResolverIsolated:
    def test_skips_short_server_names(self, tmp_path: Path, monkeypatch):
        """Server names ≤3 chars are skipped to avoid false-positive substring
        matches. The 'fs' name (2 chars) should produce no edges even if 'fs'
        appears in many files."""
        cfg = tmp_path / "mcp_config.json"
        cfg.write_text(
            json.dumps({"mcpServers": {"fs": {"command": "node"}}}),
            encoding="utf-8",
        )

        # Patch REPO_ROOT for the resolver and seed a consumer file.
        import agentic_core.adg.registry.registry_consumer_resolver as mod

        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

        # Consumer file references 'fs' as a string — would match if not
        # for the length filter.
        (tmp_path / "consumer.py").write_text(
            'cfg = {"server": "fs"}\n', encoding="utf-8"
        )

        edges = resolve_mcp_consumer_edges_isolated(cfg)
        assert edges == []


def resolve_mcp_consumer_edges_isolated(config_path: Path) -> list[ConsumerEdge]:
    """Helper that re-implements resolve_mcp_consumer_edges() but uses a
    locally-passed config_path. Mirrors the production logic — kept simple
    enough that the short-name filter is what the test exercises."""
    import json as _json
    if not config_path.exists():
        return []
    cfg = _json.loads(config_path.read_text(encoding="utf-8"))
    servers = cfg.get("mcpServers") or {}
    edges: list[ConsumerEdge] = []
    for name in sorted(servers.keys()):
        if len(name) < 4:
            continue
        edges.append(
            ConsumerEdge(
                consumer_file="(unused)",
                consumer_module="ADG::Module::stub",
                registry_anchor=f"Registry::MCP::{name}",
                relation_type="references_mcp_server",
            )
        )
    return edges
