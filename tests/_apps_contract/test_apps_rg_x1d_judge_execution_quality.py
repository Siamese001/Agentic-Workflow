"""X1D judge execution vs quality classification (preflight-parity mismatch, model-backed FAIL, Exit wiring)."""

from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch
from pathlib import Path

from apps_rg.runtime.whole_run_exit import (
    RC_JUDGE_EXECUTION_PROVIDER_MISMATCH,
    RC_JUDGE_MODEL_BACKED_QUALITY_FAIL,
    RC_JUDGE_SCHEMA_OR_PARSER_BLOCK,
    RC_JUDGE_UNKNOWN_RESULT,
    X3B_REVIEW,
    X3D_ALLOW_FINISH,
    compute_whole_run_exit,
)
from apps_rg.runtime.x1d_lane_judge_diagnostics import build_x1d_lane_judge_diagnostics, classify_judge_status


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _base_signals(**kwargs: object) -> dict[str, object]:
    s: dict[str, object] = {
        "final_resume_exists": True,
        "final_resume_json_valid": True,
        "required_generated_sections_present": True,
        "locked_sections_preserved": True,
        "final_resume_x2_all_pass": True,
        "cross_app_leakage": False,
        "mock_provider_pass": False,
        "direct_l4_write_bypass": False,
        "grounding_required": True,
        "c0_evidence_item_count": 3,
        "c0_support_status": "STRONG",
        "pa_consumed_c0": True,
        "pa_evidence_data_only": True,
        "pa_schema_bound": True,
        "x1d_overall": "PASS",
        "x1d_policy_valid": True,
        "judge_quorum_satisfied": True,
        "x2_unknown_lane": False,
        "lane_rows": [
            {"lane": "lane_a", "x3_code": "X3_ALLOW", "x2_failed": 0},
            {"lane": "lane_b", "x3_code": "X3_ALLOW", "x2_failed": 0},
        ],
        "section_gates_overall": "PASS",
        "min_chroma_evidence_items": 1,
        "product_r4_bypass_documented": False,
        "x1d_judge_failure_breakdown": {
            "x1d_judge_execution_mismatch": False,
            "x1d_judge_model_backed_fail": False,
            "x1d_judge_unknown_result": False,
            "x1d_judge_provider_unavailable_row": False,
            "x1d_judge_schema_or_parser_blocked": False,
        },
    }
    s.update(kwargs)
    return s


def _policy_all_credentials() -> dict[str, object]:
    return {
        "available_judges": ["gemini_pro", "openai_chatgpt"],
        "quorum_satisfied": True,
        "policy_valid": True,
        "per_provider": {
            "gemini_pro": {"credential_env_non_empty": True},
            "openai_chatgpt": {"credential_env_non_empty": True},
        },
        "provider_types": {
            "gemini_pro": "external_cloud_llm_judge",
            "openai_chatgpt": "external_cloud_llm_judge",
        },
    }


