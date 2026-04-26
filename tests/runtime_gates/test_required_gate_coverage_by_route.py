"""00C.8 Required-gate coverage by route class.

Proof command:
    python -m pytest tests/runtime_gates/test_required_gate_coverage_by_route.py -q

Asserts the required-gate set per route class (from 00C.7 RUNTIME GATE MESH
OVERVIEW) is a subset of the implemented mesh.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates import all_gates

# Route -> required gate IDs (subset of full mesh).
# Drawn from 00C.7 GATE MESH OVERVIEW per-stage requirements.
ROUTE_REQUIREMENTS: dict[str, frozenset[str]] = {
    # R1 cache routes still require ingress/identity/intent/policy/risk/route +
    # exit checks (G21/G22/G23/G24/G26).
    "R1_CACHE": frozenset({"G01", "G02", "G03", "G04", "G05", "G07", "G21",
                           "G22", "G23", "G24", "G26"}),
    # R3 grounded read additionally requires retrieval + evidence + prompt
    # assembly + tool gates.
    "R3_GROUNDED_READ": frozenset({
        "G01", "G02", "G03", "G04", "G05", "G07", "G08", "G09", "G10",
        "G13", "G17", "G21", "G22", "G23", "G24", "G26",
    }),
    # R4 single action additionally requires tool/arg/egress/sandbox + risk +
    # write sovereignty if mutating.
    "R4_SINGLE_ACTION": frozenset({
        "G01", "G02", "G03", "G04", "G05", "G07", "G11", "G12", "G14", "G15",
        "G21", "G22", "G23", "G24", "G26", "G27",
    }),
    # R3R4 managed workflow needs trajectory/loop/budget gates.
    "R3R4_MANAGED_WORKFLOW": frozenset({
        "G01", "G02", "G03", "G04", "G05", "G07", "G08", "G09", "G10",
        "G11", "G12", "G14", "G15", "G18", "G19", "G20", "G21", "G22",
        "G23", "G24", "G25", "G26",
    }),
    # R5 fallback still requires a minimum policy + safety + exit.
    "R5_FALLBACK": frozenset({"G01", "G02", "G03", "G04", "G22", "G23", "G26"}),
}


@pytest.mark.parametrize("route,required", sorted(ROUTE_REQUIREMENTS.items()))
def test_required_gates_for_route_are_implemented(route, required):
    """Every gate ID required by a route MUST exist in the registry."""
    implemented = set(all_gates())
    missing = required - implemented
    assert not missing, (
        f"route {route!r} requires gates not in registry: {missing}"
    )


def test_full_mesh_implements_all_29_gates():
    implemented = set(all_gates())
    expected = {f"G{i:02d}" for i in range(1, 30)}
    missing = expected - implemented
    extra = implemented - expected
    assert not missing, f"missing canonical gates: {missing}"
    assert not extra, f"unexpected gates in registry: {extra}"
