"""W1.2 — LOC/module ratchet against committed baseline + allowlist."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
BASELINE_PATH = FIXTURE_DIR / "complexity_baseline.json"
ALLOWLIST_PATH = FIXTURE_DIR / "complexity_allowlist.json"


def test_baseline_fixture_exists_and_valid() -> None:
    assert BASELINE_PATH.is_file(), "run: python -c \"from ops_scripts.apps_rg.section_complexity_reduction_audit import export_complexity_baseline_snapshot; ...\""
    doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    assert doc.get("linked_plan_id") == "apps-rg-complexity-test-radar-605dcc"
    assert doc.get("audit_script_digest")
    assert doc.get("generated_at")
    for sec in doc.get("sections") or []:
        for key in ("section_id", "tagged_runtime_loc", "module_count", "loc"):
            assert key in sec
    for mod in doc.get("modules") or []:
        for key in ("section_id", "module_path", "loc"):
            assert key in mod


def test_allowlist_entries_have_required_fields() -> None:
    if not ALLOWLIST_PATH.is_file():
        pytest.skip("allowlist optional until first allowlisted module")
    doc = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
    for entry in doc.get("entries") or []:
        assert entry.get("reason")
        assert entry.get("review_after")
        assert entry.get("linked_plan_id")
        assert entry.get("owner")
        assert entry.get("module_path")


def test_ci_complexity_baseline_gate_passes_on_clean_tree() -> None:
    from ops_scripts.ci.check_apps_rg_complexity_baseline import run_check

    report = run_check()
    assert report["STATUS"] == "PASS", report.get("decisive_failures")


def test_synthetic_loc_increase_red_path() -> None:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    live = dict(baseline)
    sections = [dict(s) for s in live.get("sections") or []]
    sections[0] = dict(sections[0])
    sections[0]["tagged_runtime_loc"] = int(sections[0]["tagged_runtime_loc"]) + 5000
    live["sections"] = sections
    base_sec = {s["section_id"]: s for s in baseline["sections"]}
    live_sec = {s["section_id"]: s for s in live["sections"]}
    increased = [
        sid
        for sid in base_sec
        if int(live_sec[sid]["tagged_runtime_loc"]) > int(base_sec[sid]["tagged_runtime_loc"])
    ]
    assert increased, "red-path fixture failed to simulate LOC increase"
