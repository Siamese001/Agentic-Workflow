def test_dedupe_and_budget():
    plan = RetrievalPlan([], {"ttl_s": 3600, "company_id": "ACME"})
    plan.add({"tool": "web_search", "query": "ACME revenue"})
    plan.add({"tool": "web_search", "query": "ACME revenue"})
    plan.add({"tool": "news", "query": "ACME earnings"})
    plan.dedupe()
    plan.budget(max_calls=2)
    assert len(plan.jobs) == 2


def test_execute_uses_cache_when_fresh():
    store = ContentStore()
    registry = ToolRegistry.default_with_builtins()
    plan = RetrievalPlan(["ACME revenue"], {"ttl_s": 3600, "company_id": "ACME"})
    plan.add({"tool": "web_search", "query": "ACME revenue"})
    plan.dedupe()
    first_results = plan.execute(registry, store)
    second_results = plan.execute(registry, store)
    assert first_results[0][0] == "live"
    assert second_results[0][0] == "cache"
