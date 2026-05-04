"""DS-1 Governance sentinels for apps_exec canonical spine wireup.

Static-analysis tests verifying that apps_exec is wired correctly onto the
canonical R3_grounded_read spine:

1. spine_manifest.yaml declares R3_grounded_read (correct route family).
2. __main__.py routes through the governed substrate (GovernedAppRunner /
   GovernedExecRun), not directly into the engine.
3. No L0 subprocess call targeting sibling apps.
4. spine_handoff.py exists and delegates to GovernedExecRun.
5. governed_exec_run.py inherits from GovernedAppRunner (or equivalent).

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-1.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_exec"
MAIN_PY = APP_DIR / "__main__.py"
MANIFEST = APP_DIR / "spine_manifest.yaml"
SPINE_HANDOFF = APP_DIR / "integrations" / "spine_handoff.py"
GOVERNED_RUN = APP_DIR / "integrations" / "governed_exec_run.py"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: spine_manifest.yaml declares the correct route family
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_exec_manifest_claims_r3_grounded_read() -> None:
    """apps_exec is a grounded read app — must claim R3_grounded_read."""
    assert MANIFEST.exists(), f"spine_manifest.yaml missing: {MANIFEST}"
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    assert routes, "spine_manifest.yaml has no claimed_routes"
    types = [r.get("type") for r in routes]
    assert "R3_grounded_read" in types, (
        f"apps_exec/spine_manifest.yaml must claim R3_grounded_read. "
        f"Found: {types}"
    )
    # Must NOT claim R4 (no static DAG recipe, no L2 deterministic pipeline)
    assert "R4_SINGLE_ACTION" not in types, (
        "apps_exec claims R4_SINGLE_ACTION but has no static L2 DAG recipe — "
        "correct family is R3_grounded_read."
    )


# ---------------------------------------------------------------------------
# Test 2: __main__.py routes through the governed substrate
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_exec_main_routes_through_governed_substrate() -> None:
    """__main__.py must call GovernedExecRun, GovernedAppRunner, or governed_run."""
    assert MAIN_PY.exists(), f"__main__.py missing: {MAIN_PY}"
    src = _src(MAIN_PY)
    governed_markers = [
        "GovernedExecRun",
        "GovernedAppRunner",
        "governed_run",
        "spine_handoff",
    ]
    assert any(m in src for m in governed_markers), (
        "apps_exec/__main__.py must route through the governed substrate. "
        f"None of {governed_markers} found."
    )


# ---------------------------------------------------------------------------
# Test 3: no L0 subprocess to sibling apps
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_exec_no_subprocess_to_sibling_apps() -> None:
    """L0 must be DECISION-ONLY. No subprocess calling sibling apps."""
    import re
    src = _src(MAIN_PY)
    bad = re.findall(
        r'subprocess\.\w+\s*\(\s*\[.*?apps_(research|lic|rfp|rg|qna).*?\]',
        src,
        re.DOTALL,
    )
    assert not bad, (
        "apps_exec/__main__.py contains subprocess targeting a sibling app. "
        f"L0 must be DECISION-ONLY. Found: {bad}"
    )


# ---------------------------------------------------------------------------
# Test 4: spine_handoff.py exists and references GovernedExecRun
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_exec_spine_handoff_delegates_to_governed_run() -> None:
    """spine_handoff.py must exist and delegate to GovernedExecRun."""
    assert SPINE_HANDOFF.exists(), f"spine_handoff.py missing: {SPINE_HANDOFF}"
    src = _src(SPINE_HANDOFF)
    assert "GovernedExecRun" in src, (
        "apps_exec/integrations/spine_handoff.py must delegate to GovernedExecRun."
    )


# ---------------------------------------------------------------------------
# Test 5: governed_exec_run.py inherits GovernedAppRunner
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_exec_governed_run_inherits_governed_app_runner() -> None:
    """governed_exec_run.py must subclass GovernedAppRunner."""
    assert GOVERNED_RUN.exists(), f"governed_exec_run.py missing: {GOVERNED_RUN}"
    src = _src(GOVERNED_RUN)
    assert "GovernedAppRunner" in src, (
        "apps_exec/integrations/governed_exec_run.py must inherit from GovernedAppRunner."
    )


# ---------------------------------------------------------------------------
# Test 6: no direct engine call bypassing governed substrate in main()
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_exec_no_direct_engine_bypass_in_main() -> None:
    """__main__.py must not import the engine directly and call it outside governed_run."""
    import ast
    assert MAIN_PY.exists()
    src = _src(MAIN_PY)
    # Forbidden: direct import of the exec engine bypassing governance
    forbidden = [
        "from apps_exec.engines",
        "import apps_exec.engines",
    ]
    # These are only forbidden if they appear OUTSIDE _run_live_cert context
    # (i.e., in the main() non-cert path). We check structurally.
    for pattern in forbidden:
        if pattern in src:
            # Check it's only used inside _run_live_cert or similar wrapper
            # For simplicity: if main() body directly references exec engine, flag it
            lines = [l.strip() for l in src.splitlines() if pattern in l]
            # Acceptable: only inside _run_live_cert helper; not in bare module scope
            for line in lines:
                if not line.startswith("#"):
                    pytest.fail(
                        f"apps_exec/__main__.py directly imports exec engine: {line!r}. "
                        "All execution must flow through the governed substrate."
                    )
