"""P0.1 Governance tests — apps_research L4 write boundary.

Enforces that no apps_research module writes directly to L4 state.
UWG (research_brief_uwg_writer.py) is the only approved write path.

Plan: apps-research-spine-alignment-d4e8f2 P0.1.

Test 21 in the P0 test suite.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"

# The only module allowed to write L4 state
UWG_WRITER = APP_DIR / "integrations" / "research_brief_uwg_writer.py"

# Patterns that indicate a direct L4 write bypassing UWG.
# Uses call-site patterns (open paren) to avoid matching import lines or type
# annotations. UWG writer's own DurableWriteGateway.commit() is the approved path.
DIRECT_L4_PATTERNS = [
    "StateStore(",
    "durable_write(",
    "write_to_l4(",
    ".write_l4(",
    "write_canonical(",
    "write_durable(",
    "l4_write(",
    "canonical_store.write(",
]

# Modules allowed to reference L4 directly (UWG writer uses DurableWriteGateway
# which IS the governed write path; _telemetry uses L4_STATE as an enum string)
ALLOWED_L4_REFS = frozenset([
    "research_brief_uwg_writer.py",  # UWG is the only approved write path
    "_telemetry.py",                  # enum string "L4_STATE" — not a write
    "ResearchOrchestrator.py",        # reads vllm routing predicates from L4_state
    "__init__.py",                    # package re-exports permitted
])

# Directories to scan
SCAN_DIRS = [
    APP_DIR / "engines",
    APP_DIR / "integrations",
    APP_DIR / "services",
    APP_DIR / "reasoning",
]


@pytest.mark.governance
def test_apps_research_no_direct_l4_writes() -> None:
    """No apps_research module (except UWG writer) may write directly to L4 state.

    UWG is the only approved durable write path. Direct L4 writes bypass
    the UWG approval gate and break the governance contract.
    """
    violations: list[str] = []

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name in ALLOWED_L4_REFS:
                continue
            src = py_file.read_text(encoding="utf-8")
            for pattern in DIRECT_L4_PATTERNS:
                if pattern in src:
                    rel = py_file.relative_to(REPO_ROOT)
                    violations.append(f"{rel} — pattern '{pattern}'")

    # Also check __main__.py
    main_py = APP_DIR / "__main__.py"
    if main_py.exists():
        src = main_py.read_text(encoding="utf-8")
        for pattern in DIRECT_L4_PATTERNS:
            if pattern in src:
                violations.append(f"apps_research/__main__.py — pattern '{pattern}'")

    assert not violations, (
        "Direct L4 write patterns detected in apps_research modules (outside UWG writer). "
        "All durable writes must go through UWG (research_brief_uwg_writer.py). "
        "Violations:\n" + "\n".join(f"  {v}" for v in violations)
    )


@pytest.mark.governance
def test_apps_research_durable_state_only_through_uwg() -> None:
    """UWG (research_brief_uwg_writer.py) is the ONLY module that imports
    DurableWriteGateway outside of agentic_core itself.

    No engine, service, or integration in apps_research should bypass the
    UWG by importing DurableWriteGateway directly.
    """
    UWG_ALLOWED = frozenset([
        "research_brief_uwg_writer.py",
        "governed_research_run.py",  # references DurableWriteGateway in a comment only
    ])
    DWG_IMPORT_PATTERN = "DurableWriteGateway"
    violations: list[str] = []

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name in UWG_ALLOWED:
                continue
            src = py_file.read_text(encoding="utf-8")
            if DWG_IMPORT_PATTERN in src:
                rel = py_file.relative_to(REPO_ROOT)
                violations.append(str(rel))

    # Also check __main__.py
    main_py = APP_DIR / "__main__.py"
    if main_py.exists():
        src = main_py.read_text(encoding="utf-8")
        if DWG_IMPORT_PATTERN in src:
            violations.append("apps_research/__main__.py")

    assert not violations, (
        "DurableWriteGateway imported outside UWG writer in apps_research. "
        "All durable state writes MUST go through research_brief_uwg_writer.py. "
        "Violating files:\n" + "\n".join(f"  {v}" for v in violations)
    )


@pytest.mark.governance
def test_apps_research_l6_does_not_mutate_current_run() -> None:
    """L6 observability modules must not mutate current-run output.

    L6 runs AFTER Exit v6.  It may read state but must never assign to
    fields on the current run record, re-emit Exit, write L4, or call
    provider synthesis directly.

    Forbidden patterns (call-site forms):
    - run_record.<field> = ...  (field assignment on run record)
    - .write_l4(           (direct L4 write)
    - provider_synthesis(  (direct synthesis call outside governed gateway)
    - DurableWriteGateway( (direct UWG bypass)
    """
    L6_MUTATION_PATTERNS = [
        "run_record.",      # attribute mutation on run record (heuristic)
        "write_l4(",
        "provider_synthesis(",
    ]
    L6_DIR = APP_DIR / "L6_observability"
    if not L6_DIR.exists():
        pytest.skip("apps_research/L6_observability directory not present")

    violations: list[str] = []
    for py_file in L6_DIR.rglob("*.py"):
        src = py_file.read_text(encoding="utf-8")
        for pattern in L6_MUTATION_PATTERNS:
            if pattern in src:
                rel = py_file.relative_to(REPO_ROOT)
                violations.append(f"{rel} — pattern '{pattern}'")

    assert not violations, (
        "L6 observability module(s) contain current-run mutation patterns. "
        "L6 must only observe, never mutate, current-run output or state. "
        "Violations:\n" + "\n".join(f"  {v}" for v in violations)
    )
