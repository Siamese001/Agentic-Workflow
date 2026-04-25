"""Unit tests for ops_scripts.ci._adg_wiring_gate_base.

Targets Wave-2 / Phase P4. Source: 429 lines, fan_in=172 (L_OPS, impact 129.0) —
second highest fan-in in top 15.
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sqlite3
import sys
from dataclasses import fields
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
_MOD_PATH = REPO_ROOT / "ops_scripts" / "ci" / "_adg_wiring_gate_base.py"


def _import_gate_base():
    """Import the underscore-prefixed module by path (can't be imported as a package member)."""
    spec = importlib.util.spec_from_file_location("_adg_wiring_gate_base_test", _MOD_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_adg_wiring_gate_base_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gate_mod():
    return _import_gate_base()


@pytest.fixture
def fake_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, gate_mod):
    """Create a minimal SQLite snapshot in tmp and point ADG_SNAPSHOT at it."""
    snap = tmp_path / "adg_indexed_test.sqlite"
    conn = sqlite3.connect(snap)
    conn.execute("CREATE TABLE nodes (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO nodes VALUES (1, 'sample')")
    conn.commit()
    conn.close()
    monkeypatch.setenv("ADG_SNAPSHOT", str(snap))
    return snap


class TestViolationDataclass:
    def test_minimal_construction(self, gate_mod) -> None:
        v = gate_mod.Violation(gate_id="G1", tier="B", subject="mod.py", rule="r", detail="d")
        assert v.gate_id == "G1"
        assert v.severity == "fail"
        assert v.extra == {}

    def test_with_extras(self, gate_mod) -> None:
        v = gate_mod.Violation(
            gate_id="G1",
            tier="R",
            subject="x.py",
            rule="r",
            detail="d",
            severity="warn",
            extra={"count": 5},
        )
        assert v.extra["count"] == 5

    def test_independent_extras(self, gate_mod) -> None:
        v1 = gate_mod.Violation(gate_id="G", tier="B", subject="x", rule="r", detail="d")
        v2 = gate_mod.Violation(gate_id="G", tier="B", subject="x", rule="r", detail="d")
        v1.extra["a"] = 1
        assert "a" not in v2.extra


class TestGateResultDataclass:
    def test_minimal_construction(self, gate_mod) -> None:
        r = gate_mod.GateResult(
            gate_id="G1",
            tier="B",
            snapshot="s.sqlite",
            timestamp="2026-01-01T00:00:00+00:00",
            status="pass",
            violations=[],
        )
        assert r.status == "pass"
        assert r.baseline_count is None
        assert r.summary == {}


class TestLatestSnapshot:
    def test_honors_env_override(self, tmp_path, monkeypatch, gate_mod) -> None:
        snap = tmp_path / "override.sqlite"
        snap.write_bytes(b"")
        monkeypatch.setenv("ADG_SNAPSHOT", str(snap))
        result = gate_mod.latest_snapshot()
        assert result.resolve() == snap.resolve()

    def test_raises_when_override_missing(self, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setenv("ADG_SNAPSHOT", str(tmp_path / "nope.sqlite"))
        with pytest.raises(FileNotFoundError, match="ADG_SNAPSHOT"):
            gate_mod.latest_snapshot()

    def test_picks_most_recently_modified(self, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.delenv("ADG_SNAPSHOT", raising=False)
        # Redirect ADG_DIR to tmp_path
        monkeypatch.setattr(gate_mod, "ADG_DIR", tmp_path)
        import os as _os
        import time as _time

        older = tmp_path / "adg_indexed_aaa.sqlite"
        older.write_bytes(b"")
        _time.sleep(0.05)
        newer = tmp_path / "adg_indexed_zzz.sqlite"
        newer.write_bytes(b"")
        result = gate_mod.latest_snapshot()
        assert result.resolve() == newer.resolve()

    def test_raises_when_no_snapshots_present(self, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.delenv("ADG_SNAPSHOT", raising=False)
        monkeypatch.setattr(gate_mod, "ADG_DIR", tmp_path)
        with pytest.raises(FileNotFoundError, match="no adg_indexed"):
            gate_mod.latest_snapshot()


class TestWaiverMatching:
    def test_entry_active_for_matching_scope_star(self, gate_mod) -> None:
        entry = {"gate": "G1", "scope": "*", "expires_on": "2099-01-01"}
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for(entry, "G1", "any_subject", today) is True

    def test_entry_active_for_exact_scope_match(self, gate_mod) -> None:
        entry = {"gate": "G1", "scope": "mod.py", "expires_on": "2099-01-01"}
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for(entry, "G1", "mod.py", today) is True

    def test_entry_active_for_suffix_match(self, gate_mod) -> None:
        entry = {"gate": "G1", "scope": "mod.py", "expires_on": "2099-01-01"}
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for(entry, "G1", "pkg/mod.py", today) is True

    def test_entry_active_for_rejects_expired(self, gate_mod) -> None:
        entry = {"gate": "G1", "scope": "*", "expires_on": "2020-01-01"}
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for(entry, "G1", "x", today) is False

    def test_entry_active_for_wrong_gate(self, gate_mod) -> None:
        entry = {"gate": "G2", "scope": "*", "expires_on": "2099-01-01"}
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for(entry, "G1", "x", today) is False

    def test_entry_active_for_malformed_date(self, gate_mod) -> None:
        entry = {"gate": "G1", "scope": "*", "expires_on": "not-a-date"}
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for(entry, "G1", "x", today) is False

    def test_entry_active_for_non_dict_entry(self, gate_mod) -> None:
        today = _dt.date(2026, 1, 1)
        assert gate_mod._entry_active_for("not-a-dict", "G1", "x", today) is False
        assert gate_mod._entry_active_for(None, "G1", "x", today) is False

    def test_waiver_matches_empty(self, gate_mod) -> None:
        assert gate_mod._waiver_matches({}, "G1", "x") is False

    def test_waiver_matches_with_active_entry(self, gate_mod) -> None:
        waivers = {"waivers": [{"gate": "G1", "scope": "*", "expires_on": "2099-01-01"}]}
        assert gate_mod._waiver_matches(waivers, "G1", "anything") is True

    def test_waiver_matches_rejects_non_dict_input(self, gate_mod) -> None:
        assert gate_mod._waiver_matches(None, "G1", "x") is False


class TestWiringGateHarness:
    """Minimal concrete gate exercising the execute() harness."""

    def _make_gate_class(self, gate_mod, *, tier="B", violations=None, gate_id="TEST_GATE"):
        viols = list(violations or [])

        class _TestGate(gate_mod.WiringGate):
            pass

        _TestGate.gate_id = gate_id
        _TestGate.tier = tier
        _TestGate.baseline_filename = None
        # Define run in the class dict BEFORE instantiation so ABC's
        # __abstractmethods__ check clears it.
        _TestGate.run = lambda self, conn: list(viols)  # type: ignore[assignment]
        _TestGate.__abstractmethods__ = frozenset()
        return _TestGate

    def test_blocking_gate_passes_when_no_violations(
        self, fake_snapshot, tmp_path, monkeypatch, gate_mod
    ) -> None:
        monkeypatch.setattr(gate_mod, "LOG_FILE", tmp_path / "viol.jsonl")
        monkeypatch.setattr(gate_mod, "LOG_DIR", tmp_path)
        GateCls = self._make_gate_class(gate_mod, tier="B", violations=[])
        result = GateCls().execute()
        assert result.status == "pass"
        assert result.violations == []
        assert result.summary["raw_count"] == 0

    def test_blocking_gate_fails_with_violation(self, fake_snapshot, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setattr(gate_mod, "LOG_FILE", tmp_path / "viol.jsonl")
        monkeypatch.setattr(gate_mod, "LOG_DIR", tmp_path)
        v = gate_mod.Violation(gate_id="TEST_GATE", tier="B", subject="mod.py", rule="r", detail="d")
        GateCls = self._make_gate_class(gate_mod, tier="B", violations=[v])
        result = GateCls().execute()
        assert result.status == "fail"
        assert len(result.violations) == 1

    def test_bypass_env_short_circuits(self, fake_snapshot, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setattr(gate_mod, "LOG_FILE", tmp_path / "viol.jsonl")
        monkeypatch.setattr(gate_mod, "LOG_DIR", tmp_path)
        monkeypatch.setenv("WIRING_GATE_BYPASS", "1")
        v = gate_mod.Violation(gate_id="TEST_GATE", tier="B", subject="mod.py", rule="r", detail="d")
        GateCls = self._make_gate_class(gate_mod, tier="B", violations=[v])
        result = GateCls().execute()
        assert result.status == "bypass"
        assert result.violations == []
        assert result.summary["reason"] == "WIRING_GATE_BYPASS=1"

    def test_warn_tier_never_blocks(self, fake_snapshot, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setattr(gate_mod, "LOG_FILE", tmp_path / "viol.jsonl")
        monkeypatch.setattr(gate_mod, "LOG_DIR", tmp_path)
        v = gate_mod.Violation(gate_id="TEST_GATE", tier="W", subject="x.py", rule="r", detail="d")
        GateCls = self._make_gate_class(gate_mod, tier="W", violations=[v])
        result = GateCls().execute()
        assert result.status == "warn"

    def test_kpi_tier_always_pass(self, fake_snapshot, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setattr(gate_mod, "LOG_FILE", tmp_path / "viol.jsonl")
        monkeypatch.setattr(gate_mod, "LOG_DIR", tmp_path)
        v = gate_mod.Violation(gate_id="TEST_GATE", tier="K", subject="x.py", rule="r", detail="d")
        GateCls = self._make_gate_class(gate_mod, tier="K", violations=[v])
        result = GateCls().execute()
        assert result.status == "pass"


class TestRatchetBaseline:
    def test_baseline_count_returns_zero_when_file_missing(self, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setattr(gate_mod, "BASELINE_DIR", tmp_path)

        class _TestGate(gate_mod.WiringGate):
            gate_id = "G"
            tier = "R"
            baseline_filename = "g.json"

            def run(self, conn):
                return []

        # Need a snapshot for __init__
        snap = tmp_path / "adg_indexed_x.sqlite"
        snap.write_bytes(b"")
        g = _TestGate(snapshot=snap)
        assert g._baseline_count() == 0

    def test_seed_baseline_writes_json_with_count(self, tmp_path, monkeypatch, gate_mod) -> None:
        monkeypatch.setattr(gate_mod, "BASELINE_DIR", tmp_path)

        class _TestGate(gate_mod.WiringGate):
            gate_id = "SEED_GATE"
            tier = "R"
            baseline_filename = "seed.json"

            def run(self, conn):
                return []

        snap = tmp_path / "adg_indexed_x.sqlite"
        snap.write_bytes(b"")
        g = _TestGate(snapshot=snap)
        g.seed_baseline(42)
        data = json.loads((tmp_path / "seed.json").read_text(encoding="utf-8"))
        assert data["count"] == 42
        assert data["gate_id"] == "SEED_GATE"


class TestConnectSnapshot:
    def test_connects_readonly_uri(self, tmp_path, gate_mod) -> None:
        snap = tmp_path / "test.sqlite"
        c = sqlite3.connect(snap)
        c.execute("CREATE TABLE x (n INTEGER)")
        c.execute("INSERT INTO x VALUES (1)")
        c.commit()
        c.close()
        conn = gate_mod.connect_snapshot(snap)
        try:
            cur = conn.execute("SELECT n FROM x")
            assert cur.fetchone() == (1,)
            # Readonly — attempting a write should raise OperationalError
            with pytest.raises(sqlite3.OperationalError):
                conn.execute("INSERT INTO x VALUES (2)")
        finally:
            conn.close()
