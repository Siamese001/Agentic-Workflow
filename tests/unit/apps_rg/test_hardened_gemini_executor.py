"""3.9: Baseline tests for HardenedGeminiExecutor (3.2)."""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hardened_gemini_executor")
_emit_applies_guardrail("p0", "test_hardened_gemini_executor", "p0_governance")
_emit_reads_policy_state("p0", "test_hardened_gemini_executor", "policy_binding")
_emit_snapshots_state("p0", "test_hardened_gemini_executor", "state_snapshot")
emit_replay_key("p0", "test_hardened_gemini_executor")
emit_determinism_digest("p0", "test_hardened_gemini_executor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
