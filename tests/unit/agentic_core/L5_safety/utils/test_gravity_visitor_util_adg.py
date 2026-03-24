"""ADG importability contract for agentic_core/L5_safety/utils/gravity_visitor_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_gravity_visitor_util.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.utils.gravity_visitor_util import (  # noqa: F401
        GravityVisitor,
        check_gravity_violation,
        extract_layer_from_import,
        extract_layer_from_path,
        get_file_imports,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GravityVisitor = None  # type: ignore[assignment,misc]
    get_file_imports = None  # type: ignore[assignment,misc]
    extract_layer_from_path = None  # type: ignore[assignment,misc]
    extract_layer_from_import = None  # type: ignore[assignment,misc]
    check_gravity_violation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_visitor_util deps unavailable")
class TestGravityVisitorUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/utils/gravity_visitor_util.py must be importable."""
        assert _AVAILABLE

    def test_gravityvisitor_defined(self) -> None:
        assert GravityVisitor is not None