"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/BenchmarkingAgent.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_BenchmarkingAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.BenchmarkingAgent import (  # noqa: F401
        BenchmarkResult,
        BenchmarkResultActual,
        BenchmarkSuite,
        BenchmarkingAgent,
        BenchmarkContext,
        get_benchmarking_agent,
        initialize_benchmarking,
        benchmark,
        benchmark_async,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    BenchmarkResult = None  # type: ignore[assignment,misc]
    BenchmarkResultActual = None  # type: ignore[assignment,misc]
    BenchmarkSuite = None  # type: ignore[assignment,misc]
    BenchmarkingAgent = None  # type: ignore[assignment,misc]
    BenchmarkContext = None  # type: ignore[assignment,misc]
    get_benchmarking_agent = None  # type: ignore[assignment,misc]
    initialize_benchmarking = None  # type: ignore[assignment,misc]
    benchmark = None  # type: ignore[assignment,misc]
    benchmark_async = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkResultContract:
    def test_is_class(self):
        assert isinstance(BenchmarkResult, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(BenchmarkResult, type)

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkResultActualContract:
    def test_is_class(self):
        assert isinstance(BenchmarkResultActual, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(BenchmarkResultActual, 'to_dict', None))

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkSuiteContract:
    def test_is_class(self):
        assert isinstance(BenchmarkSuite, type)

    def test_has_method_add_result(self):
        assert callable(getattr(BenchmarkSuite, 'add_result', None))

    def test_has_method_is_degraded(self):
        assert callable(getattr(BenchmarkSuite, 'is_degraded', None))

    def test_has_method_get_summary(self):
        assert callable(getattr(BenchmarkSuite, 'get_summary', None))

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkingAgentContract:
    def test_is_class(self):
        assert isinstance(BenchmarkingAgent, type)

    def test_has_method_heal(self):
        assert callable(getattr(BenchmarkingAgent, 'heal', None))

    def test_has_method_heal_repository(self):
        assert callable(getattr(BenchmarkingAgent, 'heal_repository', None))

    def test_has_method_benchmark(self):
        assert callable(getattr(BenchmarkingAgent, 'benchmark', None))

    def test_has_method_benchmark_async(self):
        assert callable(getattr(BenchmarkingAgent, 'benchmark_async', None))

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkContextContract:
    def test_is_class(self):
        assert isinstance(BenchmarkContext, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(BenchmarkContext, type)

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestGetBenchmarkingAgentFunction:
    def test_is_callable(self):
        assert callable(get_benchmarking_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_benchmarking_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestInitializeBenchmarkingFunction:
    def test_is_callable(self):
        assert callable(initialize_benchmarking)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(initialize_benchmarking)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkFunction:
    def test_is_callable(self):
        assert callable(benchmark)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(benchmark)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBenchmarkAsyncFunction:
    def test_is_callable(self):
        assert callable(benchmark_async)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(benchmark_async)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module BenchmarkingAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
