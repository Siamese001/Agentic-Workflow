"""Unit tests for system_learning.pipelines.meta_learning_pipeline (proposal-only mode)."""

import pytest

from system_learning.pipelines.meta_learning_pipeline import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    PipelineConfig,
    PipelineDependencies,
    run_pipeline,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake Dependencies
# =============================================================================


class FakeAuditStore:
    """In-memory fake audit store."""

    def __init__(self, audit_data: bytes):
        self.audit_data = audit_data
        self.read_calls = []

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        self.read_calls.append((window_start_utc, window_end_utc))
        return self.audit_data


class FakeTelemetryStore:
    """In-memory fake telemetry store."""

    def __init__(self, events: list[tuple[int, str, bytes]]):
        self.events = events
        self.read_calls = []

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        self.read_calls.append((window_start_utc, window_end_utc))
        filtered = [
            (ts, kind, payload)
            for ts, kind, payload in self.events
            if window_start_utc <= ts < window_end_utc
        ]
        return tuple(filtered)


class FakeConfigProvider:
    """In-memory fake config provider."""

    def __init__(self):
        self.configs = {
            "routing": b"routing_config_v1",
            "model": b"model_config_v1",
        }
        self.last_updates = {}
        self.histories = {}

    def get_current_configs(self) -> dict[str, bytes]:
        return self.configs

    def get_last_update_utc(self, surface_name: str) -> int | None:
        return self.last_updates.get(surface_name)

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        return self.histories.get(surface_name, ())


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


# =============================================================================
# Tests
# =============================================================================


class TestProposalOnlyMode:
    def test_proposal_only_returns_packages(self):
        """Proposal-only mode returns packages without commit/activate."""
        # Setup
        audit_store = FakeAuditStore(b"SyntaxError: test")
        telemetry_store = FakeTelemetryStore([])
        config_provider = FakeConfigProvider()

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
            enabled_proposers=("L0", "RAG"),
            proposal_only=True,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
        )

        # Execute
        proposals = run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=cfg,
            deps=deps,
        )

        # Assert
        assert isinstance(proposals, tuple)
        # Currently returns empty proposals (engines not implemented)
        assert len(proposals) == 0

    def test_proposal_only_does_not_call_commit(self):
        """Proposal-only mode does NOT call commit."""
        # Setup
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
            enabled_proposers=("L0",),
            proposal_only=True,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            version_store=version_store,  # Provided but should not be called
        )

        # Execute
        run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=cfg,
            deps=deps,
        )

        # Assert: version_store.commit_change_package was NOT called
        assert len(version_store.committed_packages) == 0

    def test_proposal_only_does_not_call_activate(self):
        """Proposal-only mode does NOT call activate."""
        # Setup
        audit_store = FakeAuditStore(b"SyntaxError: test")
        telemetry_store = FakeTelemetryStore([])
        config_provider = FakeConfigProvider()
        activator = FakeActivator()

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
            enabled_proposers=("RAG",),
            proposal_only=True,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            activator=activator,  # Provided but should not be called
        )

        # Execute
        run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=cfg,
            deps=deps,
        )

        # Assert: activator.activate was NOT called
        assert len(activator.activations) == 0

    def test_proposal_only_default_is_true(self):
        """PipelineConfig.proposal_only defaults to True (fail-safe: GAP-007)."""
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
        )

        assert cfg.proposal_only is True


class TestDeterminism:
    def test_pipeline_deterministic(self):
        """Pipeline produces identical results across multiple runs."""
        # Setup
        audit_store = FakeAuditStore(b"SyntaxError: test\nImportError: foo")
        telemetry_store = FakeTelemetryStore([(1700001000, "metric", b"cpu=50")])
        config_provider = FakeConfigProvider()

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
            proposal_only=True,
        )

        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
        )

        # Execute multiple times
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

        # Assert identical results
        assert proposals1 == proposals2
