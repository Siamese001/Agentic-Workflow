"""vLLM Determinism Governance Tests.

Verifies canonical normalization, hash stability, cross-process determinism,
and rejection of non-serializable types.

Compliance: REV 5 - routing_invariants_version = 1
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import os
import subprocess
import sys
from decimal import Decimal
from enum import Enum
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_BOUNDARY_CLIENT = _PROJECT_ROOT / "tools" / "vllm_boundary_client.py"


def _import_boundary_client():
    """Import boundary client module dynamically for test isolation."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("vllm_boundary_client", _BOUNDARY_CLIENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bc():
    """Boundary client module fixture."""
    return _import_boundary_client()


# ---------------------------------------------------------------------------
# Test 1 — canonical_hash stable across 10 calls
# ---------------------------------------------------------------------------


def test_canonical_hash_stable(bc) -> None:
    """Same input must produce the same hash across 10 calls."""
    payload = {"a": 1, "b": [1, 2, 3], "c": {"nested": True}}
    hashes = [bc.canonical_hash(payload) for _ in range(10)]
    assert len(set(hashes)) == 1, "canonical_hash is not stable"


# ---------------------------------------------------------------------------
# Test 2 — Idempotent normalization
# ---------------------------------------------------------------------------


def test_idempotent_normalization(bc) -> None:
    """normalize_payload must be idempotent."""
    cases = [
        {"a": 1, "b": [1, 2, 3]},
        {"f": 3.14159265358979},
        {"s": "hello"},
        {"n": None},
        {"b": True},
        {"nested": {"x": [1, 2], "y": {"z": 3}}},
    ]
    for case in cases:
        once = bc.normalize_payload(case)
        twice = bc.normalize_payload(once)
        assert once == twice, f"normalize_payload not idempotent for: {case!r}"


# ---------------------------------------------------------------------------
# Test 3 — Nested structure determinism
# ---------------------------------------------------------------------------


def test_nested_structure_determinism(bc) -> None:
    """Nested dicts/lists must hash identically regardless of construction."""
    a = {"outer": {"inner": [1, 2, 3], "key": "val"}}
    b = {"outer": {"key": "val", "inner": [1, 2, 3]}}
    assert bc.canonical_hash(a) == bc.canonical_hash(b)


# ---------------------------------------------------------------------------
# Test 4 — Set ordering stability
# ---------------------------------------------------------------------------


def test_set_ordering_stability(bc) -> None:
    """Sets must normalize to the same sorted list regardless of order."""
    result_a = bc.normalize_payload({3, 1, 2})
    result_b = bc.normalize_payload({1, 3, 2})
    assert result_a == result_b
    assert result_a == [1, 2, 3]


# ---------------------------------------------------------------------------
# Test 5 — Decimal normalization consistency
# ---------------------------------------------------------------------------


def test_decimal_normalization(bc) -> None:
    """Decimal must normalize to its string representation."""
    result = bc.normalize_payload(Decimal("3.14"))
    assert result == "3.14"
    result2 = bc.normalize_payload(Decimal("3.14"))
    assert result == result2


# ---------------------------------------------------------------------------
# Test 6 — Dataclass round-trip equality
# ---------------------------------------------------------------------------


def test_dataclass_roundtrip(bc) -> None:
    """Dataclass must normalize to same hash as equivalent dict."""

    @dataclasses.dataclass
    class Point:
        x: int
        y: int

    p = Point(x=1, y=2)
    dc_hash = bc.canonical_hash(bc.normalize_payload(p))
    dict_hash = bc.canonical_hash({"x": 1, "y": 2})
    assert dc_hash == dict_hash


# ---------------------------------------------------------------------------
# Test 7 — Float rounding to 12 decimal places
# ---------------------------------------------------------------------------


def test_float_rounding(bc) -> None:
    """Floats must be rounded to 12 decimal places."""
    result = bc.normalize_payload(3.141592653589793238)
    assert result == round(3.141592653589793238, 12)
    # Verify idempotency: already-rounded float stays the same
    assert bc.normalize_payload(result) == result


# ---------------------------------------------------------------------------
# Test 8 — Negative zero normalization
# ---------------------------------------------------------------------------


def test_negative_zero_normalization(bc) -> None:
    """canonical_hash must treat -0.0 identically to 0.0."""
    assert bc.canonical_hash({"x": -0.0}) == bc.canonical_hash({"x": 0.0})
    assert bc.normalize_payload(-0.0) == 0.0
    # Verify JSON encoding is identical
    norm_neg = bc.normalize_payload({"x": -0.0})
    norm_pos = bc.normalize_payload({"x": 0.0})
    assert json.dumps(norm_neg) == json.dumps(norm_pos)


