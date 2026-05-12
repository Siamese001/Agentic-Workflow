"""
W3 tests — GraphTraversePolicy carrier + route-profile graph_traverse plumbing.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W3
Coverage:
  1.  test_graph_traverse_policy_defaults_safe
  2.  test_route_contract_accepts_graph_traverse_policy
  3.  test_l0_maps_graph_config_to_route_contract
  4.  test_l0_omits_policy_when_graph_disabled_or_absent
  5.  test_l0_does_not_call_run_graph_traverse
  6.  test_no_app_id_branch_in_graph_policy_mapping
  7.  test_apps_lic_graph_profile_added_without_r1b_reintroduced
  8.  test_apps_rg_graph_profile_added_r1b_preserved
  9.  test_apps_research_graph_profile_added_embedding_conflict_deferred
  10. test_graph_adapter_ref_is_carried_but_not_resolved
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Helpers / fixtures (reuse pattern from W2 tests)
# ---------------------------------------------------------------------------

def _make_authority_receipt() -> Any:
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AuthorityValidationReceipt,
    )
    return AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        forbidden_fields_detected=(),
        timestamp_iso="2026-05-13T00:00:00Z",
    )


def _make_validated_request(
    app_id: str = "apps_rg",
    task_class: str = "resume_generation",
    target_company: str = "TestCo",
    request_id: str = "req-w3-001",
    run_id: str = "run-w3-001",
    tenant_id: str = "tenant-test",
    trace_id: str = "trace-w3-001",
    route_profile_ref: Optional[str] = None,
    cache_profile_ref: Optional[str] = None,
) -> Any:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    rcp = route_profile_ref or "apps_rg/config/domain_contract/route_profiles.yaml"
    ccp = cache_profile_ref or "apps_rg/config/domain_contract/cache_profiles.yaml"

    return ValidatedRequest(
        request_id=request_id,
        run_id=run_id,
        app_id=app_id,
        task_class=task_class,
        payload_digest="test-digest-w3-placeholder",
        authority_validation_receipt=_make_authority_receipt(),
        l5_certification_ref="test-l5-cert-w3-placeholder",
        trace_id=trace_id,
        tenant_id=tenant_id,
        app_payload={
            "target_company": target_company,
            "runtime_customization_package": {
                "profile_refs": {
                    "route_profile": rcp,
                    "cache_profile": ccp,
                }
            },
        },
    )


def _load_yaml(path: Path) -> Any:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# 1. test_graph_traverse_policy_defaults_safe
# ---------------------------------------------------------------------------

def test_graph_traverse_policy_defaults_safe() -> None:
    """GraphTraversePolicy() defaults must be disabled and safe-bounded."""
    from agentic_core.L0_routing.c0_retrieval.route_contract import GraphTraversePolicy

    policy = GraphTraversePolicy()
    assert policy.graph_expansion_allowed is False, "default must be disabled"
    assert policy.max_hops == 1
    assert policy.max_nodes == 64
    assert policy.max_edges == 128
    assert policy.allowed_relation_types == ()
    assert policy.contradiction_scan_enabled is False
    assert policy.supersession_scan_enabled is False
    assert policy.graph_adapter_ref is None
    assert policy.acl_scope_ref is None
    assert policy.freshness_profile_ref is None
    assert policy.support_target is None


# ---------------------------------------------------------------------------
# 2. test_route_contract_accepts_graph_traverse_policy
# ---------------------------------------------------------------------------

def test_route_contract_accepts_graph_traverse_policy() -> None:
    """Runtime RouteContract must accept graph_traverse_policy without breaking
    existing constructor behavior (backward compatible)."""
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from agentic_core.L0_routing.c0_retrieval.route_contract import GraphTraversePolicy

    policy = GraphTraversePolicy(
        graph_expansion_allowed=True,
        max_hops=2,
        allowed_relation_types=("CONTRADICTS", "GOVERNED_BY"),
    )

    # Construct with policy
    rc_with_policy = RouteContract(
        request_id="req-001",
        run_id="run-001",
        app_id="apps_lic",
        trace_id="trace-001",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        l5_certification_ref="test-l5-cert-w3-placeholder",
        graph_traverse_policy=policy,
    )
    assert rc_with_policy.graph_traverse_policy is policy
    assert rc_with_policy.graph_traverse_policy.graph_expansion_allowed is True
    assert rc_with_policy.graph_traverse_policy.max_hops == 2

    # Construct WITHOUT policy — backward compat: defaults to None
    rc_no_policy = RouteContract(
        request_id="req-002",
        run_id="run-002",
        app_id="apps_rg",
        trace_id="trace-002",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        l5_certification_ref="test-l5-cert-w3-placeholder",
    )
    assert rc_no_policy.graph_traverse_policy is None


# ---------------------------------------------------------------------------
# 3. test_l0_maps_graph_config_to_route_contract
# ---------------------------------------------------------------------------

def test_l0_maps_graph_config_to_route_contract() -> None:
    """_build_graph_traverse_policy produces a non-None policy when
    graph_expansion_allowed=true in the route profile config."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_graph_traverse_config,
        _build_graph_traverse_policy,
    )
    from agentic_core.L0_routing.c0_retrieval.route_contract import GraphTraversePolicy

    profile = {
        "graph_traverse": {
            "graph_expansion_allowed": True,
            "max_hops": 2,
            "max_nodes": 64,
            "max_edges": 128,
            "allowed_relation_types": ["GOVERNED_BY", "CONTRADICTS"],
            "contradiction_scan_enabled": True,
            "supersession_scan_enabled": False,
            "graph_adapter_ref": "apps_lic.integrations.c0_graph_adapter",
        }
    }

    gt_config = _read_graph_traverse_config(profile)
    assert gt_config["graph_expansion_allowed"] is True

    policy = _build_graph_traverse_policy(gt_config)
    assert policy is not None
    assert isinstance(policy, GraphTraversePolicy)
    assert policy.graph_expansion_allowed is True
    assert policy.max_hops == 2
    assert policy.max_nodes == 64
    assert policy.max_edges == 128
    assert "GOVERNED_BY" in policy.allowed_relation_types
    assert "CONTRADICTS" in policy.allowed_relation_types
    assert policy.contradiction_scan_enabled is True
    assert policy.supersession_scan_enabled is False
    assert policy.graph_adapter_ref == "apps_lic.integrations.c0_graph_adapter"


