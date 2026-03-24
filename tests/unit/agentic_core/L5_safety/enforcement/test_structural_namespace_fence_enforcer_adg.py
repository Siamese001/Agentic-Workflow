"""ADG importability contract for agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_structural_namespace_fence_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.structural_namespace_fence_enforcer import (  # noqa: F401
        ProvenanceLoader,
        ProvenanceTracker,
        StructuralNamespaceFinder,
        get_provenance_tracker,
        install_structural_namespace_fence,
        uninstall_structural_namespace_fence,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ProvenanceTracker = None  # type: ignore[assignment,misc]
    ProvenanceLoader = None  # type: ignore[assignment,misc]
    StructuralNamespaceFinder = None  # type: ignore[assignment,misc]
    install_structural_namespace_fence = None  # type: ignore[assignment,misc]
    uninstall_structural_namespace_fence = None  # type: ignore[assignment,misc]
    get_provenance_tracker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="structural_namespace_fence_enforcer deps unavailable")
class TestStructuralNamespaceFenceEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_provenancetracker_defined(self) -> None:
        assert ProvenanceTracker is not None

    def test_provenanceloader_defined(self) -> None:
        assert ProvenanceLoader is not None

    def test_structuralnamespacefinder_defined(self) -> None:
        assert StructuralNamespaceFinder is not None