"""Phase 3 contract tests for historical ingestion orchestrator.

Tests deterministic corpus writing, ordering invariance, end-to-end builds,
and strict schema validation.
"""

import hashlib
import tempfile
from pathlib import Path

import pytest

from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
    extract_dpo_pair_records,
    extract_healing_context_records,
    extract_telemetry_event_records,
    write_jsonl_records,
)
from system_learning.engines.historical_ingestion_orchestrator import (
    ingest_and_build_indexes,
)


class FakeEmbedder:
    """Public fake embedder for testing - deterministic mapping from text to vector."""

    def embed_batch(self, texts, dimension):
        """Generate deterministic vectors from text using SHA-256."""
        out = []
        for text in texts:
            # Use SHA-256 of text to generate deterministic vector
            h = hashlib.sha256(text.encode("utf-8")).digest()
            # Map bytes to float values in [0, 1]
            v = [(h[i % 32] / 255.0) for i in range(dimension)]
            out.append(v)
        return out


pytestmark = pytest.mark.unit_min_deps


def test_collect_only_inventory_exists():
    """Test 1: collect-only inventory exists and is discoverable."""
    # This test passes if the module is imported successfully
    assert ingest_and_build_indexes is not None
    assert FakeEmbedder is not None


def test_deterministic_corpus_writing():
    """Test 2: same input dicts -> JSONL bytes identical across two runs."""
    # Create test records
    records = [
        CorpusRecord(
            text="test text 1",
            trace_id="t1",
            content_hash=compute_content_hash(b"test text 1"),
            namespace="healing_contexts",
        ),
        CorpusRecord(
            text="test text 2",
            trace_id="t2",
            content_hash=compute_content_hash(b"test text 2"),
            namespace="healing_contexts",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Write records twice
        file1 = tmp_path / "test1.jsonl"
        file2 = tmp_path / "test2.jsonl"

        write_jsonl_records(file1, records)
        write_jsonl_records(file2, records)

        # Compare bytes
        bytes1 = file1.read_bytes()
        bytes2 = file2.read_bytes()

        assert bytes1 == bytes2, "JSONL output should be deterministic"


def test_ordering_invariance():
    """Test 3: permute input list order -> JSONL identical."""
    # Create test records in different order
    records1 = [
        CorpusRecord(
            text="zzz",
            trace_id="t3",
            content_hash="hash3",  # Higher hash
            namespace="healing_contexts",
        ),
        CorpusRecord(
            text="aaa",
            trace_id="t1",
            content_hash="hash1",  # Lower hash
            namespace="healing_contexts",
        ),
        CorpusRecord(
            text="mmm",
            trace_id="t2",
            content_hash="hash2",  # Middle hash
            namespace="healing_contexts",
        ),
    ]

    # Same records in different order
    records2 = [
        records1[2],  # zzz
        records1[0],  # aaa
        records1[1],  # mmm
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Write both orderings
        file1 = tmp_path / "test1.jsonl"
        file2 = tmp_path / "test2.jsonl"

        write_jsonl_records(file1, records1)
        write_jsonl_records(file2, records2)

        # Should be identical due to sorting by content_hash
        bytes1 = file1.read_bytes()
        bytes2 = file2.read_bytes()

        assert bytes1 == bytes2, "JSONL output should be order-invariant"


def test_end_to_end_build():
    """Test 4: end-to-end build returns stable index_version_hash across repeated runs."""
    # Prepare test data
    healing_source = [
        {
            "violation_signature": {"type": "error", "code": 500},
            "strategy": {"action": "retry", "max_attempts": 3},
            "trace_id": "heal_t1",
        }
    ]

    telemetry_source = [
        {
            "event_type": "request_completed",
            "payload": {"duration_ms": 150, "status": "success"},
            "trace_id": "tel_t1",
        }
    ]

    dpo_source = [
        {
            "prompt": "Translate to French",
            "chosen": "Bonjour le monde",
            "rejected": "Hello world",
            "trace_id": "dpo_t1",
        }
    ]

    embedder = FakeEmbedder()

    with tempfile.TemporaryDirectory() as tmp_dir:
        base_path = Path(tmp_dir)

        # Run ingestion twice
        metadata1 = ingest_and_build_indexes(
            base_path=base_path,
            built_at_utc=1234567890,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="emb-v1",
            embedding_model_checksum="0" * 64,
            canonicalization_version="canon-v1",
            embedder=embedder,
        )

        metadata2 = ingest_and_build_indexes(
            base_path=base_path,
            built_at_utc=1234567890,
            healing_source=healing_source,
            telemetry_source=telemetry_source,
            dpo_source=dpo_source,
            embedding_model_version="emb-v1",
            embedding_model_checksum="0" * 64,
            canonicalization_version="canon-v1",
            embedder=embedder,
        )

        # Should have three indexes
        expected_keys = {"healing_contexts_v1", "telemetry_events_v1", "dpo_pairs_v1"}
        assert set(metadata1.keys()) == expected_keys
        assert set(metadata2.keys()) == expected_keys

        # Hashes should be stable across runs
        for key in expected_keys:
            assert metadata1[key].index_version_hash == metadata2[key].index_version_hash
            assert len(metadata1[key].index_version_hash) == 64  # SHA-256 hex


def test_strict_schema_healing_contexts():
    """Test 5: missing required fields raises ValueError for healing contexts."""
    # Missing violation_signature
    with pytest.raises(ValueError, match="missing 'violation_signature' field"):
        extract_healing_context_records([{"strategy": {"x": 1}}])

    # Missing strategy
    with pytest.raises(ValueError, match="missing 'strategy' field"):
        extract_healing_context_records([{"violation_signature": {"y": 2}}])

    # Valid case should work
    records = extract_healing_context_records(
        [
            {
                "violation_signature": {"type": "error"},
                "strategy": {"action": "retry"},
                "trace_id": "t1",
            }
        ]
    )
    assert len(records) == 1
    assert records[0].namespace == "healing_contexts"


def test_strict_schema_telemetry_events():
    """Test 6: missing required fields raises ValueError for telemetry events."""
    # Missing event_type
    with pytest.raises(ValueError, match="missing 'event_type' field"):
        extract_telemetry_event_records([{"payload": {"x": 1}}])

    # Missing payload
    with pytest.raises(ValueError, match="missing 'payload' field"):
        extract_telemetry_event_records([{"event_type": "test"}])

    # Valid case should work
    records = extract_telemetry_event_records(
        [
            {
                "event_type": "request",
                "payload": {"duration": 100},
                "trace_id": "t1",
            }
        ]
    )
    assert len(records) == 1
    assert records[0].namespace == "telemetry_events"


def test_strict_schema_dpo_pairs():
    """Test 7: missing required fields raises ValueError for DPO pairs."""
    # Missing prompt
    with pytest.raises(ValueError, match="missing 'prompt' field"):
        extract_dpo_pair_records([{"chosen": "a", "rejected": "b"}])

    # Missing chosen
    with pytest.raises(ValueError, match="missing 'chosen' field"):
        extract_dpo_pair_records([{"prompt": "p", "rejected": "b"}])

    # Missing rejected
    with pytest.raises(ValueError, match="missing 'rejected' field"):
        extract_dpo_pair_records([{"prompt": "p", "chosen": "a"}])

    # Valid case should work
    records = extract_dpo_pair_records(
        [
            {
                "prompt": "Translate",
                "chosen": "Bonjour",
                "rejected": "Hello",
                "trace_id": "t1",
            }
        ]
    )
    assert len(records) == 1
    assert records[0].namespace == "dpo_pairs"


def test_trace_id_derivation():
    """Test 8: trace_id derivation from content_hash when missing."""
    # Test with missing trace_id
    records = extract_healing_context_records(
        [
            {
                "violation_signature": {"type": "error"},
                "strategy": {"action": "retry"},
                # No trace_id
            }
        ]
    )

    assert len(records) == 1
    # Should be first 16 chars of content_hash
    assert records[0].trace_id == records[0].content_hash[:16]
    assert len(records[0].trace_id) == 16
