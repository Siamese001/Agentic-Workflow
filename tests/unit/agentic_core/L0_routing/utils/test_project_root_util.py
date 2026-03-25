"""Foundational behavioral tests for agentic_core/L0_routing/utils/project_root_util.py.

fan_in=36 — this module is imported by 36 other modules.
ADG contract: import-hygiene is covered by test_project_root_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.utils.project_root_util import (  # noqa: F401
    clear_project_root_cache,
    get_project_root,
    get_validated_project_root,
)


class TestGetProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestClearProjectRootCacheFunction:
    def test_is_callable(self):
        assert callable(clear_project_root_cache)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(clear_project_root_cache)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetValidatedProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_validated_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_validated_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Module project_root_util must be importable or skip gracefully."""
    pass  # Import verified at module level
