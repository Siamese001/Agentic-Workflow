"""Unit tests for ops_scripts/ci/check_test_hotspot_coverage_ratchet.py (W6.2).

Plan: adg-testing-hotspots-wave-plan-a7f3c1 Wave 6 — the coverage ratchet gate.
Verifies advisory/init/monotonic/fail-closed/bypass behavior with a temp baseline
(never touches the committed baseline).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_GATE_PATH = Path(__file__).resolve().parents[4] / "ops_scripts" / "ci" / "check_test_hotspot_coverage_ratchet.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("ratchet_gate_under_test", _GATE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load_gate()


class TestPct:
    def test_basic(self) -> None:
        assert gate._pct(1, 2) == "50.0%"

    def test_zero_denominator(self) -> None:
        assert gate._pct(0, 0) == "n/a"


class TestMeasure:
    def test_measure_shape(self) -> None:
        m = gate._measure()
        assert set(m) == {"core_tested", "core_total", "apps_tested", "apps_total"}
        assert m["core_total"] > 0
        assert 0 <= m["core_tested"] <= m["core_total"]


class TestRatchetFlow:
    def test_init_then_monotonic_pass(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        bl = tmp_path / "baseline.json"
        monkeypatch.setattr(gate, "BASELINE", bl)
        assert gate.main(["--init"]) == 0
        assert bl.exists()
        assert gate.main([]) == 0  # current >= just-written baseline

    def test_regression_strict_fails_closed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        bl = tmp_path / "baseline.json"
        monkeypatch.setattr(gate, "BASELINE", bl)
        gate.main(["--init"])
        d = json.loads(bl.read_text())
        d["core_tested"] += 1_000_000  # force a regression
        bl.write_text(json.dumps(d))
        assert gate.main(["--strict"]) == 1

    def test_regression_advisory_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        bl = tmp_path / "baseline.json"
        monkeypatch.setattr(gate, "BASELINE", bl)
        monkeypatch.delenv("TEST_HOTSPOT_RATCHET_FAIL_CLOSED", raising=False)
        gate.main(["--init"])
        d = json.loads(bl.read_text())
        d["core_tested"] += 1_000_000
        bl.write_text(json.dumps(d))
        assert gate.main([]) == 0  # advisory: regression does not fail

    def test_env_fail_closed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        bl = tmp_path / "baseline.json"
        monkeypatch.setattr(gate, "BASELINE", bl)
        gate.main(["--init"])
        d = json.loads(bl.read_text())
        d["apps_tested"] += 1_000_000
        bl.write_text(json.dumps(d))
        monkeypatch.setenv("TEST_HOTSPOT_RATCHET_FAIL_CLOSED", "1")
        assert gate.main([]) == 1

    def test_bypass_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TEST_HOTSPOT_RATCHET_BYPASS", "1")
        assert gate.main([]) == 0

    def test_missing_baseline_is_advisory_pass(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gate, "BASELINE", tmp_path / "absent.json")
        monkeypatch.delenv("TEST_HOTSPOT_RATCHET_FAIL_CLOSED", raising=False)
        assert gate.main([]) == 0
