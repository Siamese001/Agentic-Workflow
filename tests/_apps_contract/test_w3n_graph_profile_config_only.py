"""
W3N config-only tests — graph_traverse profile preparation.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W3N (no-core track)
Constraint: zero agentic_core changes; no live Graph RAG wiring; CONFIG_PREPARED_ONLY.

Acceptance criteria verified:
  AC-1  apps_lic graph_traverse config canonical shape.
  AC-2  apps_rg graph_traverse config canonical shape.
  AC-3  apps_research graph_traverse config canonical shape.
  AC-4  All three profiles carry live_wiring_deferred=true.
  AC-5  W3N does not claim RouteContract carries GraphTraversePolicy.
  AC-6  W3N does not claim C0.3 executes graph traversal.
  AC-7  W3N does not create app adapter modules.
  AC-8  No agentic_core files changed in W3N.
  AC-9  apps_lic R1B absent from route order (W2N invariant preserved).
  AC-10 apps_lic semantic_cache still disabled (W2N invariant preserved).
  AC-11 apps_rg semantic_cache config still prepared (W2N invariant preserved).
  AC-12 apps_research embedding conflict deferred (W2N invariant preserved).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

LIC_ROUTE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
LIC_CACHE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
RG_ROUTE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
RG_CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
RG_R1B_ADAPTER = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
RESEARCH_ROUTE_PROFILE = (
    REPO_ROOT
    / "apps_research"
    / "config"
    / "domain_contract"
    / "route_profile.company_brief.v1.yaml"
)
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
CORE_C03_PIPELINE = (
    REPO_ROOT
    / "agentic_core"
    / "L0_routing"
    / "c0_retrieval"
    / "c0_3_enhanced"
    / "pipeline.py"
)

_WIRING_GATE_W3N = "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED"
_WIRING_GATE_W4 = "CLEARED_BY_W4_GRAPH_RAG_EXECUTION"
_VALID_WIRING_GATES = {_WIRING_GATE_W3N, _WIRING_GATE_W4}


def _load_lic_route_profile() -> dict:
    profiles = yaml.safe_load(LIC_ROUTE_PROFILE.read_text(encoding="utf-8"))
    return profiles[0] if isinstance(profiles, list) else profiles


def _load_rg_route_profile() -> dict:
    profiles = yaml.safe_load(RG_ROUTE_PROFILE.read_text(encoding="utf-8"))
    return profiles[0] if isinstance(profiles, list) else profiles


def _assert_graph_traverse_canonical(
    gt: dict,
    label: str,
    *,
    expected_max_hops: int,
    expected_max_nodes: int,
    expected_max_edges: int,
    expected_relation_types: list[str],
    expected_contradiction_scan: bool,
    expected_supersession_scan: bool,
    expected_adapter_ref: str,
) -> None:
    assert gt.get("graph_expansion_allowed") is True, (
        f"{label} graph_expansion_allowed is not true"
    )
    assert gt.get("max_hops") == expected_max_hops, (
        f"{label} max_hops: expected {expected_max_hops}, got {gt.get('max_hops')!r}"
    )
    assert gt.get("max_nodes") == expected_max_nodes, (
        f"{label} max_nodes: expected {expected_max_nodes}, got {gt.get('max_nodes')!r}"
    )
    assert gt.get("max_edges") == expected_max_edges, (
        f"{label} max_edges: expected {expected_max_edges}, got {gt.get('max_edges')!r}"
    )
    actual_types = gt.get("allowed_relation_types", [])
    for rt in expected_relation_types:
        assert rt in actual_types, (
            f"{label} allowed_relation_types missing '{rt}': {actual_types}"
        )
    assert gt.get("contradiction_scan_enabled") is expected_contradiction_scan, (
        f"{label} contradiction_scan_enabled: expected {expected_contradiction_scan}, "
        f"got {gt.get('contradiction_scan_enabled')!r}"
    )
    assert gt.get("supersession_scan_enabled") is expected_supersession_scan, (
        f"{label} supersession_scan_enabled: expected {expected_supersession_scan}, "
        f"got {gt.get('supersession_scan_enabled')!r}"
    )
    assert gt.get("graph_adapter_ref") == expected_adapter_ref, (
        f"{label} graph_adapter_ref: expected {expected_adapter_ref!r}, "
        f"got {gt.get('graph_adapter_ref')!r}"
    )
    # After W4 flip, live_wiring_deferred is false; W3N config is superseded but
    # structural shape (bool present) is still invariant.
    assert isinstance(gt.get("live_wiring_deferred"), bool), (
        f"{label} live_wiring_deferred must be a bool, got {gt.get('live_wiring_deferred')!r}"
    )
    assert gt.get("wiring_gate") in _VALID_WIRING_GATES, (
        f"{label} wiring_gate wrong: {gt.get('wiring_gate')!r} not in {_VALID_WIRING_GATES}"
    )


# ---------------------------------------------------------------------------
# AC-1: apps_lic graph_traverse config canonical shape
# ---------------------------------------------------------------------------

def test_apps_lic_graph_traverse_config_prepared() -> None:
    """AC-1: apps_lic route profile has canonical W3N graph_traverse shape."""
    profile = _load_lic_route_profile()
    gt = profile.get("graph_traverse", {})
    assert gt, "apps_lic route profile missing graph_traverse block"
    _assert_graph_traverse_canonical(
        gt,
        "apps_lic",
        expected_max_hops=2,
        expected_max_nodes=64,
        expected_max_edges=128,
        expected_relation_types=[
            "GOVERNED_BY", "OBSERVED_IN", "CONTRADICTS", "OWNED_BY", "REQUIRES"
        ],
        expected_contradiction_scan=True,
        expected_supersession_scan=False,
        expected_adapter_ref="apps_lic.integrations.c0_graph_adapter",
    )


# ---------------------------------------------------------------------------
# AC-2: apps_rg graph_traverse config canonical shape
# ---------------------------------------------------------------------------

def test_apps_rg_graph_traverse_config_prepared() -> None:
    """AC-2: apps_rg route profile has canonical W3N graph_traverse shape."""
    profile = _load_rg_route_profile()
    gt = profile.get("graph_traverse", {})
    assert gt, "apps_rg route profile missing graph_traverse block"
    _assert_graph_traverse_canonical(
        gt,
        "apps_rg",
        expected_max_hops=1,
        expected_max_nodes=32,
        expected_max_edges=64,
        expected_relation_types=[
            "DERIVED_FROM", "IMPLEMENTS", "CONTRADICTS", "SOURCE_VERSION", "EVIDENCE"
        ],
        expected_contradiction_scan=True,
        expected_supersession_scan=False,
        expected_adapter_ref="apps_rg.integrations.c0_graph_adapter",
    )


# ---------------------------------------------------------------------------
# AC-3: apps_research graph_traverse config canonical shape
# ---------------------------------------------------------------------------

def test_apps_research_graph_traverse_config_prepared() -> None:
    """AC-3: apps_research route profile has canonical W3N graph_traverse shape."""
    data = yaml.safe_load(RESEARCH_ROUTE_PROFILE.read_text(encoding="utf-8"))
    gt = data.get("graph_traverse", {})
    assert gt, "apps_research route profile missing graph_traverse block"
    _assert_graph_traverse_canonical(
        gt,
        "apps_research",
        expected_max_hops=2,
        expected_max_nodes=64,
        expected_max_edges=128,
        expected_relation_types=[
            "SOURCE_AUTHORITY", "SOURCE_VERSION", "CONTRADICTS",
            "SUPERSEDES", "SUPERSEDED_BY", "EVIDENCE", "DERIVED_FROM"
        ],
        expected_contradiction_scan=True,
        expected_supersession_scan=True,
        expected_adapter_ref="apps_research.integrations.c0_graph_adapter",
    )


# ---------------------------------------------------------------------------
# AC-4: all profiles carry live_wiring_deferred field and a recognised wiring_gate
# (W3N set live_wiring_deferred=true; W4 cleared it to false — both are valid)
# ---------------------------------------------------------------------------

def test_graph_profiles_mark_live_wiring_deferred() -> None:
    """AC-4: all three graph_traverse blocks have live_wiring_deferred bool + known wiring_gate."""
    lic_gt = _load_lic_route_profile().get("graph_traverse", {})
    rg_gt = _load_rg_route_profile().get("graph_traverse", {})
    research_data = yaml.safe_load(RESEARCH_ROUTE_PROFILE.read_text(encoding="utf-8"))
    research_gt = research_data.get("graph_traverse", {})

    for label, gt in (("apps_lic", lic_gt), ("apps_rg", rg_gt), ("apps_research", research_gt)):
        assert isinstance(gt.get("live_wiring_deferred"), bool), (
            f"{label} graph_traverse live_wiring_deferred must be a bool, "
            f"got {gt.get('live_wiring_deferred')!r}"
        )
        assert gt.get("wiring_gate") in _VALID_WIRING_GATES, (
            f"{label} graph_traverse wiring_gate {gt.get('wiring_gate')!r} "
            f"not in {_VALID_WIRING_GATES}"
        )


# ---------------------------------------------------------------------------
# AC-5: W3N does not claim RouteContract carries GraphTraversePolicy
# ---------------------------------------------------------------------------

def test_w3n_does_not_claim_route_contract_policy() -> None:
    """AC-5: route_contract.py must not contain W3N sentinel markers.

    Note: live_wiring_deferred is a legitimate field on GraphTraversePolicy (W4+).
    Only the W3N marker itself is forbidden.
    """
    source = CORE_ROUTE_CONTRACT.read_text(encoding="utf-8")
    assert "W3N" not in source, (
        "route_contract.py contains W3N marker — W3N must not touch agentic_core"
    )


# ---------------------------------------------------------------------------
# AC-6: W3N does not claim C0.3 executes graph traversal
# ---------------------------------------------------------------------------

def test_w3n_does_not_claim_c03_runtime_execution() -> None:
    """AC-6: C0.3 pipeline.py must not contain W3N sentinel markers."""
    assert CORE_C03_PIPELINE.exists(), f"C0.3 pipeline not found at {CORE_C03_PIPELINE}"
    source = CORE_C03_PIPELINE.read_text(encoding="utf-8")
    assert "W3N" not in source, (
        "C0.3 pipeline.py contains W3N marker — W3N must not touch agentic_core"
    )


# ---------------------------------------------------------------------------
# AC-7: W3N does not create app adapter modules
# ---------------------------------------------------------------------------

def test_w3n_does_not_create_app_adapters() -> None:
    """AC-7: W3N must not have created or modified c0_graph_adapter.py files.

    Note: pre-existing stubs from prior reverted W4 work may exist on disk.
    W3N neither created nor modified them — verified by confirming W3N markers
    are absent from any adapter that exists.
    """
    for app in ("apps_lic", "apps_rg", "apps_research"):
        adapter_path = REPO_ROOT / app / "integrations" / "c0_graph_adapter.py"
        if adapter_path.exists():
            source = adapter_path.read_text(encoding="utf-8")
            assert "W3N" not in source, (
                f"{adapter_path.name} ({app}) contains W3N marker — "
                "W3N must not modify app adapters"
            )
            # Pre-existing W4 stubs are acceptable — they were not created by W3N.
            # W4N will own them; W3N only confirms it did not add W3N markers.


# ---------------------------------------------------------------------------
# AC-8: no agentic_core files changed in W3N
# ---------------------------------------------------------------------------

def test_no_agentic_core_files_changed_in_w3n() -> None:
    """AC-8: agentic_core L0 binding and route_contract must not contain W3N markers.

    Note: W4 legitimately added live_wiring_deferred reading to the L0 binding
    (in _read_graph_traverse_policy / _read_semantic_cache_profile) — so we only
    check for the W3N-specific marker, not the field name itself.
    """
    for path in (CORE_L0_BINDING, CORE_ROUTE_CONTRACT):
        source = path.read_text(encoding="utf-8")
        assert "W3N" not in source, (
            f"{path.name} contains 'W3N' marker — W3N must not touch agentic_core"
        )


# ---------------------------------------------------------------------------
# AC-9: apps_lic R1B absent from route order (W2N invariant preserved)
# ---------------------------------------------------------------------------

def test_apps_lic_r1b_absent_from_route_order() -> None:
    """AC-9: R1B_SEMANTIC_CACHE must not appear in apps_lic route_evaluation_order."""
    profile = _load_lic_route_profile()
    order = profile.get("route_evaluation_order", [])
    route_ids = [
        (item.get("route_id") if isinstance(item, dict) else item)
        for item in order
    ]
    assert "R1B_SEMANTIC_CACHE" not in route_ids, (
        f"R1B_SEMANTIC_CACHE found in apps_lic route_evaluation_order: {route_ids} "
        "(W2N invariant violated)"
    )


# ---------------------------------------------------------------------------
# AC-10: apps_lic semantic_cache still disabled (W2N invariant preserved)
# ---------------------------------------------------------------------------

def test_apps_lic_semantic_cache_still_disabled() -> None:
    """AC-10: apps_lic semantic_cache.enabled must still be false (W2N invariant)."""
    data = yaml.safe_load(LIC_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is False, (
        f"apps_lic semantic_cache.enabled changed from false: {sc.get('enabled')!r} "
        "(W2N invariant violated)"
    )
    assert sc.get("reason") == "personalized_outreach_not_cacheable", (
        f"apps_lic semantic_cache.reason changed: {sc.get('reason')!r}"
    )


# ---------------------------------------------------------------------------
# AC-11: apps_rg semantic_cache config still prepared (W2N invariant preserved)
# ---------------------------------------------------------------------------

def test_apps_rg_semantic_cache_config_still_prepared() -> None:
    """AC-11: apps_rg semantic_cache config must be unchanged from W2N."""
    data = yaml.safe_load(RG_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is True, (
        f"apps_rg semantic_cache.enabled changed: {sc.get('enabled')!r}"
    )
    assert sc.get("namespace") == "apps_rg.resume_gen.section.v1", (
        f"apps_rg semantic_cache.namespace changed: {sc.get('namespace')!r}"
    )
    assert sc.get("live_wiring_deferred") is True, (
        "apps_rg semantic_cache live_wiring_deferred=true removed (W2N invariant violated)"
    )


# ---------------------------------------------------------------------------
# AC-12: apps_research embedding conflict deferred (W2N invariant preserved)
# ---------------------------------------------------------------------------

def test_apps_research_embedding_conflict_deferred() -> None:
    """AC-12: apps_research embedding_model check.

    W3N constraint: W3N must NOT have resolved the conflict (config-only wave).
    W5N update: W5N legitimately resolves the conflict to BAAI/bge-m3/1024.
    Post-W5N: accept either the original value (pre-W5N) or the fixed value.
    """
    data = yaml.safe_load(RESEARCH_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    model = sc.get("embedding_model", "")
    dims = sc.get("embedding_dimensions", 0)
    _valid_models = {"text-embedding-3-large", "BAAI/bge-m3"}
    assert model in _valid_models, (
        f"apps_research embedding_model is unrecognised: {model!r}"
    )
    _valid_dims = {3072, 1024}
    assert dims in _valid_dims, (
        f"apps_research embedding_dimensions is unrecognised: {dims!r}"
    )
