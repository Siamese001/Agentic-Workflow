from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
import yaml

from tools.reports.adg_bcg_executive_synthesis import (
    BCG_INLINE_CONTRACT_PATH,
    build_artifact_usage_matrix,
    build_canonical_next_best_actions,
    build_deprecation_deletion_plan,
    build_mv_usefulness_audit,
    build_test_scope_inventory,
    emit_bcg_executive_summary,
    _load_locked_inline_contract,
    _validate_locked_bcg_inline_markdown,
    render_bcg_inline_markdown,
    synthesize_graphdb_decision_impact,
    synthesize_testing_investment_map,
)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _p0_plan(path: Path) -> None:
    _write_json(
        path,
        {
            "schema_version": "1.0",
            "plan_required": True,
            "summary": {
                "total_p0_issues": 3,
                "layer_violations": 1,
                "circular_imports": 1,
                "dynamic_exec": 1,
                "protected_layer_violations": 1,
            },
            "waves": [
                {
                    "wave_id": "wave_0_stop_the_line",
                    "items": [
                        {
                            "issue_type": "dynamic_exec",
                            "source_file": "agentic_core/L0_routing/router.py",
                            "line_no": 10,
                            "from_layer": "L0",
                            "to_layer": "",
                            "direct_fan_in": 20,
                            "protected_surface": True,
                        },
                        {
                            "issue_type": "circular_import",
                            "source_file": "agentic_core/L2_execution/loop.py",
                            "line_no": 20,
                            "from_layer": "L2",
                            "to_layer": "L3",
                            "direct_fan_in": 7,
                            "protected_surface": True,
                        },
                    ],
                },
                {
                    "wave_id": "wave_1_protected_planes",
                    "items": [
                        {
                            "issue_type": "layer_violation",
                            "source_file": "agentic_core/L5_safety/guard.py",
                            "line_no": 30,
                            "from_layer": "L5",
                            "to_layer": "L0",
                            "direct_fan_in": 11,
                            "protected_surface": True,
                        }
                    ],
                },
            ],
            "top_files": [
                {
                    "source_file": "agentic_core/L0_routing/router.py",
                    "issue_count": 1,
                    "direct_fan_in_max": 20,
                    "protected_surface": True,
                    "issue_kinds": ["dynamic_exec"],
                    "priority_score": 1020,
                }
            ],
        },
    )


def _p0_empty_plan(path: Path) -> None:
    _write_json(
        path,
        {
            "schema_version": "1.0",
            "plan_required": False,
            "summary": {
                "total_p0_issues": 0,
                "layer_violations": 0,
                "circular_imports": 0,
                "dynamic_exec": 0,
                "protected_layer_violations": 0,
            },
            "waves": [],
            "top_files": [],
        },
    )


def _gate(gate_id: str, *, verdict: str = "FIX", band: str = "P0", records: int = 1, baseline: int = 0) -> dict:
    classification = "blocked" if verdict == "FIX" else "pass"
    enforcement = "block" if verdict == "FIX" else "ratchet"
    return {
        "gate_id": gate_id,
        "band": band,
        "classification": classification,
        "enforcement": enforcement,
        "violation_count": records,
        "baseline_count": baseline,
    }


def _sqlite(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "create table mv_hotspot_coverage_risk(path text, priority_band text, risk_band text, coverage_band text, coverage_pct real, fan_in int, fan_out int, criticality_score real, combined_risk_score real, violation_count int)"
        )
        conn.execute(
            "insert into mv_hotspot_coverage_risk values (?,?,?,?,?,?,?,?,?,?)",
            ("apps_sales/runtime/checkout.py", "P1_URGENT", "CRITICAL", "ABSENT", 0, 12, 9, 90, 95, 3),
        )
        conn.execute("create table mv_p0_ratchet_inventory(path text)")
        conn.executemany("insert into mv_p0_ratchet_inventory values (?)", [("a.py",), ("b.py",)])
        conn.execute("create table mv_empty_noise(path text)")
        conn.execute("create table mv_guardian_inventory(path text)")
        conn.execute("insert into mv_guardian_inventory values ('guardian.py')")
        conn.execute("create table nodes(id int primary key, resolved_path text, layer text, type_surface text)")
        conn.execute("create table edges(src_id int, dst_id int, relation_type text)")
        conn.executemany(
            "insert into nodes values (?,?,?,?)",
            [
                (1, "agentic_core/L3/consumer.py", "L3", "surface"),
                (2, "agentic_core/L5/provider.py", "L5", "surface"),
                (3, "agentic_core/L1/wrapper.py", "L1", "surface"),
                (4, "agentic_core/L3/untyped.py", "L3", ""),
            ],
        )
        conn.executemany(
            "insert into edges values (?,?,?)",
            [
                (1, 2, "imports"),
                (1, 2, "imports"),
                (1, 2, "imports"),
                (1, 2, "imports"),
                (3, 4, "imports"),
            ],
        )
        conn.execute(
            "create table mv_gateway_bypass_paths(src_file text, src_layer text, provider_symbol text, line_no int, bypass_type text)"
        )
        conn.execute(
            "insert into mv_gateway_bypass_paths values (?,?,?,?,?)",
            ("agentic_core/providers/tool_call.py", "L5", "provider_tool", 42, "provider"),
        )


def _repo_tests(repo: Path) -> None:
    files = {
        "tests/unit/test_core.py": "import agentic_core.runtime.foo\ndef test_x():\n assert True\n",
        "tests/e2e/test_app.py": "from apps_sales.runtime import checkout\ndef test_x():\n assert checkout is not None\n",
        "tests/regression/test_tool.py": "import tools.reports.adg_action_queue\ndef test_x(monkeypatch):\n assert True\n",
        "tests/integration/test_int.py": "import apps_lic.foo\ndef test_x():\n assert True\n",
        "tests/smoke/test_smoke.py": "def test_x():\n assert True\n",
        "tests/golden/test_golden.py": "def test_x():\n assert True\n",
        "tests/contract/test_contract.py": "def test_x():\n assert True\n",
        "tests/fixtures/sample.py": "import pytest\n@pytest.fixture\ndef f(): return 1\n",
        "tests/misc/test_unknown.py": "def test_x():\n assert True\n",
    }
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (repo / "apps_sales/runtime").mkdir(parents=True, exist_ok=True)
    (repo / "apps_sales/runtime/checkout.py").write_text("def f(): return 1\n", encoding="utf-8")
    (repo / "agentic_core/runtime").mkdir(parents=True, exist_ok=True)
    (repo / "agentic_core/runtime/foo.py").write_text("x=1\n", encoding="utf-8")


