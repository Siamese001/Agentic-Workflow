"""DS-1 Governance sentinels for apps_lic spine hard-delete convergence.

Static-analysis tests verifying:
1. Product CLI routes through ``canonical_dispatch`` only.
2. Final L0 route families (R4/R3R4/R5) are declared in spine_manifest.yaml.
3. No L0 subprocess to sibling apps.
4. Shadow pipelines (GovernedLic, integrated_r4, spine_handoff) are deleted.

Plan: apps-lic-spine-product-convergence hard-delete.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_lic"
MAIN_PY = APP_DIR / "__main__.py"
MANIFEST = APP_DIR / "spine_manifest.yaml"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.governance
def test_apps_lic_manifest_claims_final_l0_routes() -> None:
    """Manifest must declare R4 and R3R4 managed workflow (not legacy R3-only)."""
    assert MANIFEST.exists(), f"spine_manifest.yaml missing: {MANIFEST}"
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    assert routes, "spine_manifest.yaml has no claimed_routes"
    types = [r.get("type") for r in routes]
    assert "R4_SINGLE_ACTION" in types or "R4_MANAGED_DRAFT" in types, (
        f"apps_lic spine manifest must claim R4 outreach path. Found: {types}"
    )
    assert "R3R4_MANAGED_WORKFLOW" in types, (
        f"apps_lic spine manifest must claim R3R4 research-then-draft. Found: {types}"
    )
    assert "R3_grounded_read" not in types, (
        "Legacy R3_grounded_read must not be the sole claimed route."
    )


@pytest.mark.governance
def test_apps_lic_main_routes_through_canonical_dispatch() -> None:
    """Product __main__.py must call run_canonical_apps_lic_spine only."""
    assert MAIN_PY.exists(), f"__main__.py missing: {MAIN_PY}"
    src = _src(MAIN_PY)
    assert "run_canonical_apps_lic_spine" in src
    assert "build_cli_ingress_raw" in src
    assert "run_integrated_r4_lic_pipeline" not in src
    assert "_run_legacy_integrated_r4" not in src
    assert "APPS_LIC_ALLOW_LEGACY_R4" not in src
    import ast
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "governed_lic_run" not in node.module
            assert "spine_handoff" not in node.module


@pytest.mark.governance
def test_apps_lic_no_subprocess_to_sibling_apps() -> None:
    """L0 must be DECISION-ONLY. No subprocess calling sibling apps."""
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
def test_apps_lic_shadow_integrations_deleted() -> None:
    """GovernedLic and spine_handoff must not exist on disk."""
    assert not (APP_DIR / "integrations" / "spine_handoff.py").exists()
    assert not (APP_DIR / "integrations" / "governed_lic_run.py").exists()
    assert not (
        REPO_ROOT / "agentic_core" / "runtime" / "entrypoints"
        / "integrated_r4_lic_pipeline_run.py"
    ).exists()


@pytest.mark.governance
def test_apps_lic_manifest_disclaims_l4_write() -> None:
    """Manifest notes must disclaim CommitRequest / L4 durable write surface."""
    assert MANIFEST.exists()
    text = MANIFEST.read_text(encoding="utf-8")
    assert "CommitRequest" in text and (
        "No CommitRequest" in text or "no commit" in text.lower()
    ), (
        "apps_lic/spine_manifest.yaml must explicitly disclaim CommitRequest."
    )
