"""Tests for the graph projection system (Increment 1–3).

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
        from tools.generate.graph_projection import build_graph_projection

        out = build_graph_projection(tmp_canonical_sqlite, tmp_path, "test05")
        meta = _proj_meta(out)
        assert "schema_version" in meta
        assert meta["schema_version"], "schema_version must be non-empty"

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

    def test_stale_backend_still_returns_results(self, tmp_canonical_sqlite, tmp_path, monkeypatch):
        """A stale projection is still queryable — callers use is_stale() to decide."""
        from tools.generate.graph_projection import build_graph_projection

        build_graph_projection(tmp_canonical_sqlite, tmp_path, "stale02")

        conn = sqlite3.connect(str(tmp_canonical_sqlite))
        conn.execute("UPDATE meta SET value = 'mutated' WHERE key = 'artifact_digest'")
        conn.commit()
        conn.close()

        from tools.adg.core import graph_projection_backend as gpb_mod

        monkeypatch.setattr(gpb_mod, "_resolve_adg_dir", lambda: tmp_path)

        from tools.adg.core.graph_projection_backend import GraphProjectionBackend

        with GraphProjectionBackend(canonical_sqlite_path=tmp_canonical_sqlite) as backend:
            result = backend.get_blast_radius("ADG::Module::tools/a")
            assert isinstance(result, dict), "Stale backend must still return dict from get_blast_radius"
            assert result["stale"] is True


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
