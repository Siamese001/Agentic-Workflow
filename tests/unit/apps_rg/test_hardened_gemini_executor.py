"""3.9: Baseline tests for HardenedGeminiExecutor (3.2)."""

from __future__ import annotations

import pytest


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
