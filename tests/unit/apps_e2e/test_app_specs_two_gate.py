"""Unit tests for two-gate certification fields on AppSpec.

Covers W1.1 of plan apps-e2e-two-gate-certification-d8b3a1:
- 12 new fields default to backward-compatible values
- effective_*_required() resolvers fall back to legacy expects_* aliases
- effective_l3_required defaults from expected_l3_path
- has_waiver() requires the full triple
- VALID_EXECUTION_FORMS / VALID_L3_PATHS enums match field type
"""
from __future__ import annotations

from tools.certification.apps_e2e.app_specs import (
    APP_SPECS,
    AppSpec,
    EXECUTION_FORM_MANAGED_WORKFLOW,
    EXECUTION_FORM_SINGLE_STEP,
    EXECUTION_FORM_TERMINAL_SHORTCIRCUIT,
    EXECUTION_FORM_UNKNOWN,
    L3_PATH_BYPASSED,
    L3_PATH_RAN,
    L3_PATH_UNKNOWN,
    VALID_EXECUTION_FORMS,
    VALID_L3_PATHS,
    effective_c0_required,
    effective_l2_required,
    effective_l3_required,
    effective_l6_exhaust_required,
    effective_otel_required,
    effective_prompt_assembly_required,
    effective_uwg_required,
    has_waiver,
)


def _make_spec(**overrides) -> AppSpec:
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


class TestNewFieldDefaults:
    def test_defaults_are_backward_compatible(self):
        s = _make_spec()
        # All 12 new fields default to backward-compat values.
        assert s.certification_required is True
        assert s.expected_execution_form == EXECUTION_FORM_UNKNOWN
        assert s.expected_l3_path == L3_PATH_UNKNOWN
        assert s.c0_required is None
        assert s.prompt_assembly_required is None
        assert s.l2_required is None
        assert s.l3_required is None
        assert s.uwg_required is None
        assert s.l6_exhaust_required is True
        assert s.otel_required is True
        assert s.waiver_reason is None
        assert s.waiver_owner is None
        assert s.waiver_expiry is None

    def test_existing_7_specs_load_with_defaults(self):
        # Regression: extending AppSpec must not break the live registry.
        # Post-W6: certification_required may be False on waived apps; all
        # other invariants still hold.
        assert len(APP_SPECS) == 7
        for s in APP_SPECS:
            assert isinstance(s.certification_required, bool)
            assert s.expected_execution_form in VALID_EXECUTION_FORMS
            assert s.expected_l3_path in VALID_L3_PATHS


class TestEffectiveResolvers:
    def test_c0_falls_back_to_legacy_alias_when_none(self):
        assert effective_c0_required(_make_spec(expects_c0_grounding=True)) is True
        assert effective_c0_required(_make_spec(expects_c0_grounding=False)) is False

    def test_c0_explicit_overrides_legacy(self):
        # legacy=True but new=False → new wins
        s = _make_spec(expects_c0_grounding=True, c0_required=False)
        assert effective_c0_required(s) is False
        # legacy=False but new=True → new wins
        s = _make_spec(expects_c0_grounding=False, c0_required=True)
        assert effective_c0_required(s) is True

    def test_prompt_assembly_resolver(self):
        assert effective_prompt_assembly_required(_make_spec(expects_prompt_assembly=True)) is True
        assert effective_prompt_assembly_required(
            _make_spec(expects_prompt_assembly=True, prompt_assembly_required=False)
        ) is False

    def test_l2_resolver(self):
        assert effective_l2_required(_make_spec(expects_l2_execution=True)) is True
        assert effective_l2_required(
            _make_spec(expects_l2_execution=False, l2_required=True)
        ) is True

    def test_uwg_resolver(self):
        assert effective_uwg_required(_make_spec(expects_durable_mutation=True)) is True
        assert effective_uwg_required(
            _make_spec(expects_durable_mutation=True, uwg_required=False)
        ) is False

    def test_l3_required_defaults_from_expected_l3_path(self):
        # RAN → l3_required=True
        assert effective_l3_required(_make_spec(expected_l3_path=L3_PATH_RAN)) is True
        # BYPASSED → l3_required=False (bypass receipt is a different ref)
        assert effective_l3_required(_make_spec(expected_l3_path=L3_PATH_BYPASSED)) is False
        # UNKNOWN → l3_required=False
        assert effective_l3_required(_make_spec(expected_l3_path=L3_PATH_UNKNOWN)) is False

    def test_l3_required_explicit_overrides_path_default(self):
        # BYPASSED + explicit l3_required=True → True (explicit wins)
        s = _make_spec(expected_l3_path=L3_PATH_BYPASSED, l3_required=True)
        assert effective_l3_required(s) is True
        # RAN + explicit l3_required=False → False
        s = _make_spec(expected_l3_path=L3_PATH_RAN, l3_required=False)
        assert effective_l3_required(s) is False

    def test_l6_exhaust_resolver(self):
        # No legacy alias — direct field
        assert effective_l6_exhaust_required(_make_spec(l6_exhaust_required=True)) is True
        assert effective_l6_exhaust_required(_make_spec(l6_exhaust_required=False)) is False

    def test_otel_resolver(self):
        assert effective_otel_required(_make_spec(otel_required=True)) is True
        assert effective_otel_required(_make_spec(otel_required=False)) is False


class TestWaiverHelper:
    def test_no_waiver_when_all_none(self):
        assert has_waiver(_make_spec()) is False

    def test_no_waiver_when_only_reason_set(self):
        assert has_waiver(_make_spec(waiver_reason="why")) is False

    def test_no_waiver_when_only_two_of_three_set(self):
        assert has_waiver(
            _make_spec(waiver_reason="why", waiver_owner="who")
        ) is False
        assert has_waiver(
            _make_spec(waiver_owner="who", waiver_expiry="2027-01-01T00:00:00Z")
        ) is False

    def test_has_waiver_when_full_triple_set(self):
        assert has_waiver(
            _make_spec(
                waiver_reason="why",
                waiver_owner="who",
                waiver_expiry="2027-01-01T00:00:00Z",
            )
        ) is True

    def test_empty_string_does_not_count(self):
        # Empty strings are falsy; the helper requires non-empty values.
        assert has_waiver(
            _make_spec(waiver_reason="", waiver_owner="who", waiver_expiry="2027-01-01T00:00:00Z")
        ) is False


class TestEnumValidity:
    def test_valid_execution_forms_are_strings(self):
        assert EXECUTION_FORM_TERMINAL_SHORTCIRCUIT in VALID_EXECUTION_FORMS
        assert EXECUTION_FORM_SINGLE_STEP in VALID_EXECUTION_FORMS
        assert EXECUTION_FORM_MANAGED_WORKFLOW in VALID_EXECUTION_FORMS
        assert EXECUTION_FORM_UNKNOWN in VALID_EXECUTION_FORMS
        # BYPASS is explicitly NOT a valid execution form per amendment 2
        assert "BYPASS" not in VALID_EXECUTION_FORMS

    def test_valid_l3_paths(self):
        assert L3_PATH_RAN in VALID_L3_PATHS
        assert L3_PATH_BYPASSED in VALID_L3_PATHS
        assert L3_PATH_UNKNOWN in VALID_L3_PATHS
