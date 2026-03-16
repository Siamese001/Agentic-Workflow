"""Unit tests for persistent storage layer."""

import tempfile

import pytest

from agentic_core.L4_state.storage.filesystem_store import FileSystemStore
from agentic_core.L4_state.storage.persistent_store import (
    _canonicalize_payload,
    _compute_sha256,
    _sanitize_id,
    create_artifact,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_persistent_store")
_emit_applies_guardrail("p0", "test_persistent_store", "p0_governance")
_emit_reads_policy_state("p0", "test_persistent_store", "policy_binding")
_emit_snapshots_state("p0", "test_persistent_store", "state_snapshot")
emit_replay_key("p0", "test_persistent_store")
emit_determinism_digest("p0", "test_persistent_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.mark.unit_min_deps
def test_sanitize_id():
    """Test ID sanitization prevents path traversal."""
    # Normal IDs pass through
    assert _sanitize_id("test_id") == "test_id"
    assert _sanitize_id("test.id-123") == "test.id-123"

    # Path traversal attempts are blocked
    assert _sanitize_id("../etc/passwd") == ".._etc_passwd"
    assert _sanitize_id("test/../../secret") == "test_.._.._secret"
    assert _sanitize_id(r"C:\Windows\System32") == "C__Windows_System32"

    # Leading dots/dashes are prefixed
    assert _sanitize_id(".hidden") == "id_.hidden"
    assert _sanitize_id("-dash") == "id_-dash"


@pytest.mark.unit_min_deps
def test_canonicalize_payload():
    """Test payload canonicalization is deterministic."""
    payload1 = {"b": 2, "a": 1}
    payload2 = {"a": 1, "b": 2}

    canon1 = _canonicalize_payload(payload1)
    canon2 = _canonicalize_payload(payload2)

    # Should be identical regardless of key order
    assert canon1 == canon2
    assert canon1 == '{"a":1,"b":2}'


@pytest.mark.unit_min_deps
def test_compute_sha256():
    """Test SHA256 computation is stable."""
    data = "test data"
    hash1 = _compute_sha256(data)
    hash2 = _compute_sha256(data)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex length
    assert all(c in "0123456789abcdef" for c in hash1)


@pytest.mark.unit_min_deps
def test_create_artifact():
    """Test artifact creation with computed hashes."""
    payload = {"test": "data"}
    artifact = create_artifact("test_kind", "test_id", payload)

    assert artifact.kind == "test_kind"
    assert artifact.logical_id == "test_id"
    assert artifact.content_type == "application/json"
    assert artifact.payload == payload
    assert "sha256" in artifact.hashes
    assert "size" in artifact.metadata


@pytest.mark.unit_min_deps
def test_filesystem_store_put_creates_v0001_then_v0002():
    """Test that put creates v0001 then v0002 deterministically."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        artifact1 = create_artifact("test_kind", "test_id", {"version": 1})
        ref1 = store.put(artifact1)

        assert ref1.version == 1
        assert "v0001.json" in ref1.path

        artifact2 = create_artifact("test_kind", "test_id", {"version": 2})
        ref2 = store.put(artifact2)

        assert ref2.version == 2
        assert "v0002.json" in ref2.path


@pytest.mark.unit_min_deps
def test_filesystem_store_get_round_trip():
    """Test that get returns exactly what was put."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        original = create_artifact(
            "test_kind", "test_id", {"data": "test", "number": 42}, metadata={"test": "meta"}
        )
        ref = store.put(original)
        retrieved = store.get(ref)

        assert retrieved == original


@pytest.mark.unit_min_deps
def test_filesystem_store_list_ordering():
    """Test that list returns deterministically sorted results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Create artifacts in non-deterministic order
        artifacts = [
            ("z_kind", "b_id", {"data": 1}),
            ("a_kind", "c_id", {"data": 2}),
            ("a_kind", "a_id", {"data": 3}),
            ("z_kind", "a_id", {"data": 4}),
        ]

        refs = []
        for kind, id_, data in artifacts:
            artifact = create_artifact(kind, id_, data)
            ref = store.put(artifact)
            refs.append(ref)

        # List should be sorted by kind, then logical_id, then version
        listed = store.list()
        expected_order = [
            ("a_kind", "a_id", 1),
            ("a_kind", "c_id", 1),
            ("z_kind", "a_id", 1),
            ("z_kind", "b_id", 1),
        ]

        actual_order = [(r.kind, r.logical_id, r.version) for r in listed]
        assert actual_order == expected_order


@pytest.mark.unit_min_deps
def test_filesystem_store_rejects_path_traversal():
    """Test that path traversal attempts are blocked."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Attempt to create artifact with path traversal in kind
        artifact = create_artifact("../etc/passwd", "test", {"data": "test"})
        ref = store.put(artifact)

        # Should be sanitized to safe path
        assert ".._etc_passwd" in ref.path
        assert "../etc/passwd" not in ref.path


@pytest.mark.unit_min_deps
def test_filesystem_store_size_cap_enforced():
    """Test that maximum artifact size is enforced."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create store with tiny size limit
        store = FileSystemStore(temp_dir, max_artifact_size=100)

        # Create artifact that exceeds limit
        large_payload = {"data": "x" * 200}  # Will be > 100 bytes when JSON-encoded
        artifact = create_artifact("test", "large", large_payload)

        with pytest.raises(ValueError, match="Artifact size .* exceeds maximum"):
            store.put(artifact)


@pytest.mark.unit_min_deps
def test_filesystem_store_list_filter_by_kind():
    """Test that list can filter by artifact kind."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Create artifacts of different kinds
        artifact1 = create_artifact("kind1", "id1", {"data": 1})
        artifact2 = create_artifact("kind2", "id1", {"data": 2})
        artifact3 = create_artifact("kind1", "id2", {"data": 3})

        store.put(artifact1)
        store.put(artifact2)
        store.put(artifact3)

        # List all
        all_refs = store.list()
        assert len(all_refs) == 3

        # List filtered by kind
        kind1_refs = store.list(kind="kind1")
        assert len(kind1_refs) == 2
        assert all(r.kind == "kind1" for r in kind1_refs)

        kind2_refs = store.list(kind="kind2")
        assert len(kind2_refs) == 1
        assert kind2_refs[0].kind == "kind2"
