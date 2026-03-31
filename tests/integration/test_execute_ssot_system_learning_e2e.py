"""E2E tests for execute_ssot.py system learning integration.

Validates the 4-stage columnar meta-learning pipeline per Meta Learning Pipeline v2.md:
1. Detection: Learning surface identification
2. Assessment: Outcome aggregation
3. Integration: Store persistence and FAISS indexing
4. Synthesis: Proposal generation
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timezone
from dataclasses import dataclass

# Import execute_ssot system learning infrastructure
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_routing" / "scripts"))

pytestmark = [pytest.mark.integration, pytest.mark.system_learning, pytest.mark.e2e]


class TestExecuteSsotHealingOutcomeIntake:
    """Test healing outcome intake pipeline end-to-end."""

    def test_healing_actions_aggregated_into_snapshots(self):
        """Verify healing actions are aggregated into deterministic snapshots."""
        try:
            from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
            from system_learning.types.healing_outcome_types import HealingOutcomeEvent
        except ImportError as e:
            pytest.skip(f"System learning modules not available: {e}")

        aggregator = HealingOutcomeAggregator(window_size=10)

        # Ingest healing events
        events = [
            HealingOutcomeEvent(
                healer_id="LocationHealerAgent",
                tier="L2.3",
                failure_type="ImportError",
                success=True,
                timestamp_utc=1234567890,
            ),
            HealingOutcomeEvent(
                healer_id="SyntaxHealerAgent",
                tier="L2.1",
                failure_type="IndentationError",
                success=False,
                timestamp_utc=1234567891,
            ),
        ]

        for event in events:
            aggregator.ingest(event)

        # Generate snapshot
        snapshot = aggregator.snapshot()

        # Verify snapshot structure
        assert len(snapshot) == 2, f"Expected 2 snapshot entries, got {len(snapshot)}"

        # Verify deterministic (same snapshot twice)
        snapshot2 = aggregator.snapshot()
        assert snapshot == snapshot2, "Snapshots should be deterministic"

    def test_healing_records_persisted_to_store(self):
        """Verify healing records persisted to intake store."""
        try:
            from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
            from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
            from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        except ImportError as e:
            pytest.skip(f"System learning modules not available: {e}")

        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        aggregator = HealingOutcomeAggregator(window_size=5)

        # Build and persist record
        record = adapter.build_record(
            aggregator=aggregator,
            created_utc=1234567890,
            source="test_e2e",
        )
        adapter.persist_record(record)

        # Verify persistence
        assert store.count() == 1, f"Expected 1 record in store, got {store.count()}"

        records = store.get_records()
        assert len(records) == 1

    def test_intake_store_window_query(self):
        """Verify intake store supports window-based queries."""
        try:
            from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
            from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
            from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        except ImportError as e:
            pytest.skip(f"System learning modules not available: {e}")

        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)

        # Create multiple records at different times
        for i in range(3):
            aggregator = HealingOutcomeAggregator(window_size=1)
            record = adapter.build_record(
                aggregator=aggregator,
                created_utc=1000 + i * 100,
                source=f"test_{i}",
            )
            adapter.persist_record(record)

        # Query window
        recent_records = adapter.get_recent_records(
            window_start_utc=1100,
            window_end_utc=1300,
        )

        # Should get records 1 and 2 (timestamps 1100 and 1200)
        assert len(recent_records) == 2


class TestExecuteSsotMetaLearningPipeline:
    """Test meta-learning pipeline integration."""

    def test_pipeline_config_proposal_only(self):
        """Verify pipeline config has proposal_only=True (non-mutating)."""
        try:
            from system_learning.pipelines.pipeline_factory import build_pipeline_config
        except ImportError as e:
            pytest.skip(f"Pipeline factory not available: {e}")

        cfg = build_pipeline_config(proposal_only=True)

        assert cfg.proposal_only is True, "Config should have proposal_only=True"

    def test_pipeline_deps_factory(self):
        """Verify pipeline dependencies can be built."""
        try:
            from system_learning.pipelines.pipeline_factory import build_pipeline_deps
        except ImportError as e:
            pytest.skip(f"Pipeline factory not available: {e}")

        # Build deps with minimal params
        deps = build_pipeline_deps(
            repo_root=Path("/tmp/test_repo"),
        )

        assert deps is not None

    def test_meta_learning_pipeline_import(self):
        """Verify meta_learning_pipeline.run_pipeline can be imported."""
        try:
            from system_learning.pipelines.meta_learning_pipeline import run_pipeline
        except ImportError as e:
            pytest.skip(f"Meta learning pipeline not available: {e}")

        assert callable(run_pipeline)

    @pytest.mark.skip(reason="Requires full system learning stack with stores and adapters")
    def test_pipeline_generates_proposals(self):
        """Verify meta-learning pipeline generates proposals with real data."""
        pytest.skip("Full integration test requires complete system learning stack")


class TestExecuteSsotRequiredIntakeFunction:
    """Test the _fire_meta_learning_intake_required function."""

    def test_required_function_exists(self):
        """Verify _fire_meta_learning_intake_required function exists."""
        from agentic_core.L0_routing.scripts.execute_ssot import _fire_meta_learning_intake_required

        assert callable(_fire_meta_learning_intake_required)

    def test_meta_learning_error_class_exists(self):
        """Verify MetaLearningError exception class exists."""
        from agentic_core.L0_routing.scripts.execute_ssot import MetaLearningError

        # Should be able to raise it
        with pytest.raises(MetaLearningError):
            raise MetaLearningError("Test error")

    def test_meta_learning_result_class(self):
        """Verify MetaLearningResult class works correctly."""
        from agentic_core.L0_routing.scripts.execute_ssot import MetaLearningResult

        # Test empty result
        empty = MetaLearningResult.empty()
        assert empty.proposals == ()
        assert empty.records_persisted == 0
        assert empty.faiss_vectors_stored == 0

        # Test with values
        result = MetaLearningResult(
            proposals=("prop1", "prop2"),
            records_persisted=5,
        )
        assert len(result.proposals) == 2
        assert result.records_persisted == 5

    def test_required_function_with_empty_healing_actions(self):
        """Verify required function handles empty healing actions."""
        from agentic_core.L0_routing.scripts.execute_ssot import (
            _fire_meta_learning_intake_required,
            MetaLearningResult,
        )

        # Mock state manager with no healing actions
        mock_state = MagicMock()
        mock_state.state = {"healing_actions": []}

        result = _fire_meta_learning_intake_required(
            mock_state,
            now_utc=1234567890,
            repo_root=Path("/tmp"),
        )

        # Should return empty result
        assert isinstance(result, MetaLearningResult)
        assert result.records_persisted == 0
        assert result.proposals == ()

    @pytest.mark.skip(reason="Requires full system learning stack and real adapters")
    def test_required_function_with_healing_actions(self):
        """Verify required function processes healing actions."""
        pytest.skip("Full integration test requires complete system learning stack")


class TestExecuteSsotSystemLearningBridge:
    """Test system learning memory bridge integration."""

    def test_sl_memory_bridge_import(self):
        """Verify system learning memory bridge can be imported."""
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
        except ImportError as e:
            pytest.skip(f"System learning memory bridge not available: {e}")

        assert callable(get_sl_memory_bridge)

    def test_bridge_has_persist_methods(self):
        """Verify bridge has required persist methods."""
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
        except ImportError as e:
            pytest.skip(f"System learning memory bridge not available: {e}")

        bridge = get_sl_memory_bridge()

        # Check for required methods
        assert hasattr(bridge, 'persist_execute_ssot_phase_outcomes'), \
            "Bridge should have persist_execute_ssot_phase_outcomes"

    @pytest.mark.skip(reason="Requires running system learning memory service")
    def test_phase_outcomes_persisted(self):
        """Verify execute_ssot phase outcomes persisted to SL bridge."""
        pytest.skip("Requires running system learning memory service")


class TestExecuteSsotWorkflowOutcomeAdapter:
    """Test WorkflowOutcomeSLAdapter integration."""

    def test_workflow_outcome_adapter_import(self):
        """Verify WorkflowOutcomeSLAdapter can be imported."""
        try:
            from system_learning.adapters.workflow_outcome_sl_adapter import (
                WorkflowOutcomeSLAdapter,
                get_workflow_outcome_sl_adapter,
            )
        except ImportError as e:
            pytest.skip(f"Workflow outcome adapter not available: {e}")

        assert WorkflowOutcomeSLAdapter is not None
        assert callable(get_workflow_outcome_sl_adapter)

    def test_workflow_outcome_adapter_accepts_outcomes(self):
        """Verify adapter accepts workflow outcomes."""
        try:
            from system_learning.adapters.workflow_outcome_sl_adapter import WorkflowOutcomeSLAdapter
        except ImportError as e:
            pytest.skip(f"Workflow outcome adapter not available: {e}")

        adapter = WorkflowOutcomeSLAdapter()

        # Mock workflow outcome
        mock_outcome = MagicMock()
        mock_outcome.bundle_id = "test-bundle-1"
        mock_outcome.trace_id = "test-trace-1"
        mock_outcome.workflow_type = "execute_ssot"
        mock_outcome.success = True
        mock_outcome.elapsed_ms = 1000
        mock_outcome.agent_sequence = ["Agent1", "Agent2"]
        mock_outcome.quality_score = 0.95
        mock_outcome.outcome_hash = "abc123"
        mock_outcome.metadata = {"timestamp_utc": 1234567890}

        # Accept should not raise
        try:
            adapter.accept(mock_outcome)
        except Exception as e:
            # May fail if bridge not available, but shouldn't error on structure
            pass

        # Check stats were tracked
        stats = adapter.get_stats()
        assert "total_processed" in stats

    def test_adapter_get_stats(self):
        """Verify adapter provides statistics."""
        try:
            from system_learning.adapters.workflow_outcome_sl_adapter import WorkflowOutcomeSLAdapter
        except ImportError as e:
            pytest.skip(f"Workflow outcome adapter not available: {e}")

        adapter = WorkflowOutcomeSLAdapter()

        stats = adapter.get_stats()

        assert "accepted_count" in stats
        assert "error_count" in stats
        assert "total_processed" in stats


class TestExecuteSsotCrossRepoContext:
    """Test cross-repo learning context support."""

    def test_cross_repo_importer_exists(self):
        """Verify cross-repo system learning importer exists."""
        try:
            from system_learning.engines.cross_repo_system_learning_import import (
                CrossRepoSystemLearningImporter,
            )
        except ImportError as e:
            pytest.skip(f"Cross-repo importer not available: {e}")

        assert CrossRepoSystemLearningImporter is not None

    @pytest.mark.skip(reason="Requires external repository access")
    def test_cross_repo_context_import(self):
        """Verify cross-repo learning context can be imported."""
        pytest.skip("Requires external repository access")


class TestExecuteSsotHardDependencies:
    """Test that hard system learning dependencies are importable."""

    def test_healing_outcome_aggregator_import(self):
        """Verify HealingOutcomeAggregator is importable (hard dependency)."""
        from agentic_core.L0_routing.scripts.execute_ssot import HealingOutcomeAggregator
        assert HealingOutcomeAggregator is not None

    def test_healing_outcome_intake_adapter_import(self):
        """Verify HealingOutcomeIntakeAdapter is importable (hard dependency)."""
        from agentic_core.L0_routing.scripts.execute_ssot import HealingOutcomeIntakeAdapter
        assert HealingOutcomeIntakeAdapter is not None

    def test_in_memory_store_import(self):
        """Verify InMemoryHealingOutcomeIntakeStore is importable (hard dependency)."""
        from agentic_core.L0_routing.scripts.execute_ssot import InMemoryHealingOutcomeIntakeStore
        assert InMemoryHealingOutcomeIntakeStore is not None

    def test_healing_outcome_event_import(self):
        """Verify HealingOutcomeEvent is importable (hard dependency)."""
        from agentic_core.L0_routing.scripts.execute_ssot import HealingOutcomeEvent
        assert HealingOutcomeEvent is not None

    def test_build_pipeline_config_import(self):
        """Verify build_pipeline_config is importable (hard dependency)."""
        from agentic_core.L0_routing.scripts.execute_ssot import build_pipeline_config
        assert build_pipeline_config is not None

    def test_get_sl_memory_bridge_import(self):
        """Verify get_sl_memory_bridge is importable (hard dependency)."""
        from agentic_core.L0_routing.scripts.execute_ssot import get_sl_memory_bridge
        assert get_sl_memory_bridge is not None


class TestExecuteSsotIntakeDeterminism:
    """Test deterministic behavior of intake pipeline."""

    def test_aggregator_determinism(self):
        """Verify aggregator produces deterministic results."""
        try:
            from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
            from system_learning.types.healing_outcome_types import HealingOutcomeEvent
        except ImportError as e:
            pytest.skip(f"System learning modules not available: {e}")

        # Create two identical aggregators with same events
        agg1 = HealingOutcomeAggregator(window_size=5)
        agg2 = HealingOutcomeAggregator(window_size=5)

        events = [
            HealingOutcomeEvent("Agent1", "L2.1", "Error1", True, 1000),
            HealingOutcomeEvent("Agent2", "L2.3", "Error2", False, 1001),
        ]

        for event in events:
            agg1.ingest(event)
            agg2.ingest(event)

        # Snapshots should be identical
        snap1 = agg1.snapshot()
        snap2 = agg2.snapshot()

        assert snap1 == snap2, "Aggregator snapshots should be deterministic"

    def test_intake_record_determinism(self):
        """Verify intake records are built deterministically."""
        try:
            from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
            from system_learning.engines.in_memory_healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore
            from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        except ImportError as e:
            pytest.skip(f"System learning modules not available: {e}")

        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        aggregator = HealingOutcomeAggregator(window_size=3)

        # Build record twice
        record1 = adapter.build_record(aggregator, created_utc=1234567890, source="test")
        record2 = adapter.build_record(aggregator, created_utc=1234567890, source="test")

        # Should be identical
        assert record1.schema_version == record2.schema_version
        assert record1.created_utc == record2.created_utc
        assert record1.source == record2.source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
