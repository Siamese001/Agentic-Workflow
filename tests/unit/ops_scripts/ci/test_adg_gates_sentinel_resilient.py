"""Regression tests — the two ADG gates that used naive ``sorted(glob())[-1]``
snapshot resolvers MUST skip the legacy sentinel
``adg_indexed_99999999_9999.sqlite`` and pick the real snapshot.

Plan: ``.windsurf/plans/adg-three-bucket-unified-c4f8e2.md`` (W6 P6.1 / P6.3
hardening, 2026-04-30).

Failure precedent (2026-04-30):
  A 24KB sentinel at ``artifacts/adg/adg_indexed_99999999_9999.sqlite`` was
  shadowing the real 556MB snapshot because
  ``sorted(glob("adg_indexed_*.sqlite"))[-1]`` picked the lexicographically-
  larger filename. This caused:

    - ``check_adg_certified`` → falsely reported ``ADG_NOT_CERTIFIED`` with
      a "triplet completeness" blocker despite the real snapshot having
      762,238 edges properly triplet-attested (0 NULLs).
    - ``check_schema_graduation_readiness`` → falsely reported
      "column 'bucket' not present" on an empty stub with 4 columns.

The fix was to delegate both gates' ``_latest_snapshot`` to the canonical
``tools.adg.shared_modules.path_resolver.latest_sqlite`` which validates
``%m%d%Y_%H%M`` timestamps (``99999999_9999`` fails — month 99 invalid) and
picks by mtime. These tests lock that behavior in.
"""

from __future__ import annotations

# Inventory consumer: these tests probe gate file-resolution only; no MV use.
__adg_consumer_mode__ = "inventory"

import importlib
import sqlite3
from pathlib import Path


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_real_snapshot(path: Path) -> None:
    """Real snapshots have a ``nodes`` table with the expected schema."""
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, layer TEXT, "
        "entity_type TEXT, identity_kind TEXT, confidence TEXT, resolved_path TEXT)"
    )
    con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY, bucket TEXT, "
                "resolution_status TEXT, authority_status TEXT)")
    con.commit()
    con.close()


def _make_sentinel_stub(path: Path) -> None:
    """Empty 24KB-style stub that the sentinel typically is."""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE placeholder (id INTEGER)")
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# check_schema_graduation_readiness resolver
# ---------------------------------------------------------------------------


def test_schema_graduation_readiness_resolver_skips_sentinel(
    tmp_path: Path, monkeypatch
) -> None:
    """The gate's ``_latest_snapshot`` must return the real snapshot even when
    the sentinel with lexicographic-max name is present.
    """
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    real = art / "adg_indexed_04302026_1319.sqlite"
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    _make_real_snapshot(real)
    _make_sentinel_stub(sentinel)

    # Point the canonical resolver's get_adg_dir at our tmp dir.
    monkeypatch.setenv("ADG_DIR", str(art))

    # Reload the gate module so its REPO_ROOT-derived ARTIFACTS_DIR sees
    # the real files (it resolves at import time from the gate's own file
    # location, which is why tests must work through the canonical resolver
    # via ADG_DIR rather than patching the gate's module constant).
    import ops_scripts.ci.check_schema_graduation_readiness as gate  # noqa: PLC0415
    importlib.reload(gate)

    # Force the canonical-resolver path (not the ImportError fallback).
    resolved = gate._latest_snapshot()
    assert resolved is not None
    assert resolved.name == "adg_indexed_04302026_1319.sqlite", (
        f"resolver returned {resolved.name!r}; expected real snapshot "
        f"(sentinel must be skipped)"
    )


def test_schema_graduation_readiness_fallback_skips_sentinel(
    tmp_path: Path, monkeypatch
) -> None:
    """Even if tools.adg.shared_modules.path_resolver can't be imported, the
    fallback branch must still skip the sentinel by timestamp validation.
    """
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    real = art / "adg_indexed_04302026_1319.sqlite"
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    _make_real_snapshot(real)
    _make_sentinel_stub(sentinel)

    import ops_scripts.ci.check_schema_graduation_readiness as gate  # noqa: PLC0415
    monkeypatch.setattr(gate, "ARTIFACTS_DIR", art)

    # Force the fallback branch by making the canonical module unimportable.
    import sys  # noqa: PLC0415
    monkeypatch.setitem(
        sys.modules, "tools.adg.shared_modules.path_resolver", None
    )

    resolved = gate._latest_snapshot()
    assert resolved is not None
    assert resolved.name == "adg_indexed_04302026_1319.sqlite"


