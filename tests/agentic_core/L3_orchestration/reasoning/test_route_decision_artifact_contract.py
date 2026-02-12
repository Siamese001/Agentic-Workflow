"""
Test RouteDecisionArtifact attachment at L3 routing boundary (Wave 2.1.3R).

Validates that delegate_task() attaches a RouteDecisionArtifact dict to its
return value when V15 is enforced.  The artifact lives in the return dict
only (cache_routing_decision has no implementation); terminology is
"audit return enrichment", not durable emission.
"""

import hashlib
import importlib
import sys
import types
from dataclasses import fields as dc_fields
from enum import Enum
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_maintenance.types.v15_types import (
    RouteDecisionArtifact,
    RoutePath,
)

# Required keys are the field names of RouteDecisionArtifact
REQUIRED_KEYS = {f.name for f in dc_fields(RouteDecisionArtifact)}

# ---------------------------------------------------------------------------
# Module keys that need stubs for the seam file to import
# ---------------------------------------------------------------------------
_STUB_MODULES = {
    "agentic_core.L3_orchestration.unified": None,
    "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent": None,
    "agentic_core.L5_safety.enforcement.context_session": None,
    "agentic_core.L5_safety.enforcement.circuit_breaker": None,
}

# Seam module key (invalidated between tests to pick up fresh patches)
_SEAM_KEY = "agentic_core.L3_orchestration.reasoning.OrchestrationHandshakeAgent"


class _StubRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _build_stubs() -> dict[str, types.ModuleType]:
    """Build fake modules for every missing transitive dependency."""
    stubs: dict[str, types.ModuleType] = {}

    # CoreOrchestrationAgent
    fake_cls = type("CoreOrchestrationAgent", (), {})
    mod = types.ModuleType(
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
    )
    mod.CoreOrchestrationAgent = fake_cls
    stubs["agentic_core.L3_orchestration.unified.CoreOrchestrationAgent"] = mod
    pkg = types.ModuleType("agentic_core.L3_orchestration.unified")
    pkg.CoreOrchestrationAgent = mod
    stubs["agentic_core.L3_orchestration.unified"] = pkg

    # context_session (real file is context_session_manager; import alias missing)
    cs = types.ModuleType("agentic_core.L5_safety.enforcement.context_session")
    cs.RiskLevel = _StubRiskLevel
    cs.ContextSession = MagicMock
    cs.ContextSessionManager = MagicMock
    cs.classify_risk = MagicMock(return_value=_StubRiskLevel.LOW)
    cs.get_session_manager = MagicMock()
    stubs["agentic_core.L5_safety.enforcement.context_session"] = cs

    # circuit_breaker
    cb = types.ModuleType("agentic_core.L5_safety.enforcement.circuit_breaker")
    breaker = MagicMock()
    breaker.allow_request.return_value = True
    cb.get_breaker = MagicMock(return_value=breaker)
    stubs["agentic_core.L5_safety.enforcement.circuit_breaker"] = cb

    return stubs


@pytest.fixture(autouse=True)
def _stub_missing_modules():
    """Inject stubs, yield for test, then restore originals."""
    stubs = _build_stubs()
    saved: dict[str, types.ModuleType | None] = {}
    for key, mod in stubs.items():
        saved[key] = sys.modules.get(key)
        sys.modules[key] = mod

    # Force re-import of the seam module so patches take effect
    sys.modules.pop(_SEAM_KEY, None)
    # Also clear contextual_router_config so it re-imports with stubs
    sys.modules.pop("agentic_core.runtime.config.contextual_router_config", None)

    yield

    # Restore
    for key, prev in saved.items():
        if prev is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = prev
    sys.modules.pop(_SEAM_KEY, None)
    sys.modules.pop("agentic_core.runtime.config.contextual_router_config", None)


def _import_seam():
    """Import the seam module (stubs already injected by fixture)."""
    return importlib.import_module(_SEAM_KEY)


# ---------------------------------------------------------------------------
# Deterministic stub RoutingResult
# ---------------------------------------------------------------------------
def _make_routing_result(decision: RoutePath, risk_value: str = "low"):
    """Return a stub RoutingResult with the given decision."""
    risk_level = MagicMock()
    risk_level.value = risk_value
    result = MagicMock()
    result.decision = decision
    result.risk_level = risk_level
    result.reason = f"stub reason for {decision.value}"
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _build_agent(seam_mod):
    """Construct an OrchestrationHandshakeAgent with mocked internals."""
    cls = seam_mod.OrchestrationHandshakeAgent
    agent = cls.__new__(cls)
    # Set only attributes that delegate_task accesses directly;
    # discover_capable_agents (which uses self.redis) is fully mocked.
    agent.requesting_agent = "test_agent"
    agent.registry = MagicMock()
    # Both cache methods are undefined (no implementation exists);
    # stub them so delegate_task doesn't raise AttributeError.
    agent.get_cached_routing = MagicMock(return_value=None)
    agent.cache_routing_decision = MagicMock()
    return agent


def _stub_discover(agent, agent_class="StubAgent", method="heal", confidence=0.95):
    agent.discover_capable_agents = MagicMock(
        return_value=[
            {"agent_class": agent_class, "method": method, "confidence": confidence},
        ],
    )


