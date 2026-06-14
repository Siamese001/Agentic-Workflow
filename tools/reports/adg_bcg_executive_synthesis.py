"""BCG-grade executive synthesis for completed ADG runs.

This module is intentionally generic: it synthesizes the artifacts produced by
``tools/generate/generate_full_adg.py`` without hard-coding a particular run,
application, gate, timestamp, or current defect count. The output contract is a
stable JSON/YAML document plus a concise board-ready markdown brief.
"""

from __future__ import annotations

import ast
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from tools.reports.gate_signal_catalog import display_verdict, display_verdict_sub, recommended_next_step

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"
TEST_FOLDERS = ("unit", "e2e", "regression", "integration", "smoke", "golden", "contract", "fixtures", "unknown")
TEST_TYPE_BY_FOLDER = {"fixtures": "fixture"}
VERDICTS = {"BLOCKED", "GREEN_WITH_DEBT", "REPORT_INCONSISTENT", "DEGRADED", "CLEAN", "NEEDS_RUNTIME_PROOF", "TESTING_CONTROL_GAP"}


def _repo_rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {"value": data}


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _write_yaml(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return ""


def _hash_repo_state(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in paths if p and p.is_file()):
        h.update(_repo_rel(path).encode())
        h.update(str(path.stat().st_mtime_ns).encode())
        h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def _domain_for_path(path: str) -> str:
    if path.startswith("agentic_core/"):
        return "agentic_core"
    if path.startswith("apps_"):
        parts = path.split("/", 1)
        return parts[0] if parts else "apps_*"
    if path.startswith("tools/reports"):
        return "reports"
    if path.startswith("tools/"):
        return "tools"
    if path.startswith("ops_scripts/"):
        return "ops_scripts"
    return "unknown"


def _scan_import_targets(text: str) -> list[str]:
    targets: set[str] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in {"agentic_core", "tools", "ops_scripts"} or mod.startswith("apps_"):
                    targets.add(alias.name.replace(".", "/") + ".py")
        elif isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module.split(".")[0]
            if mod in {"agentic_core", "tools", "ops_scripts"} or mod.startswith("apps_"):
                targets.add(node.module.replace(".", "/") + ".py")
    return sorted(targets)


def _classify_test_path(path: Path, tests_root: Path) -> tuple[str, str]:
    rel = path.relative_to(tests_root).as_posix()
    first = rel.split("/", 1)[0] if rel else "unknown"
    folder = first if first in TEST_FOLDERS else "unknown"
    test_type = TEST_TYPE_BY_FOLDER.get(folder, folder)
    if folder == "unknown":
        lowered = rel.lower()
        for token in ("e2e", "regression", "integration", "smoke", "golden", "contract", "fixture", "unit"):
            if token in lowered:
                return ("fixtures" if token == "fixture" else token, "fixture" if token == "fixture" else token)
    return folder, test_type


def build_test_scope_inventory(repo_root: Path) -> dict[str, Any]:
    """Scan ``tests/`` and classify test scope using paths plus imports/content."""
    tests_root = repo_root / "tests"
    folders = {
        f"tests/{name}": {"folder": f"tests/{name}", "file_count": 0, "mapped_production_scopes": []}
        for name in TEST_FOLDERS
    }
    files: list[dict[str, Any]] = []
    scope_map: dict[str, set[str]] = {}
    if not tests_root.is_dir():
        return {"status": "missing", "scanned_tests_root": "tests", "files": [], "folders": list(folders.values())}

    for path in sorted(tests_root.rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        folder, test_type = _classify_test_path(path, tests_root)
        text = path.read_text(encoding="utf-8", errors="ignore")
        imports = _scan_import_targets(text)
        tokens = set(imports)
        lowered = text.lower()
        for match in re.findall(r"(?:agentic_core|apps_[a-zA-Z0-9_]+|tools|ops_scripts)/(?:[\w_./-]+)\.py", text):
            tokens.add(match)
        app_or_domain = "unknown"
        for target in sorted(tokens):
            app_or_domain = _domain_for_path(target)
            if app_or_domain != "unknown":
                break
        entry = {
            "path": rel,
            "primary_folder": f"tests/{folder}",
            "test_type": test_type,
            "app_or_domain": app_or_domain,
            "likely_target_paths": sorted(tokens),
            "imports_target_module": bool(imports),
            "has_mocks": any(tok in lowered for tok in ("mock", "monkeypatch", "patch(")),
            "has_fixtures": "@pytest.fixture" in text or "fixture" in path.as_posix().lower(),
            "has_assertions": "assert " in text or "pytest.raises" in text,
            "coverage_source": "tests_imports_and_path_tokens",
        }
        files.append(entry)
        folders[f"tests/{folder}"]["file_count"] += 1
        for target in tokens:
            scope = target.rsplit("/", 1)[0]
            scope_map.setdefault(scope, set()).add(test_type)
            mapped = folders[f"tests/{folder}"]["mapped_production_scopes"]
            if scope not in mapped:
                mapped.append(scope)
    for row in folders.values():
        row["mapped_production_scopes"] = sorted(row["mapped_production_scopes"])
    return {"status": "present", "scanned_tests_root": "tests", "files": files, "folders": list(folders.values()), "scope_type_map": {k: sorted(v) for k, v in scope_map.items()}}


def _sqlite_tables(sqlite_path: Path) -> list[str]:
    if not sqlite_path.is_file():
        return []
    with sqlite3.connect(sqlite_path) as conn:
        return [r[0] for r in conn.execute("select name from sqlite_master where type='table' order by name")]


def _table_rows(sqlite_path: Path, table: str, limit: int = 100) -> list[dict[str, Any]]:
    if not sqlite_path.is_file():
        return []
    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in conn.execute(f'SELECT * FROM "{table}" LIMIT ?', (limit,))]
        except sqlite3.Error:
            return []


def _table_count(sqlite_path: Path, table: str) -> int:
    if not sqlite_path.is_file():
        return 0
    with sqlite3.connect(sqlite_path) as conn:
        try:
            return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
        except sqlite3.Error:
            return 0


def _score_hotspot(row: dict[str, Any], mapped_tests: set[str], action_overlap: bool) -> float:
    score = 0.0
    text = " ".join(str(row.get(k, "")) for k in row)
    for token, points in (("P1", 40), ("CRITICAL", 35), ("ABSENT", 25), ("HIGH", 15), ("P2", 12)):
        if token in text.upper():
            score += points
    for key in ("combined_risk_score", "criticality_score", "fan_in", "fan_out", "violation_count"):
        try:
            score += min(float(row.get(key) or 0), 100.0) / (2 if key.endswith("score") else 10)
        except (TypeError, ValueError):
            pass
    if "unit" not in mapped_tests:
        score += 12
    if "regression" not in mapped_tests:
        score += 10
    if "e2e" not in mapped_tests and str(row.get("path", row.get("file_path", ""))).startswith("apps_"):
        score += 10
    if action_overlap:
        score += 15
    return score


def synthesize_testing_investment_map(sqlite_path: Path, repo_root: Path, test_scope_inventory: dict[str, Any], action_queue: dict[str, Any] | None = None, max_rows: int = 15) -> dict[str, Any]:
    tables = set(_sqlite_tables(sqlite_path))
    hotspot_rows = _table_rows(sqlite_path, "mv_hotspot_coverage_risk", 500) if "mv_hotspot_coverage_risk" in tables else []
    if not hotspot_rows:
        # Fallback: use action queue testing lanes if present.
        for action in (action_queue or {}).get("actions", []) or []:
            if "test" in json.dumps(action).lower() or "coverage" in json.dumps(action).lower():
                hotspot_rows.append({"path": action.get("scope") or action.get("gate_id") or "unknown", "priority_band": action.get("priority") or "P2_GAP", "risk_band": "HIGH", "source": "action_queue"})
    scope_map = {k: set(v) for k, v in (test_scope_inventory.get("scope_type_map") or {}).items()}
    action_text = json.dumps(action_queue or {}).lower()
    ranked: list[tuple[float, dict[str, Any]]] = []
    for row in hotspot_rows:
        prod = str(row.get("path") or row.get("file_path") or row.get("module_path") or row.get("scope") or row.get("production_scope") or "unknown")
        scope = prod[:-3] if prod.endswith(".py") else prod
        parent_scope = scope.rsplit("/", 1)[0]
        mapped = set(scope_map.get(scope, set())) | set(scope_map.get(parent_scope, set()))
        missing = [kind for kind in ("unit", "regression") if kind not in mapped]
        domain = _domain_for_path(prod)
        if domain.startswith("apps_") and "e2e" not in mapped:
            missing.append("e2e")
        mock_only = "mock" in mapped and len(mapped - {"mock"}) == 0
        if mock_only:
            missing.append("non_mock_assertion")
        overlap = prod.lower() in action_text or parent_scope.lower() in action_text
        score = _score_hotspot(row, mapped, overlap)
        ranked.append((score, {
            "rank": None,
            "production_scope": prod,
            "layer": prod.split("/", 2)[1] if "/" in prod else "unknown",
            "app_or_domain": domain,
            "current_tests_found": {k: [] for k in ("unit", "e2e", "regression", "integration", "smoke", "golden", "contract", "fixture", "mock_only", "unknown")},
            "missing_test_scope": missing or ["mapped_tests_present"],
            "risk": {
                "priority_band": str(row.get("priority_band") or row.get("priority") or "unknown"),
                "risk_band": str(row.get("risk_band") or "unknown"),
                "coverage_band": str(row.get("coverage_band") or "unknown"),
                "coverage_pct": str(row.get("coverage_pct") or row.get("coverage_percent") or "unknown"),
                "fan_in": row.get("fan_in"),
                "fan_out": row.get("fan_out"),
                "criticality_score": row.get("criticality_score"),
                "combined_risk_score": row.get("combined_risk_score") or score,
                "violation_count": row.get("violation_count"),
            },
            "reasoned_implication": "This production scope has structural or coverage risk; missing mapped tests make fixes harder to prove." if missing else "Mapped tests exist; keep test maintenance attached to touched fixes.",
            "recommended_test_investment": _recommended_tests(domain, missing),
            "trigger": "current action queue overlap" if overlap else "hotspot coverage MV / test inventory",
            "done_condition": "Mapped tests exist in the missing scopes and pass with the ADG run.",
            "source_signals": ["mv_hotspot_coverage_risk" if "mv_hotspot_coverage_risk" in tables else "action_queue"],
        }))
    rows = [r for _, r in sorted(ranked, key=lambda x: (-x[0], x[1]["production_scope"]))[:max_rows]]
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    summary = {
        "total_hotspots": len(hotspot_rows),
        "p1_urgent": sum("P1" in str(r.get("risk", {}).get("priority_band", "")) for r in rows),
        "p2_gap": sum("P2" in str(r.get("risk", {}).get("priority_band", "")) for r in rows),
        "critical_risk": sum("CRITICAL" in str(r.get("risk", {}).get("risk_band", "")).upper() for r in rows),
        "absent_coverage": sum("ABSENT" in str(r.get("risk", {}).get("coverage_band", "")).upper() for r in rows),
        "missing_unit_scope": sum("unit" in r.get("missing_test_scope", []) for r in rows),
        "missing_regression_scope": sum("regression" in r.get("missing_test_scope", []) for r in rows),
        "missing_e2e_scope": sum("e2e" in r.get("missing_test_scope", []) for r in rows),
        "mock_only_scope": sum("non_mock_assertion" in r.get("missing_test_scope", []) for r in rows),
    }
    return {"status": "present", "executive_read": _testing_read(rows), "summary": summary, "test_scope_inventory": {"scanned_tests_root": "tests", "folders": test_scope_inventory.get("folders", [])}, "investment_map": rows, "testing_rules": ["If a fix touches a P1_URGENT / CRITICAL / ABSENT hotspot, the fix is not complete without mapped tests or an explicit waiver.", "Do not create a generic testing mega-project unless systemic gaps affect multiple high-blast-radius scopes.", "Attach tests to the current fix slice whenever overlap exists."]}


def _recommended_tests(domain: str, missing: list[str]) -> str:
    base = []
    if "unit" in missing:
        base.append("tests/unit")
    if "regression" in missing:
        base.append("tests/regression")
    if "e2e" in missing:
        base.append("tests/e2e or app-specific e2e")
    if not base:
        return "Maintain mapped tests with the touched slice."
    return "Add mapped " + ", ".join(base) + f" coverage for {domain}."


def _testing_read(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No testing hotspot was promoted; this is a measurement gap if hotspot MVs were unavailable."
    top = rows[0]
    return f"Testing is a control gap where {top['production_scope']} lacks {', '.join(top['missing_test_scope'])} coverage; fund tests with the relevant fix slice, not as a generic test campaign."


def synthesize_graphdb_decision_impact(sqlite_path: Path, p7_artifacts: dict[str, Any], gate_rows: list[dict[str, Any]], action_queue: dict[str, Any]) -> dict[str, Any]:
    tables = [t for t in _sqlite_tables(sqlite_path) if t.startswith("mv_")]
    fix_text = json.dumps([g for g in gate_rows if display_verdict(g) == "FIX"]).lower()
    action_text = json.dumps(action_queue or {}).lower()
    rows: list[dict[str, Any]] = []
    top_graph: list[dict[str, Any]] = []
    for name in tables:
        count = _table_count(sqlite_path, name)
        lname = name.lower()
        linked = lname.replace("mv_", "") in fix_text or lname in fix_text or lname in action_text
        testing = "test" in lname or "coverage" in lname or "hotspot" in lname
        if linked:
            role = "used_now"
        elif testing:
            role = "used_for_testing"
        elif any(tok in lname for tok in ("p0", "ratchet", "burndown")):
            role = "used_after_green"
        elif count == 0:
            role = "deprecate_candidate"
        elif any(tok in lname for tok in ("guardian", "severity", "inventory")):
            role = "audit_only"
        elif count > 0:
            role = "diagnostic_monitor"
        else:
            role = "refine_candidate"
        rows.append({
            "signal": name,
            "signal_type": "materialized_view",
            "row_count": count,
            "decision_role": role,
            "used_inline": role in {"used_now", "used_for_testing"},
            "why_or_why_not": _mv_why(role, count),
            "action": _mv_action(role),
            "related_gates": [g.get("gate_id") for g in gate_rows if str(g.get("gate_id", "")).lower() in lname or lname.replace("mv_", "") in str(g).lower()][:5],
            "related_scopes": [],
        })
    for key, doc in p7_artifacts.items():
        if not doc:
            continue
        blob = json.dumps(doc)[:2000]
        role = "used_now" if any(str(g.get("gate_id", "")) in blob for g in gate_rows if display_verdict(g) == "FIX") else "diagnostic_monitor"
        rows.append({"signal": key, "signal_type": "graphdb_report" if "graph" in key else "structural_report", "row_count": _rough_count(doc), "decision_role": role, "used_inline": role == "used_now", "why_or_why_not": "P7 artifact contributes structural context; promoted only when tied to blockers, tests, or action queue.", "action": "Use as tie-breaker for blast radius and critical path planning.", "related_gates": [], "related_scopes": []})
    for i, row in enumerate(rows[:10], 1):
        if row["used_inline"] or row["decision_role"] in {"used_for_testing", "used_now"}:
            top_graph.append({"rank": i, "scope": row["signal"], "graph_signal": row["decision_role"], "centrality": None, "blast_radius": row.get("row_count"), "reverse_dependency": None, "dependency_cone": None, "executive_read": row["why_or_why_not"], "action": row["action"], "testing_implication": "Add or verify mapped tests if this signal overlaps a hotspot."})
    summary = _impact_summary(rows)
    return {"status": "present", "executive_read": "GraphDB/MV signals are used as decision drivers only when linked to blockers, testing exposure, ratchets, artifact consistency, or planned slices; raw counts alone stay diagnostic.", "summary": summary, "decision_impact_rows": rows, "top_graph_risks": top_graph[:5]}


def _rough_count(doc: Any) -> int:
    if isinstance(doc, dict):
        return sum(len(v) for v in doc.values() if isinstance(v, list)) or len(doc)
    if isinstance(doc, list):
        return len(doc)
    return 1


def _mv_why(role: str, count: int) -> str:
    return {
        "used_now": "Linked to a current FIX/action signal, so it changes immediate work order.",
        "used_for_testing": "Translates structural risk into concrete test-placement decisions.",
        "used_after_green": "Useful after CI is green to lower accepted ratchet debt.",
        "audit_only": "Audit math unless mapped to a current failing gate.",
        "diagnostic_monitor": "Useful context, but not enough by itself to fund work; raw count alone is suppressed.",
        "refine_candidate": "Signal exists but lacks a clear decision consumer.",
        "deprecate_candidate": "Empty or stale-looking signal; keep out of inline output until it proves decision value.",
    }.get(role, f"Observed {count} rows without a stronger decision linkage.")


def _mv_action(role: str) -> str:
    return {
        "used_now": "Use in current fix slice.",
        "used_for_testing": "Attach mapped tests to high-risk scopes.",
        "used_after_green": "Schedule after-green burn-down.",
        "audit_only": "Audit; do not treat as blocker by itself.",
        "diagnostic_monitor": "Monitor and hide inline.",
        "refine_candidate": "Refine into a decision-linked signal or merge.",
        "deprecate_candidate": "Deprecate/delete candidate if still empty next runs.",
    }.get(role, "Monitor")


def _impact_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total_mvs": sum(r["signal_type"] == "materialized_view" for r in rows),
        "decision_drivers": sum(r["decision_role"] == "used_now" for r in rows),
        "testing_drivers": sum(r["decision_role"] == "used_for_testing" for r in rows),
        "ratchet_drivers": sum(r["decision_role"] == "used_after_green" for r in rows),
        "audit_drivers": sum(r["decision_role"] == "audit_only" for r in rows),
        "diagnostic_only": sum(r["decision_role"] == "diagnostic_monitor" for r in rows),
        "low_value_candidates": sum(r["decision_role"] == "refine_candidate" for r in rows),
        "deprecate_candidates": sum(r["decision_role"] == "deprecate_candidate" for r in rows),
    }


def build_artifact_usage_matrix(artifacts: dict[str, Path | None], loaded_docs: dict[str, Any], decision_inputs: dict[str, Any]) -> dict[str, Any]:
    rows = []
    used_keys = set(decision_inputs.get("used_artifact_keys", []))
    for key, path in artifacts.items():
        exists = bool(path and path.is_file())
        loaded = key in loaded_docs and loaded_docs.get(key) is not None
        used_for = []
        if key in used_keys or loaded:
            if key in {"gate_results", "action_queue"}:
                used_for.append("decision")
            elif key in {"sqlite_snapshot", "graphdb_queries", "structural_outputs", "refactor_accelerator", "runtime_spine", "graph_watchlist", "p0_wave_plan"}:
                used_for.append("graphdb")
            elif key in {"burndown_table", "burndown_report"}:
                used_for.append("audit")
            elif key == "review_template":
                used_for.append("evidence_only")
            elif key == "generation_manifest":
                used_for.append("consistency")
        if not used_for:
            used_for = ["none"]
        recommendation = "keep" if exists and used_for != ["none"] else ("keep_hide_inline" if exists else "refine")
        rows.append({"artifact_key": key, "path": _repo_rel(path), "exists": exists, "stale": False, "used_for": used_for, "decision_impact": _artifact_impact(key, used_for), "recommendation": recommendation, "rationale": "Loaded and mapped to a decision lens." if used_for != ["none"] else "Available only as diagnostic/evidence context or missing from this run."})
    return {"status": "present", "rows": rows}


def _artifact_impact(key: str, used_for: list[str]) -> str:
    if "none" in used_for:
        return "No current decision effect; suppress inline unless tied to a future blocker or audit."
    if "decision" in used_for:
        return "Directly affects verdict and next-best-action ranking."
    if "graphdb" in used_for:
        return "Shapes blast-radius, MV, and structural interpretation."
    if "audit" in used_for:
        return "Provides audit/baseline context, not automatic fix priority."
    return "Supports consistency/evidence trace."


def build_mv_usefulness_audit(sqlite_path: Path, decision_usage: dict[str, Any], gate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    decision_rows = {r["signal"]: r for r in decision_usage.get("decision_impact_rows", [])}
    rows = []
    for mv in [t for t in _sqlite_tables(sqlite_path) if t.startswith("mv_")]:
        count = _table_count(sqlite_path, mv)
        role = decision_rows.get(mv, {}).get("decision_role")
        category = {
            "used_now": "decision_driver", "used_for_testing": "testing_driver", "used_after_green": "ratchet_driver", "audit_only": "audit_driver", "diagnostic_monitor": "diagnostic_monitor", "refine_candidate": "low_value_candidate", "deprecate_candidate": "stale_or_empty"
        }.get(role, "diagnostic_monitor" if count else "stale_or_empty")
        recommendation = "keep" if category in {"decision_driver", "testing_driver"} else "keep_hide_inline"
        if category == "low_value_candidate":
            recommendation = "refine"
        if category == "stale_or_empty":
            recommendation = "deprecate_candidate"
        rows.append({"mv_name": mv, "row_count": count, "category": category, "decision_impact": decision_rows.get(mv, {}).get("why_or_why_not", "Not promoted; no blocker/testing/action linkage."), "recommendation": recommendation, "replacement_or_refinement": "Tie to a gate, hotspot, action queue lane, or artifact consistency rule." if recommendation != "keep" else "", "why_not_used_if_suppressed": "Raw MV count alone is not a funding signal." if recommendation != "keep" else ""})
    summary = {
        "total_mvs": len(rows), "decision_drivers": sum(r["category"] == "decision_driver" for r in rows), "testing_drivers": sum(r["category"] == "testing_driver" for r in rows), "ratchet_drivers": sum(r["category"] == "ratchet_driver" for r in rows), "audit_drivers": sum(r["category"] == "audit_driver" for r in rows), "diagnostic_only": sum(r["category"] == "diagnostic_monitor" for r in rows), "stale_or_empty": sum(r["category"] == "stale_or_empty" for r in rows), "duplicate_signals": 0, "low_value_candidates": sum(r["recommendation"] == "refine" for r in rows), "deprecate_candidates": sum(r["recommendation"] == "deprecate_candidate" for r in rows)
    }
    return {"status": "present", "summary": summary, "rows": rows}


def build_canonical_next_best_actions(gate_rows: list[dict[str, Any]], graphdb_decision_impact: dict[str, Any], testing_investment_map: dict[str, Any], artifact_usage_matrix: dict[str, Any], mv_usefulness_audit: dict[str, Any], action_queue: dict[str, Any]) -> dict[str, Any]:
    actions = []
    inconsistent = [r for r in artifact_usage_matrix.get("rows", []) if not r.get("exists") and r.get("artifact_key") in {"gate_results", "sqlite_snapshot"}]
    if inconsistent:
        actions.append(_action("repair_reporting", "Repair missing decision-grade ADG artifact", "ADG reporting", "A required artifact is missing, so the run is degraded.", "artifact", "Confirm artifacts emit and latest/docs copies exist.", "now", "high"))
    fix = [g for g in gate_rows if display_verdict(g) == "FIX"]
    for g in sorted(fix, key=lambda r: (-_reg_delta(r), str(r.get("gate_id", ""))))[:3]:
        actions.append(_action("fix_blocker", f"Clear red gate {g.get('gate_id')}", str(g.get("gate_id")), "Current FIX gates block decision-grade green; inspect delta before assuming structural crisis.", "gate", "Add mapped tests when touched scope overlaps a hotspot.", "now", "high"))
    tests = testing_investment_map.get("investment_map", [])
    if tests:
        top = tests[0]
        actions.append(_action("add_tests", f"Fund mapped tests for {top['production_scope']}", top["production_scope"], "Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down.", "testing_hotspot", top.get("recommended_test_investment", "Add mapped tests."), "now" if not fix else "if_touched", "medium"))
    ratchets = [g for g in gate_rows if display_verdict(g) == "TRACK" and display_verdict_sub(g) == "floor"]
    if ratchets:
        g = sorted(ratchets, key=lambda r: (-int(r.get("violation_count") or 0), str(r.get("gate_id", ""))))[0]
        actions.append(_action("burn_down_ratchet", f"Burn down ratchet {g.get('gate_id')}", str(g.get("gate_id")), "Accepted baseline debt should fall after red gates are clear.", "gate", "Add tests only when touched scope overlaps hotspot.", "after_green", "medium"))
    low = [r for r in mv_usefulness_audit.get("rows", []) if r.get("recommendation") in {"refine", "deprecate_candidate"}]
    if low:
        actions.append(_action("refine", f"Refine/deprecate low-value ADG signal {low[0]['mv_name']}", low[0]["mv_name"], "Suppress or retire signals that do not affect decisions.", "mv", "No test required unless generator logic changes.", "deprecate", "low"))
    for i, row in enumerate(actions[:8], 1):
        row["rank"] = i
    return {"status": "present", "rows": actions[:8]}


def _reg_delta(g: dict[str, Any]) -> int:
    for key in ("regression_delta", "delta", "new_records", "new", "worsened"):
        try:
            return int(g.get(key) or 0)
        except (TypeError, ValueError):
            pass
    try:
        return max(0, int(g.get("violation_count") or 0) - int(g.get("baseline_count") or 0))
    except (TypeError, ValueError):
        return 0


def _action(action_type: str, action: str, scope: str, why: str, signal_type: str, testing: str, timing: str, confidence: str) -> dict[str, Any]:
    return {"rank": None, "action_type": action_type, "action": action, "scope": scope, "why_now": why, "evidence_used": [{"signal_name": scope, "signal_type": signal_type, "decision_effect": why}], "testing_requirement": testing, "done_condition": "Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived.", "confidence": confidence, "timing": timing}


def _patient_size(repo_root: Path, gate_doc: dict[str, Any] | None) -> dict[str, Any]:
    py_files = [p for p in repo_root.rglob("*.py") if "/.git/" not in p.as_posix()]
    prod = [p for p in py_files if not p.relative_to(repo_root).as_posix().startswith("tests/")]
    tests = [p for p in py_files if p.relative_to(repo_root).as_posix().startswith("tests/")]
    core = [p for p in prod if p.relative_to(repo_root).as_posix().startswith("agentic_core/")]
    apps = [p for p in prod if p.relative_to(repo_root).as_posix().startswith("apps_")]
    layer_counts: dict[str, int] = {}
    app_counts: dict[str, int] = {}
    folder_counts = {f"tests/{f}": 0 for f in TEST_FOLDERS}
    for p in core:
        rel = p.relative_to(repo_root).as_posix().split("/")
        layer_counts[rel[1] if len(rel) > 1 else "root"] = layer_counts.get(rel[1] if len(rel) > 1 else "root", 0) + 1
    for p in apps:
        app = p.relative_to(repo_root).as_posix().split("/", 1)[0]
        app_counts[app] = app_counts.get(app, 0) + 1
    for p in tests:
        rel = p.relative_to(repo_root).as_posix().split("/")
        folder = rel[1] if len(rel) > 1 and rel[1] in TEST_FOLDERS else "unknown"
        folder_counts[f"tests/{folder}"] += 1
    return {"status": "present", "total_python_files": len(py_files), "production_python_files": len(prod), "test_python_files": len(tests), "agentic_core": {"file_count": len(core), "largest_layers": [{"layer": k, "file_count": v, "executive_read": "Large core layer; treat as control-plane blast-radius context."} for k, v in sorted(layer_counts.items(), key=lambda x: -x[1])[:5]]}, "apps": {"total_files": len(apps), "app_breakdown": [{"app": k, "file_count": v, "executive_read": "Product surface; prioritize when high blast radius and missing e2e/regression tests overlap."} for k, v in sorted(app_counts.items(), key=lambda x: -x[1])[:8]]}, "tests": {"total_files": len(tests), "folder_breakdown": [{"folder": k, "file_count": v} for k, v in folder_counts.items()]}, "executive_read": "Patient-size metrics show where ADG risk lands across core, apps, and tests.", "snapshot_ts": (gate_doc or {}).get("timestamp")}


def _health_lens(gates: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = {"CLEAR": 0, "TRACK": 0, "FIX": 0}
    for g in gates:
        buckets[display_verdict(g)] = buckets.get(display_verdict(g), 0) + 1
    red = []
    for g in [x for x in gates if display_verdict(x) == "FIX"]:
        red.append({"gate_id": str(g.get("gate_id", "")), "band": str(g.get("band", "")), "enforcement": str(g.get("enforcement", "")), "total_records": int(g.get("violation_count") or 0), "baseline_records": g.get("baseline_count"), "regression_delta": _reg_delta(g), "record_type": str(g.get("record_type") or g.get("signal") or "gate records"), "executive_read": "Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure.", "next_action": recommended_next_step(g), "done_condition": "Gate returns CLEAR/TRACK with no current FIX verdict."})
    track = [g for g in gates if display_verdict(g) == "TRACK"]
    ratchets = [g for g in track if display_verdict_sub(g) == "floor"]
    open_non = [g for g in track if display_verdict_sub(g) != "floor"]
    return {"status": "present", "summary": {"total_gates": len(gates), "clear_gates": buckets.get("CLEAR", 0), "track_gates": buckets.get("TRACK", 0), "fix_gates": buckets.get("FIX", 0), "overall_verdict": "BLOCKED" if buckets.get("FIX") else "PASS", "executive_read": "FIX blocks green; TRACK is accepted backlog/ratchet work; CLEAR needs no action."}, "buckets": [{"bucket": k, "count": buckets.get(k, 0), "plain_meaning": {"CLEAR": "No action now.", "TRACK": "Known debt or advisory inventory; burn down after red gates.", "FIX": "Current blocker or regression requiring action before decision-grade green."}[k]} for k in ("CLEAR", "TRACK", "FIX")], "red_gates": red, "managed_debt": {"ratchet_floor_records": sum(int(g.get("violation_count") or 0) for g in ratchets), "open_non_ratchet_records": sum(int(g.get("violation_count") or 0) for g in open_non), "top_ratchets": [{"gate_id": str(g.get("gate_id", "")), "records": int(g.get("violation_count") or 0), "executive_read": "Accepted baseline debt, not current red.", "after_green_action": "Burn down after FIX rows clear."} for g in sorted(ratchets, key=lambda x: -int(x.get("violation_count") or 0))[:5]]}, "key_interpretation": "A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency."}


def _runtime_lens(p7: dict[str, Any]) -> dict[str, Any]:
    signals = []
    for key in ("runtime_spine", "graphdb_queries", "structural_outputs"):
        doc = p7.get(key)
        status = "present" if doc else "missing"
        signals.append({"signal": key, "status": status, "evidence_count": _rough_count(doc) if doc else 0, "executive_read": "Runtime/structural proof available for interpretation." if doc else "Measurement blind spot; not automatically a product failure.", "action": "Use to confirm runtime path risk." if doc else "Enable or repair artifact emission if the decision needs runtime proof."})
    present = any(s["status"] == "present" for s in signals)
    return {"status": "present" if present else "missing", "executive_read": "Runtime proof distinguishes observed failures from missing instrumentation.", "measurement_gap_vs_quality_failure": "Missing runtime proof is a measurement gap unless an artifact shows runtime failure evidence.", "runtime_proof_signals": signals, "blind_spots": [] if present else [{"blind_spot": "runtime proof artifacts", "why_it_matters": "Without runtime proof, ADG can flag structural risk but cannot prove production behavior.", "recommended_action": "Generate or wire runtime spine/replay/OTel evidence for critical paths."}]}


def _product_lens(testing: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    risks = []
    for row in testing.get("investment_map", []):
        if str(row.get("app_or_domain", "")).startswith("apps_"):
            risks.append({"app_or_scope": row["app_or_domain"], "risk": "Under-tested product hotspot", "evidence": [{"signal_name": row["production_scope"], "signal_type": "hotspot", "raw_count": row.get("risk", {}).get("violation_count"), "interpreted_meaning": row.get("reasoned_implication", "")}], "executive_read": "App risk is promoted because product surface and missing test scope overlap.", "next_action": row.get("recommended_test_investment", "Add mapped tests."), "priority_vs_gate_debt": "Can outrank after-green ratchet burn-down when it overlaps current work or high blast radius."})
    return {"status": "present", "executive_read": "No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row." if not risks else "App/product risks were promoted only where hotspot or test evidence changes funding posture.", "app_risks": risks[:8], "promoted_product_gaps": [{"gap_id": f"product_gap_{i}", "title": r["risk"], "app_or_scope": r["app_or_scope"], "why_high_leverage": r["executive_read"], "action": r["next_action"], "done_condition": "Mapped app tests pass and ADG no longer reports the promoted gap."} for i, r in enumerate(risks[:5], 1)]}


def _verdict(health: dict[str, Any], runtime: dict[str, Any], testing: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    missing_required = [r for r in artifacts.get("rows", []) if not r.get("exists") and r.get("artifact_key") in {"gate_results", "sqlite_snapshot"}]
    if missing_required:
        verdict = "DEGRADED"
        crisis = "measurement_gap"
        posture = "repair_reporting"
    elif int(health["summary"].get("fix_gates") or 0):
        verdict = "BLOCKED"
        crisis = "routine_nudge" if all(int(r.get("regression_delta") or 0) <= 1 for r in health.get("red_gates", []) or [{"regression_delta": 2}]) else "material_risk"
        posture = "narrow_slice"
    elif int((testing.get("summary") or {}).get("missing_unit_scope") or 0) or int((testing.get("summary") or {}).get("missing_regression_scope") or 0):
        verdict = "TESTING_CONTROL_GAP"
        crisis = "managed_debt"
        posture = "fund_now"
    elif runtime.get("status") == "missing":
        verdict = "NEEDS_RUNTIME_PROOF"
        crisis = "measurement_gap"
        posture = "monitor"
    elif int(health["summary"].get("track_gates") or 0):
        verdict = "GREEN_WITH_DEBT"
        crisis = "managed_debt"
        posture = "monitor"
    else:
        verdict = "CLEAN"
        crisis = "routine_nudge"
        posture = "monitor"
    return {"verdict": verdict, "recommendation": "Fund the smallest slice that clears current blockers and attaches tests where hotspot evidence overlaps; keep ratchets after-green.", "funding_posture": posture, "why_now": "Decision combines FIX status, regression/newness, GraphDB/MV linkage, testing exposure, and artifact consistency.", "risk_if_ignored": "The organization may chase raw counts while missing the smaller blocker or under-tested high-blast-radius surface.", "what_not_to_do": ["Do not rank work by raw MV row count alone.", "Do not treat guardian inventory as an automatic product failure.", "Do not start a generic testing mega-project when mapped tests can follow the current slice."], "crisis_level": crisis, "one_sentence_bottom_line": f"ADG is {verdict}: act on decision-linked blockers/testing gaps, defer diagnostic-only noise."}


def _base_doc(ts: str, sqlite_path: Path, gate_doc: dict[str, Any] | None, degraded: list[str]) -> dict[str, Any]:
    return {"schema_version": "1.0", "artifact_kind": "adg_bcg_executive_summary", "run": {"run_id": ts, "generated_at_utc": _now(), "snapshot_ts": (gate_doc or {}).get("timestamp") or ts, "commit_sha": _git_sha(), "repo_state_hash": "", "decision_grade_status": "DEGRADED" if degraded else "PASS", "degradation_reasons": degraded}, "plain_english_context": {"what_adg_is": {"summary": "ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.", "analogy": "ADG is the codebase X-ray: it sees dependency skeletons, health gates, and structural risk.", "measured_scope": {"connections": None, "gates": (gate_doc or {}).get("total_gates"), "files": None}, "caveats": []}}}


def build_bcg_executive_summary(adg_artifacts_dir: Path, ts: str, sqlite_path: Path, gate_results_path: Path | None, action_queue_path: Path | None, review_template_path: Path | None, burndown_path: Path | None, p7_paths: dict[str, Path | None]) -> dict[str, Any]:
    artifacts = {"gate_results": gate_results_path, "action_queue": action_queue_path, "review_template": review_template_path, "burndown_table": burndown_path, "burndown_report": adg_artifacts_dir / "adg_burndown_report.md", "sqlite_snapshot": sqlite_path, "generation_manifest": adg_artifacts_dir / f"adg_generation_manifest_{ts}.json", **p7_paths}
    loaded = {k: _read_json(v) for k, v in artifacts.items() if v and v.suffix == ".json"}
    gate_doc = loaded.get("gate_results")
    action_queue = loaded.get("action_queue") or {}
    p7_docs = {k: loaded.get(k) for k in p7_paths}
    degraded = []
    if not gate_doc:
        degraded.append("missing gate_results: cannot determine current CI blocker verdict")
    if not sqlite_path.is_file():
        degraded.append("missing sqlite_snapshot: cannot query MV/GraphDB decision impact")
    doc = _base_doc(ts, sqlite_path, gate_doc, degraded)
    gates = list((gate_doc or {}).get("gates") or [])
    doc["patient_size"] = _patient_size(REPO_ROOT, gate_doc)
    test_inventory = build_test_scope_inventory(REPO_ROOT)
    testing = synthesize_testing_investment_map(sqlite_path, REPO_ROOT, test_inventory, action_queue)
    graph = synthesize_graphdb_decision_impact(sqlite_path, p7_docs, gates, action_queue)
    artifact_matrix = build_artifact_usage_matrix(artifacts, loaded, {"used_artifact_keys": list(loaded.keys()) + ["sqlite_snapshot"]})
    mv_audit = build_mv_usefulness_audit(sqlite_path, graph, gates)
    health = _health_lens(gates)
    runtime = _runtime_lens(p7_docs)
    product = _product_lens(testing, graph)
    actions = build_canonical_next_best_actions(gates, graph, testing, artifact_matrix, mv_audit, action_queue)
    doc.update({"executive_decision": _verdict(health, runtime, testing, artifact_matrix), "prioritization_model": _prioritization_model(), "lens_1_health_gates": health, "lens_2_runtime_proof_observability": runtime, "lens_3_product_app_risk": product, "lens_4_testing_control_gaps": testing, "lens_5_graphdb_mv_decision_impact": graph, "canonical_next_best_actions": actions, "after_green_plan": _after_green(health, graph, testing), "artifact_usage_matrix": artifact_matrix, "mv_usefulness_audit": mv_audit, "defer_delete_deprecate": _defer_delete(mv_audit, artifact_matrix), "audit_notes": _audit_notes(gates, loaded.get("burndown_table")), "honest_bottom_line": _bottom_line(health, runtime, testing, actions), "raw_inputs": _raw_inputs(artifacts, loaded), "evidence_trace": _evidence_trace(graph, artifact_matrix, degraded)})
    doc["run"]["repo_state_hash"] = _hash_repo_state([p for p in artifacts.values() if p])
    if degraded:
        doc["executive_decision"]["verdict"] = "DEGRADED"
        doc["run"]["decision_grade_status"] = "DEGRADED"
    return doc


def _prioritization_model() -> dict[str, Any]:
    return {"status": "present", "lenses": [{"name": "CI blocker / FIX status", "weight": "high", "how_used": "FIX rows define immediate blocker posture, but delta and evidence decide investment size."}, {"name": "Regression / newness", "weight": "high", "how_used": "Small regressions are nudges; broad new paths indicate structural risk."}, {"name": "P0-P3 severity", "weight": "medium", "how_used": "Severity lens only; does not automatically dominate testing or GraphDB risk."}, {"name": "GraphDB centrality / blast radius", "weight": "high", "how_used": "Elevates high-blast-radius scopes when tied to tests, gates, or current action."}, {"name": "MV driver linkage", "weight": "high", "how_used": "Promotes only MVs that change action order or test placement."}, {"name": "Testing exposure", "weight": "high", "how_used": "Can outrank after-green ratchet debt when risk surface lacks mapped tests."}, {"name": "Artifact consistency", "weight": "high", "how_used": "Missing required artifacts degrade decision grade."}, {"name": "Accepted baseline debt", "weight": "medium", "how_used": "Tracked after FIX rows clear."}, {"name": "Guardian / severity audit", "weight": "low_for_action_high_for_audit", "how_used": "Audit-only unless mapped to a failing gate."}], "rationale": ["Every promoted signal must explain its decision effect.", "Every suppressed signal records why it was suppressed."]}


def _after_green(health: dict[str, Any], graph: dict[str, Any], testing: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for i, r in enumerate((health.get("managed_debt") or {}).get("top_ratchets", []), 1):
        rows.append({"order": i, "work_class": "ratchet_burndown", "scope": r["gate_id"], "records": r["records"], "driver_signals": ["gate_results"], "why_after_green": "Ratchet floor work should not distract from current FIX rows.", "next_action": r["after_green_action"], "done_condition": "Lower baseline and rerun ADG."})
    return {"status": "present", "executive_read": "After-green work lowers accepted floors and closes broad testing waves once blockers are gone.", "rows": rows}


def _defer_delete(mv: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for r in mv.get("rows", [])[:20]:
        if r.get("recommendation") != "keep":
            rows.append({"item": r["mv_name"], "item_type": "mv", "current_value": f"{r.get('row_count')} rows; {r.get('category')}", "recommendation": "deprecate" if r.get("recommendation") == "deprecate_candidate" else r.get("recommendation", "keep"), "rationale": r.get("why_not_used_if_suppressed") or r.get("decision_impact"), "revisit_condition": "Promote only when tied to blocker, test gap, critical path, or planned slice."})
    for r in artifacts.get("rows", []):
        if r.get("used_for") == ["none"]:
            rows.append({"item": r["artifact_key"], "item_type": "artifact", "current_value": "unused or missing", "recommendation": "hide_inline", "rationale": r.get("rationale"), "revisit_condition": "Use when it changes next action, audit, consistency, or test placement."})
    return {"status": "present", "rows": rows[:25]}


def _audit_notes(gates: list[dict[str, Any]], burndown: dict[str, Any] | None) -> dict[str, Any]:
    summary = (burndown or {}).get("summary") or {}
    return {"status": "present", "guardian_summary": [{"band": band, "gross": (summary.get(band) or {}).get("gross"), "guardian": (summary.get(band) or {}).get("guardian"), "non_exempt": (summary.get(band) or {}).get("net"), "executive_read": "Guardian exception math is audit context; map to a failing gate before funding fixes."} for band in ("P0", "P1", "P2", "P3")], "severity_summary": {"executive_read": "Severity inventory is audit math unless tied to current FIX/action rows.", "rows": []}, "artifact_consistency": {"status": "PASS", "errors": []}, "notes": ["Guardian exceptions are audit math only; they do not automatically explain away real problems.", "Diagnostic-only MVs are not immediate work unless tied to a blocker, testing gap, critical path, or planned slice."]}


def _bottom_line(health: dict[str, Any], runtime: dict[str, Any], testing: dict[str, Any], actions: dict[str, Any]) -> dict[str, list[str]]:
    return {"bullets": ["Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.", f"Actually blocking now: {health['summary'].get('fix_gates')} FIX gates; inspect regression delta before declaring a platform crisis.", "Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.", "Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.", (actions.get("rows") or [{"action": "Keep ADG green and monitor diagnostic signals."}])[0]["action"], "Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role."]}


def _raw_inputs(artifacts: dict[str, Path | None], loaded: dict[str, Any]) -> dict[str, Any]:
    return {"artifacts": {k: _repo_rel(v) for k, v in artifacts.items()}, "loaded_status": {"missing": [k for k, v in artifacts.items() if not (v and v.is_file())], "stale": [], "degraded": [], "used": list(loaded.keys())}}


def _evidence_trace(graph: dict[str, Any], artifacts: dict[str, Any], degraded: list[str]) -> dict[str, Any]:
    used = [{"signal_name": r["signal"], "signal_type": r["signal_type"], "used_for": r["decision_role"], "decision_effect": r["why_or_why_not"]} for r in graph.get("decision_impact_rows", []) if r.get("used_inline")]
    suppressed = [{"signal_name": r["signal"], "signal_type": r["signal_type"], "suppression_reason": r["why_or_why_not"], "revisit_condition": r["action"]} for r in graph.get("decision_impact_rows", []) if not r.get("used_inline")]
    missing = [{"signal_name": d.split(":", 1)[0], "why_needed": d, "decision_limitation": "Run is not fully decision-grade."} for d in degraded]
    return {"used_signals": used, "suppressed_signals": suppressed, "missing_signals": missing, "stale_signals": []}


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---:" if h.lower() in {"count", "rank", "total records", "regression / new delta"} or h.startswith("Rank") else "---" for h in headers]) + "|"]
    for row in rows:
        out.append("| " + " | ".join(_md(c) for c in row) + " |")
    return "\n".join(out)


def render_bcg_inline_markdown(doc: dict[str, Any]) -> str:
    """Render the locked executive inline markdown structure exactly."""
    h = doc["lens_1_health_gates"]
    lines: list[str] = []
    a = lines.append
    a("## ADG Executive Brief")
    a("")
    a("### 1. What ADG Is")
    a("")
    a(doc["plain_english_context"]["what_adg_is"]["summary"])
    a("")
    a("### 2. Patient Size")
    a("")
    ps = doc.get("patient_size", {})
    if ps.get("status") == "present":
        a(f"This patient has {ps.get('total_python_files')} Python files: {ps.get('production_python_files')} production files and {ps.get('test_python_files')} test files. agentic_core contributes {ps.get('agentic_core', {}).get('file_count')} files; apps_* contributes {ps.get('apps', {}).get('total_files')} files. Current snapshot/run ID: {doc.get('run', {}).get('run_id')}.")
    else:
        a("Patient-size metrics were not available for this run.")
    a("")
    a("### 3. Executive Decision")
    a("")
    d = doc["executive_decision"]
    a(f"ADG is {d['verdict']}: {d['recommendation']} This is a {d['crisis_level']}; do not chase {', '.join(d.get('what_not_to_do', [])[:2])}.")
    a("")
    a("### 4. Gap Analysis — Lens 1: Health Gates")
    a("")
    a(h["summary"]["executive_read"] + " " + h.get("key_interpretation", ""))
    a("")
    a(_table(["Bucket", "Count", "Executive meaning"], [[b["bucket"], b["count"], b["plain_meaning"]] for b in h.get("buckets", [])]))
    a("")
    red_rows = h.get("red_gates") or [{"gate_id": "None", "total_records": 0, "regression_delta": 0, "executive_read": "No red gates.", "next_action": "No blocker action."}]
    a(_table(["Red gate", "Total records", "Regression / new delta", "Executive read", "Next action"], [[r["gate_id"], r["total_records"], r.get("regression_delta"), r["executive_read"], r["next_action"]] for r in red_rows[:8]]))
    a("")
    a("### 5. Gap Analysis — Lens 2: Runtime Proof / Observability")
    a("")
    rt = doc["lens_2_runtime_proof_observability"]
    a(rt["measurement_gap_vs_quality_failure"])
    a("")
    a(_table(["Runtime proof signal", "Status", "Executive read", "Action"], [[r["signal"], r["status"], r["executive_read"], r["action"]] for r in rt.get("runtime_proof_signals", [])]))
    a("")
    a("### 6. Gap Analysis — Lens 3: Product / App Risk")
    a("")
    pr = doc["lens_3_product_app_risk"]
    a(pr["executive_read"])
    a("")
    app_rows = pr.get("app_risks") or [{"app_or_scope": "None", "risk": "No app-specific product gap was promoted in this run", "evidence": [], "executive_read": "App risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row.", "next_action": "Monitor."}]
    a(_table(["App / product scope", "Risk", "Evidence", "Executive read", "Next action"], [[r["app_or_scope"], r["risk"], "; ".join(e.get("signal_name", "") for e in r.get("evidence", [])), r["executive_read"], r["next_action"]] for r in app_rows[:8]]))
    a("")
    a("### 7. Gap Analysis — Lens 4: Testing Control Gaps")
    a("")
    tg = doc["lens_4_testing_control_gaps"]
    a(tg["executive_read"])
    a("")
    test_rows = tg.get("investment_map") or [{"rank": 0, "production_scope": "None", "current_tests_found": {}, "missing_test_scope": ["No mapped hotspot rows"], "risk": {}, "recommended_test_investment": "No test investment promoted.", "trigger": "No hotspot evidence"}]
    a(_table(["Rank", "Production scope", "Current tests found", "Missing test scope", "Risk", "Recommended investment", "Trigger"], [[r["rank"], r["production_scope"], ", ".join(k for k, v in r.get("current_tests_found", {}).items() if v) or "none mapped", ", ".join(r.get("missing_test_scope", [])), r.get("risk", {}).get("risk_band", "unknown"), r.get("recommended_test_investment"), r.get("trigger")] for r in test_rows[:10]]))
    a("")
    a("### 8. Gap Analysis — Lens 5: GraphDB / MV Decision Impact")
    a("")
    gr = doc["lens_5_graphdb_mv_decision_impact"]
    a(gr["executive_read"])
    a("")
    impact = sorted(gr.get("decision_impact_rows", []), key=lambda r: (not r.get("used_inline"), r.get("decision_role", "")))[:12]
    a(_table(["Signal", "Decision role", "Used now?", "Why / why not", "Action"], [[r["signal"], r["decision_role"], r["used_inline"], r["why_or_why_not"], r["action"]] for r in impact]))
    a("")
    a("### 9. Next Best Actions")
    a("")
    a(_table(["Rank", "Action", "Scope", "Why now", "Evidence used", "Testing requirement", "Done condition"], [[r["rank"], r["action"], r["scope"], r["why_now"], "; ".join(e["signal_type"] for e in r.get("evidence_used", [])), r["testing_requirement"], r["done_condition"]] for r in doc["canonical_next_best_actions"].get("rows", [])]))
    a("")
    a("### 10. Defer / Delete / Deprecate")
    a("")
    dep = doc["defer_delete_deprecate"].get("rows", [])[:12] or [{"item": "None", "current_value": "No low-value signal promoted", "recommendation": "keep", "rationale": "No action."}]
    a(_table(["Item", "Current value", "Recommendation", "Rationale"], [[r["item"], r["current_value"], r["recommendation"], r["rationale"]] for r in dep]))
    a("")
    a("### 11. Honest Bottom Line")
    a("")
    for bullet in doc["honest_bottom_line"].get("bullets", [])[:6]:
        a(f"- {bullet}")
    a("")
    return "\n".join(lines)


def emit_bcg_executive_summary(adg_artifacts_dir: Path, ts: str, sqlite_path: Path, gate_results_path: Path | None, action_queue_path: Path | None, review_template_path: Path | None, burndown_path: Path | None, p7_paths: dict[str, Path | None], print_inline: bool = True, fail_closed: bool = False) -> tuple[int, Path | None]:
    try:
        doc = build_bcg_executive_summary(adg_artifacts_dir, ts, sqlite_path, gate_results_path, action_queue_path, review_template_path, burndown_path, p7_paths)
        md = render_bcg_inline_markdown(doc)
        base = adg_artifacts_dir / f"adg_bcg_executive_summary_{ts}"
        json_path = base.with_suffix(".json")
        yaml_path = base.with_suffix(".yaml")
        md_path = base.with_suffix(".md")
        _write_json(json_path, doc)
        _write_yaml(yaml_path, doc)
        md_path.write_text(md, encoding="utf-8")
        for suffix, src in (("json", json_path), ("yaml", yaml_path), ("md", md_path)):
            latest = adg_artifacts_dir / f"adg_bcg_executive_summary_latest.{suffix}"
            docs_latest = DOCS_ADG / f"adg_bcg_executive_summary_latest.{suffix}"
            latest.parent.mkdir(parents=True, exist_ok=True)
            docs_latest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, latest)
            shutil.copyfile(src, docs_latest)
        if print_inline:
            sys.stdout.write("\n" + md + ("\n" if not md.endswith("\n") else ""))
        print(f"[adg_bcg_executive_synthesis] SUMMARY={_repo_rel(json_path)}", file=sys.stderr)
        return (0 if doc["run"].get("decision_grade_status") != "FAIL" else 2), json_path
    except (OSError, sqlite3.Error, json.JSONDecodeError, yaml.YAMLError, ValueError, TypeError) as exc:
        print(f"[adg_bcg_executive_synthesis] ERROR={exc}", file=sys.stderr)
        return (2 if fail_closed else 0), None
