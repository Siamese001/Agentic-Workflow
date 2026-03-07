"""
Unit tests for L6 Observability Outcome Logger - deterministic outcome recording.
"""

import pytest

from agentic_core.L6_observability.enforcement.outcome_logger import (
    OutcomeLogger,
    OutcomeReconciler,
    OutcomeRecord,
    ReconcileResult,
)


@pytest.mark.unit
class TestOutcomeRecord:
    """Test OutcomeRecord dataclass and deterministic hashing."""

    def test_create_with_deterministic_record_hash(self):
        """Test record creation with deterministic hash computation."""
        record = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        assert record.trace_id == "trace123"
        assert record.cid == "cid456"
        assert record.status == "success"
        assert record.manifest_hash == "manifest789"
        assert record.record_hash is not None
        assert len(record.record_hash) == 64  # SHA-256 hex length

    def test_record_hash_deterministic_across_identical_inputs(self):
        """Test record hash is deterministic across identical inputs."""
        record1 = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        record2 = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Hash should be identical for same inputs
        assert record1.record_hash == record2.record_hash

    def test_record_hash_different_for_different_inputs(self):
        """Test record hash differs for different inputs."""
        record1 = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        record2 = OutcomeRecord.create(
            trace_id="trace123",
            cid="cid456",
            status="retry",  # Different status
            manifest_hash="manifest789",
        )

        assert record1.record_hash != record2.record_hash

    def test_record_hash_ignores_field_order_in_canonical_json(self):
        """Test record hash uses canonical JSON (field order doesn't matter)."""
        # All records should have same hash regardless of internal field order
        record1 = OutcomeRecord.create(trace_id="trace1", cid="cid1", status="success", manifest_hash="hash1")

        record2 = OutcomeRecord.create(trace_id="trace1", cid="cid1", status="success", manifest_hash="hash1")

        assert record1.record_hash == record2.record_hash

    def test_record_immutability(self):
        """Test record is immutable."""
        record = OutcomeRecord.create(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            record.trace_id = "changed"

        with pytest.raises(AttributeError):
            record.cid = "changed"

        with pytest.raises(AttributeError):
            record.status = "changed"

        with pytest.raises(AttributeError):
            record.manifest_hash = "changed"

        with pytest.raises(AttributeError):
            record.record_hash = "changed"


@pytest.mark.unit
class TestOutcomeLogger:
    """Test OutcomeLogger append-only semantics."""

    def test_logger_initialization_empty(self):
        """Test logger initializes with empty storage."""
        logger = OutcomeLogger()

        records = logger.records()
        assert len(records) == 0
        assert records == ()

    def test_append_creates_and_returns_record(self):
        """Test append creates and returns OutcomeRecord."""
        logger = OutcomeLogger()

        record = logger.append(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Verify record properties
        assert record.trace_id == "trace123"
        assert record.cid == "cid456"
        assert record.status == "success"
        assert record.manifest_hash == "manifest789"
        assert record.record_hash is not None

    def test_append_produces_deterministic_record_hash(self):
        """Test append produces deterministic record_hash for identical inputs."""
        logger = OutcomeLogger()

        record1 = logger.append(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        record2 = logger.append(
            trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789"
        )

        # Each record should have same hash for same inputs
        assert record1.record_hash == record2.record_hash

    def test_log_is_append_only_older_records_unchanged(self):
        """Test log is append-only (older records unchanged, ordering preserved)."""
        logger = OutcomeLogger()

        # Append first record
        record1 = logger.append(trace_id="trace1", cid="cid1", status="success", manifest_hash="hash1")

        # Append second record
        record2 = logger.append(trace_id="trace2", cid="cid2", status="retry", manifest_hash="hash2")

        # Verify ordering and immutability
        records = logger.records()
        assert len(records) == 2
        assert records[0] is record1
        assert records[1] is record2
        assert records[0].trace_id == "trace1"
        assert records[1].trace_id == "trace2"

    def test_records_returns_immutable_snapshot(self):
        """Test records() returns tuple snapshot (immutability)."""
        logger = OutcomeLogger()

        # Add a record
        logger.append(trace_id="trace123", cid="cid456", status="success", manifest_hash="manifest789")

        # Get records snapshot
        records1 = logger.records()
        records2 = logger.records()

        # Should be tuples (immutable)
        assert isinstance(records1, tuple)
        assert isinstance(records2, tuple)

        # Should be equal but not same object reference
        assert records1 == records2
        assert records1 is not records2

    def test_multiple_appends_preserve_order(self):
        """Test multiple appends preserve chronological order."""
        logger = OutcomeLogger()

        # Append multiple records
        records = []
        for i in range(5):
            record = logger.append(
                trace_id=f"trace{i}", cid=f"cid{i}", status="success", manifest_hash=f"hash{i}"
            )
            records.append(record)

        # Verify order preserved
        all_records = logger.records()
        assert len(all_records) == 5

        for i, record in enumerate(all_records):
            assert record.trace_id == f"trace{i}"
            assert record is records[i]


@pytest.mark.unit
class TestOutcomeReconciler:
    """Test OutcomeReconciler deterministic hash comparison."""

    def test_reconcile_exact_match(self):
        """Test exact match => ok True, empty missing/extra."""
        reconciler = OutcomeReconciler()

        # Create observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Expected hashes match observed
        expected_hashes = (record1.record_hash, record2.record_hash)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is True
        assert result.missing == ()
        assert result.extra == ()

    def test_reconcile_missing_expected(self):
        """Test missing expected => ok False, missing contains hash."""
        reconciler = OutcomeReconciler()

        # Only one observed record
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        observed = (record1,)

        # Expect two hashes (one missing)
        missing_hash = "missing_hash_12345"
        expected_hashes = (record1.record_hash, missing_hash)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is False
        assert missing_hash in result.missing
        assert result.extra == ()

    def test_reconcile_extra_observed(self):
        """Test extra observed => ok False, extra contains hash."""
        reconciler = OutcomeReconciler()

        # Two observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Only expect one hash (one extra)
        expected_hashes = (record1.record_hash,)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is False
        assert result.missing == ()
        assert record2.record_hash in result.extra

    def test_reconcile_both_missing_and_extra(self):
        """Test both missing and extra => ok False, both populated."""
        reconciler = OutcomeReconciler()

        # Observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Expected hashes (different from observed)
        expected_hash1 = "expected_hash_11111"
        expected_hash2 = "expected_hash_22222"
        expected_hashes = (expected_hash1, expected_hash2)

        result = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes)

        assert result.ok is False
        assert len(result.missing) == 2
        assert expected_hash1 in result.missing
        assert expected_hash2 in result.missing
        assert len(result.extra) == 2
        assert record1.record_hash in result.extra
        assert record2.record_hash in result.extra

    def test_reconcile_determinism_shuffled_input(self):
        """Test determinism: shuffled expected_hashes input yields same result."""
        reconciler = OutcomeReconciler()

        # Create observed records
        record1 = OutcomeRecord.create("trace1", "cid1", "success", "hash1")
        record2 = OutcomeRecord.create("trace2", "cid2", "success", "hash2")
        observed = (record1, record2)

        # Expected hashes in different order
        expected_hashes1 = (record1.record_hash, record2.record_hash, "missing_hash")
        expected_hashes2 = ("missing_hash", record2.record_hash, record1.record_hash)

        result1 = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes1)
        result2 = reconciler.reconcile(observed=observed, expected_hashes=expected_hashes2)

        # Results should be identical
        assert result1.ok == result2.ok
        assert result1.missing == result2.missing
        assert result1.extra == result2.extra

    def test_reconcile_result_immutability(self):
        """Test ReconcileResult is immutable."""
        result = ReconcileResult(missing=("hash1", "hash2"), extra=("hash3",), ok=False)

        # Should be frozen dataclass
        with pytest.raises(AttributeError):
            result.missing = ("changed",)

        with pytest.raises(AttributeError):
            result.extra = ("changed",)

        with pytest.raises(AttributeError):
            result.ok = True
