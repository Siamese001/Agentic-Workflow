"""Tests for ADG CI gates evaluators (M1–M12).

Tests each gate evaluator in isolation with synthetic cur/base dicts.
No Redis or filesystem dependencies — pure unit tests.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure repo root is importable
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ops_scripts.ci._adg_ci_gates import (
    ANTIPATTERN_MAX_INCREASE_PCT,
    DEAD_IMPORT_MAX_INCREASE,
    GATE_DEFS,
    GUARDRAIL_COVERAGE_THRESHOLD,
    LAYER_VIOLATION_MAX,
    POLICY_GUARDRAIL_MIN_EDGES,
    ROUTES_PATH_MIN_EDGES,
    TRACE_COVERAGE_THRESHOLD,
    TRACE_MIN_EDGES,
    _EVALUATORS,
    _eval_m1,
    _eval_m2,
    _eval_m3,
    _eval_m4,
    _eval_m5,
    _eval_m6,
    _eval_m7,
    _eval_m8,
    _eval_m9,
    _eval_m10,
    _eval_m11,
    _eval_m12,
)


# ---------------------------------------------------------------------------
# M1 — Determinism Gate
# ---------------------------------------------------------------------------


class TestM1DeterminismGate:
    """M1: uses_wall_clock must not increase unless determinism injection present."""

    def test_pass_no_change(self):
        cur = {"uses_wall_clock": 10, "emits_determinism_digest": 5, "seeds_rng": 0}
        base = {"uses_wall_clock": 10, "emits_determinism_digest": 5, "seeds_rng": 0}
        passed, msg = _eval_m1(cur, base)
        assert passed is True
        assert "OK" in msg

    def test_pass_wall_clock_increase_with_determinism(self):
        cur = {"uses_wall_clock": 12, "emits_determinism_digest": 7, "seeds_rng": 0}
        base = {"uses_wall_clock": 10, "emits_determinism_digest": 5, "seeds_rng": 0}
        passed, msg = _eval_m1(cur, base)
        assert passed is True

    def test_pass_wall_clock_increase_with_rng_seed(self):
        cur = {"uses_wall_clock": 12, "emits_determinism_digest": 5, "seeds_rng": 2}
        base = {"uses_wall_clock": 10, "emits_determinism_digest": 5, "seeds_rng": 0}
        passed, msg = _eval_m1(cur, base)
        assert passed is True

    def test_fail_wall_clock_increase_no_injection(self):
        cur = {"uses_wall_clock": 15, "emits_determinism_digest": 5, "seeds_rng": 0}
        base = {"uses_wall_clock": 10, "emits_determinism_digest": 5, "seeds_rng": 0}
        passed, msg = _eval_m1(cur, base)
        assert passed is False
        assert "+5" in msg

    def test_pass_wall_clock_decrease(self):
        cur = {"uses_wall_clock": 8, "emits_determinism_digest": 5, "seeds_rng": 0}
        base = {"uses_wall_clock": 10, "emits_determinism_digest": 5, "seeds_rng": 0}
        passed, msg = _eval_m1(cur, base)
        assert passed is True

    def test_pass_empty_dicts(self):
        passed, msg = _eval_m1({}, {})
        assert passed is True


# ---------------------------------------------------------------------------
# M2 — Dispatch Visibility Gate
# ---------------------------------------------------------------------------


class TestM2DispatchVisibilityGate:
    """M2: getattr_dynamic must not increase unless typed dispatch added."""

    def test_pass_no_change(self):
        cur = {"invokes_getattr_dynamic": 5, "agent_executes_agent": 3}
        base = {"invokes_getattr_dynamic": 5, "agent_executes_agent": 3}
        passed, msg = _eval_m2(cur, base)
        assert passed is True

    def test_fail_getattr_increase_no_typed_dispatch(self):
        cur = {"invokes_getattr_dynamic": 8, "agent_executes_agent": 3}
        base = {"invokes_getattr_dynamic": 5, "agent_executes_agent": 3}
        passed, msg = _eval_m2(cur, base)
        assert passed is False
        assert "+3" in msg

    def test_pass_getattr_increase_with_typed_dispatch(self):
        cur = {"invokes_getattr_dynamic": 8, "agent_executes_agent": 6}
        base = {"invokes_getattr_dynamic": 5, "agent_executes_agent": 3}
        passed, msg = _eval_m2(cur, base)
        assert passed is True

    def test_pass_getattr_decrease(self):
        cur = {"invokes_getattr_dynamic": 3, "agent_executes_agent": 3}
        base = {"invokes_getattr_dynamic": 5, "agent_executes_agent": 3}
        passed, msg = _eval_m2(cur, base)
        assert passed is True


# ---------------------------------------------------------------------------
# M3 — Mutation Sovereignty Gate
# ---------------------------------------------------------------------------


class TestM3MutationSovereigntyGate:
    """M3: writes_to must not increase unless writes_through also increases."""

    def test_pass_no_change(self):
        cur = {"writes_to": 100, "writes_through": 50}
        base = {"writes_to": 100, "writes_through": 50}
        passed, msg = _eval_m3(cur, base)
        assert passed is True

    def test_fail_writes_increase_no_uwg(self):
        cur = {"writes_to": 110, "writes_through": 50}
        base = {"writes_to": 100, "writes_through": 50}
        passed, msg = _eval_m3(cur, base)
        assert passed is False
        assert "+10" in msg

    def test_pass_writes_increase_with_uwg(self):
        cur = {"writes_to": 110, "writes_through": 55}
        base = {"writes_to": 100, "writes_through": 50}
        passed, msg = _eval_m3(cur, base)
        assert passed is True

    def test_pass_writes_decrease(self):
        cur = {"writes_to": 90, "writes_through": 50}
        base = {"writes_to": 100, "writes_through": 50}
        passed, msg = _eval_m3(cur, base)
        assert passed is True


# ---------------------------------------------------------------------------
# M4 — Guardrail Coverage Gate
# ---------------------------------------------------------------------------


class TestM4GuardrailCoverageGate:
    """M4: applies_guardrail / calls >= threshold."""

    def test_pass_above_threshold(self):
        cur = {"applies_guardrail": 20, "calls": 100}
        passed, msg = _eval_m4(cur, {})
        assert passed is True
        assert "0.2000" in msg

    def test_fail_below_threshold(self):
        cur = {"applies_guardrail": 5, "calls": 100}
        passed, msg = _eval_m4(cur, {})
        assert passed is False
        assert f"{GUARDRAIL_COVERAGE_THRESHOLD}" in msg

    def test_pass_zero_calls(self):
        cur = {"applies_guardrail": 0, "calls": 0}
        passed, msg = _eval_m4(cur, {})
        assert passed is False  # 0/0 = 0 < threshold

    def test_pass_at_threshold(self):
        cur = {"applies_guardrail": 10, "calls": 100}
        passed, msg = _eval_m4(cur, {})
        assert passed is True  # 10/100 = 0.10 == threshold


# ---------------------------------------------------------------------------
# M5 — Trace Coverage Gate
# ---------------------------------------------------------------------------


class TestM5TraceCoverageGate:
    """M5: records_execution_trace / (calls + invokes_eval) >= threshold."""

    def test_pass_above_threshold(self):
        cur = {"records_execution_trace": 10, "calls": 100, "invokes_eval": 50}
        passed, msg = _eval_m5(cur, {})
        assert passed is True

    def test_fail_below_threshold(self):
        cur = {"records_execution_trace": 1, "calls": 100, "invokes_eval": 50}
        passed, msg = _eval_m5(cur, {})
        assert passed is False

    def test_pass_zero_denominator(self):
        cur = {"records_execution_trace": 0, "calls": 0, "invokes_eval": 0}
        passed, msg = _eval_m5(cur, {})
        assert passed is False  # 0/0 = 0 < threshold


# ---------------------------------------------------------------------------
# M6 — Replay Key Gate
# ---------------------------------------------------------------------------


class TestM6ReplayKeyGate:
    """M6: emits_replay_key must not decrease."""

    def test_pass_no_change(self):
        cur = {"emits_replay_key": 5}
        base = {"emits_replay_key": 5}
        passed, msg = _eval_m6(cur, base)
        assert passed is True

    def test_pass_increase(self):
        cur = {"emits_replay_key": 8}
        base = {"emits_replay_key": 5}
        passed, msg = _eval_m6(cur, base)
        assert passed is True

    def test_fail_decrease(self):
        cur = {"emits_replay_key": 3}
        base = {"emits_replay_key": 5}
        passed, msg = _eval_m6(cur, base)
        assert passed is False
        assert "regressed" in msg


# ---------------------------------------------------------------------------
# M7 — Routes Path Edge Count Gate
# ---------------------------------------------------------------------------


class TestM7RoutesPathGate:
    """M7: routes_path edges >= minimum."""

    def test_pass_above_min(self):
        cur = {"routes_path": ROUTES_PATH_MIN_EDGES + 10}
        passed, msg = _eval_m7(cur, {})
        assert passed is True

    def test_fail_below_min(self):
        cur = {"routes_path": ROUTES_PATH_MIN_EDGES - 1}
        passed, msg = _eval_m7(cur, {})
        assert passed is False

    def test_pass_at_min(self):
        cur = {"routes_path": ROUTES_PATH_MIN_EDGES}
        passed, msg = _eval_m7(cur, {})
        assert passed is True


# ---------------------------------------------------------------------------
# M8 — Guardrail Coverage Min Gate
# ---------------------------------------------------------------------------


class TestM8GuardrailMinGate:
    """M8: applies_guardrail edges >= minimum."""

    def test_pass_above_min(self):
        cur = {"applies_guardrail": POLICY_GUARDRAIL_MIN_EDGES + 10}
        passed, msg = _eval_m8(cur, {})
        assert passed is True

    def test_fail_below_min(self):
        cur = {"applies_guardrail": POLICY_GUARDRAIL_MIN_EDGES - 1}
        passed, msg = _eval_m8(cur, {})
        assert passed is False


# ---------------------------------------------------------------------------
# M9 — Trace Min Edges Gate
# ---------------------------------------------------------------------------


class TestM9TraceMinEdgesGate:
    """M9: records_execution_trace edges >= minimum."""

    def test_pass_above_min(self):
        cur = {"records_execution_trace": TRACE_MIN_EDGES + 10}
        passed, msg = _eval_m9(cur, {})
        assert passed is True

    def test_fail_below_min(self):
        cur = {"records_execution_trace": TRACE_MIN_EDGES - 1}
        passed, msg = _eval_m9(cur, {})
        assert passed is False


# ---------------------------------------------------------------------------
# M10 — Antipattern Regression Gate
# ---------------------------------------------------------------------------


class TestM10AntipatternRegressionGate:
    """M10: antipattern count must not increase by more than 5% over baseline."""

    def test_pass_no_change(self):
        cur = {"antipattern": 1000}
        base = {"antipattern": 1000}
        passed, msg = _eval_m10(cur, base)
        assert passed is True
        assert "delta=+0" in msg

    def test_pass_small_increase_within_threshold(self):
        cur = {"antipattern": 1040}
        base = {"antipattern": 1000}
        passed, msg = _eval_m10(cur, base)
        assert passed is True  # +4% < 5%

    def test_fail_large_increase_over_threshold(self):
        cur = {"antipattern": 1060}
        base = {"antipattern": 1000}
        passed, msg = _eval_m10(cur, base)
        assert passed is False  # +6% > 5%
        assert "+60" in msg
        assert "6.0%" in msg

    def test_pass_decrease(self):
        cur = {"antipattern": 800}
        base = {"antipattern": 1000}
        passed, msg = _eval_m10(cur, base)
        assert passed is True

    def test_pass_zero_baseline(self):
        cur = {"antipattern": 100}
        base = {"antipattern": 0}
        passed, msg = _eval_m10(cur, base)
        assert passed is True  # no baseline — skip

    def test_fail_exactly_at_boundary(self):
        # 5% of 1000 = 50. At +51 it should fail.
        cur = {"antipattern": 1051}
        base = {"antipattern": 1000}
        passed, msg = _eval_m10(cur, base)
        assert passed is False

    def test_pass_at_boundary(self):
        # +50 = exactly 5.0% — not > 5%, so pass
        cur = {"antipattern": 1050}
        base = {"antipattern": 1000}
        passed, msg = _eval_m10(cur, base)
        assert passed is True

    def test_pass_empty_dicts(self):
        passed, msg = _eval_m10({}, {})
        assert passed is True  # base=0 → skip


# ---------------------------------------------------------------------------
# M11 — Dead Import Regression Gate
# ---------------------------------------------------------------------------


class TestM11DeadImportRegressionGate:
    """M11: dead_imports must not increase by more than max allowed."""

    def test_pass_no_change(self):
        cur = {"dead_imports": 100}
        base = {"dead_imports": 100}
        passed, msg = _eval_m11(cur, base)
        assert passed is True

    def test_pass_small_increase(self):
        cur = {"dead_imports": 105}
        base = {"dead_imports": 100}
        passed, msg = _eval_m11(cur, base)
        assert passed is True  # +5 < 10

    def test_fail_large_increase(self):
        cur = {"dead_imports": 115}
        base = {"dead_imports": 100}
        passed, msg = _eval_m11(cur, base)
        assert passed is False  # +15 > 10
        assert "+15" in msg

    def test_pass_at_boundary(self):
        cur = {"dead_imports": 110}
        base = {"dead_imports": 100}
        passed, msg = _eval_m11(cur, base)
        assert passed is True  # +10 == max, not > max

    def test_fail_one_over_boundary(self):
        cur = {"dead_imports": 111}
        base = {"dead_imports": 100}
        passed, msg = _eval_m11(cur, base)
        assert passed is False  # +11 > 10

    def test_pass_decrease(self):
        cur = {"dead_imports": 90}
        base = {"dead_imports": 100}
        passed, msg = _eval_m11(cur, base)
        assert passed is True


# ---------------------------------------------------------------------------
# M12 — Layer Gravity Gate
# ---------------------------------------------------------------------------


class TestM12LayerGravityGate:
    """M12: layer_violation_count must stay at zero."""

    def test_pass_zero_violations(self):
        cur = {"layer_violation_count": 0}
        passed, msg = _eval_m12(cur, {})
        assert passed is True

    def test_fail_violations_present(self):
        cur = {"layer_violation_count": 3}
        passed, msg = _eval_m12(cur, {})
        assert passed is False
        assert "layer gravity violated" in msg

    def test_pass_missing_key(self):
        passed, msg = _eval_m12({}, {})
        assert passed is True  # defaults to 0


# ---------------------------------------------------------------------------
# Integration: GATE_DEFS and _EVALUATORS consistency
# ---------------------------------------------------------------------------


class TestGateConsistency:
    """Verify GATE_DEFS and _EVALUATORS are in sync."""

    def test_all_gates_have_evaluators(self):
        for gid in GATE_DEFS:
            assert gid in _EVALUATORS, f"Gate {gid} has no evaluator"

    def test_all_evaluators_have_gate_defs(self):
        for gid in _EVALUATORS:
            assert gid in GATE_DEFS, f"Evaluator {gid} has no gate definition"

    def test_all_gates_have_label_and_description(self):
        for gid, gdef in GATE_DEFS.items():
            assert "label" in gdef, f"Gate {gid} missing label"
            assert "description" in gdef, f"Gate {gid} missing description"

    def test_evaluator_signature_returns_tuple(self):
        """Every evaluator must return (bool, str)."""
        for gid, fn in _EVALUATORS.items():
            result = fn({}, {})
            assert isinstance(result, tuple), f"{gid}: expected tuple, got {type(result)}"
            assert len(result) == 2, f"{gid}: expected 2-tuple, got {len(result)}"
            assert isinstance(result[0], bool), f"{gid}: first element should be bool"
            assert isinstance(result[1], str), f"{gid}: second element should be str"

    def test_gate_count(self):
        """12 gates expected: M1–M12."""
        assert len(GATE_DEFS) == 12
        assert len(_EVALUATORS) == 12


# ---------------------------------------------------------------------------
# cmd_check integration with mocked Redis
# ---------------------------------------------------------------------------


class TestCmdCheck:
    """Test cmd_check with mocked Redis to verify enforce/warn logic."""

    def _mock_baseline(self, modes: dict, snapshot: dict) -> dict:
        return {"gate_modes": modes, "snapshot": snapshot}

    @patch("ops_scripts.ci._adg_ci_gates._get_gpc")
    @patch("ops_scripts.ci._adg_ci_gates._load_baseline")
    def test_all_pass_returns_zero(self, mock_bl, mock_gpc):
        from ops_scripts.ci._adg_ci_gates import cmd_check

        mock_gpc.return_value = {
            "uses_wall_clock": 10,
            "emits_determinism_digest": 5,
            "seeds_rng": 0,
            "invokes_getattr_dynamic": 1,
            "agent_executes_agent": 1,
            "writes_to": 100,
            "writes_through": 100,
            "applies_guardrail": 200,
            "calls": 500,
            "records_execution_trace": 400,
            "invokes_eval": 50,
            "emits_replay_key": 5,
            "routes_path": 200,
            "antipattern": 1000,
            "dead_imports": 100,
            "layer_violation_count": 0,
        }
        mock_bl.return_value = self._mock_baseline(
            modes={gid: "enforce" for gid in GATE_DEFS},
            snapshot={
                "uses_wall_clock": 10,
                "emits_determinism_digest": 5,
                "seeds_rng": 0,
                "invokes_getattr_dynamic": 1,
                "agent_executes_agent": 1,
                "writes_to": 100,
                "writes_through": 100,
                "applies_guardrail": 200,
                "calls": 500,
                "records_execution_trace": 400,
                "invokes_eval": 50,
                "emits_replay_key": 5,
                "routes_path": 200,
                "antipattern": 1000,
                "dead_imports": 100,
                "layer_violation_count": 0,
            },
        )
        assert cmd_check() == 0

    @patch("ops_scripts.ci._adg_ci_gates._get_gpc")
    @patch("ops_scripts.ci._adg_ci_gates._load_baseline")
    def test_enforce_mode_failure_returns_one(self, mock_bl, mock_gpc):
        from ops_scripts.ci._adg_ci_gates import cmd_check

        # M12 will fail: layer_violation_count > 0
        mock_gpc.return_value = {
            "uses_wall_clock": 10,
            "emits_determinism_digest": 5,
            "seeds_rng": 0,
            "invokes_getattr_dynamic": 1,
            "agent_executes_agent": 1,
            "writes_to": 100,
            "writes_through": 100,
            "applies_guardrail": 200,
            "calls": 500,
            "records_execution_trace": 400,
            "invokes_eval": 50,
            "emits_replay_key": 5,
            "routes_path": 200,
            "antipattern": 1000,
            "dead_imports": 100,
            "layer_violation_count": 5,  # violation!
        }
        mock_bl.return_value = self._mock_baseline(
            modes={gid: "enforce" for gid in GATE_DEFS},
            snapshot={
                "uses_wall_clock": 10,
                "emits_determinism_digest": 5,
                "seeds_rng": 0,
                "invokes_getattr_dynamic": 1,
                "agent_executes_agent": 1,
                "writes_to": 100,
                "writes_through": 100,
                "applies_guardrail": 200,
                "calls": 500,
                "records_execution_trace": 400,
                "invokes_eval": 50,
                "emits_replay_key": 5,
                "routes_path": 200,
                "antipattern": 1000,
                "dead_imports": 100,
                "layer_violation_count": 0,
            },
        )
        assert cmd_check() == 1

    @patch("ops_scripts.ci._adg_ci_gates._get_gpc")
    @patch("ops_scripts.ci._adg_ci_gates._load_baseline")
    def test_warn_mode_failure_returns_zero(self, mock_bl, mock_gpc):
        from ops_scripts.ci._adg_ci_gates import cmd_check

        # M12 would fail but is in warn mode
        mock_gpc.return_value = {
            "uses_wall_clock": 10,
            "emits_determinism_digest": 5,
            "seeds_rng": 0,
            "invokes_getattr_dynamic": 1,
            "agent_executes_agent": 1,
            "writes_to": 100,
            "writes_through": 100,
            "applies_guardrail": 200,
            "calls": 500,
            "records_execution_trace": 400,
            "invokes_eval": 50,
            "emits_replay_key": 5,
            "routes_path": 200,
            "antipattern": 1000,
            "dead_imports": 100,
            "layer_violation_count": 5,
        }
        modes = {gid: "enforce" for gid in GATE_DEFS}
        modes["M12"] = "warn"  # layer gate in warn mode
        mock_bl.return_value = self._mock_baseline(
            modes=modes,
            snapshot={
                "uses_wall_clock": 10,
                "emits_determinism_digest": 5,
                "seeds_rng": 0,
                "invokes_getattr_dynamic": 1,
                "agent_executes_agent": 1,
                "writes_to": 100,
                "writes_through": 100,
                "applies_guardrail": 200,
                "calls": 500,
                "records_execution_trace": 400,
                "invokes_eval": 50,
                "emits_replay_key": 5,
                "routes_path": 200,
                "antipattern": 1000,
                "dead_imports": 100,
                "layer_violation_count": 0,
            },
        )
        assert cmd_check() == 0

    @patch("ops_scripts.ci._adg_ci_gates._load_baseline")
    def test_missing_baseline_returns_two(self, mock_bl):
        from ops_scripts.ci._adg_ci_gates import cmd_check

        mock_bl.return_value = {}
        assert cmd_check() == 2

    @patch.dict(os.environ, {"ADG_CI_GATES_BYPASS": "1"})
    def test_bypass_returns_zero(self):
        from ops_scripts.ci._adg_ci_gates import cmd_check

        assert cmd_check() == 0
