"""CI Sovereignty Attack Suite — Tests to verify system resilience against attacks.

5 attack-class tests to ensure the system maintains sovereignty:
1. Kernel boundary violation attempt
2. Provider health manipulation + degraded mode interlock
3. Priority stack overflow protection
4. Replay key tampering detection
5. Surface isolation bypass prevention
"""

from __future__ import annotations

import time

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    APPS_RG_DIR,
    SYSTEM_LEARNING_DIR,
)
#  # MOVED: from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    ProviderHealthState,
    SovereignLLMGateway,
)
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (
    SOVEREIGN_KERNEL_COMPONENTS,
)
#  # MOVED: from agentic_core.L5_safety.enforcement.priority_violation_guard import (
    OptimizationPriority,
    PriorityViolationGuard,
)
#  # MOVED: from agentic_core.L6_observability.engines.drift_detector import DriftDetector
#  # MOVED: from agentic_core.L6_observability.engines.replay_key_computer import (
    ReplayKeyComponents,
    compute_replay_key,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

# REMOVED: _emit_authorize_and_execute("p2", "test_sovereignty_attack_suite", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_sovereignty_attack_suite", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_sovereignty_attack_suite", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_sovereignty_attack_suite", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_sovereignty_attack_suite", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_sovereignty_attack_suite", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_sovereignty_attack_suite", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_sovereignty_attack_suite", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_sovereignty_attack_suite", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_sovereignty_attack_suite", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_sovereignty_attack_suite", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_sovereignty_attack_suite", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_sovereignty_attack_suite", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_sovereignty_attack_suite", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_sovereignty_attack_suite", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_sovereignty_attack_suite", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_sovereignty_attack_suite", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_sovereignty_attack_suite", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_sovereignty_attack_suite", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_sovereignty_attack_suite", "exec_snapshot_link")
#  # MOVED: from system_learning.engines.surface_isolation_validator import (
    SurfaceIsolationValidator,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_sovereignty_attack_suite")
# REMOVED: _emit_reads_policy_state("p0", "test_sovereignty_attack_suite", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_sovereignty_attack_suite", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_sovereignty_attack_suite", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_sovereignty_attack_suite", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_sovereignty_attack_suite", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_sovereignty_attack_suite", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_sovereignty_attack_suite", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_sovereignty_attack_suite", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_sovereignty_attack_suite", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_sovereignty_attack_suite", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_sovereignty_attack_suite", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_sovereignty_attack_suite", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_sovereignty_attack_suite", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_sovereignty_attack_suite", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_sovereignty_attack_suite", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_sovereignty_attack_suite", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_sovereignty_attack_suite", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_sovereignty_attack_suite", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_sovereignty_attack_suite", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_sovereignty_attack_suite", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_sovereignty_attack_suite", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_sovereignty_attack_suite", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_sovereignty_attack_suite", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_sovereignty_attack_suite", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_sovereignty_attack_suite", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_sovereignty_attack_suite", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_sovereignty_attack_suite", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_sovereignty_attack_suite", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_sovereignty_attack_suite", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_sovereignty_attack_suite", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_sovereignty_attack_suite", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_sovereignty_attack_suite", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_sovereignty_attack_suite", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_sovereignty_attack_suite", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_sovereignty_attack_suite", "write_through")
# REMOVED: _emit_writes_through("p1", "test_sovereignty_attack_suite", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_sovereignty_attack_suite", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_sovereignty_attack_suite", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_sovereignty_attack_suite", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_sovereignty_attack_suite", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_sovereignty_attack_suite", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_sovereignty_attack_suite", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_sovereignty_attack_suite", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_sovereignty_attack_suite", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_sovereignty_attack_suite", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_sovereignty_attack_suite", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_sovereignty_attack_suite", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_sovereignty_attack_suite", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_sovereignty_attack_suite", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_sovereignty_attack_suite", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_sovereignty_attack_suite")
# REMOVED: _emit_gated_by_confidence("p1", "test_sovereignty_attack_suite", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_sovereignty_attack_suite")
# REMOVED: emit_determinism_digest("p0", "test_sovereignty_attack_suite")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.ci


# ---------------------------------------------------------------------------
# Fixtures — ensure clean state per test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_gateway_singleton():
    """Reset SovereignLLMGateway singleton before every test."""
    SovereignLLMGateway.reset_instance()
    yield
    SovereignLLMGateway.reset_instance()


@pytest.fixture()
def fresh_validator():
    """Return a brand-new SurfaceIsolationValidator per test."""
    return SurfaceIsolationValidator()


