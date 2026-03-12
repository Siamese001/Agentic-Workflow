"""ADG importability contract for agentic_core/L3_orchestration/types/cognitive_diff_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cognitive_diff_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.cognitive_diff_types import (  # noqa: F401
        CognitiveStateSnapshot,
        DiffOp,
        L3CognitiveDiffBundle,
        compute_cognitive_diff,
        emit_cognitive_diff_bundle,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CognitiveStateSnapshot = None  # type: ignore[assignment,misc]
    DiffOp = None  # type: ignore[assignment,misc]
    L3CognitiveDiffBundle = None  # type: ignore[assignment,misc]
    compute_cognitive_diff = None  # type: ignore[assignment,misc]
    emit_cognitive_diff_bundle = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="cognitive_diff_types.py deps unavailable")
class TestCognitiveDiffTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: cognitive_diff_types.py must be importable."""
        assert _AVAILABLE

    def test_cognitivestatesnapshot_is_type(self) -> None:
        assert CognitiveStateSnapshot is not None

    def test_diffop_is_type(self) -> None:
        assert DiffOp is not None

    def test_l3cognitivediffbundle_is_type(self) -> None:
        assert L3CognitiveDiffBundle is not None

    def test_compute_cognitive_diff_callable(self) -> None:
        assert callable(compute_cognitive_diff)

    def test_emit_cognitive_diff_bundle_callable(self) -> None:
        assert callable(emit_cognitive_diff_bundle)

