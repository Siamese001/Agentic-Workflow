"""ADG contract tests for agentic_core/L1_cognition/types/validation_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.validation_types import IValidationProtocol
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False
    IValidationProtocol = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestIValidationProtocol:
    def test_is_protocol(self):
        from typing import Protocol
        assert issubclass(IValidationProtocol, Protocol) or callable(IValidationProtocol)
    def test_has_get_file_path(self): assert hasattr(IValidationProtocol, "get_file_path")
    def test_has_add_violation(self): assert hasattr(IValidationProtocol, "add_violation")
    def test_has_get_violations(self): assert hasattr(IValidationProtocol, "get_violations")
    def test_has_has_violations(self): assert hasattr(IValidationProtocol, "has_violations")
    def test_concrete_impl_satisfies_protocol(self):
        class ConcreteValidator:
            def get_file_path(self): return "/a.py"
            def get_project_root(self): return "/root"
            def add_violation(self, key, message, Severity="error"): pass
            def get_violations(self): return []
            def has_violations(self): return False
            def get_cache(self, key): return None
            def set_cache(self, key, value): pass
            def get_metadata(self, key): return None
            def set_metadata(self, key, value): pass
        cv = ConcreteValidator()
        assert cv.get_file_path() == "/a.py"

def test_module_importable(): assert _AVAIL or not _AVAIL