"""Unit tests for apps_lic.runtime.bindings.exit_binding.

Wave 4.1 — plan adg-testing-hotspots-wave-plan-a7f3c1
Module fan-in: 48 (highest-blast binding in this wave).

Purpose: cover the pure / deterministic Exit-binding surface — the terminal-R5
denial disposition builder, the fail-closed GateMesh checks
(_check_gate_mesh_result), the read-only-draft G27 check
(_check_g27_for_read_only_draft), the exit-profile loader fail-closed paths
plus a happy-path against a temp config (_load_exit_profile), and the runtime
exhaust bundle builder. Real SealedL2Artifact instances; minimal stand-in
GateVerdict objects only where the binding consumes a duck-typed verdict (it
reads .gate_id / .result.value / .reason via getattr/hasattr — no agentic_core
verdict factory exists for a unit-level fixture, so a faithful minimal real
object is built).

NOT covered (requires the full X1/X2/X3 gate engine + provider wiring):
exit_finalize_apps_lic end-to-end through run_all_x1_gates -> build_x3_packet,
and the validation-exit-proof bridge. Those are integration surfaces.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_lic.runtime.bindings import exit_binding as mod
from apps_lic.runtime.bindings.exit_binding import (
    TERMINAL_R5_NO_L4_WRITE_RECEIPT,
    TERMINAL_R5_NO_SEND_RECEIPT,
    TERMINAL_R5_RUNTIME_EXHAUST_REF,
    AppsLicExitProfileError,
    _build_runtime_exhaust_bundle,
    _check_g27_for_read_only_draft,
    _check_gate_mesh_result,
    _load_exit_profile,
    terminal_r5_exit_disposition_apps_lic,
)


class _Result:
    def __init__(self, value: str) -> None:
        self.value = value


class _Verdict:
    """Minimal duck-typed GateVerdict the binding reads via getattr/hasattr."""

    def __init__(self, gate_id: str, result: str = "PASS", reason: str = "") -> None:
        self.gate_id = gate_id
        self.result = _Result(result)
        self.reason = reason


def _l2(**kw) -> SealedL2Artifact:
    base = dict(
        request_id="rq1",
        run_id="run1",
        app_id="apps_lic",
        trace_id="tr1",
        execution_status="completed",
        l5_certification_ref="cert-test",
    )
    base.update(kw)
    return SealedL2Artifact(**base)


class TestModuleConstants:
    def test_receipt_constants(self) -> None:
        assert TERMINAL_R5_NO_SEND_RECEIPT.startswith("pass:")
        assert TERMINAL_R5_NO_L4_WRITE_RECEIPT.startswith("pass:")
        assert "runtime_exhaust" in TERMINAL_R5_RUNTIME_EXHAUST_REF


class TestTerminalR5Disposition:
    def test_basic_shape(self) -> None:
        d = terminal_r5_exit_disposition_apps_lic(
            request_id="rq", run_id="rn", trace_id="tr", terminal_reason="some_reason"
        )
        assert d.app_id == "apps_lic"
        assert d.outcome_authorized is False
        assert d.eval_threshold_met is False
        assert d.hitl_required is False
        assert d.exit_status == "blocked"

    def test_final_output_receipts(self) -> None:
        d = terminal_r5_exit_disposition_apps_lic(
            request_id="rq", run_id="rn", trace_id="tr", terminal_reason="r"
        )
        fo = d.final_output
        assert fo["disposition"] == "DENY"
        assert fo["terminal_r5"] is True
        assert fo["no_send_receipt"] == TERMINAL_R5_NO_SEND_RECEIPT
        assert fo["no_l4_write_receipt"] == TERMINAL_R5_NO_L4_WRITE_RECEIPT
        assert fo["runtime_exhaust_ref"] == TERMINAL_R5_RUNTIME_EXHAUST_REF
        assert fo["reason_codes"] == ["r"]

    def test_default_reason_when_empty(self) -> None:
        d = terminal_r5_exit_disposition_apps_lic(
            request_id="rq", run_id="rn", trace_id="tr", terminal_reason=""
        )
        assert d.final_output["reason_codes"] == ["route_family=R5_FALLBACK"]

    def test_route_family_threaded(self) -> None:
        d = terminal_r5_exit_disposition_apps_lic(
            request_id="rq",
            run_id="rn",
            trace_id="tr",
            terminal_reason="r",
            route_family="R5_CUSTOM",
            deprecated_route_family="R5_OLD",
        )
        assert d.final_output["route_family"] == "R5_CUSTOM"
        assert d.final_output["deprecated_route_family"] == "R5_OLD"

    def test_custom_exit_status(self) -> None:
        d = terminal_r5_exit_disposition_apps_lic(
            request_id="rq", run_id="rn", trace_id="tr", terminal_reason="r",
            exit_status="failure",
        )
        assert d.exit_status == "failure"

    def test_timestamp_is_z_suffixed(self) -> None:
        d = terminal_r5_exit_disposition_apps_lic(
            request_id="rq", run_id="rn", trace_id="tr", terminal_reason="r"
        )
        assert d.exit_timestamp.endswith("Z")


class TestCheckGateMeshResult:
    def test_empty_verdicts_fail_closed(self) -> None:
        ok, reason = _check_gate_mesh_result([], {"required_gates": []})
        assert ok is False
        assert reason == "missing_gate_mesh_result"

    def test_missing_required_gate(self) -> None:
        ok, reason = _check_gate_mesh_result([_Verdict("G1")], {"required_gates": ["G2"]})
        assert ok is False
        assert reason == "missing_required_gate:G2"

    def test_missing_multiple_required_sorted(self) -> None:
        ok, reason = _check_gate_mesh_result(
            [_Verdict("G1")], {"required_gates": ["G3", "G2"]}
        )
        assert ok is False
        assert reason == "missing_required_gate:G2,G3"

    def test_all_required_present(self) -> None:
        ok, reason = _check_gate_mesh_result(
            [_Verdict("G1"), _Verdict("G2")], {"required_gates": ["G1", "G2"]}
        )
        assert ok is True
        assert reason == ""

    def test_material_unknown(self) -> None:
        ok, reason = _check_gate_mesh_result(
            [_Verdict("G1", "UNKNOWN")], {"required_gates": []}
        )
        assert ok is False
        assert reason == "material_unknown:G1"

    def test_not_applicable_without_reason(self) -> None:
        ok, reason = _check_gate_mesh_result(
            [_Verdict("G1", "NOT_APPLICABLE", "")], {"required_gates": []}
        )
        assert ok is False
        assert reason == "not_applicable_without_reason:G1"

    def test_not_applicable_with_reason_ok(self) -> None:
        ok, reason = _check_gate_mesh_result(
            [_Verdict("G1", "NOT_APPLICABLE", "inert")], {"required_gates": []}
        )
        assert ok is True


class TestCheckG27ForReadOnlyDraft:
    def test_absent_g27_ok(self) -> None:
        ok, reason = _check_g27_for_read_only_draft([_Verdict("G1")], _l2())
        assert ok is True
        assert reason == ""

    def test_correct_not_applicable_read_only(self) -> None:
        ok, _ = _check_g27_for_read_only_draft(
            [_Verdict("G27", "NOT_APPLICABLE", "read_only_draft_return")], _l2()
        )
        assert ok is True

    def test_draft_in_reason_ok(self) -> None:
        ok, _ = _check_g27_for_read_only_draft(
            [_Verdict("G27", "NOT_APPLICABLE", "draft only")], _l2()
        )
        assert ok is True

    def test_wrong_result(self) -> None:
        ok, reason = _check_g27_for_read_only_draft(
            [_Verdict("G27", "PASS", "x")], _l2()
        )
        assert ok is False
        assert reason == "g27_wrong_result:PASS"

    def test_not_applicable_without_reason(self) -> None:
        ok, reason = _check_g27_for_read_only_draft(
            [_Verdict("G27", "NOT_APPLICABLE", "")], _l2()
        )
        assert ok is False
        assert reason == "g27_not_applicable_without_reason"

    def test_wrong_reason(self) -> None:
        ok, reason = _check_g27_for_read_only_draft(
            [_Verdict("G27", "NOT_APPLICABLE", "something_else")], _l2()
        )
        assert ok is False
        assert reason == "g27_wrong_reason:something_else"


class TestLoadExitProfileFailClosed:
    def test_missing_file_raises(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(mod, "_EXIT_PROFILE_PATH", tmp_path / "nope.json")
        with pytest.raises(AppsLicExitProfileError, match="not found"):
            _load_exit_profile()

    def test_malformed_json_raises(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        monkeypatch.setattr(mod, "_EXIT_PROFILE_PATH", bad)
        with pytest.raises(AppsLicExitProfileError, match="malformed"):
            _load_exit_profile()

    def test_missing_keys_raises(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        f = tmp_path / "profile.json"
        f.write_text(json.dumps({"profile_id": "p"}), encoding="utf-8")
        monkeypatch.setattr(mod, "_EXIT_PROFILE_PATH", f)
        with pytest.raises(AppsLicExitProfileError, match="missing required keys"):
            _load_exit_profile()

    def test_real_config_missing_expected_keys(self) -> None:
        # The shipped apps_lic exit profile uses legacy_* gate keys, not the
        # required_exit_gates / conditional_exit_gates this loader expects, so
        # the loader fails closed against the real config. (Asserting the real,
        # current behavior — see report note.)
        with pytest.raises(AppsLicExitProfileError):
            _load_exit_profile()

    def test_happy_path_temp_config(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        f = tmp_path / "profile.json"
        f.write_text(
            json.dumps(
                {
                    "profile_id": "outreach_v1",
                    "required_exit_gates": ["G1", "G2"],
                    "conditional_exit_gates": ["G27"],
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "_EXIT_PROFILE_PATH", f)
        result = _load_exit_profile()
        assert result["required_gates"] == ["G1", "G2"]
        assert result["conditional_gates"] == ["G27"]
        assert result["profile_id"] == "outreach_v1"
        assert result["config_digest"].startswith("sha256:")
        assert result["config_path"] == str(f)


class TestBuildRuntimeExhaustBundle:
    def test_minimal_bundle(self) -> None:
        bundle = _build_runtime_exhaust_bundle(_l2())
        assert bundle["app_id"] == "apps_lic"
        assert bundle["request_id"] == "rq1"
        assert bundle["boundary"] == "current_run"
        assert bundle["future_run_proposals"] == []
        assert bundle["exit_status"] == "unknown"
        assert bundle["outcome_authorized"] is False

    def test_cache_bypass_receipt_present(self) -> None:
        bundle = _build_runtime_exhaust_bundle(_l2())
        receipt = bundle["cache_bypass_receipt"]
        # No package supplied -> config-default policy source.
        assert receipt["policy_source"] == "apps_lic_config_default"
        assert "final_draft_r1a_bypass" in receipt
        assert "final_draft_r1b_bypass" in receipt

    def test_no_package_omits_profile_refs(self) -> None:
        bundle = _build_runtime_exhaust_bundle(_l2())
        assert "learning_profile_ref" not in bundle
        assert "exit_profile_ref" not in bundle
