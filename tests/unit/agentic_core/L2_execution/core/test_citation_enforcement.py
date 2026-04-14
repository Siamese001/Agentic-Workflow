"""Smoke tests for CitationEnforcement exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestCitationEnforcement:
    """Smoke tests for CitationEnforcement exports."""

    def test_citation_enforcement_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "citation_enforcement")
        assert module is not None

    def test_citation_enforcement_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "CitationEnforcement")
        assert klass is not None

    def test_citation_enforcement_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_citation_enforcement")
        assert callable(validator)
