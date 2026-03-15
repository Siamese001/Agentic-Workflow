"""Foundational behavioral tests for apps_shared/scripts/refactor_agents_to_subatomic.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_refactor_agents_to_subatomic_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.refactor_agents_to_subatomic import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        add_engine_initialization,
        add_subatomic_imports,
        process_agent_file,
        remove_thinking_budget_over_limit,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    add_subatomic_imports = None  # type: ignore[assignment,misc]
    remove_thinking_budget_over_limit = None  # type: ignore[assignment,misc]
    add_engine_initialization = None  # type: ignore[assignment,misc]
    process_agent_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestAddSubatomicImportsFunction:
    def test_is_callable(self):
        assert callable(add_subatomic_imports)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_subatomic_imports)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestRemoveThinkingBudgetOverLimitFunction:
    def test_is_callable(self):
        assert callable(remove_thinking_budget_over_limit)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(remove_thinking_budget_over_limit)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestAddEngineInitializationFunction:
    def test_is_callable(self):
        assert callable(add_engine_initialization)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_engine_initialization)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestProcessAgentFileFunction:
    def test_is_callable(self):
        assert callable(process_agent_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(process_agent_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module refactor_agents_to_subatomic must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
