"""Unit tests for required_receipts.py (W2.1)."""
from __future__ import annotations

from tools.certification.apps_e2e.app_specs import (
    AppSpec,
    EXECUTION_FORM_MANAGED_WORKFLOW,
    EXECUTION_FORM_SINGLE_STEP,
    L3_PATH_BYPASSED,
    L3_PATH_RAN,
    L3_PATH_UNKNOWN,
)
from tools.certification.apps_e2e.artifact_kinds import (
    TRACE_SLOT_KINDS,
    ArtifactKind,
)
from tools.certification.apps_e2e.required_receipts import (
    ReceiptRequirement,
    find_requirement,
    required_receipts,
    required_ref_fields,
)


def _spec(**kw) -> AppSpec:
    base = dict(
        app_name="apps_test", app_package="apps_test",
        runnable=True, expected_route_form="UNKNOWN",
        expects_static_dag=False, expects_c0_grounding=False,
        expects_prompt_assembly=False, expects_l2_execution=False,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_test/runs/*",
    )
    base.update(kw)
    return AppSpec(**base)


class TestAlwaysRequired:
    def test_route_contract_l1_plan_exit_always(self):
        # Even minimal spec must include route_contract, l1_plan_contract, exit_x3.
        reqs = required_receipts(_spec())
        fields = {r.ref_field for r in reqs}
        assert "runtime_route_contract_ref" in fields
        assert "runtime_l1_plan_ref" in fields
        assert "runtime_exit_disposition_ref" in fields

    def test_exit_required_is_separate_from_exhaust(self):
        # Per amendment 1: Exit is implicit-always; exhaust is gated by flag.
        reqs_with_exhaust = required_receipts(_spec(l6_exhaust_required=True))
        reqs_no_exhaust = required_receipts(_spec(l6_exhaust_required=False))

        exit_in_both = (
            "runtime_exit_disposition_ref" in {r.ref_field for r in reqs_with_exhaust}
            and "runtime_exit_disposition_ref" in {r.ref_field for r in reqs_no_exhaust}
        )
        assert exit_in_both, "Exit must be required regardless of l6_exhaust_required"

        # Exhaust gated by flag.
        assert "runtime_exhaust_ref" in {r.ref_field for r in reqs_with_exhaust}
        assert "runtime_exhaust_ref" not in {r.ref_field for r in reqs_no_exhaust}

    def test_otel_default_required(self):
        reqs = required_receipts(_spec())
        otel_req = find_requirement(_spec(), "otel_or_runtime_trace_ref")
        assert otel_req is not None
        assert otel_req.is_kind_set
        assert otel_req.kind_matches("otel_trace")
        assert otel_req.kind_matches("runtime_adg_trace")
        assert not otel_req.kind_matches("route_contract")

    def test_otel_can_be_disabled(self):
        reqs = required_receipts(_spec(otel_required=False))
        assert "otel_or_runtime_trace_ref" not in {r.ref_field for r in reqs}


class TestL3Path:
    def test_managed_workflow_with_RAN_path(self):
        s = _spec(
            expected_execution_form=EXECUTION_FORM_MANAGED_WORKFLOW,
            expected_l3_path=L3_PATH_RAN,
        )
        reqs = required_receipts(s)
        fields = {r.ref_field for r in reqs}
        assert "runtime_l3_receipt_ref" in fields
        assert "runtime_l3_bypass_ref" not in fields

    def test_single_step_with_BYPASSED_path(self):
        s = _spec(
            expected_execution_form=EXECUTION_FORM_SINGLE_STEP,
            expected_l3_path=L3_PATH_BYPASSED,
        )
        reqs = required_receipts(s)
        fields = {r.ref_field for r in reqs}
        assert "runtime_l3_bypass_ref" in fields
        assert "runtime_l3_receipt_ref" not in fields

    def test_unknown_l3_path_adds_neither(self):
        s = _spec(expected_l3_path=L3_PATH_UNKNOWN)
        reqs = required_receipts(s)
        fields = {r.ref_field for r in reqs}
        assert "runtime_l3_receipt_ref" not in fields
        assert "runtime_l3_bypass_ref" not in fields

    def test_explicit_l3_required_does_not_override_path_xor(self):
        # Even if l3_required=True is set, the BYPASSED path means we want
        # the bypass receipt, not a runtime receipt.
        s = _spec(expected_l3_path=L3_PATH_BYPASSED, l3_required=True)
        reqs = required_receipts(s)
        fields = {r.ref_field for r in reqs}
        assert "runtime_l3_bypass_ref" in fields
        assert "runtime_l3_receipt_ref" not in fields


class TestOptionalSurfaces:
    def test_c0_added_when_required(self):
        reqs = required_receipts(_spec(c0_required=True))
        assert "runtime_c0_receipt_ref" in {r.ref_field for r in reqs}

    def test_c0_legacy_alias(self):
        # expects_c0_grounding=True without c0_required also pulls it in.
        reqs = required_receipts(_spec(expects_c0_grounding=True))
        assert "runtime_c0_receipt_ref" in {r.ref_field for r in reqs}

    def test_prompt_assembly(self):
        reqs = required_receipts(_spec(prompt_assembly_required=True))
        assert "runtime_prompt_assembly_ref" in {r.ref_field for r in reqs}

    def test_l2(self):
        reqs = required_receipts(_spec(l2_required=True))
        assert "runtime_l2_artifact_ref" in {r.ref_field for r in reqs}

    def test_uwg(self):
        reqs = required_receipts(_spec(uwg_required=True))
        assert "runtime_uwg_receipt_ref" in {r.ref_field for r in reqs}

    def test_static_dag(self):
        reqs = required_receipts(_spec(expects_static_dag=True))
        assert "static_dag_ref" in {r.ref_field for r in reqs}


class TestKindBindings:
    def test_route_contract_kind(self):
        r = find_requirement(_spec(), "runtime_route_contract_ref")
        assert r is not None
        assert r.expected_kind == ArtifactKind.route_contract
        assert r.kind_matches("route_contract")
        assert not r.kind_matches("l1_plan_contract")

    def test_otel_slot_accepts_both_trace_kinds(self):
        r = find_requirement(_spec(), "otel_or_runtime_trace_ref")
        assert r is not None
        assert r.is_kind_set
        assert r.expected_kind == TRACE_SLOT_KINDS

    def test_kind_match_rejects_none(self):
        r = find_requirement(_spec(), "runtime_route_contract_ref")
        assert r is not None
        assert r.kind_matches(None) is False


class TestRequiredRefFields:
    def test_returns_just_field_names(self):
        fields = required_ref_fields(_spec())
        assert isinstance(fields, tuple)
        assert all(isinstance(f, str) for f in fields)
        assert "runtime_route_contract_ref" in fields


class TestNonEmptyFloor:
    def test_minimal_runnable_spec_has_nonempty_floor(self):
        reqs = required_receipts(_spec())
        assert len(reqs) >= 3  # route + l1 + exit
