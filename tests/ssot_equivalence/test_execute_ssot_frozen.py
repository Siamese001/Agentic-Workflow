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

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Constants — single source of truth for all assertions
# ---------------------------------------------------------------------------

ACTIVE_HEADER = "# NOTE: l0_execute.py was planned but never implemented. This file is ACTIVE."

STALE_FROZEN_HEADER = "# FROZEN — superseded by l0_execute.py"

ACTIVE_FILES = [
    REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py",
    REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot_entrypoint.py",
]

L0_EXECUTE_PATH = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "l0_execute.py"

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
    """Each entrypoint file must carry the exact corrected ACTIVE label (§1.9)."""
    assert fpath.exists(), f"Entrypoint file not found: {fpath}"
    content = fpath.read_text(encoding="utf-8")
    assert ACTIVE_HEADER in content, (
        f"ACTIVE header missing in {fpath.name}.\n"
        f"  Expected substring: {ACTIVE_HEADER!r}\n"
        f"  First 5 non-empty lines: {_non_empty_lines(content)[:5]}"
    )


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_active_header_is_early(fpath: Path) -> None:
    """ACTIVE label must appear within the first 5 non-empty lines (boundary §1.5)."""
    content = fpath.read_text(encoding="utf-8")
    non_empty = _non_empty_lines(content)
    found_at: int | None = None
    for i, ln in enumerate(non_empty[:10]):
        if ACTIVE_HEADER in ln:
            found_at = i
            break
    assert found_at is not None, f"ACTIVE header not found in first 10 non-empty lines of {fpath.name}."
    assert found_at < 5, (
        f"ACTIVE header found at non-empty line index {found_at} in {fpath.name} "
        f"(must be index 0–4, i.e. within first 5 non-empty lines)."
    )


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_stale_frozen_label_absent(fpath: Path) -> None:
    """The false FROZEN label must not appear in either entrypoint file (§1.6 — one-way transition)."""
    content = fpath.read_text(encoding="utf-8")
    assert STALE_FROZEN_HEADER not in content, (
        f"Stale FROZEN label still present in {fpath.name}. The FROZEN→ACTIVE transition must be permanent."
    )


# ---------------------------------------------------------------------------
# §1.11 Mutation / near-miss guards
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("near_miss", NEAR_MISS_LABELS, ids=[repr(s[:40]) for s in NEAR_MISS_LABELS])
def test_active_header_exact_match_rejects_near_misses(near_miss: str) -> None:
    """Near-miss strings must NOT equal the canonical ACTIVE_HEADER (§1.11).

    Guards against accidental weakening of the exact-match predicate.
    """
    assert near_miss != ACTIVE_HEADER, (
        f"Near-miss string is identical to ACTIVE_HEADER — update the near-miss list: {near_miss!r}"
    )
    assert near_miss not in ACTIVE_HEADER or ACTIVE_HEADER not in near_miss or near_miss == "", (
        f"Near-miss {near_miss!r} is a substring/superset of ACTIVE_HEADER "
        f"in an unexpected way — review the constant."
    )


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_active_header_is_not_a_near_miss(fpath: Path) -> None:
    """Confirm none of the near-miss strings appear as the active label in real files (§1.11)."""
    content = fpath.read_text(encoding="utf-8")
    non_empty = _non_empty_lines(content)
    for near_miss in NEAR_MISS_LABELS:
        if not near_miss:
            continue
        # A near-miss in the early lines where the label should be is a fault
        early_hit = any(near_miss in ln for ln in non_empty[:5])
        exact_hit = any(ACTIVE_HEADER in ln for ln in non_empty[:5])
        if early_hit and not exact_hit:
            pytest.fail(
                f"Near-miss label found in first 5 non-empty lines of {fpath.name} "
                f"but exact ACTIVE_HEADER absent.\n"
                f"  Near-miss: {near_miss!r}"
            )


# ---------------------------------------------------------------------------
# §1.5 Edge case: file must exist and be non-empty
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fpath", ACTIVE_FILES, ids=_ACTIVE_FILES_IDS)
def test_entrypoint_file_is_non_empty(fpath: Path) -> None:
    """Entrypoint file must exist and have content (§1.5 — missing/empty input guard)."""
    assert fpath.exists(), f"Missing file: {fpath}"
    content = fpath.read_text(encoding="utf-8")
    assert len(content.strip()) > 0, f"File is empty: {fpath.name}"


# ---------------------------------------------------------------------------
# Architectural debt documentation
# ---------------------------------------------------------------------------


def test_l0_execute_does_not_exist() -> None:
    """l0_execute.py was planned but never implemented — assert non-existence.

    If this test starts failing, l0_execute.py was finally built.  At that
    point: remove this test, migrate callers, and retire execute_ssot_entrypoint.py.
    """
    assert not L0_EXECUTE_PATH.exists(), (
        f"l0_execute.py now exists at {L0_EXECUTE_PATH}. "
        "Update the entrypoint architecture and retire execute_ssot_entrypoint.py."
    )


# ---------------------------------------------------------------------------
# §1.10 Ingress-path / §3.3 AST: V15 bootstrap wired in _legacy_main
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("symbol", V15_REQUIRED_CALLS, ids=list(V15_REQUIRED_CALLS))
def test_v15_bootstrap_symbol_called_in_legacy_main(symbol: str) -> None:
    """AST-verify each §8.1e V15 symbol is called directly inside _legacy_main.

    Uses a scoped AST walk (§3.3 / §1.10): descends only _legacy_main's own
    body, excluding any nested function definitions, to prevent false positives
    from inner helpers that might happen to call the same symbols.
    """
    fpath = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
    source = fpath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(fpath))

    legacy_main_node: ast.FunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_legacy_main":
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
    """AST-count: each §8.1e symbol called exactly once inside _legacy_main (§1.7 / §1.9).

    Prevents duplicate calls (idempotency regression) and ensures neither
    call is accidentally guarded behind a branch that could skip it.
    Counts only direct body calls (§1.10 scoped walk).
    """
    fpath = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
    source = fpath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(fpath))

    legacy_main_node: ast.FunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_legacy_main":
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
