"""W2.2 — publish disposition (certified vs best_effort)."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_publish_disposition import (
    apply_publish_disposition_to_proof_bundle,
    apply_publish_disposition_to_x3_dict,
    resolve_publish_disposition,
)


def _pass_judge(pk: str = "openai") -> dict:
    return {
        "evaluator_mode": "MODEL_BACKED",
        "provider_key": pk,
        "pass": True,
        "provider_status": "MODEL_BACKED_PASS",
        "holistic_score": 4.5,
    }


def _soft_judge(pk: str = "anthropic_claude") -> dict:
    return {
        "evaluator_mode": "MODEL_BACKED",
        "provider_key": pk,
        "pass": False,
        "provider_status": "MODEL_BACKED_FAIL",
        "holistic_score": 3.2,
        "decisive_failure": False,
        "dimension_verdicts": {
            "synthesis_quality": {"pass": False, "severity": "minor", "codes": ["s6_thin"]},
        },
    }


def test_certified_when_all_judges_pass() -> None:
    disp = resolve_publish_disposition(
        [_pass_judge("openai"), _pass_judge("anthropic_claude")],
        best_effort_publish_allowed=False,
        published_from_pool=True,
    )
    assert disp["publish_disposition"] == "certified"
    assert disp["proof_eligible"] is True
    assert disp["x1d_certified"] is True


def test_best_effort_requires_flag() -> None:
    disp = resolve_publish_disposition(
        [_pass_judge(), _soft_judge()],
        best_effort_publish_allowed=True,
        published_from_pool=True,
    )
    assert disp["publish_disposition"] == "best_effort"
    assert disp["proof_eligible"] is False
    assert disp["blocking_judge_ids"]


def test_judge_certification_required_without_flag() -> None:
    disp = resolve_publish_disposition(
        [_soft_judge()],
        best_effort_publish_allowed=False,
        published_from_pool=True,
    )
    assert disp["publish_disposition"] == "judge_certification_required"


def test_best_effort_downgrades_x3_allow() -> None:
    x3 = apply_publish_disposition_to_x3_dict(
        {"pass": True, "x3_code": "X3_ALLOW", "review_reason": ""},
        resolve_publish_disposition(
            [_soft_judge()],
            best_effort_publish_allowed=True,
            published_from_pool=True,
        ),
    )
    assert x3["pass"] is False
    assert x3["x3_code"] != "X3_ALLOW"
    assert x3["publish_disposition"] == "best_effort"


def test_proof_bundle_non_certified() -> None:
    bundle = apply_publish_disposition_to_proof_bundle(
        {"proof_eligible": True, "judge_proof_eligible": True},
        resolve_publish_disposition(
            [_soft_judge()],
            best_effort_publish_allowed=True,
            published_from_pool=True,
        ),
    )
    assert bundle["proof_eligible"] is False
    assert bundle["runtime_certification"] == "NON_CERTIFIED_PUBLISH"
