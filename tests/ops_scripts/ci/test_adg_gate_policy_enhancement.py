"""Tests for P0-P3 ADG CI gate policy enhancement — Phases 01-05.

Covers:
    - ExecutionPolicy dataclass validation
    - RatchetResult from_dict / to_dict round-trip
    - TrendResult update, evaluate_promotion, from_dict round-trip
    - GateViolation new fields (path_criticality_class, structured_action_required, approval_required)
    - GateResult new fields (policy, ratchet, trend, stage) and to_dict
    - ADGGateBase._compute_ratchet path-aware logic
    - ADGGateBase preflight_mode dispatch
    - gate_ssot_catalog: build_index validates without error, correct entries
    - p0_runner: run_p0_two_pass import path structure
    - p3_trend_runner: run_p3_trend import path structure
    - adg_critical_defect_gate: module importable, main() signature
"""

from __future__ import annotations

import importlib
import json
import sys
from dataclasses import field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# gate_policy tests
# ---------------------------------------------------------------------------


class TestExecutionPolicy:
    def test_defaults_valid(self):
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        ep = ExecutionPolicy()
        errors = ep.validate()
        assert errors == [], f"Default ExecutionPolicy should be valid; got: {errors}"

    def test_to_dict_round_trip(self):
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        ep = ExecutionPolicy(
            stage="preflight+full",
            repairability="suggest_only",
            gate_action="halt",
            artifact_policy="minimal_failure_artifact",
            signal_source="sqlite_mv_ci",
            evidence_tier="truth",
        )
        d = ep.to_dict()
        assert d["stage"] == "preflight+full"
        assert d["repairability"] == "suggest_only"
        assert d["gate_action"] == "halt"
        assert d["artifact_policy"] == "minimal_failure_artifact"
        assert d["signal_source"] == "sqlite_mv_ci"
        assert d["evidence_tier"] == "truth"

    def test_invalid_stage_caught(self):
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        ep = ExecutionPolicy(stage="bad_stage")
        errors = ep.validate()
        assert any("stage" in e for e in errors)

    def test_invalid_artifact_policy_caught(self):
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        ep = ExecutionPolicy(artifact_policy="nonexistent_policy")
        errors = ep.validate()
        assert any("artifact_policy" in e for e in errors)

    def test_valid_preflight_stage(self):
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        ep = ExecutionPolicy(stage="preflight")
        errors = ep.validate()
        assert not any("stage" in e for e in errors)


class TestRatchetResult:
    def test_defaults(self):
        from ops_scripts.ci.adg_gates.gate_policy import RatchetResult

        r = RatchetResult()
        assert r.gross == 0
        assert r.blocked is False
        assert r.reason == ""

    def test_from_dict_to_dict_round_trip(self):
        from ops_scripts.ci.adg_gates.gate_policy import RatchetResult

        data = {
            "gross": 5,
            "net": 2,
            "new": 3,
            "resolved": 1,
            "critical_new": 1,
            "critical_near_sink": 0,
            "critical_cross_layer": 1,
            "modified_area_count": 2,
            "blocked": True,
            "reason": "net regression=2; critical_new=1",
        }
        r = RatchetResult.from_dict(data)
        assert r.gross == 5
        assert r.blocked is True
        assert r.reason == "net regression=2; critical_new=1"
        assert r.to_dict() == data

    def test_empty_dict_gives_defaults(self):
        from ops_scripts.ci.adg_gates.gate_policy import RatchetResult

        r = RatchetResult.from_dict({})
        assert r.gross == 0
        assert r.blocked is False


