"""Tests for W1 hardening of WiringGate base harness.

Covers:
  1. Monotone baseline auto-tighten on green run (count < baseline).
  2. Per-gate opt-out via ``auto_tighten_baseline=False`` class attr.
  3. Per-record opt-out via ``"auto_tighten": false`` in baseline JSON.
  4. R->B auto-promotion after N consecutive zero-count runs.
  5. Promoted ratchet blocks on the next run with count>0.
  6. Non-zero runs reset the streak.
  7. Baseline tighten history is capped at 20 entries.
  8. Tighten does NOT occur when count == baseline.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from ops_scripts.ci._adg_wiring_gate_base import (
    Violation,
    WiringGate,
)


class _FakeGate(WiringGate):
    """Minimal concrete ratchet gate for tests. Violation count is injected."""

    gate_id = "TEST_FAKE_R"
    tier = "R"
    baseline_filename = "test_fake_r_ratchet.json"

    def __init__(self, snapshot: Path, violation_count: int) -> None:
        self.snapshot = snapshot
        self.waivers = {}
        self._violation_count = violation_count

    def run(self, conn: sqlite3.Connection) -> list[Violation]:  # noqa: ARG002
        return [
            Violation(
                gate_id=self.gate_id,
                tier="R",
                subject=f"sub_{i}",
                rule="test",
                detail="synthetic",
            )
            for i in range(self._violation_count)
        ]


@pytest.fixture
def fake_snapshot(tmp_path: Path) -> Path:
    """Create a tiny valid SQLite snapshot file for connect_snapshot()."""
    snap = tmp_path / "adg_indexed_testshot.sqlite"
    conn = sqlite3.connect(str(snap))
    conn.execute("CREATE TABLE nodes (id INTEGER)")
    conn.close()
    return snap


@pytest.fixture
def isolated_baseline_dir(monkeypatch, tmp_path: Path) -> Path:
    """Redirect harness BASELINE_DIR + LOG_FILE so tests don't touch repo state."""
    bdir = tmp_path / "baselines"
    bdir.mkdir()
    ldir = tmp_path / "logs"
    ldir.mkdir()
    monkeypatch.setattr("ops_scripts.ci._adg_wiring_gate_base.BASELINE_DIR", bdir)
    monkeypatch.setattr("ops_scripts.ci._adg_wiring_gate_base.LOG_DIR", ldir)
    monkeypatch.setattr(
        "ops_scripts.ci._adg_wiring_gate_base.LOG_FILE",
        ldir / "wiring_gate_violations.jsonl",
    )
    # Prevent any WIRING_GATE_BYPASS from leaking in.
    monkeypatch.delenv("WIRING_GATE_BYPASS", raising=False)
    return bdir


def _write_baseline(path: Path, rec: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec), encoding="utf-8")


def _read_baseline(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# --- W1.1 monotone auto-tighten -----------------------------------------


def test_baseline_auto_tightens_on_green_run(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 10,
            "seeded_at": "2026-04-23T00:00:00+00:00",
            "snapshot": "seed.sqlite",
        },
    )

    gate = _FakeGate(fake_snapshot, violation_count=3)
    result = gate.execute()

    assert result.status == "pass"
    assert result.baseline_count == 3  # new tightened value reflected
    rec = _read_baseline(baseline_path)
    assert rec["count"] == 3
    assert rec["tightened_at"]
    assert rec["tighten_history"][-1]["from"] == 10
    assert rec["tighten_history"][-1]["to"] == 3
    assert result.summary["baseline_tightened_from"] == 10
    assert result.summary["baseline_tightened_to"] == 3


def test_no_tighten_when_count_equal_to_baseline(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 5,
            "snapshot": "seed.sqlite",
        },
    )

    gate = _FakeGate(fake_snapshot, violation_count=5)
    result = gate.execute()

    assert result.status == "pass"
    assert _read_baseline(baseline_path)["count"] == 5
    assert "baseline_tightened_from" not in result.summary


def test_fail_when_count_exceeds_baseline(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 5,
            "snapshot": "seed.sqlite",
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=10)
    result = gate.execute()
    assert result.status == "fail"
    # baseline NOT tightened on fail
    assert _read_baseline(baseline_path)["count"] == 5