# ---------------------------------------------------------------------------
# 4. test_l0_omits_policy_when_graph_disabled_or_absent
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("profile,expected_none", [
    # absent graph_traverse block
    ({}, True),
    # graph_traverse present but disabled
    ({"graph_traverse": {"graph_expansion_allowed": False}}, True),
    # graph_traverse present but missing graph_expansion_allowed (defaults False)
    ({"graph_traverse": {"max_hops": 2}}, True),
    # graph_traverse enabled
    ({"graph_traverse": {"graph_expansion_allowed": True, "max_hops": 1}}, False),
])
def test_l0_omits_policy_when_graph_disabled_or_absent(
    profile: Dict[str, Any], expected_none: bool
) -> None:
    """_build_graph_traverse_policy returns None when disabled/absent."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_graph_traverse_config,
        _build_graph_traverse_policy,
    )

    gt_config = _read_graph_traverse_config(profile)
    policy = _build_graph_traverse_policy(gt_config)
    if expected_none:
        assert policy is None, f"Expected None for profile={profile}, got {policy}"
    else:
        assert policy is not None


# ---------------------------------------------------------------------------
# 5. test_l0_does_not_call_run_graph_traverse
# ---------------------------------------------------------------------------

def test_l0_does_not_call_run_graph_traverse() -> None:
    """run_graph_traverse must never be called by L0 routing (W3 invariant).

    Verified via static AST analysis of the binding source.  The function must
    not contain a Call node whose func resolves to 'run_graph_traverse'.
    """
    binding_path = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    source = binding_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "run_graph_traverse":
                pytest.fail(
                    f"L0 binding calls run_graph_traverse() at line {node.lineno} — forbidden in W3"
                )
            if isinstance(func, ast.Attribute) and func.attr == "run_graph_traverse":
                pytest.fail(
                    f"L0 binding calls *.run_graph_traverse() at line {node.lineno} — forbidden in W3"
                )


# ---------------------------------------------------------------------------
# 6. test_no_app_id_branch_in_graph_policy_mapping
# ---------------------------------------------------------------------------

def test_no_app_id_branch_in_graph_policy_mapping() -> None:
    """Static AST check: package_driven_l0_binding.py must have no app_id == branch
    in the graph policy mapping code (_read_graph_traverse_config /
    _build_graph_traverse_policy)."""
    binding_path = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    source = binding_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(
                    comparator.value, str
                ):
                    left = node.left
                    if isinstance(left, ast.Name) and left.id == "app_id":
                        pytest.fail(
                            f"Found app_id == branch at line {node.lineno}: "
                            "no per-app_id conditionals allowed in generic binding"
                        )
                    # Also check attribute access app_id
                    if isinstance(left, ast.Attribute) and left.attr == "app_id":
                        # Only flag if used in comparison with a string literal
                        if isinstance(comparator.value, str) and comparator.value.startswith("apps_"):
                            pytest.fail(
                                f"Found app_id == 'apps_*' branch at line {node.lineno}"
                            )


# ---------------------------------------------------------------------------
# 7. test_apps_lic_graph_profile_added_without_r1b_reintroduced
# ---------------------------------------------------------------------------

def test_apps_lic_graph_profile_added_without_r1b_reintroduced() -> None:
    """apps_lic route profile must have graph_traverse block AND
    R1B_SEMANTIC_CACHE must remain absent from route_evaluation_order AND
    semantic_cache.enabled must remain false."""
    import yaml

    route_profile_path = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
    )
    cache_profile_path = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
    )

    route_data = yaml.safe_load(route_profile_path.read_text(encoding="utf-8"))
    cache_data = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))

    # route_profiles.yaml is a YAML list — get first entry
    if isinstance(route_data, list):
        route_profile = route_data[0]
    else:
        route_profile = route_data

    # graph_traverse must be present
    assert "graph_traverse" in route_profile, "apps_lic route profile missing graph_traverse block"
    gt = route_profile["graph_traverse"]
    assert gt["graph_expansion_allowed"] is True

    # R1B must be absent from route_evaluation_order
    eval_order = route_profile.get("route_evaluation_order", [])
    route_ids = [entry.get("route_id", "") for entry in eval_order]
    assert "R1B_SEMANTIC_CACHE" not in route_ids, (
        "R1B_SEMANTIC_CACHE must remain absent from apps_lic route_evaluation_order"
    )

    # semantic_cache.enabled must remain false
    sc = cache_data.get("semantic_cache", {})
    assert sc.get("enabled", True) is False, (
        "apps_lic semantic_cache.enabled must remain false"
    )


# ---------------------------------------------------------------------------
# 8. test_apps_rg_graph_profile_added_r1b_preserved
# ---------------------------------------------------------------------------

def test_apps_rg_graph_profile_added_r1b_preserved() -> None:
    """apps_rg route profile must have graph_traverse block AND
    semantic_cache.enabled must remain true AND quarantined adapter untouched."""
    import yaml

    route_profile_path = (
        REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
    )
    cache_profile_path = (
        REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    quarantined_adapter = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"

    route_data = yaml.safe_load(route_profile_path.read_text(encoding="utf-8"))
    cache_data = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))

    # route_profiles.yaml is a YAML list
    if isinstance(route_data, list):
        route_profile = route_data[0]
    else:
        route_profile = route_data

    # graph_traverse must be present
    assert "graph_traverse" in route_profile, "apps_rg route profile missing graph_traverse block"
    gt = route_profile["graph_traverse"]
    assert gt["graph_expansion_allowed"] is True
    assert gt["max_hops"] == 1  # apps_rg bounded to max_hops=1

    # apps_rg semantic_cache.enabled must remain true (W2 invariant)
    sc = cache_data.get("semantic_cache", {})
    assert sc.get("enabled", False) is True, (
        "apps_rg semantic_cache.enabled must remain true (W2 invariant)"
    )

    # Quarantined adapter must still raise RuntimeError on import
    assert quarantined_adapter.exists(), "r1b_adapter.py must still exist"
    adapter_src = quarantined_adapter.read_text(encoding="utf-8")
    assert "RuntimeError" in adapter_src, (
        "quarantined r1b_adapter.py must still raise RuntimeError on import"
    )


# ---------------------------------------------------------------------------
# 9. test_apps_research_graph_profile_added_embedding_conflict_deferred
# ---------------------------------------------------------------------------

def test_apps_research_graph_profile_added_embedding_conflict_deferred() -> None:
    """apps_research route profile must have graph_traverse block AND
    embedding model conflict must not be changed in W3."""
    import yaml

    route_profile_path = (
        REPO_ROOT
        / "apps_research"
        / "config"
        / "domain_contract"
        / "route_profile.company_brief.v1.yaml"
    )
    cache_profile_path = (
        REPO_ROOT
        / "apps_research"
        / "config"
        / "domain_contract"
        / "cache_profile.company_brief.v1.yaml"
    )

    route_data = yaml.safe_load(route_profile_path.read_text(encoding="utf-8"))
    cache_data = yaml.safe_load(cache_profile_path.read_text(encoding="utf-8"))

    # graph_traverse must be present in route profile
    assert "graph_traverse" in route_data, (
        "apps_research route profile missing graph_traverse block"
    )
    gt = route_data["graph_traverse"]
    assert gt["graph_expansion_allowed"] is True
    assert gt["supersession_scan_enabled"] is True  # apps_research enables supersession

    # Embedding model conflict: cache profile still has text-embedding-3-large (not changed in W3)
    embedding_model = cache_data.get("embedding_model", "")
    # The conflict is that text-embedding-3-large (3072-dim) is set; BAAI/bge-m3 migration
    # is deferred to W5.P0. We assert the W3 change did NOT fix this.
    assert "bge-m3" not in embedding_model, (
        "Embedding model must NOT be changed to bge-m3 in W3 — deferred to W5.P0"
    )


# ---------------------------------------------------------------------------
# 10. test_graph_adapter_ref_is_carried_but_not_resolved
# ---------------------------------------------------------------------------

def test_graph_adapter_ref_is_carried_but_not_resolved() -> None:
    """graph_adapter_ref must appear as a string in GraphTraversePolicy and
    W3 must NOT import or resolve any adapter module."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_graph_traverse_config,
        _build_graph_traverse_policy,
    )

    profile_with_adapter = {
        "graph_traverse": {
            "graph_expansion_allowed": True,
            "max_hops": 1,
            "graph_adapter_ref": "apps_lic.integrations.c0_graph_adapter",
        }
    }

    gt_config = _read_graph_traverse_config(profile_with_adapter)
    policy = _build_graph_traverse_policy(gt_config)

    assert policy is not None
    assert policy.graph_adapter_ref == "apps_lic.integrations.c0_graph_adapter"

    # The adapter module must NOT have been imported or created in W3
    import sys
    assert "apps_lic.integrations.c0_graph_adapter" not in sys.modules, (
        "graph adapter module must not be imported in W3"
    )
    assert "apps_rg.integrations.c0_graph_adapter" not in sys.modules
    assert "apps_research.integrations.c0_graph_adapter" not in sys.modules

    # Static check: binding source must not import any c0_graph_adapter
    binding_path = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    binding_src = binding_path.read_text(encoding="utf-8")
    assert "c0_graph_adapter" not in binding_src, (
        "package_driven_l0_binding.py must not import or reference c0_graph_adapter"
    )
    # run_graph_traverse may appear in docstrings/comments as a prohibition note,
    # but must NOT appear as an actual function call — use AST for precision.
    tree = ast.parse(binding_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "run_graph_traverse":
                pytest.fail(
                    f"binding calls run_graph_traverse() at line {node.lineno}"
                )
            if isinstance(func, ast.Attribute) and func.attr == "run_graph_traverse":
                pytest.fail(
                    f"binding calls *.run_graph_traverse() at line {node.lineno}"
                )


# ---------------------------------------------------------------------------
# 11. test_terminal_r1a_route_has_no_graph_policy
# ---------------------------------------------------------------------------

def test_terminal_r1a_route_has_no_graph_policy() -> None:
    """R1A_EXACT_CACHE RouteContract must carry graph_traverse_policy=None.
    Cache-only routes short-circuit before C0; graph expansion must never activate."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_graph_traverse_config,
        _build_graph_traverse_policy,
        _check_r1a_exact_cache,
    )
    from agentic_core.runtime.contracts.route_contract import RouteContract

    # Simulate what the binding does: build policy, then construct R1A with None
    profile_with_graph = {
        "graph_traverse": {
            "graph_expansion_allowed": True,
            "max_hops": 2,
        }
    }
    gt_config = _read_graph_traverse_config(profile_with_graph)
    graph_policy = _build_graph_traverse_policy(gt_config)
    assert graph_policy is not None, "precondition: policy built from enabled profile"

    # R1A RouteContract must carry None regardless of profile
    rc = RouteContract(
        request_id="req-r1a-test",
        run_id="run-r1a-test",
        app_id="apps_rg",
        trace_id="trace-r1a-test",
        route_id="R1A_EXACT_CACHE",
        l3_required=False,
        grounding_required=False,
        model_generation_required=False,
        write_authority_present=False,
        l5_certification_ref="test-l5-cert-w3-placeholder",
        graph_traverse_policy=None,
    )
    assert rc.graph_traverse_policy is None, (
        "R1A RouteContract must carry graph_traverse_policy=None — "
        "cache-only route skips C0"
    )


# ---------------------------------------------------------------------------
# 12. test_terminal_r5_route_has_no_graph_policy
# ---------------------------------------------------------------------------

def test_terminal_r5_route_has_no_graph_policy() -> None:
    """R5_PRE_ROUTE_FALLBACK RouteContract must carry graph_traverse_policy=None.
    Fallback terminal routes skip C0 entirely; graph expansion must never activate."""
    from agentic_core.runtime.contracts.route_contract import RouteContract

    rc = RouteContract(
        request_id="req-r5-test",
        run_id="run-r5-test",
        app_id="apps_rg",
        trace_id="trace-r5-test",
        route_id="R5_PRE_ROUTE_FALLBACK",
        l3_required=False,
        grounding_required=False,
        model_generation_required=False,
        write_authority_present=False,
        l5_certification_ref="test-l5-cert-w3-placeholder",
        graph_traverse_policy=None,
    )
    assert rc.graph_traverse_policy is None, (
        "R5 RouteContract must carry graph_traverse_policy=None — "
        "terminal fallback skips C0"
    )


# ---------------------------------------------------------------------------
# 13. test_r3_grounded_route_carries_graph_policy
# ---------------------------------------------------------------------------

def test_r3_grounded_route_carries_graph_policy() -> None:
    """R3_SIMPLE_GROUNDED_READ RouteContract must carry graph_traverse_policy
    when the profile has graph_expansion_allowed=true."""
    from agentic_core.L0_routing.package_driven_l0_binding import (
        _read_graph_traverse_config,
        _build_graph_traverse_policy,
    )
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from agentic_core.L0_routing.c0_retrieval.route_contract import GraphTraversePolicy

    profile = {
        "graph_traverse": {
            "graph_expansion_allowed": True,
            "max_hops": 2,
            "allowed_relation_types": ["CONTRADICTS", "GOVERNED_BY"],
        }
    }
    gt_config = _read_graph_traverse_config(profile)
    graph_policy = _build_graph_traverse_policy(gt_config)
    assert graph_policy is not None

    rc = RouteContract(
        request_id="req-r3-test",
        run_id="run-r3-test",
        app_id="apps_research",
        trace_id="trace-r3-test",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        l5_certification_ref="test-l5-cert-w3-placeholder",
        graph_traverse_policy=graph_policy,
    )
    assert rc.graph_traverse_policy is not None, (
        "R3 grounded route must carry graph_traverse_policy when profile enables it"
    )
    assert isinstance(rc.graph_traverse_policy, GraphTraversePolicy)
    assert rc.graph_traverse_policy.graph_expansion_allowed is True
    assert rc.graph_traverse_policy.max_hops == 2


# ---------------------------------------------------------------------------
# 14. test_graph_policy_only_for_c0_grounded_route
# ---------------------------------------------------------------------------

def test_graph_policy_only_for_c0_grounded_route() -> None:
    """Static AST check: in l0_evaluate_routes_package_driven(), graph_policy
    must only be passed to the R3 RouteContract, and None must be passed to R5/R1A.

    Validates the scoping invariant: graph expansion is only meaningful for
    routes that reach C0; terminal/cache-only routes must always carry None.
    """
    binding_path = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    source = binding_path.read_text(encoding="utf-8")

    # Find the l0_evaluate_routes_package_driven function body
    tree = ast.parse(source)
    eval_func = None
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "l0_evaluate_routes_package_driven"
        ):
            eval_func = node
            break

    assert eval_func is not None, "l0_evaluate_routes_package_driven not found"

    # Collect all keyword arguments named 'graph_traverse_policy' in RouteContract calls
    graph_policy_kwargs: list[dict] = []
    for node in ast.walk(eval_func):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "graph_traverse_policy":
                    # Determine the route_id keyword in the same call
                    route_id_val = None
                    for other_kw in node.keywords:
                        if other_kw.arg == "route_id":
                            if isinstance(other_kw.value, ast.Constant):
                                route_id_val = other_kw.value.value
                    is_none = isinstance(kw.value, ast.Constant) and kw.value.value is None
                    is_graph_policy_name = (
                        isinstance(kw.value, ast.Name) and kw.value.id == "graph_policy"
                    )
                    graph_policy_kwargs.append({
                        "route_id": route_id_val,
                        "lineno": node.lineno,
                        "is_none": is_none,
                        "is_graph_policy_name": is_graph_policy_name,
                    })

    assert graph_policy_kwargs, "No graph_traverse_policy kwargs found in eval function"

    for entry in graph_policy_kwargs:
        route_id = entry["route_id"]
        if route_id == "R3_SIMPLE_GROUNDED_READ":
            assert entry["is_graph_policy_name"], (
                f"R3 RouteContract at line {entry['lineno']} must pass graph_policy, "
                f"not None"
            )
        elif route_id in ("R5_PRE_ROUTE_FALLBACK", "R1A_EXACT_CACHE"):
            assert entry["is_none"], (
                f"{route_id} RouteContract at line {entry['lineno']} must pass "
                f"graph_traverse_policy=None, got graph_policy"
            )


# ---------------------------------------------------------------------------
# 15. test_l0_still_does_not_call_run_graph_traverse
# ---------------------------------------------------------------------------

def test_l0_still_does_not_call_run_graph_traverse() -> None:
    """Hardening regression: after the C0-grounded scoping patch, L0 must still
    never call run_graph_traverse() — AST check on binding source."""
    binding_path = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    )
    source = binding_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "run_graph_traverse":
                pytest.fail(
                    f"L0 binding calls run_graph_traverse() at line {node.lineno}"
                )
            if isinstance(func, ast.Attribute) and func.attr == "run_graph_traverse":
                pytest.fail(
                    f"L0 binding calls *.run_graph_traverse() at line {node.lineno}"
                )
