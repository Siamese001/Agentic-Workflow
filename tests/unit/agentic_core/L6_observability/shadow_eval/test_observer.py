"""Unit tests for agentic_core.L6_observability.shadow_eval.observer.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L6 module.
``observer`` (06.2) enforces the observer law: L6 only reads completed-run
exhaust and never writes a forbidden surface. The pure/deterministic surface
covered here is the FORBIDDEN_WRITE_SURFACES set, ``deny_if_forbidden`` raising
``ObserverViolation``, the surface-isolation status machine, the stage-barrier
roll-up, and the eval-readiness decision tree (READY / PARTIAL / HOLD /
NON_EVALUABLE). No live LLM/gateway is involved; everything is data-in/data-out.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.shadow_eval.contracts import (
    NormalizedEvidenceRecord,
    RuntimeExhaustBundle,
)
from agentic_core.L6_observability.shadow_eval.observer import (
    FORBIDDEN_WRITE_SURFACES,
    READINESS_HOLD,
    READINESS_NON_EVAL,
    READINESS_READY,
    ObserverViolation,
    build_observer_compliance_receipt,
    build_surface_isolation_manifest,
    deny_if_forbidden,
    evaluate_readiness,
    record_denied_write_attempt,
    stage_barrier_check,
)


def _bundle(**overrides: object) -> RuntimeExhaustBundle:
    base = dict(
        runtime_exhaust_bundle_id="reb-1",
        request_id="rq",
        run_id="run",
        session_id="sess",
        tenant_id="tenant",
        trace_root="trace-root",
        completed_at="2026-06-14T00:00:00Z",
        runtime_boundary_crossed=True,
        exit_disposition_ref="exit-1",
        policy_hash="ph",
        blueprint_hash="bp",
        replay_key="rk",
        route_contract_ref="route-1",
        l5_certification_ref="cert-ok",
    )
    base.update(overrides)
    return RuntimeExhaustBundle(**base)  # type: ignore[arg-type]


def _norm(**overrides: object) -> NormalizedEvidenceRecord:
    base = dict(
        normalized_record_id="nr-1",
        runtime_exhaust_bundle_id="reb-1",
        canonical_event_type="llm_call",
        canonical_stage="L2",
        source_ref="src",
        normalized_payload_ref="payload",
        trace_id="trace-1",
        span_id="span-1",
        parent_span_id=None,
        request_id="rq",
        run_id="run",
        tenant_id="tenant",
        route_id="route-1",
        prompt_hash="prompt-1",
    )
    base.update(overrides)
    return NormalizedEvidenceRecord(**base)  # type: ignore[arg-type]


class TestForbiddenSurfaces:
    @pytest.mark.parametrize(
        "surface",
        ["L4", "L4_state", "BUS_U", "policy_publish", "current_run_uwg"],
    )
    def test_known_forbidden_members(self, surface: str) -> None:
        assert surface in FORBIDDEN_WRITE_SURFACES

    @pytest.mark.parametrize("surface", list(FORBIDDEN_WRITE_SURFACES))
    def test_deny_if_forbidden_raises(self, surface: str) -> None:
        with pytest.raises(ObserverViolation, match="forbidden write surface"):
            deny_if_forbidden(surface)

    def test_deny_allows_read_surface(self) -> None:
        assert deny_if_forbidden("trace_read") is None


class TestStageBarrier:
    def test_pass_when_boundary_crossed_and_exit_present(self) -> None:
        r = stage_barrier_check(_bundle())
        assert r.barrier_status == "PASS"
        assert r.boundary_violation_flags == []

    def test_fail_when_boundary_not_crossed(self) -> None:
        r = stage_barrier_check(_bundle(runtime_boundary_crossed=False))
        assert r.barrier_status == "FAIL"
        assert "RUNTIME_BOUNDARY_NOT_CROSSED" in r.boundary_violation_flags

    def test_fail_when_exit_disposition_missing(self) -> None:
        r = stage_barrier_check(_bundle(exit_disposition_ref=None))
        assert r.barrier_status == "FAIL"
        assert "EXIT_DISPOSITION_MISSING" in r.boundary_violation_flags


class TestSurfaceIsolation:
    def test_clean_when_only_read_surfaces(self) -> None:
        m = build_surface_isolation_manifest(_bundle(), read_surfaces_touched=["trace_read"])
        assert m.isolation_status == "CLEAN"

    def test_violation_recorded_when_denied(self) -> None:
        bundle = _bundle()
        denied = record_denied_write_attempt(bundle, surface="L4", operation="write", reason_code="OBSERVER")
        m = build_surface_isolation_manifest(
            bundle,
            read_surfaces_touched=[],
            write_surfaces_requested=["L4"],
            denied_write_attempts=[denied],
        )
        assert m.isolation_status == "VIOLATION"
        assert m.l4_write_attempted is True

    def test_unknown_when_forbidden_hit_but_not_denied(self) -> None:
        m = build_surface_isolation_manifest(
            _bundle(),
            read_surfaces_touched=[],
            write_surfaces_requested=["BUS_U"],
        )
        assert m.isolation_status == "UNKNOWN"
        assert m.bus_u_publish_attempted is True

    def test_current_run_mutation_flagged(self) -> None:
        m = build_surface_isolation_manifest(
            _bundle(),
            read_surfaces_touched=[],
            write_surfaces_requested=["current_run_exit"],
        )
        assert m.current_run_mutation_attempted is True


class TestObserverComplianceReceipt:
    def test_clean_barrier_pass_no_violation(self) -> None:
        bundle = _bundle()
        barrier = stage_barrier_check(bundle)
        isolation = build_surface_isolation_manifest(bundle, read_surfaces_touched=["x"])
        receipt = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=isolation)
        assert receipt.violation_response is None
        assert receipt.no_l4_write_assertion is True

    def test_fail_barrier_sets_violation_response(self) -> None:
        bundle = _bundle(runtime_boundary_crossed=False)
        barrier = stage_barrier_check(bundle)
        isolation = build_surface_isolation_manifest(bundle, read_surfaces_touched=["x"])
        receipt = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=isolation)
        assert receipt.violation_response == "L6_OBSERVER_FAIL"


class TestEvaluateReadiness:
    def _observer(self, bundle: RuntimeExhaustBundle):
        barrier = stage_barrier_check(bundle)
        isolation = build_surface_isolation_manifest(bundle, read_surfaces_touched=["x"])
        return build_observer_compliance_receipt(bundle, barrier=barrier, isolation=isolation)

    def test_ready_when_all_present(self) -> None:
        bundle = _bundle()
        receipt, missing, non_eval = evaluate_readiness(bundle, self._observer(bundle), [_norm()])
        assert receipt.readiness_decision == READINESS_READY
        assert missing is None and non_eval is None

    def test_non_eval_when_trace_root_missing(self) -> None:
        bundle = _bundle(trace_root="")
        receipt, _missing, non_eval = evaluate_readiness(bundle, self._observer(bundle), [_norm()])
        assert receipt.readiness_decision == READINESS_NON_EVAL
        assert non_eval is not None
        assert "trace_root" in non_eval.reason_codes

    def test_hold_when_replay_key_missing_and_dependent(self) -> None:
        bundle = _bundle(replay_key=None)
        receipt, missing, _non_eval = evaluate_readiness(
            bundle, self._observer(bundle), [_norm()], replay_dependent=True
        )
        assert receipt.readiness_decision == READINESS_HOLD
        assert missing is not None and missing.blocking is True

    def test_partial_when_non_blocking_field_missing(self) -> None:
        # v40 requires policy identity before scoring, so missing policy holds.
        bundle = _bundle(policy_hash=None)
        receipt, missing, _non_eval = evaluate_readiness(
            bundle, self._observer(bundle), [_norm()], replay_dependent=False
        )
        assert receipt.readiness_decision == READINESS_HOLD
        assert missing is not None and missing.blocking is True

    def test_replay_key_missing_ok_when_not_dependent(self) -> None:
        bundle = _bundle(replay_key=None)
        receipt, _missing, _non_eval = evaluate_readiness(
            bundle, self._observer(bundle), [_norm()], replay_dependent=False
        )
        assert receipt.readiness_decision == READINESS_READY

    def test_non_eval_when_no_normalized_records(self) -> None:
        bundle = _bundle()
        receipt, missing, non_eval = evaluate_readiness(bundle, self._observer(bundle), [])
        assert receipt.readiness_decision == READINESS_HOLD
        assert missing is not None and missing.blocking is True
        assert non_eval is None
