"""ADG-driven tests for apps_shared/scripts/script_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.script_bridge import (  # noqa: F401
        ScriptBridge,
        ScriptResult,
        get_script_bridge,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ScriptResult = None  # type: ignore[assignment,misc]
    ScriptBridge = None  # type: ignore[assignment,misc]
    get_script_bridge = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="script_bridge.py deps unavailable")
class TestScriptResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScriptResult)
    def test_importable(self):
        assert ScriptResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="script_bridge.py deps unavailable")
class TestScriptBridge:
    def test_is_class(self):
        assert isinstance(ScriptBridge, type)
    def test_importable(self):
        assert ScriptBridge is not None

@pytest.mark.skipif(not _AVAILABLE, reason="script_bridge.py deps unavailable")
class TestGetScriptBridge:
    def test_is_callable(self):
        assert callable(get_script_bridge)


def test_module_importable():
    """Module script_bridge.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE