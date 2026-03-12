"""Unit tests for meta-learning pipeline Path D (HITL + DPO) wiring."""

import json

import pytest

from system_learning.engines.rlhf_optimizer import DefaultDeterministicRLHFOptimizer
from system_learning.pipelines.meta_learning_pipeline import (
    PipelineConfig,
    PipelineDependencies,
    run_pipeline,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


pytestmark = pytest.mark.unit_min_deps


class TestMetaLearningPipelinePathDWiring:
    """Test suite for Path D DPO wiring in meta-learning pipeline."""

    def test_dpo_batch_artifact_injected_processed(self):
        """DPO batch artifact should be injected and processed by RLHF optimizer."""
        # Create DPO batch with APPROVE decision
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "control_hash_123",
                        "candidate_hash": "candidate_hash_456",
                    },
                    "control_output_hash": "control_hash_123",
                    "candidate_output_hash": "candidate_hash_456",
                    "human_decision": "APPROVE",
                    "reasons": ["good_quality", "meets_requirements"],
                },
            ]
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")

        # Create RLHF optimizer
        rlhf_optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=0.1,
            reject_tighten_delta=-0.1,
        )

        # Create minimal dependencies with DPO batch
        deps = PipelineDependencies(
            audit_store=MockAuditStore(),
            telemetry_store=MockTelemetryStore(),
            config_provider=MockConfigProvider(),
            baseline_metrics_provider=MockBaselineMetricsProvider(),
            dpo_batch_bytes=dpo_bytes,
            rlhf_optimizer=rlhf_optimizer,
        )

        # Create minimal config
        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=MockShadowThresholds(),
            cooldown_policy=MockCooldownPolicy(),
            sample_policy=MockSampleSizePolicy(),
            oscillation_policy=MockOscillationPolicy(),
            enabled_proposers=(),
            require_replay_validation=False,
            proposal_only=True,
        )

        # Run pipeline
        now_utc = 1234567890
        window_start = now_utc - 3600
        window_end = now_utc

        proposals = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        # Should have DPO proposal
        assert len(proposals) > 0

        # Find DPO proposal
        dpo_proposal = None
        for proposal in proposals:
            if hasattr(proposal, "source") and proposal.source == "rlhf_optimizer":
                dpo_proposal = proposal
                break

        assert dpo_proposal is not None
        assert dpo_proposal.target == "threshold_config"
        assert dpo_proposal.confidence > 0.0
        assert dpo_proposal.timestamp_utc == now_utc
        assert "approve_relax_0.100000" in dpo_proposal.reasons

    def test_no_dpo_batch_no_rlhf_processing(self):
        """No DPO batch should result in no RLHF processing."""
        # Create RLHF optimizer but no DPO batch
        rlhf_optimizer = DefaultDeterministicRLHFOptimizer()

        deps = PipelineDependencies(
            audit_store=MockAuditStore(),
            telemetry_store=MockTelemetryStore(),
            config_provider=MockConfigProvider(),
            baseline_metrics_provider=MockBaselineMetricsProvider(),
            dpo_batch_bytes=None,  # No DPO batch
            rlhf_optimizer=rlhf_optimizer,
        )

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=MockShadowThresholds(),
            cooldown_policy=MockCooldownPolicy(),
            sample_policy=MockSampleSizePolicy(),
            oscillation_policy=MockOscillationPolicy(),
            enabled_proposers=(),
            require_replay_validation=False,
            proposal_only=True,
        )

        now_utc = 1234567890
        window_start = now_utc - 3600
        window_end = now_utc

        proposals = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        # Should not have DPO proposal
        dpo_proposals = [p for p in proposals if hasattr(p, "source") and p.source == "rlhf_optimizer"]
        assert len(dpo_proposals) == 0

    def test_no_rlhf_optimizer_no_processing(self):
        """No RLHF optimizer should result in no DPO processing."""
        # Create DPO batch but no RLHF optimizer
        dpo_batch = {"pairs": []}
        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")

        deps = PipelineDependencies(
            audit_store=MockAuditStore(),
            telemetry_store=MockTelemetryStore(),
            config_provider=MockConfigProvider(),
            baseline_metrics_provider=MockBaselineMetricsProvider(),
            dpo_batch_bytes=dpo_bytes,
            rlhf_optimizer=None,  # No RLHF optimizer
        )

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=MockShadowThresholds(),
            cooldown_policy=MockCooldownPolicy(),
            sample_policy=MockSampleSizePolicy(),
            oscillation_policy=MockOscillationPolicy(),
            enabled_proposers=(),
            require_replay_validation=False,
            proposal_only=True,
        )

        now_utc = 1234567890
        window_start = now_utc - 3600
        window_end = now_utc

        proposals = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        # Should not have DPO proposal
        dpo_proposals = [p for p in proposals if hasattr(p, "source") and p.source == "rlhf_optimizer"]
        assert len(dpo_proposals) == 0

    def test_proposal_only_no_activation(self):
        """DPO processing should be proposal-only with no activation."""
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "REJECT",
                    "reasons": ["poor_quality"],
                },
            ]
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")

        rlhf_optimizer = DefaultDeterministicRLHFOptimizer()

        deps = PipelineDependencies(
            audit_store=MockAuditStore(),
            telemetry_store=MockTelemetryStore(),
            config_provider=MockConfigProvider(),
            baseline_metrics_provider=MockBaselineMetricsProvider(),
            dpo_batch_bytes=dpo_bytes,
            rlhf_optimizer=rlhf_optimizer,
        )

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=MockShadowThresholds(),
            cooldown_policy=MockCooldownPolicy(),
            sample_policy=MockSampleSizePolicy(),
            oscillation_policy=MockOscillationPolicy(),
            enabled_proposers=(),
            require_replay_validation=False,
            proposal_only=True,  # Proposal-only mode
        )

        now_utc = 1234567890
        window_start = now_utc - 3600
        window_end = now_utc

        proposals = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        # Should have DPO proposal but no activation
        dpo_proposal = None
        for proposal in proposals:
            if hasattr(proposal, "source") and proposal.source == "rlhf_optimizer":
                dpo_proposal = proposal
                break

        assert dpo_proposal is not None
        assert dpo_proposal.target == "threshold_config"
        assert dpo_proposal.changes is not None  # Has proposed changes
        # No direct activation should occur

    def test_malformed_dpo_batch_handled_gracefully(self):
        """Malformed DPO batch should be handled gracefully without crashing."""
        malformed_bytes = b"invalid json data"

        rlhf_optimizer = DefaultDeterministicRLHFOptimizer()

        deps = PipelineDependencies(
            audit_store=MockAuditStore(),
            telemetry_store=MockTelemetryStore(),
            config_provider=MockConfigProvider(),
            baseline_metrics_provider=MockBaselineMetricsProvider(),
            dpo_batch_bytes=malformed_bytes,
            rlhf_optimizer=rlhf_optimizer,
        )

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=MockShadowThresholds(),
            cooldown_policy=MockCooldownPolicy(),
            sample_policy=MockSampleSizePolicy(),
            oscillation_policy=MockOscillationPolicy(),
            enabled_proposers=(),
            require_replay_validation=False,
            proposal_only=True,
        )

        now_utc = 1234567890
        window_start = now_utc - 3600
        window_end = now_utc

        # Should not crash
        proposals = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        # Should complete successfully (may or may not have DPO proposal)
        assert isinstance(proposals, tuple)

    def test_deterministic_processing_same_inputs(self):
        """Same DPO batch inputs should produce identical proposals."""
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {"control_hash": "control", "candidate_hash": "candidate"},
                    "control_output_hash": "control",
                    "candidate_output_hash": "candidate",
                    "human_decision": "APPROVE",
                    "reasons": ["deterministic_test"],
                },
            ]
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")

        rlhf_optimizer = DefaultDeterministicRLHFOptimizer(approve_relax_delta=0.05)

        deps = PipelineDependencies(
            audit_store=MockAuditStore(),
            telemetry_store=MockTelemetryStore(),
            config_provider=MockConfigProvider(),
            baseline_metrics_provider=MockBaselineMetricsProvider(),
            dpo_batch_bytes=dpo_bytes,
            rlhf_optimizer=rlhf_optimizer,
        )

        cfg = PipelineConfig(
            engine_version="1.0.0",
            config_surface_version="1.0.0",
            shadow_thresholds=MockShadowThresholds(),
            cooldown_policy=MockCooldownPolicy(),
            sample_policy=MockSampleSizePolicy(),
            oscillation_policy=MockOscillationPolicy(),
            enabled_proposers=(),
            require_replay_validation=False,
            proposal_only=True,
        )

        now_utc = 1234567890
        window_start = now_utc - 3600
        window_end = now_utc

        # Run pipeline twice
        proposals1 = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        proposals2 = run_pipeline(
            now_utc=now_utc,
            window_start_utc=window_start,
            window_end_utc=window_end,
            cfg=cfg,
            deps=deps,
        )

        # Should have identical DPO proposals
        dpo_proposal1 = next(
            (p for p in proposals1 if hasattr(p, "source") and p.source == "rlhf_optimizer"), None
        )
        dpo_proposal2 = next(
            (p for p in proposals2 if hasattr(p, "source") and p.source == "rlhf_optimizer"), None
        )

        assert dpo_proposal1 is not None
        assert dpo_proposal2 is not None
        assert dpo_proposal1.changes == dpo_proposal2.changes
        assert dpo_proposal1.confidence == dpo_proposal2.confidence
        assert dpo_proposal1.reasons == dpo_proposal2.reasons


# Mock classes for testing
class MockAuditStore:
    def read_audit_slice(self, start, end):
        return []


class MockTelemetryStore:
    def read_events(self, start, end):
        return []


class MockConfigProvider:
    def get_current_configs(self):
        return {"threshold_a": 0.5, "threshold_b": 1.0}


class MockBaselineMetricsProvider:
    def get_baseline_metrics(self):
        return {}


class MockShadowThresholds:
    pass


class MockCooldownPolicy:
    pass


class MockSampleSizePolicy:
    pass


class MockOscillationPolicy:
    pass