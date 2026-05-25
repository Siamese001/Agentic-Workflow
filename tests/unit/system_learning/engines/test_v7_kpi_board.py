"""Tests for ``system_learning.engines.v7_kpi_board``."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.v7_kpi_board import (
    ALL_KPI_SPECS,
    UnifiedKPIBoard,
    V6KPIName,
    V6KPISample,
    V7_KPI_SPECS,
    V7KPIName,
    V7KPISample,
    evaluate_sample,
)


def test_v7_enum_disjoint_from_v6():
    v6_values = {n.value for n in V6KPIName}
    v7_values = {n.value for n in V7KPIName}
    assert v6_values.isdisjoint(v7_values), "v6/v7 KPI names must not overlap"


def test_every_v7_name_has_spec():
    for name in V7KPIName:
        assert name in V7_KPI_SPECS, f"{name} missing spec"


def test_all_kpi_specs_includes_both_namespaces():
    for n in V6KPIName:
        assert n.value in ALL_KPI_SPECS
    for n in V7KPIName:
        assert n.value in ALL_KPI_SPECS


def test_unified_board_accepts_v6_sample():
    board = UnifiedKPIBoard()
    sample = V6KPISample(
        name=V6KPIName.TRACE_INGEST_FRESHNESS,
        value=300.0, timestamp=0.0, source="test", metadata={},
    )
    board.record(sample)
    assert board.latest(V6KPIName.TRACE_INGEST_FRESHNESS) is sample


def test_unified_board_accepts_v7_sample():
    board = UnifiedKPIBoard()
    sample = V7KPISample(
        name=V7KPIName.EVIDENCE_FIELD_COMPLETENESS,
        value=0.995, timestamp=0.0, source="test", metadata={},
    )
    board.record(sample)
    # Lookup by the v7 enum
    assert board.latest(V7KPIName.EVIDENCE_FIELD_COMPLETENESS) is sample  # type: ignore[arg-type]


def test_unified_board_rejects_unknown_name():
    board = UnifiedKPIBoard()
    class FakeName:
        value = "totally_made_up_kpi"
    class FakeSample:
        name = FakeName()
        value = 0.0
        timestamp = 0.0
        source = "test"
        metadata: dict = {}
    with pytest.raises(ValueError, match="unknown KPI name"):
        board.record(FakeSample())


def test_unified_board_rejects_missing_name():
    board = UnifiedKPIBoard()
    class NoName: ...
    with pytest.raises(ValueError, match="missing .name"):
        board.record(NoName())


def test_evaluate_sample_works_with_v7_spec():
    # observer_law_violation_count: EQ 0
    sample = V7KPISample(
        name=V7KPIName.OBSERVER_LAW_VIOLATION_COUNT,
        value=0.0, timestamp=0.0, source="test", metadata={},
    )
    spec = V7_KPI_SPECS[V7KPIName.OBSERVER_LAW_VIOLATION_COUNT]
    status = evaluate_sample(sample, spec)  # type: ignore[arg-type]
    assert status.is_green is True


def test_evaluate_sample_red_when_v7_threshold_breached():
    sample = V7KPISample(
        name=V7KPIName.HARD_CONSTRAINT_REMEDIATE_ATTEMPTS,
        value=3.0, timestamp=0.0, source="test", metadata={},
    )
    spec = V7_KPI_SPECS[V7KPIName.HARD_CONSTRAINT_REMEDIATE_ATTEMPTS]
    status = evaluate_sample(sample, spec)  # type: ignore[arg-type]
    assert status.is_green is False


def test_v7_spec_count_matches_enum():
    assert len(V7_KPI_SPECS) == len(list(V7KPIName))


def test_total_kpi_count():
    # 11 v6 + ~40 v7 = 50+ total. Sanity guard.
    assert len(ALL_KPI_SPECS) >= 40
