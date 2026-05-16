"""Whole-run Exit aggregation signals (single X3 disposition, reason codes)."""

from __future__ import annotations

import unittest

from apps_rg.runtime.whole_run_exit import (
    RC_FINAL_RESUME_X2_FAIL,
    RC_JUDGE_PROVIDER_UNAVAILABLE,
    RC_JUDGE_QUORUM_NOT_SATISFIED,
    X3_BLOCK,
    X3B_REVIEW,
    X3D_ALLOW_FINISH,
    X3E_SAFE_ABSTAIN,
    compute_whole_run_exit,
)


def _minimal_ok_signals(**kwargs: object) -> dict[str, object]:
    s: dict[str, object] = {
        "final_resume_exists": True,
        "final_resume_json_valid": True,
        "required_generated_sections_present": True,
        "locked_sections_preserved": True,
        "final_resume_x2_all_pass": True,
        "cross_app_leakage": False,
        "mock_provider_pass": False,
        "direct_l4_write_bypass": False,
        "grounding_required": False,
        "c0_evidence_item_count": 2,
        "c0_support_status": "",
        "pa_consumed_c0": True,
        "pa_evidence_data_only": True,
        "pa_schema_bound": True,
        "x1d_overall": "PASS",
        "x1d_policy_valid": True,
        "judge_quorum_satisfied": True,
        "x2_unknown_lane": False,
        "lane_rows": [
            {"lane": "a", "x3_code": "X3_ALLOW", "x2_failed": 0},
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


class TestAppsRgWholeRunExit(unittest.TestCase):
    def test_allow_finish_green_path(self) -> None:
        w = compute_whole_run_exit(_minimal_ok_signals(grounding_required=False))
        self.assertEqual(w["x3_disposition"], X3D_ALLOW_FINISH)
        self.assertTrue(w["exactly_one_x3"])

    def test_structural_block_final_resume_missing(self) -> None:
        w = compute_whole_run_exit(_minimal_ok_signals(final_resume_exists=False))
        self.assertEqual(w["x3_disposition"], X3_BLOCK)
        self.assertTrue(w["blockers"])

    def test_final_x2_unknown_abstains(self) -> None:
        w = compute_whole_run_exit(_minimal_ok_signals(final_resume_x2_all_pass=None))
        self.assertEqual(w["x3_disposition"], X3E_SAFE_ABSTAIN)
        self.assertIn(RC_FINAL_RESUME_X2_FAIL, w["block_reasons"])

    def test_quorum_failed_adds_review_and_provider_codes(self) -> None:
        w = compute_whole_run_exit(_minimal_ok_signals(judge_quorum_satisfied=False, x1d_overall="PASS"))
        self.assertEqual(w["x3_disposition"], X3B_REVIEW)
        self.assertIn(RC_JUDGE_QUORUM_NOT_SATISFIED, w["judge_reasons"])
        self.assertIn(RC_JUDGE_PROVIDER_UNAVAILABLE, w["judge_reasons"])


if __name__ == "__main__":
    unittest.main()
