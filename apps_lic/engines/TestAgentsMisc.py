def test_router_prioritizes_meeting_intent():
    router = RouterAgent()
    inputs = SimpleNamespace(prompt="Can we schedule a meeting next week?")
    decision = router.route(inputs, BiasAssessment(0.0, "clean"))
    assert decision.priority == "high"
    assert decision.channel == "email"


def test_cta_agent_appends_default_line():
    draft = CTAAgent().adjust("Body", route_decision=None)
    assert "CTA:" in draft


def test_signature_agent_adds_signature_block():
    draft = SignatureAgent().attach("Body", route_decision=None)
    assert draft.endswith("LIC Outreach Bot")
