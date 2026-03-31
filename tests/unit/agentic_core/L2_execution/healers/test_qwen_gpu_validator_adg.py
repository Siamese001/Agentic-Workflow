"""Test QwenGpuValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQwenGpuValidatorAdg:
    """Test QwenGpuValidatorAdg functionality."""

    def test_qwen_gpu_validator_adg_imports(self):
        """Test qwen_gpu_validator_adg module imports."""
        from agentic_core import qwen_gpu_validator_adg
        assert qwen_gpu_validator_adg is not None

    def test_qwen_gpu_validator_adg_class(self):
        """Test QwenGpuValidatorAdg class exists."""
        from agentic_core import QwenGpuValidatorAdg
        assert QwenGpuValidatorAdg is not None

    def test_qwen_gpu_validator_adg_callable(self):
        """Test qwen_gpu_validator_adg functions are callable."""
        from agentic_core import validate_qwen_gpu_validator_adg
        assert callable(validate_qwen_gpu_validator_adg)
