"""Test QwenVllmInferenceAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQwenVllmInferenceAdg:
    """Test QwenVllmInferenceAdg functionality."""

    def test_qwen_vllm_inference_adg_imports(self):
        """Test qwen_vllm_inference_adg module imports."""
        from agentic_core import qwen_vllm_inference_adg
        assert qwen_vllm_inference_adg is not None

    def test_qwen_vllm_inference_adg_class(self):
        """Test QwenVllmInferenceAdg class exists."""
        from agentic_core import QwenVllmInferenceAdg
        assert QwenVllmInferenceAdg is not None

    def test_qwen_vllm_inference_adg_callable(self):
        """Test qwen_vllm_inference_adg functions are callable."""
        from agentic_core import validate_qwen_vllm_inference_adg
        assert callable(validate_qwen_vllm_inference_adg)