def test_test_scope_inventory_classifies_all_required_scopes(tmp_path: Path) -> None:
    _repo_tests(tmp_path)
    inv = build_test_scope_inventory(tmp_path)
    types = {f["test_type"] for f in inv["files"]}
    assert {"unit", "e2e", "regression", "integration", "smoke", "golden", "contract", "fixture", "unknown"} <= types
    domains = {f["app_or_domain"] for f in inv["files"]}
    assert "agentic_core" in domains
    assert "apps_sales" in domains


def test_testing_map_can_prioritize_apps_testing_over_p0_ratchet(tmp_path: Path) -> None:
    _repo_tests(tmp_path)
    db = tmp_path / "adg.sqlite"
    _sqlite(db)
    inv = build_test_scope_inventory(tmp_path)
    action_queue = {"actions": [{"scope": "apps_sales/runtime/checkout.py", "why": "coverage"}]}
    testing = synthesize_testing_investment_map(db, tmp_path, inv, action_queue)
    assert "tests/e2e/test_app.py" in testing["investment_map"][0]["current_tests_found"]["e2e"]
    graph = synthesize_graphdb_decision_impact(db, {}, [_gate("p0_ratchet", verdict="TRACK", records=99)], action_queue)
    artifacts = build_artifact_usage_matrix({"gate_results": tmp_path / "gate.json", "sqlite_snapshot": db}, {}, {"used_artifact_keys": ["sqlite_snapshot"]})
    mv = build_mv_usefulness_audit(db, graph, [])
    actions = build_canonical_next_best_actions([_gate("p0_ratchet", verdict="TRACK", records=99)], graph, testing, artifacts, mv, action_queue)
    assert actions["rows"][0]["action_type"] in {"add_tests", "burn_down_ratchet"}
    assert any(r["action_type"] == "add_tests" and r["scope"].startswith("apps_sales") for r in actions["rows"])


def test_fix_blocker_rows_carry_canonical_priority_backing(tmp_path: Path) -> None:
    gate_rows = [
        {
            "gate_id": "B2_layer_skip_ratchet",
            "gate_class": "LayerSkipGate",
            "band": "P1",
            "enforcement": "ratchet",
            "violation_count": 895,
            "baseline_count": 891,
            "classification": "regressed",
        },
        {
            "gate_id": "C2_l5_bypass_pview",
            "gate_class": "L5BypassGate",
            "band": "P0",
            "enforcement": "block",
            "violation_count": 2,
            "baseline_count": None,
            "classification": "blocked",
        },
        {
            "gate_id": "F1_untyped_seam_ratchet",
            "gate_class": "UntypedSeamGate",
            "band": "P2",
            "enforcement": "ratchet",
            "violation_count": 1026,
            "baseline_count": 1019,
            "classification": "regressed",
        },
    ]
    db = tmp_path / "adg_bcg_executive_synthesis_test.sqlite"
    _sqlite(db)
    actions = build_canonical_next_best_actions(
        gate_rows,
        {"top_graph_risks": []},
        {"investment_map": []},
        {"rows": [{"artifact_key": "gate_results", "exists": True}, {"artifact_key": "sqlite_snapshot", "exists": True}]},
        {"rows": []},
        {},
        sqlite_path=db,
        run_id="run-123",
    )

    first_three = actions["rows"][:3]
    assert [r["scope"] for r in first_three] == [
        "C2_l5_bypass_pview",
        "B2_layer_skip_ratchet",
        "F1_untyped_seam_ratchet",
    ]
    assert first_three[0]["move"] == "Stop L5 gateway bypass"
    assert first_three[1]["move"] == "Clear layer-jump regression"
    assert first_three[2]["move"] == "Close untyped cross-layer seams"
    assert "provider/tool calls bypassing the l5 gateway" in first_three[0]["evidence"].lower()
    assert "direct dependency links" in first_three[1]["evidence"].lower()
    assert "cross-layer imports with empty type surfaces" in first_three[2]["evidence"].lower()
    assert "fix convenience coupling" in first_three[0]["next_step"].lower()
    assert "fix convenience coupling" in first_three[1]["next_step"].lower()
    assert "fix convenience coupling" in first_three[2]["next_step"].lower()
    assert first_three[0]["decision_options"][0]["label"] == "Fix"
    assert first_three[0]["done_condition"].startswith("Rerun ADG")


def test_canonical_next_best_actions_prioritizes_p0_over_p3_hygiene(tmp_path: Path) -> None:
    gate_rows = [
        {
            "gate_id": "S4_unused_imports_ratchet",
            "band": "P3",
            "enforcement": "ratchet",
            "violation_count": 10772,
            "baseline_count": 10750,
            "classification": "regressed",
        },
        {
            "gate_id": "13_core_imports_apps",
            "band": "P0",
            "enforcement": "block",
            "violation_count": 35,
            "classification": "blocked",
        },
        {
            "gate_id": "10_infra_wiring",
            "band": "P0",
            "enforcement": "block",
            "violation_count": 3,
            "classification": "blocked",
        },
        {
            "gate_id": "S2_uwg_bypass_ratchet",
            "band": "P0",
            "enforcement": "ratchet",
            "violation_count": 1601,
            "baseline_count": 1571,
            "classification": "regressed",
        },
        {
            "gate_id": "Q2_cyclomatic_complexity_ratchet",
            "band": "P3",
            "enforcement": "ratchet",
            "violation_count": 1168,
            "baseline_count": 1148,
            "classification": "regressed",
        },
    ]
    db = tmp_path / "adg_bcg_executive_synthesis_test.sqlite"
    _sqlite(db)
    actions = build_canonical_next_best_actions(
        gate_rows,
        {"top_graph_risks": []},
        {"investment_map": []},
        {"rows": [{"artifact_key": "gate_results", "exists": True}, {"artifact_key": "sqlite_snapshot", "exists": True}]},
        {"rows": []},
        {},
        sqlite_path=db,
        run_id="run-123",
    )

    assert [r["scope"] for r in actions["rows"][:3]] == [
        "10_infra_wiring",
        "13_core_imports_apps",
        "S2_uwg_bypass_ratchet",
    ]
    assert [r["move"] for r in actions["rows"][:3]] == [
        "Clear infra wiring P0 block",
        "Stop core importing apps",
        "Close UWG bypass regression",
    ]
    core_import_row = next(r for r in actions["rows"] if r["scope"] == "13_core_imports_apps")
    assert "35 core-to-app import row(s)" in core_import_row["evidence"]
    assert "S4_unused_imports_ratchet" not in [r["scope"] for r in actions["rows"][:3]]


