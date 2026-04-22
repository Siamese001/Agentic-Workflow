"""Behavioral tests for ``agentic_core.L0_routing.enforcement.execution_gateway``.

Targets the tractable surfaces of V15ExecutionGateway without spinning up
the full healing + guardian stack:

- Error classes: ExecutionGatewayError (holds original_error), UnregisteredAgentError.
- GatewayResult dataclass (field defaults, factory, mutable/immutable semantics).
- V15ExecutionGateway.__init__ state (clock, seen_signals, registry_digest).
- clock property exposes SemanticClock.
- _enforce_agent_registered:
    * empty / whitespace agent_id → UnregisteredAgentError
    * non-existent agent_id → UnregisteredAgentError with helpful message
    * registry RuntimeError → ExecutionGatewayError wraps it
    * registered real agent → no raise
- execute():
    * empty agent_id → UnregisteredAgentError
    * SOFT_FAIL via duplicate-signal dedupe → returns failed GatewayResult with
      SOFT_FAIL error prefix (no mutation).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.agents.types.agent_registry import list_agent_ids
from agentic_core.L0_routing.enforcement import execution_gateway as mod
from agentic_core.L0_routing.enforcement.execution_gateway import (
    ExecutionGatewayError,
    GatewayResult,
    UnregisteredAgentError,
    V15ExecutionGateway,
)
from agentic_core.L0_routing.types.determinism_types import (
    FixConstraint,
    SemanticClock,
    SurgicalManifest,
)


# ---- helpers ------------------------------------------------------------

_REAL_AGENT_ID = list_agent_ids()[0]  # guaranteed registered


def _manifest(correlation_id: str = "cid-1", node_id: str = "node-1") -> SurgicalManifest:
    """Build a valid SurgicalManifest with all 10 required fields (§1.1/§1.3)."""
    import hashlib
    ast_snippet = "pass"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=correlation_id,
        node_id=node_id,
        target_layer="L2",
        ast_snippet=ast_snippet,
        serialization_canon="canon-v1",
        fix_constraint=FixConstraint.STRICT,
        manifest_hash=hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest(),
        change_history=(),
        provenance_chain=(),
    )


def _state_hash() -> tuple[str, str, str]:
    return ("fs-hash", "git-hash", "mem-hash")


def _heal_ok(_m: SurgicalManifest) -> dict[str, Any]:  # pragma: no cover
    return {"errors": 0}


# ---- Error classes ------------------------------------------------------

class TestExceptionClasses:
    def test_execution_gateway_error_is_runtime_error(self) -> None:
        assert issubclass(ExecutionGatewayError, RuntimeError)

    def test_execution_gateway_error_holds_original(self) -> None:
        original = ValueError("root-cause")
        exc = ExecutionGatewayError("wrapper", original_error=original)
        assert exc.original_error is original
        assert "wrapper" in str(exc)

    def test_execution_gateway_error_default_original_none(self) -> None:
        exc = ExecutionGatewayError("wrapper")
        assert exc.original_error is None

    def test_unregistered_agent_error_is_runtime_error(self) -> None:
        assert issubclass(UnregisteredAgentError, RuntimeError)


# ---- GatewayResult ------------------------------------------------------

class TestGatewayResult:
    def test_minimal_fields(self) -> None:
        r = GatewayResult(
            success=True, manifest=None, semantic_clock_tick=0, pre_snapshot=None,
        )
        assert r.success is True
        assert r.manifest is None
        assert r.semantic_clock_tick == 0
        assert r.post_snapshot is None
        assert r.rollback_verified is False
        assert r.healing_output == {}
        assert r.error is None
        assert r.dedupe_hit is False
        assert r.registry_hash == ""

    def test_healing_output_default_independent(self) -> None:
        """dataclass default_factory must give each instance its own dict."""
        r1 = GatewayResult(
            success=True, manifest=None, semantic_clock_tick=0, pre_snapshot=None,
        )
        r2 = GatewayResult(
            success=True, manifest=None, semantic_clock_tick=0, pre_snapshot=None,
        )
        r1.healing_output["x"] = 1
        assert "x" not in r2.healing_output

    def test_fields_mutable(self) -> None:
        r = GatewayResult(
            success=False, manifest=None, semantic_clock_tick=0, pre_snapshot=None,
        )
        r.success = True
        r.error = "later"
        assert r.success is True
        assert r.error == "later"


# ---- V15ExecutionGateway construction & clock --------------------------

class TestGatewayConstruction:
    def test_init_state(self) -> None:
        gw = V15ExecutionGateway()
        assert isinstance(gw.clock, SemanticClock)
        assert gw._seen_signals == set()
        assert gw._pipe_violations == []
        assert gw._policy_violations == []
        assert gw._mismatch_tracker is None
        # registry_digest should be non-empty given known registered agents
        assert gw._registry_digest

    def test_clock_property_returns_same_instance(self) -> None:
        gw = V15ExecutionGateway()
        assert gw.clock is gw.clock

    def test_clock_property_readonly(self) -> None:
        gw = V15ExecutionGateway()
        with pytest.raises(AttributeError):
            gw.clock = SemanticClock()  # type: ignore[misc]


# ---- _enforce_agent_registered ------------------------------------------

class TestEnforceAgentRegistered:
    def test_empty_raises(self) -> None:
        gw = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError, match="non-empty"):
            gw._enforce_agent_registered("")

    def test_whitespace_raises(self) -> None:
        gw = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError, match="non-empty"):
            gw._enforce_agent_registered("   ")

    def test_unknown_agent_raises(self) -> None:
        gw = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError, match="not registered"):
            gw._enforce_agent_registered("definitely-not-an-agent")

    def test_known_agent_passes(self) -> None:
        gw = V15ExecutionGateway()
        gw._enforce_agent_registered(_REAL_AGENT_ID)  # no raise

    def test_runtime_error_wrapped(self) -> None:
        gw = V15ExecutionGateway()
        with patch.object(mod, "get_profile", side_effect=RuntimeError("registry-down")):
            with pytest.raises(ExecutionGatewayError, match="registry lookup failed") as info:
                gw._enforce_agent_registered("any")
        assert isinstance(info.value.__cause__, RuntimeError)


# ---- execute() agent_id contract ----------------------------------------

class TestExecuteAgentIdContract:
    def test_empty_agent_id_raises(self) -> None:
        gw = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError):
            gw.execute(
                execution_input=_manifest(),
                heal_fn=_heal_ok,
                state_hash_fn=_state_hash,
                agent_id="",
            )

    def test_unregistered_agent_id_raises(self) -> None:
        gw = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError):
            gw.execute(
                execution_input=_manifest(),
                heal_fn=_heal_ok,
                state_hash_fn=_state_hash,
                agent_id="ghost-agent-xyz",
            )


# ---- SOFT_FAIL dedupe path ----------------------------------------------

class TestSoftFailDedupePath:
    """Duplicate-signal detection lives inside _validate_manifest and raises
    V15SoftFailAbort. execute() catches SOFT_FAIL and returns a failed
    GatewayResult — this is the cleanest end-to-end path through execute().
    """

    def test_duplicate_signal_returns_softfail_result(self) -> None:
        gw = V15ExecutionGateway()
        # Pre-seed seen signals so the first (and only) validate call trips dedupe
        from agentic_core.L0_routing.types.determinism_contracts_types import dedupe_sha256
        m = _manifest(correlation_id="abc", node_id="xyz")
        gw._seen_signals.add(dedupe_sha256(m.correlation_id + m.node_id))

        result = gw.execute(
            execution_input=m,
            heal_fn=_heal_ok,
            state_hash_fn=_state_hash,
            agent_id=_REAL_AGENT_ID,
        )

        assert result.success is False
        assert result.error is not None
        assert result.error.startswith("SOFT_FAIL")
        assert "Duplicate signal" in result.error
        assert result.dedupe_hit is False  # explicit per implementation
        assert result.manifest is m
        # Clock must not have advanced past its initial step_id
        assert result.semantic_clock_tick == gw.clock.step_id
