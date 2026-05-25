"""W10-AG stress/contract — unified C0.3 spine bind (apps_rg → agentic_core)."""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
    AdapterResolutionStatus,
    resolve_graph_adapter,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
    AnchorCandidate,
    AnchorType,
    HydratedEvidence,
    RetrievalLane,
    AclStatus,
)
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
from apps_rg.integrations.c0_graph_adapter import (
    AppsRgGraphAdapter,
    build_rg_graph_traverse_input,
    get_graph_adapter,
)
from apps_rg.runtime.bindings.c0_binding import (
    C0_GRAPH_LANE_NA_REF,
    _resolve_spine_graph_expansion_refs,
)
from apps_rg.runtime.bindings.l0_binding import APPS_RG_L0_CERT_REF, reset_route_profiles_cache

_REF_RG = "apps_rg.integrations.c0_graph_adapter"


@pytest.fixture(autouse=True)
def _clear_route_cache() -> None:
    reset_route_profiles_cache()
    yield
    reset_route_profiles_cache()


def test_adapter_registry_resolves_apps_rg_live() -> None:
    result = resolve_graph_adapter(_REF_RG)
    assert result.status == AdapterResolutionStatus.RESOLVED
    assert isinstance(result.adapter, AppsRgGraphAdapter)
    health = result.adapter.health_check()
    assert health.healthy is True


def test_build_rg_input_live_when_route_policy_active() -> None:
    route = {
        "graph_traverse": {
            "graph_expansion_allowed": True,
            "live_wiring_deferred": False,
            "max_hops": 1,
            "max_nodes": 32,
            "max_edges": 64,
            "allowed_relation_types": list(
                (
                    "DERIVED_FROM",
                    "IMPLEMENTS",
                    "EVIDENCE",
                )
            ),
            "graph_adapter_ref": _REF_RG,
        }
    }
    out = build_rg_graph_traverse_input(route, [])
    assert out["live_wiring_deferred"] is False
    assert out["wiring_gate"] == "LIVE"
    assert out["graph_adapter_ref"] == _REF_RG


def test_adapter_resolves_known_fact_anchor() -> None:
    adapter = get_graph_adapter()
    cand = AnchorCandidate(
        anchor_value="fact_engineering_platform_001",
        anchor_type=AnchorType.UNKNOWN,
        original_evidence_id="ev-1",
        hint_source_id="fact_vectors",
        confidence=0.85,
    )
    result = adapter.resolve_anchor(cand, {})
    assert hasattr(result, "resolved_node_id")
    assert "fact" in result.resolved_node_id or "engineering" in result.resolved_node_id


def test_maybe_run_graph_rag_stress_with_live_route() -> None:
    from agentic_core.runtime.c0.c0_3_graph_rag_executor import maybe_run_graph_rag

    policy = GraphTraversePolicy(
        graph_expansion_allowed=True,
        max_hops=1,
        max_nodes=32,
        max_edges=64,
        allowed_relation_types=(
            "DERIVED_FROM",
            "IMPLEMENTS",
            "EVIDENCE",
            "SUPPORTS",
            "RELATED_TO",
        ),
        graph_adapter_ref=_REF_RG,
        live_wiring_deferred=False,
        wiring_gate="LIVE",
    )
    route = RouteContract(
        request_id="req-w10ag",
        run_id="run-w10ag",
        app_id="apps_rg",
        trace_id="trace-w10ag",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id="apps_rg",
        route_family="R3_SIMPLE_GROUNDED_READ",
        execution_form="SINGLE_STEP",
        graph_traverse_policy=policy,
        l5_certification_ref=APPS_RG_L0_CERT_REF,
    )
    evidence = [
        type(
            "E",
            (),
            {
                "evidence_id": "ev:fact_engineering_platform_001",
                "source_ref": "fact_engineering_platform_001",
                "content_snippet": "platform engineering leadership",
            },
        )()
    ]
    gr = maybe_run_graph_rag(route, evidence)
    assert gr.executed is True, f"skip={gr.skip_reason} err={gr.error}"
    assert gr.pool is not None
    assert len(gr.pool.accepted_graph_neighbors) >= 0


def test_spine_graph_refs_not_na_with_live_policy() -> None:
    policy = GraphTraversePolicy(
        graph_expansion_allowed=True,
        max_hops=1,
        max_nodes=32,
        max_edges=64,
        allowed_relation_types=("EVIDENCE", "RELATED_TO", "DERIVED_FROM"),
        graph_adapter_ref=_REF_RG,
        live_wiring_deferred=False,
        wiring_gate="LIVE",
    )
    route = RouteContract(
        request_id="req-spine",
        run_id="run-spine",
        app_id="apps_rg",
        trace_id="trace-spine",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id="apps_rg",
        route_family="R3_SIMPLE_GROUNDED_READ",
        execution_form="SINGLE_STEP",
        graph_traverse_policy=policy,
        l5_certification_ref=APPS_RG_L0_CERT_REF,
    )
    item = type(
        "Item",
        (),
        {
            "source": "fact_engineering_platform_001",
            "source_id": "fact_engineering_platform_001",
            "content": "engineering platform",
            "evidence_id": "ev:fact_engineering_platform_001",
        },
    )()
    refs = _resolve_spine_graph_expansion_refs(route, [item])
    assert refs
    assert refs[0] != C0_GRAPH_LANE_NA_REF
    assert any(r.startswith("ref:graph:") for r in refs)


def test_route_profiles_yaml_live_graph_block() -> None:
    import yaml

    path = Path(__file__).resolve().parents[3] / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    default = next(r for r in rows if not r.get("conditions"))
    gt = default["graph_traverse"]
    assert gt["graph_expansion_allowed"] is True
    assert gt["live_wiring_deferred"] is False
    assert gt["graph_adapter_ref"] == _REF_RG
    assert gt["wiring_gate"] == "LIVE"
