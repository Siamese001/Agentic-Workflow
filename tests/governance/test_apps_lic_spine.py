"""DS-1 Governance sentinels for apps_lic canonical spine wireup.

Static-analysis tests verifying that apps_lic is wired correctly onto the
canonical R3_grounded_read spine:

1. spine_manifest.yaml declares R3_grounded_read.
2. __main__.py routes through GovernedLicRun / GovernedAppRunner.
3. No L0 subprocess to sibling apps.
4. spine_handoff.py exists and delegates to GovernedLicRun.
5. governed_lic_run.py inherits from GovernedAppRunner.
6. Manifest explicitly disclaims CommitRequest / L4 durable writes.

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-1.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_lic"
MAIN_PY = APP_DIR / "__main__.py"
MANIFEST = APP_DIR / "spine_manifest.yaml"
SPINE_HANDOFF = APP_DIR / "integrations" / "spine_handoff.py"
GOVERNED_RUN = APP_DIR / "integrations" / "governed_lic_run.py"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.governance
def test_apps_lic_manifest_claims_r3_grounded_read() -> None:
    """apps_lic produces grounded message drafts — must claim R3_grounded_read."""
    assert MANIFEST.exists(), f"spine_manifest.yaml missing: {MANIFEST}"
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    assert routes, "spine_manifest.yaml has no claimed_routes"
    types = [r.get("type") for r in routes]
    assert "R3_grounded_read" in types, (
        f"apps_lic/spine_manifest.yaml must claim R3_grounded_read. Found: {types}"
    )
    assert "R4_SINGLE_ACTION" not in types, (
        "apps_lic must not claim R4_SINGLE_ACTION — no static L2 DAG recipe."
    )


@pytest.mark.governance
def test_apps_lic_main_routes_through_governed_substrate() -> None:
    """__main__.py must call GovernedLicRun, GovernedAppRunner, or governed_run."""
    assert MAIN_PY.exists(), f"__main__.py missing: {MAIN_PY}"
    src = _src(MAIN_PY)
    governed_markers = [
        "GovernedLicRun",
        "GovernedAppRunner",
        "governed_run",
        "spine_handoff",
    ]
    assert any(m in src for m in governed_markers), (
        "apps_lic/__main__.py must route through the governed substrate. "
        f"None of {governed_markers} found."
    )


@pytest.mark.governance
def test_apps_lic_no_subprocess_to_sibling_apps() -> None:
    """L0 must be DECISION-ONLY. No subprocess calling sibling apps."""
    import re
    src = _src(MAIN_PY)
    bad = re.findall(
        r'subprocess\.\w+\s*\(\s*\[.*?apps_(research|exec|rfp|rg|qna).*?\]',
        src,
        re.DOTALL,
    )
    assert not bad, (
        f"apps_lic/__main__.py subprocess to sibling app detected: {bad}"
    )


@pytest.mark.governance
def test_apps_lic_spine_handoff_delegates_to_governed_run() -> None:
    """spine_handoff.py must exist and delegate to GovernedLicRun."""
    assert SPINE_HANDOFF.exists(), f"spine_handoff.py missing: {SPINE_HANDOFF}"
    src = _src(SPINE_HANDOFF)
    assert "GovernedLicRun" in src, (
        "apps_lic/integrations/spine_handoff.py must delegate to GovernedLicRun."
    )


@pytest.mark.governance
def test_apps_lic_governed_run_inherits_governed_app_runner() -> None:
    """governed_lic_run.py must subclass GovernedAppRunner."""
    assert GOVERNED_RUN.exists(), f"governed_lic_run.py missing: {GOVERNED_RUN}"
    src = _src(GOVERNED_RUN)
    assert "GovernedAppRunner" in src, (
        "apps_lic/integrations/governed_lic_run.py must inherit from GovernedAppRunner."
    )


@pytest.mark.governance
def test_apps_lic_manifest_disclaims_l4_write() -> None:
    """Manifest notes must disclaim CommitRequest / L4 durable write surface."""
    assert MANIFEST.exists()
    text = MANIFEST.read_text(encoding="utf-8")
    # Manifest must contain a note that no CommitRequest is present
    assert "CommitRequest" in text and ("No CommitRequest" in text or "no commit" in text.lower()), (
        "apps_lic/spine_manifest.yaml must explicitly disclaim CommitRequest / durable writes "
        "to document why R3 (not R3R4) is correct."
    )
