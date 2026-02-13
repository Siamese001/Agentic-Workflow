"""V15 P7 Wave 7.2.3 — HashMismatchTracker Rollback Escalation Tests.

Proves:
- Single mismatch below threshold does not escalate.
- Repeated mismatches crossing threshold triggers escalation.
- Gateway records mismatch via tracker in rollback path.
"""

from __future__ import annotations

import hashlib
import os
from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
    V15ExecutionGateway,
)
from agentic_core.L0_maintenance.types.v15_p2_types import (
    FixConstraint,
    SurgicalManifest,
)
from agentic_core.L0_maintenance.types.v15_p5_types import HashMismatchTracker


def _make_manifest(trace_id: str = "CC3AL1-00000001") -> SurgicalManifest:
    ast_snippet = "heal(test)"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="TestNode",
        target_layer="L2",
        ast_snippet=ast_snippet,
        serialization_canon="test",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


class TestHashMismatchTrackerUnit:
    """Unit tests for HashMismatchTracker itself."""

    def test_single_mismatch_no_escalation(self):
        tracker = HashMismatchTracker(wave_id="w1")
        escalated = tracker.record_mismatch()
        assert not escalated
        assert tracker.mismatch_count == 1
        assert not tracker.escalated

    def test_threshold_crossed_escalates(self):
        tracker = HashMismatchTracker(wave_id="w1", escalation_threshold=2)
        tracker.record_mismatch()
        escalated = tracker.record_mismatch()
        assert escalated
        assert tracker.escalated
        assert tracker.mismatch_count == 2

    def test_custom_threshold(self):
        tracker = HashMismatchTracker(wave_id="w1", escalation_threshold=5)
        for _ in range(4):
            assert not tracker.record_mismatch()
        assert tracker.record_mismatch()  # 5th triggers
        assert tracker.escalated

    def test_empty_wave_id_raises(self):
        with pytest.raises(ValueError, match="wave_id must be non-empty"):
            HashMismatchTracker(wave_id="")


class TestGatewayHashMismatch:
    """Integration: HashMismatchTracker wired into gateway rollback path."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_tracker_initialized_per_execute(self):
        """Each execute() call creates a fresh HashMismatchTracker."""
        gw = V15ExecutionGateway()
        manifest = _make_manifest()
        gw.execute(
            manifest,
            lambda m: {"status": "ok", "errors": 0},
            lambda: ("a", "b", "c"),
            trace_id="CC3AL1-CCCCCCCC",
        )
        assert gw._mismatch_tracker is not None
        assert gw._mismatch_tracker.wave_id == "CC3AL1-CCCCCCCC"
        assert gw._mismatch_tracker.mismatch_count == 0

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_mismatch_recorded_on_rollback_failure(self):
        """When heal fails and rollback hash doesn't match, tracker records it."""
        gw = V15ExecutionGateway()
        manifest = _make_manifest(trace_id="CC3AL1-DDDDDDDD")

        call_count = [0]

        def _mutating_state_hash():
            call_count[0] += 1
            # Return different hashes on each call to trigger RollbackHashMismatch
            return (f"fs_{call_count[0]}", f"git_{call_count[0]}", f"mem_{call_count[0]}")

        def _failing_heal(m):
            raise RuntimeError("intentional failure")

        result = gw.execute(
            manifest,
            _failing_heal,
            _mutating_state_hash,
            trace_id="CC3AL1-DDDDDDDD",
        )
        assert not result.success
        assert gw._mismatch_tracker is not None
        # Rollback verification should have detected hash mismatch
        assert gw._mismatch_tracker.mismatch_count >= 1

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_escalation_after_repeated_mismatches(self):
        """Two consecutive rollback mismatches should trigger escalation."""
        gw = V15ExecutionGateway()

        call_count = [0]

        def _mutating_state_hash():
            call_count[0] += 1
            return (f"fs_{call_count[0]}", f"git_{call_count[0]}", f"mem_{call_count[0]}")

        def _failing_heal(m):
            raise RuntimeError("intentional failure")

        # First execution — mismatch recorded
        m1 = _make_manifest(trace_id="CC3AL1-EEEE0001")
        gw.execute(m1, _failing_heal, _mutating_state_hash, trace_id="CC3AL1-EEEE0001")

        # Second execution — new tracker per wave, so we need to test
        # the tracker directly for multi-mismatch within a single wave.
        # Gateway creates a new tracker per execute() call.
        tracker = HashMismatchTracker(wave_id="escalation-test", escalation_threshold=2)
        tracker.record_mismatch()
        assert not tracker.escalated
        tracker.record_mismatch()
        assert tracker.escalated
        assert tracker.mismatch_count == 2
