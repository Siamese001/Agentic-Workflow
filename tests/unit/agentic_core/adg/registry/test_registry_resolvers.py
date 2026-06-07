"""Unit tests for the registry-bucket resolvers (W3).

Coverage:

* ``resolve_mcp_config`` returns one edge per ``mcpServers`` entry, with
  STABLE_REGISTRY for enabled servers and DISABLED_REGISTRY for disabled.
* ``resolve_agent_specs`` returns one edge per top-level spec key per
  app, with deterministic per-entry digests.
* ``compute_registry_digest_set`` deduplicates per-entry digests.
* Empty / missing source files produce zero edges (not placeholder rows).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.registry.registry_resolvers import (  # noqa: E402
    AGENT_REGISTRY_ROOT,
    MCP_REGISTRY_ROOT,
    RESOLUTION_DISABLED,
    RESOLUTION_STABLE,
    AUTHORITY_AUTHORITATIVE_REGISTRY,
    AUTHORITY_RISK_SIGNAL_ONLY,
    RegistryEdge,
    compute_registry_digest_set,
    resolve_agent_specs,
    resolve_all_registries,
    resolve_mcp_config,
)


# ---------------------------------------------------------------------------
# RegistryEdge dataclass
# ---------------------------------------------------------------------------


class TestRegistryEdge:
    def test_evidence_refs_json_is_deterministic(self) -> None:
        e1 = RegistryEdge(
            src_name="r",
            dst_name="d",
            relation_type="X",
            edge_kind="Y",
            source_file="path/to/f",
            evidence_refs={"b": 2, "a": 1},
        )
        e2 = RegistryEdge(
            src_name="r",
            dst_name="d",
            relation_type="X",
            edge_kind="Y",
            source_file="path/to/f",
            evidence_refs={"a": 1, "b": 2},
        )
        # Sorted keys → same JSON regardless of insertion order.
        assert e1.evidence_refs_json() == e2.evidence_refs_json()

    def test_default_bucket_and_status(self) -> None:
        e = RegistryEdge(
            src_name="r",
            dst_name="d",
            relation_type="X",
            edge_kind="Y",
            source_file="f",
        )
        assert e.bucket == "registry"
        assert e.resolution_status == RESOLUTION_STABLE
        assert e.authority_status == AUTHORITY_AUTHORITATIVE_REGISTRY


# ---------------------------------------------------------------------------
# resolve_mcp_config
# ---------------------------------------------------------------------------


class TestResolveMcpConfig:
    @staticmethod
    def _write_config(path: Path, servers: dict[str, dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump({"mcpServers": servers}, f)

    def test_emits_one_edge_per_enabled_server(self, tmp_path: Path) -> None:
        cfg = tmp_path / "mcp_config.json"
        self._write_config(
            cfg,
            {
                "GitKraken": {"command": "gk", "args": [], "disabled": False},
                "adg_sqlite": {"command": "python", "args": ["-m", "tools.adg.mcp.server"], "disabled": False},
            },
        )
        edges = resolve_mcp_config(cfg)
        assert len(edges) == 2
        for e in edges:
            assert e.src_name == MCP_REGISTRY_ROOT
            assert e.relation_type == "MCP_SERVER_DECLARED"
            assert e.bucket == "registry"
            assert e.resolution_status == RESOLUTION_STABLE
            assert e.authority_status == AUTHORITY_AUTHORITATIVE_REGISTRY
            assert "registry_digest" in e.evidence_refs

    def test_disabled_server_classified_as_risk_only(self, tmp_path: Path) -> None:
        cfg = tmp_path / "mcp_config.json"
        self._write_config(
            cfg,
            {
                "broken_server": {"command": "x", "args": [], "disabled": True},
            },
        )
        edges = resolve_mcp_config(cfg)
        assert len(edges) == 1
        e = edges[0]
        assert e.resolution_status == RESOLUTION_DISABLED
        assert e.authority_status == AUTHORITY_RISK_SIGNAL_ONLY
        assert e.evidence_refs["disabled"] is True

    def test_missing_file_returns_empty_list(self, tmp_path: Path) -> None:
        edges = resolve_mcp_config(tmp_path / "does_not_exist.json")
        assert edges == []

    def test_invalid_json_returns_empty_list(self, tmp_path: Path) -> None:
        cfg = tmp_path / "bad.json"
        cfg.write_text("{ not valid json")
        edges = resolve_mcp_config(cfg)
        assert edges == []

    def test_no_mcp_servers_key_returns_empty_list(self, tmp_path: Path) -> None:
        cfg = tmp_path / "empty.json"
        cfg.write_text("{}")
        edges = resolve_mcp_config(cfg)
        assert edges == []

    def test_distinct_servers_have_distinct_digests(self, tmp_path: Path) -> None:
        cfg = tmp_path / "mcp_config.json"
        self._write_config(
            cfg,
            {
                "A": {"command": "a", "disabled": False},
                "B": {"command": "b", "disabled": False},
            },
        )
        edges = resolve_mcp_config(cfg)
        digests = {e.evidence_refs["registry_digest"] for e in edges}
        assert len(digests) == 2  # different configs produce different digests


# ---------------------------------------------------------------------------
# resolve_agent_specs
# ---------------------------------------------------------------------------


class TestResolveAgentSpecs:
    def test_emits_one_edge_per_spec_key(self, tmp_path: Path) -> None:
        # Simulate apps_test/config/agent_specs.json layout.
        app_dir = tmp_path / "apps_test" / "config"
        app_dir.mkdir(parents=True)
        spec = {
            "profile_analysis_agent": {"keyword": "x", "confidence": 0.9},
            "research_agent": {"top_k": 10},
        }
        spec_path = app_dir / "agent_specs.json"
        spec_path.write_text(json.dumps(spec))
        edges = resolve_agent_specs([spec_path])
        assert len(edges) == 2
        for e in edges:
            assert e.src_name == AGENT_REGISTRY_ROOT
            assert e.relation_type == "AGENT_SPEC_DECLARED"
            assert e.bucket == "registry"
            assert e.resolution_status == RESOLUTION_STABLE

    def test_dst_name_includes_app_prefix(self, tmp_path: Path) -> None:
        # Two apps both declaring "research_agent" must not collide.
        app_a = tmp_path / "apps_a" / "config"
        app_b = tmp_path / "apps_b" / "config"
        app_a.mkdir(parents=True)
        app_b.mkdir(parents=True)
        (app_a / "agent_specs.json").write_text(json.dumps({"research_agent": {"v": "a"}}))
        (app_b / "agent_specs.json").write_text(json.dumps({"research_agent": {"v": "b"}}))
        edges = resolve_agent_specs([
            app_a / "agent_specs.json",
            app_b / "agent_specs.json",
        ])
        # The dst_name doesn't include the relative-path-derived app prefix in
        # this synthetic test (paths aren't under REPO_ROOT) — but each edge
        # MUST be distinct.
        names = {e.dst_name for e in edges}
        assert len(names) == 2

    def test_empty_spec_file_returns_empty_list(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "empty.json"
        spec_path.write_text("{}")
        edges = resolve_agent_specs([spec_path])
        assert edges == []

    def test_missing_files_filtered(self, tmp_path: Path) -> None:
        edges = resolve_agent_specs([tmp_path / "does_not_exist.json"])
        assert edges == []


# ---------------------------------------------------------------------------
# compute_registry_digest_set
# ---------------------------------------------------------------------------


class TestComputeRegistryDigestSet:
    def test_returns_sorted_unique_digests(self) -> None:
        edges = [
            RegistryEdge(src_name="r", dst_name="a", relation_type="X", edge_kind="Y", source_file="", evidence_refs={"registry_digest": "d2"}),
            RegistryEdge(src_name="r", dst_name="b", relation_type="X", edge_kind="Y", source_file="", evidence_refs={"registry_digest": "d1"}),
            RegistryEdge(src_name="r", dst_name="c", relation_type="X", edge_kind="Y", source_file="", evidence_refs={"registry_digest": "d1"}),  # dup
        ]
        result = compute_registry_digest_set(edges)
        assert result == ["d1", "d2"]

    def test_skips_edges_without_digest(self) -> None:
        edges = [
            RegistryEdge(src_name="r", dst_name="a", relation_type="X", edge_kind="Y", source_file="", evidence_refs={}),
            RegistryEdge(src_name="r", dst_name="b", relation_type="X", edge_kind="Y", source_file="", evidence_refs={"registry_digest": "d1"}),
        ]
        result = compute_registry_digest_set(edges)
        assert result == ["d1"]


# ---------------------------------------------------------------------------
# resolve_all_registries — integration with the live repo
# ---------------------------------------------------------------------------


class TestResolveAllRegistries:
    def test_returns_nonempty_for_live_repo(self) -> None:
        # The live `.cursor/mcp.json` should always resolve to ≥3 servers.
        edges = resolve_all_registries()
        # Must include the MCP root edges.
        mcp_edges = [e for e in edges if e.src_name == MCP_REGISTRY_ROOT]
        assert len(mcp_edges) >= 3, (
            "expected at least 3 MCP server entries in live config; "
            f"got {len(mcp_edges)}"
        )

    def test_every_edge_has_evidence_refs(self) -> None:
        edges = resolve_all_registries()
        for e in edges:
            assert "registry_path" in e.evidence_refs
            assert "registry_digest" in e.evidence_refs
            assert "declaration_key" in e.evidence_refs


# ---------------------------------------------------------------------------
# resolve_route_contracts — W5 (plan three-bucket-otel-view-5db409)
# ---------------------------------------------------------------------------


class TestResolveRouteContracts:
    """Resolver for agentic_core/L0_routing/config/v15_policy_pack.json."""

    @staticmethod
    def _write_pack(path: Path, rules: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump({"version": "1.0.0", "rules": rules}, f)

    def test_missing_pack_returns_empty(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_route_contracts,
        )

        edges = resolve_route_contracts(policy_pack_path=tmp_path / "missing.json")
        assert edges == []

    def test_one_edge_per_rule(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            ROUTE_CONTRACT_REGISTRY_ROOT,
            resolve_route_contracts,
        )

        pack = tmp_path / "policy_pack.json"
        self._write_pack(
            pack,
            [
                {
                    "rule_id": "R_001",
                    "applies_to": "PIPE",
                    "severity": "WARN",
                    "enabled": True,
                    "description": "test 1",
                },
                {
                    "rule_id": "R_002",
                    "applies_to": "POLICY",
                    "severity": "ERROR",
                    "enabled": True,
                    "description": "test 2",
                },
            ],
        )
        edges = resolve_route_contracts(policy_pack_path=pack)
        assert len(edges) == 2
        for e in edges:
            assert e.src_name == ROUTE_CONTRACT_REGISTRY_ROOT
            assert e.relation_type == "ROUTE_CONTRACT_DECLARED"
            assert e.bucket == "registry"
            assert e.authority_status == "AUTHORITATIVE_REGISTRY"
            assert "policy_pack_version" in e.evidence_refs

    def test_disabled_rule_marked_risk(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_route_contracts,
        )

        pack = tmp_path / "pack.json"
        self._write_pack(
            pack,
            [
                {
                    "rule_id": "DISABLED_X",
                    "applies_to": "POLICY",
                    "severity": "WARN",
                    "enabled": False,
                    "description": "test disabled",
                },
            ],
        )
        edges = resolve_route_contracts(policy_pack_path=pack)
        assert len(edges) == 1
        assert edges[0].resolution_status == "DISABLED_REGISTRY"
        assert edges[0].authority_status == "RISK_SIGNAL_ONLY"

    def test_skips_malformed_rule_entries(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_route_contracts,
        )

        pack = tmp_path / "pack.json"
        with pack.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": "1.0.0",
                    "rules": [
                        {"rule_id": "good"},
                        "not a dict",
                        {"rule_id": ""},  # empty rule_id
                        {"no_rule_id_field": "x"},
                        {"rule_id": "good_2"},
                    ],
                },
                f,
            )
        edges = resolve_route_contracts(policy_pack_path=pack)
        rule_ids = {e.symbol for e in edges}
        assert rule_ids == {"good", "good_2"}

    def test_unparseable_pack_returns_empty(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_route_contracts,
        )

        pack = tmp_path / "bad.json"
        pack.write_text("{not json")
        assert resolve_route_contracts(policy_pack_path=pack) == []

    def test_live_v15_policy_pack_resolves(self) -> None:
        # The shipped agentic_core/L0_routing/config/v15_policy_pack.json
        # is the canonical source — must resolve cleanly.
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_route_contracts,
        )

        edges = resolve_route_contracts()
        assert len(edges) >= 1, "expected ≥1 rule in live policy pack"
        for e in edges:
            assert e.bucket == "registry"
            assert e.relation_type == "ROUTE_CONTRACT_DECLARED"

    def test_each_edge_has_unique_digest(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_route_contracts,
        )

        pack = tmp_path / "pack.json"
        self._write_pack(
            pack,
            [
                {"rule_id": "A", "severity": "W", "applies_to": "X"},
                {"rule_id": "B", "severity": "W", "applies_to": "X"},
            ],
        )
        edges = resolve_route_contracts(policy_pack_path=pack)
        digests = {e.evidence_refs["registry_digest"] for e in edges}
        # Two different rule_ids → two distinct digests.
        assert len(digests) == 2


# ---------------------------------------------------------------------------
# resolve_prompt_slots — W11.1 / P5.2 follow-up resolver
# ---------------------------------------------------------------------------


class TestResolvePromptSlots:
    """Tests for the prompt-slot registry resolver added in W11.1.

    The resolver reads
    ``agentic_core/prompt_governance/registry/prompt_registry_config.json``
    and emits one RegistryEdge per (slot_name, version) tuple."""

    def _write_registry(self, path: Path, prompts: dict) -> None:
        path.write_text(
            json.dumps({
                "sovereign_version": "1.0",
                "generated_date": "2026-04-30",
                "prompts": prompts,
            }),
            encoding="utf-8",
        )

    def test_emits_one_edge_per_slot_version_pair(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_prompt_slots,
        )
        reg = tmp_path / "prompts.json"
        self._write_registry(reg, {
            "alpha.jinja": [
                {"version": "v1", "active": True, "purpose": "p1",
                 "territory": "t", "author": "A", "registered_date": "2026-01-01"},
                {"version": "v2", "active": True, "purpose": "p2",
                 "territory": "t", "author": "A", "registered_date": "2026-02-01"},
            ],
            "beta.jinja": [
                {"version": "v1", "active": True, "purpose": "p", "territory": "t",
                 "author": "B", "registered_date": "2026-01-15"},
            ],
        })
        edges = resolve_prompt_slots(registry_path=reg)
        assert len(edges) == 3
        for e in edges:
            assert e.bucket == "registry"
            assert e.relation_type == "PROMPT_SLOT_DECLARED"
            assert e.edge_kind == "REGISTRY_DECLARATION"
            assert e.src_name == "Registry::PromptSlot::root"

    def test_inactive_slot_classified_as_risk_only(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            AUTHORITY_RISK_SIGNAL_ONLY,
            RESOLUTION_DISABLED,
            resolve_prompt_slots,
        )
        reg = tmp_path / "prompts.json"
        self._write_registry(reg, {
            "x.jinja": [
                {"version": "v1", "active": False, "purpose": "deprecated",
                 "territory": "t", "author": "A", "registered_date": "2026-01-01"},
            ],
        })
        edges = resolve_prompt_slots(registry_path=reg)
        assert len(edges) == 1
        assert edges[0].resolution_status == RESOLUTION_DISABLED
        assert edges[0].authority_status == AUTHORITY_RISK_SIGNAL_ONLY

    def test_missing_file_returns_empty_list(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_prompt_slots,
        )
        assert resolve_prompt_slots(registry_path=tmp_path / "nope.json") == []

    def test_invalid_json_returns_empty_list(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_prompt_slots,
        )
        bad = tmp_path / "bad.json"
        bad.write_text("not json {{", encoding="utf-8")
        assert resolve_prompt_slots(registry_path=bad) == []

    def test_no_prompts_key_returns_empty_list(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_prompt_slots,
        )
        f = tmp_path / "p.json"
        f.write_text(json.dumps({"sovereign_version": "1.0"}), encoding="utf-8")
        assert resolve_prompt_slots(registry_path=f) == []

    def test_dst_name_includes_slot_and_version(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_prompt_slots,
        )
        reg = tmp_path / "prompts.json"
        self._write_registry(reg, {
            "my_slot.jinja": [{"version": "v3", "active": True}],
        })
        edges = resolve_prompt_slots(registry_path=reg)
        assert len(edges) == 1
        assert edges[0].dst_name == "Registry::PromptSlot::my_slot.jinja::v3"
        assert edges[0].symbol == "my_slot.jinja@v3"

    def test_distinct_versions_have_distinct_digests(self, tmp_path: Path) -> None:
        from agentic_core.adg.registry.registry_resolvers import (
            resolve_prompt_slots,
        )
        reg = tmp_path / "prompts.json"
        self._write_registry(reg, {
            "a.jinja": [
                {"version": "v1", "active": True, "purpose": "old"},
                {"version": "v2", "active": True, "purpose": "new"},
            ],
        })
        edges = resolve_prompt_slots(registry_path=reg)
        digests = {e.evidence_refs["registry_digest"] for e in edges}
        assert len(digests) == 2

    def test_live_registry_loads(self) -> None:
        """Smoke test against the actual canonical registry file."""
        from agentic_core.adg.registry.registry_resolvers import (
            DEFAULT_PROMPT_REGISTRY,
            resolve_prompt_slots,
        )
        if not DEFAULT_PROMPT_REGISTRY.exists():
            pytest.skip("canonical prompt registry not present in this checkout")
        edges = resolve_prompt_slots()
        # The current registry has at least 2 slots (file_placement, gravity_repair).
        assert len(edges) >= 2
        for e in edges:
            assert e.bucket == "registry"
            assert e.relation_type == "PROMPT_SLOT_DECLARED"