class TestTrendResult:
    def test_update_increments_consecutive(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.update(current_gross=10, current_hotspots=["a"])
        t.update(current_gross=12, current_hotspots=["a", "b"])
        t.update(current_gross=15, current_hotspots=["a", "b"])
        assert t.consecutive_increases == 2

    def test_update_resets_on_decrease(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.update(current_gross=10, current_hotspots=[])
        t.update(current_gross=12, current_hotspots=[])
        t.update(current_gross=8, current_hotspots=[])
        assert t.consecutive_increases == 0

    def test_update_equal_gross_resets_consecutive(self):
        """G3: equal gross (not strictly greater) must reset consecutive_increases to 0."""
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.update(current_gross=10, current_hotspots=[])
        t.update(current_gross=12, current_hotspots=[])  # increase → consecutive=1
        t.update(current_gross=12, current_hotspots=[])  # equal → must reset to 0
        assert t.consecutive_increases == 0, (
            f"Equal gross should reset consecutive_increases; got {t.consecutive_increases}"
        )

    def test_evaluate_promotion_below_threshold(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.consecutive_increases = 2
        t.evaluate_promotion(near_critical_path=True)
        assert t.promotion_candidate is False

    def test_evaluate_promotion_at_threshold(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.consecutive_increases = 3
        t.hotspot_modules = ["routing_agent"]
        t.evaluate_promotion(near_critical_path=True)
        assert t.promotion_candidate is True
        assert "Consecutive increases=3" in t.promotion_reason

    def test_evaluate_promotion_no_near_critical(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.consecutive_increases = 5
        t.evaluate_promotion(near_critical_path=False)
        assert t.promotion_candidate is False

    def test_evaluate_promotion_sticky_flag_not_reset_by_false(self):
        """G4: promotion_candidate is sticky — evaluate_promotion(False) does NOT clear it."""
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        t = TrendResult()
        t.consecutive_increases = 3
        t.hotspot_modules = ["routing"]
        t.evaluate_promotion(near_critical_path=True)  # sets to True
        assert t.promotion_candidate is True
        t.evaluate_promotion(near_critical_path=False)  # should NOT clear it
        assert t.promotion_candidate is True, (
            "promotion_candidate must remain True once set; calling with False is not a reset"
        )

    def test_from_dict_to_dict_round_trip(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        data: dict[str, Any] = {
            "history": [{"gross": 10, "hotspots": ["a"]}],
            "consecutive_increases": 1,
            "hotspot_modules": ["a"],
            "promotion_candidate": False,
            "promotion_reason": "",
        }
        t = TrendResult.from_dict(data)
        assert t.consecutive_increases == 1
        assert t.to_dict() == data


# ---------------------------------------------------------------------------
# gate_base tests
# ---------------------------------------------------------------------------


class TestGateViolationNewFields:
    def test_new_fields_have_defaults(self):
        from ops_scripts.ci.adg_gates.gate_base import GateViolation

        v = GateViolation(
            violation_id="test_v1",
            source_view="mv_test",
            source_node="n1",
            source_edge=None,
            file="foo.py",
            line=10,
            layer_src="L0",
            layer_dst="L3",
            path_id="p1",
            first_illegal_hop="L0->L3",
            path_criticality=2.5,
            in_modified_area=True,
            message="test violation",
        )
        assert v.path_criticality_class == "unknown"
        assert v.structured_action_required is False
        assert v.approval_required is False

    def test_new_fields_override(self):
        from ops_scripts.ci.adg_gates.gate_base import GateViolation

        v = GateViolation(
            violation_id="test_v2",
            source_view="mv_test",
            source_node=None,
            source_edge="e1",
            file="bar.py",
            line=None,
            layer_src="L1",
            layer_dst=None,
            path_id=None,
            first_illegal_hop=None,
            path_criticality=4.0,
            in_modified_area=False,
            message="write bypass",
            path_criticality_class="write",
            structured_action_required=True,
            approval_required=True,
        )
        assert v.path_criticality_class == "write"
        assert v.structured_action_required is True
        assert v.approval_required is True


class TestGateResultNewFields:
    def _make_result(self) -> Any:
        from ops_scripts.ci.adg_gates.gate_base import GateResult
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        return GateResult(
            gate_family="test_gate",
            severity="P0",
            snapshot_id="snap_001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={"total": 0},
            policy=ExecutionPolicy(
                stage="preflight+full",
                repairability="manual_only",
                gate_action="halt",
                artifact_policy="minimal_failure_artifact",
                signal_source="sqlite_mv_ci",
                evidence_tier="truth",
            ),
            stage="full",
        )

    def test_to_dict_includes_policy(self):
        result = self._make_result()
        d = result.to_dict()
        assert "policy" in d
        assert d["policy"]["stage"] == "preflight+full"

    def test_to_dict_includes_stage(self):
        result = self._make_result()
        d = result.to_dict()
        assert d["stage"] == "full"

    def test_to_dict_no_ratchet_by_default(self):
        result = self._make_result()
        d = result.to_dict()
        assert "ratchet" not in d

    def test_to_dict_includes_ratchet_when_set(self):
        from ops_scripts.ci.adg_gates.gate_policy import RatchetResult

        result = self._make_result()
        result.ratchet = RatchetResult(gross=3, net=1, blocked=False)
        d = result.to_dict()
        assert "ratchet" in d
        assert d["ratchet"]["gross"] == 3

    def test_to_dict_includes_trend_when_set(self):
        from ops_scripts.ci.adg_gates.gate_policy import TrendResult

        result = self._make_result()
        result.trend = TrendResult(consecutive_increases=2)
        d = result.to_dict()
        assert "trend" in d
        assert d["trend"]["consecutive_increases"] == 2


# ---------------------------------------------------------------------------
# _compute_ratchet tests
# ---------------------------------------------------------------------------


class TestComputeRatchet:
    """Tests for ADGGateBase._compute_ratchet path-aware logic."""

    def _make_gate(self):
        """Build a minimal concrete subclass of ADGGateBase for testing."""
        from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult

        class _TestGate(ADGGateBase):
            gate_family = "test_ratchet"
            severity = "P1"
            source_views = []

            def _find_latest_sqlite(self):
                return Path("/dev/null")

            def _connect(self):
                pass

            def _close(self):
                pass

            def _get_snapshot_id(self):
                return "snap_test"

            def _execute_gate_logic(self) -> GateResult:
                return GateResult(
                    gate_family=self.gate_family,
                    severity=self.severity,
                    snapshot_id="",
                    timestamp="",
                    status="passed",
                    violations=[],
                    summary={},
                )

        return _TestGate()

    def _make_violation(
        self,
        vid: str,
        criticality_class: str = "unknown",
        criticality: float = 1.0,
        in_modified: bool = False,
        layer_src: str = "L0",
        layer_dst: str = "L0",
    ) -> Any:
        from ops_scripts.ci.adg_gates.gate_base import GateViolation

        return GateViolation(
            violation_id=vid,
            source_view="mv_test",
            source_node=vid,
            source_edge=None,
            file=f"{vid}.py",
            line=1,
            layer_src=layer_src,
            layer_dst=layer_dst,
            path_id=vid,
            first_illegal_hop="L0->L3",
            path_criticality=criticality,
            in_modified_area=in_modified,
            message="test",
            path_criticality_class=criticality_class,
        )

    def test_no_regression_passes(self, tmp_path):
        gate = self._make_gate()
        gate.sqlite_path = Path("/dev/null")
        # Patch baseline to return current violations (no regression)
        v1 = self._make_violation("v1")
        v2 = self._make_violation("v2")
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": ["v1", "v2"]}),
            patch.object(gate, "_save_baseline") as mock_save,
        ):
            result = gate._compute_ratchet([v1, v2], "test_key")
        assert result.blocked is False
        assert result.net == 0
        assert result.new == 0
        assert result.resolved == 0
        # G1 fix: save MUST be called when not blocked
        mock_save.assert_called_once()

    def test_resolved_count_when_violations_disappear(self, tmp_path):
        """G1: resolved > 0 when baseline has violations that are now gone."""
        gate = self._make_gate()
        v1 = self._make_violation("v1")
        # baseline had v1 + v2; current only has v1 → v2 resolved
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": ["v1", "v2"]}),
            patch.object(gate, "_save_baseline"),
        ):
            result = gate._compute_ratchet([v1], "test_key")
        assert result.blocked is False
        assert result.net == -1
        assert result.resolved == 1
        assert result.new == 0

    def test_net_regression_blocks(self, tmp_path):
        gate = self._make_gate()
        v1 = self._make_violation("v1")
        v2 = self._make_violation("v2")
        v3 = self._make_violation("v3")  # new
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": ["v1", "v2"]}),
            patch.object(gate, "_save_baseline"),
        ):
            result = gate._compute_ratchet([v1, v2, v3], "test_key")
        assert result.blocked is True
        assert result.net == 1
        assert result.new == 1
        assert "net regression=1" in result.reason

    def test_critical_new_blocks_even_without_net(self, tmp_path):
        gate = self._make_gate()
        # Replace v1 with v_crit (same count, but critical class)
        v_crit = self._make_violation("v_crit", criticality_class="sink")
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": ["v1"]}),
            patch.object(gate, "_save_baseline"),
        ):
            result = gate._compute_ratchet([v_crit], "test_key")
        assert result.blocked is True
        assert result.critical_new == 1
        assert "critical_new=1" in result.reason

    def test_cross_layer_counted(self, tmp_path):
        gate = self._make_gate()
        v = self._make_violation("v_cross", layer_src="L0", layer_dst="L3")
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": []}),
            patch.object(gate, "_save_baseline"),
        ):
            result = gate._compute_ratchet([v], "test_key")
        assert result.critical_cross_layer == 1

    def test_near_sink_counted(self, tmp_path):
        gate = self._make_gate()
        v = self._make_violation("v_sink", criticality=0.9)
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": []}),
            patch.object(gate, "_save_baseline"),
        ):
            result = gate._compute_ratchet([v], "test_key")
        assert result.critical_near_sink == 1

    def test_baseline_saved_when_not_blocked(self, tmp_path):
        gate = self._make_gate()
        v1 = self._make_violation("v1")
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": ["v1"]}),
            patch.object(gate, "_save_baseline") as mock_save,
        ):
            gate._compute_ratchet([v1], "test_key")
        mock_save.assert_called_once()

    def test_baseline_not_saved_when_blocked(self, tmp_path):
        gate = self._make_gate()
        v1 = self._make_violation("v1")
        v2 = self._make_violation("v2")
        with (
            patch.object(gate, "_load_baseline", return_value={"violation_ids": ["v1"]}),
            patch.object(gate, "_save_baseline") as mock_save,
        ):
            gate._compute_ratchet([v1, v2], "test_key")
        mock_save.assert_not_called()


