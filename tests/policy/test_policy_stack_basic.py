from stacks_v10_8.policy_stack import PolicyStack


class DummyOutput(dict):
    """Simple mapping to mimic stack outputs."""

    def __init__(self, text: str):
        super().__init__(text=text)
        self.text = text


def _make_stack():
    return PolicyStack(context=None, debug_mode=False)


def test_benign_output_allowed():
    stack = _make_stack()
    decision = stack.guard_output(DummyOutput("Generic help text."))

    assert hasattr(decision, "allowed")
    assert hasattr(decision, "reason")
    assert decision.allowed is True


def test_disallowed_output_blocked_when_rule_exists():
    stack = _make_stack()
    output = DummyOutput("This mentions a forbidden_topic that should be blocked.")

    decision = stack.guard_output(output)

    assert hasattr(decision, "allowed")
    assert hasattr(decision, "reason")
    assert decision.allowed is False
    assert decision.reason is not None
