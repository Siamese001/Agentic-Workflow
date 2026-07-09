from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tools.analysis import functional_hotspot_test_gaps_report as report


def _hotspot(path: str) -> dict[str, object]:
    return {
        "file": path,
        "layer": "runtime",
        "priority_band": "P1_URGENT",
        "risk_band": "CRITICAL",
        "coverage_band": "ABSENT",
        "coverage_pct": -1.0,
        "criticality_score": 100.0,
        "combined_risk_score": 80.0,
        "fan_in": 10,
        "fan_out": 5,
        "violation_count": 2,
    }


def test_structural_reachability_is_not_functional_pass() -> None:
    rows = report.analyze_hotspots(
        [_hotspot("apps_rg/runtime/unmapped_hotspot.py")],
        nodeids=["tests/unit/apps_rg/test_bullet_selector_containment.py::test_imports_selector"],
        structural_reachability={
            "apps_rg/runtime/unmapped_hotspot.py": {
                "structural_test_count": 1,
                "test_reachability_edges": 4,
            }
        },
        execution_results={
            "tests/unit/apps_rg/test_bullet_selector_containment.py::test_imports_selector": "passed"
        },
    )

    assert rows[0]["gap_type"] == "structural_only"
    assert rows[0]["structural_test_count"] == 1
    assert rows[0]["contract_id"] == ""
    assert rows[0]["execution_status"] == "not_applicable"


@pytest.mark.parametrize(
    ("hotspot", "contract_id"),
    [
        ("apps_rg/__main__.py", "apps_rg.runtime_entrypoint.functional_chain"),
        ("apps_rg/runtime/bindings/c0_binding.py", "apps_rg.c0_fact_vector.functional_chain"),
        ("apps_rg/runtime/fact_vectors_bootstrap.py", "apps_rg.c0_fact_vector.functional_chain"),
        ("apps_rg/runtime/c0/fact_vector_write_back.py", "apps_rg.c0_fact_vector.functional_chain"),
        ("apps_rg/runtime/c0/fact_vector_index_preflight.py", "apps_rg.c0_fact_vector.functional_chain"),
        ("apps_rg/runtime/judges/bullet_pool_claude_selector.py", "apps_rg.pool_selector.functional_chain"),
        ("apps_rg/runtime/bindings/l2_envelope_adapter.py", "apps_rg.l2_envelope.functional_chain"),
        ("apps_rg/runtime/orchestration/patch_run.py", "apps_rg.patch_run.functional_chain"),
        (
            "apps_rg/fact_inventory/p2_graph_skills_accelerated_closeout.py",
            "apps_rg.fact_inventory_closeout.functional_chain",
        ),
    ],
)
def test_previous_structural_only_apps_rg_hotspots_have_functional_contract_mapping(
    hotspot: str,
    contract_id: str,
) -> None:
    contracts = report._contracts_for_path(hotspot, report.DEFAULT_CONTRACTS)

    assert [contract.contract_id for contract in contracts] == [contract_id]


def test_final_aggregation_contract_rejects_cross_app_and_core_aggregate_nodeids() -> None:
    rows = report.analyze_hotspots(
        [_hotspot("apps_rg/l2_recipe/modular_resume_generation.py")],
        nodeids=[
            "tests/_apps_contract/test_ag8_apps_lic_golden_path.py::TestA15_X2ConsumesX1Checkout::test_aggregate_decision_uses_x1_checkout_result",
            "tests/unit/agentic_core/L6_observability/utils/dashboard/test_dashboard_aggregation_rca.py::TestDashboardAggregationRca::test_dashboard_aggregation_rca_callable",
        ],
        structural_reachability={},
        execution_results={},
    )

    assert rows[0]["gap_type"] == "not_collected"
    assert rows[0]["matched_nodeids"] == []
    assert rows[0]["missing_groups"] == [
        "aggregation_contract",
        "same_run_fingerprint",
        "no_latest_successful",
    ]


def test_final_aggregation_contract_counts_only_apps_rg_functional_nodeids() -> None:
    nodeids = [
        "tests/unit/apps_rg/test_aggregation_run_fingerprint.py::test_final_resume_aggregation_contract_blocks_bad_rollup",
        "tests/unit/apps_rg/test_aggregation_run_fingerprint.py::test_same_run_fingerprint_current_run_binding",
        "tests/unit/apps_rg/test_modular_lane_provider_env.py::test_modular_generation_no_latest_successful_manifest_inference",
        "tests/_apps_contract/test_ag8_apps_lic_golden_path.py::TestA15_X2ConsumesX1Checkout::test_aggregate_decision_uses_x1_checkout_result",
    ]
    rows = report.analyze_hotspots(
        [_hotspot("apps_rg/l2_recipe/modular_resume_generation.py")],
        nodeids=nodeids,
        structural_reachability={},
        execution_results={nodeid: "passed" for nodeid in nodeids},
    )

    assert rows[0]["gap_type"] == "passing"
    assert set(rows[0]["matched_nodeids"]) == set(nodeids[:3])


def test_functional_contract_requires_all_required_groups_collected() -> None:
    rows = report.analyze_hotspots(
        [_hotspot("apps_rg/runtime/sections/executive_summary_lane.py")],
        nodeids=[
            "tests/unit/apps_rg/runtime/sections/test_executive_summary_lane.py::test_executive_summary_lane_runs"
        ],
        structural_reachability={},
        execution_results={},
    )

    assert rows[0]["gap_type"] == "not_collected"
    assert rows[0]["section_id"] == "executive_summary"
    assert rows[0]["missing_groups"] == [
        "proof_authority",
        "x2_gate",
        "x1d_or_judge",
    ]


