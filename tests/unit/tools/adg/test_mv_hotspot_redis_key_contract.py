"""W3 proof: mv_hotspot_centrality Redis key contract aligns writer ↔ reader (mock-only).

No ``redis-server`` required; verifies shared prefix, hotspot key equality, ``ZREVRANGE`` wiring.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tools.adg.mv_reader import CACHE_VERSION as READER_CV, MVRedisReader, _redis_key as reader_redis_key
import tools.adg.adg_redis_ingest as adg_redis_ingest
import tools.adg.mv_projection as mv_projection
from tools.adg.mv_projection import MV_SPECS


def test_cache_version_v1_aligned_across_adg_packages() -> None:
    """All Redis key prefixes for ADG overlays use the same CACHE_VERSION literal."""
    assert READER_CV == mv_projection.CACHE_VERSION == adg_redis_ingest.CACHE_VERSION == "v1"


def test_hotspot_zset_key_reader_equals_mv_projection_writer() -> None:
    snap = "05162026_0649"
    fragment = "mv:mv_hotspot_centrality"
    assert reader_redis_key(snap, fragment) == mv_projection._redis_key(snap, fragment)


def test_hotspot_zset_literal_matches_expected_pattern() -> None:
    snap = "01011999_0000"
    assert reader_redis_key(snap, "mv:mv_hotspot_centrality") == f"adg:v1:{snap}:mv:mv_hotspot_centrality"


def test_mv_projection_hotspot_spec_matches_service_mv_reader_name() -> None:
    spec = next(s for s in MV_SPECS if s.table == "mv_hotspot_centrality")
    assert spec.member_col == "node_id"
    assert spec.score_expr == "degree_centrality"
    # ADGService.get_mv_hotspot_centrality passes mv_name == spec.table
    svc_mv_name = "mv_hotspot_centrality"
    assert svc_mv_name == spec.table


def test_mv_reader_get_mv_top_wire_zrevrange_with_snapshot_limit() -> None:
    client = MagicMock()
    client.zrevrange.return_value = [("42", "0.9")]
    reader = MVRedisReader(client=client)
    pairs = reader.get_mv_top("mv_hotspot_centrality", "SNAP_ABC", k=17)

    expected_key = reader_redis_key("SNAP_ABC", "mv:mv_hotspot_centrality")
    client.zrevrange.assert_called_once_with(expected_key, 0, 16, withscores=True)
    assert pairs == [("42", 0.9)]


def test_mv_reader_empty_zrange_returns_empty_list() -> None:
    """Compatibility with W2.1 cold-path: caller treats ``[]`` as SQLite fallback."""
    client = MagicMock()
    client.zrevrange.return_value = []
    reader = MVRedisReader(client=client)
    assert reader.get_mv_top("mv_hotspot_centrality", "S", k=99) == []


def test_mv_reader_zrevrange_error_returns_none_not_raise() -> None:
    client = MagicMock()
    client.zrevrange.side_effect = OSError("transport")
    reader = MVRedisReader(client=client)
    assert reader.get_mv_top("mv_hotspot_centrality", "S", k=10) is None


def test_projection_redis_key_fn_matches_reader_for_mv_meta_suffix() -> None:
    snap = "X"
    assert mv_projection._redis_key(snap, "mv:T:meta") == reader_redis_key(snap, "mv:T:meta")
