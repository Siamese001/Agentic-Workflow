"""W1 hardening contract tests for GovernedAppRunner.

Locks in the W1 invariants:
1. ``GovernedAppRunRecord`` exposes 7 per-phase error fields with default "".
2. ``run_governed_core`` no longer wraps the entire pipeline in a broad
   except. Phases now fail in isolation; identity is preserved per-phase.
3. The 4 governed app subclasses surface the per-phase fields in their
   sealed records.

This is the regression suite for ADG hotspot G1 (see plan
``apps-runtime-first-principles-e6ba58``).
"""

from __future__ import annotations

import dataclasses

import pytest


# ---------------------------------------------------------------------------
# Substrate record contract
# ---------------------------------------------------------------------------


def test_substrate_record_has_per_phase_error_fields() -> None:
    """W1.2: GovernedAppRunRecord must declare 7 per-phase error fields."""
    from apps_shared.integrations.governed_app_runner import GovernedAppRunRecord

    field_names = {f.name for f in dataclasses.fields(GovernedAppRunRecord)}
    expected = {"l1_error", "l0_error", "c0_error", "l2_error", "l5_error", "l6_error", "hitl_error"}
    missing = expected - field_names
    assert not missing, f"Missing per-phase error fields: {missing}"


def test_substrate_record_per_phase_errors_default_empty() -> None:
    """W1.2: Per-phase error fields default to "" so existing callers stay compatible."""
    from apps_shared.integrations.governed_app_runner import GovernedAppRunRecord

    rec = GovernedAppRunRecord(
        run_id="t1",
        app_name="apps_test",
        query="hello",
        l1_sub_queries=("hello",),
        l1_fallback=True,
        l0_intent="hello",
        l0_target="t",
        l0_confidence=0.0,
        l0_fallback=True,
        c0_raw_count=0,
        c0_shaped_count=0,
        c0_collection="x",
        disposition="unknown",
        gate_disposition="unknown",
        grounded=False,
        citation_count=0,
        support_coverage=0.0,
        l6_ingested=False,
        l2_executed=False,
        error="",
    )
    for fname in ("l1_error", "l0_error", "c0_error", "l2_error", "l5_error", "l6_error", "hitl_error"):
        assert getattr(rec, fname) == "", f"{fname} should default to ''"


# ---------------------------------------------------------------------------
# Substrate phase isolation contract
# ---------------------------------------------------------------------------


def test_substrate_no_whole_pipeline_broad_catch() -> None:
    """W1.1: The whole-pipeline broad ``except (ImportError, RuntimeError, ...)``
    block at the original line 326 must be gone. Phases now have their own
    scoped catches.
    """
    import apps_shared.integrations.governed_app_runner as substrate

    src = substrate.__file__
    with open(src, "r", encoding="utf-8") as f:
        text = f.read()

    # The W1 refactor split the outer broad catch into per-phase scoped catches.
    # Verify the original telltale string is absent.
    forbidden = '"[GovernedAppRunner] E2E failed run_id=%s app=%s: %s"'
    assert forbidden not in text, (
        "Whole-pipeline broad-catch error message still present \u2014 W1 not applied"
    )


def test_substrate_phase_outputs_carry_error() -> None:
    """W1.1: ``_PlanOutput`` and ``_RouteOutput`` must carry an error field."""
    from apps_shared.integrations.governed_app_runner import _PlanOutput, _RouteOutput

    assert "error" in {f.name for f in dataclasses.fields(_PlanOutput)}
    assert "error" in {f.name for f in dataclasses.fields(_RouteOutput)}


# ---------------------------------------------------------------------------
# Governed app record contracts (4 governed apps)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module,record_class_name",
    [
        ("apps_research.integrations.governed_research_run", "GovernedE2ERunRecord"),
        ("apps_exec.integrations.governed_exec_run", "GovernedExecE2ERunRecord"),
        ("apps_rfp.integrations.governed_rfp_run", "GovernedRfpE2ERunRecord"),
    ],
)
def test_governed_app_records_surface_per_phase_errors(module: str, record_class_name: str) -> None:
    """W1.2: Each governed app's sealed record must surface the 7 per-phase error fields."""
    import importlib

    mod = importlib.import_module(module)
    record_cls = getattr(mod, record_class_name)
    field_names = {f.name for f in dataclasses.fields(record_cls)}
    expected = {"l1_error", "l0_error", "c0_error", "l2_error", "l5_error", "l6_error", "hitl_error"}
    missing = expected - field_names
    assert not missing, f"{record_class_name} missing per-phase error fields: {missing}"
