"""P0.1 Governance tests — apps_underwriting_ai L4 write boundary.

Enforces that durable writes to L4 state are never made directly from
__main__.py, the capability registry, or the integration stub files.
All durable writes must flow through UWG (UnderwritingWriteGateway/UWG_ONLY).

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P0.1 / P0.4.

Tests 22–23 (L4 write boundary group). Both pass immediately after P0
because the stub files and capability registry contain no L4 write surfaces.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
INTEGRATIONS_DIR = APP_DIR / "integrations"

_L4_FORBIDDEN = [
    "L4_state",
    "durable_write_call",
    "write_gateway",
    "uwg_writer",
    "canonical_store",
    "commit_request",
    "CommitRequest",
    "StateDiffCandidate",
    "MutationIntent",
    "ledger_write",
    "policy_issue",
    "loan_book",
    "import apps_underwriting_ai.L4",
    "from agentic_core.L4",
]

_STUB_FILES = [
    "underwriting_capability_registry.py",
    "underwriting_c0_adapter.py",
    "underwriting_l3_workflow_adapter.py",
    "underwriting_l2_step_adapters.py",
    "underwriting_exit_fec_producer.py",
]


def _check_no_l4_writes(path: Path, label: str) -> None:
    """Assert that no L4 write surface symbols appear in the source."""
    assert path.exists(), f"{label} missing: {path}"
    src = path.read_text(encoding="utf-8")
    found = [f for f in _L4_FORBIDDEN if f in src]
    assert not found, (
        f"{label} contains L4 write surface references: {found}. "
        "All durable writes must flow through UWG only (durable_write_path=UWG_ONLY). "
        "Direct L4 writes are forbidden."
    )


# ---------------------------------------------------------------------------
# 22. No L4 write surfaces in P0 stub files
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_p0_stubs_contain_no_l4_writes() -> None:
    """All P0.3 integration stub files must not reference L4 write surfaces."""
    for stub_name in _STUB_FILES:
        stub_path = INTEGRATIONS_DIR / stub_name
        _check_no_l4_writes(stub_path, f"apps_underwriting_ai/integrations/{stub_name}")


# ---------------------------------------------------------------------------
# 23. exit_fec_producer stub declares UWG_ONLY durable write path
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_exit_fec_producer_declares_uwg_only() -> None:
    """underwriting_exit_fec_producer.py must declare DURABLE_WRITE_PATH='UWG_ONLY'.

    The stub must already encode the durable-write discipline so that
    W5.2 cannot silently drop this invariant when implementing the full path.
    """
    exit_producer = INTEGRATIONS_DIR / "underwriting_exit_fec_producer.py"
    assert exit_producer.exists(), (
        f"underwriting_exit_fec_producer.py missing: {exit_producer}"
    )
    src = exit_producer.read_text(encoding="utf-8")
    assert "UWG_ONLY" in src, (
        "underwriting_exit_fec_producer.py must declare DURABLE_WRITE_PATH='UWG_ONLY'. "
        "This constant is the machine-readable contract that W5.2 must honor."
    )
    assert "FAIL_CLOSED" in src, (
        "underwriting_exit_fec_producer.py must declare EXIT_MODE='FAIL_CLOSED'. "
        "The Exit discipline requires fail-closed on any missing precondition."
    )
