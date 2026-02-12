"""Wave 2.1 — L3 Route Decision Artifact emission tests.

Tests prove:
1) Positive: routing path emits L3RouteDecisionArtifact with required fields.
2) Negative: bypass path (no candidates) does NOT emit artifact.

These tests WILL FAIL if emission code is removed from delegate_task().
"""

from __future__ import annotations

import sys
import types
from dataclasses import asdict
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L3_orchestration.types.route_decision_artifact_types import (
    L3RouteDecisionArtifact,
    build_l3_route_decision_artifact,
)

# =========================================================================
# Unit tests — artifact construction (no mocking needed)
# =========================================================================


class TestL3RouteDecisionArtifactConstruction:
    """Unit: artifact factory produces valid, serializable artifacts."""

    def test_required_fields_present(self):
        artifact = build_l3_route_decision_artifact(
            trace_id="abc123",
            chosen={
                "agent_class": "AnalysisAgent",
                "method": "analyze",
                "module": "app.agents",
            },
            candidates=[
                {
                    "agent_class": "AnalysisAgent",
                    "method": "analyze",
                    "confidence": 0.95,
                    "docstring": "runs analysis",
                },
                {
                    "agent_class": "FallbackAgent",
                    "method": "run",
                    "confidence": 0.80,
                    "docstring": "fallback path",
                },
            ],
        )
        assert artifact.decision_id  # uuid4, non-empty
        assert artifact.timestamp_utc  # ISO8601 Z, non-empty
        assert artifact.layer == "L3"
        assert artifact.trace_id == "abc123"
        assert artifact.chosen_route.agent_class == "AnalysisAgent"
        assert artifact.chosen_route.agent_name == "analyze"
        assert artifact.chosen_route.module == "app.agents"
        assert len(artifact.candidates) == 2
        assert artifact.candidates[0].score == 0.95
        assert artifact.candidates[1].agent_class == "FallbackAgent"
        assert artifact.policy_context.security_level == "standard"
        assert artifact.determinism.model == "deterministic"

    def test_candidates_length_gte_1(self):
        artifact = build_l3_route_decision_artifact(
            trace_id="t1",
            chosen={"agent_class": "X", "method": "y"},
            candidates=[
                {"agent_class": "X", "method": "y", "confidence": 0.9, "docstring": "d"},
            ],
        )
        assert len(artifact.candidates) >= 1

    def test_artifact_is_frozen(self):
        artifact = build_l3_route_decision_artifact(
            trace_id="t2",
            chosen={"agent_class": "X", "method": "y"},
            candidates=[
                {"agent_class": "X", "method": "y", "confidence": 0.9, "docstring": "d"},
            ],
        )
        with pytest.raises(AttributeError):
            artifact.layer = "L5"  # type: ignore[misc]

    def test_artifact_serializable_via_asdict(self):
        artifact = build_l3_route_decision_artifact(
            trace_id="ser1",
            chosen={"agent_class": "X", "method": "y"},
            candidates=[
                {"agent_class": "X", "method": "y", "confidence": 0.9, "docstring": "d"},
            ],
        )
        d = asdict(artifact)
        assert isinstance(d, dict)
        assert d["layer"] == "L3"
        assert d["trace_id"] == "ser1"
        assert d["chosen_route"]["agent_class"] == "X"
        assert len(d["candidates"]) >= 1

    def test_rejects_empty_trace_id(self):
        with pytest.raises(ValueError, match="trace_id must be non-empty"):
            build_l3_route_decision_artifact(
                trace_id="",
                chosen={"agent_class": "X", "method": "y"},
                candidates=[
                    {"agent_class": "X", "method": "y", "confidence": 0.9, "docstring": "d"},
                ],
            )

    def test_rejects_wrong_layer(self):
        with pytest.raises(ValueError, match="layer must be 'L3'"):
            L3RouteDecisionArtifact(
                decision_id="abc",
                timestamp_utc="2026-01-01T00:00:00Z",
                layer="L5",
                trace_id="t",
                chosen_route=MagicMock(),
                candidates=(),
                policy_context=MagicMock(),
                determinism=MagicMock(),
            )


# =========================================================================
# Integration tests — delegate_task emission path
#
# OrchestrationHandshakeAgent has deep import chains (unified/, runtime/).
# We stub missing top-level modules in sys.modules before importing.
# =========================================================================

_STUBS_INSTALLED = False


