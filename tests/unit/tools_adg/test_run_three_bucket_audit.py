"""CLI regression tests for ``tools/adg/run_three_bucket_audit.py`` (isolated imports)."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tools" / "adg" / "run_three_bucket_audit.py"
OTB_PATH = REPO_ROOT / "tools" / "generate" / "integration" / "optional_three_bucket.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def audit_cli(monkeypatch: pytest.MonkeyPatch):
    """Load audit CLI with optional_three_bucket wired without integration package __init__."""
    otb = _load_module("optional_three_bucket_test_iso", OTB_PATH)
    audit = _load_module("run_three_bucket_audit_test_iso", SCRIPT)
    audit.run_optional_three_bucket_enrichment = otb.run_optional_three_bucket_enrichment
    audit.three_bucket_master_enabled = otb.three_bucket_master_enabled
    for name in (
        "ADG_THREE_BUCKET",
        "ADG_RUNTIME_VIEW",
        "ADG_REGISTRY_LIFT",
        "ADG_THREE_BUCKET_REPORTS",
        "ADG_THREE_BUCKET_SIGN",
    ):
        monkeypatch.delenv(name, raising=False)
    return audit


@pytest.fixture
def _argv(monkeypatch: pytest.MonkeyPatch):
    def _set(args: list[str]) -> None:
        monkeypatch.setattr(sys, "argv", ["run_three_bucket_audit.py", *args])

    return _set


def test_main_exits_2_when_no_stage_enabled(audit_cli, _argv) -> None:
    _argv([])
    assert audit_cli.main() == 2


def test_main_enable_all_missing_snapshot_returns_2(audit_cli, _argv, tmp_path: Path) -> None:
    missing = tmp_path / "missing.sqlite"
    _argv(["--enable-all", "--snapshot", str(missing)])
    assert audit_cli.main() == 2


def test_main_enable_all_skips_when_tables_missing(audit_cli, _argv, tmp_path: Path) -> None:
    snap = tmp_path / "empty.sqlite"
    snap.write_bytes(b"SQLite format 3\x00")
    _argv(["--enable-all", "--snapshot", str(snap)])
    assert audit_cli.main() == 2


def test_main_enable_all_returns_0_on_valid_minimal_snapshot(
    audit_cli, _argv, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snap = tmp_path / "adg_indexed_test.sqlite"
    con = sqlite3.connect(str(snap))
    try:
        con.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        con.commit()
    finally:
        con.close()

    monkeypatch.setattr(
        "tools.adg.snapshot_fingerprint.snapshot_fingerprint",
        lambda _p: {"source_snapshot_sha256": "abc", "source_snapshot_mtime_iso": "t"},
    )
    _argv(["--enable-all", "--snapshot", str(snap)])
    assert audit_cli.main() == 0
