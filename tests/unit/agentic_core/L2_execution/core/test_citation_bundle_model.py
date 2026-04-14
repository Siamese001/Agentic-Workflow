"""Smoke tests for citation_bundle_model exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip, import_module_or_skip


@pytest.mark.unit
class TestCitationBundleModel:
    """Smoke tests for citation_bundle_model exports."""

    def test_citation_bundle_imports(self) -> None:
        """Import submodule."""
        module = import_module_or_skip("agentic_core.L1_cognition.citation_bundle_model")
        assert module is not None

    def test_citation_bundle_class(self) -> None:
        """Import CitationBundle."""
        klass = import_attr_or_skip("agentic_core.L1_cognition.citation_bundle_model", "CitationBundle")
        assert klass is not None

    def test_validate_citation_bundle(self) -> None:
        """Import validate_citation_bundle."""
        validator = import_attr_or_skip(
            "agentic_core.L1_cognition.citation_bundle_model", "validate_citation_bundle"
        )
        assert callable(validator)
