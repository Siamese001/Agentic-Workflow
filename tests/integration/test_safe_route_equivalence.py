from src.lic_agentic.reasoning.toggles import ReasoningToggles
from src.lic_agentic.stacks.outreach_stack import OutreachStack, StackInputs


class _Inputs:
    prompt = "Hello"
    company_id = "ACME"
    contact_id = "C1"


def test_safe_route_equivalence():
    stack = OutreachStack(ReasoningToggles())
    out = stack.run(StackInputs(prompt="Hello", company_id="ACME", contact_id="C1"))
    assert "draft" in out
    assert out["verdict"].passed
    assert "[artifact_id:" in out["draft"]
