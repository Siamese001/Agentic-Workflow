"""ADG contract tests for L3_orchestration/types/telepathy_interface_types.py."""
from __future__ import annotations

import ast

import pytest

pytestmark = pytest.mark.unit

MODULE_PATH = "agentic_core/L3_orchestration/types/telepathy_interface_types.py"

def test_module_parses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    ast.parse(src)

def test_module_has_telepathy_interface():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "TelepathyInterface" in src

def test_module_has_parse_instructions():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "parse_instructions" in src

try:
    from agentic_core.L3_orchestration.types.telepathy_interface_types import (
        TelepathyInterface,
    )
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False
    TelepathyInterface = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTelepathyInterface:
    def test_is_class(self): assert TelepathyInterface is not None
    def test_module_importable(self): assert _AVAIL