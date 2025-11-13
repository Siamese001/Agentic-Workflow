from types import SimpleNamespace

from src.lic_agentic.reasoning.toggles import ReasoningToggles
from src.lic_agentic.stacks.outreach_stack import OutreachStack


def test_token_drift_guard(lic_context):
    stack = OutreachStack(ReasoningToggles(), context=lic_context)
    sample = SimpleNamespace(prompt="Checking drift bounds", company_id="ACME", contact_id="C1")
    outcome = stack.run(sample)
    verdict = outcome["verdict"]
    assert verdict.passed
    drift = stack.validator.metrics.token_drift()
    assert drift <= 0.1
