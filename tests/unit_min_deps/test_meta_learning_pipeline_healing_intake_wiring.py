"""Tests for healing outcome intake wiring in meta-learning pipeline."""

from unittest.mock import MagicMock

import pytest

from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
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


@pytest.mark.unit_min_deps
class TestMetaLearningPipelineHealingIntakeWiring:
    """Test suite for healing outcome intake wiring in meta-learning pipeline."""

    def test_pipeline_with_healing_intake_adapter_persists_record(self) -> None:
        """Pipeline Step 8 persists a window-aggregated record from real pre-seeded records.

        After GAP-C fix, Step 8 never injects mock data. This test seeds the store with
        a real HealingOutcomeIntakeRecord *before* running the pipeline, so that
        get_recent_records() returns a non-empty window and triggers aggregation.
        """
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        # Seed the store with one real record inside the pipeline window
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

        seed_ts = 7000  # inside window [5000, 10000]
        seed_agg = HealingOutcomeAggregator(window_size=2)
        seed_agg.ingest(
            HealingOutcomeEvent(
                healer_id="real_healer",
                tier="L0",
                failure_type="REAL_FAIL",
                success=True,
                timestamp_utc=seed_ts,
            )
        )
        seed_agg.ingest(
            HealingOutcomeEvent(
                healer_id="real_healer",
                tier="L0",
                failure_type="REAL_FAIL",
                success=False,
                timestamp_utc=seed_ts,
            )
        )
        seed_record = adapter.build_record(aggregator=seed_agg, created_utc=seed_ts, source="pre-seed")
        adapter.persist_record(seed_record)
        assert store.count() == 1  # one seed record

        # Create mock dependencies
        audit_store = MagicMock()
        telemetry_store = MagicMock()
        config_provider = MagicMock()
        baseline_metrics_provider = MagicMock()

        # Configure mocks
        audit_store.read_audit_slice.return_value = b"mock_audit_data"
        telemetry_store.read_events.return_value = ()
        config_provider.get_current_configs.return_value = {}
        config_provider.get_last_update_utc.return_value = None
        config_provider.get_param_history.return_value = ()
        baseline_metrics_provider.production_metrics.return_value = {}
        baseline_metrics_provider.shadow_metrics.return_value = {}

        # Create dependencies with healing intake adapter
        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=baseline_metrics_provider,
            healing_outcome_intake_adapter=adapter,
        )

        # Create pipeline config
        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            enabled_proposers=("L0", "RAG", "L1", "L5"),
            proposal_only=True,  # Don't commit/activate for test
            require_replay_validation=False,
            require_shadow_validation=False,
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=10),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.5, freeze_seconds=3600),
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
        )

        # Run pipeline — window [5000, 10000] includes seed_record at 7000
        result = run_pipeline(now_utc=10000, window_start_utc=5000, window_end_utc=10000, cfg=cfg, deps=deps)

        # Step 8 should have added one more window-aggregated record
        assert store.count() == 2
        stored_records = store.get_records()

        # The last record is the window-aggregated one from Step 8
        window_record = stored_records[-1]
        assert window_record.schema_version == 1
        assert window_record.created_utc == 10000
        assert window_record.source == "meta-learning-pipeline-window"
        # Verify healer_id from the seed flows through (not a synthetic test_healer)
        assert window_record.snapshot
        healer_ids = {s.healer_id for s in window_record.snapshot}
        assert "test_healer" not in healer_ids, (
            "Synthetic test_healer found in window record — mock path not removed"
        )
        assert "real_healer" in healer_ids

        # Verify pipeline still returns result
        assert isinstance(result, tuple)

    def test_pipeline_without_healing_intake_adapter_unchanged(self) -> None:
        """Test that pipeline behavior is unchanged when adapter is not provided."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()

        # Create mock dependencies (no healing intake adapter)
        audit_store = MagicMock()
        telemetry_store = MagicMock()
        config_provider = MagicMock()
        baseline_metrics_provider = MagicMock()

        # Configure mocks
        audit_store.read_audit_slice.return_value = b"mock_audit_data"
        telemetry_store.read_events.return_value = ()
        config_provider.get_current_configs.return_value = {}
        config_provider.get_last_update_utc.return_value = None
        config_provider.get_param_history.return_value = ()
        baseline_metrics_provider.production_metrics.return_value = {}
        baseline_metrics_provider.shadow_metrics.return_value = {}

        # Create dependencies without healing intake adapter
        deps = PipelineDependencies(
            audit_store=audit_store,
            telemetry_store=telemetry_store,
            config_provider=config_provider,
            baseline_metrics_provider=baseline_metrics_provider,
            # healing_outcome_intake_adapter=None (default)
        )

        # Create pipeline config
        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            enabled_proposers=("L0", "RAG", "L1", "L5"),
            proposal_only=True,
            require_replay_validation=False,
            require_shadow_validation=False,
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=10),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.5, freeze_seconds=3600),
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
        )

        # Run pipeline
        result = run_pipeline(now_utc=10000, window_start_utc=5000, window_end_utc=10000, cfg=cfg, deps=deps)

        # Verify no records were persisted
        assert store.count() == 0

        # Verify pipeline still returns result
        assert isinstance(result, tuple)