def _install_module_stubs():
    """Idempotent: stub missing/broken leaf modules so Python never loads their source."""
    global _STUBS_INSTALLED
    if _STUBS_INSTALLED:
        return
    _STUBS_INSTALLED = True

    _stub_cls = type("Stub", (), {"__init__": lambda self, *a, **k: None})

    def _make_stub(name, attrs):
        if name not in sys.modules:
            mod = types.ModuleType(name)
            for k, v in attrs.items():
                setattr(mod, k, v)
            sys.modules[name] = mod

    _make_stub(
        "agentic_core.L3_orchestration.unified",
        {
            "CoreOrchestrationAgent": _stub_cls,
        },
    )
    _make_stub(
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        {
            "CoreOrchestrationAgent": _stub_cls,
        },
    )
    _make_stub(
        "agentic_core.runtime.config.contextual_router_config",
        {
            "RoutingRequest": _stub_cls,
            "get_router": MagicMock(return_value=MagicMock()),
        },
    )


def _import_oha_module():
    """Import OrchestrationHandshakeAgent module with stubs in place."""
    _install_module_stubs()
    import agentic_core.L3_orchestration.reasoning.OrchestrationHandshakeAgent as mod

    return mod


def _make_handshake_agent():
    """Build a minimally-mocked OrchestrationHandshakeAgent for routing tests."""
    oha_mod = _import_oha_module()
    cls = oha_mod.OrchestrationHandshakeAgent
    agent = object.__new__(cls)
    # Write directly to __dict__ to bypass property descriptors from base classes
    agent.__dict__["requesting_agent"] = "test_caller"
    agent.__dict__["redis"] = None
    registry = MagicMock()
    registry.invoke_method = MagicMock(return_value={"ok": True})
    agent.__dict__["registry"] = registry
    return agent, oha_mod


class TestDelegateTaskEmission:
    """Integration: delegate_task emits L3RouteDecisionArtifact on routing path."""

    def test_positive_artifact_present_in_audit(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.cache_routing_decision = MagicMock()
        agent.discover_capable_agents = MagicMock(
            return_value=[
                {
                    "agent_class": "TestAgent",
                    "method": "run",
                    "confidence": 0.95,
                    "docstring": "test agent",
                },
            ],
        )

        with patch.object(oha_mod, "is_v15_enforced", return_value=False):
            result = agent.delegate_task("test routing task")

        assert result["status"] == "success"
        assert "l3_route_decision_artifact" in result
        art = result["l3_route_decision_artifact"]
        assert art["layer"] == "L3"
        assert art["chosen_route"]["agent_class"] == "TestAgent"
        assert len(art["candidates"]) >= 1
        assert art["decision_id"]  # non-empty uuid4
        assert art["timestamp_utc"]  # non-empty

    def test_positive_multiple_candidates(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.cache_routing_decision = MagicMock()
        agent.discover_capable_agents = MagicMock(
            return_value=[
                {
                    "agent_class": "PrimaryAgent",
                    "method": "run",
                    "confidence": 0.99,
                    "docstring": "primary",
                },
                {
                    "agent_class": "SecondaryAgent",
                    "method": "fallback",
                    "confidence": 0.87,
                    "docstring": "secondary",
                },
            ],
        )

        with patch.object(oha_mod, "is_v15_enforced", return_value=False):
            result = agent.delegate_task("multi candidate task")

        art = result["l3_route_decision_artifact"]
        assert len(art["candidates"]) == 2
        assert art["candidates"][0]["agent_class"] == "PrimaryAgent"
        assert art["candidates"][0]["score"] == 0.99
        assert art["candidates"][1]["agent_class"] == "SecondaryAgent"


class TestDelegateTaskBypass:
    """Negative: no routing occurred → no artifact."""

    def test_no_artifact_when_no_candidates(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.discover_capable_agents = MagicMock(return_value=[])

        with patch.object(oha_mod, "is_v15_enforced", return_value=False):
            result = agent.delegate_task("impossible task")

        assert result["status"] == "no_capable_agent"
        assert "l3_route_decision_artifact" not in result

    def test_no_artifact_on_cache_hit(self):
        agent, oha_mod = _make_handshake_agent()
        cached_result = {"status": "success", "delegated_to": "CachedAgent.run"}
        agent.get_cached_routing = MagicMock(return_value=cached_result)

        with patch.object(oha_mod, "is_v15_enforced", return_value=False):
            result = agent.delegate_task("cached task")

        assert result is cached_result
        assert "l3_route_decision_artifact" not in result
