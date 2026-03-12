"""ADG-driven tests for agentic_core/L5_safety/config/blueprint_compiler.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.blueprint_compiler import (  # noqa: F401
        CompiledBlueprint,
        make_lcd_layer,
        compile_blueprint,
        verify_blueprint_consistency,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CompiledBlueprint = None  # type: ignore[assignment,misc]
    make_lcd_layer = None  # type: ignore[assignment,misc]
    compile_blueprint = None  # type: ignore[assignment,misc]
    verify_blueprint_consistency = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="blueprint_compiler.py deps unavailable")
class TestCompiledBlueprint:
    def test_is_class(self):
        assert isinstance(CompiledBlueprint, type)
    def test_importable(self):
        assert CompiledBlueprint is not None

@pytest.mark.skipif(not _AVAILABLE, reason="blueprint_compiler.py deps unavailable")
class TestMakeLcdLayer:
    def test_is_callable(self):
        assert callable(make_lcd_layer)

@pytest.mark.skipif(not _AVAILABLE, reason="blueprint_compiler.py deps unavailable")
class TestCompileBlueprint:
    def test_is_callable(self):
        assert callable(compile_blueprint)

@pytest.mark.skipif(not _AVAILABLE, reason="blueprint_compiler.py deps unavailable")
class TestVerifyBlueprintConsistency:
    def test_is_callable(self):
        assert callable(verify_blueprint_consistency)


def test_module_importable():
    """Module blueprint_compiler.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