# ---------------------------------------------------------------------------
# preflight_mode dispatch tests
# ---------------------------------------------------------------------------


class TestPreflightDispatch:
    def _make_preflight_gate(self):
        from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult

        class _PreflightGate(ADGGateBase):
            gate_family = "preflight_test"
            severity = "P0"
            source_views = []

            def _find_latest_sqlite(self):
                return Path("/dev/null")

            def _connect(self):
                pass

            def _close(self):
                pass

            def _get_snapshot_id(self):
                return "snap_pf"

            def _execute_gate_logic(self) -> GateResult:
                return GateResult(
                    gate_family=self.gate_family,
                    severity=self.severity,
                    snapshot_id="",
                    timestamp="",
                    status="passed",
                    violations=[],
                    summary={"source": "full"},
                    stage="full",
                )

            def _execute_preflight_logic(self) -> GateResult:
                return GateResult(
                    gate_family=self.gate_family,
                    severity=self.severity,
                    snapshot_id="",
                    timestamp="",
                    status="passed",
                    violations=[],
                    summary={"source": "preflight"},
                    stage="preflight",
                )

        return _PreflightGate

    def test_preflight_mode_dispatches_to_preflight(self):
        cls = self._make_preflight_gate()
        gate = cls(preflight_mode=True)
        result = gate.run(emit_artifacts=False)
        assert result.stage == "preflight"
        assert result.summary["source"] == "preflight"

    def test_full_mode_dispatches_to_full(self):
        cls = self._make_preflight_gate()
        gate = cls(preflight_mode=False)
        result = gate.run(emit_artifacts=False)
        assert result.stage == "full"
        assert result.summary["source"] == "full"