# ---------------------------------------------------------------------------
# check_adg_certified resolver
# ---------------------------------------------------------------------------


def test_adg_certified_resolver_skips_sentinel(
    tmp_path: Path, monkeypatch
) -> None:
    """Same contract for check_adg_certified — sentinel must NOT shadow the
    real snapshot, otherwise we get a false ``ADG_NOT_CERTIFIED`` verdict.
    """
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    real = art / "adg_indexed_04302026_1319.sqlite"
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    _make_real_snapshot(real)
    _make_sentinel_stub(sentinel)

    monkeypatch.setenv("ADG_DIR", str(art))

    import ops_scripts.ci.check_adg_certified as gate  # noqa: PLC0415
    importlib.reload(gate)

    resolved = gate._latest_snapshot()
    assert resolved is not None
    assert resolved.name == "adg_indexed_04302026_1319.sqlite", (
        f"resolver returned {resolved.name!r}; expected real snapshot"
    )


def test_adg_certified_fallback_skips_sentinel(
    tmp_path: Path, monkeypatch
) -> None:
    """Fallback path for check_adg_certified must also skip the sentinel."""
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    real = art / "adg_indexed_04302026_1319.sqlite"
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    _make_real_snapshot(real)
    _make_sentinel_stub(sentinel)

    import ops_scripts.ci.check_adg_certified as gate  # noqa: PLC0415
    monkeypatch.setattr(gate, "ARTIFACT_DIR", art)

    import sys  # noqa: PLC0415
    monkeypatch.setitem(
        sys.modules, "tools.adg.shared_modules.path_resolver", None
    )

    resolved = gate._latest_snapshot()
    assert resolved is not None
    assert resolved.name == "adg_indexed_04302026_1319.sqlite"


# ---------------------------------------------------------------------------
# Both gates handle "only sentinel exists" by returning None (nothing valid)
# ---------------------------------------------------------------------------


def test_schema_graduation_only_sentinel_returns_none(
    tmp_path: Path, monkeypatch
) -> None:
    """When ONLY the sentinel is present, the resolver returns None rather
    than picking the invalid stub."""
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    _make_sentinel_stub(sentinel)

    monkeypatch.setenv("ADG_DIR", str(art))
    import ops_scripts.ci.check_schema_graduation_readiness as gate  # noqa: PLC0415
    importlib.reload(gate)

    assert gate._latest_snapshot() is None


def test_adg_certified_only_sentinel_returns_none(
    tmp_path: Path, monkeypatch
) -> None:
    """Same contract for check_adg_certified."""
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    _make_sentinel_stub(sentinel)

    monkeypatch.setenv("ADG_DIR", str(art))
    import ops_scripts.ci.check_adg_certified as gate  # noqa: PLC0415
    importlib.reload(gate)

    assert gate._latest_snapshot() is None


# ---------------------------------------------------------------------------
# Mtime tiebreak: when multiple valid snapshots exist, newest wins
# ---------------------------------------------------------------------------


def test_resolver_picks_newest_by_mtime(tmp_path: Path, monkeypatch) -> None:
    """Two valid snapshots — the one with the newer mtime wins, regardless of
    filename lexicographic order.
    """
    import os
    import time

    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    older = art / "adg_indexed_05012026_1200.sqlite"  # lexicographically later
    newer = art / "adg_indexed_04302026_1319.sqlite"  # lexicographically earlier
    _make_real_snapshot(older)
    time.sleep(0.01)
    _make_real_snapshot(newer)
    # Force older's mtime to be earlier
    os.utime(older, (older.stat().st_atime, older.stat().st_mtime - 3600))

    monkeypatch.setenv("ADG_DIR", str(art))
    import ops_scripts.ci.check_adg_certified as gate  # noqa: PLC0415
    importlib.reload(gate)

    # Should pick the newer one (by mtime), not the lexicographically-larger one.
    resolved = gate._latest_snapshot()
    assert resolved is not None
    assert resolved.name == newer.name, (
        f"resolver picked {resolved.name!r} by filename; expected "
        f"{newer.name!r} by mtime"
    )
