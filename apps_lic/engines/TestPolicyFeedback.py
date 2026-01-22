def test_policy_feedback_updates_toggles_and_budget():
    stack = OutreachStack(ReasoningToggles())

    def fake_compose(inputs, route, *, max_calls=None):
        draft = "Subject: Hi\n\nHello there\n[artifact_id:aid] evidence"
        return DraftPackage(draft=draft, artifacts={"aid": "evidence"}, total_latency_ms=5000)

    with patch.object(stack.architect, "compose", side_effect=fake_compose):
        result = stack.run(SimpleNamespace(prompt="Testing", company_id="ACME", contact_id="C1"))

    assert result["verdict"].passed
    assert stack.policy.budget_multiplier <= 1.0
    assert 1 <= stack.toggles.tot_branches <= 4
