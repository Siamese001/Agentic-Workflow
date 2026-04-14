"""Smoke tests for payload_formatter_util_adg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestPayloadFormatterUtilAdg:
    """Smoke tests for payload_formatter_util_adg exports."""

    def test_payload_formatter_util_adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "payload_formatter_util_adg")
        assert module is not None

    def test_payload_formatter_util_adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "PayloadFormatterUtilAdg")
        assert klass is not None

    def test_payload_formatter_util_adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_payload_formatter_util_adg")
        assert callable(validator)
