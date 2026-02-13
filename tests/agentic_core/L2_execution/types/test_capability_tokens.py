"""Wave 5.0.1 — Capability Token & L2 Enforcement Tests.

Contract, enforcement, and determinism tests for capability-based
access control at the single L2 execution boundary.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_maintenance.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import (
    ALL_PERMISSION_VALUES,
    PERMISSION_CODES,
    CapabilityConstraints,
    CapabilityDecisionArtifact,
    CapabilityEnforcer,
    CapabilityTokenArtifact,
    CapabilityTokenSubject,
    build_capability_decision,
    build_capability_token,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLOCK = SemanticClockSnapshot(tick=5, vector_clock={"L2": 3, "L5": 2})
SUBJECT = CapabilityTokenSubject(kind="agent", id="StructureHealerAgent")
CONSTRAINTS = CapabilityConstraints(
    allowed_paths=("tool/calculator", "tool/analyze_text"),
    max_tool_calls=3,
)


def _make_token(**overrides):
    defaults = {
        "semantic_clock": CLOCK,
        "subject": SUBJECT,
        "issued_by": "L5_Guardian",
        "permissions": [PERMISSION_CODES["TOOL_READ"], PERMISSION_CODES["FS_READ"]],
        "constraints": CONSTRAINTS,
    }
    defaults.update(overrides)
    return build_capability_token(**defaults)


# ===========================================================================
# 1) Contract Tests
# ===========================================================================


class TestCapabilityTokenContract:
    """Contract tests for CapabilityTokenArtifact."""

    def test_deterministic_json_byte_equal(self):
        t1 = _make_token()
        t2 = _make_token()
        assert t1.to_json() == t2.to_json()

    def test_missing_semantic_clock_raises_valueerror(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            CapabilityTokenArtifact(
                artifact_type="CAPABILITY_TOKEN",
                semantic_clock=None,
                trace_id="abc",
                subject=SUBJECT,
                issued_by="L5",
                permissions=("TOOL:READ",),
                constraints=CONSTRAINTS,
                policy_config_hash=None,
            )

    def test_permissions_sorted_on_construction(self):
        token = _make_token(permissions=["FS:READ", "TOOL:READ", "GIT:READ"])
        assert token.permissions == ("FS:READ", "GIT:READ", "TOOL:READ")

    def test_allowed_paths_sorted_on_construction(self):
        c = CapabilityConstraints(
            allowed_paths=("tool/z_tool", "tool/a_tool"),
            max_tool_calls=5,
        )
        assert c.allowed_paths == ("tool/a_tool", "tool/z_tool")

    def test_artifact_type_locked(self):
        with pytest.raises(ValueError, match="artifact_type"):
            CapabilityTokenArtifact(
                artifact_type="WRONG",
                semantic_clock=CLOCK,
                trace_id="abc",
                subject=SUBJECT,
                issued_by="L5",
                permissions=("TOOL:READ",),
                constraints=CONSTRAINTS,
                policy_config_hash=None,
            )

    def test_frozen(self):
        token = _make_token()
        with pytest.raises(AttributeError):
            token.issued_by = "hacker"

    def test_trace_id_is_sha256_hex(self):
        token = _make_token()
        assert len(token.trace_id) == 64
        assert all(c in "0123456789abcdef" for c in token.trace_id)

    def test_empty_issued_by_rejected(self):
        with pytest.raises(ValueError, match="issued_by"):
            build_capability_token(
                semantic_clock=CLOCK,
                subject=SUBJECT,
                issued_by="",
                permissions=["TOOL:READ"],
                constraints=CONSTRAINTS,
            )

    def test_permission_codes_complete(self):
        assert len(PERMISSION_CODES) == 8
        assert ALL_PERMISSION_VALUES == frozenset(PERMISSION_CODES.values())

    def test_json_sort_keys(self):
        token = _make_token()
        parsed = json.loads(token.to_json())
        keys = list(parsed.keys())
        assert keys == sorted(keys)

    def test_subject_empty_kind_rejected(self):
        with pytest.raises(ValueError, match="kind"):
            CapabilityTokenSubject(kind="", id="x")

    def test_subject_empty_id_rejected(self):
        with pytest.raises(ValueError, match="id"):
            CapabilityTokenSubject(kind="agent", id="")

    def test_negative_max_tool_calls_rejected(self):
        with pytest.raises(ValueError, match="max_tool_calls"):
            CapabilityConstraints(allowed_paths=(), max_tool_calls=-1)


class TestCapabilityDecisionContract:
    """Contract tests for CapabilityDecisionArtifact."""

    def test_deterministic_json(self):
        d1 = build_capability_decision(
            semantic_clock=CLOCK,
            tool_name="calculator",
            action="execute",
            requested_resource="tool/calculator",
            decision="ALLOW",
            deny_reason=None,
            capability_trace_id="abc123",
        )
        d2 = build_capability_decision(
            semantic_clock=CLOCK,
            tool_name="calculator",
            action="execute",
            requested_resource="tool/calculator",
            decision="ALLOW",
            deny_reason=None,
            capability_trace_id="abc123",
        )
        assert d1.to_json() == d2.to_json()

    def test_missing_semantic_clock_raises(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            CapabilityDecisionArtifact(
                artifact_type="CAPABILITY_DECISION",
                semantic_clock=None,
                trace_id="abc",
                tool_name="calc",
                action="execute",
                requested_resource="tool/calc",
                decision="ALLOW",
                deny_reason=None,
                capability_trace_id="tok",
            )

    def test_invalid_decision_rejected(self):
        with pytest.raises(ValueError, match="decision"):
            CapabilityDecisionArtifact(
                artifact_type="CAPABILITY_DECISION",
                semantic_clock=CLOCK,
                trace_id="abc",
                tool_name="calc",
                action="execute",
                requested_resource="tool/calc",
                decision="MAYBE",
                deny_reason=None,
                capability_trace_id="tok",
            )

    def test_frozen(self):
        d = build_capability_decision(
            semantic_clock=CLOCK,
            tool_name="calc",
            action="execute",
            requested_resource="tool/calc",
            decision="ALLOW",
            deny_reason=None,
            capability_trace_id="tok",
        )
        with pytest.raises(AttributeError):
            d.decision = "DENY"

    def test_trace_id_is_sha256(self):
        d = build_capability_decision(
            semantic_clock=CLOCK,
            tool_name="calc",
            action="execute",
            requested_resource="tool/calc",
            decision="DENY",
            deny_reason="no_perm",
            capability_trace_id="tok",
        )
        assert len(d.trace_id) == 64

    def test_empty_tool_name_rejected(self):
        with pytest.raises(ValueError, match="tool_name"):
            build_capability_decision(
                semantic_clock=CLOCK,
                tool_name="",
                action="execute",
                requested_resource="tool/calc",
                decision="ALLOW",
                deny_reason=None,
                capability_trace_id="tok",
            )


# ===========================================================================
# 2) Enforcement Tests (mock tool execution via MCPToolServer)
# ===========================================================================


class TestCapabilityEnforcement:
    """Enforcement tests via CapabilityEnforcer + MCPToolServer integration."""

    def _make_enforcer(self, **token_overrides):
        token = _make_token(**token_overrides)
        return CapabilityEnforcer(token)

    def test_allowed_permission_proceeds(self):
        enforcer = self._make_enforcer()
        decision = enforcer.check(
            tool_name="calculator",
            action="execute",
            requested_resource="tool/calculator",
            required_permission=PERMISSION_CODES["TOOL_READ"],
            semantic_clock=CLOCK,
        )
        assert decision.decision == "ALLOW"
        assert enforcer.call_count == 1

    def test_missing_permission_denies(self):
        enforcer = self._make_enforcer(permissions=["FS:READ"])
        with pytest.raises(PermissionError, match="CAPABILITY_DENIED"):
            enforcer.check(
                tool_name="calculator",
                action="execute",
                requested_resource="tool/calculator",
                required_permission=PERMISSION_CODES["TOOL_READ"],
                semantic_clock=CLOCK,
            )
        assert enforcer.call_count == 0
        assert len(enforcer.decisions) == 1
        assert enforcer.decisions[0].decision == "DENY"
        assert "MISSING_PERMISSION" in enforcer.decisions[0].deny_reason

    def test_path_outside_allowed_denies(self):
        enforcer = self._make_enforcer()
        with pytest.raises(PermissionError, match="CAPABILITY_DENIED"):
            enforcer.check(
                tool_name="evil_tool",
                action="execute",
                requested_resource="tool/evil_tool",
                required_permission=PERMISSION_CODES["TOOL_READ"],
                semantic_clock=CLOCK,
            )
        assert enforcer.decisions[-1].decision == "DENY"
        assert "PATH_NOT_ALLOWED" in enforcer.decisions[-1].deny_reason

    def test_max_tool_calls_exceeded_denies(self):
        token = _make_token(
            constraints=CapabilityConstraints(
                allowed_paths=("tool/calculator",),
                max_tool_calls=2,
            ),
        )
        enforcer = CapabilityEnforcer(token)

        # First two calls succeed
        for _ in range(2):
            enforcer.check(
                tool_name="calculator",
                action="execute",
                requested_resource="tool/calculator",
                required_permission=PERMISSION_CODES["TOOL_READ"],
                semantic_clock=CLOCK,
            )

        # Third call exceeds max_tool_calls=2
        with pytest.raises(PermissionError, match="CAPABILITY_DENIED"):
            enforcer.check(
                tool_name="calculator",
                action="execute",
                requested_resource="tool/calculator",
                required_permission=PERMISSION_CODES["TOOL_READ"],
                semantic_clock=CLOCK,
            )
        assert enforcer.decisions[-1].decision == "DENY"
        assert "MAX_TOOL_CALLS_EXCEEDED" in enforcer.decisions[-1].deny_reason

    def test_decision_artifact_emitted_on_allow(self):
        enforcer = self._make_enforcer()
        enforcer.check(
            tool_name="calculator",
            action="execute",
            requested_resource="tool/calculator",
            required_permission=PERMISSION_CODES["TOOL_READ"],
            semantic_clock=CLOCK,
        )
        assert len(enforcer.decisions) == 1
        assert isinstance(enforcer.decisions[0], CapabilityDecisionArtifact)
        assert enforcer.decisions[0].decision == "ALLOW"

    def test_decision_artifact_emitted_on_deny(self):
        enforcer = self._make_enforcer(permissions=["FS:READ"])
        with pytest.raises(PermissionError):
            enforcer.check(
                tool_name="calculator",
                action="execute",
                requested_resource="tool/calculator",
                required_permission=PERMISSION_CODES["TOOL_READ"],
                semantic_clock=CLOCK,
            )
        assert len(enforcer.decisions) == 1
        assert isinstance(enforcer.decisions[0], CapabilityDecisionArtifact)
        assert enforcer.decisions[0].decision == "DENY"

    def test_mcp_server_integration_allow(self):
        """MCPToolServer with capability enforcer allows valid tool call."""
        from agentic_core.L2_execution.types.mcp_tool_types import (
            MCPTool,
            MCPToolServer,
        )

        server = MCPToolServer("test-server")
        server.register_tool(
            MCPTool(
                name="calculator",
                description="calc",
                parameters={},
                handler=lambda operation="add", a=1, b=2: a + b,
            ),
        )

        token = _make_token()
        enforcer = CapabilityEnforcer(token)
        server.set_capability_enforcer(enforcer)

        result = server.execute_tool("calculator", {"operation": "add", "a": 1, "b": 2})
        assert result.success is True
        assert enforcer.call_count == 1

    def test_mcp_server_integration_deny(self):
        """MCPToolServer with capability enforcer blocks unauthorized tool."""
        from agentic_core.L2_execution.types.mcp_tool_types import (
            MCPTool,
            MCPToolServer,
        )

        server = MCPToolServer("test-server")
        server.register_tool(
            MCPTool(
                name="evil_tool",
                description="bad",
                parameters={},
                handler=lambda: "should not run",
            ),
        )

        token = _make_token()
        enforcer = CapabilityEnforcer(token)
        server.set_capability_enforcer(enforcer)

        with pytest.raises(PermissionError, match="CAPABILITY_DENIED"):
            server.execute_tool("evil_tool", {})

    def test_empty_allowed_paths_allows_all(self):
        """When allowed_paths is empty, all paths are permitted."""
        token = _make_token(
            constraints=CapabilityConstraints(allowed_paths=(), max_tool_calls=10),
        )
        enforcer = CapabilityEnforcer(token)
        decision = enforcer.check(
            tool_name="anything",
            action="execute",
            requested_resource="tool/anything",
            required_permission=PERMISSION_CODES["TOOL_READ"],
            semantic_clock=CLOCK,
        )
        assert decision.decision == "ALLOW"


# ===========================================================================
# 3) Determinism Tests
# ===========================================================================


class TestCapabilityDeterminism:
    """Determinism: same inputs → identical JSON output."""

    def test_same_token_same_request_identical_decision_json(self):
        enforcer1 = CapabilityEnforcer(_make_token())
        enforcer2 = CapabilityEnforcer(_make_token())

        d1 = enforcer1.check(
            tool_name="calculator",
            action="execute",
            requested_resource="tool/calculator",
            required_permission=PERMISSION_CODES["TOOL_READ"],
            semantic_clock=CLOCK,
        )
        d2 = enforcer2.check(
            tool_name="calculator",
            action="execute",
            requested_resource="tool/calculator",
            required_permission=PERMISSION_CODES["TOOL_READ"],
            semantic_clock=CLOCK,
        )
        assert d1.to_json() == d2.to_json()

    def test_shuffled_permissions_identical_serialized(self):
        t1 = _make_token(permissions=["FS:READ", "TOOL:READ", "GIT:READ"])
        t2 = _make_token(permissions=["TOOL:READ", "GIT:READ", "FS:READ"])
        assert t1.to_json() == t2.to_json()
        assert t1.trace_id == t2.trace_id

    def test_shuffled_allowed_paths_identical_serialized(self):
        c1 = CapabilityConstraints(
            allowed_paths=("tool/z", "tool/a", "tool/m"),
            max_tool_calls=5,
        )
        c2 = CapabilityConstraints(
            allowed_paths=("tool/m", "tool/z", "tool/a"),
            max_tool_calls=5,
        )
        t1 = _make_token(constraints=c1)
        t2 = _make_token(constraints=c2)
        assert t1.to_json() == t2.to_json()
        assert t1.trace_id == t2.trace_id

    def test_token_json_roundtrip_stable(self):
        token = _make_token()
        j1 = token.to_json()
        parsed = json.loads(j1)
        j2 = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        assert j1 == j2
