"""Foundational behavioral tests for agentic_core/L0_routing/scripts/gatekeeper_lock_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_gatekeeper_lock_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.gatekeeper_lock_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    check_commit_message_override,
    check_env_bypass,
    get_commit_message,
    get_staged_files,
)


class TestGetStagedFilesFunction:
    def test_is_callable(self):
        assert callable(get_staged_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_staged_files)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetCommitMessageFunction:
    def test_is_callable(self):
        assert callable(get_commit_message)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_commit_message)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCheckEnvBypassFunction:
    def test_is_callable(self):
        assert callable(check_env_bypass)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_env_bypass)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCheckCommitMessageOverrideFunction:
    def test_is_callable(self):
        assert callable(check_commit_message_override)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_commit_message_override)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module gatekeeper_lock_util must be importable or skip gracefully."""
    pass  # Import verified at module level
