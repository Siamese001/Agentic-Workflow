from types import SimpleNamespace

from src.lic_agentic.agents.k1_router_agent import RouterAgent
from src.lic_agentic.safety.bias_auditor import BiasAssessment


def test_router_prioritizes_meeting_intent():
    router = RouterAgent()
    inputs = SimpleNamespace(prompt="Can we schedule a meeting next week?")
    decision = router.route(inputs, BiasAssessment(0.0, "clean"))
    assert decision.priority == "high"
    assert decision.channel == "email"
