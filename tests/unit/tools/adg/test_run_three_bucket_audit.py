"""CLI tests for tools/adg/run_three_bucket_audit.py (ADR-079 audit entrypoint)."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPT = _REPO_ROOT / "tools" / "adg" / "run_three_bucket_audit.py"


def _touch_snapshot(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE edges (authority TEXT)")
        con.commit()
    finally:
        con.close()


def _run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    import os

    run_env = {**os.environ}
    if env:
        run_env.update(env)
    for key in (
        "ADG_THREE_BUCKET",
        "ADG_RUNTIME_VIEW",
        "ADG_REGISTRY_LIFT",
        "ADG_THREE_BUCKET_REPORTS",
        "ADG_THREE_BUCKET_SIGN",
    ):
        run_env.pop(key, None)
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        cwd=_REPO_ROOT,
        env=run_env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_exits_2_when_no_stage_enabled() -> None:
    proc = _run_cli()
    assert proc.returncode == 2
    assert "no three-bucket stage enabled" in proc.stderr


def test_cli_enable_all_with_snapshot(tmp_path: Path) -> None:
    snap = tmp_path / "adg_indexed_cli.sqlite"
    _touch_snapshot(snap)
    proc = _run_cli("--snapshot", str(snap), "--enable-all")
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_missing_snapshot_returns_2(tmp_path: Path) -> None:
    missing = tmp_path / "missing.sqlite"
    proc = _run_cli("--snapshot", str(missing), env={"ADG_THREE_BUCKET": "1"})
    assert proc.returncode == 2
    assert "not found" in proc.stderr.lower()
