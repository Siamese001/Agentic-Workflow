"""V15 P7 Wave 7.2.1 — Runtime Pipe Order Enforcement Tests.

Proves:
- Normal execution advances through all 10 pipe steps without violation.
- Out-of-order step triggers a recorded violation in LOG_ONLY mode.
- Out-of-order step blocks/raises in HARD_FAIL mode.
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
    PipeOrderEnforcer,
    PipeOrderViolation,
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


class TestPipeOrderUnit:
    """Unit tests for PipeOrderEnforcer itself."""

    def test_correct_order_completes(self):
        pipe = PipeOrderEnforcer()
        from agentic_core.L0_maintenance.types.v15_types import HEALER_PIPE_ORDER

        for step in HEALER_PIPE_ORDER:
            pipe.advance(step)
        assert pipe.is_complete

    def test_wrong_step_raises(self):
        pipe = PipeOrderEnforcer()
        with pytest.raises(PipeOrderViolation) as exc_info:
            pipe.advance("commit")  # should be schema_validation first
        assert exc_info.value.expected == "schema_validation"
        assert exc_info.value.actual == "commit"


class TestGatewayPipeOrder:
    """Integration tests: pipe order in V15ExecutionGateway."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_normal_execution_no_pipe_violations(self):
        """Normal execute() should advance all 10 steps with zero violations."""
        gw = V15ExecutionGateway()
        manifest = _make_manifest()
        result = gw.execute(manifest, _noop_heal, _noop_state_hash, trace_id="CC3AL1-AAAAAAAA")
        assert result.success
        assert len(gw._pipe_violations) == 0

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_out_of_order_recorded_in_log_mode(self):
        """Simulate a pipe order violation: call _pipe_advance out of order.

        In LOG_ONLY mode, violation is recorded but not raised.
        """
        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()
        # Advance to step 1 correctly
        gw._pipe_advance(pipe, "schema_validation", "test-trace")
        # Now skip to step 3 — should trigger violation (expected: hash_verification)
        gw._pipe_advance(pipe, "immediate_rollback_on_mismatch", "test-trace")
        assert len(gw._pipe_violations) == 1
        v = gw._pipe_violations[0]
        assert v["type"] == "pipe_order_violation"
        assert v["expected"] == "hash_verification"
        assert v["actual"] == "immediate_rollback_on_mismatch"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_out_of_order_raises_in_hard_fail(self):
        """In HARD_FAIL mode, pipe order violation must raise."""
        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()
        gw._pipe_advance(pipe, "schema_validation", "test-trace")
        with pytest.raises(PipeOrderViolation):
            gw._pipe_advance(pipe, "commit", "test-trace")
