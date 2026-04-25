"""W13 tests for ``system_learning.engines.rca_lead_time_tracker``."""

from __future__ import annotations

import pytest

from system_learning.engines.rca_lead_time_tracker import RCALeadTimeTracker
from system_learning.engines.v6_kpi_board import V6KPIBoard, V6KPIName


def test_initial_state_clean():
    t = RCALeadTimeTracker()
    assert t.sample_count == 0
    assert t.open_incident_count == 0
    assert t.p95_lead_time_seconds() == 0.0


def test_proposal_without_closure_returns_none():
    t = RCALeadTimeTracker()
    assert t.mark_proposal_emitted(incident_id="i1", epoch=10.0) is None
    assert t.sample_count == 0


def test_simple_close_then_propose():
    t = RCALeadTimeTracker()
    t.mark_incident_closed(incident_id="i1", epoch=100.0)
    lead = t.mark_proposal_emitted(incident_id="i1", epoch=400.0)
    assert lead == 300.0
    assert t.sample_count == 1


def test_close_consumed_after_proposal():
    t = RCALeadTimeTracker()
    t.mark_incident_closed(incident_id="i1", epoch=0.0)
    t.mark_proposal_emitted(incident_id="i1", epoch=10.0)
    # Second proposal for the same incident has no closure left.
    assert t.mark_proposal_emitted(incident_id="i1", epoch=20.0) is None


def test_p95_nearest_rank():
    t = RCALeadTimeTracker()
    for i in range(20):
        t.mark_incident_closed(incident_id=f"i{i}", epoch=0.0)
        t.mark_proposal_emitted(incident_id=f"i{i}", epoch=float(i + 1))
    # 20 samples sorted: leads = [1..20]. ceil(0.95*20)-1 = ceil(19.0)-1 = 18
    # → leads[18] = 19.0 (nearest-rank p95).
    assert t.p95_lead_time_seconds() == 19.0


def test_max_samples_bounds_memory():
    t = RCALeadTimeTracker(max_samples=5)
    for i in range(20):
        t.mark_incident_closed(incident_id=f"i{i}", epoch=0.0)
        t.mark_proposal_emitted(incident_id=f"i{i}", epoch=float(i + 1))
    assert t.sample_count == 5


def test_clock_skew_clamped_to_zero():
    t = RCALeadTimeTracker()
    t.mark_incident_closed(incident_id="i1", epoch=200.0)
    lead = t.mark_proposal_emitted(incident_id="i1", epoch=100.0)
    assert lead == 0.0


def test_reset():
    t = RCALeadTimeTracker()
    t.mark_incident_closed(incident_id="i1", epoch=0.0)
    t.mark_proposal_emitted(incident_id="i1", epoch=10.0)
    t.reset()
    assert t.sample_count == 0
    assert t.open_incident_count == 0


def test_publish_with_samples():
    t = RCALeadTimeTracker()
    board = V6KPIBoard()
    for i in range(20):
        t.mark_incident_closed(incident_id=f"i{i}", epoch=0.0)
        t.mark_proposal_emitted(incident_id=f"i{i}", epoch=float(i + 1))
    t.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.RCA_TO_PROPOSAL_LEAD_TIME)
    assert sample is not None
    assert sample.value == pytest.approx(19.0)
    assert sample.metadata["sample_size"] == 20


def test_publish_with_no_samples():
    t = RCALeadTimeTracker()
    board = V6KPIBoard()
    t.publish_kpi_sample(board)
    sample = board.latest(V6KPIName.RCA_TO_PROPOSAL_LEAD_TIME)
    assert sample.value == 0.0
    assert sample.metadata["sample_size"] == 0


def test_publish_does_not_raise_on_invalid_board():
    t = RCALeadTimeTracker()
    t.mark_incident_closed(incident_id="i1", epoch=0.0)
    t.mark_proposal_emitted(incident_id="i1", epoch=10.0)
    t.publish_kpi_sample(object())  # must not raise


def test_empty_incident_id_no_op():
    t = RCALeadTimeTracker()
    t.mark_incident_closed(incident_id="", epoch=10.0)
    assert t.open_incident_count == 0
    assert t.mark_proposal_emitted(incident_id="", epoch=20.0) is None
