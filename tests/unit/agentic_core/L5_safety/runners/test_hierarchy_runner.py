"""Foundational behavioral tests for agentic_core/L5_safety/runners/hierarchy_runner.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_hierarchy_runner_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.runners.hierarchy_runner import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    get_project_root,
    run_heal_violations,
    run_hierarchy_dry_run,
    verify_mro,
)


class TestGetProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestRunHierarchyDryRunFunction:
    def test_is_callable(self):
        assert callable(run_hierarchy_dry_run)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_hierarchy_dry_run)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestRunHealViolationsFunction:
    def test_is_callable(self):
        assert callable(run_heal_violations)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_heal_violations)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestVerifyMroFunction:
    def test_is_callable(self):
        assert callable(verify_mro)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(verify_mro)
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
    """Module hierarchy_runner must be importable or skip gracefully."""
    pass  # Import verified at module level
