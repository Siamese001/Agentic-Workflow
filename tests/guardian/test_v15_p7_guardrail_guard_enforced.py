"""V15 P7 Wave 1.7 — GuardrailGuard Enforcement at V15 Gateway Boundary.

Proves:
- GuardrailGuard.enforce_all is called exactly once per gateway execution.
- If enforce_all returns False the gateway raises V15HardFailAbort.
- The boundary_token passed to enforce_all matches the pre-snapshot trace_id.
"""

from __future__ import annotations

import hashlib
import os
from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
    V15ExecutionGateway,
)
from agentic_core.L0_maintenance.types.guardian_contract import V15HardFailAbort
from agentic_core.L0_maintenance.types.v15_contracts import GuardrailGuard
from agentic_core.L0_maintenance.types.v15_p2_types import (
    FixConstraint,
    SurgicalManifest,
)

# ---------------------------------------------------------------------------
# Helpers (match test_v15_p7_policy_guard.py style)
# ---------------------------------------------------------------------------


def _make_manifest(trace_id: str = "CC3AL1-GG000001") -> SurgicalManifest:
    ast_snippet = "heal(guardrail_test)"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="GuardrailNode",
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGuardrailGuardEnforced:
    """Integration tests: GuardrailGuard wired into V15ExecutionGateway."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_guardrail_runs_and_blocks_on_false(self):
        """If enforce_all returns False, gateway must raise V15HardFailAbort."""
        gw = V15ExecutionGateway()
        manifest = _make_manifest()

        with patch.object(
            GuardrailGuard,
            "enforce_all",
            return_value=False,
        ):
            with pytest.raises(V15HardFailAbort, match="GuardrailGuard"):
                gw.execute(
                    manifest,
                    _noop_heal,
                    _noop_state_hash,
                    trace_id="CC3AL1-GG000002",
                )

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_guardrail_receives_boundary_token(self):
        """boundary_token passed to enforce_all must be non-empty and match
        the gateway trace_id (which becomes pre_snapshot.trace_id)."""
        captured_kwargs: dict = {}

        def _spy_enforce_all(self, **kwargs):
            captured_kwargs.update(kwargs)
            return True

        gw = V15ExecutionGateway()
        manifest = _make_manifest()
        trace = "CC3AL1-GG000003"

        with patch.object(
            GuardrailGuard,
            "enforce_all",
            _spy_enforce_all,
        ):
            result = gw.execute(
                manifest,
                _noop_heal,
                _noop_state_hash,
                trace_id=trace,
            )

        assert result.success
        assert "boundary_token" in captured_kwargs
        bt = captured_kwargs["boundary_token"]
        assert bt and bt.strip(), "boundary_token must be non-empty"
        # The gateway passes pre_snapshot.trace_id which equals the gateway trace_id
        assert bt == trace

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_guardrail_called_once(self):
        """enforce_all must be called exactly once per gateway execution."""
        call_count = 0

        def _counting_enforce_all(self, **kwargs):
            nonlocal call_count
            call_count += 1
            return True

        gw = V15ExecutionGateway()
        manifest = _make_manifest()

        with patch.object(
            GuardrailGuard,
            "enforce_all",
            _counting_enforce_all,
        ):
            gw.execute(
                manifest,
                _noop_heal,
                _noop_state_hash,
                trace_id="CC3AL1-GG000004",
            )

        assert call_count == 1, f"Expected 1 call, got {call_count}"
