"""Smoke tests for queue_timeout_fallback exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestQueueTimeoutFallback:
    """Smoke tests for queue_timeout_fallback exports."""

    def test_queue_timeout_fallback_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "queue_timeout_fallback")
        assert module is not None

    def test_queue_timeout_fallback_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "QueueTimeoutFallback")
        assert klass is not None

    def test_queue_timeout_fallback_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_queue_timeout_fallback")
        assert callable(validator)
