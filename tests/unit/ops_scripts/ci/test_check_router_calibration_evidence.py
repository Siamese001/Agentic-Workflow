"""Tests for `ops_scripts/ci/check_router_calibration_evidence.py`.

Constitutional §28 / closed-loop-router-enforcement.md.
Refuses to pass if a router-implementing file changed without a fresh
calibration report.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / "ops_scripts" / "ci" / "check_router_calibration_evidence.py"


def _load_module():
    # Register in sys.modules BEFORE exec so @dataclass annotations resolve.
    spec = importlib.util.spec_from_file_location("check_router_calibration_evidence", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gate():
    return _load_module()


# ---------------------------------------------------------------------------
# Glob → regex translation
# ---------------------------------------------------------------------------


class TestGlobToRegex:
    def test_double_star_matches_zero_segments(self, gate):
        rx = gate._glob_to_regex("agentic_core/L0_routing/**/*bandit*.py")
        assert rx.match("agentic_core/L0_routing/bandit.py")
        assert rx.match("agentic_core/L0_routing/sub/dir/bandit_v2.py")

    def test_single_star_does_not_cross_segment(self, gate):
        rx = gate._glob_to_regex("agentic_core/L0_routing/*.py")
        assert rx.match("agentic_core/L0_routing/foo.py")
        assert not rx.match("agentic_core/L0_routing/sub/foo.py")

    def test_special_chars_escaped(self, gate):
        rx = gate._glob_to_regex("foo.bar+baz")
        assert rx.match("foo.bar+baz")
        assert not rx.match("foo_bar+baz")

    def test_question_mark_matches_one_char(self, gate):
        rx = gate._glob_to_regex("a?c.py")
        assert rx.match("abc.py")
        assert not rx.match("ac.py")
        assert not rx.match("a/c.py")


# ---------------------------------------------------------------------------
# Glob hits in router specs
# ---------------------------------------------------------------------------


class TestRouterSpecMatching:
    def test_promo_path_matches_l6_promo_router(self, gate):
        promo_router = next(r for r in gate.ROUTERS if r.key == "L6_promo")
        assert gate._matches_any_glob(
            "agentic_core/L6_observability/flywheel_promoter.py",
            promo_router.file_globs,
        )

    def test_regret_path_matches_l6_regret(self, gate):
        regret = next(r for r in gate.ROUTERS if r.key == "L6_regret")
        assert gate._matches_any_glob(
            "agentic_core/L6_observability/regret_accounting.py",
            regret.file_globs,
        )

    def test_unrelated_path_does_not_match(self, gate):
        bandit = next(r for r in gate.ROUTERS if r.key == "L0_bandit")
        assert not gate._matches_any_glob(
            "tools/generate_full_adg.py",
            bandit.file_globs,
        )

    def test_ten_routers_total(self, gate):
        # SSOT — must align with §28 / closed-loop-router-enforcement.md.
        assert len(gate.ROUTERS) == 10
        keys = sorted(r.key for r in gate.ROUTERS)
        assert keys == sorted(
            [
                "L0_bandit",
                "L0_r5",
                "L1_c0",
                "L2_cascade",
                "L3_shape",
                "L3_reroute",
                "L4_uwg",
                "L5_hitl",
                "L6_promo",
                "L6_regret",
            ]
        )


# ---------------------------------------------------------------------------
# Calibration freshness
# ---------------------------------------------------------------------------


class TestCalibrationFreshness:
    def test_missing_dir_returns_not_fresh(self, gate, tmp_path, monkeypatch):
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path / "no_dir")
        router = next(r for r in gate.ROUTERS if r.key == "L0_bandit")
        is_fresh, latest = gate._has_fresh_calibration_report(router, fresh_days=14)
        assert not is_fresh
        assert latest is None

    def test_empty_dir_returns_not_fresh(self, gate, tmp_path, monkeypatch):
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path)
        router = next(r for r in gate.ROUTERS if r.key == "L0_bandit")
        (tmp_path / router.key).mkdir()
        is_fresh, latest = gate._has_fresh_calibration_report(router, fresh_days=14)
        assert not is_fresh
        assert latest is None

    def test_recent_report_is_fresh(self, gate, tmp_path, monkeypatch):
        monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path / "calib")
        router = next(r for r in gate.ROUTERS if r.key == "L0_bandit")
        rdir = tmp_path / "calib" / router.key
        rdir.mkdir(parents=True)
        report = rdir / "2026-W17.md"
        report.write_text("# fresh", encoding="utf-8")
        is_fresh, latest = gate._has_fresh_calibration_report(router, fresh_days=14)
        assert is_fresh
        assert latest is not None
        assert latest.endswith("2026-W17.md")

    def test_stale_report_not_fresh(self, gate, tmp_path, monkeypatch):
        monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path / "calib")
        router = next(r for r in gate.ROUTERS if r.key == "L0_bandit")
        rdir = tmp_path / "calib" / router.key
        rdir.mkdir(parents=True)
        report = rdir / "old.md"
        report.write_text("# old", encoding="utf-8")
        # Backdate to 60 days ago
        old_ts = (datetime.now() - timedelta(days=60)).timestamp()
        os.utime(report, (old_ts, old_ts))
        is_fresh, latest = gate._has_fresh_calibration_report(router, fresh_days=14)
        assert not is_fresh
        assert latest is not None  # latest path returned, but not fresh


# ---------------------------------------------------------------------------
# audit() — full round-trip
# ---------------------------------------------------------------------------


class TestAudit:
    def test_no_changes_yields_no_violations(self, gate, monkeypatch):
        monkeypatch.setattr(gate, "_git_changed_files", lambda days: set())
        violations = gate.audit(window_days=7, fresh_days=14)
        assert violations == []

    def test_router_change_with_fresh_report_passes(self, gate, monkeypatch, tmp_path):
        monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path / "calib")
        promo_dir = tmp_path / "calib" / "L6_promo"
        promo_dir.mkdir(parents=True)
        (promo_dir / "fresh.md").write_text("# ok", encoding="utf-8")
        monkeypatch.setattr(
            gate,
            "_git_changed_files",
            lambda days: {
                "agentic_core/L6_observability/flywheel_promoter.py",
            },
        )
        violations = gate.audit(window_days=7, fresh_days=14)
        assert violations == []

    def test_router_change_without_report_violates(self, gate, monkeypatch, tmp_path):
        monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path / "calib")
        # No calibration directory at all.
        monkeypatch.setattr(
            gate,
            "_git_changed_files",
            lambda days: {
                "agentic_core/L6_observability/regret_accounting.py",
            },
        )
        violations = gate.audit(window_days=7, fresh_days=14)
        assert len(violations) == 1
        assert violations[0].router_key == "L6_regret"
        assert "no calibration report" in violations[0].reason

    def test_router_change_with_stale_report_violates(self, gate, monkeypatch, tmp_path):
        monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(gate, "CALIBRATION_DIR", tmp_path / "calib")
        rdir = tmp_path / "calib" / "L6_regret"
        rdir.mkdir(parents=True)
        old = rdir / "old.md"
        old.write_text("# stale", encoding="utf-8")
        old_ts = (datetime.now() - timedelta(days=60)).timestamp()
        os.utime(old, (old_ts, old_ts))
        monkeypatch.setattr(
            gate,
            "_git_changed_files",
            lambda days: {
                "agentic_core/L6_observability/regret_accounting.py",
            },
        )
        violations = gate.audit(window_days=7, fresh_days=14)
        assert len(violations) == 1
        assert "older than 14 days" in violations[0].reason

    def test_unrelated_change_no_violation(self, gate, monkeypatch):
        monkeypatch.setattr(
            gate,
            "_git_changed_files",
            lambda days: {
                "tools/generate_full_adg.py",
                "docs/reference/something.md",
            },
        )
        violations = gate.audit(window_days=7, fresh_days=14)
        assert violations == []


# ---------------------------------------------------------------------------
# main() — CLI behavior
# ---------------------------------------------------------------------------


class TestMain:
    def test_advisory_mode_returns_zero_with_violations(self, gate, monkeypatch, capsys):
        monkeypatch.setenv("ROUTER_CI_GATE_MODE", "advisory")
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        monkeypatch.setattr(
            gate,
            "audit",
            lambda *a, **kw: [
                gate.RouterViolation(
                    router_key="L6_promo",
                    changed_files=("agentic_core/L6_observability/flywheel_promoter.py",),
                    latest_report=None,
                    reason="no calibration report",
                ),
            ],
        )
        rc = gate.main([])
        out = capsys.readouterr().out
        assert rc == 0
        assert "L6_promo" in out
        assert "no calibration report" in out

    def test_strict_mode_returns_one_with_violations(self, gate, monkeypatch, capsys):
        monkeypatch.setenv("ROUTER_CI_GATE_MODE", "strict")
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        monkeypatch.setattr(
            gate,
            "audit",
            lambda *a, **kw: [
                gate.RouterViolation(
                    router_key="L6_regret",
                    changed_files=("agentic_core/L6_observability/regret_accounting.py",),
                    latest_report=None,
                    reason="no calibration report",
                ),
            ],
        )
        rc = gate.main([])
        assert rc == 1
        out = capsys.readouterr().out
        assert "L6_regret" in out

    def test_strict_no_violations_returns_zero(self, gate, monkeypatch, capsys):
        monkeypatch.setenv("ROUTER_CI_GATE_MODE", "strict")
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        monkeypatch.setattr(gate, "audit", lambda *a, **kw: [])
        rc = gate.main([])
        assert rc == 0
        assert "OK" in capsys.readouterr().out

    def test_bypass_short_circuits(self, gate, monkeypatch, capsys):
        monkeypatch.setenv("ROUTER_ENFORCEMENT_BYPASS", "1")
        monkeypatch.setenv("ROUTER_CI_GATE_MODE", "strict")
        # Even with violations, bypass returns 0 BEFORE audit runs.
        called = {"audit": 0}

        def boom(*a, **kw):
            called["audit"] += 1
            raise AssertionError("audit should not run when bypass is active")

        monkeypatch.setattr(gate, "audit", boom)
        rc = gate.main([])
        assert rc == 0
        assert called["audit"] == 0
        assert "BYPASS" in capsys.readouterr().out

    def test_invalid_mode_falls_back_to_advisory(self, gate, monkeypatch, capsys):
        monkeypatch.setenv("ROUTER_CI_GATE_MODE", "garbage")
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        monkeypatch.setattr(
            gate,
            "audit",
            lambda *a, **kw: [
                gate.RouterViolation(
                    router_key="L0_bandit",
                    changed_files=("x.py",),
                    latest_report=None,
                    reason="r",
                ),
            ],
        )
        rc = gate.main([])
        assert rc == 0  # advisory fallback
        assert "mode=advisory" in capsys.readouterr().out
