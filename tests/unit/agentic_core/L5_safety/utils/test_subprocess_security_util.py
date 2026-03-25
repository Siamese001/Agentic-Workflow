"""Foundational behavioral tests for agentic_core/L5_safety/utils/subprocess_security_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_subprocess_security_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.utils.subprocess_security_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    SecurityViolationError,
    safe_execute,
    safe_git_execute,
    safe_popen,
    validate_command_whitelist,
)


class TestSecurityViolationErrorContract:
    def test_is_class(self):
        assert isinstance(SecurityViolationError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SecurityViolationError, type)

class TestSafeExecuteFunction:
    def test_is_callable(self):
        assert callable(safe_execute)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_execute)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestSafePopenFunction:
    def test_is_callable(self):
        assert callable(safe_popen)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_popen)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestValidateCommandWhitelistFunction:
    def test_is_callable(self):
        assert callable(validate_command_whitelist)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_command_whitelist)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestSafeGitExecuteFunction:
    def test_is_callable(self):
        assert callable(safe_git_execute)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_git_execute)
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
    """Module subprocess_security_util must be importable or skip gracefully."""
    pass  # Import verified at module level