def test_passing_requires_execution_report() -> None:
    nodeids = [
        "tests/unit/apps_rg/runtime/sections/test_executive_summary_lane.py::test_executive_summary_lane_runs",
        "tests/unit/apps_rg/test_executive_summary_evidence_capsule_authority.py::test_proof_pool_digest_matches",
        "tests/unit/apps_rg/test_executive_summary_product_shape_x2.py::test_x2_gate_blocks_weak_shape",
        "tests/unit/apps_rg/test_executive_summary_x1d_judge_contract.py::test_x1d_judge_contract_blocks_override",
    ]
    hotspot = _hotspot("apps_rg/runtime/sections/executive_summary_lane.py")

    without_execution = report.analyze_hotspots(
        [hotspot],
        nodeids=nodeids,
        structural_reachability={},
        execution_results={},
    )
    assert without_execution[0]["gap_type"] == "not_run"
    assert without_execution[0]["execution_status"] == "not_proven"

    with_execution = report.analyze_hotspots(
        [hotspot],
        nodeids=nodeids,
        structural_reachability={},
        execution_results={nodeid: "passed" for nodeid in nodeids},
    )
    assert with_execution[0]["gap_type"] == "passing"
    assert with_execution[0]["execution_status"] == "passed"


def test_render_report_calls_out_structural_vs_functional_coverage(tmp_path: Path) -> None:
    rows = report.analyze_hotspots(
        [_hotspot("apps_rg/runtime/judges/bullet_pool_claude_selector.py")],
        nodeids=[],
        structural_reachability={
            "apps_rg/runtime/judges/bullet_pool_claude_selector.py": {
                "structural_test_count": 2,
                "test_reachability_edges": 5,
            }
        },
        execution_results={},
    )

    md = report.render_report(
        rows,
        snapshot=tmp_path / "adg_indexed_test.sqlite",
        commit_sha="abc123",
        app="apps_rg",
        execution_report=None,
    )

    assert "does not count basename matches, imports, or ADG test-reachability" in md
    assert "`structural_only`" in md
    assert "bullet_pool_claude_selector.py" in md


def test_collect_pytest_nodeids_from_python_tests(tmp_path: Path) -> None:
    tests_root = tmp_path / "tests"
    test_file = tests_root / "unit" / "apps_rg" / "test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "\n".join(
            [
                "def test_module_level():",
                "    assert True",
                "",
                "class TestSample:",
                "    def test_method(self):",
                "        assert True",
            ]
        ),
        encoding="utf-8",
    )

    assert report.collect_pytest_nodeids(tests_root) == [
        "tests/unit/apps_rg/test_sample.py::test_module_level",
        "tests/unit/apps_rg/test_sample.py::TestSample::test_method",
    ]


def test_load_execution_results_accepts_pytest_json_report(tmp_path: Path) -> None:
    path = tmp_path / "pytest_report.json"
    path.write_text(
        json.dumps(
            {
                "tests": [
                    {"nodeid": "tests/unit/test_a.py::test_ok", "outcome": "passed"},
                    {"nodeid": "tests/unit/test_b.py::test_fail", "outcome": "failed"},
                ]
            }
        ),
        encoding="utf-8",
    )

    assert report.load_execution_results(path) == {
        "tests/unit/test_a.py::test_ok": "passed",
        "tests/unit/test_b.py::test_fail": "failed",
    }


def test_read_adg_inputs_from_sqlite(tmp_path: Path) -> None:
    db = tmp_path / "adg.sqlite"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
        INSERT INTO meta(key, value) VALUES ('commit_sha', 'abc123');

        CREATE TABLE mv_hotspot_coverage_risk(
            file TEXT,
            layer TEXT,
            priority_band TEXT,
            risk_band TEXT,
            coverage_band TEXT,
            coverage_pct REAL,
            criticality_score REAL,
            combined_risk_score REAL,
            fan_in INTEGER,
            fan_out INTEGER,
            violation_count INTEGER
        );
        INSERT INTO mv_hotspot_coverage_risk VALUES(
            'apps_rg/runtime/sections/executive_summary_lane.py',
            'runtime',
            'P1_URGENT',
            'CRITICAL',
            'ABSENT',
            -1.0,
            100.0,
            80.0,
            10,
            5,
            2
        );

        CREATE TABLE nodes(id INTEGER PRIMARY KEY, resolved_path TEXT);
        CREATE TABLE edges(src_id INTEGER, dst_id INTEGER, relation_type TEXT, source_file TEXT);
        INSERT INTO nodes VALUES(1, 'tests/unit/apps_rg/runtime/sections/test_executive_summary_lane.py');
        INSERT INTO nodes VALUES(2, 'apps_rg/runtime/sections/executive_summary_lane.py');
        INSERT INTO edges VALUES(1, 2, 'imports', 'tests/unit/apps_rg/runtime/sections/test_executive_summary_lane.py');
        """
    )
    con.close()

    data = report.read_adg_inputs(db, app="apps_rg", top=10)

    assert data["commit_sha"] == "abc123"
    assert data["hotspots"][0]["file"] == "apps_rg/runtime/sections/executive_summary_lane.py"
    assert data["structural_reachability"]["apps_rg/runtime/sections/executive_summary_lane.py"] == {
        "structural_test_count": 1,
        "test_reachability_edges": 1,
    }
