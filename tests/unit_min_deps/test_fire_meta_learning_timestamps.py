"""GAP-A: _fire_meta_learning_intake must use injected now_utc, never timestamp_utc=0."""

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

EXECUTE_SSOT_PATH = (
    Path(__file__).parent.parent.parent / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
)


@pytest.mark.unit_min_deps
class TestFireMetaLearningTimestamps:
    def _make_state_mgr(self, healing_actions=None):
        mgr = MagicMock()
        state = {
            "healing_actions": healing_actions or [],
            "meta_learning": {},
            "apply_proposals": False,
        }
        mgr.state = state
        mgr.update_meta_learning = MagicMock()
        return mgr

    def test_signature_accepts_now_utc_parameter(self):
        """_fire_meta_learning_intake must accept now_utc as a parameter (not read wall-clock internally)."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_fire_meta_learning_intake":
                args = [a.arg for a in node.args.args]
                assert "now_utc" in args, "_fire_meta_learning_intake must declare now_utc parameter"
                return
        pytest.fail("_fire_meta_learning_intake not found in execute_ssot.py")

    def test_no_hardcoded_zero_timestamps_in_source(self):
        """AST: no timestamp_utc=0 or created_utc=0 literals remain in _fire_meta_learning_intake."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)

        # Find _fire_meta_learning_intake function node
        fn_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_fire_meta_learning_intake":
                fn_node = node
                break
        assert fn_node is not None

        # Walk all keyword arguments within that function
        for node in ast.walk(fn_node):
            if isinstance(node, ast.keyword):
                if node.arg in ("timestamp_utc", "created_utc"):
                    # Must not be a literal 0
                    if isinstance(node.value, ast.Constant) and node.value.value == 0:
                        pytest.fail(f"Hardcoded {node.arg}=0 found in _fire_meta_learning_intake")

    def test_created_utc_in_jsonl_not_zero(self):
        """Wave 2 JSONL lines must not contain created_utc: 0 literal in source."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        fn_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_fire_meta_learning_intake":
                fn_node = node
                break
        assert fn_node is not None

        for node in ast.walk(fn_node):
            if isinstance(node, ast.Dict):
                for key, val in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value == "created_utc":
                        if isinstance(val, ast.Constant) and val.value == 0:
                            pytest.fail("Dict literal 'created_utc': 0 found in _fire_meta_learning_intake")

    def test_empty_healing_actions_no_crash(self):
        """Empty healing_actions must not crash _fire_meta_learning_intake."""
        from agentic_core.L0_routing.scripts.execute_ssot import _fire_meta_learning_intake

        mgr = self._make_state_mgr(healing_actions=[])
        # Should not raise
        _fire_meta_learning_intake(mgr, now_utc=12345)

    def test_now_utc_propagated_to_intake_record(self):
        """created_utc on the persisted record must equal the injected now_utc."""
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        injected_ts = 9_000_000

        aggregator = HealingOutcomeAggregator(window_size=1)
        aggregator.ingest(
            HealingOutcomeEvent(
                healer_id="agent_x",
                tier="L5",
                failure_type="TYPE_A",
                success=True,
                timestamp_utc=injected_ts,
            )
        )
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        record = adapter.build_record(aggregator=aggregator, created_utc=injected_ts, source="test")
        adapter.persist_record(record)

        assert store.count() == 1
        assert store.get_records()[0].created_utc == injected_ts
        assert store.get_records()[0].created_utc != 0

    def test_determinism_same_input_same_bytes(self):
        """Same now_utc + same healing event → identical canonical_bytes() across two calls."""
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        fixed_ts = 5_000_000

        def make_record():
            agg = HealingOutcomeAggregator(window_size=1)
            agg.ingest(
                HealingOutcomeEvent(
                    healer_id="det_agent",
                    tier="L0",
                    failure_type="DET_FAIL",
                    success=False,
                    timestamp_utc=fixed_ts,
                )
            )
            store = InMemoryHealingOutcomeIntakeStore()
            adapter = HealingOutcomeIntakeAdapter(store=store)
            rec = adapter.build_record(aggregator=agg, created_utc=fixed_ts, source="test")
            return rec.canonical_bytes()

        assert make_record() == make_record()

    def test_boundary_single_healing_action(self):
        """Single healing action must produce exactly one record with correct timestamp."""
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        ts = 1_000_001
        agg = HealingOutcomeAggregator(window_size=1)
        agg.ingest(
            HealingOutcomeEvent(healer_id="a", tier="L1", failure_type="F", success=True, timestamp_utc=ts)
        )
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        rec = adapter.build_record(aggregator=agg, created_utc=ts, source="test")
        adapter.persist_record(rec)

        assert store.count() == 1
        assert store.get_records()[0].created_utc == ts
        assert store.get_records()[0].created_utc != 0
