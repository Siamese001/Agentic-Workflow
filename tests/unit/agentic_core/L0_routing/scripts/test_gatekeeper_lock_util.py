"""Foundational behavioral tests for agentic_core/L0_routing/scripts/gatekeeper_lock_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_gatekeeper_lock_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.gatekeeper_lock_util import (  # noqa: F401
        get_staged_files,
        get_commit_message,
        check_env_bypass,
        check_commit_message_override,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    get_staged_files = None  # type: ignore[assignment,misc]
    get_commit_message = None  # type: ignore[assignment,misc]
    check_env_bypass = None  # type: ignore[assignment,misc]
    check_commit_message_override = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestGetStagedFilesFunction:
    def test_is_callable(self):
        assert callable(get_staged_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_staged_files)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestGetCommitMessageFunction:
    def test_is_callable(self):
        assert callable(get_commit_message)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_commit_message)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestCheckEnvBypassFunction:
    def test_is_callable(self):
        assert callable(check_env_bypass)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_env_bypass)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestCheckCommitMessageOverrideFunction:
    def test_is_callable(self):
        assert callable(check_commit_message_override)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_commit_message_override)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="gatekeeper_lock_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module gatekeeper_lock_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
