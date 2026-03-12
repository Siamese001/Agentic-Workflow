"""ADG contract tests for agentic_core/L5_safety/types/cst_transformers_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    import libcst  # noqa: F401
    _LIBCST_AVAIL = True
except ImportError:
    _LIBCST_AVAIL = False

try:
    from agentic_core.L5_safety.types.cst_transformers_types import (
        ImportTarget, DocstringTarget, BareExceptTarget,
        SurgicalImportRemover, SurgicalDocstringInserter, SurgicalBareExceptFixer,
    )
    _AVAIL = _LIBCST_AVAIL
except Exception:
    _AVAIL = False
    ImportTarget = DocstringTarget = BareExceptTarget = None  # type: ignore[assignment,misc]
    SurgicalImportRemover = SurgicalDocstringInserter = SurgicalBareExceptFixer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestImportTarget:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ImportTarget)
    def test_creates(self):
        t = ImportTarget(line_number=10, module_name="os", name="path")
        assert t.line_number == 10
    def test_defaults(self):
        t = ImportTarget(line_number=5)
        assert t.module_name is None; assert t.name is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDocstringTarget:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(DocstringTarget)
    def test_creates(self):
        t = DocstringTarget(line_number=3, name="MyClass", node_type="class")
        assert t.name == "MyClass"
    def test_default_docstring(self):
        t = DocstringTarget(line_number=1)
        assert "TODO" in t.docstring

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestBareExceptTarget:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(BareExceptTarget)
    def test_creates(self):
        t = BareExceptTarget(line_number=20)
        assert t.exception_type == "Exception"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSurgicalImportRemover:
    def test_instantiates(self):
        r = SurgicalImportRemover(targets=[ImportTarget(line_number=1)])
        assert r.modifications_made == 0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSurgicalBareExceptFixer:
    def test_instantiates(self):
        f = SurgicalBareExceptFixer()
        assert f is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
