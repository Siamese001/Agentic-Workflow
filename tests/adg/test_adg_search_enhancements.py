"""Tests for ADG search enhancements — Accelerator #3.

Coverage matrix per §1.1:
- search_nodes with no filters: basic substring match, case-insensitive, sorted
- search_nodes with layer filter: exact match, case-insensitive, excludes wrong layer
- search_nodes with entity_type filter: exact match, case-insensitive
- search_nodes with both filters: AND semantics (must match both)
- search_nodes with empty substring + filters: return all nodes matching filters
- Edge cases: no matches, None filters, empty node field values
- Determinism: identical input → identical sorted output
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


def _make_client_with_nodes(nodes: list[dict[str, str]]) -> object:
    """Build ADGRedisClient stub whose scan returns the given nodes.

    Uses index-based unique keys to avoid key collisions when multiple nodes
    share the same adg_name (e.g. same filename in different layers).
    """
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()

    keys = [f"adg:node:test_node_{i}" for i in range(len(nodes))]
    node_map = {keys[i]: nodes[i] for i in range(len(nodes))}

    r.scan.return_value = (0, keys)

    def hgetall(key: str) -> dict[str, str]:
        return node_map.get(key, {})

    r.hgetall.side_effect = hgetall
    client._r = r
    return client


# ===========================================================================
# search_nodes — no filters (baseline from previous implementation)
# ===========================================================================


class TestSearchNodesBaseline:
    def test_substring_match_case_insensitive(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::apps_lic/DashboardAgent.py", "layer": "L4"},
            {"adg_name": "ADG::Module::apps_lic/RoutingAgent.py", "layer": "L4"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "dashboardagent")
        assert len(result) == 1
        assert "DashboardAgent" in result[0]["adg_name"]

    def test_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::apps_lic/RoutingAgent.py", "layer": "L4"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "nonexistent_xyz_abc")
        assert result == []

    def test_empty_substring_returns_all_nodes(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::a.py", "layer": "L0"},
            {"adg_name": "ADG::Module::b.py", "layer": "L2"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "")
        assert len(result) == 2

    def test_result_is_sorted_by_adg_name(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "z_module.py"},
            {"adg_name": "a_module.py"},
            {"adg_name": "m_module.py"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "")
        names = [n["adg_name"] for n in result]
        assert names == sorted(names)

    def test_deterministic_output(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "ADG::Module::foo.py", "layer": "L2"},
            {"adg_name": "ADG::Module::bar.py", "layer": "L2"},
        ]
        client = _make_client_with_nodes(nodes)
        r1 = ADGRedisClient.search_nodes(client, "")
        r2 = ADGRedisClient.search_nodes(client, "")
        assert r1 == r2


# ===========================================================================
# search_nodes — layer filter
# ===========================================================================


class TestSearchNodesLayerFilter:
    def test_layer_filter_returns_only_matching_layer(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L0"},
            {"adg_name": "mod_b.py", "layer": "L2"},
            {"adg_name": "mod_c.py", "layer": "L0"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="L0")
        assert len(result) == 2
        assert all(n["layer"] == "L0" for n in result)

    def test_layer_filter_case_insensitive(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L2"},
            {"adg_name": "mod_b.py", "layer": "L4"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="l2")
        assert len(result) == 1
        assert result[0]["layer"] == "L2"

    def test_layer_filter_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L0"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="L9")
        assert result == []

    def test_none_layer_does_not_filter(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "layer": "L0"},
            {"adg_name": "mod_b.py", "layer": "L5"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer=None)
        assert len(result) == 2

    def test_layer_filter_combined_with_substring(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "Router.py", "layer": "L0"},
            {"adg_name": "Router.py", "layer": "L2"},
            {"adg_name": "Dispatcher.py", "layer": "L0"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "router", layer="L0")
        assert len(result) == 1
        assert result[0]["layer"] == "L0"
        assert "Router" in result[0]["adg_name"]


# ===========================================================================
# search_nodes — entity_type filter
# ===========================================================================


class TestSearchNodesEntityTypeFilter:
    def test_entity_type_filter_returns_only_matching_type(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod_a.py", "entity_type": "module"},
            {"adg_name": "ClassA", "entity_type": "class"},
            {"adg_name": "func_a", "entity_type": "function"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type="class")
        assert len(result) == 1
        assert result[0]["entity_type"] == "class"

    def test_entity_type_filter_case_insensitive(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "MyClass", "entity_type": "Class"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type="class")
        assert len(result) == 1

    def test_entity_type_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod.py", "entity_type": "module"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type="dataclass")
        assert result == []

    def test_none_entity_type_does_not_filter(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "mod.py", "entity_type": "module"},
            {"adg_name": "MyClass", "entity_type": "class"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", entity_type=None)
        assert len(result) == 2


# ===========================================================================
# search_nodes — both filters (AND semantics)
# ===========================================================================


class TestSearchNodesBothFilters:
    def test_both_filters_must_both_match(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "AgentClass_L3", "layer": "L3", "entity_type": "class"},
            {"adg_name": "AgentClass_L4", "layer": "L4", "entity_type": "class"},
            {"adg_name": "AgentFunc_L3", "layer": "L3", "entity_type": "function"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "agent", layer="L3", entity_type="class")
        assert len(result) == 1
        assert result[0]["layer"] == "L3"
        assert result[0]["entity_type"] == "class"

    def test_both_filters_no_match_returns_empty(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "AgentClass_L3", "layer": "L3", "entity_type": "class"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "agent", layer="L5", entity_type="class")
        assert result == []

    def test_empty_substring_with_both_filters(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "A", "layer": "L2", "entity_type": "module"},
            {"adg_name": "B", "layer": "L2", "entity_type": "class"},
            {"adg_name": "C", "layer": "L4", "entity_type": "module"},
        ]
        client = _make_client_with_nodes(nodes)
        result = ADGRedisClient.search_nodes(client, "", layer="L2", entity_type="module")
        assert len(result) == 1
        assert result[0]["adg_name"] == "A"

    def test_both_filters_deterministic(self):
        from tools.adg.adg_redis_query import ADGRedisClient

        nodes = [
            {"adg_name": "X", "layer": "L0", "entity_type": "module"},
            {"adg_name": "Y", "layer": "L0", "entity_type": "class"},
        ]
        client = _make_client_with_nodes(nodes)
        r1 = ADGRedisClient.search_nodes(client, "", layer="L0")
        r2 = ADGRedisClient.search_nodes(client, "", layer="L0")
        assert r1 == r2
