"""Release SLO checks for the full outreach pipeline."""




def test_release_path_meets_slos_and_is_deterministic():
    stack = OutreachStack(ReasoningToggles())
    inputs = StackInputs(prompt="Checking in", company_id="ACME", contact_id="C1")

    drafts = []
    for _ in range(3):
        outcome = stack.run(inputs)
        drafts.append(outcome["draft"])
        assert outcome["verdict"].passed

    metrics = stack.validator.metrics
    assert metrics.pass_rate() >= 0.85
    assert metrics.latency_p95() <= 3000
    assert metrics.token_drift() <= 0.10
    assert len(set(drafts[-2:])) == 1