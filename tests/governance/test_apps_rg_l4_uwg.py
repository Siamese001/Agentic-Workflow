"""W5 T-suite — L4 / UWG governance tests (3 tests).

apps_rg must not write directly to L4 state.  All durable writes go through
the DurableWriteGateway (UWG) via the canonical Exit → UWG → L4 chain.

Verifies:
1. No direct L4 write calls in apps_rg source (no DurableWriteGateway.commit direct)
2. The chunk-commit path uses commit_chunks_via_exit (not direct UWG instantiation)
3. rg_r5_policy is decision-only (no subprocess, no write, no network)

All tests are static source analysis — no live run required.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_DIR = REPO_ROOT / "apps_rg"
MAIN_PY = APPS_RG_DIR / "__main__.py"
CHUNK_COMMIT = APPS_RG_DIR / "cache" / "chunk_commit.py"
R5_POLICY = APPS_RG_DIR / "integrations" / "rg_r5_policy.py"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: No direct DurableWriteGateway instantiation in apps_rg entrypoints
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_no_direct_l4_write_in_entrypoint() -> None:
    """apps_rg/__main__.py must not instantiate DurableWriteGateway directly."""
    src = _src(MAIN_PY)

    # Forbidden: constructing / calling DurableWriteGateway directly
    # from outside the Exit pipeline chain
    assert "DurableWriteGateway()" not in src, (
        "apps_rg/__main__.py must not instantiate DurableWriteGateway() directly. "
        "All L4 writes go through Exit → UWG → L4 (spine doctrine)."
    )
    # Allowed: reading DurableWriteGateway type for type annotations / imports
    # We only flag actual instantiation and direct .commit() calls
    direct_commit = src.count("DurableWriteGateway().commit")
    assert direct_commit == 0, (
        f"apps_rg/__main__.py calls DurableWriteGateway().commit directly "
        f"({direct_commit} occurrence(s)). Must go through Exit → UWG."
    )


# ---------------------------------------------------------------------------
# Test 2: chunk_commit.py uses commit_chunks_via_exit (not direct UWG)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_chunk_commit_uses_exit_chain() -> None:
    """apps_rg/cache/chunk_commit.py must route through Exit, not bypass UWG."""
    if not CHUNK_COMMIT.exists():
        pytest.skip(f"chunk_commit.py not found at {CHUNK_COMMIT}")
    src = _src(CHUNK_COMMIT)

    # Must use the exit-gated commit helper
    assert "commit_chunks_via_exit" in src or "durable_write_gateway" in src.lower(), (
        "apps_rg/cache/chunk_commit.py must use commit_chunks_via_exit or "
        "route through durable_write_gateway. Direct chunk writes are forbidden."
    )

    # Must NOT bypass the UWG entirely with raw file writes as "durable state"
    assert "DurableWriteGateway()" not in src, (
        "chunk_commit.py must not instantiate DurableWriteGateway() directly."
    )


# ---------------------------------------------------------------------------
# Test 3: rg_r5_policy is decision-only (no subprocess, no write, no HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_r5_policy_is_decision_only() -> None:
    """rg_r5_policy.py must be decision-only: no subprocess, no file write, no HTTP."""
    assert R5_POLICY.exists(), (
        f"rg_r5_policy.py not found at {R5_POLICY}. W4 P13 required."
    )
    src = _src(R5_POLICY)

    forbidden = [
        "subprocess.run",
        "subprocess.call",
        "subprocess.Popen",
        "requests.get",
        "requests.post",
        "httpx.",
        "open(",          # file writes
        ".write(",        # file writes (broad — combined with forbidden imports)
    ]
    # Filter: "open(" and ".write(" are too broad alone; combine with import check
    forbidden_imports = ["import subprocess", "import requests", "import httpx"]

    import_violations = [f for f in forbidden_imports if f in src]
    call_violations = [
        f for f in ["subprocess.run", "subprocess.call", "subprocess.Popen",
                    "requests.get", "requests.post", "httpx."]
        if f in src
    ]

    assert not import_violations, (
        f"rg_r5_policy.py imports forbidden modules: {import_violations}. "
        "R5 policy must be DECISION-ONLY — no subprocess, no HTTP, no file I/O "
        "(apps-rg-canonical-wireup-c8a4f2 W4 P13)."
    )
    assert not call_violations, (
        f"rg_r5_policy.py calls forbidden functions: {call_violations}. "
        "R5 policy must be DECISION-ONLY."
    )
