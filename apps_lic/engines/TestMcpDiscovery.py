"""MCPClient discovery and invocation tests."""

import pytest


def test_discover_filters_by_capability_and_trust():
    client = MCPClient(
        tools=[
            ToolSpec(
                id="alpha",
                name="Alpha",
                capabilities=("profile_lookup",),
                cost=0.2,
                trust_tier="high",
                latency_ms=200,
            ),
            ToolSpec(
                id="beta",
                name="Beta",
                capabilities=("profile_lookup", "enrichment"),
                cost=0.4,
                trust_tier="low",
                latency_ms=300,
            ),
        ]
    )
    results = client.discover("profile_lookup", {"min_trust": "medium"})
    assert len(results) == 1
    assert results[0].id == "alpha"
    payload = client.invoke("alpha", {"query": "ACME"})
    assert payload["ok"] and payload["usage_count"] == 1


def test_discover_honors_allowlist_and_cost_filters():
    client = MCPClient()
    allow_only = client.discover("web_search", {"allowlist": ["web_search_v1"]})
    assert allow_only and all(spec.id == "web_search_v1" for spec in allow_only)
    denied = client.discover("web_search", {"denylist": ["web_search_v1"]})
    assert all(spec.id != "web_search_v1" for spec in denied)
    cheap = client.discover("web_search", {"max_cost": 0.3})
    assert all(spec.cost <= 0.3 for spec in cheap)


def test_usage_count_tracks_invocations():
    client = MCPClient()
    client.invoke("web_search_v1", {"query": "one"})
    client.invoke("web_search_v1", {"query": "two"})
    assert client.usage_count("web_search_v1") == 2


def test_discover_returns_empty_for_unknown_capability():
    client = MCPClient()
    assert client.discover("nonexistent", {}) == []


def test_invoke_unknown_tool_raises_key_error():
    client = MCPClient()
    with pytest.raises(KeyError):
        client.invoke("missing")