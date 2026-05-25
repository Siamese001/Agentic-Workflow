"""Unit tests for check_l0_v15_no_v12_hotpath CI gate."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))

import check_l0_v15_no_v12_hotpath as gate  # noqa: E402


def test_scan_allows_archive_and_tests() -> None:
    gate._repo = REPO_ROOT
    archive = REPO_ROOT / "agentic_core/L0_routing/_archive/v12/reasoning/v12_route_selector.py"
    assert archive.is_file()
    assert gate._scan_file(archive) == []

    test_file = REPO_ROOT / "tests/agentic_core/L0_routing/config/test_fallback_chains_loader.py"
    assert test_file.is_file()
    assert gate._scan_file(test_file) == []


def test_scan_flags_v12_import_in_production_tree(tmp_path: Path) -> None:
    gate._repo = tmp_path
    bad = tmp_path / "apps_fake" / "bad.py"
    bad.parent.mkdir(parents=True)
    bad.write_text(
        "from agentic_core.L0_routing.reasoning.v12_route_selector import foo\n",
        encoding="utf-8",
    )
    hits = gate._scan_file(bad)
    assert hits
    assert "v12_route_selector" in hits[0]


def test_main_passes_on_current_repo() -> None:
    assert gate.main() == 0
