"""Smoke tests for serving_profile_constants exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestServingProfileConstants:
    """Smoke tests for serving_profile_constants exports."""

    def test_serving_profile_constants_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "serving_profile_constants")
        assert module is not None

    def test_serving_profile_constants_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "ServingProfileConstants")
        assert klass is not None

    def test_serving_profile_constants_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_serving_profile_constants")
        assert callable(validator)