def test_opt_out_via_class_attr(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(baseline_path, {"gate_id": "TEST_FAKE_R", "count": 10})

    class _NoTightenGate(_FakeGate):
        auto_tighten_baseline = False

    gate = _NoTightenGate(fake_snapshot, violation_count=3)
    gate.execute()
    assert _read_baseline(baseline_path)["count"] == 10


def test_opt_out_via_json_field(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 10,
            "auto_tighten": False,
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=3)
    gate.execute()
    assert _read_baseline(baseline_path)["count"] == 10


def test_tighten_history_capped_at_20(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    # Seed with 25 pre-existing history entries + a big count to force tighten.
    rec = {
        "gate_id": "TEST_FAKE_R",
        "count": 100,
        "tighten_history": [{"at": f"old-{i}", "snapshot": "x", "from": 100, "to": 50} for i in range(25)],
    }
    _write_baseline(baseline_path, rec)
    gate = _FakeGate(fake_snapshot, violation_count=1)
    gate.execute()
    rec2 = _read_baseline(baseline_path)
    assert len(rec2["tighten_history"]) == 20
    # Most recent should be the new one (from=100, to=1).
    assert rec2["tighten_history"][-1]["to"] == 1


# --- W1.2 R->B auto-promotion -----------------------------------------


def test_auto_promote_after_three_zero_runs(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(baseline_path, {"gate_id": "TEST_FAKE_R", "count": 0})

    for run_idx in range(3):
        gate = _FakeGate(fake_snapshot, violation_count=0)
        result = gate.execute()
        assert result.status == "pass"
        rec = _read_baseline(baseline_path)
        assert rec["zero_run_streak"] == run_idx + 1
        if run_idx < 2:
            assert "auto_promoted_tier" not in rec

    final = _read_baseline(baseline_path)
    assert final["auto_promoted_tier"] == "B"
    assert final["auto_promoted_after_streak"] == 3


def test_non_zero_run_resets_streak(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 5,
            "zero_run_streak": 2,
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=3)
    gate.execute()
    rec = _read_baseline(baseline_path)
    assert rec["zero_run_streak"] == 0
    assert "auto_promoted_tier" not in rec


def test_promoted_gate_blocks_on_next_nonzero_run(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    # Start already promoted.
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 0,
            "auto_promoted_tier": "B",
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=1)
    result = gate.execute()
    # Effective tier is B; any violation -> fail
    assert result.status == "fail"
    assert result.tier == "B"
    assert result.summary["effective_tier"] == "B"
    assert result.summary["declared_tier"] == "R"


def test_promoted_gate_with_nonzero_absorbed_floor_stays_ratchet(
    fake_snapshot: Path, isolated_baseline_dir: Path
) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 1,
            "auto_promoted_tier": "B",
            "loosened_at": "2026-06-08T12:37:25+00:00",
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=1)
    result = gate.execute()
    assert result.status == "pass"
    assert result.tier == "R"
    assert "effective_tier" not in result.summary


def test_promoted_gate_passes_on_zero(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 0,
            "auto_promoted_tier": "B",
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=0)
    result = gate.execute()
    assert result.status == "pass"


def test_per_gate_threshold_override_via_json(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 0,
            "auto_promote_to_block_after_zero_runs": 1,
        },
    )
    gate = _FakeGate(fake_snapshot, violation_count=0)
    gate.execute()
    rec = _read_baseline(baseline_path)
    assert rec["auto_promoted_tier"] == "B"
    assert rec["auto_promoted_after_streak"] == 1


def test_promotion_disabled_when_threshold_zero(fake_snapshot: Path, isolated_baseline_dir: Path) -> None:
    baseline_path = isolated_baseline_dir / "test_fake_r_ratchet.json"
    _write_baseline(
        baseline_path,
        {
            "gate_id": "TEST_FAKE_R",
            "count": 0,
            "auto_promote_to_block_after_zero_runs": 0,
        },
    )
    for _ in range(5):
        _FakeGate(fake_snapshot, violation_count=0).execute()
    rec = _read_baseline(baseline_path)
    assert "auto_promoted_tier" not in rec
