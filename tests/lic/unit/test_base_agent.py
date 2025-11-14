"""Tests for the shared LICBaseAgent dependency wiring."""

from src.lic_agentic.core import LICBaseAgent


class _DummyContext:
    def __init__(self):
        self.values = {
            "metrics_tracker": object(),
            "policy_controller": object(),
            "tool_registry": object(),
            "content_store": object(),
            "evidence_registry": object(),
            "conductor": object(),
        }
        self.calls: list[str] = []

    def resolve(self, key: str):  # pragma: no cover - helper used in tests only
        self.calls.append(key)
        if key not in self.values:
            raise KeyError(key)
        return self.values[key]


class _ConcreteAgent(LICBaseAgent):
    """Expose LICBaseAgent internals for testing."""

    def __init__(self, context):
        super().__init__(context)
        self.log_calls: list[str] = []

    def log(self, message: str) -> None:
        self.log_calls.append(message)
        return super().log(message)


def test_base_agent_resolves_all_core_dependencies():
    context = _DummyContext()
    agent = _ConcreteAgent(context)
    assert agent.metrics is context.values["metrics_tracker"]
    assert agent.policy is context.values["policy_controller"]
    assert agent.registry is context.values["tool_registry"]
    assert agent.content_store is context.values["content_store"]
    assert agent.evidence_registry is context.values["evidence_registry"]
    assert agent.conductor is context.values["conductor"]
    assert context.calls == [
        "metrics_tracker",
        "policy_controller",
        "tool_registry",
        "content_store",
        "evidence_registry",
        "conductor",
    ]


def test_base_agent_log_hook_is_noop():
    context = _DummyContext()
    agent = _ConcreteAgent(context)
    agent.log("diagnostic message")
    assert agent.log_calls == ["diagnostic message"]
