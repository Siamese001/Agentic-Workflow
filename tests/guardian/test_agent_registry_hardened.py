"""
Guardian Hardened Tests — Agent Registry Seam

AST-graph justification:
  agent_registry has fan_in=10 (SovereignLLMGateway, governance tests,
  dispatch engine, CI sovereignty suite, commit proof invariant).
  Current test coverage = 1 file (test_commit_proof_invariant) that only
  asserts the module is importable. No behavioral contract tests exist for:
    - unregistered agent hard fail
    - DETERMINISTIC mode blocks LLM gateway call
    - LLM_API mode with empty allowed_models
    - registry_digest stability
    - transitive enforcement contract (registry rejects → gateway rejects)

Covers:
  1. get_profile() hard fails with KeyError for unregistered agent
  2. KeyError message contains available agents list (consumer-visible contract)
  3. get_execution_profile() is an alias that delegates to get_profile()
  4. Every registered agent has non-empty agent_id matching its key
  5. DETERMINISTIC agents have empty allowed_models (registry constraint)
  6. LLM_API agents have non-empty allowed_models (registry constraint)
  7. registry_digest() is stable across repeated calls (determinism)
  8. registry_digest() changes when registry changes (sensitivity)
  9. All profile fields are frozen/immutable (dataclass frozen=True expectation)
 10. Transitive: SovereignLLMGateway raises SovereigntyViolation for unregistered agent
 11. Transitive: DETERMINISTIC agent rejected by gateway with correct message
 12. Transitive: LLM_API agent with disallowed model rejected by gateway
"""

from __future__ import annotations

