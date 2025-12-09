import asyncio

import pytest

from core_v10_7 import (
    ModelAPIError,
    WorkflowTimeoutError,
    exponential_backoff_retry,
    get_timeout_decorator,
)


@pytest.mark.asyncio
async def test_node_timeout_raises_workflow_timeout_error():
    timeout = get_timeout_decorator(0.01)

    @timeout
    async def slow_node():
        await asyncio.sleep(0.05)

    with pytest.raises(WorkflowTimeoutError):
        await slow_node()


@pytest.mark.asyncio
async def test_exponential_backoff_retry_logs_and_retries(caplog):
    attempts = {"count": 0}

    @exponential_backoff_retry(max_retries=2, initial_delay=0)
    async def flaky_node():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ModelAPIError("temporary failure")
        return "ok"

    caplog.set_level("WARNING", logger="core_v10_7")
    result = await flaky_node()

    assert result == "ok"
    assert attempts["count"] == 3
    assert any("failed (Attempt" in rec.message for rec in caplog.records)
