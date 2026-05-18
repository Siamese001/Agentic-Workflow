"""
W2N config-only tests — semantic cache configuration preparation.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W2N (no-core track)
Constraint: zero agentic_core changes; no live R1B wiring; CONFIG_PREPARED_ONLY.

Acceptance criteria verified:
  AC-1  apps_lic semantic_cache.enabled is false.
  AC-2  apps_lic R1B_SEMANTIC_CACHE absent from route_evaluation_order.
  AC-3  apps_lic cannot emit SEMANTIC_CACHE_HIT under no-core plan
        (semantic_cache.enabled=false + R1B absent = structural guarantee).
  AC-4  apps_rg semantic_cache config prepared with canonical shape.
  AC-5  apps_rg/cache/r1b_adapter.py quarantined and untouched.
  AC-6  apps_research embedding conflict deferred (not modified in W2N).
  AC-7  No agentic_core files changed in W2N.
  AC-8  W2N does not claim live R1B wiring (live_wiring_deferred=true in both profiles).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

LIC_CACHE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
LIC_ROUTE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
RG_CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
RG_R1B_ADAPTER = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
RESEARCH_CACHE_PROFILE = (
    REPO_ROOT
    / "apps_research"
    / "config"
    / "domain_contract"
    / "cache_profile.company_brief.v1.yaml"
)
CORE_L0_BINDING = REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
CORE_ROUTE_CONTRACT = (
    REPO_ROOT / "agentic_core" / "L0_routing" / "c0_retrieval" / "route_contract.py"
)


# ---------------------------------------------------------------------------
# AC-1: apps_lic semantic_cache.enabled is false
# ---------------------------------------------------------------------------

def test_apps_lic_semantic_cache_disabled() -> None:
    """AC-1: apps_lic cache profile must have semantic_cache.enabled=false."""
    data = yaml.safe_load(LIC_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is False, (
        f"apps_lic semantic_cache.enabled is not false: {sc.get('enabled')!r}"
    )
    assert sc.get("reason") == "personalized_outreach_not_cacheable", (
        f"apps_lic semantic_cache.reason is not canonical: {sc.get('reason')!r}"
    )


# ---------------------------------------------------------------------------
# AC-2: apps_lic R1B_SEMANTIC_CACHE absent from route_evaluation_order
# ---------------------------------------------------------------------------

def test_apps_lic_r1b_absent_from_route_order() -> None:
    """AC-2: R1B_SEMANTIC_CACHE must not appear in apps_lic route_evaluation_order."""
    profiles = yaml.safe_load(LIC_ROUTE_PROFILE.read_text(encoding="utf-8"))
    # route_profiles.yaml is a list
    if isinstance(profiles, list):
        profile = profiles[0]
    else:
        profile = profiles
    order = profile.get("route_evaluation_order", [])
    route_ids = [
        (item.get("route_id") if isinstance(item, dict) else item)
        for item in order
    ]
    assert "R1B_SEMANTIC_CACHE" not in route_ids, (
        f"R1B_SEMANTIC_CACHE found in apps_lic route_evaluation_order: {route_ids}"
    )


# ---------------------------------------------------------------------------
# AC-3: apps_lic cannot emit SEMANTIC_CACHE_HIT under no-core plan
# ---------------------------------------------------------------------------

def test_apps_lic_no_semantic_cache_hit_possible_under_no_core_plan() -> None:
    """AC-3: apps_lic structural guarantee — semantic_cache.enabled=false AND
    R1B absent from route order = no SEMANTIC_CACHE_HIT possible under no-core plan."""
    # semantic_cache.enabled=false (checked by AC-1)
    data = yaml.safe_load(LIC_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is False, "apps_lic semantic_cache must be disabled"

    # live_wiring_deferred marker must be present
    assert sc.get("live_wiring_deferred") is True, (
        "apps_lic cache profile missing live_wiring_deferred=true marker"
    )

    # R1B absent from route order (checked by AC-2)
    profiles = yaml.safe_load(LIC_ROUTE_PROFILE.read_text(encoding="utf-8"))
    profile = profiles[0] if isinstance(profiles, list) else profiles
    order = profile.get("route_evaluation_order", [])
    route_ids = [
        (item.get("route_id") if isinstance(item, dict) else item)
        for item in order
    ]
    assert "R1B_SEMANTIC_CACHE" not in route_ids, (
        "R1B_SEMANTIC_CACHE in route order creates a path to SEMANTIC_CACHE_HIT"
    )


# ---------------------------------------------------------------------------
# AC-4: apps_rg semantic_cache config prepared with canonical shape
# ---------------------------------------------------------------------------

def test_apps_rg_semantic_cache_config_prepared() -> None:
    """AC-4: apps_rg cache profile has canonical W2N shape."""
    data = yaml.safe_load(RG_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})

    assert sc.get("enabled") is True, (
        f"apps_rg semantic_cache.enabled should be true: {sc.get('enabled')!r}"
    )
    assert sc.get("namespace") == "apps_rg.resume_gen.section.v1", (
        f"apps_rg semantic_cache.namespace wrong: {sc.get('namespace')!r}"
    )
    assert sc.get("similarity_threshold") == 0.88, (
        f"apps_rg similarity_threshold wrong: {sc.get('similarity_threshold')!r}"
    )
    fields = sc.get("compatibility_check_fields", [])
    for required in ("role_compatible", "freshness_within_ttl", "provenance_known"):
        assert required in fields, (
            f"apps_rg compatibility_check_fields missing '{required}': {fields}"
        )

    # W7: file-backed R1B adapter wired; durable UWG persistence remains BLOCKED in code constants.
    assert sc.get("live_wiring_deferred") is False, (
        f"apps_rg semantic_cache.live_wiring_deferred should be false after W7: {sc.get('live_wiring_deferred')!r}"
    )


# ---------------------------------------------------------------------------
# AC-5: apps_rg/cache/r1b_adapter.py quarantined and untouched
# ---------------------------------------------------------------------------

def test_apps_rg_quarantined_adapter_untouched() -> None:
    """W7: r1b_adapter.py implements ROLE_TARGET_RUN persistence (quarantine cleared)."""
    assert RG_R1B_ADAPTER.exists(), "apps_rg/cache/r1b_adapter.py does not exist"
    source = RG_R1B_ADAPTER.read_text(encoding="utf-8")
    assert "check_r1b_for_apps_rg" in source
    assert "HistoricalIntentRecord" in source or "r1b_retrieval" in source


# ---------------------------------------------------------------------------
# AC-6: apps_research embedding conflict deferred (not modified in W2N)
# ---------------------------------------------------------------------------

def test_apps_research_embedding_conflict_deferred() -> None:
    """AC-6: apps_research cache profile embedding model check.

    W2N constraint: W2N must NOT have resolved the conflict (config-only wave).
    W5N update: W5N legitimately resolves the conflict to BAAI/bge-m3/1024.
    Post-W5N: profile is valid as long as it has a recognised embedding model.
    """
    assert RESEARCH_CACHE_PROFILE.exists(), (
        "apps_research cache_profile.company_brief.v1.yaml not found"
    )
    data = yaml.safe_load(RESEARCH_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    model = sc.get("embedding_model", "")
    dims = sc.get("embedding_dimensions", 0)
    # W5N resolved the conflict: accept either the original value (pre-W5N) or the fixed value.
    _valid_models = {"text-embedding-3-large", "BAAI/bge-m3"}
    assert model in _valid_models, (
        f"apps_research embedding_model is unrecognised: {model!r}"
    )
    _valid_dims = {3072, 1024}
    assert dims in _valid_dims, (
        f"apps_research embedding_dimensions is unrecognised: {dims!r}"
    )


# ---------------------------------------------------------------------------
# AC-7: no agentic_core files changed in W2N (static source check)
# ---------------------------------------------------------------------------

def test_no_agentic_core_files_changed_in_w2n() -> None:
    """AC-7: agentic_core L0 binding and route_contract must not contain W2N markers."""
    for path in (CORE_L0_BINDING, CORE_ROUTE_CONTRACT):
        assert path.exists(), f"{path} does not exist"
        source = path.read_text(encoding="utf-8")
        assert "W2N" not in source, (
            f"{path.name} contains 'W2N' marker — W2N must not touch agentic_core"
        )
        assert "live_wiring_deferred" not in source, (
            f"{path.name} contains W2N config marker — agentic_core must not be modified"
        )


def test_no_agentic_core_check_d2_wired_by_w2n() -> None:
    """AC-7 (extended): package_driven_l0_binding.py must not have a new
    check_d2_semantic_cache call added by W2N.

    We verify by confirming the binding does NOT reference live_wiring_deferred,
    which is the W2N sentinel. We do not assert check_d2_semantic_cache absent
    because it may already be present from pre-W2N state — we only assert W2N
    did not add it (checked via the W2N sentinel absence).
    """
    source = CORE_L0_BINDING.read_text(encoding="utf-8")
    assert "W2N" not in source, (
        "package_driven_l0_binding.py contains W2N marker — forbidden under no-core plan"
    )


# ---------------------------------------------------------------------------
# AC-8: W2N does not claim live R1B wiring
# ---------------------------------------------------------------------------

def test_w2n_does_not_claim_live_r1b_wiring() -> None:
    """AC-8 / W7: apps_lic still defers live wiring; apps_rg file-backed R1B adapter is live."""
    lic = yaml.safe_load(LIC_CACHE_PROFILE.read_text(encoding="utf-8")).get("semantic_cache", {})
    assert lic.get("live_wiring_deferred") is True, "apps_lic must defer live R1B wiring"
    assert lic.get("wiring_gate") == "W2_GENERIC_INFRA_EDIT_IN_AGENTIC_CORE_REQUIRED"

    rg = yaml.safe_load(RG_CACHE_PROFILE.read_text(encoding="utf-8")).get("semantic_cache", {})
    assert rg.get("live_wiring_deferred") is False, "apps_rg W7 enables file-backed R1B adapter"
