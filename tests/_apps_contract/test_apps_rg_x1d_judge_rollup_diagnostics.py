"""X1D lane rollup → diagnostics → Exit failure_breakdown wiring."""

from __future__ import annotations

import unittest

from apps_rg.runtime.x1d_lane_judge_diagnostics import build_x1d_lane_judge_diagnostics, failure_breakdown_for_signals


def _policy_all_available() -> dict[str, object]:
    return {
        "available_judges": ["gemini_pro", "openai_chatgpt", "anthropic_claude"],
        "quorum_satisfied": True,
        "policy_valid": True,
        "per_provider": {
            "gemini_pro": {"credential_env_non_empty": True},
            "openai_chatgpt": {"credential_env_non_empty": True},
            "anthropic_claude": {"credential_env_non_empty": True},
        },
        "provider_types": {
            "gemini_pro": "external_cloud_llm_judge",
            "openai_chatgpt": "external_cloud_llm_judge",
            "anthropic_claude": "external_cloud_llm_judge",
        },
    }


class TestAppsRgX1dJudgeRollupDiagnostics(unittest.TestCase):
    def test_roll_up_pass_contract_emits_failure_breakdown_all_false(self) -> None:
        diag = build_x1d_lane_judge_diagnostics(
            _policy_all_available(),
            [
                {
                    "lane": "headline",
                    "x3_code": "X3_ALLOW",
                    "gemini": "MODEL_BACKED_PASS",
                    "openai": "MODEL_BACKED_PASS",
                    "anthropic": "MODEL_BACKED_PASS",
                }
            ],
        )
        fb = failure_breakdown_for_signals(diag)
        self.assertEqual(diag["rollup_decision"], "PASS")
        self.assertFalse(fb["x1d_judge_execution_mismatch"])
        self.assertFalse(fb["x1d_judge_model_backed_fail"])
        self.assertFalse(fb["x1d_judge_unknown_result"])

    def test_schema_parser_blocked_routes_failure_breakdown(self) -> None:
        diag = build_x1d_lane_judge_diagnostics(
            _policy_all_available(),
            [
                {
                    "lane": "headline",
                    "gemini": "BLOCKED_SCHEMA_VALIDATION_ERROR",
                    "openai": "MODEL_BACKED_PASS",
                    "anthropic": "MODEL_BACKED_PASS",
                }
            ],
        )
        fb = failure_breakdown_for_signals(diag)
        self.assertTrue(fb["x1d_judge_schema_or_parser_blocked"])
        self.assertFalse(fb["x1d_judge_model_backed_fail"])


if __name__ == "__main__":
    unittest.main()
