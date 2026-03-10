"""
Phase 6 — Wave 2 Tests: RetrievalBoundarySnapshot (deterministic, non-mutating).
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L4_state.types.retrieval_boundary_snapshot_types import (
    AnchorEntry,
    RetrievalBoundarySnapshot,
    build_request_hash,
    create_retrieval_boundary_snapshot,
)

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_CONFIG_HASHES = {
    "policy_hash": "aaa111",
    "routing_hash": "bbb222",
    "model_hash": "ccc333",
    "budget_hash": "ddd444",
}


def _make_anchors(*chunk_ids: str) -> list[AnchorEntry]:
    return [AnchorEntry(chunk_id=cid, version_hash=f"vh-{cid}") for cid in chunk_ids]


def _make_snapshot(**overrides) -> RetrievalBoundarySnapshot:
    defaults: dict = {
        "schema_version": 1,
        "mission_id": "mission-test",
        "request_hash": build_request_hash("query text", 5, AGENTIC_CORE_DIR),
        "active_config_hashes": dict(_CONFIG_HASHES),
        "anchors": _make_anchors("chunk-A", "chunk-B"),
        "created_at_utc": _TS,
    }
    defaults.update(overrides)
    return RetrievalBoundarySnapshot(**defaults)


class TestSnapshotHashStable:
    def test_snapshot_hash_stable(self):
        """Same inputs produce the same snapshot_hash on repeated construction."""
        s1 = _make_snapshot()
        s2 = _make_snapshot()
        assert s1.snapshot_hash == s2.snapshot_hash
        assert len(s1.snapshot_hash) == 64

    def test_hash_changes_with_mission_id(self):
        s1 = _make_snapshot(mission_id="mission-A")
        s2 = _make_snapshot(mission_id="mission-B")
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_hash_changes_with_request_hash(self):
        s1 = _make_snapshot(request_hash=build_request_hash("query-1", 5, "dom"))
        s2 = _make_snapshot(request_hash=build_request_hash("query-2", 5, "dom"))
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_hash_changes_with_config_hashes(self):
        s1 = _make_snapshot(active_config_hashes={"policy_hash": "aaa"})
        s2 = _make_snapshot(active_config_hashes={"policy_hash": "bbb"})
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_hash_changes_with_anchors(self):
        s1 = _make_snapshot(anchors=_make_anchors("chunk-X"))
        s2 = _make_snapshot(anchors=_make_anchors("chunk-Y"))
        assert s1.snapshot_hash != s2.snapshot_hash

    def test_snapshot_hash_excluded_from_canonical_bytes(self):
        s = _make_snapshot()
        assert b"snapshot_hash" not in s.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        s1 = _make_snapshot()
        s2 = _make_snapshot()
        assert s1.canonical_bytes() == s2.canonical_bytes()


class TestSnapshotCanonicalOrdering:
    def test_snapshot_canonical_ordering(self):
        """
        Anchors in canonical_bytes must be sorted by (chunk_id, version_hash)
        regardless of the order passed to the constructor.
        """
        anchors_unsorted = _make_anchors("chunk-Z", "chunk-A", "chunk-M")
        anchors_sorted = _make_anchors("chunk-A", "chunk-M", "chunk-Z")
        s1 = _make_snapshot(anchors=anchors_unsorted)
        s2 = _make_snapshot(anchors=anchors_sorted)
        assert s1.snapshot_hash == s2.snapshot_hash

    def test_anchors_stored_sorted(self):
        s = _make_snapshot(anchors=_make_anchors("chunk-Z", "chunk-A", "chunk-M"))
        chunk_ids = [a.chunk_id for a in s.anchors]
        assert chunk_ids == sorted(chunk_ids)

    def test_config_hashes_sorted_in_canonical_bytes(self):
        """active_config_hashes keys must be sorted in canonical_bytes."""
        s = _make_snapshot(
            active_config_hashes={
                "z_hash": "zzz",
                "a_hash": "aaa",
                "m_hash": "mmm",
            }
        )
        raw = s.canonical_bytes().decode()
        a_pos = raw.index("a_hash")
        m_pos = raw.index("m_hash")
        z_pos = raw.index("z_hash")
        assert a_pos < m_pos < z_pos

    def test_empty_anchors_allowed(self):
        s = _make_snapshot(anchors=[])
        assert s.anchors == []
        assert len(s.snapshot_hash) == 64


class TestSnapshotContainsConfigHashesAndAnchorIds:
    def test_snapshot_contains_config_hashes_and_anchor_ids(self):
        """
        Snapshot must carry all active_config_hashes keys and all anchor chunk_ids.
        """
        s = _make_snapshot(
            active_config_hashes=_CONFIG_HASHES,
            anchors=_make_anchors("chunk-A", "chunk-B"),
        )
        assert "policy_hash" in s.active_config_hashes
        assert "routing_hash" in s.active_config_hashes
        assert "model_hash" in s.active_config_hashes
        assert "budget_hash" in s.active_config_hashes
        chunk_ids = {a.chunk_id for a in s.anchors}
        assert "chunk-A" in chunk_ids
        assert "chunk-B" in chunk_ids

    def test_snapshot_config_hashes_values_preserved(self):
        s = _make_snapshot(active_config_hashes=_CONFIG_HASHES)
        assert s.active_config_hashes["policy_hash"] == "aaa111"
        assert s.active_config_hashes["routing_hash"] == "bbb222"

    def test_snapshot_anchor_version_hash_preserved(self):
        s = _make_snapshot(anchors=_make_anchors("chunk-A"))
        assert s.anchors[0].version_hash == "vh-chunk-A"


class TestSnapshotValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_snapshot(schema_version=99)

    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError, match="mission_id"):
            _make_snapshot(mission_id="")

    def test_empty_request_hash_raises(self):
        with pytest.raises(ValueError, match="request_hash"):
            _make_snapshot(request_hash="")

    def test_non_dict_config_hashes_raises(self):
        with pytest.raises(TypeError, match="active_config_hashes"):
            _make_snapshot(active_config_hashes="not-a-dict")  # type: ignore[arg-type]

    def test_non_list_anchors_raises(self):
        with pytest.raises(TypeError, match="anchors"):
            _make_snapshot(anchors="not-a-list")  # type: ignore[arg-type]


class TestBuildRequestHash:
    def test_request_hash_stable(self):
        h1 = build_request_hash("query", 5, "dom")
        h2 = build_request_hash("query", 5, "dom")
        assert h1 == h2
        assert len(h1) == 64

    def test_request_hash_differs_by_query(self):
        h1 = build_request_hash("query-A", 5, "dom")
        h2 = build_request_hash("query-B", 5, "dom")
        assert h1 != h2

    def test_request_hash_differs_by_top_k(self):
        h1 = build_request_hash("query", 5, "dom")
        h2 = build_request_hash("query", 10, "dom")
        assert h1 != h2

    def test_request_hash_differs_by_domain(self):
        h1 = build_request_hash("query", 5, "dom-A")
        h2 = build_request_hash("query", 5, "dom-B")
        assert h1 != h2


class TestCreateSnapshotFactory:
    def test_factory_produces_valid_snapshot(self):
        s = create_retrieval_boundary_snapshot(
            mission_id="m1",
            query="test query",
            top_k=3,
            domain=AGENTIC_CORE_DIR,
            active_config_hashes=_CONFIG_HASHES,
            anchors=_make_anchors("chunk-X"),
            created_at_utc=_TS,
        )
        assert isinstance(s, RetrievalBoundarySnapshot)
        assert len(s.snapshot_hash) == 64

    def test_factory_request_hash_matches_build_request_hash(self):
        s = create_retrieval_boundary_snapshot(
            mission_id="m1",
            query="test query",
            top_k=3,
            domain=AGENTIC_CORE_DIR,
            active_config_hashes=_CONFIG_HASHES,
            anchors=[],
            created_at_utc=_TS,
        )
        expected = build_request_hash("test query", 3, AGENTIC_CORE_DIR)
        assert s.request_hash == expected

    def test_to_dict_contains_all_fields(self):
        s = _make_snapshot()
        d = s.to_dict()
        assert "schema_version" in d
        assert "mission_id" in d
        assert "request_hash" in d
        assert "active_config_hashes" in d
        assert "anchors" in d
        assert "created_at_utc" in d
        assert "snapshot_hash" in d
