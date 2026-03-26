"""ADG-driven tests for agentic_core/runtime/types/__init__.py — fan_in=4.

Contract tests: all __all__ re-exports must be importable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestRuntimeTypesPublicAPI:
    def test_all_exports_present(self):
        import agentic_core.runtime.types as m
        from agentic_core.runtime.types import CacheEntry
        from agentic_core.runtime.types import CacheMiss
        import agentic_core.runtime.types
        from agentic_core.runtime.types import ClaimType
        from agentic_core.runtime.types import BudgetExceededError
        from agentic_core.runtime.types import ExpansionStrategy
        from agentic_core.runtime.types import HyDeDocument
        from agentic_core.runtime.types import CostGovernor
        from agentic_core.runtime.types import get_global_cost_governor
        from agentic_core.runtime.types import track_api_call
        from agentic_core.runtime.types import CacheEntry as shim
        from agentic_core.runtime.types.cache_entry_types import CacheEntry as canon
        from agentic_core.runtime.types import Claim as shim
        from agentic_core.runtime.types.claim_type_types import Claim as canon
        from agentic_core.runtime.types import BudgetExceededError as shim
        from agentic_core.runtime.types.cost_governor_types import BudgetExceededError as canon
#  # MOVED: import agentic_core.runtime.types as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_cache_entry_importable(self):
#  # MOVED: from agentic_core.runtime.types import CacheEntry
        assert callable(CacheEntry)

    def test_cache_miss_importable(self):
#  # MOVED: from agentic_core.runtime.types import CacheMiss
        assert callable(CacheMiss)

"""Test agentic_core import functionality."""
#  # MOVED: import agentic_core.runtime.types
# Basic functionality assertion
assert True  # Replace with meaningful assertion
    def test_claim_type_importable(self):
#  # MOVED: from agentic_core.runtime.types import ClaimType
        assert ClaimType is not None

    def test_budget_exceeded_error_importable(self):
#  # MOVED: from agentic_core.runtime.types import BudgetExceededError
        assert issubclass(BudgetExceededError, Exception)

    def test_expansion_strategy_importable(self):
#  # MOVED: from agentic_core.runtime.types import ExpansionStrategy
        assert ExpansionStrategy is not None

    def test_hyde_document_importable(self):
#  # MOVED: from agentic_core.runtime.types import HyDeDocument
        assert callable(HyDeDocument)

    def test_cost_governor_importable(self):
#  # MOVED: from agentic_core.runtime.types import CostGovernor
        assert callable(CostGovernor)

    def test_get_global_cost_governor_callable(self):
#  # MOVED: from agentic_core.runtime.types import get_global_cost_governor
        assert callable(get_global_cost_governor)

    def test_track_api_call_callable(self):
#  # MOVED: from agentic_core.runtime.types import track_api_call
        assert callable(track_api_call)


class TestRuntimeTypesShimIdentity:
    """Re-exports must be identical to canonical source."""

    def test_cache_entry_identity(self):
#  # MOVED: from agentic_core.runtime.types import CacheEntry as shim
#  # MOVED: from agentic_core.runtime.types.cache_entry_types import CacheEntry as canon
        assert shim is canon

    def test_claim_identity(self):
#  # MOVED: from agentic_core.runtime.types import Claim as shim
#  # MOVED: from agentic_core.runtime.types.claim_type_types import Claim as canon
        assert shim is canon

    def test_budget_exceeded_error_identity(self):
#  # MOVED: from agentic_core.runtime.types import BudgetExceededError as shim
#  # MOVED: from agentic_core.runtime.types.cost_governor_types import BudgetExceededError as canon
        assert shim is canon
