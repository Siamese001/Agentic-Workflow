"""ADG-driven tests for L2_execution/healers/qwen_gpu_validator.py — fan_in=1."""
from __future__ import annotations

from unittest.mock import patch

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

_emit_records_execution_trace("p0", "evidence", "test_qwen_gpu_validator_adg")
_emit_applies_guardrail("p0", "test_qwen_gpu_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_qwen_gpu_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_qwen_gpu_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_qwen_gpu_validator_adg")
emit_determinism_digest("p0", "test_qwen_gpu_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.qwen_gpu_validator import (
    QwenGPUCapabilityError,
    get_cuda_version,
    get_gpu_memory_gb,
)


class TestQwenGPUCapabilityError:
    def test_creates(self):
        err = QwenGPUCapabilityError(
            requirement="24GB VRAM",
            current="8GB",
            model="Qwen-72B",
        )
        assert err.requirement == "24GB VRAM"
        assert err.current == "8GB"
        assert err.model == "Qwen-72B"

    def test_is_runtime_error(self):
        assert issubclass(QwenGPUCapabilityError, RuntimeError)

    def test_message_contains_model(self):
        err = QwenGPUCapabilityError("24GB", "8GB", "Qwen-72B")
        assert "Qwen-72B" in str(err)


class TestGetGpuMemoryGb:
    def test_returns_float(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            result = get_gpu_memory_gb()
            assert isinstance(result, float)

    def test_fallback_returns_zero(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = get_gpu_memory_gb()
            assert result == 0.0


class TestGetCudaVersion:
    def test_returns_string(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            result = get_cuda_version()
            assert isinstance(result, str)
