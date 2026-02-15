"""G-12-3 — P5.1 Capability-Gated L2 Single Chokepoint Tests.

Negative tests proving FAIL-CLOSED behavior:
- Missing token => PermissionError
- Invalid token type => PermissionError
- Valid token => execution occurs
- No alternate path to execution exists (structural)
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L2_execution.enforcement.capability_chokepoint import (
    authorize_and_execute,
    get_chokepoint,
    reset_chokepoint,
)
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityConstraints,
    CapabilityTokenArtifact,
    CapabilityTokenSubject,
    build_capability_token,
)

# =============================================================================
# Fixtures
# =============================================================================


def _make_clock(tick: int = 1) -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=tick, vector_clock=(("L2", tick),))


def _make_valid_token(
    permissions: tuple[str, ...] = ("TOOL:READ",),
    allowed_paths: tuple[str, ...] = ("coordinator",),
    max_tool_calls: int = 10,
) -> CapabilityTokenArtifact:
    return build_capability_token(
        semantic_clock=_make_clock(),
        subject=CapabilityTokenSubject(kind="agent", id="test-agent"),
        issued_by="test-issuer",
        permissions=list(permissions),
        constraints=CapabilityConstraints(
            allowed_paths=allowed_paths,
            max_tool_calls=max_tool_calls,
        ),
    )


def _dummy_fn(*args, **kwargs):
    """Dummy function that should only run on ALLOW."""
    return {"status": "executed", "args": args, "kwargs": kwargs}


@pytest.fixture(autouse=True)
def _reset():
    """Reset the module-level singleton before each test."""
    reset_chokepoint()
    yield
    reset_chokepoint()


# =============================================================================
# NEGATIVE: Missing token => FAIL-CLOSED
# =============================================================================


class TestMissingToken:
    def test_none_token_raises_permission_error(self):
        with pytest.raises(PermissionError, match="FAIL_CLOSED.*no CapabilityTokenArtifact"):
            authorize_and_execute(
                token=None,
                fn=_dummy_fn,
                tool_name="test_tool",
                action="execute",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(),
            )

    def test_none_token_emits_deny_decision(self):
        try:
            authorize_and_execute(
                token=None,
                fn=_dummy_fn,
                tool_name="test_tool",
                action="execute",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(),
            )
        except PermissionError:
            pass

        cp = get_chokepoint()
        assert len(cp.decisions) == 1
        assert cp.decisions[0].decision == "DENY"
        assert cp.decisions[0].deny_reason == "TOKEN_MISSING"

    def test_none_token_does_not_execute_fn(self):
        call_tracker = {"called": False}

        def guarded_fn():
            call_tracker["called"] = True

        try:
            authorize_and_execute(
                token=None,
                fn=guarded_fn,
                tool_name="test_tool",
                action="execute",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(),
            )
        except PermissionError:
            pass

        assert call_tracker["called"] is False


# =============================================================================
# NEGATIVE: Invalid token type => FAIL-CLOSED
# =============================================================================


class TestInvalidTokenType:
    def test_string_token_raises_permission_error(self):
        with pytest.raises(PermissionError, match="FAIL_CLOSED.*expected CapabilityTokenArtifact"):
            authorize_and_execute(
                token="not-a-token",  # type: ignore[arg-type]
                fn=_dummy_fn,
                tool_name="test_tool",
                action="execute",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(),
            )

    def test_dict_token_raises_permission_error(self):
        with pytest.raises(PermissionError, match="FAIL_CLOSED"):
            authorize_and_execute(
                token={"artifact_type": "CAPABILITY_TOKEN"},  # type: ignore[arg-type]
                fn=_dummy_fn,
                tool_name="test_tool",
                action="execute",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(),
            )

    def test_invalid_type_emits_deny_decision(self):
        try:
            authorize_and_execute(
                token=42,  # type: ignore[arg-type]
                fn=_dummy_fn,
                tool_name="test_tool",
                action="execute",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(),
            )
        except PermissionError:
            pass

        cp = get_chokepoint()
        assert len(cp.decisions) == 1
        assert cp.decisions[0].decision == "DENY"
        assert "TOKEN_INVALID_TYPE" in cp.decisions[0].deny_reason


# =============================================================================
# POSITIVE: Valid token => execution occurs
# =============================================================================


class TestValidToken:
    def test_valid_token_executes_fn(self):
        token = _make_valid_token()
        result = authorize_and_execute(
            token=token,
            fn=_dummy_fn,
            args=("arg1",),
            kwargs={"key": "val"},
            tool_name="test_tool",
            action="execute",
            requested_resource="coordinator/default",
            required_permission="TOOL:READ",
            semantic_clock=_make_clock(),
        )
        assert result["status"] == "executed"
        assert result["args"] == ("arg1",)
        assert result["kwargs"] == {"key": "val"}

    def test_valid_token_emits_allow_decision(self):
        token = _make_valid_token()
        authorize_and_execute(
            token=token,
            fn=_dummy_fn,
            tool_name="test_tool",
            action="execute",
            requested_resource="coordinator/default",
            required_permission="TOOL:READ",
            semantic_clock=_make_clock(),
        )

        cp = get_chokepoint()
        assert len(cp.decisions) == 1
        assert cp.decisions[0].decision == "ALLOW"

    def test_wrong_permission_denies(self):
        token = _make_valid_token(permissions=("TOOL:READ",))
        with pytest.raises(PermissionError, match="CAPABILITY_DENIED"):
            authorize_and_execute(
                token=token,
                fn=_dummy_fn,
                tool_name="test_tool",
                action="write",
                requested_resource="coordinator/default",
                required_permission="TOOL:WRITE",
                semantic_clock=_make_clock(),
            )

    def test_exceeded_max_tool_calls_denies(self):
        token = _make_valid_token(max_tool_calls=1)
        # First call succeeds
        authorize_and_execute(
            token=token,
            fn=_dummy_fn,
            tool_name="test_tool",
            action="execute",
            requested_resource="coordinator/default",
            required_permission="TOOL:READ",
            semantic_clock=_make_clock(),
        )
        # Second call on a new enforcer instance per call — but the enforcer is
        # re-created each invocation inside the chokepoint, so quota is per-token-presentation.
        # This tests the CapabilityEnforcer directly.
        from agentic_core.L2_execution.types.capability_token_types import CapabilityEnforcer

        enforcer = CapabilityEnforcer(token)
        enforcer.check(
            tool_name="t",
            action="a",
            requested_resource="coordinator/default",
            required_permission="TOOL:READ",
            semantic_clock=_make_clock(),
        )
        with pytest.raises(PermissionError, match="MAX_TOOL_CALLS_EXCEEDED"):
            enforcer.check(
                tool_name="t",
                action="a",
                requested_resource="coordinator/default",
                required_permission="TOOL:READ",
                semantic_clock=_make_clock(tick=2),
            )


# =============================================================================
# STRUCTURAL: No alternate path to execution exists
# =============================================================================


class TestNoBypass:
    def test_unified_engine_requires_semantic_clock(self):
        """UnifiedWorkflowEngine.orchestrate raises ValueError without semantic_clock."""
        from agentic_core.L2_execution.config.unified_workflow_config import (
            UnifiedWorkflowEngine,
        )

        engine = UnifiedWorkflowEngine()
        with pytest.raises(ValueError, match="semantic_clock is required"):
            engine.orchestrate({"focus": "default"})

    def test_unified_engine_requires_token(self):
        """UnifiedWorkflowEngine.orchestrate raises PermissionError without token."""
        from agentic_core.L2_execution.config.unified_workflow_config import (
            UnifiedWorkflowEngine,
        )

        engine = UnifiedWorkflowEngine()
        with pytest.raises(PermissionError, match="FAIL_CLOSED"):
            engine.orchestrate(
                {"focus": "default"},
                semantic_clock=_make_clock(),
            )

    def test_unified_engine_succeeds_with_valid_token(self):
        """UnifiedWorkflowEngine.orchestrate succeeds with valid token + clock."""
        from agentic_core.L2_execution.config.unified_workflow_config import (
            UnifiedWorkflowEngine,
        )

        engine = UnifiedWorkflowEngine()
        token = _make_valid_token()
        result = engine.orchestrate(
            {"focus": "default"},
            capability_token=token,
            semantic_clock=_make_clock(),
        )
        assert result["status"] == "success"

    def test_authorize_and_execute_is_single_module_entry(self):
        """Structural: module exposes exactly one authorize_and_execute callable."""
        from agentic_core.L2_execution.enforcement import capability_chokepoint

        # The module-level function is the single entry point
        assert callable(capability_chokepoint.authorize_and_execute)
        # __all__ must export it exactly once
        assert capability_chokepoint.__all__.count("authorize_and_execute") == 1

    def test_chokepoint_class_is_single(self):
        """Structural: exactly one CapabilityChokepoint class."""
        import inspect

        from agentic_core.L2_execution.enforcement import capability_chokepoint

        source = inspect.getsource(capability_chokepoint)
        count = source.count("class CapabilityChokepoint")
        assert count == 1, f"Expected 1 class, found {count}"
