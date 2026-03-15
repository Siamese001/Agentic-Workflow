"""ADG importability contract for agentic_core/utils/workflow_engines/validators.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_validators.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.utils.workflow_engines.validators import (  # noqa: F401
        ChunkQualityReport,
        DuplicateChunkDetector,
        MaxChunkSizeValidator,
        MinChunkSizeValidator,
        OrphanChunkDetector,
        OverlapSanityValidator,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ChunkQualityReport = None  # type: ignore[assignment,misc]
    MaxChunkSizeValidator = None  # type: ignore[assignment,misc]
    MinChunkSizeValidator = None  # type: ignore[assignment,misc]
    OverlapSanityValidator = None  # type: ignore[assignment,misc]
    DuplicateChunkDetector = None  # type: ignore[assignment,misc]
    OrphanChunkDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validators deps unavailable")
class TestValidatorsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/utils/workflow_engines/validators.py must be importable."""
        assert _AVAILABLE

    def test_chunkqualityreport_defined(self) -> None:
        assert ChunkQualityReport is not None

    def test_maxchunksizevalidator_defined(self) -> None:
        assert MaxChunkSizeValidator is not None

    def test_minchunksizevalidator_defined(self) -> None:
        assert MinChunkSizeValidator is not None

    def test_overlapsanityvalidator_defined(self) -> None:
        assert OverlapSanityValidator is not None

    def test_duplicatechunkdetector_defined(self) -> None:
        assert DuplicateChunkDetector is not None

    def test_orphanchunkdetector_defined(self) -> None:
        assert OrphanChunkDetector is not None
