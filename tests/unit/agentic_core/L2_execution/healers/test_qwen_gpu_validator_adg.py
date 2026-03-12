"""ADG-driven tests for L2_execution/healers/qwen_gpu_validator.py — fan_in=1."""
from __future__ import annotations

import pytest
from unittest.mock import patch

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.qwen_gpu_validator import (
    QwenGPUCapabilityError,
    get_gpu_memory_gb,
    get_cuda_version,
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
