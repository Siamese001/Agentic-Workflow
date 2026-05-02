"""Unit tests for CertificationLevel enum + compute_level() (W1.2, plan §3 + amendment 4).

Critical invariant tested here: compute_level is the SINGLE authority for
certification_level. The bundle's self-declared level is NEVER trusted —
this is amendment 4. Several tests assert that a hand-authored
certification_level=SPINE_COMPLETE_CERTIFIED in the bundle does not let a
weaker bundle pass.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.certification.apps_e2e.app_specs import (
    AppSpec,
    EXECUTION_FORM_SINGLE_STEP,
    L3_PATH_BYPASSED,
)
from tools.certification.apps_e2e.certification_levels import (
    APPROVED_LIVE_MODES,
    CertificationLevel,
    PASSING_LEVELS,
    RUNTIME_MODE_DRY_RUN_SHORT_CIRCUIT,
    RUNTIME_MODE_FIXTURE,
    RUNTIME_MODE_LIVE_RUN,
    RUNTIME_MODE_MOCK,
    RUNTIME_MODE_SKELETON_ONLY,
    RUNTIME_MODE_STANDALONE_ORCHESTRATOR,
    RUNTIME_MODE_UNKNOWN,
    VALID_RUNTIME_MODE_CLASSIFICATIONS,
    WAIVED_LEVELS,
    classify_runtime_mode,
    compute_level,
)


def _spec(**overrides) -> AppSpec:
    base = dict(
        app_name="apps_test",
        app_package="apps_test",
        runnable=True,
        expected_route_form="UNKNOWN",
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_l2_execution=False,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_test/runs/*",
    )
    base.update(overrides)
    return AppSpec(**base)


def _bundle(
    *,
    success=False,
    blocking_gaps=None,
    runtime_mode="live_run",
    mock=False,
    fixture_runtime=False,
    fixture_data=False,
    synthetic=False,
    declared_level=None,
):
    b = {
        "success": success,
        "blocking_gaps": list(blocking_gaps or []),
        "runtime_mode": runtime_mode,
        "mock_mode_detected": mock,
        "fixture_runtime_mode": fixture_runtime,
        "fixture_data_used": fixture_data,
        "synthetic_trace_detected": synthetic,
        "harness_pass": True,
        "run_id": "test-run-id",
    }
    if declared_level is not None:
        b["certification_level"] = declared_level  # tests trust-the-level invariant
    return b


# ---------------------------------------------------------------------------
# CertificationLevel enum surface
# ---------------------------------------------------------------------------


class TestCertificationLevelEnum:
    def test_five_canonical_values(self):
        vals = CertificationLevel.values()
        assert vals == frozenset({
            "EMITS_BUNDLE",
            "FAILS_CLOSED_WITH_GAPS",
            "SPINE_COMPLETE_CERTIFIED",
            "WAIVED_SKELETON",
            "WAIVED_NOT_RUNTIME_APP",
        })

    def test_passing_levels_set(self):
        assert CertificationLevel.SPINE_COMPLETE_CERTIFIED in PASSING_LEVELS
        assert CertificationLevel.WAIVED_SKELETON in PASSING_LEVELS
        assert CertificationLevel.WAIVED_NOT_RUNTIME_APP in PASSING_LEVELS
        # FAILS_CLOSED_WITH_GAPS and EMITS_BUNDLE are NOT passing levels.
        assert CertificationLevel.FAILS_CLOSED_WITH_GAPS not in PASSING_LEVELS
        assert CertificationLevel.EMITS_BUNDLE not in PASSING_LEVELS

    def test_waived_levels_set(self):
        assert WAIVED_LEVELS == frozenset({
            CertificationLevel.WAIVED_SKELETON,
            CertificationLevel.WAIVED_NOT_RUNTIME_APP,
        })


# ---------------------------------------------------------------------------
# classify_runtime_mode
# ---------------------------------------------------------------------------


class TestClassifyRuntimeMode:
    def test_mock_takes_precedence(self):
        assert classify_runtime_mode(_bundle(mock=True)) == RUNTIME_MODE_MOCK

    def test_fixture_runtime(self):
        assert classify_runtime_mode(_bundle(fixture_runtime=True)) == RUNTIME_MODE_FIXTURE

    def test_synthetic_trace_classified_as_mock(self):
        assert classify_runtime_mode(_bundle(synthetic=True)) == RUNTIME_MODE_MOCK

    def test_fixture_data_used_does_NOT_downgrade(self):
        # Amendment 3: deterministic INPUT data is allowed in strict mode.
        b = _bundle(fixture_data=True, runtime_mode="live_run")
        assert classify_runtime_mode(b) == RUNTIME_MODE_LIVE_RUN

    def test_skeleton_only(self):
        assert classify_runtime_mode(_bundle(runtime_mode="skeleton_only")) == RUNTIME_MODE_SKELETON_ONLY

    def test_dry_run(self):
        assert classify_runtime_mode(_bundle(runtime_mode="dry_run_short_circuit")) == RUNTIME_MODE_DRY_RUN_SHORT_CIRCUIT

    def test_standalone_orchestrator(self):
        assert classify_runtime_mode(_bundle(runtime_mode="standalone_orchestrator_pre_spine")) == RUNTIME_MODE_STANDALONE_ORCHESTRATOR

    def test_governed_spine_active_maps_to_live_run(self):
        # Backward-compat: existing apps_rg bundles emit governed_spine_active.
        assert classify_runtime_mode(_bundle(runtime_mode="governed_spine_active")) == RUNTIME_MODE_LIVE_RUN

    def test_live_run_passthrough(self):
        assert classify_runtime_mode(_bundle(runtime_mode="live_run")) == RUNTIME_MODE_LIVE_RUN

    def test_unknown_value_returns_unknown(self):
        assert classify_runtime_mode(_bundle(runtime_mode="not_a_mode")) == RUNTIME_MODE_UNKNOWN

    def test_empty_runtime_mode(self):
        b = _bundle()
        b["runtime_mode"] = ""
        assert classify_runtime_mode(b) == RUNTIME_MODE_UNKNOWN

    def test_classification_in_valid_enum(self):
        for raw in ("live_run", "governed_spine_active", "skeleton_only", "dry_run_short_circuit", "standalone_orchestrator_pre_spine", "fail_closed", "weird"):
            cls = classify_runtime_mode(_bundle(runtime_mode=raw))
            assert cls in VALID_RUNTIME_MODE_CLASSIFICATIONS

    def test_approved_live_modes_is_only_live_run(self):
        assert APPROVED_LIVE_MODES == frozenset({RUNTIME_MODE_LIVE_RUN})


# ---------------------------------------------------------------------------
# compute_level — the seven scenarios from the user's test list
# ---------------------------------------------------------------------------


class TestComputeLevel_BasicScenarios:
    def test_valid_bundle_only_yields_emits_bundle(self):
        # Bundle is valid (success=False, no gaps, runtime_mode=unknown) — by
        # plan §3 this is EMITS_BUNDLE because we have neither a clean
        # failure nor a clean success.
        spec = _spec()
        b = _bundle(success=False, blocking_gaps=[], runtime_mode="standalone_orchestrator_pre_spine")
        level = compute_level(b, spec, violations=[])
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_fails_closed_with_gaps(self):
        spec = _spec()
        b = _bundle(
            success=False,
            blocking_gaps=["no_route_contract", "no_l1_plan", "no_exit_disposition"],
            runtime_mode="standalone_orchestrator_pre_spine",
        )
        level = compute_level(b, spec, violations=[])
        assert level == CertificationLevel.FAILS_CLOSED_WITH_GAPS

    def test_fails_closed_with_dict_gaps(self):
        spec = _spec()
        b = _bundle(
            success=False,
            blocking_gaps=[
                {"rule_id": "no_route", "stage": "l0"},
                {"rule_id": "no_l1", "stage": "l1"},
            ],
            runtime_mode="standalone_orchestrator_pre_spine",
        )
        level = compute_level(b, spec, violations=[])
        assert level == CertificationLevel.FAILS_CLOSED_WITH_GAPS

    def test_spine_complete_certified(self):
        spec = _spec(
            expected_execution_form=EXECUTION_FORM_SINGLE_STEP,
            expected_l3_path=L3_PATH_BYPASSED,
        )
        b = _bundle(
            success=True,
            blocking_gaps=[],
            runtime_mode="live_run",
        )
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.SPINE_COMPLETE_CERTIFIED

    def test_spine_complete_certified_with_governed_spine_active_alias(self):
        # The existing apps_rg bundle today emits "governed_spine_active";
        # certification must still be reachable via the alias path.
        spec = _spec(
            expected_execution_form=EXECUTION_FORM_SINGLE_STEP,
            expected_l3_path=L3_PATH_BYPASSED,
        )
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="governed_spine_active")
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.SPINE_COMPLETE_CERTIFIED

    def test_certified_path_rejects_dry_run_runtime(self):
        # Even with success=True and no gaps, a dry-run-short-circuit
        # runtime_mode disqualifies the bundle from SPINE_COMPLETE_CERTIFIED.
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="dry_run_short_circuit")
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE


class TestComputeLevel_Waivers:
    def test_waived_skeleton_with_valid_waiver(self):
        future = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat().replace("+00:00", "Z")
        spec = _spec(
            runnable=False,
            waiver_reason="No __init__/__main__",
            waiver_owner="owner@example.com",
            waiver_expiry=future,
        )
        level = compute_level(None, spec, violations=[])
        assert level == CertificationLevel.WAIVED_SKELETON

    def test_skeleton_without_waiver_drops_to_emits_bundle(self):
        spec = _spec(runnable=False)
        level = compute_level(None, spec, violations=[])
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_skeleton_with_expired_waiver_drops(self):
        past = "2020-01-01T00:00:00Z"
        spec = _spec(
            runnable=False,
            waiver_reason="why",
            waiver_owner="who",
            waiver_expiry=past,
        )
        level = compute_level(None, spec, violations=[])
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_waived_not_runtime_app_with_valid_waiver(self):
        future = (datetime.now(timezone.utc) + timedelta(days=180)).isoformat().replace("+00:00", "Z")
        spec = _spec(
            certification_required=False,
            waiver_reason="Pack-builder app — not a managed-runtime workflow",
            waiver_owner="owner@example.com",
            waiver_expiry=future,
        )
        b = _bundle(success=False, blocking_gaps=["no_l3_receipt"])
        level = compute_level(b, spec, violations=[])
        assert level == CertificationLevel.WAIVED_NOT_RUNTIME_APP

    def test_certification_not_required_without_waiver_drops(self):
        spec = _spec(certification_required=False)
        level = compute_level(_bundle(), spec, violations=[])
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_waiver_with_unparseable_expiry_invalid(self):
        spec = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="not-a-date",
        )
        assert compute_level(None, spec, violations=[]) == CertificationLevel.EMITS_BUNDLE

    def test_waiver_with_naive_expiry_invalid(self):
        # ISO without tz suffix — must be rejected.
        spec = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="2099-01-01T00:00:00",
        )
        assert compute_level(None, spec, violations=[]) == CertificationLevel.EMITS_BUNDLE


class TestComputeLevel_TrustInvariant:
    """Amendment 4: the bundle's self-declared certification_level is NEVER trusted."""

    def test_bundle_declaring_certified_does_not_grant_certified(self):
        # Hand-author a bundle with success=False AND
        # certification_level=SPINE_COMPLETE_CERTIFIED. The verifier MUST
        # ignore the self-declaration and recompute as FAILS_CLOSED_WITH_GAPS.
        spec = _spec()
        b = _bundle(
            success=False,
            blocking_gaps=["no_route_contract"],
            runtime_mode="live_run",
            declared_level="SPINE_COMPLETE_CERTIFIED",
        )
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        # Must NOT trust the bundle's hand-authored claim.
        assert level == CertificationLevel.FAILS_CLOSED_WITH_GAPS

    def test_bundle_declaring_emits_bundle_does_not_block_certified(self):
        # Inverse case: a real cert path with declared_level="EMITS_BUNDLE"
        # in the bundle. The verifier must STILL compute SPINE_COMPLETE_CERTIFIED.
        spec = _spec()
        b = _bundle(
            success=True,
            blocking_gaps=[],
            runtime_mode="live_run",
            declared_level="EMITS_BUNDLE",
        )
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.SPINE_COMPLETE_CERTIFIED

    def test_success_true_with_nonempty_gaps_drops_to_emits_bundle(self):
        # Critical invariant: success=True paired with non-empty gaps is a
        # fabrication signal. compute_level refuses to award FAILS_CLOSED_WITH_GAPS
        # (because success=True) AND refuses SPINE_COMPLETE_CERTIFIED (because
        # gaps non-empty). Drops to EMITS_BUNDLE; verifier S8 emits the
        # success_true_with_nonempty_gaps violation separately.
        spec = _spec()
        b = _bundle(
            success=True,
            blocking_gaps=["something"],
            runtime_mode="live_run",
        )
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE


