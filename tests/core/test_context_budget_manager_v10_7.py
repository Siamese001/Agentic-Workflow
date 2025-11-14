import pytest

from core_v10_7 import ConfigV10_7, ContextBudgetManager


class StubSummarizer:
    def __init__(self, response: str | None = None, should_fail: bool = False):
        self.response = response or "short summary"
        self.should_fail = should_fail
        self.calls = 0

    async def chat_completion_async(self, *_, **__):
        self.calls += 1
        if self.should_fail:
            raise RuntimeError("LLM unavailable")
        return {"content": self.response}


@pytest.mark.asyncio
async def test_no_pruning_below_threshold():
    config = ConfigV10_7("master_config_v10_7.json")
    config.performance_config.default_token_limit = 512
    manager = ContextBudgetManager(config=config, model_client_getter=lambda *_: StubSummarizer())

    text = "Concise document"
    result = await manager.prune(text, max_tokens=512)

    assert result == text


@pytest.mark.asyncio
async def test_pruning_uses_agentic_path_when_long():
    config = ConfigV10_7("master_config_v10_7.json")
    config.performance_config.default_token_limit = 64
    summarizer = StubSummarizer("crunched")
    manager = ContextBudgetManager(config=config, model_client_getter=lambda *_: summarizer)

    long_doc = "data " * 500
    result = await manager.prune(long_doc, max_tokens=64)

    assert "DOCUMENT PRUNED (AGENTIC)" in result
    assert "crunched" in result
    assert summarizer.calls == 1


@pytest.mark.asyncio
async def test_fallback_truncation_on_agentic_error():
    config = ConfigV10_7("master_config_v10_7.json")
    config.performance_config.default_token_limit = 64
    summarizer = StubSummarizer(should_fail=True)
    manager = ContextBudgetManager(config=config, model_client_getter=lambda *_: summarizer)

    long_doc = "failure " * 400
    result = await manager.prune(long_doc, max_tokens=64)

    assert "AGENTIC_FAILURE" in result
    assert summarizer.calls == 1
