"""Tests for apps_shared.proof.app_inventory."""

from __future__ import annotations

from pathlib import Path

from apps_shared.proof.app_inventory import discover_apps, required_apps


def test_discover_apps_returns_apps_eval_and_apps_shared(tiny_adg_snapshot: Path, tmp_path: Path):
    inv = discover_apps(repo_root=tmp_path, adg_snapshot=tiny_adg_snapshot)
    pkgs = {e.app_id for e in inv}
    assert "apps_eval" in pkgs
    assert "apps_shared" in pkgs
    # agentic_core (not apps_*) must NOT appear
    assert "agentic_core" not in pkgs


def test_discover_apps_classifies_high_impact_and_infrastructure(tiny_adg_snapshot, tmp_path):
    # Add apps_underwriting_ai and apps_shared rows
    import sqlite3

    con = sqlite3.connect(tiny_adg_snapshot)
    con.execute(
        "INSERT INTO nodes VALUES ('uw1', 'apps_underwriting_ai/foo.py', 'apps_underwriting_ai/foo.py', 'L_APP')"
    )
    con.commit()
    con.close()
    inv = discover_apps(repo_root=tmp_path, adg_snapshot=tiny_adg_snapshot)
    classes = {e.app_id: e.risk_class for e in inv}
    assert classes.get("apps_underwriting_ai") == "HIGH_IMPACT"
    assert classes.get("apps_shared") == "INFRASTRUCTURE"
    assert classes.get("apps_eval") == "NORMAL"


def test_required_apps_filters_to_canonical(tiny_adg_snapshot, tmp_path):
    inv = discover_apps(repo_root=tmp_path, adg_snapshot=tiny_adg_snapshot)
    req = required_apps(inv)
    # Only apps in fixture (apps_eval, apps_shared) should remain
    assert set(req).issubset(
        {
            "apps_eval",
            "apps_exec",
            "apps_lic",
            "apps_research",
            "apps_rfp",
            "apps_rg",
            "apps_shared",
            "apps_underwriting_ai",
        }
    )


def test_discover_apps_records_node_count(tiny_adg_snapshot, tmp_path):
    inv = discover_apps(repo_root=tmp_path, adg_snapshot=tiny_adg_snapshot)
    eval_entry = next(e for e in inv if e.app_id == "apps_eval")
    assert eval_entry.node_count_in_adg == 2  # n1 + n2


def test_discover_apps_missing_snapshot_raises(tmp_path: Path):
    import pytest

    with pytest.raises(FileNotFoundError):
        discover_apps(repo_root=tmp_path, adg_snapshot=tmp_path / "no.sqlite")
