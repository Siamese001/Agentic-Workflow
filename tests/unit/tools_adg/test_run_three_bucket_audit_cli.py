"""CLI guards for optional three-bucket audit refresh (off hot path)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tools" / "adg" / "run_three_bucket_audit.py"


def test_cli_exits_when_no_stage_enabled() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={k: v for k, v in __import__("os").environ.items() if not k.startswith("ADG_")},
    )
    assert proc.returncode == 2
    assert "no three-bucket stage enabled" in proc.stderr


def test_cli_exits_when_snapshot_missing(monkeypatch) -> None:
    monkeypatch.setenv("ADG_THREE_BUCKET", "1")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--snapshot", "/nonexistent/adg.sqlite"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "snapshot not found" in proc.stderr
