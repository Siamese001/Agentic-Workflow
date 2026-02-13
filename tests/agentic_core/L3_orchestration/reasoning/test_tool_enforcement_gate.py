"""Wave 2.4 — ToolPolicyEnforcer / LawSlotHandler enforcement gate tests.

Tests prove:
1) PASS path: handler returns PASS; tool executes; exactly one artifact emitted
2) BLOCK path: handler returns BLOCK; tool NOT executed; artifact emitted; raises ToolPolicyBlocked
3) MODIFY path: handler returns MODIFY with transformed args; tool executes with new args; both hashes
4) Determinism: same input args -> same original_args_hash; MODIFY produces stable modified_args_hash
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L2_execution.enforcement.tool_policy_enforcer import (
    ToolPolicyEnforcer,
    _stable_args_hash,
    set_tool_policy_enforcer,
)
from agentic_core.L2_execution.types.capability_token_types import (
    PERMISSION_CODES,
    CapabilityConstraints,
    CapabilityTokenSubject,
    build_capability_token,
)
from agentic_core.L2_execution.types.mcp_tool_types import (
    MCPTool,
    MCPToolServer,
)
from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
    ToolEnforcementArtifact,
    ToolPolicyBlocked,
)

# §Wave5.0.5 — deterministic capability token for LawSlotHandler tests.
# These tests exercise the LawSlotHandler enforcement gate (Wave 2.4),
# not capability enforcement. The token lets calls pass the capability
# gate so they reach the LawSlot gate under test.
_TEST_CLOCK = SemanticClockSnapshot(tick=1, vector_clock={"L2": 1})
_TEST_TOKEN = build_capability_token(
    semantic_clock=_TEST_CLOCK,
    subject=CapabilityTokenSubject(kind="test", id="tool-enforcement-gate-test"),
    issued_by="test-harness",
    permissions=(PERMISSION_CODES["TOOL_READ"],),
    constraints=CapabilityConstraints(
        allowed_paths=("tool/test_tool",),
        max_tool_calls=100,
    ),
)

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(autouse=True)
def _reset_enforcer():
    """Reset global enforcer before/after each test."""
    set_tool_policy_enforcer(None)
    yield
    set_tool_policy_enforcer(None)


def _make_server_with_tool(tool_name: str = "test_tool") -> MCPToolServer:
    """Create a MCPToolServer with a single registered tool that tracks calls."""
    server = MCPToolServer(name="test-server")
    call_log: list[dict[str, Any]] = []

    def handler(**kwargs: Any) -> dict[str, Any]:
        call_log.append(kwargs)
        return {"status": "ok", "args_received": kwargs}

    tool = MCPTool(
        name=tool_name,
        description="test tool",
        parameters={},
        handler=handler,
    )
    server.register_tool(tool)
    server._test_call_log = call_log  # type: ignore[attr-defined]
    return server


# =========================================================================
# Unit tests — ToolPolicyEnforcer
# =========================================================================


class TestEnforcerUnit:
    """Unit tests for ToolPolicyEnforcer standalone logic."""

    def test_default_pass_no_rules(self):
        enforcer = ToolPolicyEnforcer()
        outcome, new_args, rationale, slots = enforcer.enforce("any_tool", {"a": 1})
        assert outcome == LawSlotOutcome.PASS
        assert new_args == {"a": 1}
        assert slots == ()

    def test_resolve_slots_returns_configured(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "my_tool",
            outcome=LawSlotOutcome.PASS,
            law_slots=("slot-A", "slot-B"),
        )
        assert enforcer.resolve_slots("my_tool") == ("slot-A", "slot-B")

    def test_block_rule(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "blocked_tool",
            outcome=LawSlotOutcome.BLOCK,
            law_slots=("deny-rule-1",),
            rationale="Denied by policy",
        )
        outcome, _, rationale, slots = enforcer.enforce("blocked_tool", {})
        assert outcome == LawSlotOutcome.BLOCK
        assert rationale == "Denied by policy"
        assert slots == ("deny-rule-1",)

    def test_modify_rule_transforms_args(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "mod_tool",
            outcome=LawSlotOutcome.MODIFY,
            law_slots=("sanitize-1",),
            rationale="Sanitized input",
            arg_transform={"safe_mode": True},
        )
        outcome, new_args, _, _ = enforcer.enforce("mod_tool", {"query": "test"})
        assert outcome == LawSlotOutcome.MODIFY
        assert new_args == {"query": "test", "safe_mode": True}


# =========================================================================
# Artifact construction tests
# =========================================================================


class TestArtifactConstruction:
    """ToolEnforcementArtifact construction and validation."""

    def test_valid_artifact(self):
        enforcer = ToolPolicyEnforcer()
        art = enforcer.build_artifact(
            tool_name="t",
            outcome=LawSlotOutcome.PASS,
            applied_slots=(),
            rationale="ok",
            original_args_hash="abc123",
        )
        assert isinstance(art, ToolEnforcementArtifact)
        assert art.tool_name == "t"
        assert art.outcome == LawSlotOutcome.PASS
        assert art.enforcement_id  # non-empty uuid
        assert art.timestamp_utc  # non-empty

    def test_modify_requires_modified_hash(self):
        with pytest.raises(ValueError, match="modified_args_hash required"):
            ToolEnforcementArtifact(
                enforcement_id="e1",
                timestamp_utc="2026-01-01T00:00:00Z",
                trace_id="t1",
                agent_id="a1",
                tool_name="t",
                outcome=LawSlotOutcome.MODIFY,
                applied_law_slots=(),
                rationale="mod",
                original_args_hash="abc",
                modified_args_hash="",
            )

    def test_artifact_is_frozen(self):
        enforcer = ToolPolicyEnforcer()
        art = enforcer.build_artifact(
            tool_name="t",
            outcome=LawSlotOutcome.PASS,
            applied_slots=(),
            rationale="ok",
            original_args_hash="abc123",
        )
        with pytest.raises(AttributeError):
            art.rationale = "changed"  # type: ignore[misc]


# =========================================================================
# Integration tests — PASS path
# =========================================================================


class TestPassPath:
    """PASS path: tool executes; exactly one artifact emitted; outcome PASS."""

    def test_pass_tool_executes(self):
        server = _make_server_with_tool()
        result = server.execute_tool("test_tool", {"key": "value"}, capability_token=_TEST_TOKEN)
        assert result.success is True
        assert result.result["status"] == "ok"
        assert len(server._test_call_log) == 1  # type: ignore[attr-defined]

    def test_pass_emits_artifact(self):
        server = _make_server_with_tool()
        emitted = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append({"type": type_label, "artifact": artifact})

        with patch(
            "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
            mock_emit,
        ):
            server.execute_tool("test_tool", {"x": 1}, capability_token=_TEST_TOKEN)

        assert len(emitted) == 1
        assert emitted[0]["type"] == "TOOL_ENFORCEMENT"
        art = emitted[0]["artifact"]
        assert art.outcome == LawSlotOutcome.PASS
        assert art.tool_name == "test_tool"

    def test_pass_with_configured_slots(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.PASS,
            law_slots=("audit-1", "audit-2"),
            rationale="Audit pass",
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        emitted = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append(artifact)

        with patch(
            "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
            mock_emit,
        ):
            result = server.execute_tool("test_tool", {"a": 1}, capability_token=_TEST_TOKEN)

        assert result.success is True
        assert len(emitted) == 1
        assert emitted[0].applied_law_slots == ("audit-1", "audit-2")


# =========================================================================
# Integration tests — BLOCK path
# =========================================================================


class TestBlockPath:
    """BLOCK path: tool NOT executed; artifact emitted; raises ToolPolicyBlocked."""

    def test_block_raises_exception(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.BLOCK,
            law_slots=("deny-1",),
            rationale="Blocked by security policy",
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        with pytest.raises(ToolPolicyBlocked, match="Blocked by security policy"):
            server.execute_tool("test_tool", {"x": 1}, capability_token=_TEST_TOKEN)

    def test_block_tool_not_executed(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.BLOCK,
            rationale="denied",
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        try:
            server.execute_tool("test_tool", {}, capability_token=_TEST_TOKEN)
        except ToolPolicyBlocked:
            pass
        assert len(server._test_call_log) == 0  # type: ignore[attr-defined]

    def test_block_emits_artifact(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.BLOCK,
            law_slots=("sec-99",),
            rationale="blocked",
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        emitted = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append(artifact)

        with patch(
            "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
            mock_emit,
        ):
            with pytest.raises(ToolPolicyBlocked):
                server.execute_tool("test_tool", {"a": 1}, capability_token=_TEST_TOKEN)

        assert len(emitted) == 1
        assert emitted[0].outcome == LawSlotOutcome.BLOCK
        assert emitted[0].applied_law_slots == ("sec-99",)

    def test_block_preserves_rationale_in_exception(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.BLOCK,
            rationale="Rate limit exceeded for tool",
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        with pytest.raises(ToolPolicyBlocked) as exc_info:
            server.execute_tool("test_tool", {}, capability_token=_TEST_TOKEN)
        assert exc_info.value.rationale == "Rate limit exceeded for tool"
        assert isinstance(exc_info.value.artifact, ToolEnforcementArtifact)


# =========================================================================
# Integration tests — MODIFY path
# =========================================================================


class TestModifyPath:
    """MODIFY path: tool executes with new args; artifact includes both hashes."""

    def test_modify_transforms_args(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.MODIFY,
            law_slots=("sanitize-1",),
            rationale="Input sanitized",
            arg_transform={"safe_mode": True, "max_depth": 3},
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        result = server.execute_tool("test_tool", {"query": "test"}, capability_token=_TEST_TOKEN)
        assert result.success is True
        received = server._test_call_log[0]  # type: ignore[attr-defined]
        assert received["safe_mode"] is True
        assert received["max_depth"] == 3
        assert received["query"] == "test"

    def test_modify_emits_both_hashes(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.MODIFY,
            law_slots=("sanitize-1",),
            rationale="sanitized",
            arg_transform={"extra": "injected"},
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        emitted = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append(artifact)

        with patch(
            "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
            mock_emit,
        ):
            server.execute_tool("test_tool", {"a": 1}, capability_token=_TEST_TOKEN)

        assert len(emitted) == 1
        art = emitted[0]
        assert art.outcome == LawSlotOutcome.MODIFY
        assert art.original_args_hash  # non-empty
        assert art.modified_args_hash  # non-empty
        assert art.original_args_hash != art.modified_args_hash


# =========================================================================
# Determinism tests
# =========================================================================


class TestDeterminism:
    """Same input args -> same hashes; MODIFY produces stable modified_args_hash."""

    def test_stable_args_hash_deterministic(self):
        h1 = _stable_args_hash({"b": 2, "a": 1})
        h2 = _stable_args_hash({"a": 1, "b": 2})
        assert h1 == h2  # sorted keys ensures stability

    def test_stable_args_hash_different_for_different_args(self):
        h1 = _stable_args_hash({"a": 1})
        h2 = _stable_args_hash({"a": 2})
        assert h1 != h2

    def test_modify_hash_stable_across_calls(self):
        enforcer = ToolPolicyEnforcer()
        enforcer.register_rule(
            "test_tool",
            outcome=LawSlotOutcome.MODIFY,
            law_slots=("s1",),
            rationale="mod",
            arg_transform={"injected": True},
        )
        set_tool_policy_enforcer(enforcer)

        server = _make_server_with_tool()
        artifacts = []

        def mock_emit(self_emitter, type_label, artifact):
            artifacts.append(artifact)

        with patch(
            "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
            mock_emit,
        ):
            server.execute_tool("test_tool", {"x": 42}, capability_token=_TEST_TOKEN)
            # Reset enforcer to same rule for second call
            set_tool_policy_enforcer(enforcer)
            server.execute_tool("test_tool", {"x": 42}, capability_token=_TEST_TOKEN)

        assert len(artifacts) == 2
        assert artifacts[0].original_args_hash == artifacts[1].original_args_hash
        assert artifacts[0].modified_args_hash == artifacts[1].modified_args_hash

    def test_pass_hash_stable(self):
        server = _make_server_with_tool()
        artifacts = []

        def mock_emit(self_emitter, type_label, artifact):
            artifacts.append(artifact)

        with patch(
            "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
            mock_emit,
        ):
            server.execute_tool("test_tool", {"key": "value"}, capability_token=_TEST_TOKEN)
            server.execute_tool("test_tool", {"key": "value"}, capability_token=_TEST_TOKEN)

        assert artifacts[0].original_args_hash == artifacts[1].original_args_hash
