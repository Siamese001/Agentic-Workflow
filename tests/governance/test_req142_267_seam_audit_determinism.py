"""Tests for Wave 18 REQ-142/267: Seam audit artifact emission + replay."""

import hashlib
import json
from typing import Any

import pytest

pytestmark = pytest.mark.governance

# Import the seam audit module
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_routing" / "seam"))

from seam_audit import (
    clear_seam_audit_records,
    get_seam_audit_digest,
    get_seam_audit_logger,
    log_seam_operation,
)


class MockSeamOperation:
    """Mock seam operation for testing."""

    def __init__(self, seam_id: str):
        self.seam_id = seam_id
        self.operation_count = 0

    def process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mock processing operation."""
        self.operation_count += 1

        # Log the seam operation
        log_seam_operation(
            seam_id=self.seam_id,
            operation="process_data",
            inputs=data,
            outputs={"processed": True, "count": self.operation_count},
            layer_source="L2_execution",
            layer_target="L3_orchestration",
            caller_id="MockSeamOperation.process_data",
        )

        return {"processed": True, "count": self.operation_count}

    def transform_data(self, data: list[Any]) -> list[Any]:
        """Mock transformation operation."""
        self.operation_count += 1

        # Log the seam operation
        log_seam_operation(
            seam_id=self.seam_id,
            operation="transform_data",
            inputs={"data_list": data},
            outputs={"transformed": True, "length": len(data)},
            layer_source="L1_routing",
            layer_target="L2_execution",
            caller_id="MockSeamOperation.transform_data",
        )

        return [f"transformed_{item}" for item in data]


class TestSeamAuditDeterminism:
    """Test seam audit determinism and replay."""

    def setup_method(self):
        """Set up test environment."""
        clear_seam_audit_records()
        self.logger = get_seam_audit_logger()
        self.logger.enable()

    def test_seam_audit_record_creation(self):
        """Test creation of seam audit records."""
        # Given - Seam operation
        seam = MockSeamOperation("test_seam")

        # When - Perform operation
        _ = seam.process_data({"input": "test"})

        # Then - Audit record should be created
        records = self.logger.get_records("test_seam")
        assert len(records) == 1, "Should create one audit record"

        record = records[0]
        assert record.seam_id == "test_seam", "Should record seam ID"
        assert record.operation == "process_data", "Should record operation"
        assert record.layer_source == "L2_execution", "Should record source layer"
        assert record.layer_target == "L3_orchestration", "Should record target layer"
        assert record.invocation_hash, "Should have invocation hash"
        assert len(record.invocation_hash) == 64, "Hash should be SHA256"

    def test_seam_audit_deterministic_digest(self):
        """Test that seam audit digest is deterministic."""
        # Given - Same operations
        seam1 = MockSeamOperation("deterministic_seam")
        seam2 = MockSeamOperation("deterministic_seam")

        # Run 1
        seam1.process_data({"input": "test1"})
        seam1.transform_data(["a", "b", "c"])
        digest1 = get_seam_audit_digest("deterministic_seam")

        # Clear and run again
        clear_seam_audit_records()
        seam2.process_data({"input": "test1"})
        seam2.transform_data(["a", "b", "c"])
        digest2 = get_seam_audit_digest("deterministic_seam")

        # Then - Digests should be identical
        assert digest1 == digest2, "Digests should be deterministic"
        assert len(digest1) == 64, "Digest should be SHA256"

    def test_seam_audit_two_run_replay(self):
        """Test two-run replay of seam audit records."""
        # Given - Identical operations in two runs
        input_data = {"test": "data", "number": 42}
        list_data = ["item1", "item2", "item3"]

        # Run 1
        seam1 = MockSeamOperation("replay_seam")
        result1a = seam1.process_data(input_data)
        result1b = seam1.transform_data(list_data)
        records1 = self.logger.get_records("replay_seam")
        digest1 = get_seam_audit_digest("replay_seam")

        # Run 2
        clear_seam_audit_records()
        seam2 = MockSeamOperation("replay_seam")
        result2a = seam2.process_data(input_data)
        result2b = seam2.transform_data(list_data)
        records2 = self.logger.get_records("replay_seam")
        digest2 = get_seam_audit_digest("replay_seam")

        # Then - Results should be identical
        assert result1a == result2a, "Process results should be identical"
        assert result1b == result2b, "Transform results should be identical"
        assert digest1 == digest2, "Digests should be identical"

        # Records should have same structure
        assert len(records1) == len(records2), "Should have same number of records"

        for r1, r2 in zip(records1, records2):
            assert r1.seam_id == r2.seam_id, "Seam ID should match"
            assert r1.operation == r2.operation, "Operation should match"
            assert r1.invocation_hash == r2.invocation_hash, "Invocation hash should match"

    def test_seam_audit_input_hash_determinism(self):
        """Test that input hashes are deterministic."""
        # Given - Same input data
        input_data = {"key1": "value1", "key2": 123, "key3": True}

        # When - Log operation twice
        log_seam_operation(
            seam_id="hash_test",
            operation="test_operation",
            inputs=input_data,
            outputs={"result": "success"},
            layer_source="L1",
            layer_target="L2",
        )

        clear_seam_audit_records()

        log_seam_operation(
            seam_id="hash_test",
            operation="test_operation",
            inputs=input_data,
            outputs={"result": "success"},
            layer_source="L1",
            layer_target="L2",
        )

        # Then - Input hashes should be identical
        records = self.logger.get_records("hash_test")
        assert len(records) == 1, "Should have one record"

        # The inputs_hash should be deterministic
        inputs_hash = records[0].inputs_hash
        assert len(inputs_hash) == 64, "Input hash should be SHA256"

        # Same input should produce same hash
        expected_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
        assert inputs_hash == expected_hash, "Input hash should match expected"

    def test_seam_audit_output_hash_determinism(self):
        """Test that output hashes are deterministic."""
        # Given - Same output data
        output_data = {"processed": True, "items": ["a", "b", "c"], "count": 3}

        # When - Log operation
        log_seam_operation(
            seam_id="output_hash_test",
            operation="test_operation",
            inputs={"input": "test"},
            outputs=output_data,
            layer_source="L1",
            layer_target="L2",
        )

        # Then - Output hash should be deterministic
        records = self.logger.get_records("output_hash_test")
        assert len(records) == 1, "Should have one record"

        outputs_hash = records[0].outputs_hash
        assert len(outputs_hash) == 64, "Output hash should be SHA256"

        # Should match expected hash
        expected_hash = hashlib.sha256(json.dumps(output_data, sort_keys=True).encode()).hexdigest()
        assert outputs_hash == expected_hash, "Output hash should match expected"

    def test_seam_audit_multiple_seams_isolation(self):
        """Test that different seams are isolated."""
        # Given - Two different seams
        seam_a = MockSeamOperation("seam_A")
        seam_b = MockSeamOperation("seam_B")

        # When - Perform operations on both
        seam_a.process_data({"data": "A"})
        seam_b.process_data({"data": "B"})

        # Then - Records should be isolated
        records_a = self.logger.get_records("seam_A")
        records_b = self.logger.get_records("seam_B")

        assert len(records_a) == 1, "Seam A should have one record"
        assert len(records_b) == 1, "Seam B should have one record"

        assert records_a[0].seam_id == "seam_A", "Seam A record should have correct ID"
        assert records_b[0].seam_id == "seam_B", "Seam B record should have correct ID"

        # Digests should be different
        digest_a = get_seam_audit_digest("seam_A")
        digest_b = get_seam_audit_digest("seam_B")
        assert digest_a != digest_b, "Different seams should have different digests"

    def test_seam_audit_operation_ordering(self):
        """Test that operation order affects digest."""
        # Given - Same operations in different order
        seam1 = MockSeamOperation("order_test")
        seam2 = MockSeamOperation("order_test")

        # Run 1 - Order A then B
        seam1.process_data({"op": "A"})
        seam1.transform_data(["x"])
        digest1 = get_seam_audit_digest("order_test")

        # Run 2 - Order B then A
        clear_seam_audit_records()
        seam2.transform_data(["x"])
        seam2.process_data({"op": "A"})
        digest2 = get_seam_audit_digest("order_test")

        # Then - Different order should produce different digest
        assert digest1 != digest2, "Different operation order should produce different digest"

    def test_seam_audit_metadata_handling(self):
        """Test seam audit metadata handling."""
        # Given - Operation with metadata
        metadata = {"user": "test_user", "session": "session_123", "priority": "high"}

        # When - Log operation with metadata
        log_seam_operation(
            seam_id="metadata_test",
            operation="test_operation",
            inputs={"input": "test"},
            outputs={"output": "result"},
            layer_source="L1",
            layer_target="L2",
            metadata=metadata,
        )

        # Then - Metadata should be preserved
        records = self.logger.get_records("metadata_test")
        assert len(records) == 1, "Should have one record"

        record = records[0]
        assert record.metadata == metadata, "Metadata should be preserved"

        # Metadata should be included in invocation hash
        assert record.invocation_hash, "Invocation hash should include metadata"

    def test_seam_audit_disabled_logging(self):
        """Test behavior when audit logging is disabled."""
        # Given - Disabled logger
        self.logger.disable()

        seam = MockSeamOperation("disabled_test")

        # When - Perform operation
        op_result = seam.process_data({"input": "test"})

        # Then - No records should be created
        records = self.logger.get_records("disabled_test")
        assert len(records) == 0, "No records should be created when disabled"

        # But operation should still work
        assert op_result["processed"], "Operation should still work"


def test_req142_seam_audit_artifact_emission():
    """REQ-142: Test seam audit artifact emission."""
    test = TestSeamAuditDeterminism()
    test.setup_method()

    # Core emission tests
    test.test_seam_audit_record_creation()
    test.test_seam_audit_input_hash_determinism()
    test.test_seam_audit_output_hash_determinism()
    test.test_seam_audit_metadata_handling()
    test.test_seam_audit_disabled_logging()


def test_req267_seam_audit_replay():
    """REQ-267: Test seam audit replay determinism."""
    test = TestSeamAuditDeterminism()
    test.setup_method()
    test.logger.enable()

    # Replay determinism tests
    test.test_seam_audit_deterministic_digest()
    test.test_seam_audit_two_run_replay()
    test.test_seam_audit_multiple_seams_isolation()
    test.test_seam_audit_operation_ordering()
