"""Smoke tests for llm_replay_types_adg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestLlmReplayTypesAdg:
    """Smoke tests for llm_replay_types_adg exports."""

    def test_llm_replay_types_adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "llm_replay_types_adg")
        assert module is not None

    def test_llm_replay_types_adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "LlmReplayTypesAdg")
        assert klass is not None

    def test_llm_replay_types_adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_llm_replay_types_adg")
        assert callable(validator)
