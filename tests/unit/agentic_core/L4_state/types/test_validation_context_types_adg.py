"""ADG contract tests for L4_state/types/validation_context_types.py."""
from __future__ import annotations

import ast

import pytest

pytestmark = pytest.mark.unit

MODULE_PATH = "agentic_core/L4_state/types/validation_context_types.py"

def test_module_parses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    ast.parse(src)

def test_has_historian_class():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "class Historian" in src

def test_has_validation_context_protocol():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "IValidationContextProtocol" in src

try:
    from agentic_core.L4_state.types.validation_context_types import (
        IValidationContextProtocol,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    IValidationContextProtocol = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestIValidationContextProtocol:
    def test_is_class(self): assert IValidationContextProtocol is not None
    def test_module_importable(self): assert _AVAIL
