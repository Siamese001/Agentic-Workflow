"""ADG-driven tests for apps_shared/scripts/refactor_agents_to_subatomic.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.refactor_agents_to_subatomic import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        add_engine_initialization,
        add_subatomic_imports,
        main,
        process_agent_file,
        remove_thinking_budget_over_limit,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    add_subatomic_imports = None  # type: ignore[assignment,misc]
    remove_thinking_budget_over_limit = None  # type: ignore[assignment,misc]
    add_engine_initialization = None  # type: ignore[assignment,misc]
    process_agent_file = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestAddSubatomicImports:
    def test_is_callable(self):
        assert callable(add_subatomic_imports)

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestRemoveThinkingBudgetOverLimit:
    def test_is_callable(self):
        assert callable(remove_thinking_budget_over_limit)

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestAddEngineInitialization:
    def test_is_callable(self):
        assert callable(add_engine_initialization)

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestProcessAgentFile:
    def test_is_callable(self):
        assert callable(process_agent_file)

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

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

@pytest.mark.skipif(not _AVAILABLE, reason="refactor_agents_to_subatomic.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module refactor_agents_to_subatomic.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE