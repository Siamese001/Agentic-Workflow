"""Unit tests for ops_scripts/ci/check_plan_notion_wave_freshness.py (NP4).

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W4.P4.2).

Network is fully mocked. NOTION_TOKEN is mocked via env. The on-disk plans
directory is mocked via monkeypatched ``PLANS_DIR``.
"""
from __future__ import annotations

import importlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_plan_notion_wave_freshness.py"


def _load_gate():
    sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"))
    sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))
    spec = importlib.util.spec_from_file_location(
        "check_plan_notion_wave_freshness", GATE_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_plan_notion_wave_freshness"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def gate():
    return _load_gate()


def _make_row(slug: str, status: str, last_edited_iso: str) -> dict:
    return {
        "id": f"page-{slug}",
        "last_edited_time": last_edited_iso,
        "properties": {
            "Slug": {"title": [{"plain_text": slug}]},
            "Status": {"select": {"name": status}},
        },
    }


# ---------------------------------------------------------------------------
# evaluate() — skip / api_error / ok / violations
# ---------------------------------------------------------------------------


class TestEvaluate:
    def test_skips_when_no_token(self, gate, monkeypatch):
        monkeypatch.delenv("NOTION_TOKEN", raising=False)
        monkeypatch.delenv("NOTION_API_KEY", raising=False)
        report = gate.evaluate(threshold_hours=24)
        assert report["status"] == "skipped"
        assert "unset" in report["reason"]

    def test_api_error_status(self, gate, monkeypatch):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")

        def boom(token):
            raise OSError("network down")

        with patch.object(gate, "_query_plans", side_effect=boom):
            report = gate.evaluate(threshold_hours=24)
        assert report["status"] == "api_error"
        assert "network down" in report["reason"]

    def test_ok_when_no_active_plans(self, gate, monkeypatch):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")

        def fake_rows(token):
            yield _make_row("foo-aaaaaa", "Completed", "2026-01-01T00:00:00.000Z")

        with patch.object(gate, "_query_plans", side_effect=fake_rows):
            report = gate.evaluate(threshold_hours=24)
        assert report["status"] == "ok"
        assert report["violation_count"] == 0

    def test_ok_when_active_plan_synced_recently(self, gate, monkeypatch, tmp_path):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        plan_file = plans_dir / "demo-plan-abc123.md"
        plan_file.write_text("# demo", encoding="utf-8")

        # Notion edited 1 hour ago, file edited 1 hour ago -> within threshold.
        notion_iso = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        def fake_rows(token):
            yield _make_row("demo-plan-abc123", "In Progress", notion_iso)

        with patch.object(gate, "_query_plans", side_effect=fake_rows), patch.object(
            gate, "PLANS_DIR", plans_dir
        ):
            report = gate.evaluate(threshold_hours=24)
        assert report["status"] == "ok"
        assert report["violation_count"] == 0

    def test_violation_when_file_newer_than_notion_by_threshold(
        self, gate, monkeypatch, tmp_path
    ):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        plan_file = plans_dir / "stale-plan-bbbbbb.md"
        plan_file.write_text("# stale", encoding="utf-8")

        # Notion last_edited 30 days ago. File mtime is now (much newer).
        notion_iso = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        def fake_rows(token):
            yield _make_row("stale-plan-bbbbbb", "In Progress", notion_iso)

        with patch.object(gate, "_query_plans", side_effect=fake_rows), patch.object(
            gate, "PLANS_DIR", plans_dir
        ):
            report = gate.evaluate(threshold_hours=24)

        assert report["status"] == "violations"
        assert report["violation_count"] == 1
        v = report["violations"][0]
        assert v["slug"] == "stale-plan-bbbbbb"
        assert v["status"] == "In Progress"
        assert v["skew_hours"] > 24

    def test_skips_status_outside_active_set(self, gate, monkeypatch, tmp_path):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        (plans_dir / "old-plan-cccccc.md").write_text("# old", encoding="utf-8")
        notion_iso = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()

        def fake_rows(token):
            # Completed/Retired/Archived/Waiting/Deprioritized must be skipped.
            yield _make_row("old-plan-cccccc", "Completed", notion_iso)
            yield _make_row("old-plan-cccccc", "Retired", notion_iso)
            yield _make_row("old-plan-cccccc", "Archived", notion_iso)

        with patch.object(gate, "_query_plans", side_effect=fake_rows), patch.object(
            gate, "PLANS_DIR", plans_dir
        ):
            report = gate.evaluate(threshold_hours=24)
        assert report["status"] == "ok"
        assert report["checked_count"] == 0

    def test_skips_plan_without_on_disk_file(self, gate, monkeypatch, tmp_path):
        # Plan in Notion but no .md on disk -> skipped (different gate covers it).
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()  # empty
        notion_iso = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()

        def fake_rows(token):
            yield _make_row("ghost-plan-dddddd", "In Progress", notion_iso)

        with patch.object(gate, "_query_plans", side_effect=fake_rows), patch.object(
            gate, "PLANS_DIR", plans_dir
        ):
            report = gate.evaluate(threshold_hours=24)
        assert report["status"] == "ok"
        assert report["checked_count"] == 0


# ---------------------------------------------------------------------------
# main() — exit codes by mode
# ---------------------------------------------------------------------------


class TestMainExitCodes:
    def test_advisory_returns_zero_on_violations(self, gate, monkeypatch, tmp_path):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        monkeypatch.delenv("NOTION_PLANS_WAVE_FAIL_CLOSED", raising=False)
        monkeypatch.delenv("NOTION_PLANS_WAVE_BYPASS", raising=False)

        violations_report = {
            "status": "violations",
            "threshold_hours": 24,
            "checked_count": 1,
            "violation_count": 1,
            "violations": [
                {
                    "slug": "stale-plan-bbbbbb",
                    "status": "In Progress",
                    "file_mtime": "2026-05-10T00:00:00+00:00",
                    "notion_last_edited": "2026-04-01T00:00:00+00:00",
                    "skew_hours": 936.0,
                    "threshold_hours": 24,
                }
            ],
            "evaluated_at": "2026-05-10T00:00:00+00:00",
        }

        with patch.object(gate, "evaluate", return_value=violations_report):
            rc = gate.main(["--threshold-hours", "24"])
        assert rc == 0  # advisory

    def test_fail_closed_returns_one_on_violations(self, gate, monkeypatch):
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        monkeypatch.setenv("NOTION_PLANS_WAVE_FAIL_CLOSED", "1")
        monkeypatch.delenv("NOTION_PLANS_WAVE_BYPASS", raising=False)

        violations_report = {
            "status": "violations",
            "threshold_hours": 24,
            "checked_count": 1,
            "violation_count": 1,
            "violations": [
                {
                    "slug": "x-aaaaaa",
                    "status": "In Progress",
                    "file_mtime": "2026-05-10T00:00:00+00:00",
                    "notion_last_edited": "2026-04-01T00:00:00+00:00",
                    "skew_hours": 936.0,
                    "threshold_hours": 24,
                }
            ],
            "evaluated_at": "2026-05-10T00:00:00+00:00",
        }

        with patch.object(gate, "evaluate", return_value=violations_report):
            rc = gate.main(["--threshold-hours", "24"])
        assert rc == 1

    def test_bypass_returns_zero(self, gate, monkeypatch):
        monkeypatch.setenv("NOTION_PLANS_WAVE_BYPASS", "1")
        rc = gate.main([])
        assert rc == 0

    def test_skip_returns_zero(self, gate, monkeypatch):
        monkeypatch.delenv("NOTION_TOKEN", raising=False)
        monkeypatch.delenv("NOTION_API_KEY", raising=False)
        monkeypatch.delenv("NOTION_PLANS_WAVE_BYPASS", raising=False)
        rc = gate.main([])
        assert rc == 0


# ---------------------------------------------------------------------------
# Gate registration
# ---------------------------------------------------------------------------


class TestGateRegistration:
    def test_np4_registered_in_run_contract_gates(self):
        run_gates = REPO_ROOT / "ops_scripts" / "ci" / "run_contract_gates.py"
        text = run_gates.read_text(encoding="utf-8")
        assert "NP4 Notion Plans wave freshness" in text
        assert "check_plan_notion_wave_freshness.py" in text
