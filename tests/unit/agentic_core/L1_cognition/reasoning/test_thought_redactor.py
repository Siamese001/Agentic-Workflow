"""Tests for thought_redactor (ADR-043, W4/P4.4)."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.thought_redactor import (
    ThoughtLeakageViolation,
    assert_no_leakage,
    publish_rationale,
    redact_scratchpad,
)


class TestRedactScratchpad:
    def test_removes_w2_canary_block(self):
        text = "Plan rationale. <<<PRIVATE_SCRATCHPAD private thoughts >>> End."
        out = redact_scratchpad(text)
        assert "PRIVATE_SCRATCHPAD" not in out
        assert "private thoughts" not in out
        assert "Plan rationale." in out
        assert "End." in out

    def test_removes_prose_scratchpad_block(self):
        text = (
            "Public rationale here.\n\n"
            "BEGIN PRIVATE SCRATCHPAD\n"
            "secret analysis that must not leak\n"
            "END PRIVATE SCRATCHPAD\n\n"
            "Continued public rationale."
        )
        out = redact_scratchpad(text)
        assert "secret analysis" not in out
        assert "PRIVATE SCRATCHPAD" not in out
        assert "Public rationale" in out
        assert "Continued public rationale." in out

    def test_removes_xml_scratchpad_tag(self):
        text = "answer: 42. <scratchpad>chain of thought</scratchpad> done."
        out = redact_scratchpad(text)
        assert "chain of thought" not in out
        assert "scratchpad" not in out.lower()
        assert "answer: 42" in out

    def test_removes_thinking_tag(self):
        text = "Here is the plan. <thinking>I considered A vs B</thinking> Final answer."
        out = redact_scratchpad(text)
        assert "A vs B" not in out
        assert "thinking" not in out.lower()

    def test_removes_multiple_sibling_blocks(self):
        text = (
            "<thinking>first</thinking> middle "
            "<scratchpad>second</scratchpad> end "
            "<<<PRIVATE_SCRATCHPAD third >>>"
        )
        out = redact_scratchpad(text)
        assert "first" not in out
        assert "second" not in out
        assert "third" not in out
        assert "middle" in out
        assert "end" in out

    def test_idempotent_on_clean_text(self):
        clean = "Nothing to strip here. Just a normal rationale."
        assert redact_scratchpad(clean) == clean

    def test_idempotent_after_one_pass(self):
        text = "<thinking>hidden</thinking> rest"
        once = redact_scratchpad(text)
        twice = redact_scratchpad(once)
        assert once == twice

    def test_non_string_input_raises(self):
        with pytest.raises(TypeError):
            redact_scratchpad(123)  # type: ignore[arg-type]


class TestAssertNoLeakage:
    def test_clean_text_passes(self):
        assert_no_leakage("This is a fine rationale with no canaries.")

    def test_w2_canary_raises(self):
        with pytest.raises(ThoughtLeakageViolation, match="PRIVATE_SCRATCHPAD"):
            assert_no_leakage("prefix <<<PRIVATE_SCRATCHPAD leaked >>> suffix")

    def test_begin_marker_without_block_raises(self):
        # A stray BEGIN marker should still fail closed even without END.
        with pytest.raises(ThoughtLeakageViolation):
            assert_no_leakage("intro BEGIN PRIVATE SCRATCHPAD tail")

    def test_internal_thought_vocab_raises(self):
        with pytest.raises(ThoughtLeakageViolation, match="internal"):
            assert_no_leakage("response: the internal_thought here is obvious.")

    def test_secret_reasoning_vocab_raises(self):
        with pytest.raises(ThoughtLeakageViolation, match="secret"):
            assert_no_leakage("conclusion: my secret reasoning was X.")

    def test_case_insensitive_canary(self):
        with pytest.raises(ThoughtLeakageViolation):
            assert_no_leakage("oh no <<<private_scratchpad LEAK >>>")

    def test_non_string_input_raises(self):
        with pytest.raises(TypeError):
            assert_no_leakage(None)  # type: ignore[arg-type]


class TestPublishRationale:
    def test_clean_roundtrip(self):
        clean = "Plan A chosen because cost was lowest."
        assert publish_rationale(clean) == clean

    def test_strips_and_passes(self):
        text = "Decision: refuse. <thinking>weighed 3 options</thinking>"
        out = publish_rationale(text)
        assert "Decision: refuse." in out
        assert "weighed" not in out

    def test_residual_canary_after_redact_raises(self):
        # A raw "internal_thought" vocab is a canary but not inside any
        # redaction block — so redact_scratchpad leaves it alone and
        # assert_no_leakage must fail closed.
        with pytest.raises(ThoughtLeakageViolation):
            publish_rationale("final answer, plus my internal_thought leaked.")

    def test_block_removal_eliminates_canary(self):
        # The W2 canary is both a canary pattern AND a block pattern.
        # redact_scratchpad strips the whole block, so assert_no_leakage
        # sees a clean string and does not raise.
        out = publish_rationale("ok. <<<PRIVATE_SCRATCHPAD this gets scrubbed >>> done.")
        assert "scrubbed" not in out
        assert "ok." in out
        assert "done." in out


class TestIntegrationWithContract:
    def test_publish_output_passes_contract_validate(self):
        """Output of publish_rationale must satisfy L1PlanContractV2.validate() canary check."""
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

        dirty = "Planner chose R3. <thinking>I weighed options</thinking>"
        clean = publish_rationale(dirty)

        contract = L1PlanContractV2(
            plan_id="p1",
            request_id="r1",
            policy_hash="sha256:pol",
            proposed_route=ProposedRoute.R3,
            reasoning_mode=ReasoningMode.DECOMPOSED,
            query_spec=QuerySpec(query_text="q", freshness_window_s=3600, max_results=10),
            task_spec=(
                PlanTaskStep(
                    step_id="s1",
                    description="do the thing",
                    expected_ground_truth=ExpectedGroundTruth(
                        signal_kind="tool_result",
                        shape_hint="dict",
                        success_predicate="ok",
                    ),
                ),
            ),
            route_risk=RouteRisk(
                cost_band=RiskBand.LOW,
                latency_band=RiskBand.LOW,
                safety_band=RiskBand.LOW,
                reversibility=Reversibility.READ,
            ),
            confidence_score=0.9,
            grounding_required=True,
            declared_assumptions=(
                Assumption(statement="cache fresh", grade=AssumptionGrade.DIRECTLY_OBSERVED),
            ),
            unresolved_gaps=(),
            published_rationale=clean,
            planner_telemetry=PlannerTelemetry(
                refinements_used=0, wall_clock_ms=10, token_usage=50, critic_iterations=1
            ),
        )
        contract.validate()  # must not raise
