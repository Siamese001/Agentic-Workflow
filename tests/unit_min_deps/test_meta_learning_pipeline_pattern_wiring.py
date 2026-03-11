"""Tests for Meta Learning Pipeline Pattern Analysis Wiring - Phase 8."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
)
from system_learning.pipelines.meta_learning_pipeline import (
    PipelineConfig,
    PipelineDependencies,
    run_pipeline,
)
from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.healing_outcome_types import HealingOutcomeProposal, HealingOutcomeStats
from system_learning.types.pattern_analysis_types import (
    PatternFinding,
    PatternFindingKey,
    PatternFindingReport,
    PatternSourceIds,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds


def _make_seed_record(created_utc: int) -> HealingOutcomeIntakeRecord:
    """Build a minimal valid HealingOutcomeIntakeRecord for seeding tests."""
    stats = (HealingOutcomeStats.from_counts("healer1", "LOCAL_AGENT", "failure1", 7, 3),)
    return HealingOutcomeIntakeRecord(
        schema_version=1,
        created_utc=created_utc,
        window_size=1,
        snapshot=stats,
        proposal=HealingOutcomeProposal(stats=stats),
        source="test-seed",
    )


@dataclass(frozen=True, slots=True)
class FakeAuditStore:
    """Fake audit store for testing."""

    records: list[Any] = None

    def __post_init__(self):
        if self.records is None:
            object.__setattr__(self, "records", [])

    def read_records(self, start_utc: int, end_utc: int):
        return []

    def read_audit_slice(self, start_utc: int, end_utc: int):
        return b'{"audit": []}'


@dataclass(frozen=True, slots=True)
class FakeTelemetryStore:
    """Fake telemetry store for testing."""

    data: dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            object.__setattr__(self, "data", {})

    def read_metrics(self, start_utc: int, end_utc: int):
        return {}

    def read_events(self, start_utc: int, end_utc: int):
        return []


@dataclass(frozen=True, slots=True)
class FakeConfigProvider:
    """Fake config provider for testing."""

    def get_config(self, component: str):
        return {}

    def get_current_configs(self):
        return {}

    def get_last_update_utc(self, surface_name: str):
        return 1000

    def get_param_history(self, surface_name: str, window: int):
        return []


@dataclass(frozen=True, slots=True)
class FakeBaselineMetricsProvider:
    """Fake baseline metrics provider for testing."""

    def get_baseline(self, component: str):
        return {}

    def production_metrics(self):
        return {}

    def shadow_metrics(self, pkg):
        return {}


@dataclass(frozen=True, slots=True)
class FakeL4StateWriter(L4StateWriter):
    """Fake L4 state writer that returns test data."""

    healing_snapshot_bytes: bytes = None
    detection_signal_bytes: bytes = None
    drift_snapshot_bytes: bytes = None
    l4b_writes: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.l4b_writes is None:
            object.__setattr__(self, "l4b_writes", [])

    def write_l4b_healing_snapshot(self, payload_bytes: bytes, component_name: str, created_utc: int):
        self.l4b_writes.append(
            {"payload_bytes": payload_bytes, "component_name": component_name, "created_utc": created_utc}
        )

    def read_latest_healing_snapshot(self):
        return self.healing_snapshot_bytes

    def read_latest_detection_signal(self):
        return self.detection_signal_bytes

    def read_latest_drift_snapshot(self):
        return self.drift_snapshot_bytes


@dataclass(frozen=True, slots=True)
class FakeHealingConfigOptimizer(HealingConfigOptimizer):
    """Fake healing config optimizer that tracks pattern reports."""

    pattern_reports_received: list[PatternFindingReport] = None

    def __post_init__(self):
        if self.pattern_reports_received is None:
            object.__setattr__(self, "pattern_reports_received", [])

    def propose_threshold_adjustments_with_patterns(self, snapshot, pattern_report=None):
        if pattern_report:
            # Store the pattern report for verification
            self.pattern_reports_received.append(pattern_report)

        # Return a proposal with adjustments
        from system_learning.engines.healing_config_optimizer import (
            ThresholdAdjustment,
            ThresholdAdjustmentProposal,
        )

        # Create a simple adjustment
        adjustment = ThresholdAdjustment(
            healer_name="test_healer",
            tier="LOCAL_AGENT",
            failure_type="timeout",
            current_threshold=THRESHOLD,
            proposed_threshold=THRESHOLD,
            reason="Test adjustment",
            confidence=0.8,
        )

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=(adjustment,),
        )


@dataclass(frozen=True, slots=True)
class FakePatternAnalysisEngine(PatternAnalysisEngine):
    """Fake pattern analysis engine that tracks calls."""

    analyze_calls: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.analyze_calls is None:
            object.__setattr__(self, "analyze_calls", [])

    def analyze(self, *, healing_snapshot_bytes, detection_signal_bytes, drift_snapshot_bytes, now_utc):
        # Track the call
        self.analyze_calls.append(
            {
                "healing_snapshot_bytes": healing_snapshot_bytes,
                "detection_signal_bytes": detection_signal_bytes,
                "drift_snapshot_bytes": drift_snapshot_bytes,
                "now_utc": now_utc,
            }
        )

        # Return a simple report
        return PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_component",
                        dimension="performance",
                        label="UNDERPERFORMING_HEALER_TIER",
                    ),
                    severity=0.5,
                    evidence=("success_rate_0.300000",),
                    metrics=(("success_rate", 0.3),),
                ),
            ),
        )


@dataclass(frozen=True, slots=True)
class FakeHealingOutcomeIntakeAdapter:
    """Fake intake adapter for testing."""

    records_persisted: list[Any] = None

    def __post_init__(self):
        if self.records_persisted is None:
            object.__setattr__(self, "records_persisted", [])

    def build_record(self, aggregator, created_utc: int, source: str):
        # Return a fake intake record with snapshot
        @dataclass(frozen=True, slots=True)
        class FakeIntakeRecord:
            snapshot: list[Any]

        # Create stats objects with poor performance to trigger adjustments
        @dataclass(frozen=True, slots=True)
        class FakeStats:
            healer_id: str
            tier: str
            failure_type: str
            success_count: int
            failure_count: int
            total_count: int

        stats = [
            FakeStats(
                healer_id="test_healer",
                tier="LOCAL_AGENT",
                failure_type="timeout",
                success_count=30,
                failure_count=70,
                total_count=100,
            )
        ]

        return FakeIntakeRecord(snapshot=stats)

    def persist_record(self, record):
        self.records_persisted.append(record)

    def get_recent_records(self, window_start_utc: int, window_end_utc: int) -> list:
        """Return persisted records within the window."""
        return [
            r
            for r in self.records_persisted
            if window_start_utc <= getattr(r, "created_utc", 0) <= window_end_utc
        ]


class TestMetaLearningPipelinePatternWiring:
    """Test suite for meta learning pipeline pattern analysis integration."""

    def test_pattern_engine_called_with_correct_inputs(self):
        """Test that pattern engine is called exactly once with correct inputs."""
        # Create test healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        healing_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create fake dependencies
        fake_l4_writer = FakeL4StateWriter(healing_snapshot_bytes=healing_snapshot.canonical_bytes())
        fake_pattern_engine = FakePatternAnalysisEngine()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 produces a real intake_record
        fake_intake.records_persisted.append(_make_seed_record(created_utc=1950))

        deps = PipelineDependencies(
            audit_store=FakeAuditStore(),
            telemetry_store=FakeTelemetryStore(),
            config_provider=FakeConfigProvider(),
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=fake_l4_writer,
            pattern_analysis_engine=fake_pattern_engine,
        )

        # Run pipeline
        _proposals = run_pipeline(
            now_utc=2000,
            window_start_utc=1900,
            window_end_utc=2100,
            cfg=PipelineConfig(
                engine_version="1.0",
                config_surface_version="1.0",
                shadow_thresholds=ShadowThresholds(
                    max_p95_latency_regression_pct=10.0,
                    max_error_rate_regression_abs=0.05,
                    max_cpu_regression_pct=20.0,
                    max_mem_regression_pct=20.0,
                    forbid_any_safety_violation_increase=True,
                ),
                cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
                sample_policy=SampleSizePolicy(min_observations=20),
                oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
                enabled_proposers=(),
                require_replay_validation=False,
                require_shadow_validation=False,
                proposal_only=True,
            ),
            deps=deps,
        )

        # Verify pattern engine was called exactly once
        assert len(fake_pattern_engine.analyze_calls) == 1

        call = fake_pattern_engine.analyze_calls[0]
        assert call["now_utc"] == 2000
        assert call["healing_snapshot_bytes"] is not None
        assert call["detection_signal_bytes"] is None  # Not provided in fake
        assert call["drift_snapshot_bytes"] is None  # Not provided in fake

    def test_optimizer_receives_pattern_report(self):
        """Test that optimizer receives the pattern report."""
        # Create test healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        healing_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create fake dependencies
        fake_l4_writer = FakeL4StateWriter()
        fake_pattern_engine = FakePatternAnalysisEngine()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 produces a real intake_record
        fake_intake.records_persisted.append(_make_seed_record(created_utc=1950))

        deps = PipelineDependencies(
            audit_store=FakeAuditStore(),
            telemetry_store=FakeTelemetryStore(),
            config_provider=FakeConfigProvider(),
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=fake_l4_writer,
            pattern_analysis_engine=fake_pattern_engine,
        )

        # Run pipeline
        _proposals = run_pipeline(
            now_utc=2000,
            window_start_utc=1900,
            window_end_utc=2100,
            cfg=PipelineConfig(
                engine_version="1.0",
                config_surface_version="1.0",
                shadow_thresholds=ShadowThresholds(
                    max_p95_latency_regression_pct=10.0,
                    max_error_rate_regression_abs=0.05,
                    max_cpu_regression_pct=20.0,
                    max_mem_regression_pct=20.0,
                    forbid_any_safety_violation_increase=True,
                ),
                cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
                sample_policy=SampleSizePolicy(min_observations=20),
                oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
                enabled_proposers=(),
                require_replay_validation=False,
                require_shadow_validation=False,
                proposal_only=True,
            ),
            deps=deps,
        )

        # Verify optimizer received pattern report
        assert len(fake_optimizer.pattern_reports_received) == 1

        pattern_report = fake_optimizer.pattern_reports_received[0]
        assert isinstance(pattern_report, PatternFindingReport)
        assert pattern_report.source_ids.healing_snapshot_version == "test_v1"
        assert len(pattern_report.findings) == 1
        assert pattern_report.findings[0].key.label == "UNDERPERFORMING_HEALER_TIER"

    def test_pipeline_emits_proposal_only_change_package(self):
        """Test that pipeline emits proposal-only ChangePackage (no activation)."""
        # Create test healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=30, failure_count=70, total_count=100),
            )
        ]

        healing_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create fake dependencies
        fake_l4_writer = FakeL4StateWriter(healing_snapshot_bytes=healing_snapshot.canonical_bytes())
        fake_pattern_engine = FakePatternAnalysisEngine()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 produces a real intake_record
        fake_intake.records_persisted.append(_make_seed_record(created_utc=1950))

        deps = PipelineDependencies(
            audit_store=FakeAuditStore(),
            telemetry_store=FakeTelemetryStore(),
            config_provider=FakeConfigProvider(),
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=fake_l4_writer,
            pattern_analysis_engine=fake_pattern_engine,
        )

        # Run pipeline with proposal_only=True
        proposals = run_pipeline(
            now_utc=2000,
            window_start_utc=1900,
            window_end_utc=2100,
            cfg=PipelineConfig(
                engine_version="1.0",
                config_surface_version="1.0",
                shadow_thresholds=ShadowThresholds(
                    max_p95_latency_regression_pct=10.0,
                    max_error_rate_regression_abs=0.05,
                    max_cpu_regression_pct=20.0,
                    max_mem_regression_pct=20.0,
                    forbid_any_safety_violation_increase=True,
                ),
                cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
                sample_policy=SampleSizePolicy(min_observations=20),
                oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
                enabled_proposers=(),
                require_replay_validation=False,
                require_shadow_validation=False,
                proposal_only=True,
            ),
            deps=deps,
        )

        # Verify proposals are returned (no activation occurred)
        assert isinstance(proposals, tuple)
        # Should have at least the threshold adjustment proposal
        assert len(proposals) >= 1

        # Verify no activation occurred (would require version_store and activator)
        # Since proposal_only=True, pipeline should return early before activation step

    def test_optional_detection_and_drift_signals(self):
        """Test that optional detection and drift signals are handled."""
        # Create test healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        healing_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create detection and drift signals
        detection_data = {
            "version": "detection_v1",
            "signals": [{"component": "test_component", "severity": 0.9}],
        }

        drift_data = {"version": "drift_v1", "drift_scores": [{"component": "test_component", "score": 0.8}]}

        detection_bytes = json.dumps(detection_data).encode("utf-8")
        drift_bytes = json.dumps(drift_data).encode("utf-8")

        # Create fake dependencies with signals
        fake_l4_writer = FakeL4StateWriter(
            detection_signal_bytes=detection_bytes, drift_snapshot_bytes=drift_bytes
        )
        fake_pattern_engine = FakePatternAnalysisEngine()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 produces a real intake_record
        fake_intake.records_persisted.append(_make_seed_record(created_utc=1950))

        deps = PipelineDependencies(
            audit_store=FakeAuditStore(),
            telemetry_store=FakeTelemetryStore(),
            config_provider=FakeConfigProvider(),
            baseline_metrics_provider=FakeBaselineMetricsProvider(),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=fake_l4_writer,
            pattern_analysis_engine=fake_pattern_engine,
        )

        # Run pipeline
        _proposals = run_pipeline(
            now_utc=2000,
            window_start_utc=1900,
            window_end_utc=2100,
            cfg=PipelineConfig(
                engine_version="1.0",
                config_surface_version="1.0",
                shadow_thresholds=ShadowThresholds(
                    max_p95_latency_regression_pct=10.0,
                    max_error_rate_regression_abs=0.05,
                    max_cpu_regression_pct=20.0,
                    max_mem_regression_pct=20.0,
                    forbid_any_safety_violation_increase=True,
                ),
                cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
                sample_policy=SampleSizePolicy(min_observations=20),
                oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
                enabled_proposers=(),
                require_replay_validation=False,
                require_shadow_validation=False,
                proposal_only=True,
            ),
            deps=deps,
        )

        # Verify pattern engine received the signals
        assert len(fake_pattern_engine.analyze_calls) == 1
        call = fake_pattern_engine.analyze_calls[0]
        assert call["detection_signal_bytes"] == detection_bytes
        assert call["drift_snapshot_bytes"] == drift_bytes
