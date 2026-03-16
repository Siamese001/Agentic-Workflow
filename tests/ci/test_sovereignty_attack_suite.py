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

from agentic_core.L0_routing.config.path_constants import (
    APPS_RG_DIR,
    SYSTEM_LEARNING_DIR,
)
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    ProviderHealthState,
    SovereignLLMGateway,
)
from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (
    SOVEREIGN_KERNEL_COMPONENTS,
)
from agentic_core.L5_safety.enforcement.priority_violation_guard import (
    OptimizationPriority,
    PriorityViolationGuard,
)
from agentic_core.L6_observability.engines.drift_detector import DriftDetector
from agentic_core.L6_observability.engines.replay_key_computer import (
    ReplayKeyComponents,
    compute_replay_key,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.engines.surface_isolation_validator import (
    SurfaceIsolationValidator,
)

_emit_records_execution_trace("p0", "evidence", "test_sovereignty_attack_suite")
_emit_reads_policy_state("p0", "test_sovereignty_attack_suite", "policy_binding")
_emit_snapshots_state("p0", "test_sovereignty_attack_suite", "state_snapshot")
emit_replay_key("p0", "test_sovereignty_attack_suite")
emit_determinism_digest("p0", "test_sovereignty_attack_suite")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        """STANDARD_LIBRARY_MODULES in boundary checker must be a non-empty set."""
        from ops_scripts.ci.check_kernel_extension_boundary import STANDARD_LIBRARY_MODULES

        assert isinstance(STANDARD_LIBRARY_MODULES, (set, frozenset))
        assert len(STANDARD_LIBRARY_MODULES) > 10
        # Kernel modules must NOT appear in stdlib allowlist
        assert "agentic_core.L5_safety" not in STANDARD_LIBRARY_MODULES
        assert "agentic_core.L2_execution" not in STANDARD_LIBRARY_MODULES


# ---------------------------------------------------------------------------
# Test 2: Provider Health Manipulation
# ---------------------------------------------------------------------------


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
