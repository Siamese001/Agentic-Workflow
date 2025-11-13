"""System tests covering CTA and signature agents."""
from src.lic_agentic.agents.k5_cta_agent import CTAAgent
from src.lic_agentic.agents.k6_signature_agent import SignatureAgent


def test_cta_agent_appends_default_line(lic_context):
    draft = CTAAgent(lic_context).adjust("Body", route_decision=None)
    assert "CTA:" in draft
    assert draft.endswith("chat next week?")


def test_signature_agent_adds_signature_block(lic_context):
    draft = SignatureAgent(lic_context).attach("Body", route_decision=None)
    assert draft.endswith("LIC Outreach Bot")
    assert "Best regards" in draft
