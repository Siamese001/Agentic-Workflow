"""W1.P2 unit tests — heuristic grounding-need classifier."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.ml_decision_support.features.grounding_need_features import (
    DEFAULT_INTERCEPT,
    GroundingNeedClassification,
    classify_grounding_need,
    classify_work_class,
)
from agentic_core.runtime.contracts.routing_features import WorkClass


class TestClassifyWorkClass:
    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            ("Summarize this document for me", WorkClass.SUMMARIZE),
            ("Compare Postgres versus MySQL for OLTP", WorkClass.COMPARE),
            ("Analyze Q3 customer churn", WorkClass.ANALYZE),
            ("Deploy the new build to prod", WorkClass.ACT),
            ("What is the capital of France?", WorkClass.FACTUAL),
            ("Write me a short story about dragons", WorkClass.GENERATE),
        ],
    )
    def test_keyword_detection(self, query: str, expected: WorkClass) -> None:
        assert classify_work_class(query) == expected

    def test_unknown_when_no_keyword(self) -> None:
        assert classify_work_class("xyz foo bar") == WorkClass.UNKNOWN

    def test_tldr_maps_to_summarize(self) -> None:
        assert classify_work_class("tldr of this thread") == WorkClass.SUMMARIZE

    def test_creative_question_goes_to_generate(self) -> None:
        # "what" would normally route to FACTUAL, but a creative keyword
        # flips the heuristic.
        assert classify_work_class("What if we imagine a fictional city?") == WorkClass.GENERATE


class TestClassifyGroundingNeed:
    def test_returns_classification_dataclass(self) -> None:
        result = classify_grounding_need("What is 2+2?")
        assert isinstance(result, GroundingNeedClassification)

    def test_score_is_bounded_open_interval(self) -> None:
        result = classify_grounding_need("")
        assert 0.0 < result.score < 1.0

    def test_factual_grounding_query_scores_high(self) -> None:
        result = classify_grounding_need(
            "What is the current Federal Reserve interest rate as of today?",
            work_class=WorkClass.FACTUAL,
        )
        assert result.score > 0.70
        assert result.grounding_token_hits >= 2  # "current" + "today"
        assert result.grounding_phrase_hits >= 1  # "as of"

    def test_creative_query_scores_low(self) -> None:
        result = classify_grounding_need(
            "Write a short fictional poem about a dragon",
            work_class=WorkClass.GENERATE,
        )
        assert result.score < 0.30
        assert result.reformat_token_hits >= 1

    def test_reformat_query_scores_low(self) -> None:
        result = classify_grounding_need(
            "Summarize the text below in three bullets",
            work_class=WorkClass.SUMMARIZE,
        )
        assert result.score < 0.30

    def test_unknown_work_class_defaults_neutral_low(self) -> None:
        # Empty query, no work_class hint → should fall below R3 default
        # Vertex threshold of 0.7.
        result = classify_grounding_need("", work_class=None)
        assert result.score < 0.70

    def test_work_class_autodetected_when_omitted(self) -> None:
        result = classify_grounding_need("Summarize this document")
        assert result.work_class == WorkClass.SUMMARIZE

    def test_empty_string_allowed(self) -> None:
        result = classify_grounding_need("")
        assert isinstance(result.score, float)

    def test_none_query_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be None"):
            classify_grounding_need(None)  # type: ignore[arg-type]

    def test_intercept_shifts_score(self) -> None:
        # Raising the intercept makes every query score higher.
        low = classify_grounding_need("generic query", intercept=DEFAULT_INTERCEPT - 1.0)
        high = classify_grounding_need("generic query", intercept=DEFAULT_INTERCEPT + 1.0)
        assert high.score > low.score

    def test_grounding_token_cap_prevents_runaway(self) -> None:
        # 10 grounding tokens should not score higher than 3 grounding tokens
        # at the cap — guards against long pathological queries.
        three = classify_grounding_need(
            "What is the current latest policy today?",
            work_class=WorkClass.FACTUAL,
        )
        many = classify_grounding_need(
            "What is the current latest policy today news weather price 2026 law real-time?",
            work_class=WorkClass.FACTUAL,
        )
        # The many-tokens version may win slightly due to reformat absence,
        # but the DELTA must be small (cap is working).
        assert abs(many.score - three.score) < 0.15

    def test_reformat_unbounded_can_drive_score_down(self) -> None:
        # Reformat evidence is deliberately NOT capped.
        wordy_reformat = classify_grounding_need(
            "summarize rewrite paraphrase reword reformat bullet",
            work_class=WorkClass.SUMMARIZE,
        )
        single_reformat = classify_grounding_need(
            "summarize this",
            work_class=WorkClass.SUMMARIZE,
        )
        assert wordy_reformat.score < single_reformat.score
        assert wordy_reformat.score < 0.10

    def test_scores_align_with_w0_fixture_intent(self) -> None:
        """Sanity check against the W0 r3_grounding.json fixture labels.

        Not a full calibration — the fixture uses hand-labeled scores — but
        the heuristic's RANKING should agree with the fixture's positive /
        negative classes on the strong-signal rows.
        """
        positive_cases = [
            # Factual / policy / recent — should score > default 0.7.
            ("What is the current policy on data retention as of 2026?", WorkClass.FACTUAL),
            ("Compare the latest prices of two cloud providers", WorkClass.COMPARE),
        ]
        negative_cases = [
            ("Summarize this text for me", WorkClass.SUMMARIZE),
            ("Draft a boilerplate email", WorkClass.GENERATE),
            ("Write a fictional poem", WorkClass.GENERATE),
        ]
        for q, wc in positive_cases:
            result = classify_grounding_need(q, work_class=wc)
            assert result.score > 0.70, f"Expected positive for {q!r}, got {result.score}"
        for q, wc in negative_cases:
            result = classify_grounding_need(q, work_class=wc)
            assert result.score < 0.50, f"Expected negative for {q!r}, got {result.score}"


class TestClassificationDataclass:
    def test_is_frozen(self) -> None:
        result = classify_grounding_need("test", work_class=WorkClass.UNKNOWN)
        with pytest.raises((AttributeError, Exception)):
            result.score = 0.5  # type: ignore[misc]

    def test_exposes_debug_fields(self) -> None:
        result = classify_grounding_need(
            "What is the current policy",
            work_class=WorkClass.FACTUAL,
        )
        assert result.linear_logit is not None
        assert result.grounding_token_hits >= 1
        assert result.work_class == WorkClass.FACTUAL
