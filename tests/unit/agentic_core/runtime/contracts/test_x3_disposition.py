"""Unit tests for agentic_core.runtime.contracts.x3_disposition.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 Exit/X3 spine.
``x3_disposition`` (fan_in=23, L_RUNTIME) is the single Exit-stage output emitted
once per request. Frozen/slots dataclass with the L5 cert-ref fail-closed guard.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.posture import POSTURE_WRITE_INTENT, RuntimePosture
from agentic_core.runtime.contracts.x3_disposition import X3Disposition


def _x3(**overrides: object) -> X3Disposition:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        exit_status="success",
        l5_certification_ref="cert-ref-1",
    )
    base.update(overrides)
    return X3Disposition(**base)  # type: ignore[arg-type]


class TestX3Disposition:
    def test_valid_construction(self) -> None:
        d = _x3()
        assert d.exit_status == "success"
        assert d.app_id == "apps_rg"

    def test_defaults(self) -> None:
        d = _x3()
        assert d.outcome_authorized is False
        assert d.final_output == {}
        assert d.output_artifact_path is None
        assert d.eval_score is None
        assert d.eval_threshold_met is False
        assert d.hitl_required is False
        assert d.schema_version == "W6.0"
        assert d.is_uwg_write_authority is False
        assert d.is_future_run_only is False
        assert d.otel_span_refs == ()
        assert d.gate_verdict_refs == ()

    def test_posture_default_write_intent(self) -> None:
        d = _x3()
        assert isinstance(d.posture, RuntimePosture)
        assert d.posture == POSTURE_WRITE_INTENT

    def test_carries_disposition_fields(self) -> None:
        d = _x3(exit_status="abstain", outcome_authorized=True, eval_score=0.91, eval_threshold_met=True)
        assert d.exit_status == "abstain"
        assert d.outcome_authorized is True
        assert d.eval_score == 0.91
        assert d.eval_threshold_met is True

    def test_missing_cert_ref_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _x3(l5_certification_ref="")

    @pytest.mark.parametrize("bad", ["   ", "\t"])
    def test_blank_cert_ref_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _x3(l5_certification_ref=bad)

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _x3().exit_status = "failure"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(_x3(), "__dict__")