# ---------------------------------------------------------------------------
# Test 9 — NaN rejected
# ---------------------------------------------------------------------------


def test_nan_rejected(bc) -> None:
    """NaN must raise TypeError."""
    with pytest.raises(TypeError, match="NaN"):
        bc.normalize_payload(float("nan"))


# ---------------------------------------------------------------------------
# Test 10 — Infinity rejected
# ---------------------------------------------------------------------------


def test_inf_rejected(bc) -> None:
    """Infinity must raise TypeError."""
    with pytest.raises(TypeError, match="Infinity"):
        bc.normalize_payload(float("inf"))
    with pytest.raises(TypeError, match="Infinity"):
        bc.normalize_payload(float("-inf"))


# ---------------------------------------------------------------------------
# Test 11 — datetime rejected
# ---------------------------------------------------------------------------


def test_datetime_rejected(bc) -> None:
    """datetime objects must raise TypeError."""
    with pytest.raises(TypeError, match="datetime"):
        bc.normalize_payload(datetime.datetime.now())
    with pytest.raises(TypeError, match="datetime"):
        bc.normalize_payload(datetime.date.today())


# ---------------------------------------------------------------------------
# Test 12 — bytes rejected
# ---------------------------------------------------------------------------


def test_bytes_rejected(bc) -> None:
    """bytes objects must raise TypeError."""
    with pytest.raises(TypeError, match="bytes"):
        bc.normalize_payload(b"hello")


# ---------------------------------------------------------------------------
# Test 13 — complex rejected
# ---------------------------------------------------------------------------


def test_complex_rejected(bc) -> None:
    """complex objects must raise TypeError."""
    with pytest.raises(TypeError, match="complex"):
        bc.normalize_payload(1 + 2j)


# ---------------------------------------------------------------------------
# Test 14 — Tuple to list preserves order (no sorting)
# ---------------------------------------------------------------------------


def test_tuple_to_list_preserves_order(bc) -> None:
    """Tuples must convert to lists preserving original order."""
    assert bc.normalize_payload((3, 1, 2)) == [3, 1, 2]
    assert bc.normalize_payload((3, 1, 2)) != [1, 2, 3]
    assert bc.normalize_payload(("z", "a", "m")) == ["z", "a", "m"]


# ---------------------------------------------------------------------------
# Test 15 — canonical_hash rejects non-dict top level
# ---------------------------------------------------------------------------


def test_canonical_hash_rejects_non_dict(bc) -> None:
    """canonical_hash must reject non-dict at top level."""
    with pytest.raises(TypeError, match="dict"):
        bc.canonical_hash([1, 2, 3])
    with pytest.raises(TypeError, match="dict"):
        bc.canonical_hash("string")
    with pytest.raises(TypeError, match="dict"):
        bc.canonical_hash(42)


# ---------------------------------------------------------------------------
# Test 16 — Cross-process determinism (3 interpreter instances)
# ---------------------------------------------------------------------------

_HASH_SCRIPT = """
import sys
sys.path.insert(0, sys.argv[1])
import importlib.util
spec = importlib.util.spec_from_file_location("vllm_boundary_client", sys.argv[2])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
payload = {"a": 1, "b": [3, 1, 2], "c": {"nested": True}, "f": 3.14}
print(mod.canonical_hash(payload))
"""


def test_cross_process_determinism() -> None:
    """canonical_hash must be identical across 3 interpreter instances.

    PYTHONHASHSEED=0 is enforced to eliminate hash randomisation.
    """
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"

    script_args = [
        sys.executable,
        "-c",
        _HASH_SCRIPT,
        str(_PROJECT_ROOT),
        str(_BOUNDARY_CLIENT),
    ]

    hashes = []
    for _ in range(3):
        result = subprocess.run(
            script_args,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        assert result.returncode == 0, f"Subprocess failed:\n{result.stderr}"
        hashes.append(result.stdout.strip())

    hash_a, hash_b, hash_c = hashes
    assert hash_a == hash_b == hash_c, (
        f"Cross-process hash mismatch:\n  A={hash_a}\n  B={hash_b}\n  C={hash_c}"
    )


# ---------------------------------------------------------------------------
# Test 17 — Enum normalization
# ---------------------------------------------------------------------------


def test_enum_normalization(bc) -> None:
    """Enum values must normalize to their .name string."""

    class Color(Enum):
        RED = 1
        GREEN = 2

    assert bc.normalize_payload(Color.RED) == "RED"
    assert bc.normalize_payload(Color.GREEN) == "GREEN"
    # Idempotent: already a string
    assert bc.normalize_payload("RED") == "RED"
