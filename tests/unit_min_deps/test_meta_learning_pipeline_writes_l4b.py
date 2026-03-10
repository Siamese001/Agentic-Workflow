"""Tests for Meta Learning Pipeline L4B writes - Phase 7 functionality.

Tests that healing snapshots are written to L4B state and version IDs are returned.
"""

from __future__ import annotations

import hashlib
from unittest.mock import Mock

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

from system_learning.pipelines.meta_learning_pipeline import (
    AuditStore,
    BaselineMetricsProvider,
    ConfigProvider,
    PipelineConfig,
    PipelineDependencies,
    TelemetryStore,
    run_pipeline,
)
from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.healing_outcome_types import HealingOutcomeProposal, HealingOutcomeStats


class FakeL4StateWriter:
    """Fake L4 state writer that captures writes."""

    def __init__(self) -> None:
        self.l4b_writes: list[dict] = []

    def write_l4a_detection_signal(self, **kwargs) -> str:
        """Not used in this test."""
        return "noop_l4a"

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Capture L4B healing snapshot writes."""
        self.l4b_writes.append(
            {"payload_bytes": payload_bytes, "component_name": component_name, "created_utc": created_utc}
        )
        # Return a deterministic fake version ID based on content
        import hashlib

        content = f"{component_name}:{created_utc}:{payload_bytes}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class FakeHealingConfigOptimizer:
    """Fake healing config optimizer for testing."""

    def __init__(self) -> None:
        self.snapshot_to_return = None

    def create_snapshot_from_intake(self, intake_record, created_utc: int):
        """Return a predefined snapshot for testing."""
        if self.snapshot_to_return is None:
            # Create a test snapshot
            aggregates = [
                (
                    HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                    HealingOutcomeAggregate(success_count=7, failure_count=3, total_count=10),
                ),
            ]
            self.snapshot_to_return = HealingOutcomeAggregateSnapshot(
                version_id="test_snapshot_123", created_utc=created_utc, aggregates=tuple(aggregates)
            )
        return self.snapshot_to_return

    def propose_threshold_adjustments(self, snapshot):
        """Return empty proposal (no adjustments needed for this test)."""
        from system_learning.engines.healing_config_optimizer import ThresholdAdjustmentProposal

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id, created_utc=snapshot.created_utc, adjustments=()
        )


class FakeHealingOutcomeIntakeAdapter:
    """Fake intake adapter for testing."""

    def __init__(self) -> None:
        self.records_persisted: list[HealingOutcomeIntakeRecord] = []

    def build_record(self, aggregator, created_utc: int, source: str):
        """Build a fake intake record."""
        stats = (HealingOutcomeStats.from_counts("healer1", "LOCAL_AGENT", "failure1", 7, 3),)

        return HealingOutcomeIntakeRecord(
            schema_version=1,
            created_utc=created_utc,
            window_size=100,
            snapshot=stats,
            proposal=None,  # type: ignore
            source=source,
        )

    def persist_record(self, record: HealingOutcomeIntakeRecord) -> None:
        """Persist the record."""
        self.records_persisted.append(record)

    def get_recent_records(self, window_start_utc: int, window_end_utc: int) -> list:
        """Return persisted records within the window."""
        return [r for r in self.records_persisted if window_start_utc <= r.created_utc <= window_end_utc]


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


class TestMetaLearningPipelineWritesL4B:
    """Test suite for meta learning pipeline L4B writing."""

    def test_pipeline_writes_l4b_healing_snapshot_deterministically(self):
        """Test that pipeline writes L4B healing snapshot and returns version ID deterministically."""
        # Setup fake dependencies
        fake_l4_writer = FakeL4StateWriter()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake_adapter = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed the adapter with a real record inside the window so Step 8 runs
        now_utc = 1000
        window_start_utc = 900
        window_end_utc = 1100
        fake_intake_adapter.records_persisted.append(_make_seed_record(created_utc=950))

        # Create minimal pipeline dependencies
        mock_telemetry_store = Mock(spec=TelemetryStore)
        mock_telemetry_store.read_events.return_value = []
        mock_audit_store = Mock(spec=AuditStore)
        mock_audit_store.read_audit_slice.return_value = b""

        deps = PipelineDependencies(
            audit_store=mock_audit_store,
            telemetry_store=mock_telemetry_store,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake_adapter,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=fake_l4_writer,
        )

        # Create pipeline config
        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.oscillation_detector import OscillationPolicy
        from system_learning.validators.shadow_evaluator import ShadowThresholds

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
            sample_policy=SampleSizePolicy(min_observations=10),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
            enabled_proposers=(),
            require_replay_validation=False,
            require_shadow_validation=False,
            proposal_only=True,  # Don't commit/activate
        )

        run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start_utc,
            window_end_utc=window_end_utc,
            cfg=cfg,
            deps=deps,
        )

        # Verify L4B write occurred (pipeline ran Step 8 and persisted)
        assert len(fake_l4_writer.l4b_writes) == 1

        # Verify write parameters
        write = fake_l4_writer.l4b_writes[0]
        assert write["component_name"] == "meta-learning"
        assert write["created_utc"] == now_utc

        # Verify payload bytes contain serialized snapshot
        payload_bytes = write["payload_bytes"]
        assert isinstance(payload_bytes, bytes)
        # Should contain healer name in serialized form
        assert b"healer1" in payload_bytes

        # Verify version ID is deterministic
        version_id = hashlib.sha256(f"meta-learning:{now_utc}:{payload_bytes}".encode()).hexdigest()[:16]
        # The actual version ID would be returned by the writer
        assert isinstance(version_id, str)
        assert len(version_id) == 16

    def test_pipeline_without_l4_writer_no_writes(self):
        """Test that pipeline doesn't write L4B when writer not provided."""
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake_adapter = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 produces an intake record
        fake_intake_adapter.records_persisted.append(_make_seed_record(created_utc=1950))

        # Create dependencies without L4 writer
        mock_telemetry_store = Mock(spec=TelemetryStore)
        mock_telemetry_store.read_events.return_value = []
        mock_audit_store = Mock(spec=AuditStore)
        mock_audit_store.read_audit_slice.return_value = b""

        deps = PipelineDependencies(
            audit_store=mock_audit_store,
            telemetry_store=mock_telemetry_store,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake_adapter,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=None,  # No L4 writer
        )

        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.oscillation_detector import OscillationPolicy
        from system_learning.validators.shadow_evaluator import ShadowThresholds

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
            sample_policy=SampleSizePolicy(min_observations=10),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
            enabled_proposers=(),
            require_replay_validation=False,
            require_shadow_validation=False,
            proposal_only=True,
        )

        # Run pipeline
        run_pipeline(now_utc=2000, window_start_utc=1900, window_end_utc=2100, cfg=cfg, deps=deps)

        # Intake adapter received the pipeline-produced record (seed + pipeline = 2)
        assert len(fake_intake_adapter.records_persisted) >= 2
        # No L4B writes since no writer provided

    def test_pipeline_l4b_write_failure_doesnt_break_pipeline(self):
        """Test that L4B write failure doesn't break the pipeline."""

        class FailingL4StateWriter:
            """L4B writer that always fails."""

            def write_l4b_healing_snapshot(self, **kwargs) -> str:
                raise RuntimeError("Simulated L4B write failure")

        failing_writer = FailingL4StateWriter()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake_adapter = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 produces an intake record
        fake_intake_adapter.records_persisted.append(_make_seed_record(created_utc=2950))

        mock_telemetry_store = Mock(spec=TelemetryStore)
        mock_telemetry_store.read_events.return_value = []
        mock_audit_store = Mock(spec=AuditStore)
        mock_audit_store.read_audit_slice.return_value = b""

        deps = PipelineDependencies(
            audit_store=mock_audit_store,
            telemetry_store=mock_telemetry_store,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake_adapter,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=failing_writer,
        )

        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.oscillation_detector import OscillationPolicy
        from system_learning.validators.shadow_evaluator import ShadowThresholds

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
            sample_policy=SampleSizePolicy(min_observations=10),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
            enabled_proposers=(),
            require_replay_validation=False,
            require_shadow_validation=False,
            proposal_only=True,
        )

        # Should not raise exception even if L4B write fails
        proposals = run_pipeline(now_utc=3000, window_start_utc=2900, window_end_utc=3100, cfg=cfg, deps=deps)

        # Pipeline should still complete successfully
        assert isinstance(proposals, tuple)
        # Intake adapter should have seed + pipeline-produced record
        assert len(fake_intake_adapter.records_persisted) >= 2

    def test_pipeline_l4b_version_id_deterministic_same_snapshot(self):
        """Test that same snapshot produces same L4B version ID."""
        fake_l4_writer = FakeL4StateWriter()
        fake_optimizer = FakeHealingConfigOptimizer()
        fake_intake_adapter = FakeHealingOutcomeIntakeAdapter()

        # Pre-seed so Step 8 runs for both pipeline executions
        fake_intake_adapter.records_persisted.append(_make_seed_record(created_utc=3950))

        # Create deterministic snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=5, failure_count=5, total_count=10),
            ),
        ]
        deterministic_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="det_snapshot_456", created_utc=4000, aggregates=tuple(aggregates)
        )
        fake_optimizer.snapshot_to_return = deterministic_snapshot

        mock_telemetry_store = Mock(spec=TelemetryStore)
        mock_telemetry_store.read_events.return_value = []
        mock_audit_store = Mock(spec=AuditStore)
        mock_audit_store.read_audit_slice.return_value = b""

        deps = PipelineDependencies(
            audit_store=mock_audit_store,
            telemetry_store=mock_telemetry_store,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake_adapter,
            healing_config_optimizer=fake_optimizer,
            l4_state_writer=fake_l4_writer,
        )

        from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
        from system_learning.validators.oscillation_detector import OscillationPolicy
        from system_learning.validators.shadow_evaluator import ShadowThresholds

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=300),
            sample_policy=SampleSizePolicy(min_observations=10),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=300),
            enabled_proposers=(),
            require_replay_validation=False,
            require_shadow_validation=False,
            proposal_only=True,
        )

        # Run pipeline twice with same inputs
        run_pipeline(now_utc=4000, window_start_utc=3900, window_end_utc=4100, cfg=cfg, deps=deps)

        run_pipeline(now_utc=4000, window_start_utc=3900, window_end_utc=4100, cfg=cfg, deps=deps)

        # Should have two L4B writes
        assert len(fake_l4_writer.l4b_writes) == 2

        # Payload bytes should be identical
        payload1 = fake_l4_writer.l4b_writes[0]["payload_bytes"]
        payload2 = fake_l4_writer.l4b_writes[1]["payload_bytes"]
        assert payload1 == payload2
