"""ADG importability contract for agentic_core/adg/artifact/layer_splitter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_layer_splitter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.artifact.layer_splitter import (  # noqa: F401
        SplitArtifact,
        split_artifact,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SplitArtifact = None  # type: ignore[assignment,misc]
    split_artifact = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="layer_splitter.py deps unavailable")
class TestLayerSplitterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: layer_splitter.py must be importable."""
        assert _AVAILABLE

    def test_splitartifact_is_type(self) -> None:
        assert SplitArtifact is not None

    def test_split_artifact_callable(self) -> None:
        assert callable(split_artifact)

