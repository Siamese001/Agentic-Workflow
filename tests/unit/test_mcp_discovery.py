from src.lic_agentic.mcp import MCPClient, ToolSpec


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