# ---------------------------------------------------------------------------
# Test 1: Kernel Boundary Violation
# ---------------------------------------------------------------------------


class TestKernelBoundaryViolation:
    """Verify kernel boundary is fully declared and tamper-evident."""

    def test_sovereign_kernel_contains_critical_components(self):
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (
        from agentic_core.L5_safety.enforcement.priority_violation_guard import (
        from agentic_core.L6_observability.engines.drift_detector import DriftDetector
        from agentic_core.L6_observability.engines.replay_key_computer import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.engines.surface_isolation_validator import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """Immutable frozenset must contain every L2/L5 kernel component."""
        assert "agentic_core.L5_safety" in SOVEREIGN_KERNEL_COMPONENTS
        assert "agentic_core.L2_execution" in SOVEREIGN_KERNEL_COMPONENTS
        assert "agentic_core.L0_routing" in SOVEREIGN_KERNEL_COMPONENTS

    def test_sovereign_kernel_excludes_non_kernel_modules(self):
        """Malicious or extension modules must not be in the kernel."""
        assert "malicious.kernel.bypass" not in SOVEREIGN_KERNEL_COMPONENTS
        assert SYSTEM_LEARNING_DIR not in SOVEREIGN_KERNEL_COMPONENTS
        assert APPS_RG_DIR not in SOVEREIGN_KERNEL_COMPONENTS

    def test_sovereign_kernel_is_immutable(self):
        """frozenset cannot be modified at runtime — attack surface is zero."""
        with pytest.raises((AttributeError, TypeError)):
            SOVEREIGN_KERNEL_COMPONENTS.add("malicious.injection")  # type: ignore[attr-defined]

    def test_boundary_checker_stdlib_set_is_finite(self):
    """Test boundary_checker_stdlib_set_is_finite contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"

class TestProviderHealthManipulation:
    """Verify provider health monitoring resists manipulation and enforces degraded mode."""

    def test_initial_health_is_clean(self):
        """Fresh gateway must report all providers healthy with zero error rate."""
        gw = SovereignLLMGateway()
        for provider in ("openai", "anthropic", "google"):
            health = gw.get_provider_health(provider)
            assert health.is_healthy, f"{provider} should start healthy"
            assert health.error_rate == 0.0
            assert health.consecutive_failures == 0

    def test_repeated_failures_trigger_degraded_mode(self):
        """After enough consecutive failures, provider enters degraded mode and is unavailable."""
        gw = SovereignLLMGateway()

        # Drive provider into degraded mode (threshold: 5 failures)
        for _ in range(6):
            gw._update_provider_health("openai", False)

        degraded = gw.get_provider_health("openai")
        assert not degraded.is_healthy
        assert degraded.consecutive_failures >= 5
        assert degraded.error_rate >= 0.5
        assert degraded.degraded_until > 0

        # Provider must be unavailable during degraded window
        assert not gw._is_provider_available("openai")

    def test_degraded_mode_auto_recovery_after_timeout(self):
        """Provider must auto-recover and become available once degraded_until has passed."""
        gw = SovereignLLMGateway()

        for _ in range(6):
            gw._update_provider_health("openai", False)

        assert not gw._is_provider_available("openai")

        # Manually expire the degraded window by setting degraded_until to the past
        health = gw._provider_health["openai"]
        gw._provider_health["openai"] = ProviderHealthState(
            provider="openai",
            is_healthy=False,
            error_rate=health.error_rate,
            last_check=health.last_check,
            degraded_until=int(time.time()) - 1,  # already expired
            consecutive_failures=health.consecutive_failures,
        )

        assert gw._is_provider_available("openai")

    def test_health_state_is_frozen_cannot_be_mutated(self):
        """ProviderHealthState is frozen — direct mutation attempt must raise."""
        gw = SovereignLLMGateway()
        health = gw.get_provider_health("openai")
        with pytest.raises((AttributeError, TypeError)):
            health.error_rate = -1.0  # type: ignore[misc]

    def test_success_resets_consecutive_failures(self):
        """A single success must reset consecutive_failures to 0."""
        gw = SovereignLLMGateway()
        for _ in range(3):
            gw._update_provider_health("anthropic", False)
        assert gw.get_provider_health("anthropic").consecutive_failures == 3

        gw._update_provider_health("anthropic", True)
        assert gw.get_provider_health("anthropic").consecutive_failures == 0


# ---------------------------------------------------------------------------
# Test 3: Priority Stack Overflow
# ---------------------------------------------------------------------------


class TestPriorityStackOverflow:
    """Verify priority stack enforces ordering and records violations."""

    def test_lower_priority_blocked_when_higher_active(self):
        """LOW operation must be denied when HIGH is active."""
        guard = PriorityViolationGuard()
        assert guard.start_operation("high_op", OptimizationPriority.HIGH)

        allowed = guard.start_operation("low_op", OptimizationPriority.LOW)
        assert not allowed

        violations = guard.get_violations()
        assert len(violations) == 1
        assert violations[0]["operation_id"] == "low_op"
        assert "priority" in violations[0]["reason"].lower()
        guard.end_operation("high_op")

    def test_same_priority_allowed_to_stack(self):
        """Multiple operations at the same priority level must all be accepted."""
        guard = PriorityViolationGuard()
        for i in range(5):
            assert guard.start_operation(f"op_{i}", OptimizationPriority.MEDIUM)
        assert guard.get_stack_summary()["stack_depth"] == 5
        for i in range(5):
            guard.end_operation(f"op_{i}")

    def test_end_operation_reduces_stack(self):
        """Ending an operation removes it from the stack."""
        guard = PriorityViolationGuard()
        guard.start_operation("a", OptimizationPriority.HIGH)
        guard.start_operation("b", OptimizationPriority.HIGH)
        assert guard.get_stack_summary()["stack_depth"] == 2

        guard.end_operation("a")
        assert guard.get_stack_summary()["stack_depth"] == 1
        guard.end_operation("b")
        assert guard.get_stack_summary()["stack_depth"] == 0

    def test_duplicate_operation_id_rejected(self):
        """Starting the same operation_id twice must be denied."""
        guard = PriorityViolationGuard()
        assert guard.start_operation("dup", OptimizationPriority.HIGH)
        assert not guard.start_operation("dup", OptimizationPriority.HIGH)
        guard.end_operation("dup")

    def test_emergency_priority_always_allowed(self):
        """EMERGENCY can always start even over CRITICAL."""
        guard = PriorityViolationGuard()
        assert guard.start_operation("critical_op", OptimizationPriority.CRITICAL)
        assert guard.start_operation("emergency_op", OptimizationPriority.EMERGENCY)
        guard.end_operation("critical_op")
        guard.end_operation("emergency_op")


# ---------------------------------------------------------------------------
# Test 4: Replay Key Tampering
# ---------------------------------------------------------------------------


class TestReplayKeyTampering:
    """Verify replay keys are deterministic and tamper-evident."""

    def _make_components(self, tier: str = "LOCAL_AGENT", c0: str = "ctx_hash") -> ReplayKeyComponents:
        return ReplayKeyComponents(
            tier_selection=tier,
            retry_count=0,
            threshold_config={"X": 0.75, "Y": 0.40},
            tool_budget_caps={"ast_rewrite": 10},
            freshness_windows={"config": 3600},
            config_surface_hash="abc123",
            embedding_pack_hash="def456",
            embedding_model_version="v1.0",
            c0_context_hash=c0,
        )

    def test_identical_components_produce_identical_key(self):
        """Same inputs must always produce the same 64-char SHA-256 hex digest."""
        c = self._make_components()
        assert compute_replay_key(c) == compute_replay_key(c)
        assert len(compute_replay_key(c)) == 64

    def test_tier_change_changes_key(self):
        """Changing tier_selection must produce a different replay key."""
        key_local = compute_replay_key(self._make_components(tier="LOCAL_AGENT"))
        key_qwen = compute_replay_key(self._make_components(tier="QWEN_VLLM"))
        assert key_local != key_qwen

    def test_c0_hash_change_changes_key(self):
        """Changing c0_context_hash must produce a different replay key (drift-evident)."""
        key_a = compute_replay_key(self._make_components(c0="context_v1"))
        key_b = compute_replay_key(self._make_components(c0="context_v2"))
        assert key_a != key_b

    def test_drift_detector_first_registration_no_alert(self):
        """First registration of a hash must never produce a drift alert."""
        detector = DriftDetector()
        h = detector.compute_c0_context_hash("initial_context")
        assert not detector.register_context_hash("key_a", h)
        assert not detector.has_drift("key_a")

    def test_drift_detector_same_hash_no_alert(self):
        """Re-registering the identical hash must not produce a drift alert."""
        detector = DriftDetector()
        h = detector.compute_c0_context_hash("stable_context")
        detector.register_context_hash("key_b", h)
        assert not detector.register_context_hash("key_b", h)

    def test_drift_detector_different_hash_raises_alert(self):
        """A changed hash must be flagged as drift with correct old/new hashes."""
        detector = DriftDetector()
        h1 = detector.compute_c0_context_hash("v1")
        h2 = detector.compute_c0_context_hash("v2")
        detector.register_context_hash("key_c", h1)

        drifted = detector.register_context_hash("key_c", h2)
        assert drifted
        alert = detector.get_drift_alert("key_c")
        assert alert is not None
        assert alert[0] == h1
        assert alert[1] == h2


# ---------------------------------------------------------------------------
# Test 5: Surface Isolation Bypass Prevention
# ---------------------------------------------------------------------------


class TestSurfaceIsolationBypass:
    """Verify surface isolation cannot be bypassed at any authority level."""

    def test_first_surface_is_allowed(self, fresh_validator):
        """With an empty window, any MEDIUM surface must be allowed."""
        ok, reason = fresh_validator.can_mutate_surface("surface_A", "MEDIUM")
        assert ok
        assert "No active surfaces" in reason

    def test_second_surface_blocked_while_first_active(self, fresh_validator):
        """A second MEDIUM surface must be denied while the first is still active."""
        fresh_validator.can_mutate_surface("surface_A", "MEDIUM")
        ok, reason = fresh_validator.can_mutate_surface("surface_B", "MEDIUM")
        assert not ok
        assert "surface_A is active" in reason

    def test_completed_surface_cannot_be_remutated(self, fresh_validator):
        """A completed surface must be denied even by MEDIUM authority."""
        fresh_validator.can_mutate_surface("surface_A", "MEDIUM")
        fresh_validator.mark_surface_completed("surface_A")
        ok, reason = fresh_validator.can_mutate_surface("surface_A", "MEDIUM")
        assert not ok
        assert "already completed" in reason

    def test_new_surface_allowed_after_completion(self, fresh_validator):
        """After completing surface_A, a new surface_B must be allowed."""
        fresh_validator.can_mutate_surface("surface_A", "MEDIUM")
        fresh_validator.mark_surface_completed("surface_A")
        ok, _ = fresh_validator.can_mutate_surface("surface_B", "MEDIUM")
        assert ok

    def test_high_authority_bypasses_active_surface_constraint(self, fresh_validator):
        """HIGH authority must override the single-active-surface constraint."""
        fresh_validator.can_mutate_surface("surface_A", "MEDIUM")
        # HIGH authority can proceed even though surface_A is active
        ok, reason = fresh_validator.can_mutate_surface("surface_B", "HIGH")
        assert ok
        assert "HIGH authority" in reason

    def test_high_authority_cannot_bypass_completed_surface(self, fresh_validator):
        """HIGH authority must NOT be able to re-mutate a completed surface."""
        fresh_validator.can_mutate_surface("critical", "HIGH")
        fresh_validator.mark_surface_completed("critical")
        ok, reason = fresh_validator.can_mutate_surface("critical", "HIGH")
        assert not ok
        assert "already completed" in reason


# ---------------------------------------------------------------------------
# Integration: all defences active simultaneously
# ---------------------------------------------------------------------------


class TestAttackSuiteIntegration:
    """Smoke-test that all defence mechanisms co-exist without conflict."""

    def test_all_defenses_active(self, fresh_validator):
        # 1. Kernel
        assert "agentic_core.L5_safety" in SOVEREIGN_KERNEL_COMPONENTS
        assert len(SOVEREIGN_KERNEL_COMPONENTS) > 3

        # 2. Provider health
        gw = SovereignLLMGateway()
        assert gw.get_provider_health("openai").is_healthy

        # 3. Priority guard
        guard = PriorityViolationGuard()
        assert guard.start_operation("integration_test", OptimizationPriority.MEDIUM)

        # 4. Replay key
        key = compute_replay_key(
            ReplayKeyComponents(
                tier_selection="LOCAL_AGENT",
                retry_count=0,
                threshold_config={},
                tool_budget_caps={},
                freshness_windows={},
                config_surface_hash="x",
                embedding_pack_hash="y",
                embedding_model_version="z",
                c0_context_hash="w",
            )
        )
        assert len(key) == 64

        # 5. Surface isolation
        ok, _ = fresh_validator.can_mutate_surface("integration_surface", "MEDIUM")
        assert ok

        # cleanup
        guard.end_operation("integration_test")
        fresh_validator.mark_surface_completed("integration_surface")
