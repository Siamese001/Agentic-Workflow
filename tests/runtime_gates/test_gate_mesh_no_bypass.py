"""00C.8 anti-bypass tests.

Proof command:
    python -m pytest tests/runtime_gates/test_gate_mesh_no_bypass.py -q

Validates that for every layer surface, the doctrine-required gate set runs
and that ``GateMeshResult.missing_gate_ids`` correctly flags any bypass.

The test does not depend on every gate being present in the runtime — it
only asserts the framework refuses to silently allow a missing required
gate ID.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.dispatch import (
    LAYER_C0,
    LAYER_EXIT,
    LAYER_GATES,
    LAYER_L0,
    LAYER_L1,
    LAYER_L2,
    LAYER_L3,
    LAYER_L4,
    LAYER_L6,
    LAYER_PROMPT,
    LAYER_U0,
    LAYER_UWG,
    run_layer,
)
from agentic_core.L5_safety.runtime_gates.mesh_result import build_mesh_result
from agentic_core.L5_safety.runtime_gates.types import Disposition, GateDecision

# 00C.8 — every owner layer that may admit packets MUST require its gate set.
REQUIRED_BY_LAYER: dict[str, frozenset[str]] = {
    LAYER_U0: frozenset({"G01", "G02"}),
    LAYER_L1: frozenset({"G03"}),
    LAYER_L0: frozenset({"G04", "G05", "G06", "G07"}),
    LAYER_C0: frozenset({"G08", "G09"}),
    LAYER_PROMPT: frozenset({"G10"}),
    LAYER_L2: frozenset({"G11", "G12", "G13", "G14", "G15"}),
    LAYER_L4: frozenset({"G16", "G17"}),
    LAYER_L3: frozenset({"G18", "G19", "G20"}),
    LAYER_EXIT: frozenset({"G21", "G22", "G23", "G24", "G26"}),
    LAYER_UWG: frozenset({"G27"}),
    LAYER_L6: frozenset({"G25", "G28", "G29"}),
}


@pytest.mark.parametrize("layer", sorted(REQUIRED_BY_LAYER.keys()))
def test_layer_dispatch_lists_required_gates(layer):
    """``LAYER_GATES`` must contain every doctrine-required gate ID."""
    declared = set(LAYER_GATES[layer])
    required = set(REQUIRED_BY_LAYER[layer])
    missing = required - declared
    assert not missing, f"layer {layer} missing required gates: {missing}"


def test_mesh_result_flags_missing_gate(base_ctx):
    """If a required gate did not run, GateMeshResult.missing_gate_ids surfaces it."""
    decisions = [GateDecision(gate_id="G01", disposition=Disposition.ALLOW)]
    bundle = build_mesh_result(
        decisions,
        required_gate_ids=["G01", "G02"],
        evaluated_surface=LAYER_U0,
        evaluated_packet_ref=base_ctx.evaluated_packet_ref,
        request_id=base_ctx.request_id,
        run_id=base_ctx.run_id,
        trace_root=base_ctx.trace_root,
    )
    assert bundle.missing_gate_ids == ["G02"]
    assert bundle.recommended_disposition_summary == "BLOCK_EXIT"


def test_run_layer_emits_decisions_for_every_required_gate(base_ctx):
    """``run_layer(U0)`` produces verdicts for the U0 required gate set."""
    result = run_layer(LAYER_U0, base_ctx)
    completed = {d.gate_id for d in result.decisions}
    required = REQUIRED_BY_LAYER[LAYER_U0]
    # Either run to completion or halt — but every required gate must have
    # at least been attempted before the halt.
    if result.passed:
        assert required.issubset(completed)
    else:
        # On halt, the halting gate is the last completed; everything before
        # it must still be a doctrine-required gate.
        assert completed.issubset(set(LAYER_GATES[LAYER_U0]))


def test_no_layer_dispatches_an_undeclared_gate():
    """Every LAYER_GATES entry must be a real ``GXX`` ID."""
    for layer, ids in LAYER_GATES.items():
        for gid in ids:
            assert gid.startswith("G") and len(gid) == 3, (
                f"layer {layer} declares non-canonical gate id: {gid}"
            )


def test_hard_fail_aggregates_to_deny_summary():
    """A FAIL/DENY anywhere in the mesh produces summary=DENY (00C.7 rule)."""
    decisions = [
        GateDecision(gate_id="G01", disposition=Disposition.ALLOW),
        GateDecision(gate_id="G04", disposition=Disposition.DENY, reason_codes=["policy"]),
    ]
    bundle = build_mesh_result(
        decisions,
        required_gate_ids=["G01", "G04"],
        evaluated_surface=LAYER_L0,
    )
    assert bundle.hard_fail_present is True
    assert bundle.recommended_disposition_summary == "DENY"


def test_unknown_material_aggregates_to_escalate():
    """Material UNKNOWN escalates to ESCALATE_HITL (00C.7 aggregation)."""
    from agentic_core.L5_safety.runtime_gates.types import Result, Severity

    decisions = [
        GateDecision(gate_id="G01", disposition=Disposition.ALLOW),
        GateDecision(
            gate_id="G09",
            disposition=Disposition.ESCALATE_HITL,
            result=Result.UNKNOWN,
            severity=Severity.HIGH,
        ),
    ]
    bundle = build_mesh_result(
        decisions,
        required_gate_ids=["G01", "G09"],
        evaluated_surface=LAYER_C0,
    )
    assert bundle.unknown_material_present is True
    assert bundle.recommended_disposition_summary == "ESCALATE_HITL"
