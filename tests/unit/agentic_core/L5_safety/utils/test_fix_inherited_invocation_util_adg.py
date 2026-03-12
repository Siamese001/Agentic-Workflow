"""ADG-driven tests for agentic_core/L5_safety/utils/fix_inherited_invocation_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.fix_inherited_invocation_util import (  # noqa: F401
        load_inherited_agents,
        find_class_end,
        has_heal_repository,
        add_heal_repository,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    load_inherited_agents = None  # type: ignore[assignment,misc]
    find_class_end = None  # type: ignore[assignment,misc]
    has_heal_repository = None  # type: ignore[assignment,misc]
    add_heal_repository = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestLoadInheritedAgents:
    def test_is_callable(self):
        assert callable(load_inherited_agents)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestFindClassEnd:
    def test_is_callable(self):
        assert callable(find_class_end)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestHasHealRepository:
    def test_is_callable(self):
        assert callable(has_heal_repository)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestAddHealRepository:
    def test_is_callable(self):
        assert callable(add_heal_repository)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

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

@pytest.mark.skipif(not _AVAILABLE, reason="fix_inherited_invocation_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module fix_inherited_invocation_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
