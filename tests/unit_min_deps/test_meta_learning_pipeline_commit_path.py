"""Unit tests for system_learning.pipelines.meta_learning_pipeline (commit path)."""

import pytest

from system_learning.pipelines.approval_gates import ApprovalDecision
from system_learning.pipelines.meta_learning_pipeline import (
    PipelineConfig,
    PipelineDependencies,
    PipelineError,
    run_pipeline,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake Dependencies (reuse from proposal_only tests)
# =============================================================================


class FakeAuditStore:
    """In-memory fake audit store."""

    def __init__(self, audit_data: bytes):
        self.audit_data = audit_data

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        return self.audit_data


class FakeTelemetryStore:
    """In-memory fake telemetry store."""

    def __init__(self, events: list[tuple[int, str, bytes]]):
        self.events = events

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        filtered = [
            (ts, kind, payload)
            for ts, kind, payload in self.events
            if window_start_utc <= ts < window_end_utc
        ]
        return tuple(filtered)


class FakeConfigProvider:
    """In-memory fake config provider."""

    def __init__(self):
        self.configs = {"routing": b"routing_config_v1"}

    def get_current_configs(self) -> dict[str, bytes]:
        return self.configs

    def get_last_update_utc(self, surface_name: str) -> int | None:
        return None

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        return ()


class FakeBaselineMetricsProvider:
    """In-memory fake baseline metrics provider."""

    def __init__(self):
        from system_learning.validators.shadow_evaluator import ShadowMetrics

        self.production = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        self.shadow = ShadowMetrics(
            p95_latency_ms=105.0,
            error_rate=0.015,
            safety_violation_count=0,
            cpu_pct=52.0,
            mem_mb=1020.0,
        )

    def production_metrics(self):
        return self.production

    def shadow_metrics(self, pkg):
        return self.shadow


class FakeVersionStore:
    """In-memory fake version store."""

    def __init__(self):
        self.committed_packages = []

    def commit_change_package(self, pkg) -> str:
        self.committed_packages.append(pkg)
        return f"version_{len(self.committed_packages)}"


class FakeActivator:
    """In-memory fake activator."""

    def __init__(self):
        self.activations = []

    def activate(self, component: str, version_id: str) -> None:
        self.activations.append((component, version_id))


class FakeApprovalGate:
    """In-memory fake approval gate."""

    def __init__(self, decision: ApprovalDecision):
        self.decision = decision
        self.decide_calls = []

    def decide(self, pkg, rca, snapshot):
        self.decide_calls.append((pkg, rca, snapshot))
        return self.decision


# =============================================================================
# Tests
# =============================================================================


class TestCommitPath:
    def test_commit_path_requires_version_store(self):
        """proposal_only=False requires version_store."""
        audit_store = FakeAuditStore(b"SyntaxError: test")
        telemetry_store = FakeTelemetryStore([])
        config_provider = FakeConfigProvider()
        approval_gate = FakeApprovalGate(ApprovalDecision.APPROVE)

        cfg = PipelineConfig(
            engine_version="v1",
            config_surface_version="v1",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.05,
                max_cpu_regression_pct=10.0,
                max_mem_regression_pct=10.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=1000),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
            enabled_proposers=(),
            proposal_only=False,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            version_store=None,  # Missing
            approval_gate=approval_gate,
        )

        with pytest.raises(PipelineError, match="version_store required"):
            run_pipeline(
                now_utc=1700003600,
                window_start_utc=1700000000,
                window_end_utc=1700003600,
                cfg=cfg,
                deps=deps,
            )

    def test_commit_path_requires_approval_gate(self):
        """proposal_only=False requires approval_gate."""
        audit_store = FakeAuditStore(b"SyntaxError: test")
        telemetry_store = FakeTelemetryStore([])
        config_provider = FakeConfigProvider()
        version_store = FakeVersionStore()

        cfg = PipelineConfig(
            engine_version="v1",
            config_surface_version="v1",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.05,
                max_cpu_regression_pct=10.0,
                max_mem_regression_pct=10.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=1000),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
            enabled_proposers=(),
            proposal_only=False,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            version_store=version_store,
            approval_gate=None,  # Missing
        )

        with pytest.raises(PipelineError, match="approval_gate required"):
            run_pipeline(
                now_utc=1700003600,
                window_start_utc=1700000000,
                window_end_utc=1700003600,
                cfg=cfg,
                deps=deps,
            )

    def test_approval_reject_does_not_commit(self):
        """Approval REJECT prevents commit and activation."""
        audit_store = FakeAuditStore(b"SyntaxError: test")
        telemetry_store = FakeTelemetryStore([])
        config_provider = FakeConfigProvider()
        version_store = FakeVersionStore()
        activator = FakeActivator()
        approval_gate = FakeApprovalGate(ApprovalDecision.REJECT)

        cfg = PipelineConfig(
            engine_version="v1",
            config_surface_version="v1",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.05,
                max_cpu_regression_pct=10.0,
                max_mem_regression_pct=10.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=1000),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
            enabled_proposers=(),
            proposal_only=False,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            version_store=version_store,
            activator=activator,
            approval_gate=approval_gate,
        )

        run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=cfg,
            deps=deps,
        )

        # Assert: no commits or activations
        assert len(version_store.committed_packages) == 0
        assert len(activator.activations) == 0


class TestDeterminism:
    def test_commit_path_deterministic(self):
        """Commit path produces identical results."""
        audit_store = FakeAuditStore(b"SyntaxError: test")
        telemetry_store = FakeTelemetryStore([])
        config_provider = FakeConfigProvider()
        version_store = FakeVersionStore()
        approval_gate = FakeApprovalGate(ApprovalDecision.APPROVE)

        cfg = PipelineConfig(
            engine_version="v1",
            config_surface_version="v1",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.05,
                max_cpu_regression_pct=10.0,
                max_mem_regression_pct=10.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=1000),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
            enabled_proposers=(),
            proposal_only=False,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            version_store=version_store,
            approval_gate=approval_gate,
        )

        proposals1 = run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=cfg,
            deps=deps,
        )

        proposals2 = run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=cfg,
            deps=deps,
        )

        assert proposals1 == proposals2
