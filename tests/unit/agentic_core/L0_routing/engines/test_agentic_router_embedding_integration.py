"""Behavioral tests for AgenticRouter embedding integration.

Covers:
- AgenticRouter.__init__ accepts classifier=None (default, backward-compatible)
- AgenticRouter.__init__ accepts an IntentEmbeddingClassifier
- register() calls encode_prototype when classifier is injected
- register() skips encode_prototype when no classifier
- _classify() uses embedding path when classifier has prototypes
- _classify() falls back to keyword path when classifier returns None
- _classify() falls back to keyword path when classifier raises
- _classify() falls back to keyword path when classifier has no prototypes
- Route dispatch returns RoutingDecision with correct target
- fallback triggered when confidence below min_confidence
- min_confidence respected in keyword path
- Determinism: same input → same classification
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_agentic_router_embedding_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_agentic_router_embedding_integration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_agentic_router_embedding_integration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_agentic_router_embedding_integration", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_agentic_router_embedding_integration")
# REMOVED: emit_determinism_digest("p0", "test_agentic_router_embedding_integration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_agentic_router_embedding_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_agentic_router_embedding_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_agentic_router_embedding_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_agentic_router_embedding_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_agentic_router_embedding_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_agentic_router_embedding_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_agentic_router_embedding_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_agentic_router_embedding_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_agentic_router_embedding_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_agentic_router_embedding_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_agentic_router_embedding_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_agentic_router_embedding_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_agentic_router_embedding_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_agentic_router_embedding_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_agentic_router_embedding_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_agentic_router_embedding_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_agentic_router_embedding_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_agentic_router_embedding_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_agentic_router_embedding_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_agentic_router_embedding_integration", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.engines.agentic_router import AgenticRouter, RoutingDecision
from agentic_core.L0_routing.engines.intent_embedding_classifier import IntentEmbeddingClassifier
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_agentic_router_embedding_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_agentic_router_embedding_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_agentic_router_embedding_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_agentic_router_embedding_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_agentic_router_embedding_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_agentic_router_embedding_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_agentic_router_embedding_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_agentic_router_embedding_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_agentic_router_embedding_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_agentic_router_embedding_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_agentic_router_embedding_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_agentic_router_embedding_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_agentic_router_embedding_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_agentic_router_embedding_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_agentic_router_embedding_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_agentic_router_embedding_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_agentic_router_embedding_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_agentic_router_embedding_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_agentic_router_embedding_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_agentic_router_embedding_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_agentic_router_embedding_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_agentic_router_embedding_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_agentic_router_embedding_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_agentic_router_embedding_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_agentic_router_embedding_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_agentic_router_embedding_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_agentic_router_embedding_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_agentic_router_embedding_integration", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_agentic_router_embedding_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_agentic_router_embedding_integration", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_agentic_router_embedding_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_agentic_router_embedding_integration", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_agentic_router_embedding_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_agentic_router_embedding_integration", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_agentic_router_embedding_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_agentic_router_embedding_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_agentic_router_embedding_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_agentic_router_embedding_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_agentic_router_embedding_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_agentic_router_embedding_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_agentic_router_embedding_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_agentic_router_embedding_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_agentic_router_embedding_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_agentic_router_embedding_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_agentic_router_embedding_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_agentic_router_embedding_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_agentic_router_embedding_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_agentic_router_embedding_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_agentic_router_embedding_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_agentic_router_embedding_integration", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _handler(inp: str, ctx: dict) -> str:
    return f"result:{inp[:8]}"


async def _fallback(inp: str, ctx: dict) -> str:
    return "fallback"


def _unit_vec(dim: int, idx: int) -> list[float]:
    v = [0.0] * dim
    v[idx] = 1.0
    return v


class _StubEmbedder:
    """Orthogonal unit vector embedder for deterministic cosine tests."""

    def __init__(self, mapping: dict[str, list[float]]) -> None:
        self._map = mapping

    def embed(self, text: str) -> Any:
        vec = self._map.get(text, [0.5, 0.5, 0.0, 0.0])
        result = MagicMock()
        result.vector = vec
        return result


def _make_classifier(mapping: dict[str, list[float]]) -> IntentEmbeddingClassifier:
    stub = _StubEmbedder(mapping)
    return IntentEmbeddingClassifier(embedder=stub)


_MAPPING = {
    "resume": _unit_vec(4, 0),
    "cv": _unit_vec(4, 0),
    "career": _unit_vec(4, 0),
    "code": _unit_vec(4, 1),
    "review": _unit_vec(4, 1),
    "python": _unit_vec(4, 1),
    "query resume": _unit_vec(4, 0),
    "query code": _unit_vec(4, 1),
}


# ---------------------------------------------------------------------------
# __init__ backward compatibility
# ---------------------------------------------------------------------------


class TestAgenticRouterInit:
    def test_no_classifier_by_default(self):
        router = AgenticRouter()
        assert router._classifier is None

    def test_accepts_none_classifier_explicitly(self):
        router = AgenticRouter(classifier=None)
        assert router._classifier is None

    def test_accepts_classifier_instance(self):
        clf = _make_classifier(_MAPPING)
        router = AgenticRouter(classifier=clf)
        assert router._classifier is clf

    def test_min_confidence_default(self):
        router = AgenticRouter()
        assert router.min_confidence == 0.2

    def test_min_confidence_custom(self):
        router = AgenticRouter(min_confidence=0.5)
        assert router.min_confidence == 0.5


# ---------------------------------------------------------------------------
# register() prototype encoding
# ---------------------------------------------------------------------------


class TestRegisterWithClassifier:
    def test_register_calls_encode_prototype(self):
        clf = MagicMock(spec=IntentEmbeddingClassifier)
        clf.prototype_count.return_value = 1
        router = AgenticRouter(classifier=clf)
        router.register(
            "resume_writer", _handler, intent_keywords=["resume", "cv"], description="writes resumes"
        )
        clf.encode_prototype.assert_called_once()
        call_args = clf.encode_prototype.call_args
        assert call_args[0][0] == "resume_writer"
        texts = call_args[0][1]
        assert "resume" in texts
        assert "cv" in texts
        assert "writes resumes" in texts

    def test_register_without_classifier_does_not_raise(self):
        router = AgenticRouter(classifier=None)
        try:
            router.register("resume_writer", _handler, intent_keywords=["resume"])
        except Exception as exc:
            pytest.fail(f"register() raised unexpectedly: {exc}")

    def test_register_empty_keywords_skips_encode(self):
        clf = MagicMock(spec=IntentEmbeddingClassifier)
        clf.prototype_count.return_value = 0
        router = AgenticRouter(classifier=clf)
        router.register("target", _handler, intent_keywords=[], description="")
        clf.encode_prototype.assert_not_called()


# ---------------------------------------------------------------------------
# _classify() embedding path
# ---------------------------------------------------------------------------


class TestClassifyEmbeddingPath:
    def setup_method(self):
        self.clf = _make_classifier(_MAPPING)
        self.router = AgenticRouter(classifier=self.clf)
        self.router.register("resume_writer", _handler, intent_keywords=["resume", "cv", "career"])
        self.router.register("code_reviewer", _handler, intent_keywords=["code", "review", "python"])

    def test_embedding_path_used_when_classifier_has_prototypes(self):
        intent, target, conf = self.router._classify("query resume")
        assert target == "resume_writer"
        assert 0.0 <= conf <= 1.0

    def test_embedding_path_selects_code_reviewer(self):
        intent, target, conf = self.router._classify("query code")
        assert target == "code_reviewer"

    def test_embedding_intent_equals_target_name(self):
        intent, target, conf = self.router._classify("query resume")
        assert intent == target

    def test_embedding_result_deterministic(self):
        r1 = self.router._classify("query resume")
        r2 = self.router._classify("query resume")
        assert r1 == r2


# ---------------------------------------------------------------------------
# _classify() fallback to keyword path
# ---------------------------------------------------------------------------


class TestClassifyFallbackToKeyword:
    def test_fallback_when_classifier_is_none(self):
        router = AgenticRouter(classifier=None)
        router.register("resume_writer", _handler, intent_keywords=["resume", "cv"])
        router.register("code_reviewer", _handler, intent_keywords=["code", "review"])
        _, target, conf = router._classify("write my resume cv")
        assert target == "resume_writer"

    def test_fallback_when_classifier_returns_none(self):
        clf = MagicMock(spec=IntentEmbeddingClassifier)
        clf.prototype_count.return_value = 2
        clf.classify.return_value = None
        router = AgenticRouter(classifier=clf)
        router.register("resume_writer", _handler, intent_keywords=["resume", "cv"])
        _, target, conf = router._classify("write my resume")
        assert target == "resume_writer"
        assert conf > 0.0

    def test_fallback_when_classifier_raises(self):
        clf = MagicMock(spec=IntentEmbeddingClassifier)
        clf.prototype_count.return_value = 2
        clf.classify.side_effect = RuntimeError("simulated failure")
        router = AgenticRouter(classifier=clf)
        router.register("resume_writer", _handler, intent_keywords=["resume"])
        # Must not raise — must fall back silently
        try:
            intent, target, conf = router._classify("my resume")
        except Exception as exc:
            pytest.fail(f"_classify() raised unexpectedly: {exc}")
        assert target == "resume_writer"

    def test_fallback_when_no_prototypes_registered(self):
        clf = _make_classifier(_MAPPING)
        # Don't register anything — prototype_count() = 0
        router = AgenticRouter(classifier=clf)
        router.register("resume_writer", _handler, intent_keywords=["resume"])
        # The fresh classifier has 0 prototypes for this router's targets
        # (register was called but clf was brand new above)
        clf_empty = IntentEmbeddingClassifier(embedder=None)
        router2 = AgenticRouter(classifier=clf_empty)
        router2.register("resume_writer", _handler, intent_keywords=["resume"])
        _, target, _ = router2._classify("resume writing")
        # Must fall through to keyword path
        assert target == "resume_writer"

    def test_keyword_path_no_targets_returns_unknown(self):
        router = AgenticRouter(classifier=None)
        intent, target, conf = router._classify("anything")
        assert intent == "unknown"
        assert target == ""
        assert conf == 0.0

    def test_keyword_path_confidence_is_hit_ratio(self):
        router = AgenticRouter(classifier=None)
        router.register("target", _handler, intent_keywords=["resume", "portfolio", "linkedin", "career"])
        # "write resume now" contains "resume" (1/4 = 0.25)
        _, _, conf = router._classify("write resume now")
        assert abs(conf - 0.25) < 1e-6  # 1/4


# ---------------------------------------------------------------------------
# route() dispatch integration
# ---------------------------------------------------------------------------


class TestRouteDispatch:
    def test_route_returns_routing_decision(self):
        router = AgenticRouter()
        router.register("resume_writer", _handler, intent_keywords=["resume"])
        decision = asyncio.get_event_loop().run_until_complete(router.route("write resume", context={}))
        assert isinstance(decision, RoutingDecision)

    def test_route_dispatches_to_correct_target(self):
        router = AgenticRouter(min_confidence=0.1)
        router.register("resume_writer", _handler, intent_keywords=["resume", "cv"])
        router.register("code_reviewer", _handler, intent_keywords=["code", "review"])
        decision = asyncio.get_event_loop().run_until_complete(router.route("write my resume cv", context={}))
        assert decision.target_name == "resume_writer"
        assert decision.error is None

    def test_route_uses_fallback_below_min_confidence(self):
        router = AgenticRouter(min_confidence=0.99, fallback_handler=_fallback)
        router.register("resume_writer", _handler, intent_keywords=["resume"])
        decision = asyncio.get_event_loop().run_until_complete(
            router.route("completely unrelated query xyz", context={})
        )
        assert decision.result == "fallback"

    def test_route_with_embedding_classifier(self):
        clf = _make_classifier(_MAPPING)
        router = AgenticRouter(classifier=clf, min_confidence=0.1)
        router.register("resume_writer", _handler, intent_keywords=["resume", "cv", "career"])
        router.register("code_reviewer", _handler, intent_keywords=["code", "review", "python"])
        decision = asyncio.get_event_loop().run_until_complete(router.route("query code", context={}))
        assert decision.target_name == "code_reviewer"
        assert decision.error is None
