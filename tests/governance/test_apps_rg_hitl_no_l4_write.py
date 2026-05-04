"""W7 HITL sentinel — no direct L4 write from HITL layer.

Verifies:
1. runtime_author_gate.py has no direct DurableWriteGateway instantiation.
2. runtime_author_gate.py has no direct L4_state imports (other than via Exit).
3. hitl_replay_store.py writes only to local JSONL — no L4/UWG imports.
4. All apps_rg/hitl/ modules combined contain zero DurableWriteGateway references.

Durable writes and cache promotions after HITL must go through Exit → UWG → L4.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 sentinel.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HITL_DIR = REPO_ROOT / "apps_rg" / "hitl"

FORBIDDEN_PATTERNS = [
    "DurableWriteGateway(",
    "DurableWriteGateway()",
    "from agentic_core.L4_state",
    "import agentic_core.L4_state",
    "from agentic_core.L4",
    ".commit_to_l4(",
    "l4_write(",
]


@pytest.mark.governance
def test_apps_rg_hitl_no_durable_write_gateway_in_hitl_dir() -> None:
    """No apps_rg/hitl/ module may instantiate or import DurableWriteGateway."""
    assert HITL_DIR.exists(), f"apps_rg/hitl/ directory not found: {HITL_DIR}"
    violations: list[str] = []
    for py_file in sorted(HITL_DIR.rglob("*.py")):
        src = py_file.read_text(encoding="utf-8")
        for pat in FORBIDDEN_PATTERNS:
            if pat in src:
                rel = py_file.relative_to(REPO_ROOT)
                violations.append(f"{rel}: contains {pat!r}")

    assert not violations, (
        "HITL layer must not write L4 directly. All durable writes go through "
        "Exit → UWG → L4.\nViolations:\n" + "\n".join(f"  {v}" for v in violations)
    )


@pytest.mark.governance
def test_apps_rg_runtime_author_gate_no_l4_import() -> None:
    """runtime_author_gate.py specifically must have zero L4 state imports."""
    gate_file = HITL_DIR / "runtime_author_gate.py"
    assert gate_file.exists(), f"runtime_author_gate.py not found: {gate_file}"
    src = gate_file.read_text(encoding="utf-8")
    l4_patterns = [p for p in FORBIDDEN_PATTERNS if "L4" in p or "commit_to_l4" in p or "l4_write" in p]
    found = [p for p in l4_patterns if p in src]
    assert not found, (
        f"runtime_author_gate.py contains direct L4 imports: {found}. "
        "HITL core must not write L4; use Exit → UWG → L4 path."
    )


@pytest.mark.governance
def test_apps_rg_hitl_replay_store_no_uwg_import() -> None:
    """hitl_replay_store.py must not import UWG or L4 — it writes JSONL only."""
    store_file = HITL_DIR / "hitl_replay_store.py"
    assert store_file.exists(), f"hitl_replay_store.py not found: {store_file}"
    src = store_file.read_text(encoding="utf-8")
    forbidden = ["DurableWriteGateway", "L4_state", "UWG", "uwg"]
    found = [f for f in forbidden if f in src]
    assert not found, (
        f"hitl_replay_store.py must write JSONL only — found forbidden refs: {found}"
    )
