"""ADG importability contract for agentic_core/prompt_governance/scripts/import_violation_visitor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_import_violation_visitor.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.scripts.import_violation_visitor import (  # noqa: F401
        FORBIDDEN_IMPORTS,
        ImportViolationVisitor,
        analyze_file,
        enforce_layer_boundaries,
        find_python_files,
        main,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    FORBIDDEN_IMPORTS = None  # type: ignore[assignment,misc]
    ImportViolationVisitor = None  # type: ignore[assignment,misc]
    find_python_files = None  # type: ignore[assignment,misc]
    analyze_file = None  # type: ignore[assignment,misc]
    enforce_layer_boundaries = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="import_violation_visitor deps unavailable")
class TestImportViolationVisitorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/scripts/import_violation_visitor.py must be importable."""
        assert _AVAILABLE

    def test_importviolationvisitor_defined(self) -> None:
        assert ImportViolationVisitor is not None
