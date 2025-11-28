import asyncio
from types import SimpleNamespace

import pytest

from core_v10_7 import PromptTemplateManager
from core_v10_7.services import _format_prompt_with_defaults


class NoopBudgetManager:
    async def prune(self, document: str, max_tokens: int | None = None) -> str:  # pragma: no cover - trivial helper
        return document or ""


class StubLLMClient:
    def __init__(self, content: str):
        self._content = content

    async def chat_completion_async(self, *_, **__):
        return {"content": self._content}


class PruningBudgetManager:
    def __init__(self, marker: str = "AGENTIC"):
        self.marker = marker

    async def prune(self, document: str, max_tokens: int | None = None) -> str:
        text = document or ""
        if len(text) > 50:
            return f"compressed\n\n[... DOCUMENT PRUNED ({self.marker}) ...]"
        return text


@pytest.mark.asyncio
async def test_prompt_injects_goal_and_failures_header():
    manager = PromptTemplateManager(feedback_reader=SimpleNamespace(get_failures=lambda max_entries=100: []))
    manager.top_failures = ["PromptAgent::alignment"]
    template = manager.get_template("review_draft_strategy")

    formatted = await _format_prompt_with_defaults(
        template,
        {
            "master_resume": "resume text",
            "draft_text": "draft",
            "job_description": "job",
            "strategy": {"tone": "executive"},
        },
        NoopBudgetManager(),
        manager.goal_state,
        manager.top_failures,
    )

    assert "GLOBAL_GOAL:" in formatted
    assert "BEWARE:" in formatted
    assert "executive" in formatted


@pytest.mark.asyncio
async def test_prompt_prunes_long_inputs(monkeypatch):
    template_manager = PromptTemplateManager(feedback_reader=SimpleNamespace(get_failures=lambda max_entries=100: []))
    template_manager.top_failures = ["Stack::failure"]
    template = template_manager.get_template("validate_claims")

    huge_text = "Long " * 1000
    formatted = await _format_prompt_with_defaults(
        template,
        {
            "master_resume": huge_text,
            "draft_text": huge_text,
            "job_description": huge_text,
            "strategy": {"tone": "analytical"},
        },
        PruningBudgetManager(),
        template_manager.goal_state,
        template_manager.top_failures,
    )

    assert "DOCUMENT PRUNED" in formatted
    assert len(formatted) < len(huge_text)


def test_template_fallback_error_message():
    manager = PromptTemplateManager(feedback_reader=SimpleNamespace(get_failures=lambda max_entries=100: []))
    missing_prompt = manager.get_template("nonexistent_tool_name")
    assert "ERROR: PROMPT NOT FOUND" in missing_prompt


@pytest.mark.asyncio
async def test_prompt_handles_missing_optional_fields():
    manager = PromptTemplateManager(feedback_reader=SimpleNamespace(get_failures=lambda max_entries=100: []))
    template = manager.get_template("prompt_engineer")
    formatted = await _format_prompt_with_defaults(
        template,
        {"strategy": {}},
        NoopBudgetManager(),
        manager.goal_state,
        manager.top_failures,
    )

    assert "unknown" in formatted
    assert "Default style" in formatted
