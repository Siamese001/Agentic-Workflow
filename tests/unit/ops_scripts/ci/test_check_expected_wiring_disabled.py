"""Tests for the ``disabled:`` opt-out on individual wiring rows.

Plan: ``adg-expected-wiring-drift-cleanup``. Adds a single-row escape hatch
to the wiring gate so a row may carry ``disabled: true`` plus a
``disabled_reason`` and be skipped without removing the contract from the
yaml. Use cases:

  * Real architectural debt where the call IS missing AND a separate plan
    owns the fix (avoids double-tracking the failure here).
  * Lazy-factory indirection patterns the AST walker cannot resolve when
    the proof_test already validates the runtime behaviour.
"""

from __future__ import annotations

# pylint: disable=protected-access
# Note: module-private _check_row is the unit under test, so protected-access
# warnings on every call site are unavoidable and not actionable.

from typing import Any

from ops_scripts.ci import check_expected_wiring as gate


def _row(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "fixture-row",
        "entry_module": "agentic_core/L0_routing/reasoning/execution_orchestrator.py",
        "entry_symbol": "ExecutionOrchestrator.execute",
        "required_call": "this_call_does_not_exist_anywhere_in_the_repo",
        "required_env_flags": [],
    }
    base.update(overrides)
    return base


class TestDisabledFlag:
    def test_disabled_true_short_circuits_to_zero_errors(self) -> None:
        row = _row(disabled=True)
        assert gate._check_row(row) == []

    def test_disabled_true_skips_even_with_unresolvable_required_call(self) -> None:
        # Without disabled, this row would emit "required_call ... not invoked"
        row = _row(disabled=True, required_call="absolutely_not_called_anywhere")
        assert gate._check_row(row) == []

    def test_disabled_false_runs_the_check_normally(self) -> None:
        row = _row(disabled=False)
        errors = gate._check_row(row)
        assert errors, "disabled=False must NOT skip; row should produce a real failure"
        assert any("not invoked" in e or "not found" in e for e in errors)

    def test_disabled_absent_runs_the_check_normally(self) -> None:
        row = _row()  # no disabled key at all
        errors = gate._check_row(row)
        assert errors, "absent disabled must NOT skip; row should produce a real failure"

    def test_disabled_truthy_string_skips(self) -> None:
        # YAML scalar "true" decodes to bool, but defensively accept any truthy
        row = _row(disabled="yes")
        assert gate._check_row(row) == []

    def test_disabled_falsy_zero_runs_normally(self) -> None:
        row = _row(disabled=0)
        errors = gate._check_row(row)
        assert errors

    def test_disabled_with_reason_field_skips_and_preserves_reason(self) -> None:
        row = _row(
            disabled=True,
            disabled_reason="real architectural debt; plan owns the fix",
        )
        assert gate._check_row(row) == []
        # Reason field is descriptive only — the gate doesn't validate it.
        assert row["disabled_reason"]
