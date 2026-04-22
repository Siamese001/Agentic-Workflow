"""Smoke tests for EmbeddingSovereignAgent exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestEmbeddingsovereignagent:
    """Smoke tests for EmbeddingSovereignAgent exports."""

    def test_EmbeddingSovereignAgent_imports(self) -> None:
        """Import module export."""
        symbol = import_attr_or_skip("agentic_core", "EmbeddingSovereignAgent")
        assert symbol is not None

    def test_EmbeddingSovereignAgent_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "Embeddingsovereignagent")
        assert klass is not None

    def test_EmbeddingSovereignAgent_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_EmbeddingSovereignAgent")
        assert callable(validator)
