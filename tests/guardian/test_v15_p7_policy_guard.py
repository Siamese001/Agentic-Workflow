"""V15 P7 Wave 7.2.2 — PolicyConfigGuard at Wave Start Tests.

Proves:
- Unchanged policy passes without violation.
- Mutation detected and recorded in LOG_ONLY mode.
- Mutation blocks/raises in HARD_FAIL mode.
"""

from __future__ import annotations

import hashlib
import os
from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
    V15ExecutionGateway,
)
from agentic_core.L0_maintenance.types.v15_contracts import (
    PolicyConfigGuard,
    PolicyMutationIncident,
)
from agentic_core.L0_maintenance.types.v15_p2_types import (
    FixConstraint,
    SurgicalManifest,
)


def _make_manifest(trace_id: str = "CC3AL1-00000001") -> SurgicalManifest:
    ast_snippet = "heal(test)"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="TestNode",
        target_layer="L2",
        ast_snippet=ast_snippet,
        serialization_canon="test",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


def _noop_heal(manifest):
    return {"status": "completed", "errors": 0}


def _noop_state_hash():
    return ("aaa", "bbb", "ccc")


class TestPolicyConfigGuardUnit:
    """Unit tests for PolicyConfigGuard itself."""

    def test_unchanged_policy_passes(self):
        cfg = {"max_retries": 3, "timeout": 60}
        guard = PolicyConfigGuard(policy_config=cfg, wave_id="w1")
        # Same config → no exception
        guard.read_config(cfg)

    def test_mutated_policy_raises(self):
        cfg = {"max_retries": 3, "timeout": 60}
        guard = PolicyConfigGuard(policy_config=cfg, wave_id="w1")
        mutated = {"max_retries": 999, "timeout": 60}
        with pytest.raises(PolicyMutationIncident) as exc_info:
            guard.read_config(mutated)
        assert exc_info.value.wave_id == "w1"


class TestGatewayPolicyGuard:
    """Integration tests: PolicyConfigGuard in V15ExecutionGateway."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_no_mutation_no_violation(self):
        """Execute with unchanged policy_config → zero policy violations."""
        gw = V15ExecutionGateway()
        manifest = _make_manifest()
        cfg = {"key": "value"}
        result = gw.execute(
            manifest,
            _noop_heal,
            _noop_state_hash,
            trace_id="CC3AL1-BBBBBBBB",
            policy_config=cfg,
        )
        assert result.success
        assert len(gw._policy_violations) == 0

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_mutation_recorded_in_log_mode(self):
        """Simulate policy mutation mid-wave via _policy_check.

        In LOG_ONLY mode, violation is recorded but not raised.
        """
        gw = V15ExecutionGateway()
        original = {"key": "original"}
        guard = PolicyConfigGuard(policy_config=original, wave_id="test-wave")
        mutated = {"key": "mutated"}
        # Should not raise in log mode
        gw._policy_check(guard, mutated, "test-trace")
        assert len(gw._policy_violations) == 1
        v = gw._policy_violations[0]
        assert v["type"] == "policy_mutation"
        assert v["wave_id"] == "test-wave"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_mutation_raises_in_hard_fail(self):
        """In HARD_FAIL mode, policy mutation must raise."""
        gw = V15ExecutionGateway()
        original = {"key": "original"}
        guard = PolicyConfigGuard(policy_config=original, wave_id="test-wave")
        mutated = {"key": "mutated"}
        with pytest.raises(PolicyMutationIncident):
            gw._policy_check(guard, mutated, "test-trace")
