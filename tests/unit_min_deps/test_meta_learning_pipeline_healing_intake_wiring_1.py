"""Tests for healing outcome intake wiring in meta-learning pipeline."""

from unittest.mock import MagicMock

import pytest

from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
from system_learning.pipelines.meta_learning_pipeline import (
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
        """Test that pipeline persists exactly one intake record when adapter is provided."""
        # Setup
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)

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

        # Run pipeline
        result = run_pipeline(now_utc=10000, window_start_utc=5000, window_end_utc=10000, cfg=cfg, deps=deps)

        # Verify exactly one record was persisted
        assert store.count() == 1
        stored_records = store.get_records()
        assert len(stored_records) == 1

        # Verify record contents
        record = stored_records[0]
        assert record.schema_version == 1
        assert record.created_utc == 10000
        assert record.source == "meta-learning-pipeline"
        assert record.window_size == 1  # Mock aggregator has one event
        assert len(record.snapshot) == 1

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
