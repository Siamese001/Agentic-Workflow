"""Smoke tests for vllm_replay_validator exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestVllmReplayValidator:
    """Smoke tests for vllm_replay_validator exports."""

    def test_vllm_replay_validator_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "vllm_replay_validator")
        assert module is not None

    def test_vllm_replay_validator_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "VllmReplayValidator")
        assert klass is not None

    def test_vllm_replay_validator_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_vllm_replay_validator")
        assert callable(validator)