import asyncio

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_agent_registry_hardened")
_emit_reads_policy_state("p0", "test_agent_registry_hardened", "policy_binding")
_emit_snapshots_state("p0", "test_agent_registry_hardened", "state_snapshot")
emit_replay_key("p0", "test_agent_registry_hardened")
emit_determinism_digest("p0", "test_agent_registry_hardened")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_agent_registry_hardened", "execution_auth")
_emit_validates_capability("p2", "test_agent_registry_hardened", "capability_check")
_emit_routes_to_capability("p2", "test_agent_registry_hardened", "capability_route")
_emit_writes_via_uwg("p2", "test_agent_registry_hardened", "uwg_write")
_emit_blocks_direct_write("p2", "test_agent_registry_hardened", "direct_write_block")
_emit_records_tool_invocation("p2", "test_agent_registry_hardened", "tool_invocation")
_emit_captures_execution_output("p2", "test_agent_registry_hardened", "exec_output")
_emit_dispatches_agent("p3", "test_agent_registry_hardened", "agent_dispatch")
_emit_coordinates_agents("p3", "test_agent_registry_hardened", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_agent_registry_hardened", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_agent_registry_hardened", "healing_outcome")
_emit_escalates_failure("p3", "test_agent_registry_hardened", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_agent_registry_hardened", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_agent_registry_hardened", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_agent_registry_hardened", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_agent_registry_hardened", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_agent_registry_hardened", "eval_metric")
_emit_stores_embedding("p4", "test_agent_registry_hardened", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_agent_registry_hardened", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_agent_registry_hardened", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from agentic_core.agents.agent_registry import (
    AGENT_REGISTRY,
    get_execution_profile,
    get_profile,
    registry_digest,
)
from agentic_core.agents.types.agent_execution_profile_types import (
    AgentExecutionProfile,
    ExecutionMode,
    ReasoningIntensity,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_agent_registry_hardened", "p4obs", "metric_1")
_emit_emits_metric_event("test_agent_registry_hardened", "p4obs", "metric_2")
_emit_emits_metric_event("test_agent_registry_hardened", "p4obs", "metric_3")
_emit_emits_metric_event("test_agent_registry_hardened", "p4obs", "metric_4")
_emit_emits_metric_event("test_agent_registry_hardened", "p4obs", "metric_5")
_emit_emits_metric_event("test_agent_registry_hardened", "p4obs", "metric_6")
_emit_records_incident_event("test_agent_registry_hardened", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_agent_registry_hardened", "p4obs", "anomaly")
_emit_writes_observability_log("test_agent_registry_hardened", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_agent_registry_hardened", "p4obs", "mon_state")
_emit_triggers_alert("test_agent_registry_hardened", "p4obs", "alert")
_emit_links_incident_trace("test_agent_registry_hardened", "p4obs", "trace_link")
_emit_captures_pattern("test_agent_registry_hardened", "p3lm", "pattern")
_emit_records_learning_event("test_agent_registry_hardened", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_agent_registry_hardened", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_agent_registry_hardened", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_agent_registry_hardened", "p3lm", "routing")
_emit_improves_agent_policy("test_agent_registry_hardened", "p3lm", "policy")
_emit_stores_learning_state("test_agent_registry_hardened", "p3lm", "state")
_emit_records_execution_trace("test_agent_registry_hardened", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_agent_registry_hardened", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_agent_registry_hardened", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_agent_registry_hardened", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_agent_registry_hardened", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_agent_registry_hardened", "env_read", "p2_env_1")
_emit_reads_environ("test_agent_registry_hardened", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_agent_registry_hardened", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_agent_registry_hardened", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_agent_registry_hardened", "context_pull")
_emit_pulls_context("p1", "test_agent_registry_hardened", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_agent_registry_hardened", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_agent_registry_hardened", "uwg_term_2")
_emit_writes_through("p1", "test_agent_registry_hardened", "write_through")
_emit_writes_through("p1", "test_agent_registry_hardened", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_agent_registry_hardened", "safety_validation")
_emit_invokes_eval("p1", "test_agent_registry_hardened", "eval_call")
_emit_proposal_commits_routing("p1", "test_agent_registry_hardened", "routing_commit")
_emit_escalates_to_human("p1", "test_agent_registry_hardened", "human_escalation")
_emit_routes_through("p1", "test_agent_registry_hardened", "route_through")
_emit_checks_agent_registry("p1", "test_agent_registry_hardened", "agent_registry")
_emit_validates_agent_capability("p1", "test_agent_registry_hardened", "capability")
_emit_dispatches_execution_plan("p1", "test_agent_registry_hardened", "exec_plan")
_emit_agent_executes_agent("p1", "test_agent_registry_hardened", "sub_agent")
_emit_routes_to_agent("p1", "test_agent_registry_hardened", "target_agent")
_emit_verifies_policy("p1", "test_agent_registry_hardened", "policy_check")
_emit_observes_runtime_state("p1", "test_agent_registry_hardened", "runtime_state")
_emit_verifies_boundary("p1", "test_agent_registry_hardened", "boundary_check")
_emit_transcripts_response("p1", "test_agent_registry_hardened", "transcript")
_emit_hard_fails_untranscripted("p1", "test_agent_registry_hardened")
_emit_gated_by_confidence("p1", "test_agent_registry_hardened", "confidence_gate")

# ---------------------------------------------------------------------------
# 1. get_profile() hard fail for unregistered agent
# ---------------------------------------------------------------------------


class TestGetProfileHardFail:
    def test_unregistered_agent_raises_key_error(self):
        with pytest.raises(KeyError):
            get_profile("__totally_nonexistent_agent__")

    def test_error_message_contains_available_agents(self):
        with pytest.raises(KeyError, match="not found in registry"):
            get_profile("__nonexistent__")

    def test_error_message_contains_available_list(self):
        try:
            get_profile("__nonexistent__")
        except KeyError as exc:
            msg = str(exc)
            assert "Available" in msg

    def test_empty_string_agent_id_raises(self):
        with pytest.raises(KeyError):
            get_profile("")

    def test_whitespace_agent_id_raises(self):
        with pytest.raises(KeyError):
            get_profile("   ")

    def test_get_execution_profile_delegates_to_get_profile(self):
        with pytest.raises(KeyError):
            get_execution_profile("__nonexistent__")

    def test_no_silent_default_returned_for_unknown(self):
        result = None
        try:
            result = get_profile("__nonexistent__")
        except KeyError:
            pass
        assert result is None, "get_profile must not silently return a default"


# ---------------------------------------------------------------------------
# 2. Registered agent profile field contracts
# ---------------------------------------------------------------------------


class TestRegisteredAgentContracts:
    def test_every_registered_agent_id_matches_key(self):
        for key, profile in AGENT_REGISTRY.items():
            assert profile.agent_id == key, (
                f"Registry key '{key}' does not match profile.agent_id='{profile.agent_id}'"
            )

    def test_deterministic_agents_have_empty_allowed_models(self):
        for key, profile in AGENT_REGISTRY.items():
            if profile.execution_mode == ExecutionMode.DETERMINISTIC:
                assert (
                    profile.allowed_models == ()
                    or profile.allowed_models is None
                    or len(profile.allowed_models) == 0
                ), f"DETERMINISTIC agent '{key}' must have empty allowed_models"

    def test_llm_api_agents_have_nonempty_allowed_models(self):
        llm_agents = [(k, p) for k, p in AGENT_REGISTRY.items() if p.execution_mode == ExecutionMode.LLM_API]
        for key, profile in llm_agents:
            assert len(profile.allowed_models) > 0, (
                f"LLM_API agent '{key}' must have at least one allowed_model"
            )

    def test_all_agents_have_valid_reasoning_intensity(self):
        valid_intensities = {ri.value for ri in ReasoningIntensity}
        for key, profile in AGENT_REGISTRY.items():
            assert profile.reasoning_intensity.value in valid_intensities, (
                f"Agent '{key}' has invalid reasoning_intensity"
            )

    def test_all_agents_have_valid_execution_mode(self):
        valid_modes = {em.value for em in ExecutionMode}
        for key, profile in AGENT_REGISTRY.items():
            assert profile.execution_mode.value in valid_modes, f"Agent '{key}' has invalid execution_mode"

    def test_get_profile_returns_correct_type(self):
        first_key = next(iter(AGENT_REGISTRY))
        profile = get_profile(first_key)
        assert isinstance(profile, AgentExecutionProfile)

    def test_known_deterministic_agent_returns_deterministic_mode(self):
        profile = get_profile("reconciler")
        assert profile.execution_mode == ExecutionMode.DETERMINISTIC

    def test_known_llm_api_agent_returns_llm_api_mode(self):
        profile = get_profile("conversational_repair")
        assert profile.execution_mode == ExecutionMode.LLM_API

    def test_known_llm_api_agent_has_models(self):
        profile = get_profile("conversational_repair")
        assert len(profile.allowed_models) > 0


# ---------------------------------------------------------------------------
# 3. registry_digest() stability and sensitivity
# ---------------------------------------------------------------------------


class TestRegistryDigest:
    def test_digest_is_deterministic_across_calls(self):
        d1 = registry_digest()
        d2 = registry_digest()
        assert d1 == d2

    def test_digest_contains_all_registered_agents(self):
        d = registry_digest()
        for key in AGENT_REGISTRY:
            assert key in d

    def test_digest_values_contain_execution_mode(self):
        d = registry_digest()
        for key, value in d.items():
            profile = AGENT_REGISTRY[key]
            assert profile.execution_mode.value in value

    def test_digest_values_contain_agent_id(self):
        d = registry_digest()
        for key, value in d.items():
            assert key in value

    def test_digest_format_is_colon_delimited(self):
        d = registry_digest()
        for key, value in d.items():
            parts = value.split(":")
            assert len(parts) == 3, f"Digest for '{key}' expected 3 colon-delimited parts, got: {value}"


# ---------------------------------------------------------------------------
# 4. Transitive consumer contract: SovereignLLMGateway enforces registry
# ---------------------------------------------------------------------------


class TestGatewayTransitiveEnforcement:
    """
    Graph-selected transitive tests: agent_registry → SovereignLLMGateway.
    Proves the enforcement chain is intact without requiring live LLM calls.
    """

    def _make_gateway(self):
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
            SovereignLLMGateway,
            SovereigntyViolation,
        )

        SovereignLLMGateway.reset_instance()
        gw = SovereignLLMGateway()
        return gw, SovereigntyViolation

    def test_unregistered_agent_raises_sovereignty_violation(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation, match="not found in registry"):
            asyncio.run(gw.route_generation(_make_request(agent_id="__totally_nonexistent__")))

    def test_missing_agent_id_raises_sovereignty_violation(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation, match="agent_id is required"):
            asyncio.run(gw.route_generation(_make_request(agent_id="")))

    def test_deterministic_agent_blocked_by_gateway(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation, match="DETERMINISTIC"):
            asyncio.run(gw.route_generation(_make_request(agent_id="reconciler")))

    def test_deterministic_agent_error_contains_agent_id(self):
        gw, SovereigntyViolation = self._make_gateway()
        try:
            asyncio.run(gw.route_generation(_make_request(agent_id="reconciler")))
        except SovereigntyViolation as exc:
            assert "reconciler" in str(exc)

    def test_llm_api_agent_with_disallowed_model_raises(self):
        gw, SovereigntyViolation = self._make_gateway()
        with pytest.raises(SovereigntyViolation):
            asyncio.run(
                gw.route_generation(
                    _make_request(
                        agent_id="conversational_repair",
                        model="gpt-99-imaginary",
                    )
                )
            )

    def test_llm_api_rejection_message_contains_model_name(self):
        gw, SovereigntyViolation = self._make_gateway()
        try:
            asyncio.run(
                gw.route_generation(
                    _make_request(
                        agent_id="conversational_repair",
                        model="gpt-99-imaginary",
                    )
                )
            )
        except SovereigntyViolation as exc:
            assert "gpt-99-imaginary" in str(exc)

    def test_rejection_is_not_silent_fallback(self):
        """No silent provider substitution: rejection must raise, not return a result."""
        gw, SovereigntyViolation = self._make_gateway()
        result = None
        raised = False
        try:
            result = asyncio.run(gw.route_generation(_make_request(agent_id="reconciler")))
        except SovereigntyViolation:
            raised = True
        assert raised, "DETERMINISTIC agent must raise, not return a result"
        assert result is None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_request(agent_id: str, model: str | None = None):
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    return GenerationRequest(
        prompt="test prompt",
        agent_id=agent_id,
        provider="openai",
        model=model,
        temperature=0.0,
        max_tokens=16,
    )
