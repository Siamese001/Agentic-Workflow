"""Regression test enforcing retrieval latency SLO."""


import math



def percentile(values: list[int], pct: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(ordered[int(k)])
    d0 = ordered[f] * (c - k)
    d1 = ordered[c] * (k - f)
    return float(d0 + d1)


def test_retrieval_p95_below_budget():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    sanitized = type(
        "Inputs",
        (),
        {"prompt": "Share recent milestones", "company_id": "ACME", "contact_id": "C1"},
    )()
    plan = architect._build_plan(["ACME latest milestones", "ACME recent news"], sanitized)
    plan.dedupe()
    plan.budget(max_calls=6)
    outcomes = plan.execute(architect.tool_registry, architect.content_store)
    latencies = [result.latency_ms for _source, _job, result in outcomes]
    assert percentile(latencies, 0.95) <= 3500