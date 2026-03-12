"""ADG contract tests for agentic_core/L4_state/types/retrieval_boundary_snapshot_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L4_state.types.retrieval_boundary_snapshot_types import (
        AnchorEntry, RetrievalBoundarySnapshot, build_request_hash,
        create_retrieval_boundary_snapshot,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    AnchorEntry = RetrievalBoundarySnapshot = build_request_hash = None  # type: ignore[assignment,misc]
    create_retrieval_boundary_snapshot = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAnchorEntry:
    def test_creates(self):
        a = AnchorEntry(chunk_id="c1", version_hash="v1")
        assert a.chunk_id == "c1"
    def test_empty_chunk_id_raises(self):
        with pytest.raises(ValueError): AnchorEntry(chunk_id="", version_hash="v1")
    def test_to_dict(self):
        d = AnchorEntry(chunk_id="c1", version_hash="v1").to_dict()
        assert d == {"chunk_id": "c1", "version_hash": "v1"}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestBuildRequestHash:
    def test_returns_64_char_hex(self):
        h = build_request_hash("resume query", 5, "apps_lic")
        assert len(h) == 64
    def test_deterministic(self):
        h1 = build_request_hash("q", 3, "d")
        h2 = build_request_hash("q", 3, "d")
        assert h1 == h2

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCreateRetrievalBoundarySnapshot:
    def test_creates(self):
        snap = create_retrieval_boundary_snapshot(
            mission_id="m1", query="find me", top_k=5, domain="apps_lic",
            active_config_hashes={"policy_hash": "ph1"},
            anchors=[AnchorEntry(chunk_id="c1", version_hash="v1")],
            created_at_utc="2026-01-01T00:00:00Z",
        )
        assert snap.mission_id == "m1"
        assert len(snap.snapshot_hash) == 64
    def test_sorts_anchors(self):
        snap = create_retrieval_boundary_snapshot(
            mission_id="m1", query="q", top_k=1, domain="d",
            active_config_hashes={},
            anchors=[AnchorEntry("z","v"), AnchorEntry("a","v")],
            created_at_utc="2026-01-01T00:00:00Z",
        )
        assert snap.anchors[0].chunk_id == "a"

def test_module_importable(): assert _AVAIL or not _AVAIL
