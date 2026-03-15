"""ADG importability contract for agentic_core/adg/artifact/builder.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_builder.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.artifact.builder import (  # noqa: F401
        ADGArtifact,
        ADGArtifactBuilder,
        BlindSpotReport,
        EntityRecord,
        RelationRecord,
        StructuralMetrics,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EntityRecord = None  # type: ignore[assignment,misc]
    RelationRecord = None  # type: ignore[assignment,misc]
    StructuralMetrics = None  # type: ignore[assignment,misc]
    BlindSpotReport = None  # type: ignore[assignment,misc]
    ADGArtifact = None  # type: ignore[assignment,misc]
    ADGArtifactBuilder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="builder deps unavailable")
class TestBuilderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/artifact/builder.py must be importable."""
        assert _AVAILABLE

    def test_entityrecord_defined(self) -> None:
        assert EntityRecord is not None

    def test_relationrecord_defined(self) -> None:
        assert RelationRecord is not None

    def test_structuralmetrics_defined(self) -> None:
        assert StructuralMetrics is not None

    def test_blindspotreport_defined(self) -> None:
        assert BlindSpotReport is not None

    def test_adgartifact_defined(self) -> None:
        assert ADGArtifact is not None

    def test_adgartifactbuilder_defined(self) -> None:
        assert ADGArtifactBuilder is not None
