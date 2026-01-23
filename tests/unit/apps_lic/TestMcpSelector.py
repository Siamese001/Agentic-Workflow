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


def test_register_discovered_tools_wires_new_adapters():
    client = MCPClient()
    policy = PolicyController()
    selector = MCPSelector(client, policy)
    registry = ToolRegistry()
    selections = register_discovered_tools(registry, selector, "web_search")
    assert selections
    assert any(name.startswith("web_search") for name in registry.available())
    adapter = registry.resolve(selections[0].spec.id)
    result = adapter.run("test", {})
    assert "response" in result.content.lower()


def test_selector_quarantine_updates_policy_state():
    client = MCPClient()
    policy = PolicyController()
    policy.register_tool("web_search_v1", quarantined=False)
    selector = MCPSelector(client, policy)
    selector.quarantine("web_search_v1")
    selections = selector.discover("web_search")
    assert any(sel.quarantined for sel in selections if sel.spec.id == "web_search_v1")


def test_mark_promoted_clears_quarantine():
    client = MCPClient()
    policy = PolicyController()
    policy.register_tool("web_search_v1", quarantined=True)
    selector = MCPSelector(client, policy)
    selector.mark_promoted("web_search_v1")
    assert not policy.quarantine_status("web_search_v1")


def test_quarantined_tools_use_smaller_budget():
    client = MCPClient()
    policy = PolicyController()
    policy.register_tool("web_search_v1", quarantined=True)
    selector = MCPSelector(client, policy)
    selections = selector.discover("web_search")
    quarantined = next(sel for sel in selections if sel.spec.id == "web_search_v1")
    selector.mark_promoted("web_search_v1")
    promoted = next(
        sel for sel in selector.discover("web_search") if sel.spec.id == "web_search_v1"
    )
    assert quarantined.budget_multiplier < promoted.budget_multiplier


def test_selector_allowlist_filters_out_unapproved_tools():
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
    selector = MCPSelector(client, PolicyController(), allowlist=["trusted"])
    selections = selector.discover("web_search")
    assert all(sel.spec.id == "trusted" for sel in selections)