def _stub_invoke(agent, return_value="invoke_ok"):
    agent.registry.invoke_method = MagicMock(return_value=return_value)


def _stub_cache(agent):
    agent.cache_routing_decision = MagicMock()
    return agent.cache_routing_decision


# ===========================================================================
# Tests
# ===========================================================================


class TestRouteDecisionArtifactContract:
    """Assert RouteDecisionArtifact is attached to delegate_task return."""

    def test_success_path_contains_artifact_with_all_keys(self):
        """STANDARD_VALIDATION route proceeds; audit return has artifact."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        stub_result = _make_routing_result(RoutePath.STANDARD_VALIDATION, "medium")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
        ):
            out = agent.delegate_task("test task")

        assert out["status"] == "success"
        artifact = out["route_decision_artifact"]
        assert artifact is not None
        assert set(artifact.keys()) == REQUIRED_KEYS

    def test_success_path_route_path_matches(self):
        """route_path in artifact matches the RoutePath from routing result."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        stub_result = _make_routing_result(RoutePath.LOW_RISK_BYPASS, "low")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
        ):
            out = agent.delegate_task("test task low risk")

        artifact = out["route_decision_artifact"]
        assert artifact["route_path"] == RoutePath.LOW_RISK_BYPASS

    def test_blocked_path_human_escalation_has_artifact(self):
        """HUMAN_ESCALATION blocks delegation but still attaches artifact."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        stub_result = _make_routing_result(RoutePath.HUMAN_ESCALATION, "high")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
        ):
            out = agent.delegate_task("test escalation task")

        assert out["status"] == "route_blocked"
        artifact = out["route_decision_artifact"]
        assert artifact is not None
        assert set(artifact.keys()) == REQUIRED_KEYS
        assert artifact["route_path"] == RoutePath.HUMAN_ESCALATION

    def test_blocked_path_budget_overflow_has_artifact(self):
        """ROUTE_RECOVERY_BUDGET_OVERFLOW blocks and attaches artifact."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        stub_result = _make_routing_result(
            RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW,
            "high",
        )
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
        ):
            out = agent.delegate_task("test overflow task")

        assert out["status"] == "route_blocked"
        artifact = out["route_decision_artifact"]
        assert artifact is not None
        assert artifact["route_path"] == RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW

    def test_no_artifact_when_v15_not_enforced(self):
        """Without V15 enforcement, route_decision_artifact is None."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        with patch.object(seam, "is_v15_enforced", return_value=False):
            out = agent.delegate_task("test task no v15")

        assert out["route_decision_artifact"] is None

    def test_trace_id_deterministic(self):
        """trace_id must be the SHA-256 prefix of the Task string."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        task = "deterministic trace test"
        expected_trace = hashlib.sha256(task.encode()).hexdigest()[:16]

        stub_result = _make_routing_result(RoutePath.STANDARD_VALIDATION, "medium")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
        ):
            out = agent.delegate_task(task)

        assert out["route_decision_artifact"]["trace_id"] == expected_trace

    def test_sentinel_fields_are_zero_values(self):
        """Fields not available at L3 seam use documented sentinel values."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)
        _stub_cache(agent)

        stub_result = _make_routing_result(RoutePath.STANDARD_VALIDATION, "medium")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
        ):
            out = agent.delegate_task("sentinel check")

        artifact = out["route_decision_artifact"]
        assert artifact["risk_score"] == 0.0
        assert artifact["budget_est"] == 0.0
        assert artifact["policy_config_hash"] == ""


class TestDurableEmission:
    """Assert TelemetryEmitter.emit_route_decision is called as durable sink."""

    def test_emit_route_decision_called_once_with_all_keys(self):
        """emit_route_decision called exactly once; payload has all artifact keys."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)

        stub_result = _make_routing_result(RoutePath.STANDARD_VALIDATION, "medium")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        captured = []

        def _capture_emit(artifact):
            from dataclasses import asdict

            captured.append(asdict(artifact))

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
            patch.object(
                seam.TelemetryEmitter,
                "emit_route_decision",
                side_effect=_capture_emit,
            ),
        ):
            out = agent.delegate_task("durable emission test")

        assert out["status"] == "success"
        assert len(captured) == 1, f"Expected 1 emission, got {len(captured)}"
        assert set(captured[0].keys()) == REQUIRED_KEYS

    def test_emit_route_decision_called_on_blocked_path(self):
        """Emission fires even when route is blocked (HUMAN_ESCALATION)."""
        seam = _import_seam()
        agent = _build_agent(seam)
        _stub_discover(agent)
        _stub_invoke(agent)

        stub_result = _make_routing_result(RoutePath.HUMAN_ESCALATION, "high")
        fake_router = MagicMock()
        fake_router.route.return_value = stub_result

        captured = []

        def _capture_emit(artifact):
            from dataclasses import asdict

            captured.append(asdict(artifact))

        with (
            patch.object(seam, "is_v15_enforced", return_value=True),
            patch.object(seam, "get_router", return_value=fake_router),
            patch.object(
                seam.TelemetryEmitter,
                "emit_route_decision",
                side_effect=_capture_emit,
            ),
        ):
            out = agent.delegate_task("blocked emission test")

        assert out["status"] == "route_blocked"
        assert len(captured) == 1
        assert captured[0]["route_path"] == RoutePath.HUMAN_ESCALATION
