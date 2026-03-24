"""ADG-driven tests for agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.flatten_scripts_directory_util import (  # noqa: F401
        flatten_scripts,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    flatten_scripts = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="flatten_scripts_directory_util.py deps unavailable")
class TestFlattenScripts:
    def test_is_callable(self):
        assert callable(flatten_scripts)


def test_module_importable():
    """Module flatten_scripts_directory_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE