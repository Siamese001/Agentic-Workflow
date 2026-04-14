"""Smoke tests for token_cap_enforced exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestTokenCapEnforced:
    """Smoke tests for token_cap_enforced exports."""

    def test_token_cap_enforced_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "token_cap_enforced")
        assert module is not None

    def test_token_cap_enforced_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "TokenCapEnforced")
        assert klass is not None

    def test_token_cap_enforced_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_token_cap_enforced")
        assert callable(validator)