def test_graphdb_mv_audit_classifies_all_mvs_and_suppresses_raw_counts(tmp_path: Path) -> None:
    db = tmp_path / "adg.sqlite"
    _sqlite(db)
    impact = synthesize_graphdb_decision_impact(db, {"structural_outputs": {"centrality": [{"path": "x"}]}}, [_gate("unrelated", verdict="FIX")], {})
    mv = build_mv_usefulness_audit(db, impact, [])
    names = {r["mv_name"] for r in mv["rows"]}
    assert {"mv_hotspot_coverage_risk", "mv_p0_ratchet_inventory", "mv_empty_noise", "mv_guardian_inventory"} <= names
    empty = next(r for r in mv["rows"] if r["mv_name"] == "mv_empty_noise")
    assert empty["recommendation"] == "deprecate_candidate"
    diagnostic = [r for r in impact["decision_impact_rows"] if r["decision_role"] == "diagnostic_monitor" and r["signal_type"] == "materialized_view"]
    assert all("Raw" in r["why_or_why_not"] or "not enough" in r["why_or_why_not"] for r in diagnostic)


def test_deprecation_deletion_plan_prioritizes_confirmed_dead_code_before_noise() -> None:
    dead_code_report = {
        "summary": {
            "total_dead_imports": 0,
            "total_dead_code_candidates": 2,
            "total_unresolved_imports": 17,
            "first_party_low_confidence_ratio": 2.5,
            "inferred_symbol_ratio": 9.0,
        },
        "dead_code_candidates": {
            "dead_code_hotspots": [
                ("ADG::Module::legacy_path", 4),
                ("ADG::Module::stale_path", 2),
            ]
        },
        "unresolved_imports": {"unresolved_hotspots": [("ADG::Module::tests/foo.py", 7)]},
        "low_confidence_zones": {"first_party_low_confidence_ratio": 2.5},
        "inferred_symbols": {"inferred_symbol_ratio": 9.0},
    }
    mv_audit = {
        "rows": [
            {
                "mv_name": "mv_empty_noise",
                "row_count": 0,
                "category": "stale_or_empty",
                "recommendation": "deprecate_candidate",
                "why_not_used_if_suppressed": "Raw MV count alone is not a funding signal.",
                "decision_impact": "Not promoted; no blocker/testing/action linkage.",
            }
        ]
    }
    artifacts = {
        "rows": [
            {"artifact_key": "dead_code_report", "used_for": ["audit"], "rationale": "report"},
            {"artifact_key": "unused_report", "used_for": ["none"], "rationale": "unused"},
        ]
    }

    plan = build_deprecation_deletion_plan(dead_code_report, mv_audit, artifacts)

    assert plan["priority_rows"][0]["scope"] == "ADG::Module::legacy_path"
    assert plan["priority_rows"][0]["decision"] == "delete_after_deprecation"
    assert plan["priority_rows"][1]["scope"] == "ADG::Module::stale_path"
    assert plan["priority_rows"][2]["move"] == "Triage unresolved imports"
    assert plan["summary"]["cleanup_candidate_count"] == 2


def test_locked_inline_contract_validates_final_bcg_shape() -> None:
    contract = _load_locked_inline_contract()
    expected_sections = [
        "## ADG Executive Brief",
        "| Question | Answer |",
        "ADG Run Metrics",
        "| Metric | Value |",
        "P0-P3 Severity Inventory",
        "| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |",
        "### Recommended Next Steps",
        "| Priority | Action | Evidence | Exit criterion |",
    ]

    assert BCG_INLINE_CONTRACT_PATH.name == "adg_bcg_inline_contract.locked.json"
    assert contract["render_inline_required"] is True
    assert contract["ordered_sections"] == expected_sections
    _validate_locked_bcg_inline_markdown("\n\n".join(expected_sections), contract)

    with pytest.raises(ValueError, match="forbidden legacy inline content"):
        _validate_locked_bcg_inline_markdown("\n\n".join(expected_sections + ["### 1. Key Findings"]), contract)

    bad_order = "\n\n".join(
        [
            "## ADG Executive Brief",
            "| Question | Answer |",
            "### Recommended Next Steps",
            "| Priority | Action | Evidence | Exit criterion |",
            "ADG Run Metrics",
            "| Metric | Value |",
            "P0-P3 Severity Inventory",
            "| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |",
        ]
    )
    with pytest.raises(ValueError, match="section/table out of order"):
        _validate_locked_bcg_inline_markdown(bad_order, contract)


