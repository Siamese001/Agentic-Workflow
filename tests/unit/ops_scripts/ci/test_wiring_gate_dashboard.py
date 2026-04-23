"""Tests for ops_scripts/ci/wiring_gate_dashboard.py (W3)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from ops_scripts.ci import wiring_gate_dashboard as mod


NOW = datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc)


def _write(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec), encoding="utf-8")


def test_collect_rows_empty_dir(tmp_path: Path) -> None:
    assert mod.collect_rows(tmp_path, now=NOW) == []


def test_row_parses_core_fields(tmp_path: Path) -> None:
    _write(tmp_path / "wiring_alpha_ratchet.json", {
        "gate_id": "ALPHA",
        "count": 42,
        "seeded_at": (NOW - timedelta(days=100)).isoformat(),
        "tightened_at": (NOW - timedelta(days=2)).isoformat(),
        "tighten_history": [
            {"from": 90, "to": 50, "at": "x"},
            {"from": 50, "to": 42, "at": "y"},
        ],
    })
    rows = mod.collect_rows(tmp_path, now=NOW)
    assert len(rows) == 1
    r = rows[0]
    assert r.gate_id == "ALPHA"
    assert r.count == 42
    assert r.age_days == 100
    assert r.last_change_days == 2
    assert r.last_from == 50
    assert r.last_to == 42
    assert r.tighten_count == 2


def test_auto_promoted_tier_surfaced(tmp_path: Path) -> None:
    _write(tmp_path / "wiring_bravo_ratchet.json", {
        "gate_id": "BRAVO",
        "count": 0,
        "auto_promoted_tier": "B",
    })
    rows = mod.collect_rows(tmp_path, now=NOW)
    assert rows[0].auto_promoted_tier == "B"


def test_summary_aggregates(tmp_path: Path) -> None:
    _write(tmp_path / "wiring_a_ratchet.json",
           {"gate_id": "A", "count": 0})
    _write(tmp_path / "wiring_b_ratchet.json",
           {"gate_id": "B", "count": 10,
            "seeded_at": (NOW - timedelta(days=60)).isoformat()})
    _write(tmp_path / "wiring_c_ratchet.json",
           {"gate_id": "C", "count": 3,
            "seeded_at": (NOW - timedelta(days=5)).isoformat(),
            "tighten_history": [{"from": 5, "to": 3}]})
    _write(tmp_path / "wiring_d_ratchet.json",
           {"gate_id": "D", "count": 0, "auto_promoted_tier": "B"})

    rows = mod.collect_rows(tmp_path, now=NOW)
    summary = mod.summarize(rows)
    assert summary["total_ratchets"] == 4
    assert summary["zero_count_ratchets"] == 2
    assert summary["ratchets_with_tighten_history"] == 1
    assert summary["total_debt_units"] == 13
    assert summary["auto_promoted_gates"] == ["D"]
    # B is dormant (count=10, no history), older than C
    assert summary["oldest_dormant_ratchet"]["gate_id"] == "B"
    assert summary["oldest_dormant_ratchet"]["count"] == 10


def test_sort_by_count(tmp_path: Path) -> None:
    _write(tmp_path / "wiring_a_ratchet.json", {"gate_id": "A", "count": 5})
    _write(tmp_path / "wiring_b_ratchet.json", {"gate_id": "B", "count": 100})
    _write(tmp_path / "wiring_c_ratchet.json", {"gate_id": "C", "count": 50})
    rows = mod.collect_rows(tmp_path, now=NOW)
    sorted_rows = mod._sort_rows(rows, "count")
    assert [r.gate_id for r in sorted_rows] == ["B", "C", "A"]


def test_sort_by_age(tmp_path: Path) -> None:
    _write(tmp_path / "wiring_a_ratchet.json",
           {"gate_id": "A", "count": 1,
            "seeded_at": (NOW - timedelta(days=10)).isoformat()})
    _write(tmp_path / "wiring_b_ratchet.json",
           {"gate_id": "B", "count": 1,
            "seeded_at": (NOW - timedelta(days=100)).isoformat()})
    rows = mod.collect_rows(tmp_path, now=NOW)
    sorted_rows = mod._sort_rows(rows, "age")
    assert sorted_rows[0].gate_id == "B"


def test_malformed_json_skipped(tmp_path: Path) -> None:
    (tmp_path / "wiring_bad_ratchet.json").write_text("{ broken",
                                                       encoding="utf-8")
    _write(tmp_path / "wiring_ok_ratchet.json", {"gate_id": "OK", "count": 1})
    rows = mod.collect_rows(tmp_path, now=NOW)
    assert [r.gate_id for r in rows] == ["OK"]


def test_cli_table_output(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _write(tmp_path / "wiring_x_ratchet.json",
           {"gate_id": "X", "count": 7})
    rc = mod.main(["--baseline-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "gate_id" in out
    assert "X" in out
    assert "total_debt_units=7" in out


def test_cli_json_output(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _write(tmp_path / "wiring_j_ratchet.json",
           {"gate_id": "J", "count": 0})
    rc = mod.main(["--baseline-dir", str(tmp_path), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["total_ratchets"] == 1
    assert payload["rows"][0]["gate_id"] == "J"


def test_cli_only_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _write(tmp_path / "wiring_zz_ratchet.json",
           {"gate_id": "ZZ", "count": 0})
    _write(tmp_path / "wiring_nz_ratchet.json",
           {"gate_id": "NZ", "count": 3})
    rc = mod.main(["--baseline-dir", str(tmp_path),
                   "--only-nonzero", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    gate_ids = [r["gate_id"] for r in payload["rows"]]
    assert "ZZ" not in gate_ids
    assert "NZ" in gate_ids
