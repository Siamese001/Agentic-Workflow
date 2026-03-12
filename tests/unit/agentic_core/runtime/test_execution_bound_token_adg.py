"""ADG-driven tests for runtime/execution_bound_token.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.execution_bound_token import CapabilityType, ExecutionBoundToken


class TestCapabilityType:
    def test_read_only_value(self):
        assert CapabilityType.READ_ONLY.value == "read_only"

    def test_write_state_value(self):
        assert CapabilityType.WRITE_STATE.value == "write_state"

    def test_mutate_config_value(self):
        assert CapabilityType.MUTATE_CONFIG.value == "mutate_config"

    def test_all_types(self):
        for name in ("READ_ONLY", "WRITE_STATE", "MUTATE_CONFIG", "ACTIVATE_LEARNING"):
            assert hasattr(CapabilityType, name)


class TestExecutionBoundToken:
    def test_creates(self):
        token = ExecutionBoundToken(
            token_id="tok-1",
            capability_type=CapabilityType.READ_ONLY,
            caller_context="AgentA",
            target_context="AgentB",
            execution_trace_id="trace-1",
            policy_hash="phash",
            determinism_digest="ddig",
            hierarchy_hash="hhash",
            signature_hash="sig",
            authority_hash="auth",
        )
        assert token.token_id == "tok-1"
        assert token.capability_type == CapabilityType.READ_ONLY

    def test_is_frozen(self):
        token = ExecutionBoundToken(
            token_id="t2",
            capability_type=CapabilityType.WRITE_STATE,
            caller_context="A",
            target_context="B",
            execution_trace_id="tr",
            policy_hash="p",
            determinism_digest="d",
            hierarchy_hash="h",
            signature_hash="s",
            authority_hash="a",
        )
        with pytest.raises(Exception):
            token.token_id = "modified"

    def test_metadata_default_empty(self):
        token = ExecutionBoundToken(
            token_id="t3",
            capability_type=CapabilityType.READ_ONLY,
            caller_context="X",
            target_context="Y",
            execution_trace_id="tr",
            policy_hash="p",
            determinism_digest="d",
            hierarchy_hash="h",
            signature_hash="s",
            authority_hash="a",
        )
        assert token.metadata == {}
