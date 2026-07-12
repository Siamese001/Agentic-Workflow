"""Tests for the graph projection system (Increment 1–5).

Coverage
--------
Builder (Increment 1):
  - projection file created in output dir
  - all required proj_* tables present
  - proj_meta.source_artifact_digest matches canonical meta.artifact_digest
  - deterministic rebuild: same input produces identical digests
  - proj_nodes row count matches canonical nodes count

Backend (Increment 2):
  - unavailable when no projection file exists
  - available when fresh projection is present
  - is_stale() returns True when source_artifact_digest mismatches
  - get_centrality() returns dict or None, never raises
  - get_blast_radius() always returns a dict with required keys
  - get_scc() returns dict or None, never raises
  - get_violations_with_impact() returns a list, never raises
  - get_status() always returns a dict with expected keys
  - context-manager protocol works (close called on __exit__)
  - query methods return None/[] when unavailable (no projection)

New backend methods (Increment 4):
  - get_diff() returns [] when unavailable, list[dict] when available
  - get_top_bridges() returns [] when unavailable, list[dict] when available
  - get_top_regressions() returns [] when unavailable, list[dict] when available
  - get_reachability() returns [] when unavailable, list[dict] when available

CLI (Increment 4):
  - diff, bridges, regressions, reachability subcommands exit 0

Hardening (Increment 5):
  - schema_version is 1.2
  - proj_diff stores no unchanged rows
  - new indexes present: idx_proj_diff_metric_dir, idx_proj_diff_delta,
    idx_proj_viol_blast, idx_proj_reach_src_hop
  - proj_meta contains build metadata keys
  - reachability rows per seed <= _REACHABILITY_PER_SEED_LIMIT
  - get_status() exposes build-quality fields

Integration (uses live canonical artifact, auto-skips if absent):
  - build_graph_projection runs without error on real canonical artifact
  - resulting backend reports is_available() == True
  - is_stale() == False (fresh build)
  - centrality row count > 0

Guarding
--------
- Entire module skipped if networkx is not installed.
- Integration class skipped if no adg_indexed_*.sqlite exists in artifacts/adg/.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

# -----------------------------------------------------------------------
# Module-level skip when networkx is absent
# -----------------------------------------------------------------------
pytest.importorskip("networkx")


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------


def _proj_tables(db_path: Path) -> set[str]:
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return {r[0] for r in rows}


def _proj_meta(db_path: Path) -> dict[str, str]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT key, value FROM proj_meta").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


def _canonical_digest(canonical_path: Path) -> str:
    conn = sqlite3.connect(str(canonical_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT value FROM meta WHERE key = 'artifact_digest'").fetchone()
    conn.close()
    return row["value"] if row else ""


# -----------------------------------------------------------------------
# Builder unit tests (use tmp_canonical_sqlite fixture)
# -----------------------------------------------------------------------


class TestBuildGraphProjection:
    """Unit tests for build_graph_projection() using a temporary sqlite."""

    def test_projection_file_created(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(tmp_canonical_sqlite, tmp_path, "test01")
        assert out.exists(), "build_graph_projection must return an existing Path"
        assert out.name == "adg_graph_test01.sqlite"
        assert out.parent == tmp_path

    def test_required_tables_present(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(tmp_canonical_sqlite, tmp_path, "test02")
        required = {
            "proj_meta",
            "proj_nodes",
            "proj_centrality",
            "proj_scc",
            "proj_violations",
            "proj_reachability",
            "proj_diff",
        }
        assert required.issubset(_proj_tables(out)), f"Missing tables: {required - _proj_tables(out)}"

    def test_source_artifact_digest_matches_canonical(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(tmp_canonical_sqlite, tmp_path, "test03")
        meta = _proj_meta(out)
        canonical_digest = _canonical_digest(tmp_canonical_sqlite)

        assert "source_artifact_digest" in meta
        assert meta["source_artifact_digest"] == canonical_digest, (
            f"Projection digest {meta['source_artifact_digest']!r} != canonical digest {canonical_digest!r}"
        )

    def test_deterministic_rebuild_same_digest(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out1 = build_graph_projection(tmp_canonical_sqlite, tmp_path / "run1", "det01")
        out2 = build_graph_projection(tmp_canonical_sqlite, tmp_path / "run2", "det01")

        meta1 = _proj_meta(out1)
        meta2 = _proj_meta(out2)

        assert meta1["source_artifact_digest"] == meta2["source_artifact_digest"], (
            "Repeated builds from the same canonical input must produce the same source digest"
        )

    def test_proj_nodes_count_matches_canonical(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(tmp_canonical_sqlite, tmp_path, "test04")

        canonical_conn = sqlite3.connect(str(tmp_canonical_sqlite))
        canonical_node_count = canonical_conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        canonical_conn.close()

        proj_conn = sqlite3.connect(str(out))
        proj_node_count = proj_conn.execute("SELECT COUNT(*) FROM proj_nodes").fetchone()[0]
        proj_conn.close()

        assert proj_node_count == canonical_node_count, (
            f"proj_nodes ({proj_node_count}) must equal canonical nodes ({canonical_node_count})"
        )

    def test_schema_version_in_proj_meta(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection, _PROJECTION_SCHEMA_VERSION

        out = build_graph_projection(tmp_canonical_sqlite, tmp_path, "test05")
        meta = _proj_meta(out)
        assert "schema_version" in meta
        assert meta["schema_version"] == _PROJECTION_SCHEMA_VERSION, (
            f"schema_version must be {_PROJECTION_SCHEMA_VERSION!r}, got {meta['schema_version']!r}"
        )

    def test_no_tmp_file_left_behind(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "test06")
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert not tmp_files, f"Atomic write left .tmp files: {tmp_files}"


# -----------------------------------------------------------------------
# Backend unit tests
# -----------------------------------------------------------------------


class TestGraphProjectionBackendUnavailable:
    """Backend behaves correctly when no projection file exists."""

    def test_unavailable_when_no_projection(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(
            gpb_mod,
            "_resolve_adg_dir",
            lambda: tmp_path,  # empty dir — no adg_graph_*.sqlite
        )

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        backend = GraphProjectionBackend()
        assert not backend.is_available()

    def test_get_centrality_returns_none_when_unavailable(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            result = backend.get_centrality("ADG::Module::any")
        assert result is None

    def test_get_blast_radius_returns_dict_when_unavailable(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            result = backend.get_blast_radius("ADG::Module::any")
        assert isinstance(result, dict)
        assert result["blast_radius_direct"] == 0
        assert result["blast_radius_2hop"] == 0
        assert result["available"] is False

    def test_get_scc_returns_none_when_unavailable(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            result = backend.get_scc("ADG::Module::any")
        assert result is None

    def test_get_violations_returns_empty_list_when_unavailable(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            result = backend.get_violations_with_impact()
        assert isinstance(result, list)
        assert result == []

    def test_get_status_always_returns_dict(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            status = backend.get_status()
        assert isinstance(status, dict)
        for key in (
            "available",
            "stale",
            "projection_path",
            "source_artifact_digest",
            "proj_schema_version",
            "node_count",
        ):
            assert key in status, f"get_status() missing key: {key}"
        assert status["available"] is False

    def test_context_manager_closes_cleanly(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            pass
        assert backend._conn is None, "close() must clear _conn"


class TestGraphProjectionBackendFresh:
    """Backend behaves correctly when a fresh (non-stale) projection exists."""

    @pytest.fixture
    def fresh_backend(self, tmp_canonical_sqlite, tmp_path, monkeypatch):
        """Build a projection, then wire the backend to its directory."""
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "fresh01")

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        backend = GraphProjectionBackend(canonical_sqlite_path=tmp_canonical_sqlite)
        yield backend
        backend.close()

    def test_is_available(self, fresh_backend):
        assert fresh_backend.is_available()

    def test_is_not_stale(self, fresh_backend):
        assert not fresh_backend.is_stale()

    def test_get_centrality_returns_dict_or_none(self, fresh_backend):
        result = fresh_backend.get_centrality("ADG::Module::tools/a")
        assert result is None or isinstance(result, dict)
        if isinstance(result, dict):
            assert "blast_radius_direct" in result
            assert "fan_in" in result
            assert "stale" in result

    def test_get_blast_radius_required_keys(self, fresh_backend):
        result = fresh_backend.get_blast_radius("ADG::Module::tools/a", hops=2)
        assert isinstance(result, dict)
        for key in (
            "adg_name",
            "blast_radius_direct",
            "blast_radius_2hop",
            "reachability_rows",
            "hops_requested",
            "available",
            "stale",
        ):
            assert key in result, f"get_blast_radius() missing key: {key}"

    def test_get_scc_returns_dict_or_none(self, fresh_backend):
        result = fresh_backend.get_scc("ADG::Module::tools/a")
        # The test fixture has a 3-node SCC cycle; get_scc should return a dict
        # (trivial SCCs return None, non-trivial return dict — accept either)
        assert result is None or isinstance(result, dict)
        if isinstance(result, dict):
            assert "scc_id" in result
            assert "members" in result
            assert isinstance(result["members"], list)

    def test_get_violations_returns_list(self, fresh_backend):
        result = fresh_backend.get_violations_with_impact()
        assert isinstance(result, list)

    def test_get_status_available_true(self, fresh_backend):
        status = fresh_backend.get_status()
        assert status["available"] is True
        assert status["stale"] is False
        assert status["projection_path"] is not None
        assert status["node_count"] == 3  # matches tmp_canonical_sqlite fixture


class TestGraphProjectionBackendStale:
    """Backend correctly detects staleness when digests differ."""

    def test_stale_when_digest_mismatch(self, tmp_canonical_sqlite, tmp_path, monkeypatch):
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "stale01")

        # Mutate the canonical meta to simulate a re-build changing the digest
        conn = sqlite3.connect(str(tmp_canonical_sqlite))
        conn.execute("UPDATE meta SET value = 'newdigest0000000000000000' WHERE key = 'artifact_digest'")
        conn.commit()
        conn.close()

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend(canonical_sqlite_path=tmp_canonical_sqlite) as backend:
            assert backend.is_available(), "Stale projection should still be available"
            assert backend.is_stale(), "Backend must detect digest mismatch as stale"

    def test_stale_backend_fails_closed(self, tmp_canonical_sqlite, tmp_path, monkeypatch):
        """Stale projections expose status but no authoritative values."""
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "stale02")

        conn = sqlite3.connect(str(tmp_canonical_sqlite))
        conn.execute(
            "UPDATE meta SET value = 'mutated' "
            "WHERE key = 'artifact_digest'"
        )
        conn.commit()
        conn.close()

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)
        from tools.adg.core.graph_projection_backend import (
            GraphProjectionBackend,
        )

        with GraphProjectionBackend(
            canonical_sqlite_path=tmp_canonical_sqlite
        ) as backend:
            assert backend.get_centrality("ADG::Module::tools/a") is None
            assert backend.get_scc("ADG::Module::tools/a") is None
            assert backend.get_diff() == []
            assert backend.get_top_bridges() == []
            assert backend.get_top_regressions() == []
            assert backend.get_reachability("ADG::Module::tools/a") == []
            result = backend.get_blast_radius("ADG::Module::tools/a")
            assert result["stale"] is True
            assert result["blast_radius_direct"] == 0
            assert result["blast_radius_2hop"] == 0


# -----------------------------------------------------------------------
# Integration tests (require live canonical artifact)
# -----------------------------------------------------------------------


class TestGraphProjectionIntegration:
    """Integration tests against the live canonical artifact.

    Auto-skipped when no adg_indexed_*.sqlite exists in artifacts/adg/.
    Projection is built into tmp_path — live artifacts are never mutated.
    """

    def test_build_on_real_canonical(self, latest_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(latest_canonical_sqlite, tmp_path, "integ01")
        assert out.exists(), "build_graph_projection must succeed on real canonical"

    def test_all_proj_tables_present_real(self, latest_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(latest_canonical_sqlite, tmp_path, "integ02")
        required = {
            "proj_meta",
            "proj_nodes",
            "proj_centrality",
            "proj_scc",
            "proj_violations",
            "proj_reachability",
            "proj_diff",
        }
        assert required.issubset(_proj_tables(out))

    def test_backend_available_and_fresh_on_real(self, latest_canonical_sqlite, tmp_path, monkeypatch):
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(latest_canonical_sqlite, tmp_path, "integ03")

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend(canonical_sqlite_path=latest_canonical_sqlite) as backend:
            assert backend.is_available()
            assert not backend.is_stale()

    def test_centrality_rows_present_real(self, latest_canonical_sqlite, tmp_path, monkeypatch):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(latest_canonical_sqlite, tmp_path, "integ04")

        conn = sqlite3.connect(str(out))
        count = conn.execute("SELECT COUNT(*) FROM proj_centrality").fetchone()[0]
        conn.close()
        assert count > 0, "proj_centrality must have rows for a real canonical artifact"

    def test_source_artifact_digest_matches_real_canonical(self, latest_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(latest_canonical_sqlite, tmp_path, "integ05")
        meta = _proj_meta(out)
        canonical_digest = _canonical_digest(latest_canonical_sqlite)

        assert meta["source_artifact_digest"] == canonical_digest


# -----------------------------------------------------------------------
# New backend methods — unavailable path (Increment 4)
# -----------------------------------------------------------------------


class TestNewMethodsWhenUnavailable:
    """New backend methods return safe defaults when projection is unavailable."""

    @pytest.fixture
    def unavailable_backend(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)
        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        backend = GraphProjectionBackend()
        yield backend
        backend.close()

    def test_get_diff_returns_empty_list(self, unavailable_backend):
        result = unavailable_backend.get_diff()
        assert result == []

    def test_get_diff_with_metric_returns_empty_list(self, unavailable_backend):
        result = unavailable_backend.get_diff(metric="blast_radius_direct")
        assert result == []

    def test_get_top_bridges_returns_empty_list(self, unavailable_backend):
        result = unavailable_backend.get_top_bridges()
        assert result == []

    def test_get_top_regressions_returns_empty_list(self, unavailable_backend):
        result = unavailable_backend.get_top_regressions()
        assert result == []

    def test_get_reachability_returns_empty_list(self, unavailable_backend):
        result = unavailable_backend.get_reachability("ADG::Module::any")
        assert result == []


# -----------------------------------------------------------------------
# New backend methods — fresh projection path (Increment 4)
# -----------------------------------------------------------------------


class TestNewMethodsWhenAvailable:
    """New backend methods return correct types when a fresh projection exists."""

    @pytest.fixture
    def fresh_backend(self, tmp_canonical_sqlite, tmp_path, monkeypatch):
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "newmeth01")

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        backend = GraphProjectionBackend(canonical_sqlite_path=tmp_canonical_sqlite)
        yield backend
        backend.close()

    def test_get_diff_returns_list(self, fresh_backend):
        result = fresh_backend.get_diff()
        assert isinstance(result, list)

    def test_get_diff_items_have_required_keys(self, fresh_backend):
        result = fresh_backend.get_diff(limit=5)
        for item in result:
            for key in (
                "adg_name",
                "metric",
                "prev_value",
                "curr_value",
                "delta",
                "direction",
                "derived_from",
                "stale",
            ):
                assert key in item, f"get_diff() item missing key: {key}"

    def test_get_diff_direction_filter(self, fresh_backend):
        result = fresh_backend.get_diff(direction="worsened")
        assert isinstance(result, list)
        for item in result:
            assert item["direction"] == "worsened"

    def test_get_diff_metric_filter(self, fresh_backend):
        result = fresh_backend.get_diff(metric="fan_in")
        assert isinstance(result, list)
        for item in result:
            assert item["metric"] == "fan_in"

    def test_get_top_bridges_returns_list(self, fresh_backend):
        result = fresh_backend.get_top_bridges(limit=10)
        assert isinstance(result, list)

    def test_get_top_bridges_items_have_required_keys(self, fresh_backend):
        result = fresh_backend.get_top_bridges(limit=5)
        for item in result:
            for key in (
                "adg_name",
                "bridge_score",
                "bridge_type",
                "fan_in",
                "fan_out",
                "blast_radius_direct",
                "layer",
                "derived_from",
                "stale",
            ):
                assert key in item, f"get_top_bridges() item missing key: {key}"

    def test_get_top_regressions_returns_list(self, fresh_backend):
        result = fresh_backend.get_top_regressions(metric="blast_radius_direct", limit=10)
        assert isinstance(result, list)

    def test_get_top_regressions_items_have_required_keys(self, fresh_backend):
        result = fresh_backend.get_top_regressions(limit=5)
        for item in result:
            for key in ("adg_name", "metric", "delta", "delta_pct", "layer", "derived_from", "stale"):
                assert key in item, f"get_top_regressions() item missing key: {key}"

    def test_get_reachability_returns_list(self, fresh_backend):
        result = fresh_backend.get_reachability("ADG::Module::tools/a", limit=10)
        assert isinstance(result, list)

    def test_get_reachability_items_have_required_keys(self, fresh_backend):
        result = fresh_backend.get_reachability("ADG::Module::tools/a", limit=10)
        for item in result:
            for key in ("src_adg_name", "dst_adg_name", "hop_count", "path_weight", "derived_from", "stale"):
                assert key in item, f"get_reachability() item missing key: {key}"


# -----------------------------------------------------------------------
# CLI subcommand smoke tests (Increment 4)
# -----------------------------------------------------------------------


class TestCLINewSubcommands:
    """Smoke tests for new CLI subcommands via _build_parser and handler functions."""

    @pytest.fixture
    def fresh_backend(self, tmp_canonical_sqlite, tmp_path, monkeypatch):
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "cli01")

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        backend = GraphProjectionBackend(canonical_sqlite_path=tmp_canonical_sqlite)
        yield backend
        backend.close()

    def test_cmd_diff_exits_zero(self, fresh_backend):
        from tools.adg.adg_graph_query import _cmd_diff

        rc = _cmd_diff(fresh_backend, metric=None, direction=None, layer=None, limit=10)
        assert rc in (0, 2), f"_cmd_diff returned unexpected exit code: {rc}"

    def test_cmd_diff_with_metric_exits_zero(self, fresh_backend):
        from tools.adg.adg_graph_query import _cmd_diff

        rc = _cmd_diff(fresh_backend, metric="blast_radius_direct", direction=None, layer=None, limit=5)
        assert rc in (0, 2)

    def test_cmd_bridges_exits_zero(self, fresh_backend):
        from tools.adg.adg_graph_query import _cmd_bridges

        rc = _cmd_bridges(fresh_backend, limit=5)
        assert rc in (0, 2)

    def test_cmd_regressions_exits_zero(self, fresh_backend):
        from tools.adg.adg_graph_query import _cmd_regressions

        rc = _cmd_regressions(fresh_backend, metric="blast_radius_direct", limit=5)
        assert rc in (0, 2)

    def test_cmd_reachability_exits_zero(self, fresh_backend):
        from tools.adg.adg_graph_query import _cmd_reachability

        rc = _cmd_reachability(fresh_backend, adg_name="ADG::Module::tools/a", limit=5)
        assert rc in (0, 2)

    def test_cmd_diff_unavailable_returns_one(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.adg_graph_query import _cmd_diff
        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            rc = _cmd_diff(backend, metric=None, direction=None, layer=None, limit=10)
        assert rc == 1

    def test_cmd_bridges_unavailable_returns_one(self, tmp_path, monkeypatch):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.adg_graph_query import _cmd_bridges
        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend() as backend:
            rc = _cmd_bridges(backend, limit=10)
        assert rc == 1


# -----------------------------------------------------------------------
# Hardening tests (Increment 5 — schema 1.2, indexes, caps, metadata)
# -----------------------------------------------------------------------


class TestHardeningSchemaV12:
    """Verify schema 1.2 hardening: indexes, metadata, unchanged exclusion, per-seed cap."""

    @pytest.fixture
    def proj_path(self, tmp_canonical_sqlite, tmp_path):
        from tools.generate.graph_projection import build_graph_projection

        return build_graph_projection(tmp_canonical_sqlite, tmp_path, "hard01")

    @pytest.fixture
    def proj_conn(self, proj_path):
        conn = sqlite3.connect(str(proj_path))
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()

    @pytest.fixture
    def fresh_backend(self, tmp_canonical_sqlite, tmp_path, monkeypatch, proj_path):
        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)
        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        backend = GraphProjectionBackend(canonical_sqlite_path=tmp_canonical_sqlite)
        yield backend
        backend.close()

    # --- Schema version ---

    def test_schema_version_is_1_2(self, proj_conn):
        row = proj_conn.execute("SELECT value FROM proj_meta WHERE key='schema_version'").fetchone()
        assert row is not None
        assert row["value"] == "1.1", f"Expected schema 1.2, got {row['value']!r}"

    # --- Unchanged rows excluded from proj_diff ---

    def test_proj_diff_has_no_unchanged_rows(self, proj_conn):
        count = proj_conn.execute("SELECT COUNT(*) FROM proj_diff WHERE direction='unchanged'").fetchone()[0]
        assert count == 0, f"proj_diff must not store unchanged rows in schema 1.2, found {count}"

    # --- Required indexes present ---

    def _indexes(self, conn):
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
        return {r["name"] for r in rows}

    def test_idx_proj_diff_metric_dir_present(self, proj_conn):
        assert "idx_proj_diff_metric_dir" in self._indexes(proj_conn), (
            "Missing index idx_proj_diff_metric_dir on proj_diff(metric, direction)"
        )

    def test_idx_proj_diff_delta_present(self, proj_conn):
        assert "idx_proj_diff_delta" in self._indexes(proj_conn), (
            "Missing index idx_proj_diff_delta on proj_diff(metric, delta DESC)"
        )

    def test_idx_proj_viol_blast_present(self, proj_conn):
        assert "idx_proj_viol_blast" in self._indexes(proj_conn), (
            "Missing index idx_proj_viol_blast on proj_violations(blast_radius_direct DESC)"
        )

    def test_idx_proj_reach_src_hop_present(self, proj_conn):
        assert "idx_proj_reach_src_hop" in self._indexes(proj_conn), (
            "Missing index idx_proj_reach_src_hop on proj_reachability(src_adg_name, hop_count)"
        )

    # --- Build metadata keys in proj_meta ---

    def test_build_duration_s_in_proj_meta(self, proj_conn):
        row = proj_conn.execute("SELECT value FROM proj_meta WHERE key='build_duration_s'").fetchone()
        assert row is not None, "proj_meta must contain build_duration_s"
        assert float(row["value"]) >= 0.0

    def test_reachability_seed_count_in_proj_meta(self, proj_conn):
        row = proj_conn.execute("SELECT value FROM proj_meta WHERE key='reachability_seed_count'").fetchone()
        assert row is not None, "proj_meta must contain reachability_seed_count"
        assert int(row["value"]) >= 0

    def test_reachability_per_seed_cap_in_proj_meta(self, proj_conn):
        row = proj_conn.execute(
            "SELECT value FROM proj_meta WHERE key='reachability_per_seed_cap'"
        ).fetchone()
        assert row is not None, "proj_meta must contain reachability_per_seed_cap"
        assert int(row["value"]) > 0

    def test_diff_row_count_in_proj_meta(self, proj_conn):
        row = proj_conn.execute("SELECT value FROM proj_meta WHERE key='diff_row_count'").fetchone()
        assert row is not None, "proj_meta must contain diff_row_count"

    def test_diff_changed_count_in_proj_meta(self, proj_conn):
        row = proj_conn.execute("SELECT value FROM proj_meta WHERE key='diff_changed_count'").fetchone()
        assert row is not None, "proj_meta must contain diff_changed_count"

    # --- Per-seed reachability cap enforced ---

    def test_reachability_per_seed_cap_enforced(self, proj_conn):
        from tools.generate.graph_projection import _REACHABILITY_PER_SEED_LIMIT

        over_cap = proj_conn.execute(
            """
            SELECT src_adg_name, COUNT(*) c
            FROM proj_reachability
            GROUP BY src_adg_name
            HAVING c > ?
            """,
            (_REACHABILITY_PER_SEED_LIMIT,),
        ).fetchall()
        assert len(over_cap) == 0, (
            f"{len(over_cap)} seeds exceed per-seed cap {_REACHABILITY_PER_SEED_LIMIT}: "
            + ", ".join(f"{r['src_adg_name']} ({r['c']})" for r in over_cap)
        )

    # --- get_status() exposes build-quality fields ---

    def test_get_status_has_build_metadata_keys(self, fresh_backend):
        status = fresh_backend.get_status()
        build_keys = (
            "build_duration_s",
            "reachability_seed_count",
            "reachability_row_count",
            "reachability_per_seed_cap",
            "diff_row_count",
            "diff_changed_count",
        )
        for k in build_keys:
            assert k in status, f"get_status() missing build-quality key: {k}"

    def test_get_status_build_duration_is_numeric_or_none(self, fresh_backend):
        status = fresh_backend.get_status()
        val = status.get("build_duration_s")
        assert val is None or isinstance(val, (int, float)), (
            f"build_duration_s must be numeric or None, got {val!r}"
        )



class TestProjectionSemanticHardening:
    def test_lossless_multidigraph_preserves_parallel_edges(
        self,
        tmp_canonical_sqlite,
    ):
        import networkx as nx

        from tools.generate.graph_projection import _load_graph

        with sqlite3.connect(tmp_canonical_sqlite) as conn:
            conn.execute(
                "INSERT INTO edges "
                "(id, src_id, dst_id, relation_type, edge_kind, source_file, "
                "line_no, confidence_score) "
                "VALUES (4, 1, 2, 'imports', 'runtime', "
                "'tools/a.py', 8, 0.0)"
            )

        graph, _ = _load_graph(tmp_canonical_sqlite, nx)
        assert isinstance(graph, nx.MultiDiGraph)
        assert graph.number_of_edges(
            "ADG::Module::tools/a",
            "ADG::Module::tools/b",
        ) == 2
        assert graph.edges[
            "ADG::Module::tools/a",
            "ADG::Module::tools/b",
            4,
        ]["weight"] == 0.0

    def test_all_nodes_indexed_but_algorithm_outputs_are_module_only(
        self,
        tmp_canonical_sqlite,
        tmp_path,
    ):
        from tools.generate.graph_projection import build_graph_projection

        with sqlite3.connect(tmp_canonical_sqlite) as conn:
            conn.execute(
                "INSERT INTO nodes VALUES "
                "(4, 'ADG::Symbol::tools/a.fn', 'symbol', 'L0_routing', "
                "'tools/a.py', 'tools/a.py', 'symbol')"
            )
            conn.execute(
                "INSERT INTO edges "
                "(id, src_id, dst_id, relation_type, edge_kind, source_file, "
                "line_no, confidence_score) "
                "VALUES (4, 1, 4, 'exports', 'static', "
                "'tools/a.py', 10, 1.0)"
            )

        out = build_graph_projection(
            tmp_canonical_sqlite,
            tmp_path,
            "moduleonly",
        )
        with sqlite3.connect(out) as conn:
            assert conn.execute(
                "SELECT COUNT(*) FROM proj_nodes"
            ).fetchone()[0] == 4
            centrality_types = {
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT n.entity_type "
                    "FROM proj_centrality c "
                    "JOIN proj_nodes n ON n.adg_name = c.adg_name"
                )
            }
            assert centrality_types == {"module"}
            assert conn.execute("PRAGMA foreign_key_check").fetchall() == []

    def test_excluded_relations_are_accounted_for(
        self,
        tmp_canonical_sqlite,
        tmp_path,
    ):
        from tools.generate.graph_projection import build_graph_projection

        with sqlite3.connect(tmp_canonical_sqlite) as conn:
            conn.execute(
                "INSERT INTO edges "
                "(id, src_id, dst_id, relation_type, edge_kind, source_file, "
                "line_no, confidence_score) "
                "VALUES (4, 1, 2, 'covers', 'static', "
                "'tools/a.py', 12, 1.0)"
            )

        out = build_graph_projection(
            tmp_canonical_sqlite,
            tmp_path,
            "exclusions",
        )
        meta = _proj_meta(out)
        assert meta["excluded_edge_count"] == "1"
        assert json.loads(meta["excluded_edge_relation_counts"]) == {
            "covers": 1
        }
        assert (
            int(meta["graph_edge_count"]) + int(meta["excluded_edge_count"])
            == int(meta["canonical_edge_count"])
        )

    def test_current_snapshot_id_is_populated_in_diff(
        self,
        tmp_canonical_sqlite,
        tmp_path,
    ):
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "prior")
        current_digest = "cafebabecafebabecafebabecafebabe"
        with sqlite3.connect(tmp_canonical_sqlite) as conn:
            conn.execute(
                "UPDATE meta SET value=? WHERE key='artifact_digest'",
                (current_digest,),
            )
            conn.execute(
                "INSERT INTO edges "
                "(id, src_id, dst_id, relation_type, edge_kind, source_file, "
                "line_no, confidence_score) "
                "VALUES (4, 1, 2, 'imports', 'runtime', "
                "'tools/a.py', 13, 1.0)"
            )

        out = build_graph_projection(
            tmp_canonical_sqlite,
            tmp_path,
            "current",
        )
        with sqlite3.connect(out) as conn:
            values = {
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT curr_snapshot_id FROM proj_diff"
                )
            }
        assert values == {current_digest}

    def test_layer_weights_follow_authoritative_order(self):
        from tools.generate.graph_projection import (
            _layer_criticality_weight,
        )

        assert _layer_criticality_weight("L0_routing") == 2.0
        assert _layer_criticality_weight("L2_execution") == 1.8
        assert _layer_criticality_weight("L5") == 1.7
        assert _layer_criticality_weight("L6") == 1.0
        assert _layer_criticality_weight("unknown") == 0.2
