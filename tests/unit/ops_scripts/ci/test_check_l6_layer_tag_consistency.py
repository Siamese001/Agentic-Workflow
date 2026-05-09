"""Tests for ops_scripts/ci/check_l6_layer_tag_consistency.py (plan W5)."""
from __future__ import annotations

import importlib
import json
import sqlite3
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GATE = importlib.import_module("ops_scripts.ci.check_l6_layer_tag_consistency")


def _make_fake_adg(db_path: Path, l6_paths: list[str]) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE nodes (id TEXT, layer TEXT, resolved_path TEXT)"
        )
        for p in l6_paths:
            conn.execute(
                "INSERT INTO nodes (id, layer, resolved_path) VALUES (?, ?, ?)",
                (p, "L6", p),
            )
        conn.commit()
    finally:
        conn.close()


def test_main_bypass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("L6_LAYER_TAG_BYPASS", "1")
    assert GATE.main() == 0


def test_main_skips_when_no_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("L6_LAYER_TAG_BYPASS", raising=False)
    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(GATE, "SL_ROOT", tmp_path / "system_learning")
    monkeypatch.setattr(GATE, "ADG_DIR", tmp_path / "artifacts" / "adg")
    rc = GATE.main()
    assert rc == 0
    report = json.loads(
        (tmp_path / "artifacts" / "windsurf" / "l6_layer_tag_violations.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["status"] == "skipped"


def test_main_skips_stale_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    adg_dir = tmp_path / "artifacts" / "adg"
    adg_dir.mkdir(parents=True)
    snap = adg_dir / "adg_indexed_old.sqlite"
    _make_fake_adg(snap, [])
    # Force mtime to 30 days ago.
    old = time.time() - 30 * 24 * 3600
    import os as _os

    _os.utime(snap, (old, old))

    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(GATE, "SL_ROOT", tmp_path / "system_learning")
    monkeypatch.setattr(GATE, "ADG_DIR", adg_dir)
    monkeypatch.delenv("L6_LAYER_TAG_BYPASS", raising=False)

    rc = GATE.main()
    assert rc == 0
    report = json.loads(
        (tmp_path / "artifacts" / "windsurf" / "l6_layer_tag_violations.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["status"] == "skipped"
    assert "older than 7 days" in report["reason"]


def test_main_reports_full_coverage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sl = tmp_path / "system_learning"
    (sl / "engines").mkdir(parents=True)
    (sl / "engines" / "foo.py").write_text("# stub", encoding="utf-8")
    (sl / "__init__.py").write_text("# stub", encoding="utf-8")

    adg_dir = tmp_path / "artifacts" / "adg"
    adg_dir.mkdir(parents=True)
    snap = adg_dir / "adg_indexed_fresh.sqlite"
    _make_fake_adg(
        snap,
        ["system_learning/engines/foo.py", "system_learning/__init__.py"],
    )

    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(GATE, "SL_ROOT", sl)
    monkeypatch.setattr(GATE, "ADG_DIR", adg_dir)
    monkeypatch.delenv("L6_LAYER_TAG_BYPASS", raising=False)
    monkeypatch.delenv("L6_LAYER_TAG_FAIL_CLOSED", raising=False)

    rc = GATE.main()
    assert rc == 0
    report = json.loads(
        (tmp_path / "artifacts" / "windsurf" / "l6_layer_tag_violations.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["status"] == "ok"
    assert report["coverage"] == 1.0
    assert report["missing"] == []


def test_main_reports_missing_module(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sl = tmp_path / "system_learning"
    (sl / "engines").mkdir(parents=True)
    (sl / "engines" / "foo.py").write_text("# stub", encoding="utf-8")
    (sl / "engines" / "untagged.py").write_text("# stub", encoding="utf-8")

    adg_dir = tmp_path / "artifacts" / "adg"
    adg_dir.mkdir(parents=True)
    snap = adg_dir / "adg_indexed_fresh.sqlite"
    _make_fake_adg(snap, ["system_learning/engines/foo.py"])

    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(GATE, "SL_ROOT", sl)
    monkeypatch.setattr(GATE, "ADG_DIR", adg_dir)
    monkeypatch.delenv("L6_LAYER_TAG_BYPASS", raising=False)
    monkeypatch.delenv("L6_LAYER_TAG_FAIL_CLOSED", raising=False)

    rc = GATE.main()
    assert rc == 0  # advisory
    report = json.loads(
        (tmp_path / "artifacts" / "windsurf" / "l6_layer_tag_violations.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["status"] == "findings"
    assert "system_learning/engines/untagged.py" in report["missing"]
    assert report["coverage"] < 1.0


def test_main_fail_closed_returns_2(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sl = tmp_path / "system_learning"
    sl.mkdir(parents=True)
    (sl / "untagged.py").write_text("# stub", encoding="utf-8")
    adg_dir = tmp_path / "artifacts" / "adg"
    adg_dir.mkdir(parents=True)
    snap = adg_dir / "adg_indexed_fresh.sqlite"
    _make_fake_adg(snap, [])

    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(GATE, "SL_ROOT", sl)
    monkeypatch.setattr(GATE, "ADG_DIR", adg_dir)
    monkeypatch.setenv("L6_LAYER_TAG_FAIL_CLOSED", "1")
    monkeypatch.delenv("L6_LAYER_TAG_BYPASS", raising=False)

    rc = GATE.main()
    assert rc == 2
