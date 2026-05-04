"""DS-1 Governance sentinels for apps_rfp canonical spine wireup.

Static-analysis tests verifying that apps_rfp is wired correctly onto the
canonical R3_grounded_read spine:

1. spine_manifest.yaml declares R3_grounded_read (no portal submission).
2. __main__.py routes through GovernedRfpRun / GovernedAppRunner.
3. No L0 subprocess to sibling apps.
4. spine_handoff.py exists and delegates to GovernedRfpRun.
5. governed_rfp_run.py inherits from GovernedAppRunner.
6. Manifest explicitly disclaims CommitRequest and portal submission.
7. No real UWG call — ExecutionAdapter.submit is in-memory log only.

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-1.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_rfp"
MAIN_PY = APP_DIR / "__main__.py"
MANIFEST = APP_DIR / "spine_manifest.yaml"
SPINE_HANDOFF = APP_DIR / "integrations" / "spine_handoff.py"
GOVERNED_RUN = APP_DIR / "integrations" / "governed_rfp_run.py"
EXECUTION_ADAPTER = APP_DIR / "integrations" / "execution_adapter.py"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.governance
def test_apps_rfp_manifest_claims_r3_grounded_read() -> None:
    """apps_rfp produces grounded RFP proposals — must claim R3_grounded_read."""
    assert MANIFEST.exists(), f"spine_manifest.yaml missing: {MANIFEST}"
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    assert routes, "spine_manifest.yaml has no claimed_routes"
    types = [r.get("type") for r in routes]
    assert "R3_grounded_read" in types, (
        f"apps_rfp/spine_manifest.yaml must claim R3_grounded_read. Found: {types}"
    )
    assert "R4_SINGLE_ACTION" not in types, (
        "apps_rfp must not claim R4_SINGLE_ACTION — no static L2 DAG recipe."
    )
    assert "R3R4_managed_workflow" not in types, (
        "apps_rfp must not claim R3R4_managed_workflow — audit confirmed zero "
        "CommitRequest / durable-write surface."
    )


@pytest.mark.governance
def test_apps_rfp_main_routes_through_governed_substrate() -> None:
    """__main__.py must call GovernedRfpRun, GovernedAppRunner, or governed_run."""
    assert MAIN_PY.exists(), f"__main__.py missing: {MAIN_PY}"
    src = _src(MAIN_PY)
    governed_markers = [
        "GovernedRfpRun",
        "GovernedAppRunner",
        "governed_run",
        "spine_handoff",
    ]
    assert any(m in src for m in governed_markers), (
        "apps_rfp/__main__.py must route through the governed substrate. "
        f"None of {governed_markers} found."
    )


@pytest.mark.governance
def test_apps_rfp_no_subprocess_to_sibling_apps() -> None:
    """L0 must be DECISION-ONLY. No subprocess calling sibling apps."""
    src = _src(MAIN_PY)
    bad = re.findall(
        r'subprocess\.\w+\s*\(\s*\[.*?apps_(research|exec|lic|rg|qna).*?\]',
        src,
        re.DOTALL,
    )
    assert not bad, (
        f"apps_rfp/__main__.py subprocess to sibling app detected: {bad}"
    )


@pytest.mark.governance
def test_apps_rfp_spine_handoff_delegates_to_governed_run() -> None:
    """spine_handoff.py must exist and delegate to GovernedRfpRun."""
    assert SPINE_HANDOFF.exists(), f"spine_handoff.py missing: {SPINE_HANDOFF}"
    src = _src(SPINE_HANDOFF)
    assert "GovernedRfpRun" in src, (
        "apps_rfp/integrations/spine_handoff.py must delegate to GovernedRfpRun."
    )


@pytest.mark.governance
def test_apps_rfp_governed_run_inherits_governed_app_runner() -> None:
    """governed_rfp_run.py must subclass GovernedAppRunner."""
    assert GOVERNED_RUN.exists(), f"governed_rfp_run.py missing: {GOVERNED_RUN}"
    src = _src(GOVERNED_RUN)
    assert "GovernedAppRunner" in src, (
        "apps_rfp/integrations/governed_rfp_run.py must inherit from GovernedAppRunner."
    )


@pytest.mark.governance
def test_apps_rfp_manifest_disclaims_l4_write_and_portal_submission() -> None:
    """Manifest must disclaim CommitRequest AND portal submission."""
    assert MANIFEST.exists()
    text = MANIFEST.read_text(encoding="utf-8")
    assert "CommitRequest" in text and "No CommitRequest" in text, (
        "apps_rfp/spine_manifest.yaml must disclaim CommitRequest."
    )
    assert "portal" in text.lower() and (
        "no portal" in text.lower() or "out of scope" in text.lower()
    ), (
        "apps_rfp/spine_manifest.yaml must disclaim portal submission "
        "(R3 not R3R4 — no portal API calls)."
    )


@pytest.mark.governance
def test_apps_rfp_execution_adapter_submit_is_in_memory_only() -> None:
    """ExecutionAdapter.submit must be an in-memory log append, not a real UWG call."""
    assert EXECUTION_ADAPTER.exists(), f"execution_adapter.py missing: {EXECUTION_ADAPTER}"
    src = _src(EXECUTION_ADAPTER)
    # Must have a submit method
    assert "def submit" in src or "submit" in src, (
        "apps_rfp/integrations/execution_adapter.py has no submit surface."
    )
    # Must NOT call DurableWriteGateway or UWG admission
    forbidden = ["DurableWriteGateway(", "uwg.commit(", "write_gateway.admit("]
    found = [f for f in forbidden if f in src]
    assert not found, (
        f"apps_rfp/integrations/execution_adapter.py must not call UWG: {found}. "
        "submit() is an in-memory log append per the manifest audit."
    )
