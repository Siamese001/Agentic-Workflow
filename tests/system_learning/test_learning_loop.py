"""Phase A — Learning Loop Persistence acceptance tests.

A-test hardenings verified:
  (a) failure_vector is never None (A5 hash-fallback determinism).
  (b) W-A-DETERMINISM-DIGEST is printed exactly once by persist_to_disk().
  (c) load_from_disk() round-trip passes (restore pass).
  (d) Manifest tamper → ManifestIntegrityError (negative control, xfail strict).
  (e) cluster_id and files_touched fields are populated on HealingOutcomeEvent.
  (f) Two identical persist calls produce identical digests (determinism).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_learning_loop")
_emit_applies_guardrail("p0", "test_learning_loop", "p0_governance")
_emit_reads_policy_state("p0", "test_learning_loop", "policy_binding")
_emit_snapshots_state("p0", "test_learning_loop", "state_snapshot")
emit_replay_key("p0", "test_learning_loop")
emit_determinism_digest("p0", "test_learning_loop")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# A5 — generate_fallback_vector determinism
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fallback_vector_never_none():
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    vec = generate_fallback_vector("IMPORT_BOUNDARY_VIOLATION unknown_agent")
    assert vec is not None
    assert len(vec) == 16


@pytest.mark.unit
@pytest.mark.determinism
def test_fallback_vector_determinism():
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    text = "LAYER_VIOLATION gate:check DependencyRepairAgent fix yaml"
    v1 = generate_fallback_vector(text)
    v2 = generate_fallback_vector(text)
    assert v1 == v2, "generate_fallback_vector must be deterministic"


@pytest.mark.unit
def test_fallback_vector_l2_normalized():
    import math

    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    vec = generate_fallback_vector("any text here")
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 1e-5, f"Expected L2 norm ~1.0, got {norm}"


@pytest.mark.unit
def test_fallback_vector_different_inputs_differ():
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    v1 = generate_fallback_vector("text_a")
    v2 = generate_fallback_vector("text_b")
    assert v1 != v2, "Different inputs should produce different fallback vectors"


# ---------------------------------------------------------------------------
# A1 — cluster_id and files_touched on HealingOutcomeEvent
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_healing_outcome_event_cluster_id_and_files_touched():
    from system_learning.types.healing_outcome_types import HealingOutcomeEvent

    evt = HealingOutcomeEvent(
        healer_id="agent_x",
        tier="L2",
        failure_type="IMPORT_BOUNDARY_VIOLATION",
        success=True,
        timestamp_utc=0,
        cluster_id="cluster-abc",
        files_touched=("foo/bar.py", "baz/qux.py"),
    )
    assert evt.cluster_id == "cluster-abc"
    assert evt.files_touched == ("foo/bar.py", "baz/qux.py")


@pytest.mark.unit
def test_healing_outcome_event_defaults_none():
    from system_learning.types.healing_outcome_types import HealingOutcomeEvent

    evt = HealingOutcomeEvent(
        healer_id="agent_x",
        tier="L2",
        failure_type="UNKNOWN",
        success=False,
        timestamp_utc=0,
    )
    assert evt.cluster_id is None
    assert evt.files_touched == ()


# ---------------------------------------------------------------------------
# A3 — FAISS disk persistence + manifest + W-A-DETERMINISM-DIGEST
# ---------------------------------------------------------------------------


@pytest.fixture()
def temp_index_dir(tmp_path: Path):
    return tmp_path / "faiss_test"


@pytest.fixture()
def built_store(temp_index_dir: Path):
    import hashlib as _hashlib
    import struct as _struct

    from system_learning.engines.local_faiss_store import LocalFAISSStore
    from system_learning.types.index_build_metadata_types import IndexBuildMetadata

    store = LocalFAISSStore(base_path=temp_index_dir)
    index_id = "test_idx"
    dim = 16
    vectors = [[float(i) / 100 for i in range(dim)], [float(i) / 200 for i in range(dim)]]
    metas = [{"content_hash": "aaa", "trace_id": "t1"}, {"content_hash": "bbb", "trace_id": "t2"}]

    # Directly populate in-memory index — bypasses FAISS presence check in begin_build()
    raw_bytes = b""
    for v in vectors:
        raw_bytes += b"".join(_struct.pack("<f", x) for x in v)
    version_hash = _hashlib.sha256(raw_bytes).hexdigest()
    metadata = IndexBuildMetadata(
        index_id=index_id,
        faiss_version="in-memory-v1",
        build_seed=0,
        canonicalization_version="1",
        embedding_model_version="hash-fallback-v1",
        embedding_model_checksum="abc123",
        built_at_utc=0,
        index_version_hash=version_hash,
        vector_count=2,
        dimension=dim,
    )
    store._memory_indexes[index_id] = {
        "dimension": dim,
        "seed": 0,
        "vectors": vectors,
        "metadatas": metas,
        "metadata": metadata,
        "version_hash": version_hash,
    }
    return store, index_id


@pytest.mark.unit
def test_persist_to_disk_writes_three_files(built_store, tmp_path):
    store, index_id = built_store
    dest = tmp_path / "artifact"
    store.persist_to_disk(index_id, dest, embedder_id="hash-fallback", model_version="v1")
    assert (dest / "index.json").exists()
    assert (dest / "meta.json").exists()
    assert (dest / "manifest.json").exists()


@pytest.mark.unit
@pytest.mark.determinism
def test_persist_to_disk_prints_determinism_digest(built_store, tmp_path, capsys):
    store, index_id = built_store
    dest = tmp_path / "artifact_det"
    store.persist_to_disk(index_id, dest, embedder_id="hash-fallback", model_version="v1")
    captured = capsys.readouterr()
    lines = [ln for ln in captured.out.splitlines() if "W-A-DETERMINISM-DIGEST:" in ln]
    assert len(lines) == 1, f"Expected exactly 1 W-A-DETERMINISM-DIGEST line, got {len(lines)}"
    digest = lines[0].split("W-A-DETERMINISM-DIGEST:")[-1].strip()
    assert len(digest) == 64, f"Expected 64-char hex digest, got {len(digest)}: {digest!r}"


@pytest.mark.unit
@pytest.mark.determinism
def test_persist_to_disk_digest_deterministic(built_store, tmp_path, capsys):
    store, index_id = built_store
    dest1 = tmp_path / "run1"
    dest2 = tmp_path / "run2"
    store.persist_to_disk(index_id, dest1, embedder_id="hash-fallback", model_version="v1")
    out1 = capsys.readouterr().out
    store.persist_to_disk(index_id, dest2, embedder_id="hash-fallback", model_version="v1")
    out2 = capsys.readouterr().out

    digest1 = [ln for ln in out1.splitlines() if "W-A-DETERMINISM-DIGEST:" in ln][0].split(":")[-1].strip()
    digest2 = [ln for ln in out2.splitlines() if "W-A-DETERMINISM-DIGEST:" in ln][0].split(":")[-1].strip()
    assert digest1 == digest2, "Two identical persist calls must produce identical digest"


@pytest.mark.unit
def test_load_from_disk_round_trip(built_store, tmp_path):
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    store, index_id = built_store
    dest = tmp_path / "roundtrip"
    store.persist_to_disk(index_id, dest, embedder_id="hash-fallback", model_version="v1")

    store2 = LocalFAISSStore(base_path=dest)
    store2.load_from_disk("loaded_idx", dest)
    assert "loaded_idx" in store2._memory_indexes, "Loaded index must be registered"
    loaded = store2._memory_indexes["loaded_idx"]
    assert loaded["dimension"] == 16
    assert len(loaded["vectors"]) == 2


@pytest.mark.unit
@pytest.mark.negative_control
def test_manifest_tamper_raises_integrity_error(built_store, tmp_path):
    from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

    store, index_id = built_store
    dest = tmp_path / "tamper"
    store.persist_to_disk(index_id, dest, embedder_id="hash-fallback", model_version="v1")

    index_path = dest / "index.json"
    index_path.write_bytes(index_path.read_bytes() + b" ")

    store2 = LocalFAISSStore(base_path=dest)
    with pytest.raises(ManifestIntegrityError, match="sha256 mismatch"):
        store2.load_from_disk("bad_idx", dest)


@pytest.mark.unit
@pytest.mark.negative_control
def test_load_missing_manifest_raises(tmp_path):
    from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

    store = LocalFAISSStore(base_path=tmp_path)
    with pytest.raises(ManifestIntegrityError, match="manifest.json not found"):
        store.load_from_disk("ghost", tmp_path / "nonexistent")
