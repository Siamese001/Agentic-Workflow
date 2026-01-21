from types import SimpleNamespace

from src.lic_agentic.reasoning.toggles import ReasoningToggles
from src.lic_agentic.stacks.outreach_stack import OutreachStack


def test_full_pipeline_pass_rate():
    stack = OutreachStack(ReasoningToggles())
    samples = [
        SimpleNamespace(prompt="Excited to connect", company_id="ACME", contact_id="C1"),
        SimpleNamespace(
            prompt="Shared interest in innovation", company_id="OMEGA", contact_id="C2"
        ),
        SimpleNamespace(prompt="Curious about collaboration", company_id="BETA", contact_id="C3"),
    ]
    passes = 0
    for sample in samples:
        outcome = stack.run(sample)
        verdict = outcome["verdict"]
        if verdict.passed:
            passes += 1
        assert "[artifact_id:" in outcome["draft"]
    assert passes / len(samples) >= 0.85
    assert stack.validator.metrics.pass_rate() >= 0.85
    failing_drafts = [
        "Subject: Follow up\n\n"
        + " ".join(
            [
                "This detailed note maintains substantial context for evaluation",
                "and demonstrates reflective intent with customer centric framing",
                "while awaiting artifact grounding",
                "The narrative reiterates partnership opportunities across multiple domains",
                "and reinforces diligence in aligning outcomes with stakeholder needs",
            ]
        )
        + "\nCTA: Would a quick sync be useful?\nBest regards,\nLIC Outreach Bot",
        "Subject: Quick ping\n\n"
        + " ".join(
            [
                "Here is another comprehensive paragraph designed to hold steady token counts",
                "showing empathy and curiosity about mutual goals",
                "pending reinforcement with evidence",
                "The structure acknowledges prior interactions and commitments",
                "and articulates the shared momentum behind the outreach",
            ]
        )
        + "\nCTA: Can we schedule a short intro?\nBest regards,\nLIC Outreach Bot",
    ]
    for failing in failing_drafts:
        verdict = stack.validator.check(
            failing,
            route_decision=None,
            pii_map={},
            artifacts={"aid": "Grounded data point"},
        )
        assert verdict.passed
    assert stack.validator.metrics.retry_success_rate() >= 0.8
    assert stack.validator.metrics.token_drift() <= 0.1
