"""Golden end-to-end branch-matrix tests for the L1 Thinking Desk (W5/P5.2).

Each test composes the full W2→W3→W4 primitive chain for one exit branch
of the v33 §2 T3 diagram:

    T3 exit branches (mutually exclusive):
       (a) ACCEPT           → plan approved, emit L1PlanContractV2
       (b) REFINE_EXHAUSTED → evaluator loop could not converge within cap
       (c) CLARIFY          → ambiguous user intent, block on user input
       (d) BEST_EFFORT      → budget exhausted but safe partial plan possible
       (e) ABSTAIN          → unsafe / under-specified → safe default
       (f) REPLAN           → exit gate invalidated an assumption → re-enter L1
       (g) ESCALATE         → critic demanded escalation

The chain per scenario:
  1. Seed a PlannerBudgetTracker
  2. Build a PromptEnvelope (L5/M1/M2/M3 → system/developer/user)
  3. Run the evaluator-optimizer loop with injected draft/critique fns
  4. Branch: plan_clarify / plan_abstain / validate_replan_request
  5. Redact + publish_rationale
  6. Emit L1PlanContractV2; call validate()
  7. Emit planner_overhead_metric and assert shape
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.enforcement.planner_budget import (
    PlannerBudget,
    PlannerBudgetTracker,
)
from agentic_core.L1_cognition.enforcement.planner_overhead_metric import (
    emit_from_tracker,
)
from agentic_core.L1_cognition.reasoning.evaluator_optimizer import (
    Critique,
    DraftResult,
    LoopBudget,
    LoopOutcome,
    run_evaluator_optimizer_loop,
)
from agentic_core.L1_cognition.reasoning.prompt_envelope import build_envelope
from agentic_core.L1_cognition.reasoning.thought_redactor import publish_rationale
from agentic_core.L1_cognition.types.plan_contract_types import (
    Assumption,
    AssumptionGrade,
    ExpectedGroundTruth,
    L1PlanContractV2,
    PlanTaskStep,
    PlannerTelemetry,
    ProposedRoute,
    QuerySpec,
    ReasoningMode,
    Reversibility,
    RiskBand,
    RouteRisk,
)
from agentic_core.runtime.contracts.abstain_contract import (
    DECISION_ABSTAIN,
    DECISION_CLARIFY,
    plan_abstain,
    plan_clarify,
)
from agentic_core.runtime.contracts.replan_contract import (
    MAX_REPLAN_DEPTH,
    ReplanContractViolation,
    advance_replan_depth,
    validate_replan_request,
)


# ---------------------------------------------------------------------------
# Shared scaffolding
# ---------------------------------------------------------------------------


def _fake_clock(ticks: list[int]):
    it = iter(ticks)

    def _now() -> int:
        try:
            return next(it)
        except StopIteration:
            return ticks[-1]

    return _now


def _std_envelope():
    return build_envelope(
        l5_policy="L5: no PII exfiltration.",
        schemas="M1: plan_contract_v2 JSON.",
        safety_envelope="M2: HITL < 0.6.",
        exemplars="",
        user_intent="I1: summarise Q2 report. I2: ≤200 words. I3: markdown.",
        is_reasoning_model=False,
    )


def _risk_low() -> RouteRisk:
    return RouteRisk(
        cost_band=RiskBand.LOW,
        latency_band=RiskBand.LOW,
        safety_band=RiskBand.LOW,
        reversibility=Reversibility.READ,
    )


def _step(step_id: str = "s1") -> PlanTaskStep:
    return PlanTaskStep(
        step_id=step_id,
        description="retrieve Q2 report summary",
        expected_ground_truth=ExpectedGroundTruth(
            signal_kind="tool_result",
            shape_hint="dict[str, Any]",
            success_predicate="rows > 0",
        ),
    )


def _build_contract(
    *,
    plan_id: str,
    route: ProposedRoute,
    telemetry: PlannerTelemetry,
    rationale: str,
    confidence: float = 0.85,
    grounding: bool = True,
    query_spec: QuerySpec | None = None,
) -> L1PlanContractV2:
    return L1PlanContractV2(
        plan_id=plan_id,
        request_id="req-gold",
        policy_hash="sha256:pol",
        proposed_route=route,
        reasoning_mode=ReasoningMode.DECOMPOSED,
        query_spec=query_spec if grounding else None,
        task_spec=(_step(),),
        route_risk=_risk_low(),
        confidence_score=confidence,
        grounding_required=grounding,
        declared_assumptions=(
            Assumption(statement="cache is fresh", grade=AssumptionGrade.DIRECTLY_OBSERVED),
        ),
        unresolved_gaps=(),
        published_rationale=rationale,
        planner_telemetry=telemetry,
    )


# ---------------------------------------------------------------------------
# (a) ACCEPT
# ---------------------------------------------------------------------------


class TestGoldenAccept:
    def test_accept_happy_path(self):
        env = _std_envelope()
        assert env.user_message.startswith("I1:")

        tracker = PlannerBudgetTracker(
            budget=PlannerBudget(max_refinements=3, token_cap=10_000),
            clock_ms=_fake_clock([0, 5, 10, 15, 20]),
        )

        def draft_fn(prior):
            tracker.record_tokens(50)
            return DraftResult(draft={"plan": "v1"}, token_delta=50)

        def critique_fn(draft):
            tracker.record_critic_pass()
            tracker.record_tokens(20)
            return Critique(verdict="accept", reason="grounded + complete", token_delta=20)

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=3, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 5, 10]),
        )
        assert result.outcome == LoopOutcome.ACCEPT

        rationale = publish_rationale(
            "Chose R3 — single grounded read satisfies the summary ask. "
            "<thinking>ruled out R4 because no action required</thinking>"
        )
        contract = _build_contract(
            plan_id="gold-accept",
            route=ProposedRoute.R3,
            query_spec=QuerySpec(query_text="q2 report", freshness_window_s=86400, max_results=5),
            telemetry=PlannerTelemetry(**tracker.snapshot()),
            rationale=rationale,
        )
        contract.validate()

        event = emit_from_tracker(
            plan_id=contract.plan_id,
            planner_enabled=True,
            tracker=tracker,
            outcome_hint="ACCEPT",
        )
        assert event["outcome_hint"] == "ACCEPT"
        assert event["refinements_used"] == 0
        assert event["critic_iterations"] == 1
        assert "thinking" not in contract.published_rationale.lower()


# ---------------------------------------------------------------------------
# (b) REFINE_EXHAUSTED
# ---------------------------------------------------------------------------


class TestGoldenRefineExhausted:
    def test_critic_demands_refine_until_cap(self):
        tracker = PlannerBudgetTracker(
            budget=PlannerBudget(max_refinements=2, token_cap=10_000),
            clock_ms=_fake_clock([0, 1, 2, 3, 4, 5]),
        )

        def draft_fn(prior):
            tracker.record_tokens(10)
            if prior is not None:
                tracker.record_refinement()
            return DraftResult(draft="draft", token_delta=10)

        def critique_fn(draft):
            tracker.record_critic_pass()
            return Critique(verdict="refine", reason="still incomplete")

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=2, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 1, 2, 3, 4, 5, 6, 7, 8]),
        )
        assert result.outcome == LoopOutcome.REFINE_EXHAUSTED

        # Gracefully demote to BEST_EFFORT with limitations surfaced.
        rationale = publish_rationale(
            "Best-effort plan — critic could not reach ACCEPT within refinement cap."
        )
        contract = _build_contract(
            plan_id="gold-refine-exhausted",
            route=ProposedRoute.R5,
            grounding=False,
            confidence=0.55,
            telemetry=PlannerTelemetry(**tracker.snapshot()),
            rationale=rationale,
        )
        contract.validate()

        event = emit_from_tracker(
            plan_id=contract.plan_id,
            planner_enabled=True,
            tracker=tracker,
            outcome_hint="REFINE_EXHAUSTED",
        )
        assert event["outcome_hint"] == "REFINE_EXHAUSTED"
        assert tracker.refinements_used == 2


# ---------------------------------------------------------------------------
# (c) CLARIFY
# ---------------------------------------------------------------------------


class TestGoldenClarify:
    def test_ambiguous_intent_routes_to_clarify(self):
        decision = plan_clarify(
            confidence=0.85,
            ambiguity_score=0.72,
            reason_hint="two valid interpretations: summarise Q2 vs Q2 vs Q1 delta",
        )
        assert decision["decision"] == DECISION_CLARIFY
        assert decision["action"] == "request_clarification"

        tracker = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 5, 10]))
        tracker.record_tokens(30)
        tracker.record_critic_pass()

        rationale = publish_rationale("Ambiguous intent; blocking on user clarification before draft.")
        contract = _build_contract(
            plan_id="gold-clarify",
            route=ProposedRoute.CLARIFY,
            grounding=False,  # CLARIFY+grounding is forbidden by contract validate()
            confidence=decision["confidence"],
            telemetry=PlannerTelemetry(**tracker.snapshot()),
            rationale=rationale,
        )
        contract.validate()
        assert contract.proposed_route is ProposedRoute.CLARIFY
        assert contract.grounding_required is False

    def test_clarify_plus_grounding_contract_rejected(self):
        """Defense-in-depth: even if a caller builds a bad CLARIFY contract,
        validate() must block it."""
        from agentic_core.L1_cognition.types.plan_contract_types import (
            PlanContractViolation,
        )

        tracker = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 1]))
        bad = L1PlanContractV2(
            plan_id="bad-clarify",
            request_id="r",
            policy_hash="sha256:p",
            proposed_route=ProposedRoute.CLARIFY,
            reasoning_mode=ReasoningMode.DECOMPOSED,
            query_spec=QuerySpec(query_text="q", freshness_window_s=60, max_results=1),
            task_spec=(_step(),),
            route_risk=_risk_low(),
            confidence_score=0.5,
            grounding_required=True,  # illegal with CLARIFY
            declared_assumptions=(),
            unresolved_gaps=(),
            published_rationale="illegal combo",
            planner_telemetry=PlannerTelemetry(**tracker.snapshot()),
        )
        with pytest.raises(PlanContractViolation, match="CLARIFY"):
            bad.validate()


# ---------------------------------------------------------------------------
# (d) BEST_EFFORT (budget exhausted but safe partial plan possible)
# ---------------------------------------------------------------------------


class TestGoldenBestEffort:
    def test_wall_clock_exhausted_yields_best_effort_r5(self):
        tracker = PlannerBudgetTracker(
            budget=PlannerBudget(wall_clock_ms_cap=100),
            clock_ms=_fake_clock([0, 50, 500]),  # jumps past cap on 3rd tick
        )

        def draft_fn(prior):
            return DraftResult(draft="slow", token_delta=0)

        def critique_fn(draft):
            return Critique(verdict="refine", reason="more needed")

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=5, wall_clock_ms_cap=100, token_cap=10_000),
            clock_ms=_fake_clock([0, 50, 500, 600, 700]),
        )
        assert result.outcome == LoopOutcome.BUDGET_EXHAUSTED

        rationale = publish_rationale("Budget exhausted mid-loop; emitting best-effort R5 safe-default.")
        contract = _build_contract(
            plan_id="gold-best-effort",
            route=ProposedRoute.R5,
            grounding=False,
            confidence=0.50,
            telemetry=PlannerTelemetry(**tracker.snapshot()),
            rationale=rationale,
        )
        contract.validate()
        assert contract.proposed_route is ProposedRoute.R5


# ---------------------------------------------------------------------------
# (e) ABSTAIN
# ---------------------------------------------------------------------------


class TestGoldenAbstain:
    def test_low_confidence_triggers_abstain(self):
        decision = plan_abstain(
            confidence=0.30,
            threshold=0.50,
            reason_hint="insufficient grounding support",
        )
        assert decision["decision"] == DECISION_ABSTAIN
        assert decision["action"] == "emit_r5_candidate"

        tracker = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 3]))
        tracker.record_tokens(15)
        tracker.record_critic_pass()

        rationale = publish_rationale(
            "Abstained: confidence 0.30 below floor 0.50; routing to R5 safe-default."
        )
        contract = _build_contract(
            plan_id="gold-abstain",
            route=ProposedRoute.R5,
            grounding=False,
            confidence=decision["confidence"],
            telemetry=PlannerTelemetry(**tracker.snapshot()),
            rationale=rationale,
        )
        contract.validate()
        assert contract.confidence_score == 0.30


# ---------------------------------------------------------------------------
# (f) REPLAN re-entry
# ---------------------------------------------------------------------------


class TestGoldenReplan:
    def test_assumption_invalidation_produces_replan_request(self):
        from agentic_core.runtime.contracts.replan_contract import ReplanRequest

        # Original plan: assumes cache is fresh, grounding not required.
        tracker = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 2]))
        original = _build_contract(
            plan_id="gold-orig",
            route=ProposedRoute.R1A,
            grounding=False,
            confidence=0.90,
            telemetry=PlannerTelemetry(**tracker.snapshot()),
            rationale="cache-fresh assumption held",
        )
        original.validate()

        # Exit gate observed cache was stale → emit ReplanRequest.
        req = ReplanRequest(
            original_plan_id=original.plan_id,
            failed_assumption="cache is fresh",
            observed_evidence="cache_ts=2025-12-01 > freshness_window",
            residual_budget_ms=5_000,
            residual_refinements=1,
            replan_depth=0,
        )
        validate_replan_request(req)

        # L1 re-enters; successor plan carries linked plan_id.
        tracker2 = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 8]))
        tracker2.record_tokens(40)
        tracker2.record_refinement()
        tracker2.record_critic_pass()

        successor = _build_contract(
            plan_id=f"{original.plan_id}-replan-1",
            route=ProposedRoute.R3,
            query_spec=QuerySpec(query_text="q", freshness_window_s=60, max_results=5),
            confidence=0.82,
            telemetry=PlannerTelemetry(**tracker2.snapshot()),
            rationale="Replanned with R3 after cache-fresh assumption invalidated.",
        )
        successor.validate()
        assert successor.proposed_route is ProposedRoute.R3
        assert successor.grounding_required is True

    def test_replan_depth_cap_forces_escalation(self):
        from agentic_core.runtime.contracts.replan_contract import ReplanRequest

        # Already at cap-1; advancing would reach cap, which is forbidden.
        req = ReplanRequest(
            original_plan_id="p",
            failed_assumption="a",
            observed_evidence="b",
            residual_budget_ms=100,
            residual_refinements=0,
            replan_depth=MAX_REPLAN_DEPTH - 1,  # = 2
        )
        validate_replan_request(req)  # still legal
        with pytest.raises(ReplanContractViolation, match="escalate"):
            advance_replan_depth(req)


# ---------------------------------------------------------------------------
# (g) ESCALATE
# ---------------------------------------------------------------------------


class TestGoldenEscalate:
    def test_critic_escalate_terminates_loop_early(self):
        tracker = PlannerBudgetTracker(budget=PlannerBudget(), clock_ms=_fake_clock([0, 5, 10]))

        def draft_fn(prior):
            tracker.record_tokens(5)
            return DraftResult(draft="attempt", token_delta=5)

        def critique_fn(draft):
            tracker.record_critic_pass()
            return Critique(verdict="escalate", reason="policy conflict detected")

        result = run_evaluator_optimizer_loop(
            draft_fn=draft_fn,
            critique_fn=critique_fn,
            budget=LoopBudget(max_refinements=5, wall_clock_ms_cap=10_000, token_cap=10_000),
            clock_ms=_fake_clock([0, 5, 10]),
        )
        assert result.outcome == LoopOutcome.ESCALATE
        assert result.refinements_used == 0

        event = emit_from_tracker(
            plan_id="gold-escalate",
            planner_enabled=True,
            tracker=tracker,
            outcome_hint="ESCALATE",
        )
        assert event["outcome_hint"] == "ESCALATE"


# ---------------------------------------------------------------------------
# Branch-matrix coverage guard
# ---------------------------------------------------------------------------


class TestBranchMatrixCoverage:
    """Sanity guard that every v33 §2 T3 exit branch has at least one golden."""

    EXPECTED_BRANCHES = {
        "ACCEPT",
        "REFINE_EXHAUSTED",
        "CLARIFY",
        "BEST_EFFORT",
        "ABSTAIN",
        "REPLAN",
        "ESCALATE",
    }

    def test_all_branches_have_a_golden(self):
        # Classes above each exercise one branch; this assertion documents
        # the expectation and will fail if someone removes a class without
        # updating the registry here.
        present = {
            "ACCEPT": TestGoldenAccept,
            "REFINE_EXHAUSTED": TestGoldenRefineExhausted,
            "CLARIFY": TestGoldenClarify,
            "BEST_EFFORT": TestGoldenBestEffort,
            "ABSTAIN": TestGoldenAbstain,
            "REPLAN": TestGoldenReplan,
            "ESCALATE": TestGoldenEscalate,
        }
        assert set(present.keys()) == self.EXPECTED_BRANCHES
