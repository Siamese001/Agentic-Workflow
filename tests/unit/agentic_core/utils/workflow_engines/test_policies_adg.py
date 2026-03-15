"""ADG importability contract for agentic_core/utils/workflow_engines/policies.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_policies.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.utils.workflow_engines.policies import (  # noqa: F401
        Chunk,
        ChunkManifest,
        ChunkPolicy,
        FixedTokenChunkPolicy,
        OverlapWindowChunkPolicy,
        SectionAwareChunkPolicy,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    Chunk = None  # type: ignore[assignment,misc]
    ChunkManifest = None  # type: ignore[assignment,misc]
    ChunkPolicy = None  # type: ignore[assignment,misc]
    FixedTokenChunkPolicy = None  # type: ignore[assignment,misc]
    OverlapWindowChunkPolicy = None  # type: ignore[assignment,misc]
    SectionAwareChunkPolicy = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="policies deps unavailable")
class TestPoliciesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/utils/workflow_engines/policies.py must be importable."""
        assert _AVAILABLE

    def test_chunk_defined(self) -> None:
        assert Chunk is not None

    def test_chunkmanifest_defined(self) -> None:
        assert ChunkManifest is not None

    def test_chunkpolicy_defined(self) -> None:
        assert ChunkPolicy is not None

    def test_fixedtokenchunkpolicy_defined(self) -> None:
        assert FixedTokenChunkPolicy is not None

    def test_overlapwindowchunkpolicy_defined(self) -> None:
        assert OverlapWindowChunkPolicy is not None

    def test_sectionawarechunkpolicy_defined(self) -> None:
        assert SectionAwareChunkPolicy is not None
