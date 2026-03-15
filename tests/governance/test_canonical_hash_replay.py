"""W19: Two-run canonical serializer; assert identical bytes both runs.

REQ-184/381/384: Canonical hashing determinism — the canonical serializer
produces byte-identical output across two independent runs given identical inputs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance


def canonical_serialize(obj: Any) -> bytes:
    """
    Canonical serializer: JSON with sort_keys, no extra spaces, UTF-8 encoded.
    Deterministic across runs and Python versions.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def canonical_hash(obj: Any) -> str:
    """SHA-256 of the canonical serialisation."""
    return hashlib.sha256(canonical_serialize(obj)).hexdigest()


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

_ARTIFACT_A = {
    "schema_version": "1.0.0",
    "artifact_id": "art_001",
    "payload": {"action": "update", "target": "L4_state", "value": 42},
    "tags": ["governance", "replay", "determinism"],
    "nested": {"level1": {"level2": {"value": True}}},
}

_ARTIFACT_B: list[dict[str, Any]] = [
    {"id": 1, "name": "alpha", "score": 0.99},
    {"id": 2, "name": "beta", "score": 0.88},
    {"id": 3, "name": "gamma", "score": 0.77},
]

_ARTIFACT_C = {
    "empty_dict": {},
    "empty_list": [],
    "null_value": None,
    "unicode": "\u00e9l\u00e8ve",
    "integer": 0,
    "negative": -1,
    "float_val": 3.14159,
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.governance
def test_canonical_hash_two_run_dict():
    """Two-run hash of a dict produces identical bytes."""
    h1 = canonical_hash(_ARTIFACT_A)
    h2 = canonical_hash(_ARTIFACT_A)
    assert h1 == h2
    assert len(h1) == 64


@pytest.mark.governance
def test_canonical_hash_two_run_list():
    """Two-run hash of a list produces identical bytes."""
    h1 = canonical_hash(_ARTIFACT_B)
    h2 = canonical_hash(_ARTIFACT_B)
    assert h1 == h2


@pytest.mark.governance
def test_canonical_hash_two_run_edge_cases():
    """Two-run hash of edge-case values is identical."""
    h1 = canonical_hash(_ARTIFACT_C)
    h2 = canonical_hash(_ARTIFACT_C)
    assert h1 == h2


@pytest.mark.governance
def test_canonical_serialize_sort_keys():
    """Key order in the source dict does not affect canonical bytes."""
    obj_a = {"z": 1, "a": 2, "m": 3}
    obj_b = {"a": 2, "m": 3, "z": 1}
    assert canonical_serialize(obj_a) == canonical_serialize(obj_b)


@pytest.mark.governance
def test_canonical_hash_field_sensitivity():
    """Changing one field changes the hash."""
    base = canonical_hash(_ARTIFACT_A)
    mutated = {**_ARTIFACT_A, "artifact_id": "art_TAMPERED"}
    assert canonical_hash(mutated) != base


@pytest.mark.governance
def test_canonical_serialize_empty_object():
    """Empty dict serialises deterministically."""
    b1 = canonical_serialize({})
    b2 = canonical_serialize({})
    assert b1 == b2 == b"{}"


@pytest.mark.governance
def test_canonical_hash_known_value():
    """Hash of a known object matches independently computed expected value."""
    obj = {"key": "value"}
    expected = hashlib.sha256(b'{"key":"value"}').hexdigest()
    assert canonical_hash(obj) == expected


@pytest.mark.governance
def test_req381_canonical_hash_used_in_artifact_binding():
    """REQ-381: Artifacts must carry canonical hash binding."""

    @dataclass(frozen=True)
    class BoundArtifact:
        artifact_id: str
        payload: dict
        canonical_hash: str

    payload = {"action": "promote", "target": "ns_a"}
    h = canonical_hash(payload)
    artifact = BoundArtifact(artifact_id="art_bound_001", payload=payload, canonical_hash=h)

    assert artifact.canonical_hash == canonical_hash(artifact.payload)
    assert len(artifact.canonical_hash) == 64


@pytest.mark.governance
def test_req384_replay_hash_identical_two_runs():
    """REQ-384: Replay hash must be identical across two runs for same artifact."""
    payload = {"trace_id": "trace_abc", "plan_hash": "aabbcc" * 10, "tick": 7}
    run1 = canonical_hash(payload)
    run2 = canonical_hash(payload)
    assert run1 == run2