# ---------------------------------------------------------------------------
# SSOT catalog tests
# ---------------------------------------------------------------------------


class TestGateSSotCatalog:
    def test_catalog_imports_without_error(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_CATALOG, GATE_INDEX

        assert len(GATE_CATALOG) > 0
        assert len(GATE_INDEX) > 0

    def test_no_duplicate_gate_ids(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_CATALOG

        ids = [e.gate_id for e in GATE_CATALOG]
        assert len(ids) == len(set(ids)), f"Duplicate gate_ids: {ids}"

    def test_all_entries_valid(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_CATALOG

        for entry in GATE_CATALOG:
            errors = entry.validate()
            assert errors == [], f"{entry.gate_id} has validation errors: {errors}"

    def test_p0_write_preflight_capable(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_INDEX, get_preflight_gates

        preflight = get_preflight_gates()
        preflight_ids = [e.gate_id for e in preflight]
        assert "G-P0-WRITE" in preflight_ids
        assert "G-P0-TTA" in preflight_ids

    def test_full_only_gates_not_in_preflight(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_INDEX, get_preflight_gates

        preflight_ids = {e.gate_id for e in get_preflight_gates()}
        assert "G-P0-AUTH" not in preflight_ids
        assert "G-P0-CAP" not in preflight_ids

    def test_critical_defect_gate_reclassified_p0(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_INDEX

        entry = GATE_INDEX.get("G-P0-CRIT-DEF")
        assert entry is not None
        assert entry.severity == "P0"
        assert "adg_critical_defect_gate" in entry.file

    def test_m1_m6_entries_present(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_INDEX

        for gate_id in (
            "G-M1-DET",
            "G-M2-DISPATCH",
            "G-M3-MUTATION",
            "G-M4-GUARDRAIL",
            "G-M5-TRACE",
            "G-M6-REPLAY",
        ):
            assert gate_id in GATE_INDEX, f"Missing catalog entry: {gate_id}"

    def test_p3_gates_are_watch_action(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import get_gates_by_severity

        p3 = get_gates_by_severity("P3")
        for e in p3:
            assert e.policy.gate_action == "watch", (
                f"{e.gate_id} is P3 but gate_action={e.policy.gate_action}"
            )

    def test_to_dict_round_trip(self):
        from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_CATALOG

        for entry in GATE_CATALOG:
            d = entry.to_dict()
            assert d["gate_id"] == entry.gate_id
            assert "policy" in d


# ---------------------------------------------------------------------------
# _write_artifacts artifact_policy branch tests
# ---------------------------------------------------------------------------


class TestWriteArtifacts:
    def _make_concrete_gate(self, tmp_path: Path, policy_name: str) -> Any:
        from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        class _ArtGate(ADGGateBase):
            gate_family = "art_test"
            severity = "P1"
            source_views = []
            execution_policy = ExecutionPolicy(
                stage="full",
                repairability="manual_only",
                gate_action="halt",
                artifact_policy=policy_name,
                signal_source="canonical_policy",
                evidence_tier="truth",
            )

            def _find_latest_sqlite(self):
                return Path("/dev/null")

            def _connect(self):
                pass

            def _close(self):
                pass

            def _get_snapshot_id(self):
                return "snap_art"

            def _execute_gate_logic(self) -> GateResult:
                return GateResult(
                    gate_family=self.gate_family,
                    severity=self.severity,
                    snapshot_id="snap_art",
                    timestamp="2026-01-01T00:00:00Z",
                    status="passed",
                    violations=[],
                    summary={},
                    policy=self.execution_policy,
                    stage="full",
                )

        import ops_scripts.ci.adg_gates.gate_base as gb

        original = gb.CI_ARTIFACTS_DIR
        gb.CI_ARTIFACTS_DIR = tmp_path / "ci_gates"
        gate = _ArtGate()
        gate._artifact_dir_override = tmp_path / "ci_gates"
        gb.CI_ARTIFACTS_DIR = original
        return gate

    def test_trend_only_policy_emits_trend_json(self, tmp_path):
        """G5: trend_only policy must write a *_trend.json file with trend key."""
        from ops_scripts.ci.adg_gates.gate_base import GateResult
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy, TrendResult
        import ops_scripts.ci.adg_gates.gate_base as gb

        original_dir = gb.CI_ARTIFACTS_DIR
        gb.CI_ARTIFACTS_DIR = tmp_path / "ci_gates"
        try:
            gate = self._make_concrete_gate(tmp_path, "trend_only")
            trend = TrendResult(consecutive_increases=2, hotspot_modules=["foo"])
            result = GateResult(
                gate_family="art_test",
                severity="P3",
                snapshot_id="snap_art",
                timestamp="2026-01-01T00:00:00Z",
                status="passed",
                violations=[],
                summary={},
                policy=ExecutionPolicy(
                    stage="full",
                    repairability="suggest_only",
                    gate_action="watch",
                    artifact_policy="trend_only",
                    signal_source="canonical_policy",
                    evidence_tier="truth",
                ),
                trend=trend,
                stage="full",
            )
            artifact_dir = gate._write_artifacts(result)
            trend_files = list(artifact_dir.glob("*_trend.json"))
            assert len(trend_files) == 1, f"Expected 1 trend JSON; got {trend_files}"
            data = json.loads(trend_files[0].read_text())
            assert "trend" in data
            assert data["trend"]["consecutive_increases"] == 2
            assert data["gate_family"] == "art_test"
        finally:
            gb.CI_ARTIFACTS_DIR = original_dir

    def test_minimal_failure_policy_emits_compact_json(self, tmp_path):
        """G5 adjacent: minimal_failure_artifact must NOT emit full findings.txt."""
        from ops_scripts.ci.adg_gates.gate_base import GateResult, GateViolation
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy
        import ops_scripts.ci.adg_gates.gate_base as gb

        original_dir = gb.CI_ARTIFACTS_DIR
        gb.CI_ARTIFACTS_DIR = tmp_path / "ci_gates"
        try:
            gate = self._make_concrete_gate(tmp_path, "minimal_failure_artifact")
            v = GateViolation(
                violation_id="v_min",
                source_view="mv",
                source_node="n",
                source_edge=None,
                file="x.py",
                line=1,
                layer_src="L0",
                layer_dst="L3",
                path_id="p1",
                first_illegal_hop="L0->L3",
                path_criticality=1.0,
                in_modified_area=True,
                message="test violation",
                structured_action_required=True,
                approval_required=True,
            )
            result = GateResult(
                gate_family="art_test",
                severity="P0",
                snapshot_id="snap_art",
                timestamp="2026-01-01T00:00:00Z",
                status="blocked",
                violations=[v],
                summary={},
                policy=ExecutionPolicy(
                    stage="preflight",
                    repairability="manual_only",
                    gate_action="halt",
                    artifact_policy="minimal_failure_artifact",
                    signal_source="sqlite_mv_ci",
                    evidence_tier="truth",
                ),
                stage="preflight",
            )
            artifact_dir = gate._write_artifacts(result)
            minimal_files = list(artifact_dir.glob("*_minimal_failure.json"))
            findings_files = list(artifact_dir.glob("*_findings.txt"))
            assert len(minimal_files) == 1, f"Expected 1 minimal JSON; got {minimal_files}"
            assert len(findings_files) == 0, "minimal_failure must NOT emit findings.txt"
            data = json.loads(minimal_files[0].read_text())
            assert data["violations"][0]["structured_action_required"] is True
            assert data["violations"][0]["approval_required"] is True
        finally:
            gb.CI_ARTIFACTS_DIR = original_dir


# ---------------------------------------------------------------------------
# adg_critical_defect_gate importability
# ---------------------------------------------------------------------------


class TestCriticalDefectGate:
    def test_module_importable(self):
        import ops_scripts.ci.adg_critical_defect_gate as m

        assert hasattr(m, "main")
        assert callable(m.main)

    def test_main_returns_0_when_no_sqlite(self, tmp_path, monkeypatch):
        """When no ADG SQLite is present, gate degrades to allowed (exit 0)."""
        import ops_scripts.ci.adg_critical_defect_gate as m

        monkeypatch.setattr(m, "_get_repo_root", lambda: tmp_path)
        rc = m.main()
        assert rc == 0, "With no SQLite file, gate should return 0 (no violations to block on)"

    def test_sqlite_error_degrades_to_empty_and_returns_0(self, tmp_path, monkeypatch):
        """G6: sqlite3.Error during query is caught; _get_critical_violations returns [] and main() returns 0."""
        import sqlite3

        import ops_scripts.ci.adg_critical_defect_gate as m

        # Provide a real-looking sqlite file so the glob finds it, then error on connect
        fake_sqlite = tmp_path / "artifacts" / "adg" / "adg_indexed_20260101.sqlite"
        fake_sqlite.parent.mkdir(parents=True)
        fake_sqlite.touch()
        monkeypatch.setattr(m, "_get_repo_root", lambda: tmp_path)

        with patch("sqlite3.connect", side_effect=sqlite3.Error("db locked")):
            violations = m._get_critical_violations()

        assert violations == [], f"Expected [] on sqlite3.Error; got {violations}"

    def test_main_returns_0_on_sqlite_error(self, tmp_path, monkeypatch):
        """G6: main() returns 0 (not crash) when sqlite3.Error is raised during query."""
        import sqlite3

        import ops_scripts.ci.adg_critical_defect_gate as m

        fake_sqlite = tmp_path / "artifacts" / "adg" / "adg_indexed_20260101.sqlite"
        fake_sqlite.parent.mkdir(parents=True, exist_ok=True)
        fake_sqlite.touch()
        monkeypatch.setattr(m, "_get_repo_root", lambda: tmp_path)

        with patch("sqlite3.connect", side_effect=sqlite3.Error("db locked")):
            rc = m.main()

        assert rc == 0, "main() must return 0 when sqlite3.Error degrades to no violations"


# ---------------------------------------------------------------------------
# p0_runner module structure
# ---------------------------------------------------------------------------


class TestP0RunnerStructure:
    def test_module_importable(self):
        import ops_scripts.ci.adg_gates.p0_runner as m

        assert hasattr(m, "run_p0_two_pass")
        assert hasattr(m, "run_preflight")
        assert hasattr(m, "run_full")
        assert hasattr(m, "PREFLIGHT_GATE_CLASSES")
        assert hasattr(m, "FULL_GATE_CLASSES")

    def test_preflight_subset_of_full(self):
        from ops_scripts.ci.adg_gates.p0_runner import FULL_GATE_CLASSES, PREFLIGHT_GATE_CLASSES

        for cls in PREFLIGHT_GATE_CLASSES:
            assert cls in FULL_GATE_CLASSES, (
                f"Preflight gate {cls} not in FULL_GATE_CLASSES — full pass must include all"
            )

    def test_run_p0_two_pass_skip_preflight_returns_int(self):
        from ops_scripts.ci.adg_gates.p0_runner import run_p0_two_pass

        with (
            patch("ops_scripts.ci.adg_gates.p0_runner._GATE_IMPORTS_OK", False),
            patch("ops_scripts.ci.adg_gates.p0_runner._IMPORT_ERROR", "test"),
        ):
            rc = run_p0_two_pass(emit_artifacts=False, skip_preflight=True)
        assert rc == 2  # import error → exit 2


# ---------------------------------------------------------------------------
# p3_trend_runner module structure
# ---------------------------------------------------------------------------


class TestP3TrendRunnerStructure:
    def test_module_importable(self):
        import ops_scripts.ci.adg_gates.p3_trend_runner as m

        assert hasattr(m, "run_p3_trend")
        assert hasattr(m, "_load_trend")
        assert hasattr(m, "_save_trend")

    def test_run_p3_returns_2_on_import_error(self):
        import ops_scripts.ci.adg_gates.p3_trend_runner as m

        with patch.object(m, "_IMPORTS_OK", False), patch.object(m, "_IMPORT_ERROR", "test"):
            rc = m.run_p3_trend(emit_artifacts=False)
        assert rc == 2


# ---------------------------------------------------------------------------
# M-gates module structure
# ---------------------------------------------------------------------------


class TestMGatesStructure:
    def test_module_importable(self):
        import ops_scripts.ci.adg_gates.gate_m_gates as m

        assert hasattr(m, "M1DeterminismGate")
        assert hasattr(m, "M2DispatchVisibilityGate")
        assert hasattr(m, "M3MutationSovereigntyGate")
        assert hasattr(m, "M4GuardrailCoverageGate")
        assert hasattr(m, "M5TraceCoverageGate")
        assert hasattr(m, "M6ReplayKeyGate")

    def test_all_gates_have_execution_policy(self):
        from ops_scripts.ci.adg_gates.gate_m_gates import (
            M1DeterminismGate,
            M2DispatchVisibilityGate,
            M3MutationSovereigntyGate,
            M4GuardrailCoverageGate,
            M5TraceCoverageGate,
            M6ReplayKeyGate,
        )
        from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

        for cls in (
            M1DeterminismGate,
            M2DispatchVisibilityGate,
            M3MutationSovereigntyGate,
            M4GuardrailCoverageGate,
            M5TraceCoverageGate,
            M6ReplayKeyGate,
        ):
            assert isinstance(cls.execution_policy, ExecutionPolicy), (
                f"{cls.__name__} missing execution_policy"
            )

    def test_m_gate_degrades_gracefully_when_redis_unavailable(self):
        from ops_scripts.ci.adg_gates.gate_m_gates import M1DeterminismGate

        gate = M1DeterminismGate()
        with patch(
            "ops_scripts.ci.adg_gates.gate_m_gates._get_gpc", side_effect=RuntimeError("redis unavailable")
        ):
            result = gate.run(emit_artifacts=False)
        assert result.status == "warn"

    def test_m1_blocks_on_wall_clock_regression(self):
        from ops_scripts.ci.adg_gates.gate_m_gates import M1DeterminismGate

        gate = M1DeterminismGate()
        base_gpc = {
            "uses_wall_clock": 5,
            "emits_determinism_digest": 2,
            "seeds_rng": 1,
        }
        cur_gpc = {
            "uses_wall_clock": 8,  # +3 — regression
            "emits_determinism_digest": 2,
            "seeds_rng": 1,
        }

        with (
            patch("ops_scripts.ci.adg_gates.gate_m_gates._get_gpc", return_value=cur_gpc),
            patch.object(gate, "_load_gpc_baseline", return_value=base_gpc),
            patch.object(gate, "_seed_baseline_if_absent"),
            patch.object(gate, "_save_gpc_baseline"),
        ):
            result = gate.run(emit_artifacts=False)

        assert result.status == "blocked"
        assert len(result.violations) == 1
        assert "uses_wall_clock" in result.violations[0].message

    def test_m1_passes_when_determinism_added(self):
        from ops_scripts.ci.adg_gates.gate_m_gates import M1DeterminismGate

        gate = M1DeterminismGate()
        base_gpc = {"uses_wall_clock": 5, "emits_determinism_digest": 2, "seeds_rng": 1}
        cur_gpc = {"uses_wall_clock": 8, "emits_determinism_digest": 5, "seeds_rng": 1}

        with (
            patch("ops_scripts.ci.adg_gates.gate_m_gates._get_gpc", return_value=cur_gpc),
            patch.object(gate, "_load_gpc_baseline", return_value=base_gpc),
            patch.object(gate, "_seed_baseline_if_absent"),
            patch.object(gate, "_save_gpc_baseline"),
        ):
            result = gate.run(emit_artifacts=False)

        assert result.status == "passed"

    def test_m4_blocks_when_guardrail_ratio_below_threshold(self):
        from ops_scripts.ci.adg_gates.gate_m_gates import M4GuardrailCoverageGate

        gate = M4GuardrailCoverageGate()
        cur_gpc = {"applies_guardrail": 5, "calls": 100}  # ratio = 0.05 < 0.10

        with patch("ops_scripts.ci.adg_gates.gate_m_gates._get_gpc", return_value=cur_gpc):
            result = gate.run(emit_artifacts=False)

        assert result.status == "blocked"
        assert "applies_guardrail/calls" in result.violations[0].message

    def test_m6_blocks_on_replay_key_regression(self):
        from ops_scripts.ci.adg_gates.gate_m_gates import M6ReplayKeyGate

        gate = M6ReplayKeyGate()
        base_gpc = {"emits_replay_key": 50}
        cur_gpc = {"emits_replay_key": 45}  # decreased

        with (
            patch("ops_scripts.ci.adg_gates.gate_m_gates._get_gpc", return_value=cur_gpc),
            patch.object(gate, "_load_gpc_baseline", return_value=base_gpc),
            patch.object(gate, "_seed_baseline_if_absent"),
            patch.object(gate, "_save_gpc_baseline"),
        ):
            result = gate.run(emit_artifacts=False)

        assert result.status == "blocked"
        assert "regressed" in result.violations[0].message
