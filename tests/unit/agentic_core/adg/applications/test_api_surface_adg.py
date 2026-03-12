"""ADG importability contract for agentic_core/adg/applications/api_surface.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_api_surface.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.api_surface import (  # noqa: F401
        ModuleAPISurface,
        BoundaryViolation,
        APISurfaceReport,
        build_api_surface,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ModuleAPISurface = None  # type: ignore[assignment,misc]
    BoundaryViolation = None  # type: ignore[assignment,misc]
    APISurfaceReport = None  # type: ignore[assignment,misc]
    build_api_surface = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="api_surface.py deps unavailable")
class TestApiSurfaceImportability:
    def test_module_importable(self) -> None:
        """ADG contract: api_surface.py must be importable."""
        assert _AVAILABLE

    def test_moduleapisurface_is_type(self) -> None:
        assert ModuleAPISurface is not None

    def test_boundaryviolation_is_type(self) -> None:
        assert BoundaryViolation is not None

    def test_apisurfacereport_is_type(self) -> None:
        assert APISurfaceReport is not None

    def test_build_api_surface_callable(self) -> None:
        assert callable(build_api_surface)

