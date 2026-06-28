"""CLI exit code mapping for exec-summary failures."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.cli_exit_codes import (
    EXIT_JUDGE_REVIEW_REQUIRED,
    EXIT_TOKEN_BUDGET_BLOCKED,
    exit_code_for_executive_summary_artifact,
)


def test_exit_token_budget_from_receipt(tmp_path: Path) -> None:
    ad = tmp_path / "lane"
    ad.mkdir()
    (ad / "token_budget_receipt.json").write_text(
        json.dumps(
            {
                "dispatch_allowed": False,
                "fail_closed_reason": "TOKEN_BUDGET_EXCEEDED_FIRST_PASS_95PCT",
            }
        ),
        encoding="utf-8",
    )
    assert exit_code_for_executive_summary_artifact(ad) == EXIT_TOKEN_BUDGET_BLOCKED


def test_exit_judge_soft_fail(tmp_path: Path) -> None:
    ad = tmp_path / "lane"
    ad.mkdir()
    (ad / "token_budget_receipt.json").write_text(
        json.dumps({"dispatch_allowed": True, "fail_closed_reason": None}),
        encoding="utf-8",
    )
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False}),
        encoding="utf-8",
    )
    assert exit_code_for_executive_summary_artifact(ad) == EXIT_JUDGE_REVIEW_REQUIRED


def test_exit_judge_certification_required_even_with_publish_review_code(tmp_path: Path) -> None:
    ad = tmp_path / "lane"
    ad.mkdir()
    (ad / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": "X3_REVIEW_PUBLISH_NOT_CERTIFIED",
                "pass": False,
                "publish_disposition": "judge_certification_required",
                "x1d_certified": False,
                "blocking_judge_ids": ["gemini_pro"],
            }
        ),
        encoding="utf-8",
    )
    assert exit_code_for_executive_summary_artifact(ad) == EXIT_JUDGE_REVIEW_REQUIRED
