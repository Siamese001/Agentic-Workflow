"""Smoke tests for safe_subprocess exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestSafeSubprocess:
    """Smoke tests for safe_subprocess exports."""

    def test_safe_subprocess_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "safe_subprocess")
        assert module is not None

    def test_safe_subprocess_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "SafeSubprocess")
        assert klass is not None

    def test_safe_subprocess_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_safe_subprocess")
        assert callable(validator)
