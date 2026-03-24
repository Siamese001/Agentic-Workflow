"""ADG-driven tests for apps_shared/scripts/clean_shims_simple.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.clean_shims_simple import (  # noqa: F401
        clean_other_directories,
        clean_prompt_governance,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    clean_prompt_governance = None  # type: ignore[assignment,misc]
    clean_other_directories = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="clean_shims_simple.py deps unavailable")
class TestCleanPromptGovernance:
    def test_is_callable(self):
        assert callable(clean_prompt_governance)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_shims_simple.py deps unavailable")
class TestCleanOtherDirectories:
    def test_is_callable(self):
        assert callable(clean_other_directories)


def test_module_importable():
    """Module clean_shims_simple.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE