"""Canonical agentic_core spine scenarios.

Declarative list of scenarios the core harness must prove. Each is a
single end-to-end traversal of the spine without any apps_* overlay.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoreScenario:
    scenario_id: str
    description: str
    expected_route_form: str  # MANAGED_WORKFLOW | TERMINAL_SHORTCIRCUIT | SINGLE_STEP_ROUTE | etc.
    expects_l3: bool
    expects_c0: bool
    expects_pa: bool
    expects_l2: bool
    expects_uwg: bool
    expects_l6: bool


CORE_SCENARIOS: tuple[CoreScenario, ...] = (
    CoreScenario(
        scenario_id="terminal_cache",
        description="Cache-hit terminal short-circuit; L0 → Exit → L6 only.",
        expected_route_form="TERMINAL_SHORTCIRCUIT",
        expects_l3=False, expects_c0=False, expects_pa=False,
        expects_l2=False, expects_uwg=False, expects_l6=True,
    ),
    CoreScenario(
        scenario_id="grounded_read",
        description="C0-grounded read route; PA + L2 model exec required.",
        expected_route_form="SINGLE_STEP_ROUTE",
        expects_l3=False, expects_c0=True, expects_pa=True,
        expects_l2=True, expects_uwg=False, expects_l6=True,
    ),
    CoreScenario(
        scenario_id="single_action",
        description="Single deterministic action route; no model exec.",
        expected_route_form="SINGLE_STEP_ROUTE",
        expects_l3=False, expects_c0=False, expects_pa=False,
        expects_l2=True, expects_uwg=False, expects_l6=True,
    ),
    CoreScenario(
        scenario_id="managed_workflow",
        description="MANAGED_WORKFLOW route bound to a static L3 DAG.",
        expected_route_form="MANAGED_WORKFLOW",
        expects_l3=True, expects_c0=True, expects_pa=True,
        expects_l2=True, expects_uwg=False, expects_l6=True,
    ),
    CoreScenario(
        scenario_id="managed_workflow_bypass",
        description="L3 capable but bypassed (NO_MANAGED_WORKFLOW_REQUIRED).",
        expected_route_form="SINGLE_STEP_ROUTE",
        expects_l3=False, expects_c0=False, expects_pa=False,
        expects_l2=True, expects_uwg=False, expects_l6=True,
    ),
    CoreScenario(
        scenario_id="durable_mutation",
        description="L2 → Exit → UWG (L4) durable write path.",
        expected_route_form="SINGLE_STEP_ROUTE",
        expects_l3=False, expects_c0=False, expects_pa=False,
        expects_l2=True, expects_uwg=True, expects_l6=True,
    ),
    CoreScenario(
        scenario_id="post_exit_exhaust",
        description="L6 RuntimeExhaustBundle handoff observed AFTER Exit.",
        expected_route_form="SINGLE_STEP_ROUTE",
        expects_l3=False, expects_c0=False, expects_pa=False,
        expects_l2=True, expects_uwg=False, expects_l6=True,
    ),
)


def find_scenario(scenario_id: str) -> CoreScenario | None:
    for s in CORE_SCENARIOS:
        if s.scenario_id == scenario_id:
            return s
    return None


__all__ = ["CoreScenario", "CORE_SCENARIOS", "find_scenario"]
