"""apps-test-model: APP CONTRACT.

Functional hotspot coverage must be contract-mapped for apps_rg hotspots.
"""

from __future__ import annotations

from pathlib import Path

from tools.analysis import functional_hotspot_test_gaps_report as report


FORMER_STRUCTURAL_ONLY_HOTSPOTS = {
    "apps_rg/__main__.py": "apps_rg.runtime_entrypoint.functional_chain",
    "apps_rg/runtime/bindings/c0_binding.py": "apps_rg.c0_fact_vector.functional_chain",
    "apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py": (
        "apps_rg.fact_inventory_closeout.functional_chain"
    ),
    "apps_rg/runtime/fact_vectors_bootstrap.py": "apps_rg.c0_fact_vector.functional_chain",
    "apps_rg/runtime/c0/fact_vector_write_back.py": "apps_rg.c0_fact_vector.functional_chain",
    "apps_rg/runtime/judges/bullet_pool_claude_selector.py": (
        "apps_rg.pool_selector.functional_chain"
    ),
    "apps_rg/runtime/c0/fact_vector_index_preflight.py": "apps_rg.c0_fact_vector.functional_chain",
    "apps_rg/runtime/bindings/l2_envelope_adapter.py": "apps_rg.l2_envelope.functional_chain",
    "apps_rg/runtime/orchestration/patch_run.py": "apps_rg.patch_run.functional_chain",
}


def _hotspot(path: str) -> dict[str, object]:
    return {
        "file": path,
        "layer": "L_APP",
        "priority_band": "P1_URGENT",
        "risk_band": "CRITICAL",
        "coverage_band": "ABSENT",
        "coverage_pct": -1.0,
        "criticality_score": 1.0,
        "combined_risk_score": 1.0,
        "fan_in": 0,
        "fan_out": 0,
        "violation_count": 0,
    }


def test_apps_rg_gap_report_hotspot_inventory_is_functionally_mapped() -> None:
    nodeids = report.collect_pytest_nodeids(Path("tests"))
    rows = report.analyze_hotspots(
        [_hotspot(path) for path in FORMER_STRUCTURAL_ONLY_HOTSPOTS],
        nodeids=nodeids,
        structural_reachability={},
        execution_results={},
    )

    by_file = {str(row["file"]): row for row in rows}
    assert set(by_file) == set(FORMER_STRUCTURAL_ONLY_HOTSPOTS)
    for path, contract_id in FORMER_STRUCTURAL_ONLY_HOTSPOTS.items():
        row = by_file[path]
        assert row["contract_id"] == contract_id
        assert row["gap_type"] == "not_run"
        assert row["missing_groups"] == []
        assert row["matched_nodeids"], path


def test_apps_rg_hotspot_inventory_never_counts_structural_edges_as_functional_pass() -> None:
    rows = report.analyze_hotspots(
        [_hotspot("apps_rg/runtime/bindings/c0_binding.py")],
        nodeids=["tests/unit/apps_rg/test_c0_evidence_room.py::test_c0_binding_importable"],
        structural_reachability={
            "apps_rg/runtime/bindings/c0_binding.py": {
                "structural_test_count": 49,
                "test_reachability_edges": 120,
            }
        },
        execution_results={
            "tests/unit/apps_rg/test_c0_evidence_room.py::test_c0_binding_importable": "passed"
        },
    )

    assert rows[0]["contract_id"] == "apps_rg.c0_fact_vector.functional_chain"
    assert rows[0]["gap_type"] == "not_collected"
    assert rows[0]["structural_test_count"] == 49
