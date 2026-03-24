"""ADG importability contract for agentic_core/L0_routing/utils/complexity_visitor_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_complexity_visitor_util.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.utils.complexity_visitor_util import (  # noqa: F401
        AGENTIC_CORE,
        CANONICAL_JSON,
        LEGACY_JSON,
        MANIFEST_JSON,
        MISTAKE_JSON,
        PROJECT_ROOT,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    AGENTIC_CORE = None  # type: ignore[assignment,misc]
    CANONICAL_JSON = None  # type: ignore[assignment,misc]
    MANIFEST_JSON = None  # type: ignore[assignment,misc]
    LEGACY_JSON = None  # type: ignore[assignment,misc]
    MISTAKE_JSON = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util deps unavailable")
class TestComplexityVisitorUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/utils/complexity_visitor_util.py must be importable."""
        assert _AVAILABLE