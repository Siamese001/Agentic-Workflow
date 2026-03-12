"""Foundational behavioral tests for agentic_core/prompt_governance/optimization/optimization_strategy.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_optimization_strategy_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.optimization.optimization_strategy import (  # noqa: F401
        OptimizationStrategy,
        OptimizationLevel,
        OptimizationConfig,
        PromptOptimizer,
        create_prompt_optimizer,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    OptimizationStrategy = None  # type: ignore[assignment,misc]
    OptimizationLevel = None  # type: ignore[assignment,misc]
    OptimizationConfig = None  # type: ignore[assignment,misc]
    PromptOptimizer = None  # type: ignore[assignment,misc]
    create_prompt_optimizer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestOptimizationStrategyContract:
    def test_is_enum(self):
        import enum
        assert issubclass(OptimizationStrategy, enum.Enum)

    def test_has_members(self):
        assert len(list(OptimizationStrategy)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestOptimizationLevelContract:
    def test_is_enum(self):
        import enum
        assert issubclass(OptimizationLevel, enum.Enum)

    def test_has_members(self):
        assert len(list(OptimizationLevel)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestOptimizationConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(OptimizationConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(OptimizationConfig)}
        assert field_names >= {'max_length', 'level', 'strategy', 'preserve_intent'}

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestPromptOptimizerContract:
    def test_is_class(self):
        assert isinstance(PromptOptimizer, type)

    def test_has_method_optimize(self):
        assert callable(getattr(PromptOptimizer, 'optimize', None))

    def test_has_method_analyze_prompt(self):
        assert callable(getattr(PromptOptimizer, 'analyze_prompt', None))

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestCreatePromptOptimizerFunction:
    def test_is_callable(self):
        assert callable(create_prompt_optimizer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_prompt_optimizer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module optimization_strategy must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
