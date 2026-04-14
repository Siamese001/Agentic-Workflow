"""Smoke tests for kv_cache_headroom_under_concurrency exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestKvCacheHeadroomUnderConcurrency:
    """Smoke tests for kv_cache_headroom_under_concurrency exports."""

    def test_kv_cache_headroom_under_concurrency_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "kv_cache_headroom_under_concurrency")
        assert module is not None

    def test_kv_cache_headroom_under_concurrency_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "KvCacheHeadroomUnderConcurrency")
        assert klass is not None

    def test_kv_cache_headroom_under_concurrency_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_kv_cache_headroom_under_concurrency")
        assert callable(validator)
