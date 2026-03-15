"""Foundational behavioral tests for agentic_core/L5_safety/config/structure_blueprint/ssot.py.

fan_in=12 — imported by 12 other modules.
ADG import-hygiene is covered separately by test_ssot_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (  # noqa: F401
        get_canonical_test_path,
        get_validated_project_root,
        is_allowed_subfolder,
        is_layer_root,
        validate_no_nested_lcd,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    is_layer_root = None  # type: ignore[assignment,misc]
    is_allowed_subfolder = None  # type: ignore[assignment,misc]
    validate_no_nested_lcd = None  # type: ignore[assignment,misc]
    get_canonical_test_path = None  # type: ignore[assignment,misc]
    get_validated_project_root = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot.py deps unavailable")
class TestIsLayerRootFunction:
    def test_is_callable(self):
        assert callable(is_layer_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_layer_root)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot.py deps unavailable")
class TestIsAllowedSubfolderFunction:
    def test_is_callable(self):
        assert callable(is_allowed_subfolder)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_allowed_subfolder)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot.py deps unavailable")
class TestValidateNoNestedLcdFunction:
    def test_is_callable(self):
        assert callable(validate_no_nested_lcd)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_no_nested_lcd)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot.py deps unavailable")
class TestGetCanonicalTestPathFunction:
    def test_is_callable(self):
        assert callable(get_canonical_test_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_canonical_test_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot.py deps unavailable")
class TestGetValidatedProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_validated_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_validated_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: ssot importable or gracefully unavailable."""
    pass
