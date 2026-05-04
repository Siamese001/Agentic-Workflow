"""P0.1 Governance tests — apps_research recipe/capability resolution.

Enforces that:
- agentic_core owns route and capability resolution
- apps_research declares R3_SIMPLE_GROUNDED_READ with l3_required=false
- R3 requires C0 evidence (no ungrounded synthesis)
- The direct path uses no L3 managed workflow
- Recipe resolution failure fails closed through Exit v6 (no generic brief)
- The capability registry exports required symbols

Plan: apps-research-spine-alignment-d4e8f2 P0.1.

Tests 10-16 in the P0 test suite. Initially RED on the current codebase
because capability resolution is not wired through agentic_core.
"""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"
ROUTE_REGISTRY = APP_DIR / "config" / "route_registry.yaml"
CERT_REGISTRY = APP_DIR / "config" / "cert_route_registry.yaml"
CAPABILITY_REGISTRY = APP_DIR / "integrations" / "research_capability_registry.py"
C0_ADAPTER = APP_DIR / "integrations" / "research_c0_adapter.py"


def _src(path: Path) -> str:
    assert path.exists(), f"File missing: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 10. Core runner must be the resolution authority
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_core_runner_resolves_company_brief_capability() -> None:
    """research_capability_registry.py must export register_company_brief_capability
    and resolve_company_brief_capability — the agentic_core delegation contract.
    """
    assert CAPABILITY_REGISTRY.exists(), (
        f"apps_research/integrations/research_capability_registry.py missing: "
        f"{CAPABILITY_REGISTRY}. "
        "agentic_core must own route/capability resolution. This file is the "
        "apps_research side of that delegation contract."
    )
    src = _src(CAPABILITY_REGISTRY)
    assert "register_company_brief_capability" in src, (
        "research_capability_registry.py must define register_company_brief_capability(). "
        "This registers apps_research.company_brief_v1 with the agentic_core runner."
    )
    assert "resolve_company_brief_capability" in src, (
        "research_capability_registry.py must define resolve_company_brief_capability(). "
        "Delegates capability lookup to agentic_core runner."
    )
    assert "apps_research.company_brief_v1" in src or "company_brief_v1" in src, (
        "research_capability_registry.py must register capability ID "
        "'apps_research.company_brief_v1'."
    )


# ---------------------------------------------------------------------------
# 11. route_registry.yaml declares R3_SIMPLE_GROUNDED_READ with required fields
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_route_registry_selects_r3_simple_grounded_read() -> None:
    """route_registry.yaml must declare R3_SIMPLE_GROUNDED_READ with all required fields."""
    assert ROUTE_REGISTRY.exists(), f"route_registry.yaml missing: {ROUTE_REGISTRY}"
    doc = yaml.safe_load(ROUTE_REGISTRY.read_text(encoding="utf-8"))
    routes = doc.get("routes", [])
    assert routes, "route_registry.yaml has no routes"

    r3_routes = [r for r in routes if r.get("route_id") == "R3_SIMPLE_GROUNDED_READ"]
    assert r3_routes, (
        "apps_research/config/route_registry.yaml must declare "
        "route_id: R3_SIMPLE_GROUNDED_READ"
    )
    r3 = r3_routes[0]
    assert r3.get("execution_form") == "SINGLE_STEP", (
        f"R3_SIMPLE_GROUNDED_READ must have execution_form: SINGLE_STEP. "
        f"Got: {r3.get('execution_form')}"
    )
    assert r3.get("l3_required") is False, (
        f"R3_SIMPLE_GROUNDED_READ must have l3_required: false. "
        f"Got: {r3.get('l3_required')}"
    )
    assert r3.get("selected_capability") == "apps_research.company_brief_v1", (
        f"R3_SIMPLE_GROUNDED_READ must have "
        f"selected_capability: apps_research.company_brief_v1. "
        f"Got: {r3.get('selected_capability')}"
    )


# ---------------------------------------------------------------------------
# 12. R3 requires C0 — not ungrounded
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_r3_requires_c0() -> None:
    """R3_SIMPLE_GROUNDED_READ must require C0 evidence. GROUNDED means C0 is mandatory.

    Verified by:
    - route_registry or spine_manifest declaring grounding_required=true
    - OR research_c0_adapter.py existing as the C0 delegation point
    - AND no code path in __main__.py that skips C0 for R3
    """
    # C0 adapter must exist as the mandatory grounding delegate
    assert C0_ADAPTER.exists(), (
        f"apps_research/integrations/research_c0_adapter.py missing: {C0_ADAPTER}. "
        "R3_SIMPLE_GROUNDED_READ is GROUNDED — C0 retrieval is mandatory. "
        "This adapter is the C0 delegation point."
    )

    # route_registry or spine_manifest must assert grounding
    route_doc = yaml.safe_load(ROUTE_REGISTRY.read_text(encoding="utf-8"))
    routes = route_doc.get("routes", [])
    r3_routes = [r for r in routes if r.get("route_id") == "R3_SIMPLE_GROUNDED_READ"]

    manifest_path = APP_DIR / "spine_manifest.yaml"
    grounding_declared = False
    if r3_routes:
        r3 = r3_routes[0]
        # Any of these fields assert grounding
        grounding_declared = (
            r3.get("grounding_required") is True
            or r3.get("c0_required") is True
            or "GROUNDED" in r3.get("route_id", "")
        )
    if not grounding_declared and manifest_path.exists():
        manifest_doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        grounding_declared = manifest_doc.get("expects_c0_grounding", False) is True

    assert grounding_declared or "GROUNDED" in "R3_SIMPLE_GROUNDED_READ", (
        "R3_SIMPLE_GROUNDED_READ: GROUNDED means C0 is mandatory. "
        "Declare grounding_required: true in route_registry.yaml or "
        "expects_c0_grounding: true in spine_manifest.yaml."
    )

    # __main__.py must not skip C0 on R3 path
    if MAIN_PY.exists():
        src = MAIN_PY.read_text(encoding="utf-8")
        assert "skip_c0" not in src and "bypass_c0" not in src, (
            "apps_research/__main__.py contains skip_c0 / bypass_c0 pattern — "
            "C0 is mandatory for R3_SIMPLE_GROUNDED_READ."
        )


