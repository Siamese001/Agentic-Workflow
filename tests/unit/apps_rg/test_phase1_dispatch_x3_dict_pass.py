"""W1 — Phase-1 dispatch must read X3 pass from dict mirrors (executive_summary publish path)."""

from __future__ import annotations

from dataclasses import dataclass

from apps_rg.runtime.sections.executive_summary_publish_disposition import (
    apply_publish_disposition_to_x3_dict,
    resolve_publish_disposition,
)
from apps_rg.runtime.spine.section_cli_runners import _lane_dispatch_status_from_x3
from apps_rg.runtime.spine.section_x3_finalize import (
    lane_outcome_authorized_from_x3,
    lane_x3_code_from_x3,
)


@dataclass
class _X3Stub:
    x3_code: str
    pass_: bool


def test_lane_outcome_authorized_from_x3_dataclass_pass() -> None:
    x3 = _X3Stub(x3_code="X3_ALLOW", pass_=True)
    assert lane_outcome_authorized_from_x3(x3) is True
    assert lane_x3_code_from_x3(x3) == "X3_ALLOW"


def test_lane_outcome_authorized_from_x3_dict_pass_key() -> None:
    x3 = {"x3_code": "X3_ALLOW", "pass": True, "product_quality_status": "PASS"}
    assert lane_outcome_authorized_from_x3(x3) is True
    authorized, exit_status, code = _lane_dispatch_status_from_x3(x3)
    assert authorized is True
    assert exit_status == "success"
    assert code == "X3_ALLOW"


def test_lane_outcome_authorized_from_x3_dict_getattr_pass_fails_without_helper() -> None:
    """Regression: bare getattr(x3, 'pass_', False) is False on dict even when pass is True."""
    x3 = {"x3_code": "X3_ALLOW", "pass": True}
    assert bool(getattr(x3, "pass_", False)) is False
    assert lane_outcome_authorized_from_x3(x3) is True


def test_lane_outcome_authorized_from_x3_dict_x3_allow_without_pass_key() -> None:
    x3 = {"x3_code": "X3_ALLOW", "product_quality_status": "PASS"}
    assert lane_outcome_authorized_from_x3(x3) is True


def test_lane_outcome_authorized_from_x3_dict_review_not_authorized() -> None:
    x3 = {"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False}
    assert lane_outcome_authorized_from_x3(x3) is False
    _, exit_status, _ = _lane_dispatch_status_from_x3(x3)
    assert exit_status == "error"


def test_executive_summary_publish_disposition_certified_dict_dispatch_success() -> None:
    """Mirrors executive_summary_lane ctx x3 after publish_disposition (dict mirror on disk)."""
    x3_doc = {
        "x3_code": "X3_ALLOW",
        "pass": True,
        "product_quality_status": "PASS",
        "publish_disposition": "certified",
        "x1d_certified": True,
        "blocking_judge_ids": [],
    }
    authorized, exit_status, code = _lane_dispatch_status_from_x3(x3_doc)
    assert authorized is True
    assert exit_status == "success"
    assert code == "X3_ALLOW"


def test_executive_summary_publish_disposition_apply_certified_path() -> None:
    """apply_publish_disposition_to_x3_dict leaves pass True when disposition is certified."""
    base = {"x3_code": "X3_ALLOW", "pass": True, "review_reason": ""}
    pub = resolve_publish_disposition(
        [
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
            },
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
            },
        ],
        best_effort_publish_allowed=False,
        published_from_pool=True,
    )
    assert pub.get("publish_disposition") == "certified"
    x3_doc = apply_publish_disposition_to_x3_dict(base, pub)
    assert x3_doc.get("pass") is True
    assert lane_outcome_authorized_from_x3(x3_doc) is True


def test_lane_outcome_authorized_from_x3_pass_underscore_key_only() -> None:
    x3 = {"x3_code": "X3_ALLOW", "pass_": True}
    assert lane_outcome_authorized_from_x3(x3) is True


def test_lane_outcome_authorized_from_x3_x3_block_not_authorized() -> None:
    x3 = {"x3_code": "X3_BLOCK", "pass": False}
    assert lane_outcome_authorized_from_x3(x3) is False
    _, exit_status, code = _lane_dispatch_status_from_x3(x3)
    assert exit_status == "error"
    assert code == "X3_BLOCK"


def test_lane_outcome_authorized_from_x3_none_and_empty() -> None:
    assert lane_outcome_authorized_from_x3(None) is False
    assert lane_outcome_authorized_from_x3({}) is False
    assert lane_x3_code_from_x3(None) == ""


def test_lane_outcome_authorized_exit_ok_family_without_pass_key() -> None:
    for code in ("EXIT_OK", "EXIT_PARTIAL", "X3C", "X3D"):
        assert lane_outcome_authorized_from_x3({"x3_code": code}) is True


def test_phase1_dispatch_hard_failed_true_on_soft_fail_dispatch() -> None:
    from apps_rg.runtime.product_output_policy import phase1_dispatch_hard_failed

    x3_doc = {"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False}
    _, exit_status, _ = _lane_dispatch_status_from_x3(x3_doc)
    dispatch = {"exit_status": exit_status, "fault": ""}
    assert exit_status == "error"
    assert phase1_dispatch_hard_failed(dispatch) is True


def test_phase1_dispatch_hard_failed_false_on_dict_allow() -> None:
    from apps_rg.runtime.product_output_policy import phase1_dispatch_hard_failed

    x3_doc = {"x3_code": "X3_ALLOW", "pass": True}
    authorized, exit_status, _ = _lane_dispatch_status_from_x3(x3_doc)
    dispatch = {
        "exit_status": exit_status,
        "outcome_authorized": authorized,
        "x3_disposition": lane_x3_code_from_x3(x3_doc),
        "fault": "",
    }
    assert authorized is True
    assert phase1_dispatch_hard_failed(dispatch) is False
