from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import yaml

from tools.reports.adg_bcg_executive_synthesis import (
    build_artifact_usage_matrix,
    build_canonical_next_best_actions,
    build_mv_usefulness_audit,
    build_test_scope_inventory,
    emit_bcg_executive_summary,
    render_bcg_inline_markdown,
    synthesize_graphdb_decision_impact,
    synthesize_testing_investment_map,
)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


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
    graph = synthesize_graphdb_decision_impact(db, {}, [_gate("p0_ratchet", verdict="TRACK", records=99)], action_queue)
    artifacts = build_artifact_usage_matrix({"gate_results": tmp_path / "gate.json", "sqlite_snapshot": db}, {}, {"used_artifact_keys": ["sqlite_snapshot"]})
    mv = build_mv_usefulness_audit(db, graph, [])
    actions = build_canonical_next_best_actions([_gate("p0_ratchet", verdict="TRACK", records=99)], graph, testing, artifacts, mv, action_queue)
    assert actions["rows"][0]["action_type"] in {"repair_reporting", "add_tests", "burn_down_ratchet"}
    assert any(r["action_type"] == "add_tests" and r["scope"].startswith("apps_sales") for r in actions["rows"])


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
    _write_json(gate, {"timestamp": "run", "total_gates": 2, "overall_exit_code": 1, "gates": [_gate("blocker", records=1), _gate("ratchet", verdict="TRACK", records=5)]})
    _write_json(queue, {"actions": [{"scope": "apps_sales/runtime/checkout.py"}]})
    _write_json(review, {"artifact_kind": "adg_run_review_template"})
    _write_json(burndown, {"summary": {"P0": {"gross": 1, "guardian": 0, "net": 1}, "P1": {}, "P2": {}, "P3": {}}})

    rc, out = emit_bcg_executive_summary(
        artifacts,
        "run",
        db,
        gate,
        queue,
        review,
        burndown,
        {"structural_outputs": None, "refactor_accelerator": None, "graphdb_queries": None, "runtime_spine": None},
        print_inline=True,
    )
    assert rc == 0
    assert out == artifacts / "adg_bcg_executive_summary_run.json"
    for suffix in ("json", "yaml", "md"):
        assert (artifacts / f"adg_bcg_executive_summary_run.{suffix}").is_file()
        assert (artifacts / f"adg_bcg_executive_summary_latest.{suffix}").is_file()
        assert (Path("docs/reports/adg") / f"adg_bcg_executive_summary_latest.{suffix}").is_file()
    data = yaml.safe_load((artifacts / "adg_bcg_executive_summary_run.yaml").read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert data["artifact_kind"] == "adg_bcg_executive_summary"
    assert "lens_4_testing_control_gaps" in data
    md = (artifacts / "adg_bcg_executive_summary_run.md").read_text(encoding="utf-8")
    for section in [
        "## ADG Executive Brief",
        "### 1. What ADG Is",
        "### 2. Patient Size",
        "### 3. Executive Decision",
        "### 4. Gap Analysis — Lens 1: Health Gates",
        "### 5. Gap Analysis — Lens 2: Runtime Proof / Observability",
        "### 6. Gap Analysis — Lens 3: Product / App Risk",
        "### 7. Gap Analysis — Lens 4: Testing Control Gaps",
        "### 8. Gap Analysis — Lens 5: GraphDB / MV Decision Impact",
        "### 9. Next Best Actions",
        "### 10. Defer / Delete / Deprecate",
        "### 11. Honest Bottom Line",
    ]:
        assert section in md
    assert "## ADG Executive Brief" in capsys.readouterr().out


def test_render_markdown_accepts_locked_verdicts(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    db = artifacts / "x.sqlite"
    _sqlite(db)
    gate = artifacts / "gate.json"
    _write_json(gate, {"timestamp": "ts", "total_gates": 0, "overall_exit_code": 0, "gates": []})
    rc, out = emit_bcg_executive_summary(artifacts, "ts", db, gate, None, None, None, {}, print_inline=False)
    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["executive_decision"]["verdict"] in {"BLOCKED", "GREEN_WITH_DEBT", "REPORT_INCONSISTENT", "DEGRADED", "CLEAN", "NEEDS_RUNTIME_PROOF", "TESTING_CONTROL_GAP"}
    assert render_bcg_inline_markdown(doc).startswith("## ADG Executive Brief")