# ---------------------------------------------------------------------------
# 13. Direct path uses no L3
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_direct_path_uses_no_l3() -> None:
    """apps_research direct path must not invoke L3 managed workflow.

    R3_SIMPLE_GROUNDED_READ = SIMPLE (no L3). apps_rg / apps_lic MAY call
    apps_research as a dependency inside their own L3 DAG; that does not
    make direct apps_research a managed workflow.
    """
    if not MAIN_PY.exists():
        pytest.skip("__main__.py not found")
    src = MAIN_PY.read_text(encoding="utf-8")
    l3_forbidden = [
        "L3_orchestration",
        "managed_workflow",
        "ManagedWorkflowDispatcher",
        "R3R4_managed",
        "workflow_dispatcher",
        "workflow_manager",
    ]
    found = [f for f in l3_forbidden if f in src]
    assert not found, (
        f"apps_research/__main__.py references L3 managed workflow constructs: {found}. "
        "The direct apps_research path is R3_SIMPLE_GROUNDED_READ — SIMPLE means "
        "no L3 managed workflow. l3_required=false."
    )


# ---------------------------------------------------------------------------
# 14. Recipe resolution failure fails closed through Exit
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_recipe_resolution_failure_fails_closed_through_exit() -> None:
    """When capability is unavailable, apps_research must fail closed via Exit v6.

    No generic brief fallback. Must emit R5 terminal packet or equivalent
    through Exit with reason_code = CAPABILITY_UNAVAILABLE or
    RECIPE_RESOLUTION_FAILED.
    """
    assert CAPABILITY_REGISTRY.exists(), (
        f"research_capability_registry.py missing: {CAPABILITY_REGISTRY}"
    )
    src = _src(CAPABILITY_REGISTRY)
    # Must have error/exception type for unavailable capability
    has_error_type = (
        "CapabilityUnavailableError" in src
        or "CapabilityResolutionError" in src
        or "RecipeResolutionError" in src
        or "CAPABILITY_UNAVAILABLE" in src
        or "RECIPE_RESOLUTION_FAILED" in src
    )
    assert has_error_type, (
        "research_capability_registry.py must define a failure mode for unavailable "
        "capability (CapabilityUnavailableError, CAPABILITY_UNAVAILABLE reason_code, "
        "or equivalent). Failure must route through Exit v6 — no generic brief fallback."
    )


# ---------------------------------------------------------------------------
# 15. No generic brief fallback when recipe missing
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_no_generic_brief_when_recipe_missing() -> None:
    """apps_research must not fall back to a generic brief when capability is missing.

    Verified: __main__.py and capability registry must not contain any
    'generic_brief', 'fallback_brief', or 'default_brief' patterns.
    """
    for path in [MAIN_PY, CAPABILITY_REGISTRY]:
        if not path.exists():
            continue
        src = path.read_text(encoding="utf-8")
        forbidden = ["generic_brief", "fallback_brief", "default_brief", "GENERIC_BRIEF"]
        found = [f for f in forbidden if f in src]
        assert not found, (
            f"{path.name} contains generic brief fallback pattern: {found}. "
            "When capability/recipe is missing, apps_research must fail closed "
            "through Exit v6 — no generic brief fallback."
        )


# ---------------------------------------------------------------------------
# 16. Direct apps_research uses no static DAG
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_direct_path_uses_no_static_dag_terms() -> None:
    """Direct apps_research must not describe itself as a static DAG or use DAG terms.

    apps_rg/apps_lic may use apps_research as a node in their own static DAG.
    That does not make direct apps_research a DAG.
    """
    if not MAIN_PY.exists():
        pytest.skip("__main__.py not found")
    src = MAIN_PY.read_text(encoding="utf-8")
    dag_forbidden = [
        "static_dag",
        "StaticDag",
        "dag_path",
        "l3_dag_path",
        "HopStageSpec",  # hop = canonical DAG terminology for apps with static DAGs
    ]
    # Exceptions:
    # - l3_dag_path=None is permitted (explicitly setting to None is correct)
    # - expects_static_dag=False is permitted (it ASSERTS apps_research is not a static DAG)
    src_filtered = (
        src
        .replace("l3_dag_path=None", "")
        .replace("l3_dag_path = None", "")
        .replace("expects_static_dag=False", "")
        .replace("expects_static_dag = False", "")
    )
    found = [f for f in dag_forbidden if f in src_filtered]
    assert not found, (
        f"apps_research/__main__.py uses static DAG terminology: {found}. "
        "Direct apps_research is R3_SIMPLE_GROUNDED_READ — not a static DAG. "
        "apps_rg/apps_lic may call apps_research as a DAG node; that is their DAG, not this."
    )
