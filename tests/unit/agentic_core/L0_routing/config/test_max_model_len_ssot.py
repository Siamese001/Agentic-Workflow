"""Wave 2 — token-budget SSOT reconciliation tests.

Plan ref: ``.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md`` Wave 2.

Verifies:
  - ``QWEN_LOCAL_MAX_MODEL_LEN`` is exported and equals the env-var override
    or the post-cutover default 24576.
  - ``vllm_serving_profile_types.QWEN_SERVED_MODEL_MAX_LEN_CEILING`` is the
    same value (single SSOT, no drift).
  - A profile with ``max_model_len`` exceeding the SSOT ceiling raises
    ``VLLMServingProfileInvalid`` at construction time (regression guard
    for the stale 32768 ceiling that previously silently passed).
"""

from __future__ import annotations

import importlib
import os
import unittest


class MaxModelLenSSOTTest(unittest.TestCase):
    def test_default_matches_running_server(self) -> None:
        # Reload to make sure no test-side env mutation is leaked in
        from agentic_core.L0_routing.config import model_registry

        importlib.reload(model_registry)
        self.assertEqual(model_registry.QWEN_LOCAL_MAX_MODEL_LEN, 24576)

    def test_env_override_respected(self) -> None:
        os.environ["VLLM_MAX_MODEL_LEN"] = "8192"
        try:
            from agentic_core.L0_routing.config import model_registry

            importlib.reload(model_registry)
            self.assertEqual(model_registry.QWEN_LOCAL_MAX_MODEL_LEN, 8192)
        finally:
            del os.environ["VLLM_MAX_MODEL_LEN"]
            from agentic_core.L0_routing.config import model_registry

            importlib.reload(model_registry)

    def test_vllm_token_budget_types_max_model_len_reads_from_ssot(self) -> None:
        from agentic_core.L0_routing.config.model_registry import (
            QWEN_LOCAL_MAX_MODEL_LEN,
        )
        from agentic_core.L2_execution.types import vllm_token_budget_types

        importlib.reload(vllm_token_budget_types)
        self.assertEqual(
            vllm_token_budget_types.QWEN_MAX_MODEL_LEN,
            QWEN_LOCAL_MAX_MODEL_LEN,
        )

    def test_serving_profile_ceiling_reads_from_ssot(self) -> None:
        from agentic_core.L0_routing.config.model_registry import (
            QWEN_LOCAL_MAX_MODEL_LEN,
        )
        from agentic_core.L2_execution.types import vllm_serving_profile_types

        importlib.reload(vllm_serving_profile_types)
        self.assertEqual(
            vllm_serving_profile_types.QWEN_SERVED_MODEL_MAX_LEN_CEILING,
            QWEN_LOCAL_MAX_MODEL_LEN,
            msg="ceiling must mirror the L0 SSOT — drift indicates the stale 32768 default returned",
        )

    def test_profile_above_ceiling_rejects_at_construction(self) -> None:
        from agentic_core.L2_execution.types.vllm_serving_profile_types import (
            QWEN_SERVED_MODEL_MAX_LEN_CEILING,
            VLLMServingProfile,
            VLLMServingProfileInvalid,
        )

        bad_len = QWEN_SERVED_MODEL_MAX_LEN_CEILING + 1024
        with self.assertRaises(VLLMServingProfileInvalid):
            VLLMServingProfile(
                profile_name="LOCAL_OVER_CEILING",
                model="Qwen/Qwen2.5-32B-Instruct-AWQ",
                max_model_len=bad_len,
                max_num_seqs=4,
                gpu_memory_utilization=0.85,
            )

    def test_in_bounds_profile_constructs(self) -> None:
        from agentic_core.L2_execution.types.vllm_serving_profile_types import (
            QWEN_SERVED_MODEL_MAX_LEN_CEILING,
            VLLMServingProfile,
        )

        prof = VLLMServingProfile(
            profile_name="LOCAL_AT_CEILING",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            max_model_len=QWEN_SERVED_MODEL_MAX_LEN_CEILING,
            max_num_seqs=8,
            gpu_memory_utilization=0.85,
        )
        self.assertEqual(prof.max_model_len, QWEN_SERVED_MODEL_MAX_LEN_CEILING)


if __name__ == "__main__":
    unittest.main()
