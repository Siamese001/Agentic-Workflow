"""Smoke tests for MutationReplayIntegrity exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestMutationReplayIntegrity:
    """Smoke tests for MutationReplayIntegrity exports."""

    def test_mutation_replay_integrity_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "mutation_replay_integrity")
        assert module is not None

    def test_mutation_replay_integrity_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "MutationReplayIntegrity")
        assert klass is not None

    def test_mutation_replay_integrity_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_mutation_replay_integrity")
        assert callable(validator)
