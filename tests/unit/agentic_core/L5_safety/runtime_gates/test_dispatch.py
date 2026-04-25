"""Tests for the per-layer dispatch API."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates import GateContext, all_gates
from agentic_core.L5_safety.runtime_gates.dispatch import (
    LAYER_C0,
    LAYER_EXIT,
    LAYER_GATES,
    LAYER_L0,
    LAYER_L2,
    LAYER_L3,
    LAYER_U0,
    LAYER_UWG,
    gates_for_layer,
    run_layer,
)
from agentic_core.L5_safety.runtime_gates.types import Disposition

from tests.unit.agentic_core.L5_safety.runtime_gates._ctx_fixtures import clean_ctx


def test_layer_gates_cover_all_29_gates() -> None:
    """Every gate must appear in at least one layer (L5 may overlap)."""
    seen: set[str] = set()
    for layer, gates in LAYER_GATES.items():
        if layer == "L5":
            continue
        seen.update(gates)
    assert seen == set(all_gates())


def test_u0_layer_covers_g01_g02() -> None:
    assert gates_for_layer(LAYER_U0) == ("G01", "G02")


def test_exit_layer_covers_expected() -> None:
    assert gates_for_layer(LAYER_EXIT) == ("G21", "G22", "G23", "G24", "G26")


def test_uwg_layer_covers_g27_only() -> None:
    assert gates_for_layer(LAYER_UWG) == ("G27",)


def test_unknown_layer_raises() -> None:
    with pytest.raises(ValueError, match="unknown layer"):
        gates_for_layer("BOGUS")


def test_run_layer_u0_clean() -> None:
    result = run_layer(LAYER_U0, clean_ctx())
    assert result.passed
    assert [d.gate_id for d in result.decisions] == ["G01", "G02"]


def test_run_layer_u0_halts_on_missing_envelope() -> None:
    ctx = clean_ctx()
    ctx.request_id = ""
    result = run_layer(LAYER_U0, ctx)
    assert not result.passed
    assert result.halted_at == "G01"
    assert result.decisions[-1].disposition is Disposition.DENY


def test_run_layer_l0_runs_g04_g07() -> None:
    result = run_layer(LAYER_L0, clean_ctx())
    assert [d.gate_id for d in result.decisions] == ["G04", "G05", "G06", "G07"]


def test_run_layer_uwg_blocks_non_uwg_caller() -> None:
    ctx = GateContext(
        memory_op={"is_proposed_mutation": True, "caller_layer": "L2"},
    )
    result = run_layer(LAYER_UWG, ctx)
    assert not result.passed
    assert result.halted_at == "G27"


def test_run_layer_c0_no_grounding_required() -> None:
    result = run_layer(LAYER_C0, clean_ctx())
    assert result.passed
    assert len(result.decisions) == 2


def test_run_layer_l3_short_circuits_on_budget_exhaustion() -> None:
    """L3 layer dispatch halts at G20 on budget exhaustion."""
    ctx = clean_ctx()
    ctx.budget["used_tokens"] = ctx.budget["max_tokens"]
    result = run_layer(LAYER_L3, ctx)
    assert not result.passed
    # L3 = G18, G19, G20 — budget hit at G20.
    assert result.halted_at == "G20"


def test_run_layer_l2_dispatch_order() -> None:
    assert gates_for_layer(LAYER_L2) == ("G11", "G12", "G13", "G14", "G15")


def test_run_layer_exit_visits_expected_gates() -> None:
    """Exit layer dispatch visits G21,G22,G23,G24,G26 in order."""
    result = run_layer(LAYER_EXIT, clean_ctx())
    visited = [d.gate_id for d in result.decisions]
    assert visited == list(gates_for_layer(LAYER_EXIT)[: len(visited)])