class TestComputeLevel_ViolationDowngrade:
    def test_schema_violation_drops_to_emits_bundle(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run")

        class V:
            rule_id = "bundle_missing_required_field"

        level = compute_level(b, spec, violations=[V()], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_non_schema_violation_blocks_certified_but_keeps_path_open(self):
        # A non-schema violation blocks SPINE_COMPLETE_CERTIFIED (because
        # viols list is non-empty) and the bundle has success=True with
        # no gaps, so neither FAILS_CLOSED_WITH_GAPS nor SPINE_COMPLETE_CERTIFIED.
        # Result: EMITS_BUNDLE.
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run")

        class V:
            rule_id = "duplicate_route_contract"

        level = compute_level(b, spec, violations=[V()], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_violation_as_dict(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run")
        v = {"rule_id": "bundle_missing_required_field", "stage": "schema"}
        level = compute_level(b, spec, violations=[v], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_violation_as_string_alias(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run")
        level = compute_level(
            b, spec,
            violations=["bundle_missing_required_field"],
            required_receipts_present=True,
        )
        assert level == CertificationLevel.EMITS_BUNDLE


class TestComputeLevel_FixturePolicy:
    """Amendment 3 — fixture data legit; fixture runtime rejected."""

    def test_fixture_data_used_with_live_run_can_certify(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run", fixture_data=True)
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.SPINE_COMPLETE_CERTIFIED

    def test_fixture_runtime_mode_blocks_cert(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run", fixture_runtime=True)
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_mock_mode_blocks_cert(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run", mock=True)
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_synthetic_trace_blocks_cert(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run", synthetic=True)
        level = compute_level(b, spec, violations=[], required_receipts_present=True)
        assert level == CertificationLevel.EMITS_BUNDLE


class TestComputeLevel_ReceiptSignal:
    def test_required_receipts_absent_blocks_cert(self):
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run")
        level = compute_level(b, spec, violations=[], required_receipts_present=False)
        # Receipts known to be absent → cannot award SPINE_COMPLETE_CERTIFIED.
        # success=True + empty gaps means we don't fall into FAILS_CLOSED_WITH_GAPS either.
        assert level == CertificationLevel.EMITS_BUNDLE

    def test_required_receipts_unknown_default_does_not_block(self):
        # When the caller doesn't pass required_receipts_present (W2.1 not
        # yet wired), compute_level treats it as "no information available"
        # and does NOT downgrade.
        spec = _spec()
        b = _bundle(success=True, blocking_gaps=[], runtime_mode="live_run")
        level = compute_level(b, spec, violations=[])  # default None
        assert level == CertificationLevel.SPINE_COMPLETE_CERTIFIED


class TestComputeLevel_Determinism:
    def test_now_parameter_controls_waiver_expiry(self):
        # An expiry in 2030 is "future" if now=2025 but "past" if now=2040.
        spec = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="2030-06-01T00:00:00Z",
        )
        now_2025 = datetime(2025, 1, 1, tzinfo=timezone.utc)
        now_2040 = datetime(2040, 1, 1, tzinfo=timezone.utc)
        assert compute_level(None, spec, violations=[], now=now_2025) == CertificationLevel.WAIVED_SKELETON
        assert compute_level(None, spec, violations=[], now=now_2040) == CertificationLevel.EMITS_BUNDLE

    def test_pure_function_no_global_state(self):
        # Calling compute_level twice with identical args produces identical results.
        spec = _spec()
        b = _bundle(success=False, blocking_gaps=["a"], runtime_mode="standalone_orchestrator_pre_spine")
        a1 = compute_level(b, spec, violations=[])
        a2 = compute_level(b, spec, violations=[])
        assert a1 == a2 == CertificationLevel.FAILS_CLOSED_WITH_GAPS
