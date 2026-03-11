"""Tests for SystemLearningMemoryBridge and all wired system_learning engines.

Covers:
  - SystemLearningMemoryBridge instantiation and fallback resilience
  - persist_healing_success_rate / restore_healing_success_rates
  - persist_rca_findings / query_rca_pattern_frequency
  - persist_drift_summary / query_drift_history
  - persist_policy_recommendation / query_policy_recommendations
  - persist_healing_aggregate_snapshot
  - persist_failure_pattern / query_failure_patterns
  - HealingSuccessRateStore._maybe_persist_to_mcp + restore_from_memory
  - analyze_failures_and_persist (RCA wrapper)
  - ShadowDriftAnalyzer MCP persistence in _emit_to_registry
  - MemoryAwarePolicyRecommendationEngine persistence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

from system_learning.adapters.system_learning_memory_bridge import (
    SystemLearningMemoryBridge,
    get_sl_memory_bridge,
)
from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
from system_learning.engines.rca_engine import analyze_failures, analyze_failures_and_persist

# ---------------------------------------------------------------------------
# Helper stubs
# ---------------------------------------------------------------------------


@dataclass
class _MockBridge:
    """Minimal mock of GraphMemoryBridge for unit tests."""

    is_available: bool = True
    created_entities: list = field(default_factory=list)
    created_relations: list = field(default_factory=list)
    observations_added: list = field(default_factory=list)
    search_returns: list = field(default_factory=list)

    def create_agent_entity(self, agent_name: str, agent_type: str, observations: list) -> None:
        self.created_entities.append({"name": agent_name, "type": agent_type, "observations": observations})

    def create_relation(self, from_name: str, to_name: str, relation_type: str) -> None:
        self.created_relations.append((from_name, to_name, relation_type))

    def add_observation(self, entity_name: str, observation: str) -> bool:
        self.observations_added.append((entity_name, observation))
        return True

    def search_entities(self, query: str) -> list:
        return self.search_returns


@dataclass(frozen=True)
class _MockRCAFinding:
    category: str
    signature: str
    count: int
    evidence_hash: str = "deadbeef12345678"


@dataclass
class _MockRCAReport:
    findings: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class _MockDriftSummary:
    profile_id: str = "profile_test"
    batch_size: int = 32
    mean_cosine: float = 0.95
    p95_cosine: float = 0.93
    drift_flag: bool = False
    drift_score: float = 0.07
    deterministic_digest: str = "cafebabe12345678" * 4
    drift_threshold: float = 0.92


@dataclass(frozen=True)
class _MockPolicyRecommendation:
    profile_id: str = "profile_test"
    recommended_changes: dict = field(default_factory=lambda: {"similarity_cutoff": 0.78})
    rationale: str = "No drift detected"
    confidence_score: float = 0.95
    deterministic_digest: str = "feedface12345678" * 4


@dataclass
class _MockAggKey:
    healer_name: str
    tier: str
    failure_type: str


@dataclass
class _MockAggValue:
    success_count: int
    failure_count: int


@dataclass
class _MockAggSnapshot:
    version_id: str = "v_test_snap"
    created_utc: int = 1_700_000_000
    aggregates: tuple = field(
        default_factory=lambda: (
            (_MockAggKey("HealerA", "L2", "IMPORT"), _MockAggValue(8, 2)),
            (_MockAggKey("HealerB", "L3", "RUNTIME"), _MockAggValue(5, 5)),
        )
    )


# ---------------------------------------------------------------------------
# SystemLearningMemoryBridge — instantiation
# ---------------------------------------------------------------------------


class TestSLMemoryBridgeInit:
    def test_singleton(self):
        a = SystemLearningMemoryBridge.get_instance()
        b = SystemLearningMemoryBridge.get_instance()
        assert a is b

    def test_get_sl_memory_bridge_alias(self):
        bridge = get_sl_memory_bridge()
        assert isinstance(bridge, SystemLearningMemoryBridge)

    def test_is_available_bool(self):
        bridge = SystemLearningMemoryBridge()
        assert isinstance(bridge.is_available, bool)

    def test_no_exception_when_mcp_unavailable(self):
        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge._load_bridge",
            return_value=None,
        ):
            bridge = SystemLearningMemoryBridge()
            assert not bridge.is_available


# ---------------------------------------------------------------------------
# persist_healing_success_rate / restore_healing_success_rates
# ---------------------------------------------------------------------------


class TestHealingSuccessRatePersistence:
    def _bridge_with_mock(self) -> tuple[SystemLearningMemoryBridge, _MockBridge]:
        mock_gmb = _MockBridge()
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = mock_gmb
        return bridge, mock_gmb

    def test_persist_rate_creates_entity(self):
        bridge, mock_gmb = self._bridge_with_mock()
        result = bridge.persist_healing_success_rate("IMPORT_ERROR", rate=0.87, count=42)
        assert result is True
        assert len(mock_gmb.created_entities) == 1
        entity = mock_gmb.created_entities[0]
        assert entity["type"] == SystemLearningMemoryBridge.ENTITY_TYPE_HEALING_RATE
        obs = entity["observations"]
        assert any("IMPORT_ERROR" in o for o in obs)
        assert any("0.870000" in o for o in obs)
        assert any("42" in o for o in obs)

    def test_persist_rate_no_bridge_returns_false(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        result = bridge.persist_healing_success_rate("ERR", rate=0.5, count=10)
        assert result is False

    def test_persist_all_rates_caps_at_max(self):
        bridge, mock_gmb = self._bridge_with_mock()
        rates = {f"ERR_{i}": 0.5 + i * 0.01 for i in range(100)}
        counts = dict.fromkeys(rates, 10)
        persisted = bridge.persist_all_healing_rates(rates, counts)
        assert persisted == 50  # capped at _MAX_SIGNATURES=50

    def test_restore_rates_parses_observations(self):
        bridge, mock_gmb = self._bridge_with_mock()
        mock_gmb.search_returns = [
            {
                "name": "SLHealRate_abc123",
                "observations": [
                    "error_signature=IMPORT_ERROR",
                    "rate=0.870000",
                    "count=42",
                    "ts=",
                ],
            }
        ]
        restored = bridge.restore_healing_success_rates()
        assert "IMPORT_ERROR" in restored
        rate, count = restored["IMPORT_ERROR"]
        assert abs(rate - 0.87) < 1e-5
        assert count == 42

    def test_restore_rates_no_bridge_returns_empty(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.restore_healing_success_rates() == {}

    def test_restore_rates_tolerates_malformed_observations(self):
        bridge, mock_gmb = self._bridge_with_mock()
        mock_gmb.search_returns = [
            {"name": "SLHealRate_xyz", "observations": ["bad_obs", "rate=not_a_float"]},
        ]
        restored = bridge.restore_healing_success_rates()
        assert restored == {}


# ---------------------------------------------------------------------------
# persist_rca_findings / query_rca_pattern_frequency
# ---------------------------------------------------------------------------


class TestRCAPersistence:
    def _bridge_with_mock(self) -> tuple[SystemLearningMemoryBridge, _MockBridge]:
        mock_gmb = _MockBridge()
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = mock_gmb
        return bridge, mock_gmb

    def test_persist_rca_report_creates_report_entity(self):
        bridge, mock_gmb = self._bridge_with_mock()
        report = _MockRCAReport(
            findings=(
                _MockRCAFinding("IMPORT", "ModuleNotFoundError", 3),
                _MockRCAFinding("RUNTIME", "AttributeError", 1),
            )
        )
        result = bridge.persist_rca_findings("snap_001", report, window_start=0, window_end=100)
        assert result is True
        types = [e["type"] for e in mock_gmb.created_entities]
        assert SystemLearningMemoryBridge.ENTITY_TYPE_RCA_REPORT in types
        assert SystemLearningMemoryBridge.ENTITY_TYPE_RCA_FINDING in types

    def test_persist_rca_creates_relations(self):
        bridge, mock_gmb = self._bridge_with_mock()
        report = _MockRCAReport(findings=(_MockRCAFinding("SYNTAX", "SyntaxError", 2),))
        bridge.persist_rca_findings("snap_002", report)
        assert any(r[2] == SystemLearningMemoryBridge.RELATION_TRIGGERED for r in mock_gmb.created_relations)

    def test_persist_rca_no_bridge_returns_false(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.persist_rca_findings("s", _MockRCAReport()) is False

    def test_query_rca_no_bridge_returns_empty(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.query_rca_pattern_frequency() == []

    def test_query_rca_with_category_filter(self):
        bridge, mock_gmb = self._bridge_with_mock()
        mock_gmb.search_returns = [{"name": "SLRCAFinding_IMPORT_abc", "observations": []}]
        result = bridge.query_rca_pattern_frequency("IMPORT")
        assert len(result) == 1

    def test_analyze_failures_and_persist_returns_same_report(self):
        """analyze_failures_and_persist must produce same result as analyze_failures."""
        audit = b"ModuleNotFoundError: No module named 'foo'\nImportError: cannot import bar"
        report_plain = analyze_failures("snap_base", audit, 0, 1000)
        report_persist = analyze_failures_and_persist("snap_base", audit, 0, 1000)
        plain_findings = {(f.category, f.signature) for f in report_plain.findings}
        persist_findings = {(f.category, f.signature) for f in report_persist.findings}
        assert plain_findings == persist_findings

    def test_analyze_failures_and_persist_is_resilient(self):
        """analyze_failures_and_persist must not raise even if MCP is down."""
        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            side_effect=RuntimeError("MCP down"),
        ):
            SystemLearningMemoryBridge._instance = None
            audit = b"SyntaxError: invalid syntax"
            report = analyze_failures_and_persist("snap_resilient", audit, 0, 500)
            SystemLearningMemoryBridge._instance = None
        assert report is not None


# ---------------------------------------------------------------------------
# persist_drift_summary / query_drift_history
# ---------------------------------------------------------------------------


class TestDriftPersistence:
    def _bridge_with_mock(self) -> tuple[SystemLearningMemoryBridge, _MockBridge]:
        mock_gmb = _MockBridge()
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = mock_gmb
        return bridge, mock_gmb

    def test_persist_drift_creates_entity(self):
        bridge, mock_gmb = self._bridge_with_mock()
        summary = _MockDriftSummary()
        result = bridge.persist_drift_summary(summary, ts="1700000000")
        assert result is True
        entity = mock_gmb.created_entities[0]
        assert entity["type"] == SystemLearningMemoryBridge.ENTITY_TYPE_DRIFT
        obs = entity["observations"]
        assert any("profile_test" in o for o in obs)
        assert any("drift_flag=False" in o for o in obs)

    def test_persist_drift_flag_true(self):
        bridge, mock_gmb = self._bridge_with_mock()
        summary = _MockDriftSummary(drift_flag=True, drift_score=0.15)
        result = bridge.persist_drift_summary(summary)
        assert result is True
        obs = mock_gmb.created_entities[0]["observations"]
        assert any("drift_flag=True" in o for o in obs)

    def test_persist_drift_no_bridge_returns_false(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.persist_drift_summary(_MockDriftSummary()) is False

    def test_query_drift_no_bridge_returns_empty(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.query_drift_history() == []

    def test_shadow_drift_analyzer_emits_to_mcp(self):
        """ShadowDriftAnalyzer.analyze_batch should call persist_drift_summary."""
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        called = []
        mock_bridge_instance = MagicMock()
        mock_bridge_instance.persist_drift_summary = lambda s: called.append(s) or True

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            return_value=mock_bridge_instance,
        ):
            SystemLearningMemoryBridge._instance = None
            analyzer = ShadowDriftAnalyzer()
            records = [{"primary_shadow_cosine": 0.95}] * 10
            analyzer.analyze_batch(shadow_records=records, profile_id="p1", now_utc=1000)
            SystemLearningMemoryBridge._instance = None

        assert len(called) == 1
        assert called[0].profile_id == "p1"


# ---------------------------------------------------------------------------
# persist_policy_recommendation / query_policy_recommendations
# ---------------------------------------------------------------------------


class TestPolicyRecommendationPersistence:
    def _bridge_with_mock(self) -> tuple[SystemLearningMemoryBridge, _MockBridge]:
        mock_gmb = _MockBridge()
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = mock_gmb
        return bridge, mock_gmb

    def test_persist_policy_rec_creates_entity(self):
        bridge, mock_gmb = self._bridge_with_mock()
        rec = _MockPolicyRecommendation()
        result = bridge.persist_policy_recommendation(rec, ts="1700000001")
        assert result is True
        entity = mock_gmb.created_entities[0]
        assert entity["type"] == SystemLearningMemoryBridge.ENTITY_TYPE_POLICY_REC
        obs = entity["observations"]
        assert any("applied=False" in o for o in obs)
        assert any("profile_test" in o for o in obs)

    def test_persist_policy_rec_applied_flag(self):
        bridge, mock_gmb = self._bridge_with_mock()
        rec = _MockPolicyRecommendation()
        bridge.persist_policy_recommendation(rec, applied=True)
        obs = mock_gmb.created_entities[0]["observations"]
        assert any("applied=True" in o for o in obs)

    def test_mark_recommendation_applied(self):
        bridge, mock_gmb = self._bridge_with_mock()
        bridge.mark_recommendation_applied("SLPolicyRec_abc123")
        assert len(mock_gmb.observations_added) == 1
        assert mock_gmb.observations_added[0] == ("SLPolicyRec_abc123", "applied=true")

    def test_query_policy_recs_applied_only_filter(self):
        bridge, mock_gmb = self._bridge_with_mock()
        mock_gmb.search_returns = [
            {"name": "rec_1", "observations": ["applied=true", "profile_id=p1"]},
            {"name": "rec_2", "observations": ["applied=False", "profile_id=p1"]},
        ]
        results = bridge.query_policy_recommendations(applied_only=True)
        assert len(results) == 1
        assert results[0]["name"] == "rec_1"

    def test_memory_aware_engine_persists(self):
        """MemoryAwarePolicyRecommendationEngine persists each recommendation."""
        from system_learning.engines.policy_recommendation_engine import (
            MemoryAwarePolicyRecommendationEngine,
        )
        from system_learning.engines.retrieval_profile import RetrievalProfile

        called = []
        mock_bridge_instance = MagicMock()
        mock_bridge_instance.persist_policy_recommendation = lambda rec, ts="": called.append(rec) or True

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            return_value=mock_bridge_instance,
        ):
            SystemLearningMemoryBridge._instance = None
            engine = MemoryAwarePolicyRecommendationEngine()
            profile = RetrievalProfile.create_default()
            drift = _MockDriftSummary(drift_flag=False, drift_score=0.02)
            engine.generate_recommendation(drift_summary=drift, active_profile=profile, now_utc=1_700_000_000)
            SystemLearningMemoryBridge._instance = None

        assert len(called) == 1

    def test_memory_aware_engine_resilient(self):
        """MemoryAwarePolicyRecommendationEngine still returns recommendation on MCP failure."""
        from system_learning.engines.policy_recommendation_engine import (
            MemoryAwarePolicyRecommendationEngine,
        )
        from system_learning.engines.retrieval_profile import RetrievalProfile

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            side_effect=RuntimeError("MCP down"),
        ):
            SystemLearningMemoryBridge._instance = None
            engine = MemoryAwarePolicyRecommendationEngine()
            profile = RetrievalProfile.create_default()
            drift = _MockDriftSummary(drift_flag=True, drift_score=0.15)
            rec = engine.generate_recommendation(
                drift_summary=drift, active_profile=profile, now_utc=1_700_000_001
            )
            SystemLearningMemoryBridge._instance = None
        assert rec is not None


# ---------------------------------------------------------------------------
# persist_healing_aggregate_snapshot
# ---------------------------------------------------------------------------


class TestAggregateSnapshotPersistence:
    def _bridge_with_mock(self) -> tuple[SystemLearningMemoryBridge, _MockBridge]:
        mock_gmb = _MockBridge()
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = mock_gmb
        return bridge, mock_gmb

    def test_persist_aggregate_snapshot_creates_entity(self):
        bridge, mock_gmb = self._bridge_with_mock()
        snap = _MockAggSnapshot()
        result = bridge.persist_healing_aggregate_snapshot(snap)
        assert result is True
        entity = mock_gmb.created_entities[0]
        assert entity["type"] == SystemLearningMemoryBridge.ENTITY_TYPE_AGGREGATE
        obs = entity["observations"]
        assert any("aggregate_count=2" in o for o in obs)
        assert any("v_test_snap" in o for o in obs)

    def test_persist_aggregate_no_bridge_returns_false(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.persist_healing_aggregate_snapshot(_MockAggSnapshot()) is False


# ---------------------------------------------------------------------------
# persist_failure_pattern / query_failure_patterns
# ---------------------------------------------------------------------------


class TestFailurePatternPersistence:
    def _bridge_with_mock(self) -> tuple[SystemLearningMemoryBridge, _MockBridge]:
        mock_gmb = _MockBridge()
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = mock_gmb
        return bridge, mock_gmb

    def test_persist_failure_pattern_creates_entity(self):
        bridge, mock_gmb = self._bridge_with_mock()
        result = bridge.persist_failure_pattern(
            "abc123def456abc1",
            "IMPORT_LOOP cluster",
            "feed1234",
            member_count=42,
        )
        assert result is True
        entity = mock_gmb.created_entities[0]
        assert entity["type"] == SystemLearningMemoryBridge.ENTITY_TYPE_PATTERN
        obs = entity["observations"]
        assert any("member_count=42" in o for o in obs)

    def test_query_patterns_no_bridge_returns_empty(self):
        bridge = SystemLearningMemoryBridge.__new__(SystemLearningMemoryBridge)
        bridge._bridge = None
        assert bridge.query_failure_patterns() == []


# ---------------------------------------------------------------------------
# HealingSuccessRateStore integration
# ---------------------------------------------------------------------------


class TestHealingSuccessRateStoreMCPIntegration:
    def test_maybe_persist_fires_after_min_sample_size(self):
        """_maybe_persist_to_mcp fires when count reaches _MIN_SAMPLE_SIZE."""
        persisted = []
        mock_bridge_instance = MagicMock()
        mock_bridge_instance.persist_healing_success_rate = (
            lambda sig, rate, count: persisted.append((sig, rate, count)) or True
        )

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            return_value=mock_bridge_instance,
        ):
            SystemLearningMemoryBridge._instance = None
            store = HealingSuccessRateStore()
            for _ in range(4):
                store.record_outcome("IMPORT_ERROR", True)
            assert len(persisted) == 0  # below threshold
            store.record_outcome("IMPORT_ERROR", True)
            assert len(persisted) == 1  # exactly at threshold
            SystemLearningMemoryBridge._instance = None

    def test_maybe_persist_does_not_fire_below_threshold(self):
        persisted = []
        mock_bridge_instance = MagicMock()
        mock_bridge_instance.persist_healing_success_rate = lambda *a: persisted.append(a) or True

        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            return_value=mock_bridge_instance,
        ):
            SystemLearningMemoryBridge._instance = None
            store = HealingSuccessRateStore()
            for _ in range(3):
                store.record_outcome("SYNTAX_ERROR", False)
            SystemLearningMemoryBridge._instance = None
        assert len(persisted) == 0

    def test_restore_from_memory_merges_without_overwriting_local(self):
        mock_bridge_instance = MagicMock()
        mock_bridge_instance.restore_healing_success_rates = lambda: {
            "IMPORT_ERROR": (0.9, 100),
            "NEW_ERROR": (0.75, 20),
        }
        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            return_value=mock_bridge_instance,
        ):
            SystemLearningMemoryBridge._instance = None
            store = HealingSuccessRateStore()
            # Seed local data for IMPORT_ERROR
            store._rates["IMPORT_ERROR"] = 0.5
            store._counts["IMPORT_ERROR"] = 10

            merged = store.restore_from_memory()
            assert merged == 1  # only NEW_ERROR merged
            assert store._rates["IMPORT_ERROR"] == 0.5  # unchanged
            assert store._rates["NEW_ERROR"] == 0.75  # restored
            assert store._counts["NEW_ERROR"] == 20
            SystemLearningMemoryBridge._instance = None

    def test_restore_from_memory_resilient_on_mcp_error(self):
        with patch(
            "system_learning.adapters.system_learning_memory_bridge.SystemLearningMemoryBridge.get_instance",
            side_effect=RuntimeError("MCP offline"),
        ):
            SystemLearningMemoryBridge._instance = None
            store = HealingSuccessRateStore()
            merged = store.restore_from_memory()
            SystemLearningMemoryBridge._instance = None
        assert merged == 0
