"""DS-2 Governance sentinels for apps_research HOP inner-DAG discipline.

DS-2 was originally scoped as "wire apps_research managed-workflow dispatcher
(L0→L3→2-step L2)".  Investigation found the assumption was incorrect:
apps_research already has a 3-stage HOP inner-DAG (ResearchHopOrchestrator)
running INSIDE the R3_grounded_read substrate, not as a separate L3
managed-workflow route.

The cert_route_registry declares:
  - execution_form: SINGLE_STEP
  - l3_required: false
  - invoke_exit_eval: true

DS-2 is therefore closed as: governance tests that lock this correct invariant
and prevent accidental future drift to R3R4_managed_workflow semantics.

Tests cover:
1. cert_route_registry declares SINGLE_STEP (not MANAGED_WORKFLOW).
2. cert_route_registry has l3_required: false.
3. spine_manifest does NOT claim R3R4_managed_workflow.
4. hop_pipeline.py declares exactly 3 stages (not a 2-step L2 plan).
5. ResearchHopOrchestrator runs INSIDE GovernedResearchRun (substrate-bounded).
6. No direct L3_orchestration managed_workflow import from apps_research __main__.

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-2.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"
MANIFEST = APP_DIR / "spine_manifest.yaml"
CERT_REGISTRY = APP_DIR / "config" / "cert_route_registry.yaml"
HOP_PIPELINE = APP_DIR / "config" / "hop_pipeline.py"
GOVERNED_RUN = APP_DIR / "integrations" / "governed_research_run.py"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.governance
def test_apps_research_cert_registry_declares_single_step() -> None:
    """cert_route_registry must declare execution_form: SINGLE_STEP, not MANAGED_WORKFLOW."""
    assert CERT_REGISTRY.exists(), f"cert_route_registry.yaml missing: {CERT_REGISTRY}"
    doc = yaml.safe_load(CERT_REGISTRY.read_text(encoding="utf-8"))
    routes = doc.get("routes", [])
    assert routes, "cert_route_registry.yaml has no routes"
    forms = [r.get("execution_form") for r in routes]
    assert all(f == "SINGLE_STEP" for f in forms), (
        f"apps_research cert_route_registry must declare execution_form=SINGLE_STEP. "
        f"Found: {forms}. DS-2 investigation confirmed apps_research is R3_grounded_read "
        "with a HOP inner-DAG, not a managed-workflow route."
    )


@pytest.mark.governance
def test_apps_research_cert_registry_l3_not_required() -> None:
    """cert_route_registry must set l3_required: false for all routes."""
    assert CERT_REGISTRY.exists()
    doc = yaml.safe_load(CERT_REGISTRY.read_text(encoding="utf-8"))
    routes = doc.get("routes", [])
    for r in routes:
        assert r.get("l3_required") is False, (
            f"apps_research cert_route_registry route '{r.get('route_id')}' has "
            f"l3_required={r.get('l3_required')}. Must be false — apps_research does "
            "not use an L3 managed-workflow dispatcher."
        )


@pytest.mark.governance
def test_apps_research_manifest_does_not_claim_managed_workflow() -> None:
    """spine_manifest must NOT claim R3R4_managed_workflow or any managed-workflow variant."""
    assert MANIFEST.exists(), f"spine_manifest.yaml missing: {MANIFEST}"
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    types = [r.get("type", "") for r in routes]
    bad = [t for t in types if "managed" in t.lower() or "R3R4" in t]
    assert not bad, (
        f"apps_research spine_manifest must not claim managed-workflow route types. "
        f"Found: {bad}. Apps_research is strictly R3_grounded_read."
    )


@pytest.mark.governance
def test_apps_research_hop_pipeline_has_three_stages() -> None:
    """hop_pipeline.py must declare exactly 3 stages (retrieve→brief→assemble)."""
    assert HOP_PIPELINE.exists(), f"hop_pipeline.py missing: {HOP_PIPELINE}"
    src = _src(HOP_PIPELINE)
    tree = ast.parse(src)
    # Count HopStageSpec(...) instantiations
    stage_count = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "HopStageSpec"
    )
    assert stage_count == 3, (
        f"apps_research hop_pipeline.py must have exactly 3 HopStageSpec stages. "
        f"Found {stage_count}. The 3-stage topology is: research_retrieval → "
        "company_brief → research_assembly."
    )


@pytest.mark.governance
def test_apps_research_hop_pipeline_stage_ids_are_sequential() -> None:
    """hop_pipeline.py stages must have stage_id 1, 2, 3 in order."""
    assert HOP_PIPELINE.exists()
    doc = _src(HOP_PIPELINE)
    tree = ast.parse(doc)
    stage_ids: list[int] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "HopStageSpec"
        ):
            for kw in node.keywords:
                if kw.arg == "stage_id" and isinstance(kw.value, ast.Constant):
                    stage_ids.append(kw.value.value)
    assert sorted(stage_ids) == [1, 2, 3], (
        f"apps_research hop_pipeline stage_ids must be [1, 2, 3]. Found: {sorted(stage_ids)}"
    )


@pytest.mark.governance
def test_apps_research_hop_orchestrator_bounded_inside_governed_run() -> None:
    """ResearchHopOrchestrator must be called inside GovernedResearchRun, not __main__."""
    assert GOVERNED_RUN.exists(), f"governed_research_run.py missing: {GOVERNED_RUN}"
    governed_src = _src(GOVERNED_RUN)
    assert "ResearchHopOrchestrator" in governed_src, (
        "GovernedResearchRun must drive ResearchHopOrchestrator. "
        "HOP inner-DAG must be substrate-bounded, not floating in __main__."
    )
    # __main__.py must NOT import ResearchHopOrchestrator directly
    # (it should go through GovernedResearchRun)
    if MAIN_PY.exists():
        main_src = _src(MAIN_PY)
        assert "ResearchHopOrchestrator" not in main_src, (
            "apps_research/__main__.py must not import ResearchHopOrchestrator directly. "
            "HOP orchestration is substrate-internal — route through GovernedResearchRun."
        )


@pytest.mark.governance
def test_apps_research_main_no_managed_workflow_import() -> None:
    """__main__.py must not import L3 managed_workflow dispatcher."""
    if not MAIN_PY.exists():
        pytest.skip("__main__.py not found")
    src = _src(MAIN_PY)
    forbidden = [
        "managed_workflow",
        "R3R4_managed",
        "ManagedWorkflowDispatcher",
        "managed_workflow_router",
    ]
    found = [f for f in forbidden if f in src]
    assert not found, (
        f"apps_research/__main__.py must not reference managed-workflow constructs: {found}. "
        "apps_research uses R3_grounded_read + HOP inner-DAG — not a managed-workflow route."
    )
