"""
Eternal Sovereign Smoke Test – Session 6 Final Lock.
Run on every commit to validate SSOT runtime integrity.
"""
import pytest
from agentic_core.schemas.models.core_contracts import CORE_CONTRACTS_REGISTRY, RetryPolicy, HopSpec
from typing import Any

@pytest.mark.sovereign
def test_registry_uniqueness() -> Any:
    """Ensure no class is registered twice (Shadow Override check)."""
    unique_classes: Any = set(CORE_CONTRACTS_REGISTRY.values())
    assert len(CORE_CONTRACTS_REGISTRY) == len(unique_classes), f'Registry contains duplicates: {len(CORE_CONTRACTS_REGISTRY)} keys vs {len(unique_classes)} unique classes.'

@pytest.mark.sovereign
def test_pydantic_purity() -> Any:
    """Ensure key models are Pydantic BaseModels, not dataclasses."""
    assert hasattr(RetryPolicy, 'model_dump'), 'RetryPolicy must be a Pydantic model'

@pytest.mark.sovereign
def test_no_underscore_leakage() -> Any:
    """Runtime check: Ensure no public fields start with underscore."""
    policy: Any = RetryPolicy(max_retries=3)
    assert policy.max_retries == 3
    assert not hasattr(policy, '_max_retries')
if __name__ == '__main__':
    pytest.main(['-v', __file__])
