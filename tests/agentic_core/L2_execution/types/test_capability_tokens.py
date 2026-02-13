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
    issue_capability_token,
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


# ===========================================================================
# 4) Wave 5.0.2 — Explicit Token Propagation Tests
# ===========================================================================


class TestCapabilityPropagation:
    """Wave 5.0.2: explicit capability_token parameter propagation."""

    @staticmethod
    def _server_with_tool(name="calculator"):
        from agentic_core.L2_execution.types.mcp_tool_types import (
            MCPTool,
            MCPToolServer,
        )

        server = MCPToolServer("test-propagation")
        server.register_tool(
            MCPTool(
                name=name,
                description="test tool",
                parameters={},
                handler=lambda **kw: "ok",
            ),
        )
        return server

    def test_explicit_token_reaches_execute_tool(self):
        """Token passed via capability_token= is used for enforcement."""
        server = self._server_with_tool()
        token = _make_token()
        result = server.execute_tool(
            "calculator",
            {},
            capability_token=token,
        )
        assert result.success is True

    def test_no_token_no_enforcer_denies(self):
        """No token and no legacy enforcer => deterministic DENY."""
        server = self._server_with_tool()
        with pytest.raises(PermissionError, match="CAPABILITY_DENIED:NO_TOKEN_PROVIDED"):
            server.execute_tool("calculator", {})

    def test_no_token_emits_deny_artifact(self):
        """The DENY path emits a CapabilityDecisionArtifact with NO_TOKEN_PROVIDED."""
        from agentic_core.L2_execution.types.capability_token_types import (
            build_capability_decision,
        )

        captured = []
        _orig = build_capability_decision

        def _capture(**kwargs):
            artifact = _orig(**kwargs)
            captured.append(artifact)
            return artifact

        import agentic_core.L2_execution.types.mcp_tool_types as _mod

        _mod_ref = _mod.__dict__
        server = self._server_with_tool()

        import agentic_core.L2_execution.types.capability_token_types as _cap_mod

        original_fn = _cap_mod.build_capability_decision
        _cap_mod.build_capability_decision = _capture
        try:
            with pytest.raises(PermissionError, match="NO_TOKEN_PROVIDED"):
                server.execute_tool("calculator", {})
        finally:
            _cap_mod.build_capability_decision = original_fn

        assert len(captured) == 1
        assert captured[0].decision == "DENY"
        assert captured[0].deny_reason == "NO_TOKEN_PROVIDED"
        assert captured[0].capability_trace_id == "NONE"

    def test_explicit_token_deterministic_decision(self):
        """Same token + same call => byte-identical decision artifact JSON."""
        server1 = self._server_with_tool()
        server2 = self._server_with_tool()
        token = _make_token()

        decisions1: list = []
        decisions2: list = []
        _orig_check = CapabilityEnforcer.check

        def _capture_to(target):
            def _wrap(self, **kwargs):
                result = _orig_check(self, **kwargs)
                target.append(result)
                return result

            return _wrap

        CapabilityEnforcer.check = _capture_to(decisions1)
        try:
            server1.execute_tool("calculator", {}, capability_token=token)
        finally:
            CapabilityEnforcer.check = _orig_check

        CapabilityEnforcer.check = _capture_to(decisions2)
        try:
            server2.execute_tool("calculator", {}, capability_token=token)
        finally:
            CapabilityEnforcer.check = _orig_check

        assert len(decisions1) == 1
        assert len(decisions2) == 1
        assert decisions1[0].to_json() == decisions2[0].to_json()

    def test_execute_tool_calls_propagates_token(self):
        """execute_tool_calls passes capability_token through to each call."""
        from agentic_core.L2_execution.types.mcp_tool_types import execute_tool_calls

        server = self._server_with_tool("calc")
        token = _make_token(
            constraints=CapabilityConstraints(
                allowed_paths=("tool/calc",),
                max_tool_calls=10,
            ),
        )

        tool_calls = [
            {"function": {"name": "calc", "arguments": {}}},
            {"function": {"name": "calc", "arguments": {}}},
        ]
        results = execute_tool_calls(
            server,
            tool_calls,
            capability_token=token,
        )
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_legacy_enforcer_still_works(self):
        """set_capability_enforcer path works when capability_token is None."""
        server = self._server_with_tool()
        token = _make_token()
        enforcer = CapabilityEnforcer(token)
        server.set_capability_enforcer(enforcer)

        result = server.execute_tool("calculator", {})
        assert result.success is True
        assert enforcer.call_count == 1


class TestCapabilityNoScatter:
    """Wave 5.0.2: enforcement logic confined to expected files only."""

    def test_enforcer_usage_only_in_expected_files(self):
        """CapabilityEnforcer( construction only in mcp_tool_types + capability_token_types."""
        import subprocess

        result = subprocess.run(
            [
                "python",
                "-c",
                "import pathlib, re; "
                "root = pathlib.Path(r'c:/Git/Agentic-Workflow/agentic_core'); "
                "hits = []; "
                "[hits.append(str(p.relative_to(root))) "
                " for p in root.rglob('*.py') "
                " if 'CapabilityEnforcer(' in p.read_text(encoding='utf-8', errors='ignore')]; "
                "print('\\n'.join(sorted(set(hits))))",
            ],
            capture_output=True,
            text=True,
        )
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        allowed = {
            "L2_execution\\types\\capability_token_types.py",
            "L2_execution\\types\\mcp_tool_types.py",
        }
        actual = set(lines)
        assert actual <= allowed, f"CapabilityEnforcer( found outside expected files: {actual - allowed}"


