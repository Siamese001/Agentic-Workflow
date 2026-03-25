"""
SSOT entrypoint label contract.

History: both execute_ssot.py and execute_ssot_entrypoint.py were once labelled
'# FROZEN — superseded by l0_execute.py'.  l0_execute.py was never built.
These files ARE the active entrypoints.  The tests below enforce the corrected
state and document the architectural debt explicitly.

Test rigor: .windsurfrules §1 (Testing & Evidence)
  §1.3  Deterministic tests only — all reads are from fixed repo paths, no
        randomness, no wall clock, no external state.
  §1.5  Edge cases — empty file, label at boundary line 5 vs 6, near-miss
        label strings, partial label, missing file.
  §1.6  State transitions — FROZEN→ACTIVE is a one-way transition; tests
        prove the old state cannot re-appear and the new state is exact.
  §1.9  Matrix testing — label × file is fully parametrized so failures
        name the exact file.
  §1.10 Ingress-path — V15 wiring test uses AST scoped strictly to the
        _legacy_main FunctionDef body, not module-level walk.
  §1.11 Regression/mutation guards — near-miss strings that differ by one
        character or word must NOT satisfy the active-label predicate.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Constants — single source of truth for all assertions
# ---------------------------------------------------------------------------

ACTIVE_HEADER = "# NOTE: l0_execute.py was planned but never implemented. This file is ACTIVE."

STALE_FROZEN_HEADER = "# FROZEN — superseded by l0_execute.py"

ACTIVE_FILES = [
    REPO_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot.py",
    REPO_ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot_entrypoint.py",
]

L0_EXECUTE_PATH = REPO_ROOT / L0_ROUTING_DIR / "scripts" / "l0_execute.py"

# §8.1e V15 bootstrap symbols that must be called inside _legacy_main
V15_REQUIRED_CALLS = (
    "_v15_build_ssot_manifest",
    "_v15_ssot_gateway_audit",
)

# Near-miss strings that must NOT satisfy the active-label predicate (§1.11)
NEAR_MISS_LABELS = [
    "# NOTE: l0_execute.py was planned but never implemented. This file is active.",  # wrong case
    "# NOTE: l0_execute.py was planned but never implemented.",  # truncated
    "# FROZEN — superseded by l0_execute.py (Guardian→Dispatcher→Healer pipeline).",  # old stale label
    "# NOTE: l0_execute.py was planned but never implemented. This file is FROZEN.",  # wrong terminal word
    "",  # empty string
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ACTIVE_FILES_IDS = [p.name for p in ACTIVE_FILES]


def _non_empty_lines(content: str, head: int = 10) -> list[str]:
    """Return the first `head` non-empty, non-whitespace lines."""
    return [ln for ln in content.splitlines()[:head] if ln.strip()]


def _collect_direct_calls_in_function(func_node: ast.FunctionDef) -> set[str]:
    """AST-walk only the direct body of func_node (not nested defs).

    §1.10 / §3.3: scoped AST walk, not heuristic string scan.
    Collects call names from ast.Name and ast.Attribute call targets.
    Excludes nodes that are inside a nested FunctionDef or AsyncFunctionDef
    to prevent false-positive matches from inner helpers.
    """
    call_names: set[str] = set()

    def _walk_body(nodes: list) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # do not descend into nested functions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    call_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    call_names.add(node.func.attr)
            for child in ast.iter_child_nodes(node):
                _walk_body([child])

    _walk_body(func_node.body)
    return call_names


# ---------------------------------------------------------------------------
# §1.9 Matrix: label presence × each file (parametrized)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_active_header_present(fpath: Path) -> None:
"""Test active_header_present runtime behavior."""
# Arrange
# TODO: Set up test data for active_header_present
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute active_header_present
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
"""Test active_header_is_early runtime behavior."""
# Arrange
# TODO: Set up test data for active_header_is_early
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute active_header_is_early
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_stale_frozen_label_absent(fpath: Path) -> None:
"""Test stale_frozen_label_absent runtime behavior."""
# Arrange
# TODO: Set up test data for stale_frozen_label_absent
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute stale_frozen_label_absent
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
def test_active_header_exact_match_rejects_near_misses(near_miss: str) -> None:
"""Test active_header_exact_match_rejects_near_misses runtime behavior."""
# Arrange
# TODO: Set up test data for active_header_exact_match_rejects_near_misses
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute active_header_exact_match_rejects_near_misses
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_active_header_is_not_a_near_miss(fpath: Path) -> None:
"""Test active_header_is_not_a_near_miss runtime behavior."""
# Arrange
# TODO: Set up test data for active_header_is_not_a_near_miss
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute active_header_is_not_a_near_miss
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
                f"  Near-miss: {near_miss!r}"
            )


# ---------------------------------------------------------------------------
# §1.5 Edge case: file must exist and be non-empty
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_entrypoint_file_is_non_empty(fpath: Path) -> None:
"""Test entrypoint_file_is_non_empty runtime behavior."""
# Arrange
# TODO: Set up test data for entrypoint_file_is_non_empty
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute entrypoint_file_is_non_empty
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
"""Test l0_execute_does_not_exist runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute l0_execute_does_not_exist
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("symbol", V15_REQUIRED_CALLS, ids=list(V15_REQUIRED_CALLS))
def test_v15_bootstrap_symbol_called_in_legacy_main(symbol: str) -> None:
"""Test v15_bootstrap_symbol_called_in_legacy_main runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute v15_bootstrap_symbol_called_in_legacy_main
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
            legacy_main_node = node
            break

    assert legacy_main_node is not None, "_legacy_main function not found in execute_ssot.py"

    call_names = _collect_direct_calls_in_function(legacy_main_node)

    assert symbol in call_names, (
        f"§8.1e: {symbol}() not called directly inside _legacy_main body. "
        f"V15 bootstrap is missing from the SSOT entrypoint. "
        f"Calls found: {sorted(call_names)}"
    )


def test_v15_bootstrap_call_count_is_exactly_one_each() -> None:
"""Test v15_bootstrap_call_count_is_exactly_one_each runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute v15_bootstrap_call_count_is_exactly_one_each
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
            legacy_main_node = node
            break

    assert legacy_main_node is not None, "_legacy_main not found in execute_ssot.py"

    # Count occurrences of each required symbol in the direct body
    counts: dict[str, int] = dict.fromkeys(V15_REQUIRED_CALLS, 0)

    def _count(nodes: list) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if isinstance(node, ast.Call):
                name: str | None = None
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                if name in counts:
                    counts[name] += 1
            for child in ast.iter_child_nodes(node):
                _count([child])

    _count(legacy_main_node.body)

    for sym, count in counts.items():
        assert count == 1, (
            f"§8.1e: {sym}() called {count} time(s) in _legacy_main body; expected exactly 1. "
            f"Duplicate calls risk double-auditing; zero calls break enforcement."
        )
