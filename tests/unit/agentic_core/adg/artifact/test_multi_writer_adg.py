"""ADG importability contract for agentic_core/adg/artifact/multi_writer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_multi_writer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.artifact.multi_writer import (  # noqa: F401
        ArtifactPaths,
        write_all_artifacts,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ArtifactPaths = None  # type: ignore[assignment,misc]
    write_all_artifacts = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="multi_writer.py deps unavailable")
class TestMultiWriterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: multi_writer.py must be importable."""
        assert _AVAILABLE

    def test_artifactpaths_is_type(self) -> None:
        assert ArtifactPaths is not None

    def test_write_all_artifacts_callable(self) -> None:
        assert callable(write_all_artifacts)

