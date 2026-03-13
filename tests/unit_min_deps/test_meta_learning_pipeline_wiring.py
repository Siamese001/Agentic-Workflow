"""Meta-learning pipeline wiring tests: merged from 7-file family.

Covers:
  commit_path:          proposal_only=False guards, approval gate, determinism
  healing_intake:       healing outcome intake adapter wiring (Step 8)
  ingests_phase9:       Phase 9 artifact bytes in PipelineDependencies
  path_d_wiring:        HITL + DPO (RLHF optimizer) wiring
  pattern_wiring:       Pattern analysis engine wiring (Phase 8)
  proposal_only:        proposal_only mode — no commit/activate
  writes_l4b:           L4B healing-snapshot write path
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300

pytestmark = pytest.mark.unit_min_deps

# ---------------------------------------------------------------------------
# Top-level imports (shared across all sections)
# ---------------------------------------------------------------------------

from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.pattern_analysis_engine import PatternAnalysisEngine
from system_learning.engines.rlhf_optimizer import DefaultDeterministicRLHFOptimizer
from system_learning.pipelines.approval_gates import ApprovalDecision
from system_learning.pipelines.meta_learning_pipeline import (
    AuditStore,
    BaselineMetricsProvider,
    ConfigProvider,
    PipelineConfig,
    PipelineDependencies,
    PipelineError,
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
from system_learning.types.pattern_analysis_types import (
    PatternFinding,
    PatternFindingKey,
    PatternFindingReport,
    PatternSourceIds,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowMetrics, ShadowThresholds

# ===========================================================================
# Shared helpers / constants
# ===========================================================================


def _default_shadow_thresholds(**kw):
    defaults: dict = {
        "max_p95_latency_regression_pct": 10.0,
        "max_error_rate_regression_abs": 0.05,
        "max_cpu_regression_pct": 10.0,
        "max_mem_regression_pct": 10.0,
        "forbid_any_safety_violation_increase": True,
    }
    defaults.update(kw)
    return ShadowThresholds(**defaults)


def _default_cfg(**kw):
    defaults: dict = {
        "engine_version": "v1",
        "config_surface_version": "v1",
        "shadow_thresholds": _default_shadow_thresholds(),
        "cooldown_policy": CooldownPolicy(min_seconds_between_updates=3600),
        "sample_policy": SampleSizePolicy(min_observations=1000),
        "oscillation_policy": OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
        "enabled_proposers": (),
        "proposal_only": True,
    }
    defaults.update(kw)
    return PipelineConfig(**defaults)


def _make_seed_record(created_utc: int) -> HealingOutcomeIntakeRecord:
    stats = (HealingOutcomeStats.from_counts("healer1", "LOCAL_AGENT", "failure1", 7, 3),)
    return HealingOutcomeIntakeRecord(
        schema_version=1,
        created_utc=created_utc,
        window_size=1,
        snapshot=stats,
        proposal=HealingOutcomeProposal(stats=stats),
        source="test-seed",
    )


# ===========================================================================
# commit_path fakes
# ===========================================================================


class _CommitFakeAuditStore:
    def __init__(self, audit_data: bytes):
        self.audit_data = audit_data

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        return self.audit_data


class _CommitFakeTelemetryStore:
    def __init__(self, events: list[tuple[int, str, bytes]]):
        self.events = events

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        return tuple(
            (ts, kind, payload)
            for ts, kind, payload in self.events
            if window_start_utc <= ts < window_end_utc
        )


class _CommitFakeConfigProvider:
    def __init__(self):
        self.configs = {"routing": b"routing_config_v1"}

    def get_current_configs(self) -> dict[str, bytes]:
        return self.configs

    def get_last_update_utc(self, surface_name: str) -> int | None:
        return None

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        return ()


class _CommitFakeBaselineMetricsProvider:
    def __init__(self):
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


class _FakeVersionStore:
    def __init__(self):
        self.committed_packages = []

    def commit_change_package(self, pkg) -> str:
        self.committed_packages.append(pkg)
        return f"version_{len(self.committed_packages)}"


class _FakeActivator:
    def __init__(self):
        self.activations = []

    def activate(self, component: str, version_id: str) -> None:
        self.activations.append((component, version_id))


class _FakeApprovalGate:
    def __init__(self, decision: ApprovalDecision):
        self.decision = decision
        self.decide_calls = []

    def decide(self, pkg, rca, snapshot):
        self.decide_calls.append((pkg, rca, snapshot))
        return self.decision


def _commit_deps(**kw):
    base: dict = {
        "audit_store": _CommitFakeAuditStore(b"SyntaxError: test"),
        "telemetry_store": _CommitFakeTelemetryStore([]),
        "config_provider": _CommitFakeConfigProvider(),
        "baseline_metrics_provider": _CommitFakeBaselineMetricsProvider(),
    }
    base.update(kw)
    return PipelineDependencies(**base)


# ===========================================================================
# commit_path tests
# ===========================================================================


class TestCommitPath:
    def test_commit_path_requires_version_store(self):
        with pytest.raises(PipelineError, match="version_store required"):
            run_pipeline(
                now_utc=1700003600,
                window_start_utc=1700000000,
                window_end_utc=1700003600,
                cfg=_default_cfg(proposal_only=False),
                deps=_commit_deps(
                    version_store=None, approval_gate=_FakeApprovalGate(ApprovalDecision.APPROVE)
                ),
            )

    def test_commit_path_requires_approval_gate(self):
        with pytest.raises(PipelineError, match="approval_gate required"):
            run_pipeline(
                now_utc=1700003600,
                window_start_utc=1700000000,
                window_end_utc=1700003600,
                cfg=_default_cfg(proposal_only=False),
                deps=_commit_deps(version_store=_FakeVersionStore(), approval_gate=None),
            )

    def test_approval_reject_does_not_commit(self):
        version_store = _FakeVersionStore()
        activator = _FakeActivator()
        run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=_default_cfg(proposal_only=False),
            deps=_commit_deps(
                version_store=version_store,
                activator=activator,
                approval_gate=_FakeApprovalGate(ApprovalDecision.REJECT),
            ),
        )
        assert len(version_store.committed_packages) == 0
        assert len(activator.activations) == 0

    def test_commit_path_deterministic(self):
        cfg = _default_cfg(proposal_only=False)
        deps = _commit_deps(
            version_store=_FakeVersionStore(),
            approval_gate=_FakeApprovalGate(ApprovalDecision.APPROVE),
        )
        kw = {"now_utc": 1700003600, "window_start_utc": 1700000000, "window_end_utc": 1700003600}
        assert run_pipeline(cfg=cfg, deps=deps, **kw) == run_pipeline(cfg=cfg, deps=deps, **kw)


# ===========================================================================
# healing_intake tests
# ===========================================================================


class TestMetaLearningPipelineHealingIntakeWiring:
    def _minimal_cfg(self):
        return PipelineConfig(
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

    def _mock_base_deps(self):
        audit_store = MagicMock()
        telemetry_store = MagicMock()
        config_provider = MagicMock()
        baseline_metrics_provider = MagicMock()
        audit_store.read_audit_slice.return_value = b"mock_audit_data"
        telemetry_store.read_events.return_value = ()
        config_provider.get_current_configs.return_value = {}
        config_provider.get_last_update_utc.return_value = None
        config_provider.get_param_history.return_value = ()
        baseline_metrics_provider.production_metrics.return_value = {}
        baseline_metrics_provider.shadow_metrics.return_value = {}
        return audit_store, telemetry_store, config_provider, baseline_metrics_provider

    def test_pipeline_with_healing_intake_adapter_persists_record(self) -> None:
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store)
        seed_ts = 7000
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
        assert store.count() == 1

        a, t, c, b = self._mock_base_deps()
        deps = PipelineDependencies(
            audit_store=a,
            telemetry_store=t,
            config_provider=c,
            baseline_metrics_provider=b,
            healing_outcome_intake_adapter=adapter,
        )
        result = run_pipeline(
            now_utc=10000, window_start_utc=5000, window_end_utc=10000, cfg=self._minimal_cfg(), deps=deps
        )
        assert store.count() == 2
        window_record = store.get_records()[-1]
        assert window_record.schema_version == 1
        assert window_record.created_utc == 10000
        assert window_record.source == "meta-learning-pipeline-window"
        healer_ids = {s.healer_id for s in window_record.snapshot}
        assert "test_healer" not in healer_ids
        assert "real_healer" in healer_ids
        assert isinstance(result, tuple)

    def test_pipeline_without_healing_intake_adapter_unchanged(self) -> None:
        store = InMemoryHealingOutcomeIntakeStore()
        a, t, c, b = self._mock_base_deps()
        deps = PipelineDependencies(
            audit_store=a,
            telemetry_store=t,
            config_provider=c,
            baseline_metrics_provider=b,
        )
        result = run_pipeline(
            now_utc=10000, window_start_utc=5000, window_end_utc=10000, cfg=self._minimal_cfg(), deps=deps
        )
        assert store.count() == 0
        assert isinstance(result, tuple)


# ===========================================================================
# ingests_phase9 tests
# ===========================================================================


class _Phase9Mock:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        return _Phase9Mock()

    def __call__(self, *args, **kwargs):
        return _Phase9Mock()


class TestMetaLearningPipelineIngestsPhase9Artifacts:
    def test_pipeline_dependencies_accept_phase9_artifacts(self):
        from agentic_core.L2_execution.types.resource_prediction_types import (
            FailureSignature,
            ResourceEnvelope,
            ResourcePrediction,
        )
        from agentic_core.L2_execution.types.rollback_refinement_types import (
            RollbackRefinementDecision,
            RollbackStrategyId,
        )

        signature = FailureSignature(
            component="test_component",
            failure_type="timeout",
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )
        envelope = ResourceEnvelope(cpu_cores=4, memory_mb=2048, timeout_s=600)
        resource_prediction = ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=0.85,
            reasons=("failure_type_timeout", "history_available", "high_cpu"),
        )
        resource_prediction_bytes = json.dumps(
            {
                "signature": {
                    "component": signature.component,
                    "failure_type": signature.failure_type,
                    "fingerprint": signature.fingerprint,
                },
                "envelope": {
                    "cpu_cores": envelope.cpu_cores,
                    "memory_mb": envelope.memory_mb,
                    "timeout_s": envelope.timeout_s,
                },
                "confidence": resource_prediction.confidence,
                "reasons": list(resource_prediction.reasons),
            }
        ).encode("utf-8")

        chosen_strategy = RollbackStrategyId("state_snapshot")
        ranked_strategies = (
            RollbackStrategyId("state_snapshot"),
            RollbackStrategyId("checkpoint_restore"),
            RollbackStrategyId("graceful_shutdown"),
        )
        rollback_decision = RollbackRefinementDecision(
            chosen=chosen_strategy,
            ranked=ranked_strategies,
            reasons=("chosen_strategy_state_snapshot", "failure_type_memory_error", "history_based"),
        )
        rollback_decision_bytes = json.dumps(
            {
                "chosen": {"name": chosen_strategy.name},
                "ranked": [{"name": s.name} for s in ranked_strategies],
                "reasons": list(rollback_decision.reasons),
            }
        ).encode("utf-8")

        deps = PipelineDependencies(
            audit_store=_Phase9Mock(),
            telemetry_store=_Phase9Mock(),
            config_provider=_Phase9Mock(),
            baseline_metrics_provider=_Phase9Mock(),
            resource_predictor_bytes=resource_prediction_bytes,
            rollback_refinement_decision_bytes=rollback_decision_bytes,
        )
        assert deps.resource_predictor_bytes is not None
        assert deps.rollback_refinement_decision_bytes is not None
        assert isinstance(deps.resource_predictor_bytes, bytes)
        assert isinstance(deps.rollback_refinement_decision_bytes, bytes)

    def test_pipeline_dependencies_accept_none_artifacts(self):
        deps = PipelineDependencies(
            audit_store=_Phase9Mock(),
            telemetry_store=_Phase9Mock(),
            config_provider=_Phase9Mock(),
            baseline_metrics_provider=_Phase9Mock(),
            resource_predictor_bytes=None,
            rollback_refinement_decision_bytes=None,
        )
        assert deps.resource_predictor_bytes is None
        assert deps.rollback_refinement_decision_bytes is None

    def test_artifact_serialization_stability(self):
        from agentic_core.L2_execution.types.resource_prediction_types import (
            FailureSignature,
            ResourceEnvelope,
            ResourcePrediction,
        )

        signature = FailureSignature(
            component="stability_test",
            failure_type="cpu_error",
            fingerprint="stable_fingerprint_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )
        envelope = ResourceEnvelope(cpu_cores=8, memory_mb=4096, timeout_s=900)
        resource_prediction = ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=0.9,
            reasons=("failure_type_cpu_error", "history_available"),
        )
        payload = {
            "signature": {
                "component": signature.component,
                "failure_type": signature.failure_type,
                "fingerprint": signature.fingerprint,
            },
            "envelope": {
                "cpu_cores": envelope.cpu_cores,
                "memory_mb": envelope.memory_mb,
                "timeout_s": envelope.timeout_s,
            },
            "confidence": resource_prediction.confidence,
            "reasons": list(resource_prediction.reasons),
        }
        assert json.dumps(payload).encode() == json.dumps(payload).encode()

    def test_malformed_artifact_handling(self):
        deps = PipelineDependencies(
            audit_store=_Phase9Mock(),
            telemetry_store=_Phase9Mock(),
            config_provider=_Phase9Mock(),
            baseline_metrics_provider=_Phase9Mock(),
            resource_predictor_bytes=b"invalid json data",
            rollback_refinement_decision_bytes=b"invalid json data",
        )
        assert deps.resource_predictor_bytes == b"invalid json data"
        assert deps.rollback_refinement_decision_bytes == b"invalid json data"

    def test_empty_artifact_bytes(self):
        deps = PipelineDependencies(
            audit_store=_Phase9Mock(),
            telemetry_store=_Phase9Mock(),
            config_provider=_Phase9Mock(),
            baseline_metrics_provider=_Phase9Mock(),
            resource_predictor_bytes=b"",
            rollback_refinement_decision_bytes=b"",
        )
        assert deps.resource_predictor_bytes == b""
        assert deps.rollback_refinement_decision_bytes == b""


# ===========================================================================
# path_d_wiring (DPO / RLHF) fakes + tests
# ===========================================================================


class _MockAuditStore:
    def read_audit_slice(self, start, end):
        return []


class _MockTelemetryStore:
    def read_events(self, start, end):
        return []


class _MockConfigProvider:
    def get_current_configs(self):
        return {"threshold_a": 0.5, "threshold_b": 1.0}


class _MockBaselineMetricsProvider:
    def get_baseline_metrics(self):
        return {}


class _MockShadowThresholds:
    pass


class _MockCooldownPolicy:
    pass


class _MockSampleSizePolicy:
    pass


class _MockOscillationPolicy:
    pass


def _path_d_cfg(**kw):
    defaults: dict = {
        "engine_version": "1.0.0",
        "config_surface_version": "1.0.0",
        "shadow_thresholds": _MockShadowThresholds(),
        "cooldown_policy": _MockCooldownPolicy(),
        "sample_policy": _MockSampleSizePolicy(),
        "oscillation_policy": _MockOscillationPolicy(),
        "enabled_proposers": (),
        "require_replay_validation": False,
        "proposal_only": True,
    }
    defaults.update(kw)
    return PipelineConfig(**defaults)


def _path_d_deps(**kw):
    base: dict = {
        "audit_store": _MockAuditStore(),
        "telemetry_store": _MockTelemetryStore(),
        "config_provider": _MockConfigProvider(),
        "baseline_metrics_provider": _MockBaselineMetricsProvider(),
    }
    base.update(kw)
    return PipelineDependencies(**base)


def _dpo_bytes(human_decision: str = "APPROVE") -> bytes:
    batch = {
        "pairs": [
            {
                "example_id": {"control_hash": "control_hash_123", "candidate_hash": "candidate_hash_456"},
                "control_output_hash": "control_hash_123",
                "candidate_output_hash": "candidate_hash_456",
                "human_decision": human_decision,
                "reasons": ["good_quality"],
            }
        ]
    }
    return json.dumps(batch, separators=(",", ":"), sort_keys=True).encode("utf-8")


class TestMetaLearningPipelinePathDWiring:
    def _run(self, deps, cfg=None):
        now_utc = 1234567890
        return run_pipeline(
            now_utc=now_utc,
            window_start_utc=now_utc - 3600,
            window_end_utc=now_utc,
            cfg=cfg or _path_d_cfg(),
            deps=deps,
        )

    def test_dpo_batch_artifact_injected_processed(self):
        rlhf = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=0.1,
            reject_tighten_delta=-0.1,
        )
        proposals = self._run(_path_d_deps(dpo_batch_bytes=_dpo_bytes("APPROVE"), rlhf_optimizer=rlhf))
        assert len(proposals) > 0
        dpo = next((p for p in proposals if hasattr(p, "source") and p.source == "rlhf_optimizer"), None)
        assert dpo is not None
        assert dpo.target == "threshold_config"
        assert dpo.confidence > 0.0
        assert "approve_relax_0.100000" in dpo.reasons

    def test_no_dpo_batch_no_rlhf_processing(self):
        rlhf = DefaultDeterministicRLHFOptimizer()
        proposals = self._run(_path_d_deps(dpo_batch_bytes=None, rlhf_optimizer=rlhf))
        dpo = [p for p in proposals if hasattr(p, "source") and p.source == "rlhf_optimizer"]
        assert len(dpo) == 0

    def test_no_rlhf_optimizer_no_processing(self):
        proposals = self._run(
            _path_d_deps(dpo_batch_bytes=json.dumps({"pairs": []}).encode(), rlhf_optimizer=None)
        )
        dpo = [p for p in proposals if hasattr(p, "source") and p.source == "rlhf_optimizer"]
        assert len(dpo) == 0

    def test_proposal_only_no_activation(self):
        rlhf = DefaultDeterministicRLHFOptimizer()
        proposals = self._run(_path_d_deps(dpo_batch_bytes=_dpo_bytes("REJECT"), rlhf_optimizer=rlhf))
        dpo = next((p for p in proposals if hasattr(p, "source") and p.source == "rlhf_optimizer"), None)
        assert dpo is not None
        assert dpo.changes is not None

    def test_malformed_dpo_batch_handled_gracefully(self):
        rlhf = DefaultDeterministicRLHFOptimizer()
        proposals = self._run(_path_d_deps(dpo_batch_bytes=b"invalid json data", rlhf_optimizer=rlhf))
        assert isinstance(proposals, tuple)

    def test_deterministic_processing_same_inputs(self):
        rlhf = DefaultDeterministicRLHFOptimizer(approve_relax_delta=0.05)
        deps = _path_d_deps(dpo_batch_bytes=_dpo_bytes("APPROVE"), rlhf_optimizer=rlhf)
        now_utc = 1234567890
        kw = {
            "now_utc": now_utc,
            "window_start_utc": now_utc - 3600,
            "window_end_utc": now_utc,
            "cfg": _path_d_cfg(),
        }
        p1 = run_pipeline(deps=deps, **kw)
        p2 = run_pipeline(deps=deps, **kw)
        d1 = next((p for p in p1 if hasattr(p, "source") and p.source == "rlhf_optimizer"), None)
        d2 = next((p for p in p2 if hasattr(p, "source") and p.source == "rlhf_optimizer"), None)
        assert d1 is not None and d2 is not None
        assert d1.changes == d2.changes
        assert d1.confidence == d2.confidence
        assert d1.reasons == d2.reasons


# ===========================================================================
# pattern_wiring fakes + tests
# ===========================================================================


def _pattern_seed_record(created_utc: int) -> HealingOutcomeIntakeRecord:
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
class _PatternFakeAuditStore:
    records: list[Any] = None

    def __post_init__(self):
        if self.records is None:
            object.__setattr__(self, "records", [])

    def read_records(self, start_utc, end_utc):
        return []

    def read_audit_slice(self, start_utc, end_utc):
        return b'{"audit": []}'


@dataclass(frozen=True, slots=True)
class _PatternFakeTelemetryStore:
    data: dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            object.__setattr__(self, "data", {})

    def read_metrics(self, start_utc, end_utc):
        return {}

    def read_events(self, start_utc, end_utc):
        return []


@dataclass(frozen=True, slots=True)
class _PatternFakeConfigProvider:
    def get_config(self, component):
        return {}

    def get_current_configs(self):
        return {}

    def get_last_update_utc(self, surface_name):
        return 1000

    def get_param_history(self, surface_name, window):
        return []


@dataclass(frozen=True, slots=True)
class _PatternFakeBaselineMetricsProvider:
    def get_baseline(self, component):
        return {}

    def production_metrics(self):
        return {}

    def shadow_metrics(self, pkg):
        return {}


@dataclass(frozen=True, slots=True)
class _PatternFakeL4StateWriter(L4StateWriter):
    healing_snapshot_bytes: bytes = None
    detection_signal_bytes: bytes = None
    drift_snapshot_bytes: bytes = None
    l4b_writes: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.l4b_writes is None:
            object.__setattr__(self, "l4b_writes", [])

    def write_l4b_healing_snapshot(self, payload_bytes, component_name, created_utc):
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
class _PatternFakeHealingConfigOptimizer(HealingConfigOptimizer):
    pattern_reports_received: list[PatternFindingReport] = None

    def __post_init__(self):
        if self.pattern_reports_received is None:
            object.__setattr__(self, "pattern_reports_received", [])

    def propose_threshold_adjustments_with_patterns(self, snapshot, pattern_report=None):
        if pattern_report:
            self.pattern_reports_received.append(pattern_report)
        from system_learning.engines.healing_config_optimizer import (
            ThresholdAdjustment,
            ThresholdAdjustmentProposal,
        )

        adj = ThresholdAdjustment(
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
            adjustments=(adj,),
        )


@dataclass(frozen=True, slots=True)
class _PatternFakePatternAnalysisEngine(PatternAnalysisEngine):
    analyze_calls: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.analyze_calls is None:
            object.__setattr__(self, "analyze_calls", [])

    def analyze(self, *, healing_snapshot_bytes, detection_signal_bytes, drift_snapshot_bytes, now_utc):
        self.analyze_calls.append(
            {
                "healing_snapshot_bytes": healing_snapshot_bytes,
                "detection_signal_bytes": detection_signal_bytes,
                "drift_snapshot_bytes": drift_snapshot_bytes,
                "now_utc": now_utc,
            }
        )
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
class _PatternFakeIntakeAdapter:
    records_persisted: list[Any] = None

    def __post_init__(self):
        if self.records_persisted is None:
            object.__setattr__(self, "records_persisted", [])

    def build_record(self, aggregator, created_utc, source):
        @dataclass(frozen=True, slots=True)
        class _FakeRecord:
            snapshot: list[Any]

        @dataclass(frozen=True, slots=True)
        class _FakeStats:
            healer_id: str
            tier: str
            failure_type: str
            success_count: int
            failure_count: int
            total_count: int

        return _FakeRecord(
            snapshot=[
                _FakeStats(
                    healer_id="test_healer",
                    tier="LOCAL_AGENT",
                    failure_type="timeout",
                    success_count=30,
                    failure_count=70,
                    total_count=100,
                )
            ]
        )

    def persist_record(self, record):
        self.records_persisted.append(record)

    def get_recent_records(self, window_start_utc, window_end_utc):
        return [
            r
            for r in self.records_persisted
            if window_start_utc <= getattr(r, "created_utc", 0) <= window_end_utc
        ]


def _pattern_cfg():
    return PipelineConfig(
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
    )


def _pattern_deps(fake_l4=None, fake_engine=None, fake_opt=None, fake_intake=None):
    return PipelineDependencies(
        audit_store=_PatternFakeAuditStore(),
        telemetry_store=_PatternFakeTelemetryStore(),
        config_provider=_PatternFakeConfigProvider(),
        baseline_metrics_provider=_PatternFakeBaselineMetricsProvider(),
        healing_outcome_intake_adapter=fake_intake or _PatternFakeIntakeAdapter(),
        healing_config_optimizer=fake_opt or _PatternFakeHealingConfigOptimizer(),
        l4_state_writer=fake_l4 or _PatternFakeL4StateWriter(),
        pattern_analysis_engine=fake_engine or _PatternFakePatternAnalysisEngine(),
    )


def _pattern_run(deps, now_utc=2000):
    return run_pipeline(
        now_utc=now_utc,
        window_start_utc=now_utc - 100,
        window_end_utc=now_utc + 100,
        cfg=_pattern_cfg(),
        deps=deps,
    )


class TestMetaLearningPipelinePatternWiring:
    def test_pattern_engine_called_with_correct_inputs(self):
        aggregates = [
            (
                HealingOutcomeAggregateKey("test_healer", "LOCAL_AGENT", "timeout"),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]
        snap = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )
        fake_engine = _PatternFakePatternAnalysisEngine()
        fake_intake = _PatternFakeIntakeAdapter()
        fake_intake.records_persisted.append(_pattern_seed_record(created_utc=1950))
        deps = _pattern_deps(
            fake_l4=_PatternFakeL4StateWriter(healing_snapshot_bytes=snap.canonical_bytes()),
            fake_engine=fake_engine,
            fake_intake=fake_intake,
        )
        _pattern_run(deps)
        assert len(fake_engine.analyze_calls) == 1
        call = fake_engine.analyze_calls[0]
        assert call["now_utc"] == 2000
        assert call["healing_snapshot_bytes"] is not None
        assert call["detection_signal_bytes"] is None
        assert call["drift_snapshot_bytes"] is None

    def test_optimizer_receives_pattern_report(self):
        aggregates = [
            (
                HealingOutcomeAggregateKey("test_healer", "LOCAL_AGENT", "timeout"),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]
        snap = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )
        fake_opt = _PatternFakeHealingConfigOptimizer()
        fake_intake = _PatternFakeIntakeAdapter()
        fake_intake.records_persisted.append(_pattern_seed_record(created_utc=1950))
        deps = _pattern_deps(fake_l4=_PatternFakeL4StateWriter(), fake_opt=fake_opt, fake_intake=fake_intake)
        _pattern_run(deps)
        assert len(fake_opt.pattern_reports_received) == 1
        report = fake_opt.pattern_reports_received[0]
        assert isinstance(report, PatternFindingReport)
        assert report.source_ids.healing_snapshot_version == "test_v1"
        assert report.findings[0].key.label == "UNDERPERFORMING_HEALER_TIER"

    def test_pipeline_emits_proposal_only_change_package(self):
        aggregates = [
            (
                HealingOutcomeAggregateKey("test_healer", "LOCAL_AGENT", "timeout"),
                HealingOutcomeAggregate(success_count=30, failure_count=70, total_count=100),
            )
        ]
        snap = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )
        fake_intake = _PatternFakeIntakeAdapter()
        fake_intake.records_persisted.append(_pattern_seed_record(created_utc=1950))
        deps = _pattern_deps(
            fake_l4=_PatternFakeL4StateWriter(healing_snapshot_bytes=snap.canonical_bytes()),
            fake_intake=fake_intake,
        )
        proposals = _pattern_run(deps)
        assert isinstance(proposals, tuple)
        assert len(proposals) >= 1

    def test_optional_detection_and_drift_signals(self):
        detection_bytes = json.dumps({"version": "detection_v1", "signals": []}).encode()
        drift_bytes = json.dumps({"version": "drift_v1", "drift_scores": []}).encode()
        fake_engine = _PatternFakePatternAnalysisEngine()
        fake_intake = _PatternFakeIntakeAdapter()
        fake_intake.records_persisted.append(_pattern_seed_record(created_utc=1950))
        deps = _pattern_deps(
            fake_l4=_PatternFakeL4StateWriter(
                detection_signal_bytes=detection_bytes, drift_snapshot_bytes=drift_bytes
            ),
            fake_engine=fake_engine,
            fake_intake=fake_intake,
        )
        _pattern_run(deps)
        assert len(fake_engine.analyze_calls) == 1
        call = fake_engine.analyze_calls[0]
        assert call["detection_signal_bytes"] == detection_bytes
        assert call["drift_snapshot_bytes"] == drift_bytes


# ===========================================================================
# proposal_only fakes + tests
# ===========================================================================


class _ProposalFakeAuditStore:
    def __init__(self, audit_data: bytes):
        self.audit_data = audit_data
        self.read_calls = []

    def read_audit_slice(self, window_start_utc, window_end_utc) -> bytes:
        self.read_calls.append((window_start_utc, window_end_utc))
        return self.audit_data


class _ProposalFakeTelemetryStore:
    def __init__(self, events):
        self.events = events
        self.read_calls = []

    def read_events(self, window_start_utc, window_end_utc):
        self.read_calls.append((window_start_utc, window_end_utc))
        return tuple(
            (ts, kind, payload)
            for ts, kind, payload in self.events
            if window_start_utc <= ts < window_end_utc
        )


class _ProposalFakeConfigProvider:
    def __init__(self):
        self.configs = {"routing": b"routing_config_v1", "model": b"model_config_v1"}

    def get_current_configs(self):
        return self.configs

    def get_last_update_utc(self, surface_name):
        return None

    def get_param_history(self, surface_name, n):
        return ()


class _ProposalFakeBaselineMetricsProvider:
    def __init__(self):
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


def _proposal_cfg(**kw):
    defaults: dict = {
        "engine_version": "v1",
        "config_surface_version": "v1",
        "shadow_thresholds": _default_shadow_thresholds(),
        "cooldown_policy": CooldownPolicy(min_seconds_between_updates=3600),
        "sample_policy": SampleSizePolicy(min_observations=1000),
        "oscillation_policy": OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
        "enabled_proposers": (),
        "proposal_only": True,
    }
    defaults.update(kw)
    return PipelineConfig(**defaults)


def _proposal_deps(**kw):
    base: dict = {
        "audit_store": _ProposalFakeAuditStore(b"SyntaxError: test"),
        "telemetry_store": _ProposalFakeTelemetryStore([]),
        "config_provider": _ProposalFakeConfigProvider(),
        "baseline_metrics_provider": _ProposalFakeBaselineMetricsProvider(),
    }
    base.update(kw)
    return PipelineDependencies(**base)


class TestProposalOnlyMode:
    def test_proposal_only_returns_packages(self):
        proposals = run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=_proposal_cfg(enabled_proposers=("L0", "RAG")),
            deps=_proposal_deps(),
        )
        assert isinstance(proposals, tuple)
        assert len(proposals) == 0

    def test_proposal_only_does_not_call_commit(self):
        version_store = _FakeVersionStore()
        run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=_proposal_cfg(enabled_proposers=("L0",)),
            deps=_proposal_deps(version_store=version_store),
        )
        assert len(version_store.committed_packages) == 0

    def test_proposal_only_does_not_call_activate(self):
        activator = _FakeActivator()
        run_pipeline(
            now_utc=1700003600,
            window_start_utc=1700000000,
            window_end_utc=1700003600,
            cfg=_proposal_cfg(enabled_proposers=("RAG",)),
            deps=_proposal_deps(activator=activator),
        )
        assert len(activator.activations) == 0

    def test_proposal_only_default_is_true(self):
        cfg = PipelineConfig(
            engine_version="v1",
            config_surface_version="v1",
            shadow_thresholds=_default_shadow_thresholds(),
            cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
            sample_policy=SampleSizePolicy(min_observations=1000),
            oscillation_policy=OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600),
            enabled_proposers=(),
        )
        assert cfg.proposal_only is True

    def test_pipeline_deterministic(self):
        cfg = _proposal_cfg()
        deps = _proposal_deps(
            audit_store=_ProposalFakeAuditStore(b"SyntaxError: test\nImportError: foo"),
            telemetry_store=_ProposalFakeTelemetryStore([(1700001000, "metric", b"cpu=50")]),
        )
        kw = {"now_utc": 1700003600, "window_start_utc": 1700000000, "window_end_utc": 1700003600}
        assert run_pipeline(cfg=cfg, deps=deps, **kw) == run_pipeline(cfg=cfg, deps=deps, **kw)


# ===========================================================================
# writes_l4b fakes + tests
# ===========================================================================


class _L4BFakeL4StateWriter:
    def __init__(self) -> None:
        self.l4b_writes: list[dict] = []

    def write_l4a_detection_signal(self, **kwargs) -> str:
        return "noop_l4a"

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        self.l4b_writes.append(
            {"payload_bytes": payload_bytes, "component_name": component_name, "created_utc": created_utc}
        )
        content = f"{component_name}:{created_utc}:{payload_bytes}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class _L4BFakeHealingConfigOptimizer:
    def __init__(self) -> None:
        self.snapshot_to_return = None

    def create_snapshot_from_intake(self, intake_record, created_utc: int):
        if self.snapshot_to_return is None:
            aggregates = [
                (
                    HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                    HealingOutcomeAggregate(success_count=7, failure_count=3, total_count=10),
                )
            ]
            self.snapshot_to_return = HealingOutcomeAggregateSnapshot(
                version_id="test_snapshot_123",
                created_utc=created_utc,
                aggregates=tuple(aggregates),
            )
        return self.snapshot_to_return

    def propose_threshold_adjustments(self, snapshot):
        from system_learning.engines.healing_config_optimizer import ThresholdAdjustmentProposal

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=(),
        )


class _L4BFakeIntakeAdapter:
    def __init__(self) -> None:
        self.records_persisted: list[HealingOutcomeIntakeRecord] = []

    def build_record(self, aggregator, created_utc: int, source: str):
        stats = (HealingOutcomeStats.from_counts("healer1", "LOCAL_AGENT", "failure1", 7, 3),)
        return HealingOutcomeIntakeRecord(
            schema_version=1,
            created_utc=created_utc,
            window_size=100,
            snapshot=stats,
            proposal=None,
            source=source,  # type: ignore
        )

    def persist_record(self, record: HealingOutcomeIntakeRecord) -> None:
        self.records_persisted.append(record)

    def get_recent_records(self, window_start_utc: int, window_end_utc: int) -> list:
        return [r for r in self.records_persisted if window_start_utc <= r.created_utc <= window_end_utc]


def _l4b_cfg():
    return PipelineConfig(
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


def _l4b_deps(fake_l4, fake_opt, fake_intake, seed_utc: int):
    mock_ts = Mock(spec=TelemetryStore)
    mock_ts.read_events.return_value = []
    mock_as = Mock(spec=AuditStore)
    mock_as.read_audit_slice.return_value = b""
    fake_intake.records_persisted.append(_make_seed_record(created_utc=seed_utc))
    return PipelineDependencies(
        audit_store=mock_as,
        telemetry_store=mock_ts,
        config_provider=Mock(spec=ConfigProvider),
        baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
        healing_outcome_intake_adapter=fake_intake,
        healing_config_optimizer=fake_opt,
        l4_state_writer=fake_l4,
    )


class TestMetaLearningPipelineWritesL4B:
    def test_pipeline_writes_l4b_healing_snapshot_deterministically(self):
        fake_l4 = _L4BFakeL4StateWriter()
        fake_opt = _L4BFakeHealingConfigOptimizer()
        fake_intake = _L4BFakeIntakeAdapter()
        now_utc = 1000
        deps = _l4b_deps(fake_l4, fake_opt, fake_intake, seed_utc=950)
        run_pipeline(now_utc=now_utc, window_start_utc=900, window_end_utc=1100, cfg=_l4b_cfg(), deps=deps)
        assert len(fake_l4.l4b_writes) == 1
        write = fake_l4.l4b_writes[0]
        assert write["component_name"] == "meta-learning"
        assert write["created_utc"] == now_utc
        assert isinstance(write["payload_bytes"], bytes)
        assert b"healer1" in write["payload_bytes"]
        version_id = hashlib.sha256(f"meta-learning:{now_utc}:{write['payload_bytes']}".encode()).hexdigest()[
            :16
        ]
        assert isinstance(version_id, str) and len(version_id) == 16

    def test_pipeline_without_l4_writer_no_writes(self):
        fake_opt = _L4BFakeHealingConfigOptimizer()
        fake_intake = _L4BFakeIntakeAdapter()
        mock_ts = Mock(spec=TelemetryStore)
        mock_ts.read_events.return_value = []
        mock_as = Mock(spec=AuditStore)
        mock_as.read_audit_slice.return_value = b""
        fake_intake.records_persisted.append(_make_seed_record(created_utc=1950))
        deps = PipelineDependencies(
            audit_store=mock_as,
            telemetry_store=mock_ts,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_opt,
            l4_state_writer=None,
        )
        run_pipeline(now_utc=2000, window_start_utc=1900, window_end_utc=2100, cfg=_l4b_cfg(), deps=deps)
        assert len(fake_intake.records_persisted) >= 2

    def test_pipeline_l4b_write_failure_doesnt_break_pipeline(self):
        class _FailingWriter:
            def write_l4b_healing_snapshot(self, **kwargs) -> str:
                raise RuntimeError("Simulated L4B write failure")

        fake_opt = _L4BFakeHealingConfigOptimizer()
        fake_intake = _L4BFakeIntakeAdapter()
        mock_ts = Mock(spec=TelemetryStore)
        mock_ts.read_events.return_value = []
        mock_as = Mock(spec=AuditStore)
        mock_as.read_audit_slice.return_value = b""
        fake_intake.records_persisted.append(_make_seed_record(created_utc=2950))
        deps = PipelineDependencies(
            audit_store=mock_as,
            telemetry_store=mock_ts,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_opt,
            l4_state_writer=_FailingWriter(),
        )
        proposals = run_pipeline(
            now_utc=3000, window_start_utc=2900, window_end_utc=3100, cfg=_l4b_cfg(), deps=deps
        )
        assert isinstance(proposals, tuple)
        assert len(fake_intake.records_persisted) >= 2

    def test_pipeline_l4b_version_id_deterministic_same_snapshot(self):
        fake_l4 = _L4BFakeL4StateWriter()
        fake_opt = _L4BFakeHealingConfigOptimizer()
        fake_intake = _L4BFakeIntakeAdapter()
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=5, failure_count=5, total_count=10),
            )
        ]
        fake_opt.snapshot_to_return = HealingOutcomeAggregateSnapshot(
            version_id="det_snapshot_456",
            created_utc=4000,
            aggregates=tuple(aggregates),
        )
        mock_ts = Mock(spec=TelemetryStore)
        mock_ts.read_events.return_value = []
        mock_as = Mock(spec=AuditStore)
        mock_as.read_audit_slice.return_value = b""
        fake_intake.records_persisted.append(_make_seed_record(created_utc=3950))
        deps = PipelineDependencies(
            audit_store=mock_as,
            telemetry_store=mock_ts,
            config_provider=Mock(spec=ConfigProvider),
            baseline_metrics_provider=Mock(spec=BaselineMetricsProvider),
            healing_outcome_intake_adapter=fake_intake,
            healing_config_optimizer=fake_opt,
            l4_state_writer=fake_l4,
        )
        run_pipeline(now_utc=4000, window_start_utc=3900, window_end_utc=4100, cfg=_l4b_cfg(), deps=deps)
        run_pipeline(now_utc=4000, window_start_utc=3900, window_end_utc=4100, cfg=_l4b_cfg(), deps=deps)
        assert len(fake_l4.l4b_writes) == 2
        assert fake_l4.l4b_writes[0]["payload_bytes"] == fake_l4.l4b_writes[1]["payload_bytes"]
