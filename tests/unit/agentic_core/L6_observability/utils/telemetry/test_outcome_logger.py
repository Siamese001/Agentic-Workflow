"""Compatibility smoke tests for the current L6 Observability outcome logger."""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.enforcement.outcome_logger import (
    OutcomeLogger,
    OutcomeRecord,
    OutcomeReconciler,
)


@pytest.mark.unit
class TestOutcomeLogger:
    """Test the current deterministic OutcomeLogger implementation."""

    def test_outcome_logger_initialization(self) -> None:
        logger = OutcomeLogger()

        assert logger is not None
        assert hasattr(logger, "append")
        assert hasattr(logger, "records")

    def test_append_records_event(self) -> None:
        logger = OutcomeLogger()

        record = logger.append(
            trace_id="trace-001",
            cid="cid-001",
            status="SUCCESS",
            manifest_hash="hash-001",
        )

        records = logger.records()

        assert isinstance(record, OutcomeRecord)
        assert len(records) == 1
        assert records[0].trace_id == "trace-001"
        assert records[0].cid == "cid-001"
        assert records[0].status == "SUCCESS"

    def test_records_returns_copy(self) -> None:
        logger = OutcomeLogger()
        logger.append(
            trace_id="trace-001",
            cid="cid-001",
            status="SUCCESS",
            manifest_hash="hash-001",
        )

        outcomes1 = logger.records()
        outcomes2 = logger.records()

        assert outcomes1 == outcomes2
        assert outcomes1 is not outcomes2

    def test_multiple_records_ordered(self) -> None:
        logger = OutcomeLogger()

        first = logger.append(
            trace_id="trace-001",
            cid="cid-001",
            status="SUCCESS",
            manifest_hash="hash-001",
        )
        second = logger.append(
            trace_id="trace-002",
            cid="cid-002",
            status="FAILURE",
            manifest_hash="hash-002",
        )
        third = logger.append(
            trace_id="trace-003",
            cid="cid-003",
            status="SUCCESS",
            manifest_hash="hash-003",
        )

        records = logger.records()

        assert len(records) == 3
        assert records == (first, second, third)
        assert records[0].trace_id == "trace-001"
        assert records[1].trace_id == "trace-002"
        assert records[2].trace_id == "trace-003"

    def test_reconciler_round_trip(self) -> None:
        logger = OutcomeLogger()
        record = logger.append(
            trace_id="trace-001",
            cid="cid-001",
            status="SUCCESS",
            manifest_hash="hash-001",
        )

        result = OutcomeReconciler().reconcile(
            observed=logger.records(),
            expected_hashes=(record.record_hash,),
        )

        assert result.ok is True
        assert result.missing == ()
        assert result.extra == ()
