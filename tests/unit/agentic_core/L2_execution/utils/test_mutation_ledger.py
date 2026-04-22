"""Smoke tests for mutation_ledger exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestMutationLedger:
    """Smoke tests for mutation_ledger exports."""

    def test_mutation_ledger_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "mutation_ledger")
        assert module is not None

    def test_mutation_ledger_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "MutationLedger")
        assert klass is not None

    def test_mutation_ledger_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_mutation_ledger")
        assert callable(validator)