class TestX1dJudgeExecutionQuality(unittest.TestCase):
    def test_preflight_available_runtime_blocked_is_execution_mismatch(self) -> None:
        r = classify_judge_status("BLOCKED_PROVIDER_UNAVAILABLE", preflight_credential_available=True)
        self.assertEqual(r["mapped_judge_status"], "JUDGE_EXECUTION_PROVIDER_MISMATCH")
        diag = build_x1d_lane_judge_diagnostics(
            _policy_all_credentials(),
            [
                {
                    "lane": "headline",
                    "x3_code": "X3_REVIEW",
                    "gemini": "BLOCKED_PROVIDER_UNAVAILABLE",
                    "openai": "MODEL_BACKED_PASS",
                    "anthropic": "MODEL_BACKED_PASS",
                }
            ],
        )
        jr = diag["lanes"]["headline"]["judge_results"]
        gem = next(x for x in jr if x["provider_key"] == "gemini_pro")
        self.assertTrue(gem["preflight_available"])
        self.assertEqual(gem["mapped_judge_status_enum"], "JUDGE_EXECUTION_PROVIDER_MISMATCH")

    def test_blocked_rate_limit_is_execution_mismatch_when_preflight_ok(self) -> None:
        r = classify_judge_status("BLOCKED_RATE_LIMIT", preflight_credential_available=True)
        self.assertEqual(r["mapped_judge_status"], "JUDGE_EXECUTION_PROVIDER_MISMATCH")

    def test_execution_mismatch_keeps_whole_run_review(self) -> None:
        w = compute_whole_run_exit(
            _base_signals(
                x1d_overall="PARTIAL",
                x1d_judge_failure_breakdown={
                    "x1d_judge_execution_mismatch": True,
                    "x1d_judge_model_backed_fail": False,
                    "x1d_judge_unknown_result": False,
                    "x1d_judge_provider_unavailable_row": False,
                    "x1d_judge_schema_or_parser_blocked": False,
                },
            )
        )
        self.assertEqual(w["x3_disposition"], X3B_REVIEW)
        self.assertIn(RC_JUDGE_EXECUTION_PROVIDER_MISMATCH, w["judge_reasons"])

    def test_model_backed_quality_fail_named_not_provider_unavailable(self) -> None:
        diag = build_x1d_lane_judge_diagnostics(
            _policy_all_credentials(),
            [
                {
                    "lane": "headline",
                    "x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL",
                    "gemini": "MODEL_BACKED_PASS",
                    "openai": "MODEL_BACKED_FAIL",
                    "anthropic": "MODEL_BACKED_PASS",
                }
            ],
        )
        fb = diag["failure_breakdown_for_exit"]
        self.assertTrue(fb["x1d_judge_model_backed_fail"])
        self.assertFalse(fb["x1d_judge_execution_mismatch"])
        openai = next(
            x for x in diag["lanes"]["headline"]["judge_results"] if x["provider_key"] == "openai_chatgpt"
        )
        self.assertEqual(openai["mapped_judge_status_enum"], "MODEL_BACKED_FAIL")

    def test_model_backed_quality_fail_keeps_whole_run_review(self) -> None:
        w = compute_whole_run_exit(
            _base_signals(
                x1d_overall="PARTIAL",
                x1d_judge_failure_breakdown={
                    "x1d_judge_execution_mismatch": False,
                    "x1d_judge_model_backed_fail": True,
                    "x1d_judge_unknown_result": False,
                    "x1d_judge_provider_unavailable_row": False,
                    "x1d_judge_schema_or_parser_blocked": False,
                },
            )
        )
        self.assertEqual(w["x3_disposition"], X3B_REVIEW)
        self.assertIn(RC_JUDGE_MODEL_BACKED_QUALITY_FAIL, w["judge_reasons"])

    def test_model_backed_pass_all_required_clears_judge_reasons_on_allow_finish_path(self) -> None:
        w = compute_whole_run_exit(_base_signals())
        self.assertEqual(w["x3_disposition"], X3D_ALLOW_FINISH)
        self.assertEqual(w["judge_reasons"], [])

    def test_one_passing_judge_does_not_override_required_fail_contract(self) -> None:
        diag = build_x1d_lane_judge_diagnostics(
            _policy_all_credentials(),
            [
                {
                    "lane": "single",
                    "x3_code": "X3_REVIEW",
                    "gemini": "MODEL_BACKED_PASS",
                    "openai": "MODEL_BACKED_FAIL",
                    "anthropic": "MODEL_BACKED_PASS",
                }
            ],
        )
        self.assertFalse(diag["lanes"]["single"]["lane_contract_pass"])
        self.assertNotEqual(diag["rollup_decision"], "PASS")
        fb = diag["failure_breakdown_for_exit"]
        self.assertTrue(fb["x1d_judge_model_backed_fail"])

    def test_schema_parse_blocked_vs_content_quality_buckets(self) -> None:
        s = classify_judge_status(
            "BLOCKED_SCHEMA_VALIDATION_ERROR", preflight_credential_available=True
        )
        self.assertEqual(s["mapped_judge_status"], "JUDGE_SCHEMA_OR_PARSER_BLOCKED")
        self.assertFalse(s.get("quality_fail"))
        fb = classify_judge_status("MODEL_BACKED_FAIL", preflight_credential_available=True)
        self.assertTrue(fb.get("quality_fail"))
        diag = build_x1d_lane_judge_diagnostics(
            _policy_all_credentials(),
            [
                {
                    "lane": "headline",
                    "gemini": "BLOCKED_SCHEMA_VALIDATION_ERROR_json",
                    "openai": "MODEL_BACKED_PASS",
                    "anthropic": "MODEL_BACKED_PASS",
                }
            ],
        )
        bd = diag["failure_breakdown_for_exit"]
        self.assertTrue(bd["x1d_judge_schema_or_parser_blocked"])
        self.assertFalse(bd["x1d_judge_model_backed_fail"])
        w = compute_whole_run_exit(
            _base_signals(
                x1d_overall="PARTIAL",
                x1d_judge_failure_breakdown={
                    "x1d_judge_execution_mismatch": False,
                    "x1d_judge_model_backed_fail": False,
                    "x1d_judge_unknown_result": False,
                    "x1d_judge_provider_unavailable_row": False,
                    "x1d_judge_schema_or_parser_blocked": True,
                },
            )
        )
        self.assertIn(RC_JUDGE_SCHEMA_OR_PARSER_BLOCK, w["judge_reasons"])

    def test_unknown_result_is_not_green_path(self) -> None:
        w = compute_whole_run_exit(
            _base_signals(
                x1d_overall="PARTIAL",
                x1d_judge_failure_breakdown={
                    "x1d_judge_execution_mismatch": False,
                    "x1d_judge_model_backed_fail": False,
                    "x1d_judge_unknown_result": True,
                    "x1d_judge_provider_unavailable_row": False,
                    "x1d_judge_schema_or_parser_blocked": False,
                },
            )
        )
        self.assertNotEqual(w["x3_disposition"], X3D_ALLOW_FINISH)
        self.assertIn(RC_JUDGE_UNKNOWN_RESULT, w["judge_reasons"])

    def test_deterministic_x2_pass_without_x1d_pass_still_requires_review_disposition(self) -> None:
        w = compute_whole_run_exit(
            _base_signals(
                final_resume_x2_all_pass=True,
                x1d_overall="PARTIAL",
                x1d_judge_failure_breakdown={
                    "x1d_judge_execution_mismatch": True,
                    "x1d_judge_model_backed_fail": False,
                    "x1d_judge_unknown_result": False,
                    "x1d_judge_provider_unavailable_row": False,
                    "x1d_judge_schema_or_parser_blocked": False,
                },
            )
        )
        self.assertEqual(w["x3_disposition"], X3B_REVIEW)

    def test_not_claiming_strings_absent_from_disposition_shell(self) -> None:
        w = compute_whole_run_exit(_base_signals())
        blob = str(w).lower()
        self.assertNotIn("fort knox", blob)

    def test_agentic_core_dirty_never_modified_by_this_task_finalize(self) -> None:
        from tests.helpers import ci_lane_dev_boundary as peg

        def fake_run(argv: list[str], *, cwd: Path, env=None):  # noqa: ANN001
            if argv[:7] == ["git", "status", "--porcelain=v1", "--", "agentic_core"]:
                return subprocess.CompletedProcess(argv, 0, " M agentic_core/runtime/x.py\n", "")
            raise AssertionError(f"unexpected argv: {argv}")

        with patch.object(peg, "run_git_cmd", fake_run):
            art = peg.minimal_ci_lane_dev_artifact()
            peg.finalize_boundary_no_bypass(art, _REPO_ROOT)
        box = art["boundary_no_bypass"]
        self.assertTrue(box["agentic_core_modified"])
        self.assertFalse(box["agentic_core_modified_by_this_task"])


if __name__ == "__main__":
    unittest.main()
