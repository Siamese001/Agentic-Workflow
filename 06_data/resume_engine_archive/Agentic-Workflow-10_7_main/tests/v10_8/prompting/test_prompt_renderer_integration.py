import asyncio
from types import SimpleNamespace

import pytest

from core_v10_7 import PromptEnvelope
from stacks_v10_8.prompt_renderer_stack import PromptRendererStack


class _StubDecision:
    def __init__(self, payload):
        self._payload = payload

    def dict(self):  # pragma: no cover - simple passthrough
        return dict(self._payload)


class DummyContext:
    def __init__(self):
        config = SimpleNamespace()
        prompt_manager = SimpleNamespace()
        response_validator = SimpleNamespace()
        context_budget_manager = SimpleNamespace()
        metrics_collector = SimpleNamespace()
        self.config = config
        self.prompt_manager = prompt_manager
        self.response_validator = response_validator
        self.context_budget_manager = context_budget_manager
        self.metrics_collector = metrics_collector
        self.self_correction_manager = None
        self.policy_stack = SimpleNamespace(guard_output=lambda payload: _StubDecision({"allow": True, "payload": payload}))
        self.constitutional_engine = SimpleNamespace(
            review_text=lambda text: _StubDecision({"text": text, "decision": "ok"})
        )
        self.prompt_injection_detector = SimpleNamespace(detect=lambda text: {"analysis": "clean", "text": text})

    def is_mcp_enabled(self):  # pragma: no cover - trivial stub
        return False

    def ensure_mcp_clients(self):  # pragma: no cover - trivial stub
        return {}


@pytest.mark.asyncio
async def test_prompt_renderer_appends_safety_signals():
    state = {
        "prompts": {
            "prompt_envelope": {
                "framing": "You are a helpful assistant",
                "context": "User provided resume snippets",
                "reasoning": "Summarize experience succinctly",
                "instructions": "Generate three bullet points",
                "tool_context": "No tools needed",
                "output_schema": "{bullets: list[str]}",
            }
        }
    }

    renderer = PromptRendererStack(DummyContext())
    result = await renderer.run_async(state)

    final_prompt = result["prompts"]["final_prompt"]
    assert "[FRAMING]\nYou are a helpful assistant" in final_prompt
    assert "[CONTEXT]\nUser provided resume snippets" in final_prompt
    assert "[REASONING]\nSummarize experience succinctly" in final_prompt
    assert "[INSTRUCTIONS]\nGenerate three bullet points" in final_prompt
    assert "[TOOL CONTEXT]\nNo tools needed" in final_prompt
    assert "[OUTPUT SCHEMA]\n{bullets: list[str]}" in final_prompt
    assert "injection" in final_prompt
    assert "policy" in final_prompt
    assert "constitution" in final_prompt
