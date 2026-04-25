"""Unit tests for PA.5 budget contracts."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.pa5_budget import (
    BUDGET_TRIM_ORDER,
    BudgetClass,
    OverflowStatus,
    SlotBudgetEntry,
    build_budget_report,
    deterministic_trim,
)


def _entries() -> list[SlotBudgetEntry]:
    return [
        SlotBudgetEntry("S0", 100, BudgetClass.MANDATORY_NEVER_TRIM),
        SlotBudgetEntry("D0", 50, BudgetClass.MANDATORY_NEVER_TRIM),
        SlotBudgetEntry("I0", 200, BudgetClass.MANDATORY_COMPRESS_CAREFULLY),
        SlotBudgetEntry("E0:ex1", 300, BudgetClass.OPTIONAL_TRIM_FIRST),
        SlotBudgetEntry("E0:ex2", 300, BudgetClass.OPTIONAL_TRIM_FIRST),
        SlotBudgetEntry("C0:must_use", 400, BudgetClass.MANDATORY_NEVER_TRIM, must_use=True),
        SlotBudgetEntry("C0:supporting_redundant", 250, BudgetClass.OPTIONAL_TRIM_FIRST),
        SlotBudgetEntry("C0:background", 500, BudgetClass.DROP_WITH_REASON),
        SlotBudgetEntry("HISTORY:irrelevant", 350, BudgetClass.DROP_WITH_REASON),
        SlotBudgetEntry("U0", 100, BudgetClass.MANDATORY_NEVER_TRIM),
    ]


def test_trim_order_exposes_ten_steps():
    assert len(BUDGET_TRIM_ORDER) == 10
    assert BUDGET_TRIM_ORDER[0][1] == "remove_irrelevant_conversation_history"
    assert BUDGET_TRIM_ORDER[9][1] == "overflow_refine_abstain"


def test_no_trim_when_under_budget():
    kept, actions, dropped, status = deterministic_trim(_entries(), available_input_tokens=10_000)
    assert status is OverflowStatus.OK
    assert actions == []
    assert dropped == []
    assert len(kept) == len(_entries())


def test_trim_drops_history_first_then_exemplars_then_background():
    # Total tokens = 100+50+200+300+300+400+250+500+350+100 = 2550. Cap at 1500.
    kept, actions, dropped, status = deterministic_trim(_entries(), available_input_tokens=1500)
    dropped_labels = [label for label, _r in dropped]
    # HISTORY:irrelevant must be removed before E0 exemplars
    assert "HISTORY:irrelevant" in dropped_labels
    # Step 1 must precede step 3 in actions
    step_ids = [int(a.split(":", 1)[0].split("_")[1]) for a in actions if a.startswith("step_")]
    assert step_ids == sorted(step_ids), "trim actions must run in canonical step order"
    # Status reflects trim happened
    assert status in {OverflowStatus.TRIMMED, OverflowStatus.OK}
    # Must-use evidence must survive
    must_use_labels = {e.label for e in kept if e.must_use}
    assert "C0:must_use" in must_use_labels
    # Mandatory-never-trim must survive
    assert any(e.label == "S0" for e in kept)
    assert any(e.label == "D0" for e in kept)
    assert any(e.label == "U0" for e in kept)


def test_overflow_when_must_use_alone_exceeds_cap():
    only_mandatory = [
        SlotBudgetEntry("S0", 500, BudgetClass.MANDATORY_NEVER_TRIM),
        SlotBudgetEntry("C0:must_use", 5_000, BudgetClass.MANDATORY_NEVER_TRIM, must_use=True),
    ]
    kept, actions, dropped, status = deterministic_trim(only_mandatory, available_input_tokens=1_000)
    # Cannot drop any; overflow recommended
    assert status is OverflowStatus.REFINE
    assert dropped == []


def test_build_budget_report_populates_all_fields():
    report, kept = build_budget_report(
        model_context_window=10_000,
        reserved_output_tokens=2000,
        reserved_schema_tokens=200,
        reserved_tool_tokens=300,
        entries=_entries(),
    )
    assert report.model_context_window == 10_000
    assert report.reserved_output_tokens == 2000
    assert report.reserved_schema_tokens == 200
    assert report.reserved_tool_tokens == 300
    # Stable prefix = S0 + D0 + I0 = 350
    assert report.stable_prefix_tokens == 350
    assert report.u0_tokens == 100
    assert report.can_dispatch is True
    assert report.overflow_status in {OverflowStatus.OK, OverflowStatus.TRIMMED}
    # Round-trip dict
    d = report.to_dict()
    assert d["overflow_status"] in {"OK", "TRIMMED"}


def test_build_budget_report_non_positive_input_budget_refines():
    report, kept = build_budget_report(
        model_context_window=1000,
        reserved_output_tokens=900,
        reserved_schema_tokens=200,
        reserved_tool_tokens=200,
        entries=_entries(),
    )
    assert report.can_dispatch is False
    assert report.overflow_status is OverflowStatus.REFINE


def test_trim_is_deterministic_with_same_input():
    # Two runs with identical input must produce identical output
    e = _entries()
    a1 = deterministic_trim(e, available_input_tokens=1500)
    a2 = deterministic_trim(_entries(), available_input_tokens=1500)
    assert [x.label for x in a1[0]] == [x.label for x in a2[0]]
    assert a1[1] == a2[1]
    assert a1[2] == a2[2]
    assert a1[3] is a2[3]


def test_trim_preserves_must_use_even_when_drop_with_reason():
    must_use_drop = [
        SlotBudgetEntry("C0:supporting", 50, BudgetClass.DROP_WITH_REASON, must_use=True),
        SlotBudgetEntry("C0:background", 5000, BudgetClass.DROP_WITH_REASON),
    ]
    kept, _actions, _dropped, _status = deterministic_trim(must_use_drop, available_input_tokens=100)
    # must_use entry must NEVER be removed even if its budget_class is DROP_WITH_REASON
    assert any(e.label == "C0:supporting" for e in kept)
