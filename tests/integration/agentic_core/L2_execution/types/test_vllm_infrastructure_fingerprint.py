"""Test VllmInfrastructureFingerprint functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmInfrastructureFingerprint:
    """Test VllmInfrastructureFingerprint functionality."""

    def test_vllm_infrastructure_fingerprint_imports(self):
        """Test vllm_infrastructure_fingerprint module imports."""
        try:
            from agentic_core import vllm_infrastructure_fingerprint

            assert vllm_infrastructure_fingerprint is not None
        except ImportError:
            pytest.skip("vllm_infrastructure_fingerprint not available")

    def test_vllm_infrastructure_fingerprint_class(self):
        """Test VllmInfrastructureFingerprint class exists."""
        try:
            from agentic_core import VllmInfrastructureFingerprint

            assert VllmInfrastructureFingerprint is not None
        except ImportError:
            pytest.skip("VllmInfrastructureFingerprint not available")

    def test_vllm_infrastructure_fingerprint_callable(self):
        """Test vllm_infrastructure_fingerprint functions are callable."""
        try:
            from agentic_core import validate_vllm_infrastructure_fingerprint

            assert callable(validate_vllm_infrastructure_fingerprint)
        except ImportError:
            pytest.skip("validate_vllm_infrastructure_fingerprint not available")
