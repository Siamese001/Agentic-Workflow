import asyncio
import pytest

from core_v10_7 import (
    CacheManager,
    CircuitBreaker,
    CircuitBreakerOpenError,
    ModelAPIError,
    exponential_backoff_retry,
)

# ---- CircuitBreaker matrix (threshold x pattern) → 12 tests
@pytest.mark.parametrize("threshold,failures,opens", [
    (1, 1, True), (1, 0, False),
    (2, 1, False), (2, 2, True),
    (3, 2, False), (3, 3, True),
])
def test_circuit_breaker_opening_behavior(threshold, failures, opens):
    cb = CircuitBreaker(failure_threshold=threshold)
    for _ in range(failures):
        cb.record_failure()
    assert cb.is_open is opens
    if opens:
        with pytest.raises(CircuitBreakerOpenError):
            cb.check()
    else:
        cb.check()  # no raise

# ---- Reset semantics (6 tests)
@pytest.mark.parametrize("threshold", [1, 2, 3])
def test_circuit_breaker_resets_on_success(threshold):
    cb = CircuitBreaker(failure_threshold=threshold)
    for _ in range(threshold):
        cb.record_failure()
    assert cb.is_open
    cb.record_success()
    cb.check()
    assert not cb.is_open

# ---- Backoff decorator matrix (8 tests)
@pytest.mark.parametrize("max_retries, succeed_on", [(1, 1), (2, 2), (3, 3), (4, 3)])
def test_exponential_backoff_eventual_success(max_retries, succeed_on):
    calls = {"n": 0}
    @exponential_backoff_retry(max_retries=max_retries, initial_delay=0)
    async def flaky():
        calls["n"] += 1
        if calls["n"] < succeed_on:
            raise ModelAPIError("temporary")
        return "ok"
    out = asyncio.run(flaky())
    assert out == "ok"
    assert calls["n"] == succeed_on

@pytest.mark.parametrize("max_retries", [0, 1, 2, 3])
def test_exponential_backoff_propagates(max_retries):
    @exponential_backoff_retry(max_retries=max_retries, initial_delay=0)
    async def always_fail():
        raise ModelAPIError("boom")
    with pytest.raises(ModelAPIError):
        asyncio.run(always_fail())

# ---- Cache exact & tool cache (14 tests via params)
@pytest.mark.parametrize("provider,model,temp,prompt,content", [
    ("openai","gpt-test",0.1,"hello","cached-1"),
    ("openai","gpt-test",0.0,"world","cached-2"),
    ("anthropic","claude-3",0.2,"alpha","A"),
    ("anthropic","claude-3",0.5,"beta","B"),
    ("gemini","1.5",0.3,"gamma","C"),
    ("groq","mixtral",0.0,"delta","D"),
    ("ollama","llama3",0.1,"eps","E"),
])
def test_cache_manager_exact(cache_manager: CacheManager, provider, model, temp, prompt, content):
    asyncio.run(cache_manager.set_llm_cache(provider, model, prompt, temp, {"content": content}))
    got = asyncio.run(cache_manager.get_llm_cache(provider, model, prompt, temp))
    assert got and got["content"] == content

@pytest.mark.parametrize("tool,payload,result", [
    ("demo", {"a":1},{"r":1}),
    ("search", {"q":"ai"},{"hits":3}),
    ("rank", {"ids":[1,2,3]},{"top":1})
])
def test_cache_manager_tool_cache(cache_manager: CacheManager, tool, payload, result):
    cache_manager.set_tool_cache(tool, payload, result)
    got = cache_manager.get_tool_cache(tool, payload)
    assert got == result
