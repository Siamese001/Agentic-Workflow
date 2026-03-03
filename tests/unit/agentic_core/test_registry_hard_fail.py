"""Tests for L0 agent registry hard-fail gate.

Phase 2: Agent Registry L0 Hard-Fail Gate.
Spec: L0 Authority Node, AGENT EXECUTION PROFILE ENFORCEMENT, Guarantee #7.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.agents.agent_registry import assert_registered
from agentic_core.L0_routing.enforcement.execution_gateway import UnregisteredAgentError


class TestAssertRegistered:
    def test_known_agent_returns_profile(self):
        profile = assert_registered("SovereignLLMGateway")
        assert profile.agent_id == "SovereignLLMGateway"

    def test_empty_string_raises(self):
        with pytest.raises(UnregisteredAgentError, match="non-empty string"):
            assert_registered("")

    def test_whitespace_only_raises(self):
        with pytest.raises(UnregisteredAgentError, match="non-empty string"):
            assert_registered("   ")

    def test_unknown_agent_raises(self):
        with pytest.raises(UnregisteredAgentError, match="not registered"):
            assert_registered("NonExistentAgent_XYZ")

    def test_error_message_lists_available_agents(self):
        with pytest.raises(UnregisteredAgentError, match="Available agents"):
            assert_registered("ghost_agent")


class TestGatewayAgentIdEnforcement:
    """Verify V15ExecutionGateway.execute() hard-fails on empty/unknown agent_id."""

    def _make_manifest(self):
        import hashlib

        from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest

        ast_snippet = "def test(): pass"
        manifest_hash = hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest()
        return SurgicalManifest(
            schema_version="1.0.0",
            correlation_id="test-corr-001",
            node_id="test-node",
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="canonical",
            fix_constraint=FixConstraint.STRICT,
            manifest_hash=manifest_hash,
            change_history=(),
            provenance_chain=(),
        )

    def test_empty_agent_id_raises_before_execution(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = self._make_manifest()

        with pytest.raises(UnregisteredAgentError, match="non-empty string"):
            gw.execute(
                execution_input=manifest,
                heal_fn=lambda m: {},
                state_hash_fn=lambda: ("", "", ""),
                trace_id="t001",
                agent_id="",
            )

    def test_unknown_agent_id_raises_before_execution(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = self._make_manifest()

        with pytest.raises(UnregisteredAgentError, match="not registered"):
            gw.execute(
                execution_input=manifest,
                heal_fn=lambda m: {},
                state_hash_fn=lambda: ("", "", ""),
                trace_id="t002",
                agent_id="UnknownAgent_99",
            )

    def test_known_agent_id_passes_registration_check(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = self._make_manifest()

        # Should NOT raise UnregisteredAgentError — may raise other errors during execution
        # but registration check itself must pass for known agents
        try:
            gw.execute(
                execution_input=manifest,
                heal_fn=lambda m: {},
                state_hash_fn=lambda: ("", "", ""),
                trace_id="t003",
                agent_id="SovereignLLMGateway",
            )
        except UnregisteredAgentError:
            pytest.fail("UnregisteredAgentError raised for a known registered agent")
        except Exception:
            pass  # Other execution errors are expected in unit test context

    def test_gateway_result_has_registry_hash_field(self):
        # Verify GatewayResult dataclass has registry_hash field (Guarantee #7 audit trail)
        import dataclasses

        from agentic_core.L0_routing.enforcement.execution_gateway import GatewayResult

        field_names = {f.name for f in dataclasses.fields(GatewayResult)}
        assert "registry_hash" in field_names
