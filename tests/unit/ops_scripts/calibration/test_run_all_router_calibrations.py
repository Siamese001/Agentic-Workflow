"""Tests for `ops_scripts/calibration/run_all_router_calibrations.py`.

Constitutional §28. Verifies all 10 routers are wired and the orchestrator
produces 10 reports under the SSOT path.
"""

from __future__ import annotations

import json

import pytest

from ops_scripts.calibration import _router_calibration_base as base
from ops_scripts.calibration import run_all_router_calibrations as orch


@pytest.fixture
def isolated_root(tmp_path, monkeypatch):
    """Redirect REPO_ROOT/LEDGERS_DIR/REPORT_BASE_DIR for isolation."""
    monkeypatch.setattr(base, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(base, "LEDGERS_DIR", tmp_path / "artifacts" / "ledgers")
    monkeypatch.setattr(
        base, "REPORT_BASE_DIR",
        tmp_path / "docs" / "reports" / "calibration" / "routers",
    )
    monkeypatch.setattr(orch, "REPO_ROOT", tmp_path)
    return tmp_path


class TestSpecRegistry:
    def test_all_specs_present(self) -> None:
        assert len(orch.ALL_SPECS) == 10

    def test_all_keys_unique(self) -> None:
        keys = [s.key for s in orch.ALL_SPECS]
        assert len(set(keys)) == 10

    def test_keys_match_constitutional_28(self) -> None:
        expected = {
            "L0_bandit", "L0_r5", "L1_c0", "L2_cascade",
            "L3_shape", "L3_reroute", "L4_uwg", "L5_hitl",
            "L6_promo", "L6_regret",
        }
        actual = {s.key for s in orch.ALL_SPECS}
        assert actual == expected

    def test_promo_carries_constitutional_floor_thresholds(self) -> None:
        promo = next(s for s in orch.ALL_SPECS if s.key == "L6_promo")
        assert promo.nominal_thresholds["wilson_lower_min"] == 0.60
        assert promo.nominal_thresholds["z_score_min"] == 1.96
        assert promo.nominal_thresholds["uplift_min"] == 0.0
        assert promo.nominal_thresholds["n_min"] == 30


class TestRunAll:
    def test_generates_10_reports(self, isolated_root) -> None:
        successes, failures = orch.run_all()
        assert len(successes) == 10
        assert failures == []

    def test_reports_at_ssot_paths(self, isolated_root) -> None:
        successes, _ = orch.run_all()
        for r in successes:
            assert r.output_path.exists()
            # Must be under the configured REPORT_BASE_DIR.
            assert "docs" in r.output_path.parts
            assert "calibration" in r.output_path.parts
            assert "routers" in r.output_path.parts
            assert r.spec_key in r.output_path.parts

    def test_all_marked_unavailable_when_no_ledgers(self, isolated_root) -> None:
        successes, _ = orch.run_all()
        for r in successes:
            assert not r.available

    def test_failure_is_collected_not_raised(self, isolated_root, monkeypatch) -> None:
        # Force generate() to fail for one spec only
        original = base.generate
        target_key = "L6_promo"

        def flaky(spec, *, now=None):
            if spec.key == target_key:
                raise OSError("synthetic failure")
            return original(spec, now=now)

        monkeypatch.setattr(orch, "generate", flaky)
        successes, failures = orch.run_all()
        assert len(successes) == 9
        assert len(failures) == 1
        assert failures[0][0] == target_key
        assert "synthetic" in failures[0][1]


class TestMain:
    def test_text_output_default(self, isolated_root, capsys) -> None:
        rc = orch.main([])
        assert rc == 0
        out = capsys.readouterr().out
        assert "10/10 reports" in out
        # Each router key should appear in the listing
        for spec in orch.ALL_SPECS:
            assert spec.key in out

    def test_json_output(self, isolated_root, capsys) -> None:
        rc = orch.main(["--json"])
        assert rc == 0
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["total_specs"] == 10
        assert len(payload["successes"]) == 10
        assert payload["failures"] == []

    def test_failures_yield_exit_two(self, isolated_root, monkeypatch, capsys) -> None:
        def boom(spec, *, now=None):
            raise OSError("disk")

        monkeypatch.setattr(orch, "generate", boom)
        rc = orch.main([])
        assert rc == 2
        out = capsys.readouterr().out
        assert "0/10 reports" in out
        assert "✗" in out