def test_emit_bcg_summary_writes_locked_outputs_and_inline_structure(tmp_path: Path, capsys) -> None:
    _repo_tests(tmp_path)
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_run.sqlite"
    _sqlite(db)
    gate = artifacts / "adg_gate_results_run.json"
    queue = artifacts / "adg_action_queue_run.json"
    review = artifacts / "adg_review_template_run.json"
    burndown = artifacts / "adg_burndown_table.json"
    _write_json(
        gate,
        {
            "timestamp": "2026-06-18T18:02:31+00:00",
            "total_gates": 2,
            "overall_exit_code": 1,
            "gates": [_gate("blocker", records=1), _gate("ratchet", verdict="TRACK", records=5)],
        },
    )
    _write_json(queue, {"actions": [{"scope": "apps_sales/runtime/checkout.py"}]})
    _write_json(review, {"artifact_kind": "adg_run_review_template"})
    _write_json(burndown, {"summary": {"P0": {"gross": 1, "guardian": 0, "net": 1}, "P1": {}, "P2": {}, "P3": {}}})
    dead_code_report = artifacts / "dead_code_zone_control_report_run.json"
    _write_json(
        dead_code_report,
        {
            "status": "PASS",
            "dead_imports": {
                "total_dead_imports": 0,
                "dead_imports_by_layer": {},
                "dead_imports_by_domain": {},
                "dead_imports_by_confidence": {},
                "dead_import_hotspots": [],
                "l4_dead_imports": 0,
            },
            "dead_code_candidates": {
                "total_dead_code_candidates": 0,
                "dead_code_by_layer": {},
                "dead_code_by_entity_type": {},
                "dead_code_by_confidence": {},
                "dead_code_hotspots": [],
            },
            "unresolved_imports": {
                "total_unresolved_imports": 928,
                "unresolved_by_layer": {"": 928},
                "unresolved_by_confidence": {"LOW": 928},
                "unresolved_hotspots": [["ADG::Module::tests/foo.py", 9]],
                "l4_unresolved": 0,
            },
            "low_confidence_zones": {
                "total_low_confidence": 928,
                "low_conf_by_layer": {"": 928},
                "low_conf_by_entity_type": {"symbol": 928},
                "low_conf_by_identity_kind": {"unresolved_import": 928},
                "first_party_low_confidence_ratio": 3.0327788489819927,
                "governance_low_confidence_ratio": 0.0,
                "low_conf_hotspots": [["", 928]],
            },
            "inferred_symbols": {
                "total_inferred_symbols": 17161,
                "total_symbols": 173449,
                "inferred_symbol_ratio": 9.893974597720367,
                "inferred_by_layer": {"L0": 1},
                "inferred_by_confidence": {"MEDIUM": 1},
            },
            "executive_readiness": {
                "executive_metrics": {
                    "dead_import_count": 0,
                    "dead_code_count": 0,
                    "unresolved_import_count": 928,
                    "low_confidence_count": 928,
                    "l4_unresolved_import_count": 0,
                    "first_party_low_confidence_ratio": 3.0327788489819927,
                    "inferred_symbol_ratio": 9.893974597720367,
                },
                "first_party_metrics": {
                    "dead_import_count": 0,
                    "dead_code_count": 0,
                    "unresolved_import_count": 928,
                    "low_confidence_count": 928,
                    "l4_unresolved_import_count": 0,
                },
                "readiness_issues": [],
                "executive_ready": True,
            },
            "errors": [],
            "warnings": [],
            "summary": {
                "total_dead_imports": 0,
                "total_dead_code_candidates": 0,
                "total_unresolved_imports": 928,
                "total_low_confidence": 928,
                "l4_unresolved_imports": 0,
                "first_party_low_confidence_ratio": 3.0327788489819927,
                "inferred_symbol_ratio": 9.893974597720367,
                "executive_ready": True,
            },
        },
    )
    p0_plan = artifacts / "issues" / "p0_remediation_wave_plan_run.json"
    _p0_plan(p0_plan)

    docs = tmp_path / "docs_mirror"
    rc, out = emit_bcg_executive_summary(
        artifacts,
        "run",
        db,
        gate,
        queue,
        review,
        burndown,
        {"structural_outputs": None, "refactor_accelerator": None, "graphdb_queries": None, "runtime_spine": None, "p0_wave_plan": p0_plan, "dead_code_report": dead_code_report},
        print_inline=True,
        docs_dir=docs,
    )
    assert rc == 0
    assert out == artifacts / "adg_bcg_executive_summary_run.json"
    for suffix in ("json", "yaml", "md"):
        assert (artifacts / f"adg_bcg_executive_summary_run.{suffix}").is_file()
        assert (artifacts / f"adg_bcg_executive_summary_latest.{suffix}").is_file()
        assert (docs / f"adg_bcg_executive_summary_latest.{suffix}").is_file()
    data = yaml.safe_load((artifacts / "adg_bcg_executive_summary_run.yaml").read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert data["bcg_findings"]["title"] == "BCG Executive Brief"
    assert data["artifact_kind"] == "adg_bcg_executive_summary"
    assert data["raw_inputs"]["artifacts"]["sqlite_snapshot"].endswith("adg_indexed_run.sqlite")
    assert data["run"]["emit_status"] == "PASS"
    assert data["run"]["decision_grade_status"] in {
        "BLOCKED",
        "GREEN_WITH_DEBT",
        "REPORT_INCONSISTENT",
        "DEGRADED",
        "CLEAN",
        "NEEDS_RUNTIME_PROOF",
        "TESTING_CONTROL_GAP",
        "RUNTIME_PROOF_FAILING",
    }
    assert data["kpi_scorecard"]["rule"].startswith("Do not add these counts together")
    assert data["lens_0_p0_landmines"]["summary"]["wrong_way_imports"] == 1
    assert data["lens_0_p0_landmines"]["display_name"] == "Foundation blockers"
    assert data["lens_0_p0_landmines"]["landmines"][0]["protected_surface"] is True
    assert "lens_4_testing_control_gaps" in data
    assert data["dead_code_report"]["summary"]["total_dead_code_candidates"] == 0
    assert data["deprecation_deletion_plan"]["summary"]["executive_read"].startswith("No deletions are approved")
    for key in [
        "lens_0_p0_landmines",
        "lens_1_health_gates",
        "lens_2_runtime_proof_observability",
        "lens_3_product_app_risk",
        "lens_4_testing_control_gaps",
        "lens_5_graphdb_mv_decision_impact",
    ]:
        assert data[key]["why_it_matters"]
        assert data[key]["action_impact_rows"]
    md = (artifacts / "adg_bcg_executive_summary_run.md").read_text(encoding="utf-8")
    _validate_locked_bcg_inline_markdown(md)
    for section in [
        "## ADG Executive Brief",
        "| Question | Answer |",
        "| Can we merge? | No. A live P0 gate driver is red. |",
        "| What blocks merge? |",
        "ADG Run Metrics",
        "| Metric | Value |",
        "P0-P3 Severity Inventory",
        "| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |",
        "### Recommended Next Steps",
        "No deletions are approved in this run",
        "| Priority | Action | Evidence | Exit criterion |",
    ]:
        assert section in md
    assert md.index("| Question | Answer |") < md.index("ADG Run Metrics")
    assert md.index("ADG Run Metrics") < md.index("P0-P3 Severity Inventory")
    assert md.index("P0-P3 Severity Inventory") < md.index("### Recommended Next Steps")
    assert "- **Readout:**" not in md
    assert "### 1. Executive Bottom Line" not in md
    assert "North star:" not in md
    assert "Business read:" not in md
    assert "Technical evidence:" not in md
    assert "Fix now:" not in md
    assert "### BCG Executive Brief" not in md
    assert "### 1. What ADG Is" not in md
    assert "### 2. Patient Size" not in md
    assert "### 3. Executive Decision" not in md
    assert "Patient-size metrics were not available" not in md
    assert "Risk level:" not in md
    assert "### 3A. KPI Scorecard — Decision vs Audit" not in md
    assert "### 4. Lens 0 — Foundation Blockers" not in md
    assert "### 8. Gap Analysis — Lens 4: Testing Control Gaps" not in md
    assert "### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact" not in md
    assert "### BCG Deletion Brief" not in md
    assert "Action impact:" not in md
    assert "Business reason" not in md
    assert "Technical reason" not in md
    assert "Why this order" not in md
    assert "fix_blocker" not in md
    assert "| FIX gates (all bands) | 1 |" in md
    assert "| Live P0 gate drivers | 1 |" in md
    assert "| P0 action queue | no P0 action-queue rows |" in md
    assert "| P0 ledgers |" in md
    assert "foundation risk inventory=3; audit net backlog=1; live merge drivers=1" in md
    assert "Classify remaining P0 counts after the rerun" in md
    assert "Do not open a separate product/app workstream" in md
    assert "Keep deletion/deprecation cleanup after P0" in md
    assert "### 1. Key Findings" not in md
    assert "| Finding | What it says |" not in md
    assert "| Finding | What it says | Response |" not in md
    assert "| P0 | 1 | 0 | 1 | 3 | 1 |" in md
    assert "adg_indexed_run.sqlite" in md
    assert "| Snapshot | 2026-06-18T18:02:31+00:00 |" in md
    assert "## ADG Executive Brief" in capsys.readouterr().out


def test_inconsistent_report_brief_uses_decision_status_and_repair_next_step(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_run.sqlite"
    _sqlite_structural(db)
    gate = artifacts / "adg_gate_results_run.json"
    _write_json(gate, {"timestamp": "run", "total_gates": 1, "overall_exit_code": 1, "gates": [_gate("blocker", records=1)]})

    rc, out = emit_bcg_executive_summary(
        artifacts,
        "run",
        db,
        gate,
        None,
        None,
        None,
        {},
        print_inline=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["run"]["emit_status"] == "PASS"
    assert doc["run"]["decision_grade_status"] == "REPORT_INCONSISTENT"

    md = (artifacts / "adg_bcg_executive_summary_run.md").read_text(encoding="utf-8")
    assert "| Audit caveat | REPORT_INCONSISTENT; report consistency=FAIL |" in md
    assert "- **Emit status:** PASS" not in md
    assert "- **Status:** PASS" not in md
    assert "Business read:" not in md
    assert "Technical evidence:" not in md
    assert "ADG Run Metrics" in md
    assert "P0-P3 Severity Inventory" in md
    assert "P0 action queue" in md
    assert "Report consistency" in md
    assert "| Question | Answer |" in md
    assert "| Can we merge? | No. A live P0 gate driver is red. |" in md
    assert "| What blocks merge? | `blocker` has 1 blocking row(s). |" in md
    assert "### 1. Key Findings" not in md
    assert "| Repair graph/report consistency |" not in md
    assert "| 1 | Repair graph/report consistency |" not in md
    assert "### Recommended Next Steps" in md
    assert "Fix now:" not in md
    assert "| Priority | Action | Evidence | Exit criterion |" in md
    assert "Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3." in md
    assert "Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing." in md
    assert "Post-P0 ADG has report consistency PASS or an explicit waiver." in md
    assert "Next step: Repair graph/report consistency first." not in md


def test_inline_report_prioritizes_p0_wave_before_p1_fix(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_run.sqlite"
    _sqlite_structural(db)
    gate = artifacts / "adg_gate_results_run.json"
    queue = artifacts / "adg_action_queue_run.json"
    burndown = artifacts / "adg_burndown_table_run.json"
    _write_json(
        gate,
        {
            "timestamp": "run",
            "total_gates": 1,
            "overall_exit_code": 1,
            "gates": [
                {
                    "gate_id": "H1_new_orphans_delta_ratchet",
                    "band": "P1",
                    "enforcement": "ratchet",
                    "classification": "regressed",
                    "violation_count": 1,
                    "baseline_count": 0,
                    "status": "fail",
                }
            ],
        },
    )
    _write_json(
        queue,
        {
            "actions": [
                {"verdict_cluster": "FIX", "sort_band": "P1", "gate_id": "H1_new_orphans_delta_ratchet"},
                {
                    "verdict_cluster": "P0_WAVE",
                    "sort_band": "P0",
                    "action_kind": "p0_wave_file",
                    "file_path": "agentic_core/L1_cognition/__init__.py",
                },
                {
                    "verdict_cluster": "P0_WAVE",
                    "sort_band": "P0",
                    "action_kind": "p0_wave_file",
                    "file_path": "agentic_core/L1_cognition/apps_research_c0_binding.py",
                },
            ]
        },
    )
    _write_json(
        burndown,
        {
            "summary": {
                "P0": {"gross": 37, "guardian": 33, "net": 4},
                "P1": {"gross": 1, "guardian": 0, "net": 1},
                "P2": {},
                "P3": {},
            }
        },
    )

    rc, out = emit_bcg_executive_summary(
        artifacts,
        "run",
        db,
        gate,
        queue,
        None,
        burndown,
        {},
        print_inline=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["p0_action_queue_summary"]["p0_wave_count"] == 2
    md = (artifacts / "adg_bcg_executive_summary_run.md").read_text(encoding="utf-8")
    _validate_locked_bcg_inline_markdown(md)
    assert "| Can we merge? | No. ADG is red and P0 foundation/wave work remains before lower-severity lanes. |" in md
    assert "No. A P0 FIX gate is red." not in md
    assert "| Live P0 gate drivers | 0 |" in md
    assert "| P0 action queue | 2 P0 wave file row(s): agentic_core/L1_cognition/__init__.py, agentic_core/L1_cognition/apps_research_c0_binding.py |" in md
    assert "top red FIX gate=H1_new_orphans_delta_ratchet; rows=1" in md
    assert md.index("| 1 | Clear P0 foundation wave.") < md.rindex("Address H1_new_orphans_delta_ratchet")


def test_render_markdown_accepts_locked_verdicts(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    db = artifacts / "x.sqlite"
    _sqlite(db)
    gate = artifacts / "gate.json"
    _write_json(gate, {"timestamp": "ts", "total_gates": 0, "overall_exit_code": 0, "gates": []})
    rc, out = emit_bcg_executive_summary(artifacts, "ts", db, gate, None, None, None, {}, print_inline=False, docs_dir=tmp_path / "docs_mirror")
    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["executive_decision"]["verdict"] in {"BLOCKED", "GREEN_WITH_DEBT", "REPORT_INCONSISTENT", "DEGRADED", "CLEAN", "NEEDS_RUNTIME_PROOF", "TESTING_CONTROL_GAP", "RUNTIME_PROOF_FAILING"}
    assert render_bcg_inline_markdown(doc).startswith("## ADG Executive Brief")


# ---------------------------------------------------------------------------
# Substance: the synthesis must actually STUDY the structural graph MVs.
# ---------------------------------------------------------------------------

_STRUCT_SCOPE = "agentic_core/L0_routing/router.py"


def _sqlite_structural(path: Path) -> None:
    """ADG snapshot with real structural-graph MVs (centrality / blast radius / reverse
    deps / cones / chokepoints / SCC / newly-introduced) + a graph-vs-report mismatch."""
    with sqlite3.connect(path) as conn:
        conn.execute("create table mv_hotspot_coverage_risk(file text, priority_band text, risk_band text, coverage_band text, coverage_pct real, fan_in int, fan_out int, criticality_score real, combined_risk_score real, violation_count int)")
        conn.execute("insert into mv_hotspot_coverage_risk values (?,?,?,?,?,?,?,?,?,?)", (_STRUCT_SCOPE, "P1_URGENT", "CRITICAL", "ABSENT", 0, 40, 30, 95, 99, 7))
        conn.execute("create table mv_hotspot_centrality(node_id int, resolved_path text, layer text, fan_in int, fan_out int, degree int, betweenness_approx real, degree_centrality real)")
        conn.execute("insert into mv_hotspot_centrality values (1, ?, 'L0', 40, 30, 70, 0.42, 0.31)", (_STRUCT_SCOPE,))
        conn.execute("create table mv_graph_critical_path_blast_radius(node_id int, file_path text, layer text, direct_downstream int, hop2_downstream int, raw_blast_radius int, weighted_blast_radius real, critical_downstream_count int, blast_radius_type text)")
        conn.execute("insert into mv_graph_critical_path_blast_radius values (1, ?, 'L0', 20, 50, 70, 612.5, 12, 'critical')", (_STRUCT_SCOPE,))
        conn.execute("create table mv_graph_reverse_dependency_hotspots(node_id int, file_path text, layer text, direct_inbound int, hop2_inbound int, reverse_dependency_score real, layer_criticality_weight real)")
        conn.execute("insert into mv_graph_reverse_dependency_hotspots values (1, ?, 'L0', 35, 80, 410.0, 2.0)", (_STRUCT_SCOPE,))
        conn.execute("create table mv_dependency_cone_risk(node_id int, resolved_path text, layer text, direct_fan_in int, hop2_fan_in int, hop3_fan_in int, transitive_depth_approx int, cone_risk_score real)")
        conn.execute("insert into mv_dependency_cone_risk values (1, ?, 'L0', 35, 60, 90, 5, 288.0)", (_STRUCT_SCOPE,))
        conn.execute("create table mv_graph_chokepoint_bridges(node_id int, file_path text, layer text, fan_in int, fan_out int, bridge_score real, imbalance_ratio real, bridge_type text)")
        conn.execute("insert into mv_graph_chokepoint_bridges values (1, ?, 'L0', 40, 30, 120.0, 1.3, 'articulation')", (_STRUCT_SCOPE,))
        conn.execute("create table mv_graph_scc_clusters(node_id int, file_path text, layer text, cluster_size int, cluster_members text, scc_risk_score real, cluster_type text)")  # intentionally empty
        conn.execute("create table mv_newly_introduced_critical_paths(node_id int, adg_name text, layer text, file text, criticality_score real, prev_score real, delta real, is_new int)")
        conn.execute("insert into mv_newly_introduced_critical_paths values (1, 'ADG::Module::router', 'L0', ?, 99.0, 0.0, 99.0, 1)", (_STRUCT_SCOPE,))
        conn.execute("create table mv_graph_vs_report_mismatches(snapshot_id text, mismatch_type text, ref_id text, file text, detail text, mismatch_delta int)")
        conn.execute("insert into mv_graph_vs_report_mismatches values ('s', 'centrality_drift', 'n1', ?, 'report disagrees with graph', 3)", (_STRUCT_SCOPE,))


def test_structural_graph_mvs_are_actually_queried(tmp_path: Path) -> None:
    db = tmp_path / "adg.sqlite"
    _sqlite_structural(db)
    impact = synthesize_graphdb_decision_impact(db, {}, [_gate("c3_silent_writes", verdict="FIX")], {})
    risks = impact["top_graph_risks"]
    assert risks, "structural MVs must produce top_graph_risks"
    top = risks[0]
    assert top["scope"] == _STRUCT_SCOPE
    # Real values from the MVs — NOT the old NULL placeholders.
    assert top["centrality"] is not None
    assert top["blast_radius"] is not None
    assert top["reverse_dependency"] is not None
    assert top["dependency_cone"] is not None
    assert impact["summary"]["structural_mvs_queried"] >= 5
    # Empty SCC MV is handled (available, queried, zero rows used) — not a crash.
    assert impact["structural_mv_status"]["mv_graph_scc_clusters"]["available"] is True
    assert impact["structural_mv_status"]["mv_graph_scc_clusters"]["rows_used"] == 0


def test_high_blast_scope_overlapping_fix_emits_refactor_action(tmp_path: Path) -> None:
    _repo_tests(tmp_path)
    db = tmp_path / "adg.sqlite"
    _sqlite_structural(db)
    fix_gate = _gate(_STRUCT_SCOPE, verdict="FIX")  # gate id == scope → overlap
    inv = build_test_scope_inventory(tmp_path)
    testing = synthesize_testing_investment_map(db, tmp_path, inv, {})
    graph = synthesize_graphdb_decision_impact(db, {}, [fix_gate], {})
    artifacts = build_artifact_usage_matrix({"gate_results": tmp_path / "g.json", "sqlite_snapshot": db}, {}, {})
    mv = build_mv_usefulness_audit(db, graph, [fix_gate])
    actions = build_canonical_next_best_actions([fix_gate], graph, testing, artifacts, mv, {})
    assert any(r["action_type"] == "refactor" for r in actions["rows"]), [r["action_type"] for r in actions["rows"]]


def test_artifact_consistency_reflects_graph_vs_report_mismatches(tmp_path: Path) -> None:
    from tools.reports.adg_bcg_executive_synthesis import _artifact_consistency, _audit_notes

    db = tmp_path / "adg.sqlite"
    _sqlite_structural(db)  # has one mismatch row
    cons = _artifact_consistency(db)
    assert cons["status"] == "FAIL"
    assert cons["errors"]
    notes = _audit_notes([], None, cons)
    assert notes["artifact_consistency"]["status"] == "FAIL"


def test_artifact_consistency_pass_when_no_mismatch_rows(tmp_path: Path) -> None:
    from tools.reports.adg_bcg_executive_synthesis import _artifact_consistency

    db = tmp_path / "adg.sqlite"
    with sqlite3.connect(db) as conn:
        conn.execute("create table mv_graph_vs_report_mismatches(mismatch_type text, ref_id text, file text, detail text, mismatch_delta int)")
    assert _artifact_consistency(db)["status"] == "PASS"


def test_runtime_proof_distinguishes_quality_failure_from_measurement_gap(tmp_path: Path) -> None:
    from tools.reports.adg_bcg_executive_synthesis import _runtime_lens

    db = tmp_path / "adg.sqlite"
    _sqlite_structural(db)
    failing = _runtime_lens({"runtime_spine": {"semantic_failures": [{"x": 1}, {"y": 2}]}}, db)
    assert "FAILING" in failing["measurement_gap_vs_quality_failure"]
    spine = next(s for s in failing["runtime_proof_signals"] if s["signal"] == "runtime_spine")
    assert spine["status"] == "present_failing"
    missing = _runtime_lens({}, db)
    assert "measurement gap" in missing["measurement_gap_vs_quality_failure"].lower()


def test_artifact_staleness_flagged_on_divergent_timestamp(tmp_path: Path) -> None:
    current = tmp_path / "adg_structural_outputs_06132026_2227.json"
    current.write_text("{}", encoding="utf-8")
    old = tmp_path / "adg_structural_outputs_06012026_0900.json"
    old.write_text("{}", encoding="utf-8")
    m = build_artifact_usage_matrix({"current": current, "old": old}, {}, {"run_ts": "06132026_2227"})
    by = {r["artifact_key"]: r for r in m["rows"]}
    assert by["current"]["stale"] is False
    assert by["old"]["stale"] is True


def test_summary_fails_when_gate_artifacts_do_not_match_sqlite_snapshot(tmp_path: Path) -> None:
    from tools.reports.adg_bcg_executive_synthesis import build_bcg_executive_summary

    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_06272026_2302.sqlite"
    _sqlite(db)
    gate = artifacts / "adg_gate_results_20260627_091354.json"
    _write_json(gate, {"timestamp": "2026-06-27T09:13:54Z", "total_gates": 1, "gates": [_gate("old_blocker")]})
    _write_json(
        artifacts / "adg_generation_manifest_06272026_2302.json",
        {
            "certification_status": "failed",
            "sqlite_path": None,
            "snapshot_path": None,
        },
    )

    doc = build_bcg_executive_summary(
        artifacts,
        "06272026_2302",
        db,
        gate,
        None,
        None,
        None,
        {},
    )

    consistency = doc["audit_notes"]["artifact_consistency"]
    assert consistency["status"] == "FAIL"
    assert doc["executive_decision"]["verdict"] == "REPORT_INCONSISTENT"
    mismatch_types = {err["mismatch_type"] for err in consistency["errors"]}
    assert "artifact_timestamp_mismatch" in mismatch_types
    assert "generation_manifest_not_certified" in mismatch_types


def test_missing_artifact_is_not_loaded_or_used_even_if_requested(tmp_path: Path) -> None:
    missing = tmp_path / "missing_p0.json"
    matrix = build_artifact_usage_matrix(
        {"p0_wave_plan": missing},
        {},
        {"used_artifact_keys": ["p0_wave_plan"], "run_ts": "06152026_1200"},
    )
    row = matrix["rows"][0]
    assert row["exists"] is False
    assert row["loaded"] is False
    assert row["used_for"] == ["none"]


def test_p0_wave_plan_json_drives_lens_zero(tmp_path: Path) -> None:
    _repo_tests(tmp_path)
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_run.sqlite"
    _sqlite(db)
    gate = artifacts / "adg_gate_results_run.json"
    _write_json(gate, {"timestamp": "run", "total_gates": 1, "overall_exit_code": 1, "gates": [_gate("blocker", records=1)]})
    p0_json = artifacts / "issues" / "p0_remediation_wave_plan_run.json"
    _p0_plan(p0_json)

    rc, out = emit_bcg_executive_summary(
        artifacts,
        "run",
        db,
        gate,
        None,
        None,
        None,
        {"p0_wave_plan": p0_json},
        print_inline=False,
        docs_dir=tmp_path / "docs_mirror",
    )
    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    lens = doc["lens_0_p0_landmines"]
    assert lens["status"] == "present"
    assert lens["summary"]["dynamic_exec"] == 1
    assert lens["summary"]["circular_imports"] == 1
    assert lens["summary"]["wrong_way_imports"] == 1
    assert any(r["landmine"] == "Wrong-way layer import" for r in lens["landmines"])
    assert any(r["direct_fan_in"] == 20 for r in lens["landmines"])


def test_p0_scorecard_separates_foundation_blockers_from_audit_net(tmp_path: Path) -> None:
    _repo_tests(tmp_path)
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_run.sqlite"
    _sqlite(db)
    gate = artifacts / "adg_gate_results_run.json"
    _write_json(gate, {"timestamp": "run", "total_gates": 1, "overall_exit_code": 1, "gates": [_gate("G_REACH_l0_reachability", records=3)]})
    p0_json = artifacts / "issues" / "p0_remediation_wave_plan_run.json"
    _p0_empty_plan(p0_json)
    burndown = artifacts / "adg_burndown_table_run.json"
    _write_json(
        burndown,
        {
            "summary": {
                "P0": {"gross": 43, "guardian": 40, "net": 3},
                "P1": {"gross": 10, "guardian": 8, "net": 2},
                "P2": {"gross": 7, "guardian": 2, "net": 5},
                "P3": {"gross": 0, "guardian": 0, "net": 0},
            }
        },
    )

    rc, out = emit_bcg_executive_summary(
        artifacts,
        "run",
        db,
        gate,
        None,
        None,
        burndown,
        {"p0_wave_plan": p0_json},
        print_inline=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    kpis = {row["id"]: row for row in doc["kpi_scorecard"]["kpis"]}
    assert kpis["foundation_blockers"]["value"] == 0
    assert kpis["p0_audit_net"]["value"] == 3
    assert kpis["p0_live_gate_drivers"]["value"] == 1
    assert doc["audit_notes"]["guardian_summary"][0]["audit_net"] == 3
    assert doc["audit_notes"]["guardian_summary"][0]["non_exempt"] == 3
    assert doc["lens_0_p0_landmines"]["summary"]["foundation_blockers"] == 0

    md = (artifacts / "adg_bcg_executive_summary_run.md").read_text(encoding="utf-8")
    assert "P0-P3 Severity Inventory" in md
    assert "| Band | Gross | Guardian exempted | Net | Foundation blockers | Live gate drivers |" in md
    assert "| P0 | 43 | 40 | 3 | 0 | 1 |" in md
    assert "| P1 | 10 | 8 | 2 | n/a | 0 |" in md
    assert "| P2 | 7 | 2 | 5 | n/a | 0 |" in md
    assert "| P3 | 0 | 0 | 0 | n/a | 0 |" in md
    assert "### 1. Key Findings" not in md
    assert "foundation risk inventory=0; audit net backlog=3; live merge drivers=1" in md
    assert "| P0 ledgers |" in md
    assert "Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates." in md
    assert "Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate." in md
    assert "### 3A. KPI Scorecard — Decision vs Audit" not in md
    assert "### 4. Lens 0 — Foundation Blockers" not in md
    assert "### 4. Lens 0 — P0 Landmines / Foundation Cracks" not in md


def test_report_inconsistency_and_runtime_failure_precede_fix_gates() -> None:
    from tools.reports.adg_bcg_executive_synthesis import _verdict

    health = {
        "summary": {"fix_gates": 3, "track_gates": 0},
        "red_gates": [{"regression_delta": 99}],
    }
    testing = {"summary": {}}
    artifacts = {"rows": [{"artifact_key": "gate_results", "exists": True}]}
    assert _verdict(health, {"status": "present"}, testing, artifacts, {"status": "FAIL"})["verdict"] == "REPORT_INCONSISTENT"
    assert _verdict(health, {"status": "present_failing"}, testing, artifacts, {"status": "PASS"})["verdict"] == "RUNTIME_PROOF_FAILING"


def test_generator_uses_emitted_p0_wave_plan_json_path() -> None:
    src = Path("tools/generate/generate_full_adg.py").read_text(encoding="utf-8")
    assert "p0_wave_plan.get(\"json_path\")" in src
    assert "adg_p0_remediation_wave_plan_" not in src


def test_docs_dir_isolates_writes(tmp_path: Path) -> None:
    _repo_tests(tmp_path)
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    db = artifacts / "adg_indexed_run.sqlite"
    _sqlite_structural(db)
    gate = artifacts / "adg_gate_results_run.json"
    _write_json(gate, {"timestamp": "run", "total_gates": 1, "overall_exit_code": 1, "gates": [_gate("blk", records=1)]})
    docs = tmp_path / "docs_mirror"
    rc, _ = emit_bcg_executive_summary(artifacts, "run", db, gate, None, None, None, {}, print_inline=False, docs_dir=docs)
    assert rc == 0
    assert (docs / "adg_bcg_executive_summary_latest.md").is_file()
    assert (artifacts / "adg_bcg_executive_summary_latest.md").is_file()


def test_module_has_no_hardcoded_current_run_values() -> None:
    import tools.reports.adg_bcg_executive_synthesis as module

    src = Path(module.__file__).read_text(encoding="utf-8")
    for forbidden in ("571000", "12341", "5047", "2843", "1583", "10940", "4533"):
        assert forbidden not in src, f"forbidden current-run constant {forbidden} leaked into module"
