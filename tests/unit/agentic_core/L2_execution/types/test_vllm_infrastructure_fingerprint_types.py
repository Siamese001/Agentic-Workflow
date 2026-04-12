"""Test VllmInfrastructureFingerprintTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmInfrastructureFingerprintTypes:
    """Test VllmInfrastructureFingerprintTypes functionality."""

    def test_vllm_infrastructure_fingerprint_types_imports(self):
        """Test vllm_infrastructure_fingerprint_types module imports."""
        from agentic_core import vllm_infrastructure_fingerprint_types

        assert vllm_infrastructure_fingerprint_types is not None

    def test_vllm_infrastructure_fingerprint_types_class(self):
        """Test VllmInfrastructureFingerprintTypes class exists."""
        from agentic_core import VllmInfrastructureFingerprintTypes

        assert VllmInfrastructureFingerprintTypes is not None

    def test_vllm_infrastructure_fingerprint_types_callable(self):
        """Test vllm_infrastructure_fingerprint_types functions are callable."""
        from agentic_core import validate_vllm_infrastructure_fingerprint_types

        assert callable(validate_vllm_infrastructure_fingerprint_types)