# ===========================================================================
# 5) Wave 5.0.3 — Issuance Helper + Integration Seam Tests
# ===========================================================================


class TestIssueCapabilityToken:
    """Wave 5.0.3: issue_capability_token helper tests."""

    def test_helper_determinism_identical_inputs(self):
        """Same inputs => byte-identical token JSON."""
        kwargs = {
            "semantic_clock": CLOCK,
            "subject_kind": "agent",
            "subject_id": "StructureHealerAgent",
            "issued_by": "L5_Guardian",
            "permissions": [PERMISSION_CODES["TOOL_READ"], PERMISSION_CODES["FS_READ"]],
            "allowed_paths": ["tool/calculator", "tool/analyze_text"],
            "max_tool_calls": 3,
        }
        t1 = issue_capability_token(**kwargs)
        t2 = issue_capability_token(**kwargs)
        assert t1.to_json() == t2.to_json()
        assert t1.trace_id == t2.trace_id

    def test_helper_determinism_shuffled_inputs(self):
        """Shuffled permissions and paths => identical output JSON."""
        t1 = issue_capability_token(
            semantic_clock=CLOCK,
            subject_kind="agent",
            subject_id="TestAgent",
            issued_by="L5_Guardian",
            permissions=["FS:READ", "TOOL:READ", "GIT:READ"],
            allowed_paths=["tool/z", "tool/a", "tool/m"],
            max_tool_calls=5,
        )
        t2 = issue_capability_token(
            semantic_clock=CLOCK,
            subject_kind="agent",
            subject_id="TestAgent",
            issued_by="L5_Guardian",
            permissions=["TOOL:READ", "GIT:READ", "FS:READ"],
            allowed_paths=["tool/m", "tool/z", "tool/a"],
            max_tool_calls=5,
        )
        assert t1.to_json() == t2.to_json()
        assert t1.trace_id == t2.trace_id

    def test_helper_rejects_unknown_permission(self):
        """Unknown permission code => ValueError with stable message."""
        with pytest.raises(ValueError, match="unknown permission 'BOGUS:PERM'"):
            issue_capability_token(
                semantic_clock=CLOCK,
                subject_kind="agent",
                subject_id="TestAgent",
                issued_by="L5_Guardian",
                permissions=["TOOL:READ", "BOGUS:PERM"],
                allowed_paths=["tool/calc"],
                max_tool_calls=3,
            )

    def test_helper_rejects_permission_key_not_value(self):
        """Permission key (e.g. 'TOOL_READ') is not a valid value => ValueError."""
        with pytest.raises(ValueError, match="unknown permission 'TOOL_READ'"):
            issue_capability_token(
                semantic_clock=CLOCK,
                subject_kind="agent",
                subject_id="TestAgent",
                issued_by="L5_Guardian",
                permissions=["TOOL_READ"],
                allowed_paths=["tool/calc"],
                max_tool_calls=3,
            )

    def test_helper_missing_semantic_clock(self):
        """None semantic_clock => ValueError."""
        with pytest.raises(ValueError, match="semantic_clock is required"):
            issue_capability_token(
                semantic_clock=None,
                subject_kind="agent",
                subject_id="TestAgent",
                issued_by="L5_Guardian",
                permissions=["TOOL:READ"],
                allowed_paths=["tool/calc"],
                max_tool_calls=3,
            )

    def test_e2e_helper_token_allow_decision(self):
        """Helper-minted token passed to execute_tool => ALLOW with matching trace_id."""
        from agentic_core.L2_execution.types.mcp_tool_types import (
            MCPTool,
            MCPToolServer,
        )

        server = MCPToolServer("test-issuance-e2e")
        server.register_tool(
            MCPTool(
                name="calculator",
                description="test tool",
                parameters={},
                handler=lambda **kw: "ok",
            ),
        )
        token = issue_capability_token(
            semantic_clock=CLOCK,
            subject_kind="agent",
            subject_id="StructureHealerAgent",
            issued_by="L5_Guardian",
            permissions=[PERMISSION_CODES["TOOL_READ"]],
            allowed_paths=["tool/calculator"],
            max_tool_calls=5,
        )
        result = server.execute_tool("calculator", {}, capability_token=token)
        assert result.success is True

    def test_e2e_integration_seam(self):
        """execute_tool_with_capability issues token and executes in one call."""
        from agentic_core.L2_execution.types.mcp_tool_types import (
            MCPTool,
            MCPToolServer,
            execute_tool_with_capability,
        )

        server = MCPToolServer("test-seam-e2e")
        server.register_tool(
            MCPTool(
                name="analyzer",
                description="test tool",
                parameters={},
                handler=lambda **kw: "analyzed",
            ),
        )
        result = execute_tool_with_capability(
            server,
            "analyzer",
            {},
            semantic_clock=CLOCK,
            subject_kind="agent",
            subject_id="TestAgent",
            issued_by="L5_Guardian",
            permissions=[PERMISSION_CODES["TOOL_READ"]],
            allowed_paths=["tool/analyzer"],
            max_tool_calls=3,
        )
        assert result.success is True
        assert result.tool_name == "analyzer"
