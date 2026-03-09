"""3.9: Baseline tests for HardenedGeminiExecutor (3.2)."""

from __future__ import annotations

import pytest


class TestHardenedGeminiExecutorInit:
    def test_instantiates_without_error(self):
        from apps_rg.engines.hardened_gemini_executor import HardenedGeminiExecutor

        executor = HardenedGeminiExecutor()
        assert executor.agent_id == "HardenedGeminiExecutor"
        assert executor.max_retries == 3

    def test_is_available_returns_bool(self):
        from apps_rg.engines.hardened_gemini_executor import HardenedGeminiExecutor

        executor = HardenedGeminiExecutor()
        result = executor.is_available()
        assert isinstance(result, bool)

    def test_execute_raises_when_gateway_unavailable(self):
        from apps_rg.engines.hardened_gemini_executor import HardenedGeminiExecutor

        executor = HardenedGeminiExecutor()
        executor._gateway = None
        with pytest.raises(RuntimeError, match="not available"):
            executor.execute("test prompt")
