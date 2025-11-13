from src.lic_agentic.agents.k7_validator_agent import ValidatorAgent


def test_retry_brings_to_pass(lic_context):
    agent = ValidatorAgent(lic_context, max_retries=1)
    initial_draft = """Subject: Hello\n\nHello there\nBest regards,\nLIC Outreach Bot"""
    artifacts = {"aid": "Grounded insight"}
    verdict = agent.check(
        initial_draft,
        route_decision=None,
        pii_map={},
        artifacts=artifacts,
    )
    assert verdict.passed
    assert "CTA:" in verdict.final_draft
    assert "[artifact_id:aid]" in verdict.final_draft
