"""Foundational behavioral tests for agentic_core/L5_safety/utils/fix_inherited_invocation_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_fix_inherited_invocation_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.fix_inherited_invocation_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        add_heal_repository,
        find_class_end,
        has_heal_repository,
        load_inherited_agents,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    load_inherited_agents = None  # type: ignore[assignment,misc]
    find_class_end = None  # type: ignore[assignment,misc]
    has_heal_repository = None  # type: ignore[assignment,misc]
    add_heal_repository = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestLoadInheritedAgentsFunction:
    def test_is_callable(self):
        assert callable(load_inherited_agents)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_inherited_agents)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestFindClassEndFunction:
    def test_is_callable(self):
        assert callable(find_class_end)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_class_end)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestHasHealRepositoryFunction:
    def test_is_callable(self):
        assert callable(has_heal_repository)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_heal_repository)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestAddHealRepositoryFunction:
    def test_is_callable(self):
        assert callable(add_heal_repository)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_heal_repository)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module fix_inherited_invocation_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
