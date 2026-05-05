"""P0.1 Governance tests — apps_underwriting_ai recipe/capability resolution.

Enforces that:
- The capability registry exports required symbols
- The capability is registered with R3R4_MANAGED_WORKFLOW (not R3_SIMPLE_GROUNDED_READ)
- l3_required=true, c0_required=true in the registered capability
- Resolution failure returns None (fail-closed; no generic packet emitted)
- spine_manifest.yaml will eventually declare R3R4_MANAGED_WORKFLOW (W3.3 xfail)

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P0.1 / P0.4.

Tests 12–17 in the P0 test suite. Tests 12–15 pass immediately (capability
registry created in P0.2). Test 16 (spine_manifest route correction) is
xfail(strict=True) until W3.3 updates spine_manifest.yaml.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
SPINE_MANIFEST = APP_DIR / "spine_manifest.yaml"
CAPABILITY_REGISTRY = APP_DIR / "integrations" / "underwriting_capability_registry.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# 12. Capability registry file exists and exports required symbols
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_capability_registry_exports_required_symbols() -> None:
    """underwriting_capability_registry.py must export the required symbols."""
    assert CAPABILITY_REGISTRY.exists(), (
        f"underwriting_capability_registry.py missing: {CAPABILITY_REGISTRY}"
    )
    src = CAPABILITY_REGISTRY.read_text(encoding="utf-8")
    required = [
        "register_decision_packet_capability",
        "resolve_decision_packet_capability",
        "apps_underwriting_ai.decision_packet_v1",
    ]
    missing = [r for r in required if r not in src]
    assert not missing, (
        f"underwriting_capability_registry.py is missing required symbols: {missing}. "
        "agentic_core capability delegation contract requires these exports."
    )


# ---------------------------------------------------------------------------
# 13. Capability registry declares R3R4_MANAGED_WORKFLOW (not R3_SIMPLE_GROUNDED_READ)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_capability_registry_declares_r3r4_managed_workflow() -> None:
    """The capability registry must declare R3R4_MANAGED_WORKFLOW route family."""
    assert CAPABILITY_REGISTRY.exists(), (
        f"underwriting_capability_registry.py missing: {CAPABILITY_REGISTRY}"
    )
    src = CAPABILITY_REGISTRY.read_text(encoding="utf-8")
    assert "R3R4_MANAGED_WORKFLOW" in src, (
        "underwriting_capability_registry.py must declare route_family='R3R4_MANAGED_WORKFLOW'. "
        "apps_underwriting_ai is a 5-stage dependent workflow — R3_SIMPLE_GROUNDED_READ is wrong."
    )
    assert "R3_SIMPLE_GROUNDED_READ" not in src, (
        "underwriting_capability_registry.py must NOT declare R3_SIMPLE_GROUNDED_READ. "
        "The correct route family is R3R4_MANAGED_WORKFLOW."
    )


# ---------------------------------------------------------------------------
# 14. Capability registry declares l3_required=True and c0_required=True
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_capability_registry_requires_l3_and_c0() -> None:
    """The registered capability must set l3_required=True and c0_required=True."""
    assert CAPABILITY_REGISTRY.exists(), (
        f"underwriting_capability_registry.py missing: {CAPABILITY_REGISTRY}"
    )
    mod_name = "apps_underwriting_ai.integrations.underwriting_capability_registry"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    registry = importlib.import_module(mod_name)
    registry.register_decision_packet_capability()
    cap = registry.resolve_decision_packet_capability()
    assert cap is not None, (
        "resolve_decision_packet_capability() returned None after registration. "
        "The capability must be resolvable after register_decision_packet_capability() is called."
    )
    assert cap.get("l3_required") is True, (
        f"Registered capability has l3_required={cap.get('l3_required')!r}; expected True. "
        "apps_underwriting_ai requires a 5-stage L3 workflow."
    )
    assert cap.get("c0_required") is True, (
        f"Registered capability has c0_required={cap.get('c0_required')!r}; expected True. "
        "apps_underwriting_ai requires C0 SUBMITTED_DOCUMENT_EVIDENCE_ONLY mode."
    )


# ---------------------------------------------------------------------------
# 15. Unregistered capability resolution returns None (fail-closed)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_unregistered_capability_returns_none() -> None:
    """resolve_decision_packet_capability() returns None for unknown IDs."""
    mod_name = "apps_underwriting_ai.integrations.underwriting_capability_registry"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    registry = importlib.import_module(mod_name)
    result = registry.resolve_decision_packet_capability("nonexistent_capability_id")
    assert result is None, (
        f"resolve_decision_packet_capability('nonexistent') returned {result!r}; "
        "expected None. Callers must treat None as R5 fail-closed terminal."
    )


# ---------------------------------------------------------------------------
# 16. spine_manifest.yaml must eventually declare R3R4_MANAGED_WORKFLOW
# ---------------------------------------------------------------------------

@pytest.mark.governance
@pytest.mark.xfail(strict=True, reason="W3.3: spine_manifest.yaml route correction pending")
def test_apps_underwriting_ai_spine_manifest_declares_r3r4_managed_workflow() -> None:
    """spine_manifest.yaml must declare R3R4_MANAGED_WORKFLOW (not R3_grounded_read).

    Currently declares type: R3_grounded_read — a material routing contradiction
    for a 5-stage dependent workflow. W3.3 corrects this.
    """
    assert SPINE_MANIFEST.exists(), f"spine_manifest.yaml missing: {SPINE_MANIFEST}"
    doc = yaml.safe_load(SPINE_MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    assert routes, "spine_manifest.yaml has no claimed_routes"
    route_types = [r.get("type", "") for r in routes]
    assert any("R3R4_MANAGED_WORKFLOW" in t or "managed_workflow" in t.lower() for t in route_types), (
        f"spine_manifest.yaml declared route types: {route_types}. "
        "Expected R3R4_MANAGED_WORKFLOW for the full decision path. "
        "W3.3 must correct this routing contradiction."
    )
