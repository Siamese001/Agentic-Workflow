"""Registry lift must not abort on Windows junction dirs (.venv/lib64)."""

from __future__ import annotations

from pathlib import Path

from tools.adg.safe_repo_scan import safe_scan_files

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_safe_scan_repo_root_does_not_raise() -> None:
    hits = safe_scan_files(REPO_ROOT, r"mcp_config\.json")
    assert isinstance(hits, dict)
