import asyncio

import pytest

from core_v10_7 import CacheManager

@pytest.mark.parametrize(
    "provider,model,temps",
    [
        ("openai", "gpt-test", [0.0, 0.1, 0.2]),
        ("anthropic", "claude-3", [0.0, 0.3]),
        ("gemini", "1.5-pro", [0.2, 0.5]),
    ],
)
def test_cache_roundtrip_variants(
    cache_manager: CacheManager, provider, model, temps
):
    for temp in temps:
        key = f"{provider}-{model}-{temp}"
        asyncio.run(
            cache_manager.set_llm_cache(
                provider, model, key, temp, {"content": key}
            )
        )
        got = asyncio.run(cache_manager.get_llm_cache(provider, model, key, temp))
        assert got and got["content"] == key

@pytest.mark.parametrize("tool", ["search", "rerank", "hybrid", "bm25", "embed"])
def test_tool_cache_variants(cache_manager: CacheManager, tool):
    payload = {"k": tool}
    cache_manager.set_tool_cache(tool, payload, {"ok": True, "tool": tool})
    assert cache_manager.get_tool_cache(tool, payload)["ok"]
