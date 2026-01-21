"""Unit tests for the async Conductor helper."""

import asyncio

import pytest
from src.lic_agentic.orchestration.conductor import Conductor


async def _task(value):
    await asyncio.sleep(0)
    return value


def test_conductor_generates_stable_artifact_ids():
    conductor = Conductor(seed=3)
    first = conductor.make_artifact_id("value", company_id="ACME")
    conductor.reset()
    second = conductor.make_artifact_id("value", company_id="ACME")
    assert first == second


def test_conductor_latency_delay_positive():
    conductor = Conductor()

    async def _job():
        return 0, "done"

    results = asyncio.run(conductor._execute_async([lambda: _job()]))
    assert results == [(0, "done")]
    assert conductor._latency_delay(500) > 0


def test_wrap_tool_call_runs_callable():
    conductor = Conductor()

    def call():
        return "value", 50

    wrapped = conductor.wrap_tool_call(0, call)
    results = asyncio.run(conductor._execute_async([wrapped]))
    assert results[0][1] == "value"


def test_conductor_run_invokes_factories():
    conductor = Conductor()

    async def job():
        return 0, "payload"

    outcome = conductor.run([lambda: job()])
    assert outcome == [(0, "payload")]
    assert conductor.concurrency == 3


def test_wrap_tool_call_supports_after_callback():
    conductor = Conductor()
    seen = []

    def call():
        return "value", 10

    def after(value):
        seen.append(value)

    wrapped = conductor.wrap_tool_call(0, call, after=after)
    asyncio.run(conductor._execute_async([wrapped]))
    assert seen == ["value"]


def test_conductor_requires_positive_concurrency():
    with pytest.raises(ValueError):
        Conductor(concurrency=0)


def test_run_with_no_jobs_returns_empty_list():
    conductor = Conductor()
    assert conductor.run([]) == []
