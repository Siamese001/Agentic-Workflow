"""vLLM Determinism Governance Tests.

Verifies canonical normalization, hash stability, cross-process determinism,
and rejection of non-serializable types.

Compliance: REV 5 - routing_invariants_version = 1
"""

from __future__ import annotations

import ast
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


# ===========================================================================
# PHASE 2 — ROUTING PREDICATE GOVERNANCE TESTS
# ===========================================================================

_PREDICATE_REGISTRY = _PROJECT_ROOT / "agentic_core" / "L4_state" / "config" / "vllm_routing_predicates.py"


def _import_predicate_registry():
    """Import predicate registry module dynamically for test isolation."""
    import importlib.util

    mod_name = "vllm_routing_predicates"
    spec = importlib.util.spec_from_file_location(mod_name, _PREDICATE_REGISTRY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pr():
    """Predicate registry module fixture."""
    return _import_predicate_registry()


# ---------------------------------------------------------------------------
# Phase 2 Test A1 — RoutingDecision frozen (attribute assignment)
# ---------------------------------------------------------------------------


def test_routing_decision_frozen(pr) -> None:
    """RoutingDecision must reject attribute assignment."""
    decision = pr.evaluate({"routing_version": "1"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.routing_version = "x"


# ---------------------------------------------------------------------------
# Phase 2 Test A2 — RoutingDecision frozen (object.__setattr__)
# ---------------------------------------------------------------------------


def test_routing_decision_frozen_setattr(pr) -> None:
    """RoutingDecision with slots rejects new attribute creation."""
    decision = pr.evaluate({"routing_version": "1"})
    # With frozen=True + slots=True, object.__setattr__ can
    # overwrite existing slots but cannot create new attributes.
    with pytest.raises(AttributeError):
        object.__setattr__(decision, "nonexistent_attr", "x")


# ---------------------------------------------------------------------------
# Phase 2 Test A3 — ROUTING_PREDICATES immutable tuple
# ---------------------------------------------------------------------------


def test_routing_predicates_immutable(pr) -> None:
    """ROUTING_PREDICATES must be an immutable tuple."""
    assert pr.ROUTING_PREDICATES == tuple(pr.ROUTING_PREDICATES)
    assert isinstance(pr.ROUTING_PREDICATES, tuple)
    # Tuple itself is immutable — cannot append in-place
    original = pr.ROUTING_PREDICATES
    local_ref = original
    with pytest.raises(TypeError):
        local_ref[0] = None  # type: ignore[index]
    assert pr.ROUTING_PREDICATES is original


# ---------------------------------------------------------------------------
# Phase 2 Test B1 — No ast.Lambda in predicate registry
# ---------------------------------------------------------------------------


def test_no_lambda_in_predicate_registry() -> None:
    """Predicate registry must contain no lambda expressions."""
    tree = ast.parse(
        _PREDICATE_REGISTRY.read_text(encoding="utf-8"),
        filename=str(_PREDICATE_REGISTRY),
    )
    lambdas = [node for node in ast.walk(tree) if isinstance(node, ast.Lambda)]
    assert not lambdas, "Lambda found in predicate registry"


# ---------------------------------------------------------------------------
# Phase 2 Test B2 — No forbidden AST nodes in predicate registry
# ---------------------------------------------------------------------------


def test_no_forbidden_ast_nodes_in_predicate_registry() -> None:
    """Predicate registry must not contain AugAssign/Delete/With/Try/Raise/Yield."""
    _FORBIDDEN_NODES = (
        ast.AugAssign,
        ast.Delete,
        ast.With,
        ast.AsyncWith,
        ast.Try,
        ast.Raise,
        ast.Yield,
        ast.YieldFrom,
    )
    tree = ast.parse(
        _PREDICATE_REGISTRY.read_text(encoding="utf-8"),
        filename=str(_PREDICATE_REGISTRY),
    )
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, _FORBIDDEN_NODES):
            violations.append(f"line {node.lineno}: {type(node).__name__}")
    assert not violations, "Forbidden AST nodes in predicate registry:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Phase 2 Test B3 — No eval/exec/compile in predicate registry
# ---------------------------------------------------------------------------


def test_no_eval_exec_compile_in_predicate_registry() -> None:
    """Predicate registry must not call eval, exec, or compile."""
    tree = ast.parse(
        _PREDICATE_REGISTRY.read_text(encoding="utf-8"),
        filename=str(_PREDICATE_REGISTRY),
    )
    _FORBIDDEN_CALLS = {"eval", "exec", "compile"}
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in _FORBIDDEN_CALLS:
                violations.append(f"line {node.lineno}: {func.id}()")
    assert not violations, "eval/exec/compile found in predicate registry:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Phase 2 Test B4 — Predicate functions have no free variables
# ---------------------------------------------------------------------------


def test_predicate_functions_no_free_vars(pr) -> None:
    """All predicate functions must have co_freevars == ()."""
    for entry in pr.ROUTING_PREDICATES:
        fn = entry.predicate
        assert fn.__code__.co_freevars == (), f"{fn.__name__} has free vars: {fn.__code__.co_freevars}"


# ---------------------------------------------------------------------------
# Phase 2 Test B5 — Provider strict type
# ---------------------------------------------------------------------------


def test_provider_strict_type(pr) -> None:
    """Decision provider must be exact Provider enum type."""
    decision = pr.evaluate({"routing_version": "1"})
    assert isinstance(decision.provider, pr.Provider)
    assert type(decision.provider) is pr.Provider


# ---------------------------------------------------------------------------
# Phase 2 Test B6 — No provider-name string literals in registry AST
# ---------------------------------------------------------------------------


def test_no_provider_string_literals_in_registry(pr) -> None:
    """Predicate registry must not contain provider value string literals."""
    tree = ast.parse(
        _PREDICATE_REGISTRY.read_text(encoding="utf-8"),
        filename=str(_PREDICATE_REGISTRY),
    )
    provider_values = {m.value for m in pr.Provider}
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in provider_values:
                # Allow inside the Enum class definition itself
                pass
    # Re-scan excluding Enum class body
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Provider":
            continue
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Constant)
                and isinstance(child.value, str)
                and child.value in provider_values
            ):
                violations.append(f"line {child.lineno}: string literal {child.value!r}")
    assert not violations, (
        "Provider-name string literals found outside Enum in predicate registry:\n" + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# Phase 2 Test C1 — Context structural immutability
# ---------------------------------------------------------------------------


def test_context_structural_immutability(pr, bc) -> None:
    """evaluate() must not mutate the context dict."""
    import copy

    ctx = {"routing_version": "1", "requires_policy_read": True}
    snapshot = copy.deepcopy(ctx)
    pr.evaluate(ctx)
    assert ctx == snapshot


# ---------------------------------------------------------------------------
# Phase 2 Test C2 — Context hash immutability
# ---------------------------------------------------------------------------


def test_context_hash_immutability(pr, bc) -> None:
    """canonical_hash(ctx) must be unchanged after evaluate()."""
    ctx = {"routing_version": "1", "requires_policy_read": True}
    hash_before = bc.canonical_hash(dict(ctx))
    pr.evaluate(ctx)
    hash_after = bc.canonical_hash(dict(ctx))
    assert hash_before == hash_after


# ---------------------------------------------------------------------------
# Phase 2 Test C3 — Key-order independence
# ---------------------------------------------------------------------------


def test_key_order_independence(pr) -> None:
    """Two dicts with same items in different order must produce identical decisions."""
    ctx_a = {"routing_version": "1", "requires_policy_read": True, "z": 99}
    ctx_b = {"z": 99, "requires_policy_read": True, "routing_version": "1"}
    decision_a = pr.evaluate(ctx_a)
    decision_b = pr.evaluate(ctx_b)
    assert decision_a == decision_b
    assert decision_a.predicate_evaluation_hash == decision_b.predicate_evaluation_hash


# ---------------------------------------------------------------------------
# Phase 2 Test C4 — Double evaluation equality
# ---------------------------------------------------------------------------


def test_double_evaluation_equality(pr) -> None:
    """evaluate(ctx) called twice must return identical results."""
    ctx = {"routing_version": "1", "iteration_count": 5}
    assert pr.evaluate(ctx) == pr.evaluate(ctx)


# ---------------------------------------------------------------------------
# Phase 2 Test C5 — Predicate hash correctness
# ---------------------------------------------------------------------------


def test_predicate_hash_correctness(pr, bc) -> None:
    """decision.predicate_evaluation_hash must equal canonical_hash(dict(ctx))."""
    ctx = {"routing_version": "1", "invalid_ast": True}
    decision = pr.evaluate(ctx)
    expected = bc.canonical_hash(dict(ctx))
    assert decision.predicate_evaluation_hash == expected
