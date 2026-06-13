"""W4 judge calibration status verification.

Plan: apps-core-contract-rectification-a8f3c2 Phase 4
Confirms all active targeted LLM judges are promoted (IS_STUB=False) and have
deterministic v2 GRADER_IDs. These were promoted in plan
apps-eval-harness-deferred-e4a1b7 and should remain non-stub.
"""

from __future__ import annotations

import pytest


def test_executive_positioning_judge_not_stub() -> None:
    from apps_rg.engines.judges.executive_positioning_judge import IS_STUB, GRADER_ID

    assert IS_STUB is False, "executive_positioning_judge must not be a stub"
    assert "v2" in GRADER_ID, f"Expected v2 GRADER_ID, got {GRADER_ID!r}"


def test_response_likelihood_judge_not_stub() -> None:
    from apps_lic.engines.judges.response_likelihood_judge import IS_STUB, GRADER_ID

    assert IS_STUB is False, "response_likelihood_judge must not be a stub"
    assert "v2" in GRADER_ID, f"Expected v2 GRADER_ID, got {GRADER_ID!r}"


def test_brand_voice_judge_not_stub() -> None:
    from apps_lic.engines.judges.brand_voice_judge import IS_STUB, GRADER_ID

    assert IS_STUB is False, "brand_voice_judge must not be a stub"
    assert "v2" in GRADER_ID, f"Expected v2 GRADER_ID, got {GRADER_ID!r}"


def test_all_active_judges_have_grade_callable() -> None:
    from apps_rg.engines.judges.executive_positioning_judge import ExecutivePositioningJudge
    from apps_lic.engines.judges.response_likelihood_judge import ResponseLikelihoodJudge
    from apps_lic.engines.judges.brand_voice_judge import BrandVoiceJudge

    for cls in (
        ExecutivePositioningJudge,
        ResponseLikelihoodJudge,
        BrandVoiceJudge,
    ):
        assert callable(getattr(cls, "grade", None)), (
            f"{cls.__name__} missing callable grade() method"
        )
