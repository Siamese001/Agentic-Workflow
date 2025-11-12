from src.lic_agentic.mcp import MCPClient, ToolSpec
from src.lic_agentic.rag import MCPSelector
from src.lic_agentic.telemetry import PolicyController


def test_selector_respects_allowlist_and_quarantine():
    client = MCPClient(
        tools=[
            ToolSpec(
                id="trusted",
                name="Trusted",
                capabilities=("web_search",),
                cost=0.3,
                trust_tier="high",
                latency_ms=250,
            ),
            ToolSpec(
                id="beta",
                name="Beta",
                capabilities=("web_search",),
                cost=0.2,
                trust_tier="low",
                latency_ms=400,
            ),
        ]
    )
    policy = PolicyController()
    selector = MCPSelector(client, policy, allowlist=["trusted", "beta"])
    selections = selector.discover("web_search")
    assert selections[0].spec.id == "trusted"
    assert any(sel.quarantined for sel in selections if sel.spec.id == "beta")
    selector.mark_promoted("trusted")
    assert not selector.policy.quarantine_status("trusted")
