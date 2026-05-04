"""W7 HITL sentinel — L6 consumption is post-Exit only.

Verifies (static analysis):
1. runtime_author_gate.py does NOT call any L6 record/observe/emit function directly.
2. runtime_author_gate.py does NOT import from agentic_core.L6_observability.
3. cli_hitl_adapter.py has no L6 imports.
4. hitl_replay_store.py has no L6 imports.
5. The HITLReviewPacket carrier does not have an L6-consumer field.

L6 may ONLY consume the human decision after Exit X3 finalizes the run.
The governed_run.__exit__() unwind is the synchronization point.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 sentinel.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HITL_DIR = REPO_ROOT / "apps_rg" / "hitl"

L6_PATTERNS = [
    "L6_observability",
    "record_human_decision(",
    "l6_emit(",
    "learning_bus",
    "from agentic_core.L6",
    "import agentic_core.L6",
    "system_learning",
]


@pytest.mark.governance
def test_apps_rg_hitl_no_l6_in_runtime_author_gate() -> None:
    """runtime_author_gate.py must not directly invoke L6 consumers."""
    gate_file = HITL_DIR / "runtime_author_gate.py"
    assert gate_file.exists(), f"runtime_author_gate.py missing: {gate_file}"
    src = gate_file.read_text(encoding="utf-8")
    found = [p for p in L6_PATTERNS if p in src]
    assert not found, (
        "runtime_author_gate.py must NOT call L6 directly — L6 consumption "
        f"is post-Exit only.\nForbidden references found: {found}"
    )


@pytest.mark.governance
def test_apps_rg_hitl_no_l6_in_cli_hitl_adapter() -> None:
    """cli_hitl_adapter.py must not import or call L6."""
    adapter_file = HITL_DIR / "cli_hitl_adapter.py"
    assert adapter_file.exists(), f"cli_hitl_adapter.py missing: {adapter_file}"
    src = adapter_file.read_text(encoding="utf-8")
    found = [p for p in L6_PATTERNS if p in src]
    assert not found, (
        f"cli_hitl_adapter.py has forbidden L6 references: {found}"
    )


@pytest.mark.governance
def test_apps_rg_hitl_no_l6_in_replay_store() -> None:
    """hitl_replay_store.py must not import or call L6."""
    store_file = HITL_DIR / "hitl_replay_store.py"
    assert store_file.exists(), f"hitl_replay_store.py missing: {store_file}"
    src = store_file.read_text(encoding="utf-8")
    found = [p for p in L6_PATTERNS if p in src]
    assert not found, (
        f"hitl_replay_store.py has forbidden L6 references: {found}"
    )


@pytest.mark.governance
def test_apps_rg_hitl_schemas_no_l6_consumer_field() -> None:
    """HITLReviewPacket must not carry an l6_consumer or learning_signal field."""
    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from apps_rg.hitl.hitl_schemas import HITLReviewPacket
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(HITLReviewPacket)}
    forbidden_fields = {"l6_consumer", "learning_signal", "l6_emit", "record_human_decision"}
    found = field_names & forbidden_fields
    assert not found, (
        f"HITLReviewPacket must not carry L6 consumer fields: {found}. "
        "L6 consumption is wired by the caller after Exit finalizes."
    )
