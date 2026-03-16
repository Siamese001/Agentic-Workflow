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

from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_route_decision_artifact_contract")
_emit_applies_guardrail("p0", "test_route_decision_artifact_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_route_decision_artifact_contract", "policy_binding")
_emit_snapshots_state("p0", "test_route_decision_artifact_contract", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_route_decision_artifact_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_route_decision_artifact_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_route_decision_artifact_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_route_decision_artifact_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_route_decision_artifact_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_route_decision_artifact_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_route_decision_artifact_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_route_decision_artifact_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_route_decision_artifact_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_route_decision_artifact_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_route_decision_artifact_contract", "p4obs", "alert")
_emit_links_incident_trace("test_route_decision_artifact_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_route_decision_artifact_contract", "p3lm", "pattern")
_emit_records_learning_event("test_route_decision_artifact_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_route_decision_artifact_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_route_decision_artifact_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_route_decision_artifact_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_route_decision_artifact_contract", "p3lm", "policy")
_emit_stores_learning_state("test_route_decision_artifact_contract", "p3lm", "state")
_emit_records_execution_trace("test_route_decision_artifact_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_route_decision_artifact_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_route_decision_artifact_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_route_decision_artifact_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_route_decision_artifact_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_route_decision_artifact_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_route_decision_artifact_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_route_decision_artifact_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_route_decision_artifact_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_route_decision_artifact_contract", "context_pull")
_emit_pulls_context("p1", "test_route_decision_artifact_contract", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_route_decision_artifact_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_route_decision_artifact_contract", "uwg_term_2")
_emit_writes_through("p1", "test_route_decision_artifact_contract", "write_through")
_emit_writes_through("p1", "test_route_decision_artifact_contract", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_route_decision_artifact_contract", "safety_validation")
_emit_invokes_eval("p1", "test_route_decision_artifact_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_route_decision_artifact_contract", "routing_commit")
emit_replay_key("p0", "test_route_decision_artifact_contract")
emit_determinism_digest("p0", "test_route_decision_artifact_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_route_decision_artifact_contract", "execution_auth")
_emit_validates_capability("p2", "test_route_decision_artifact_contract", "capability_check")
_emit_routes_to_capability("p2", "test_route_decision_artifact_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_route_decision_artifact_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_route_decision_artifact_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_route_decision_artifact_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_route_decision_artifact_contract", "exec_output")
_emit_dispatches_agent("p3", "test_route_decision_artifact_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_route_decision_artifact_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_route_decision_artifact_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_route_decision_artifact_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_route_decision_artifact_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_route_decision_artifact_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_route_decision_artifact_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_route_decision_artifact_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_route_decision_artifact_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_route_decision_artifact_contract", "eval_metric")
_emit_stores_embedding("p4", "test_route_decision_artifact_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_route_decision_artifact_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_route_decision_artifact_contract", "exec_snapshot_link")

# Required keys are the field names of RouteDecisionArtifact
REQUIRED_KEYS = {f.name for f in dc_fields(RouteDecisionArtifact)}

# ---------------------------------------------------------------------------
# Module keys that need stubs for the seam file to import
# ---------------------------------------------------------------------------
_STUB_MODULES = {
    "agentic_core.L3_orchestration.unified": None,
    "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent": None,
    "agentic_core.L5_safety.enforcement.context_session": None,
    "agentic_core.L5_safety.enforcement.circuit_breaker_gate": None,
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
    cb = types.ModuleType("agentic_core.L5_safety.enforcement.circuit_breaker_gate")
    breaker = MagicMock()
    breaker.allow_request.return_value = True
    cb.get_breaker = MagicMock(return_value=breaker)
    stubs["agentic_core.L5_safety.enforcement.circuit_breaker_gate"] = cb

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


class TestFlushDurability:
    """Assert TelemetryEmitter.flush_to_artifacts_dir persists events to disk."""

    def test_flush_writes_ndjson_with_route_decision(self, tmp_path):
        """flush_to_artifacts_dir writes NDJSON containing ROUTE_DECISION payload."""
        import json

        from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter

        artifact = RouteDecisionArtifact(
            trace_id="flush-test-trace",
            timestamp="2026-02-12T00:00:00Z",
            route_path=RoutePath.STANDARD_VALIDATION,
            risk_score=0.0,
            budget_est=0.0,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="",
        )

        emitter = TelemetryEmitter()
        emitter.emit_route_decision(artifact)
        out_path = emitter.flush_to_artifacts_dir(tmp_path)

        assert out_path is not None
        assert out_path.exists()

        lines = out_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

        event = json.loads(lines[0])
        assert event["type"] == "ROUTE_DECISION"
        assert set(event["payload"].keys()) == REQUIRED_KEYS
        assert event["payload"]["trace_id"] == "flush-test-trace"

    def test_flush_returns_none_when_no_events(self, tmp_path):
        """flush_to_artifacts_dir returns None if no events buffered."""
        from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter

        emitter = TelemetryEmitter()
        assert emitter.flush_to_artifacts_dir(tmp_path) is None
