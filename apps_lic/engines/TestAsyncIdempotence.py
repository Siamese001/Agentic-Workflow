"""Integration tests for the async conductor."""




def test_conductor_preserves_order_under_concurrency():
    conductor = Conductor(concurrency=2, seed=11)
    factories = [
        conductor.wrap_tool_call(i, lambda value=value, index=i: (value * 2, 25 + index * 5))
        for i, value in enumerate((2, 3, 5))
    ]
    results = conductor.run(factories)
    assert results == [(0, 4), (1, 6), (2, 10)]


def test_conductor_artifact_ids_are_deterministic():
    conductor = Conductor(seed=5)
    first = conductor.make_artifact_id("outreach", "ACME")
    second = conductor.make_artifact_id("outreach", "ACME")
    conductor.reset()
    replay = conductor.make_artifact_id("outreach", "ACME")
    assert first != second
    assert first == replay