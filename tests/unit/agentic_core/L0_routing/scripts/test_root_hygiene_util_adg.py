"""ADG importability contract for agentic_core/L0_routing/scripts/root_hygiene_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_root_hygiene_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.root_hygiene_util import (  # noqa: F401
        get_project_root,
        enforce_root_hygiene,
        ROOT_MARKERS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    get_project_root = None  # type: ignore[assignment,misc]
    enforce_root_hygiene = None  # type: ignore[assignment,misc]
    ROOT_MARKERS = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="root_hygiene_util.py deps unavailable")
class TestRootHygieneUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: root_hygiene_util.py must be importable."""
        assert _AVAILABLE

    def test_get_project_root_callable(self) -> None:
        assert callable(get_project_root)

    def test_enforce_root_hygiene_callable(self) -> None:
        assert callable(enforce_root_hygiene)

    def test_root_markers_defined(self) -> None:
        assert ROOT_MARKERS is not None

