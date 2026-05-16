"""Contract tests for X1D judge preflight policy (credential env parity with ``run_llm_judges``)."""

from __future__ import annotations

import unittest

from apps_rg.runtime.x1d_judge_policy import preflight_x1d_judge_policy


class TestPrefetchX1dJudgePolicy(unittest.TestCase):
    def test_default_csv_matches_required_providers(self) -> None:
        p = preflight_x1d_judge_policy(
            environ={},
            configured_judge_csv=None,
            repo_dotenv_path_existed=False,
            repo_dotenv_loaded=False,
        )
        self.assertEqual(p["configured_judges"], p["required_judges"])
        self.assertTrue(p["policy_valid"])

    def test_unknown_provider_marks_policy_invalid(self) -> None:
        p = preflight_x1d_judge_policy(
            environ={},
            configured_judge_csv="fake_provider,openai_chatgpt,anthropic_claude,gemini_pro",
            repo_dotenv_path_existed=False,
            repo_dotenv_loaded=False,
        )
        self.assertFalse(p["policy_valid"])
        self.assertFalse(p["quorum_satisfied"])

    def test_credentials_populated_satisfies_quorum_without_network_proof(self) -> None:
        env = {
            "GEMINI_API_KEY": "fake-gemini",
            "OPENAI_API_KEY": "fake-openai",
            "ANTHROPIC_API_KEY": "fake-anthropic",
        }
        p = preflight_x1d_judge_policy(
            environ=env,
            configured_judge_csv=None,
            repo_dotenv_path_existed=True,
            repo_dotenv_loaded=True,
        )
        self.assertTrue(p["quorum_satisfied"])
        self.assertIn("credential_vs_runtime_capability_disclaimer", p)
        self.assertIn("RPM", str(p["credential_vs_runtime_capability_disclaimer"]))

    def test_google_api_key_satisfies_gemini_preflight_when_gemini_primary_empty(self) -> None:
        env = {
            "GOOGLE_API_KEY": "studio-style-key",
            "OPENAI_API_KEY": "fake-openai",
            "ANTHROPIC_API_KEY": "fake-anthropic",
        }
        p = preflight_x1d_judge_policy(
            environ=env,
            configured_judge_csv=None,
            repo_dotenv_path_existed=True,
            repo_dotenv_loaded=True,
        )
        self.assertTrue(p["quorum_satisfied"])
        gem_pp = p["per_provider"]["gemini_pro"]
        self.assertTrue(gem_pp["credential_env_non_empty"])
        self.assertEqual(gem_pp["credential_env_candidates"], ["GEMINI_API_KEY", "GOOGLE_API_KEY"])


if __name__ == "__main__":
    unittest.main()
