"""DS-1 Governance sentinels for apps_research canonical spine wireup.

Static-analysis tests verifying that apps_research is wired correctly onto the
canonical R3_grounded_read spine:

1. spine_manifest.yaml declares R3_grounded_read.
2. __main__.py routes through U0-bound AppRuntimeProfile / AppIngressRunner (governed_run envelope optional).
3. No L0 subprocess to sibling apps.
4. spine_handoff.py exists and delegates to GovernedResearchRun.
5. governed_research_run.py inherits from GovernedAppRunner.
6. FEC producer is registered (apps_research.cert module wired in __main__.py).
7. Exit hook adoption: _maybe_run_exit_hook invoked in the live-cert path.

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-1.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"
MANIFEST = APP_DIR / "spine_manifest.yaml"
SPINE_HANDOFF = APP_DIR / "integrations" / "spine_handoff.py"
GOVERNED_RUN = APP_DIR / "integrations" / "governed_research_run.py"
CERT_DIR = APP_DIR / "cert"
CERT_ROUTE_REGISTRY = APP_DIR / "config" / "cert_route_registry.yaml"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.governance
def test_apps_research_manifest_claims_r3_grounded_read() -> None:
    """apps_research produces grounded research briefs — must claim R3_grounded_read."""
    assert MANIFEST.exists(), f"spine_manifest.yaml missing: {MANIFEST}"
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    routes = doc.get("claimed_routes", [])
    assert routes, "spine_manifest.yaml has no claimed_routes"
    types = [r.get("type") for r in routes]
    assert "R3_grounded_read" in types, (
        f"apps_research/spine_manifest.yaml must claim R3_grounded_read. Found: {types}"
    )


@pytest.mark.governance
def test_apps_research_main_routes_through_profile_spine() -> None:
    """__main__.py must route default product CLI through the R3 spine handoff."""
    assert MAIN_PY.exists(), f"__main__.py missing: {MAIN_PY}"
    src = _src(MAIN_PY)
    profile_markers = [
        "_run_profile_spine",
        "run_research_via_spine",
    ]
    missing = [m for m in profile_markers if m not in src]
    assert not missing, (
        "apps_research/__main__.py must route through the canonical profile spine. "
        f"Missing: {missing}"
    )


@pytest.mark.governance
def test_apps_research_no_subprocess_to_sibling_apps() -> None:
    """L0 must be DECISION-ONLY. No subprocess calling sibling apps."""
    src = _src(MAIN_PY)
    bad = re.findall(
        r'subprocess\.\w+\s*\(\s*\[.*?apps_(exec|lic|rfp|rg|qna).*?\]',
        src,
        re.DOTALL,
    )
    assert not bad, (
        f"apps_research/__main__.py subprocess to sibling app detected: {bad}"
    )


@pytest.mark.governance
def test_apps_research_spine_handoff_delegates_to_governed_run() -> None:
    """spine_handoff.py must exist and delegate to GovernedResearchRun."""
    assert SPINE_HANDOFF.exists(), f"spine_handoff.py missing: {SPINE_HANDOFF}"
    src = _src(SPINE_HANDOFF)
    assert "GovernedResearchRun" in src, (
        "apps_research/integrations/spine_handoff.py must delegate to GovernedResearchRun."
    )


@pytest.mark.governance
def test_apps_research_governed_run_inherits_governed_app_runner() -> None:
    """governed_research_run.py must subclass GovernedAppRunner."""
    assert GOVERNED_RUN.exists(), f"governed_research_run.py missing: {GOVERNED_RUN}"
    src = _src(GOVERNED_RUN)
    assert "GovernedAppRunner" in src, (
        "apps_research/integrations/governed_research_run.py must inherit from GovernedAppRunner."
    )


@pytest.mark.governance
def test_apps_research_fec_producer_registered() -> None:
    """apps_research/cert/ must exist with a fec_producer.py that registers produce_fec."""
    fec_producer = CERT_DIR / "fec_producer.py"
    assert fec_producer.exists(), (
        f"apps_research/cert/fec_producer.py missing — FEC producer not wired. "
        f"Plan: apps-research-c0-fec-producer-wiring-e7a2c3."
    )
    src = _src(fec_producer)
    assert "produce_fec" in src, (
        "apps_research/cert/fec_producer.py must define produce_fec()."
    )
    init = CERT_DIR / "__init__.py"
    assert init.exists(), f"apps_research/cert/__init__.py missing."
    init_src = _src(init)
    assert "register_producer" in init_src or "produce_fec" in init_src, (
        "apps_research/cert/__init__.py must register produce_fec via register_producer side-effect."
    )


@pytest.mark.governance
def test_apps_research_exit_hook_wired_in_main() -> None:
    """__main__.py must invoke _maybe_run_exit_hook in the live-cert path."""
    src = _src(MAIN_PY)
    assert "_maybe_run_exit_hook" in src, (
        "apps_research/__main__.py must call _maybe_run_exit_hook in _run_live_cert "
        "to invoke the v6 Exit pipeline. Missing."
    )


@pytest.mark.governance
def test_apps_research_cert_route_registry_opts_in_to_exit_eval() -> None:
    """cert_route_registry.yaml must have invoke_exit_eval: true for apps_research."""
    assert CERT_ROUTE_REGISTRY.exists(), f"cert_route_registry.yaml missing: {CERT_ROUTE_REGISTRY}"
    text = CERT_ROUTE_REGISTRY.read_text(encoding="utf-8")
    assert "invoke_exit_eval" in text, (
        "apps_research/config/cert_route_registry.yaml must declare invoke_exit_eval."
    )
    assert "true" in text.lower() or "True" in text, (
        "apps_research/config/cert_route_registry.yaml must set invoke_exit_eval: true."
    )
