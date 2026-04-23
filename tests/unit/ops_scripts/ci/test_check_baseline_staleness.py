"""Tests for ops_scripts/ci/check_baseline_staleness.py (W2)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from ops_scripts.ci import check_baseline_staleness as mod


NOW = datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc)


def _write(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec), encoding="utf-8")


def test_empty_dir_returns_no_rows(tmp_path: Path) -> None:
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []


def test_zero_count_is_never_stale(tmp_path: Path) -> None:
    _write(
        tmp_path / "wiring_zero_ratchet.json",
        {
            "gate_id": "ZERO",
            "count": 0,
            "seeded_at": "2020-01-01T00:00:00+00:00",
        },
    )
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []


def test_recent_baseline_not_flagged(tmp_path: Path) -> None:
    recent = (NOW - timedelta(days=5)).isoformat()
    _write(
        tmp_path / "wiring_recent_ratchet.json",
        {"gate_id": "RECENT", "count": 10, "seeded_at": recent},
    )
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []


def test_old_baseline_with_nonzero_count_flagged(tmp_path: Path) -> None:
    old = (NOW - timedelta(days=45)).isoformat()
    _write(
        tmp_path / "wiring_old_ratchet.json",
        {"gate_id": "OLD", "count": 100, "seeded_at": old},
    )
    rows = mod.collect_stale(tmp_path, threshold_days=30, now=NOW)
    assert len(rows) == 1
    assert rows[0]["gate_id"] == "OLD"
    assert rows[0]["count"] == 100
    assert rows[0]["age_days"] == 45


def test_most_recent_timestamp_wins(tmp_path: Path) -> None:
    """seeded_at is old but tightened_at is recent -> not stale."""
    _write(
        tmp_path / "wiring_tightened_ratchet.json",
        {
            "gate_id": "TIGHTENED",
            "count": 50,
            "seeded_at": (NOW - timedelta(days=90)).isoformat(),
            "tightened_at": (NOW - timedelta(days=3)).isoformat(),
        },
    )
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []


def test_missing_all_timestamps_treated_as_maximally_stale(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "wiring_nots_ratchet.json",
        {"gate_id": "NOTS", "count": 5},
    )
    rows = mod.collect_stale(tmp_path, threshold_days=30, now=NOW)
    assert len(rows) == 1
    assert rows[0]["effective_timestamp"] is None
    assert rows[0]["age_days"] > 30


def test_auto_promoted_tier_surfaced(tmp_path: Path) -> None:
    old = (NOW - timedelta(days=60)).isoformat()
    _write(
        tmp_path / "wiring_prom_ratchet.json",
        {
            "gate_id": "PROM",
            "count": 7,
            "seeded_at": old,
            "auto_promoted_tier": "B",
        },
    )
    rows = mod.collect_stale(tmp_path, threshold_days=30, now=NOW)
    assert rows[0]["auto_promoted_tier"] == "B"


def test_threshold_override(tmp_path: Path) -> None:
    age = (NOW - timedelta(days=10)).isoformat()
    _write(
        tmp_path / "wiring_tenday_ratchet.json",
        {"gate_id": "TENDAY", "count": 1, "seeded_at": age},
    )
    # threshold=30 -> not stale
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []
    # threshold=7 -> stale
    rows = mod.collect_stale(tmp_path, threshold_days=7, now=NOW)
    assert len(rows) == 1


def test_malformed_json_is_skipped(tmp_path: Path) -> None:
    (tmp_path / "wiring_bad_ratchet.json").write_text(
        "not valid json", encoding="utf-8"
    )
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []


def test_non_wiring_prefix_ignored(tmp_path: Path) -> None:
    _write(
        tmp_path / "other_ratchet.json",
        {"gate_id": "OTHER", "count": 100,
         "seeded_at": (NOW - timedelta(days=400)).isoformat()},
    )
    assert mod.collect_stale(tmp_path, threshold_days=30, now=NOW) == []


def test_cli_default_returns_zero_when_empty(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    rc = mod.main(["--baseline-dir", str(tmp_path), "--days", "30"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "status=pass" in out
    assert "stale_ratchets=0" in out


def test_cli_strict_fails_when_stale(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _write(
        tmp_path / "wiring_stale_ratchet.json",
        {
            "gate_id": "STALE",
            "count": 5,
            "seeded_at": (NOW - timedelta(days=60)).isoformat(),
        },
    )
    rc = mod.main(
        ["--baseline-dir", str(tmp_path), "--days", "30", "--strict"]
    )
    assert rc == 1
    out = capsys.readouterr().out
    assert "STALE" in out


def test_cli_json_output_is_machine_readable(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _write(
        tmp_path / "wiring_jsoncase_ratchet.json",
        {
            "gate_id": "JSONCASE",
            "count": 3,
            "seeded_at": (NOW - timedelta(days=90)).isoformat(),
        },
    )
    rc = mod.main(["--baseline-dir", str(tmp_path), "--days", "30", "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["gate_id"] == "S_STALE_baseline_age"
    assert payload["stale_count"] == 1
    assert payload["ratchets"][0]["gate_id"] == "JSONCASE"
