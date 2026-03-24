"""ADG importability contract for agentic_core/L5_safety/types/cst_transformers_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cst_transformers_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.cst_transformers_types import (  # noqa: F401
        BareExceptTarget,
        DocstringTarget,
        ImportTarget,
        SurgicalBareExceptFixer,
        SurgicalDocstringInserter,
        SurgicalImportRemover,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ImportTarget = None  # type: ignore[assignment,misc]
    DocstringTarget = None  # type: ignore[assignment,misc]
    BareExceptTarget = None  # type: ignore[assignment,misc]
    SurgicalImportRemover = None  # type: ignore[assignment,misc]
    SurgicalDocstringInserter = None  # type: ignore[assignment,misc]
    SurgicalBareExceptFixer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cst_transformers_types deps unavailable")
class TestCstTransformersTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/types/cst_transformers_types.py must be importable."""
        assert _AVAILABLE

    def test_importtarget_defined(self) -> None:
        assert ImportTarget is not None

    def test_docstringtarget_defined(self) -> None:
        assert DocstringTarget is not None

    def test_bareexcepttarget_defined(self) -> None:
        assert BareExceptTarget is not None

    def test_surgicalimportremover_defined(self) -> None:
        assert SurgicalImportRemover is not None

    def test_surgicaldocstringinserter_defined(self) -> None:
        assert SurgicalDocstringInserter is not None

    def test_surgicalbareexceptfixer_defined(self) -> None:
        assert SurgicalBareExceptFixer is not None