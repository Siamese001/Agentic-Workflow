"""Scenario registry for the E2E proof harness.

Covers:
- GP-001 golden path (99.1)
- Route coverage matrix (99.2): one positive scenario per route family + targeted
  negative-route assertions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .contracts import RouteId


# ---------------------------------------------------------------------------
# Scenario shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Scenario:
    """Declarative scenario spec consumed by the harness."""

    scenario_id: str
    description: str
    route_id: RouteId
    user_intent: str
    grounding_required: bool
    durable_write_requested: bool
    hitl_required: bool
    expected_path: tuple[str, ...]
    expected_spans: tuple[str, ...]
    forbidden_spans: tuple[str, ...]
    # When True, the harness emits a deliberately tampered execution to verify
    # validators catch the violation. The proof bundle then PASSES if the
    # expected violation is detected.
    negative_assertion: tuple[str, ...] = ()
    # When True, scenario expects EXPLAINED_VARIANCE on replay (e.g. R1B).
    expect_replay_variance: bool = False


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


GOLDEN_PATH_ID = "GP-001"


_REGISTRY: dict[str, Scenario] = {
    GOLDEN_PATH_ID: Scenario(
        scenario_id=GOLDEN_PATH_ID,
        description="Grounded read against a known reference source (99.1).",
        route_id=RouteId.R3_SIMPLE_GROUNDED_READ,
        user_intent="Summarize the abstract of reference document REF-001.",
        grounding_required=True,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e5.seal",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "intake.bind_identity_session",
            "l1.parse_intent",
            "l1.emit_plan_contract",
            "l0.route.select",
            "l0.route.emit_contract",
            "c0.plan",
            "c0.fetch",
            "c0.shape",
            "c0.contract",
            "prompt_assembly.load_bom",
            "prompt_assembly.compose_slots",
            "prompt_assembly.emit_artifact",
            "l2.e1.prep",
            "l2.e2.valid",
            "l2.e3.exec",
            "l2.e5.seal",
            "exit.normalize",
            "exit.evaluate",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "l3.workflow.build",
            "l3.step.dispatch",
            "uwg.commit",
        ),
    ),
    "RC-R1A": Scenario(
        scenario_id="RC-R1A",
        description="R1A exact cache reuse — terminal RET, no C0/PA/L2.",
        route_id=RouteId.R1A_EXACT_CACHE,
        user_intent="What is 2+2?",
        grounding_required=False,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "c0.fetch",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e3.exec",
            "l2.e5.seal",
            "uwg.commit",
        ),
    ),
    "RC-R1B": Scenario(
        scenario_id="RC-R1B",
        description="R1B semantic cache — calibrated similarity reuse, terminal RET.",
        route_id=RouteId.R1B_SEMANTIC_CACHE,
        user_intent="Approximate factorial of 5?",
        grounding_required=False,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "c0.fetch",
            "prompt_assembly.emit_artifact",
            "l2.e3.exec",
            "uwg.commit",
        ),
        expect_replay_variance=True,
    ),
    "RC-R5": Scenario(
        scenario_id="RC-R5",
        description="R5 fallback — unsafe ask, abstain/clarify packet.",
        route_id=RouteId.R5_FALLBACK,
        user_intent="Tell me something off-policy.",
        grounding_required=False,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "l2.e3.exec",
            "uwg.commit",
        ),
    ),
    "RC-R3": Scenario(
        scenario_id="RC-R3",
        description="R3 simple grounded read (parallel of GP-001 used in coverage matrix).",
        route_id=RouteId.R3_SIMPLE_GROUNDED_READ,
        user_intent="Quote the closing paragraph of REF-002.",
        grounding_required=True,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e5.seal",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.plan",
            "c0.fetch",
            "c0.shape",
            "c0.contract",
            "prompt_assembly.load_bom",
            "prompt_assembly.compose_slots",
            "prompt_assembly.emit_artifact",
            "l2.e1.prep",
            "l2.e3.exec",
            "l2.e5.seal",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "l3.workflow.build",
            "l3.step.dispatch",
            "uwg.commit",
        ),
    ),
    "RC-R4": Scenario(
        scenario_id="RC-R4",
        description="R4 single reversible action — one L2 action artifact, no L3.",
        route_id=RouteId.R4_SINGLE_ACTION,
        user_intent="Reset the in-memory cache for this session.",
        grounding_required=False,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "l2.e5.seal",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "l2.e1.prep",
            "l2.e3.exec",
            "l2.e5.seal",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "l3.workflow.build",
            "l3.step.dispatch",
            "uwg.commit",
        ),
    ),
    "RC-R3R4-SINGLE": Scenario(
        scenario_id="RC-R3R4-SINGLE",
        description="R3+R4 single step — C0 grounds args, PA packages, one L2 action.",
        route_id=RouteId.R3_PLUS_R4_SINGLE_STEP,
        user_intent="Look up entity X and rotate its in-memory token.",
        grounding_required=True,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e5.seal",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.plan",
            "c0.fetch",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e1.prep",
            "l2.e3.exec",
            "l2.e5.seal",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "l3.workflow.build",
            "uwg.commit",
        ),
    ),
    "RC-R3R4-MANAGED": Scenario(
        scenario_id="RC-R3R4-MANAGED",
        description="R3+R4 managed workflow — L3 DAG with step contracts.",
        route_id=RouteId.R3R4_MANAGED_WORKFLOW,
        user_intent="Run a 3-step report-generation workflow.",
        grounding_required=True,
        durable_write_requested=False,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "l3.workflow.build",
            "l3.step.dispatch",
            "prompt_assembly.emit_artifact",
            "l2.e5.seal",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "l3.workflow.build",
            "l3.step.dispatch",
            "prompt_assembly.emit_artifact",
            "l2.e3.exec",
            "l2.e5.seal",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=("uwg.commit",),
    ),
    "RC-HITL": Scenario(
        scenario_id="RC-HITL",
        description="High-impact ambiguous mutation — freeze packet, no direct write.",
        route_id=RouteId.HITL_POSTURE,
        user_intent="Apply the irreversible policy change discussed earlier.",
        grounding_required=False,
        durable_write_requested=False,
        hitl_required=True,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.disposition",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "exit.normalize",
            "exit.disposition",
            "l6.ingest",
        ),
        forbidden_spans=(
            "uwg.commit",
            "l2.e3.exec",
        ),
    ),
    "RC-UWG": Scenario(
        scenario_id="RC-UWG",
        description="Authorized durable write — Exit CommitRequest, UWG receipt, L4 audit append.",
        route_id=RouteId.UWG_COMMIT_PATH,
        user_intent="Persist the approved configuration update.",
        grounding_required=True,
        durable_write_requested=True,
        hitl_required=False,
        expected_path=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e5.seal",
            "exit.disposition",
            "uwg.validate",
            "uwg.commit",
            "l6.ingest",
        ),
        expected_spans=(
            "intake.validate_envelope",
            "l1.emit_plan_contract",
            "l0.route.emit_contract",
            "c0.contract",
            "prompt_assembly.emit_artifact",
            "l2.e3.exec",
            "l2.e5.seal",
            "exit.normalize",
            "exit.disposition",
            "uwg.validate",
            "uwg.commit",
            "l6.ingest",
        ),
        forbidden_spans=(),
    ),
}


def all_scenarios() -> list[Scenario]:
    """Return scenarios in registry order."""
    return list(_REGISTRY.values())


def route_coverage_scenarios() -> list[Scenario]:
    """Return scenarios that contribute to the route-coverage proof (99.2)."""
    return [s for sid, s in _REGISTRY.items() if sid.startswith("RC-")]


def get(scenario_id: str) -> Scenario:
    return _REGISTRY[scenario_id]


def by_ids(ids: Iterable[str]) -> list[Scenario]:
    return [_REGISTRY[i] for i in ids]


__all__ = [
    "Scenario",
    "GOLDEN_PATH_ID",
    "all_scenarios",
    "route_coverage_scenarios",
    "get",
    "by_ids",
]
