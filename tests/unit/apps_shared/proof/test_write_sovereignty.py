"""Tests for apps_shared.proof.write_sovereignty."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from apps_shared.proof.write_sovereignty import (
    WriteSovereigntyResult,
    validate_write_sovereignty,
)


def test_clean_snapshot_passes(tiny_adg_snapshot: Path):
    r = validate_write_sovereignty(snapshot=tiny_adg_snapshot, apps=("apps_eval",))
    assert r.ok
    assert r.fail_reasons == []
    assert "apps_eval" in r.direct_writes_per_app


def test_dirty_snapshot_fails(tiny_adg_snapshot: Path):
    # Replace the empty mv_write_sovereignty_paths view with one that returns rows
    con = sqlite3.connect(tiny_adg_snapshot)
    con.execute("DROP VIEW mv_write_sovereignty_paths")
    con.execute(
        """
        CREATE VIEW mv_write_sovereignty_paths AS
            SELECT id AS edge_id, resolved_path AS writer_file, layer AS writer_layer,
                   'os.write' AS write_symbol, 1 AS write_line,
                   0 AS is_uwg_routed, 1 AS is_direct_infra_write,
                   'P0' AS severity
            FROM nodes WHERE resolved_path LIKE 'apps_eval/%'
        """
    )
    con.commit()
    con.close()
    r = validate_write_sovereignty(snapshot=tiny_adg_snapshot, apps=("apps_eval",))
    assert not r.ok
    assert any("apps_eval" in s for s in r.fail_reasons)


def test_missing_snapshot_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        validate_write_sovereignty(snapshot=tmp_path / "nope.sqlite", apps=("apps_eval",))


def test_result_to_dict_serializable(tiny_adg_snapshot: Path):
    r = validate_write_sovereignty(snapshot=tiny_adg_snapshot, apps=("apps_eval",))
    d = r.to_dict()
    assert "snapshot_path" in d
    assert d["ok"] is True
    assert isinstance(d["apps_checked"], list)
