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
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from tools.reports.adg_bcg_adapter import (
    build_bcg_brief,
    build_deprecation_deletion_plan as _build_deprecation_deletion_plan,
    render_bcg_brief_md,
)
from tools.reports.gate_signal_catalog import display_verdict, display_verdict_sub, recommended_next_step

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"
TEST_FOLDERS = ("unit", "e2e", "regression", "integration", "smoke", "golden", "contract", "fixtures", "unknown")
TEST_TYPE_BY_FOLDER = {"fixtures": "fixture"}
VERDICTS = {"BLOCKED", "GREEN_WITH_DEBT", "REPORT_INCONSISTENT", "DEGRADED", "CLEAN", "NEEDS_RUNTIME_PROOF", "TESTING_CONTROL_GAP", "RUNTIME_PROOF_FAILING"}

# The next-slice fix ordering is intentionally human-readable, not a raw count sort.
# We keep the broad architecture drift row ahead of the narrow control bypass row,
# then the contract-seam debt row, so the executive brief can explain the business
# tradeoff in plain English.
_FIX_PRIORITY_FAMILY_ORDER: dict[str, int] = {
    "LayerSkipGate": 0,
    "L5BypassGate": 1,
    "UntypedSeamGate": 2,
    "LpgDriftRatchetGate": 3,
    "UnusedImportsRatchetGate": 4,
}


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


def _latest_by_glob(root: Path, pattern: str) -> Path | None:
    candidates = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _sqlite_ts(sqlite_path: Path) -> str:
    stem = sqlite_path.stem
    prefix = "adg_indexed_"
    if stem.startswith(prefix):
        return stem[len(prefix) :]
    return stem


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


def _table_columns(sqlite_path: Path, table: str) -> list[str]:
    """Column names for a table OR view (works for materialized views)."""
    if not sqlite_path.is_file():
        return []
    with sqlite3.connect(sqlite_path) as conn:
        try:
            return [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]
        except sqlite3.Error:
            return []


# Structural graph MVs the synthesis must actually STUDY (not just count). Each spec is
# (mv_name, scope columns in priority order, score column, signal key). Querying is fully
# generic — a missing table / missing column / empty MV is tolerated, never raised.
_STRUCTURAL_MV_SPECS: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    ("mv_hotspot_centrality", ("resolved_path", "file_path", "file", "adg_name"), "betweenness_approx", "centrality"),
    ("mv_graph_reverse_dependency_hotspots", ("file_path", "resolved_path", "file"), "reverse_dependency_score", "reverse_dependency"),
    ("mv_graph_critical_path_blast_radius", ("file_path", "resolved_path", "file"), "weighted_blast_radius", "blast_radius"),
    ("mv_dependency_cone_risk", ("resolved_path", "file_path", "file"), "cone_risk_score", "dependency_cone"),
    ("mv_graph_chokepoint_bridges", ("file_path", "resolved_path", "file"), "bridge_score", "chokepoint"),
    ("mv_graph_scc_clusters", ("file_path", "resolved_path", "file"), "scc_risk_score", "scc"),
    ("mv_newly_introduced_critical_paths", ("file", "resolved_path", "file_path", "adg_name"), "criticality_score", "newly_introduced"),
)


def _query_structural_mvs(sqlite_path: Path, top_n: int = 25) -> dict[str, Any]:
    """Query the structural graph MVs (centrality, blast radius, reverse deps,
    dependency cones, chokepoints, SCC, newly-introduced critical paths) and fold the
    real scored rows into a per-scope risk map. Generic + defensive."""
    by_scope: dict[str, dict[str, Any]] = {}
    mv_status: dict[str, dict[str, Any]] = {}
    if not sqlite_path.is_file():
        return {"by_scope": {}, "mv_status": {}, "ranked_scopes": []}
    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        for mv, scope_cols, score_col, signal in _STRUCTURAL_MV_SPECS:
            try:
                cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{mv}")')]
            except sqlite3.Error:
                cols = []
            available = bool(cols)
            scope_col = next((c for c in scope_cols if c in cols), None)
            has_score = score_col in cols
            total = 0
            rows_used = 0
            if available:
                try:
                    total = int(conn.execute(f'SELECT COUNT(*) FROM "{mv}"').fetchone()[0])
                except sqlite3.Error:
                    total = 0
            if available and scope_col and has_score:
                where = ' WHERE "is_new" = 1' if "is_new" in cols else ""
                layer_sel = ', "layer"' if "layer" in cols else ""
                try:
                    cur = conn.execute(
                        f'SELECT "{scope_col}" AS scope, "{score_col}" AS score{layer_sel} '
                        f'FROM "{mv}"{where} ORDER BY "{score_col}" DESC LIMIT ?',
                        (top_n,),
                    )
                    for r in cur:
                        scope = str(r["scope"] or "").strip()
                        if not scope or scope.endswith("/"):
                            continue
                        try:
                            val = float(r["score"]) if r["score"] is not None else 0.0
                        except (TypeError, ValueError):
                            val = 0.0
                        entry = by_scope.setdefault(scope, {"signals": [], "layer": None})
                        entry[signal] = val
                        if signal not in entry["signals"]:
                            entry["signals"].append(signal)
                        if layer_sel and entry.get("layer") is None:
                            entry["layer"] = r["layer"]
                        rows_used += 1
                except sqlite3.Error:
                    pass
            mv_status[mv] = {
                "available": available,
                "queried": bool(available and scope_col and has_score),
                "score_column": score_col if has_score else None,
                "rows_used": rows_used,
                "total_rows": total,
            }
    ranked = sorted(
        by_scope.items(),
        key=lambda kv: (
            -len(kv[1].get("signals", [])),
            -sum(v for k, v in kv[1].items() if isinstance(v, (int, float))),
        ),
    )
    ranked_scopes = [{"scope": s, "signal_count": len(d.get("signals", [])), **d} for s, d in ranked]
    return {"by_scope": by_scope, "mv_status": mv_status, "ranked_scopes": ranked_scopes}


def _artifact_consistency(sqlite_path: Path) -> dict[str, Any]:
    """Real graph-vs-report consistency from mv_graph_vs_report_mismatches — never a
    hardcoded PASS."""
    if not _table_columns(sqlite_path, "mv_graph_vs_report_mismatches"):
        return {"status": "DEGRADED", "errors": [], "note": "graph-vs-report consistency MV not present this run"}
    rows = _table_rows(sqlite_path, "mv_graph_vs_report_mismatches", 50)
    if not rows:
        return {"status": "PASS", "errors": []}
    errors = [
        {
            "mismatch_type": str(r.get("mismatch_type") or "unknown"),
            "ref_id": r.get("ref_id"),
            "file": r.get("file"),
            "detail": str(r.get("detail") or "")[:200],
            "delta": r.get("mismatch_delta"),
        }
        for r in rows
    ]
    return {"status": "FAIL", "errors": errors}


def _empty_current_tests() -> dict[str, list[str]]:
    return {k: [] for k in ("unit", "e2e", "regression", "integration", "smoke", "golden", "contract", "fixture", "mock_only", "unknown")}


def _test_paths_for_scope(prod: str, test_scope_inventory: dict[str, Any]) -> dict[str, list[str]]:
    """Return concrete test files that appear to exercise a production scope."""
    found = _empty_current_tests()
    prod_norm = prod[:-3] if prod.endswith(".py") else prod
    parent_scope = prod_norm.rsplit("/", 1)[0] if "/" in prod_norm else prod_norm
    domain = _domain_for_path(prod)
    for test in test_scope_inventory.get("files", []) or []:
        test_path = str(test.get("path") or "")
        test_type = str(test.get("test_type") or "unknown")
        if test_type not in found:
            test_type = "unknown"
        likely = [str(v) for v in test.get("likely_target_paths", []) or []]
        likely_norm = [v[:-3] if v.endswith(".py") else v for v in likely]
        mapped = False
        for target in likely_norm:
            if not target:
                continue
            if target == prod_norm or prod_norm.startswith(target + "/") or target.startswith(parent_scope + "/") or target == parent_scope:
                mapped = True
                break
        if not mapped and domain != "unknown" and str(test.get("app_or_domain") or "") == domain and parent_scope in " ".join(likely_norm + [test_path]):
            mapped = True
        if mapped and test_path and test_path not in found[test_type]:
            found[test_type].append(test_path)
    return {k: sorted(v) for k, v in found.items()}


def _action_impact(rows: list[dict[str, Any]] | None, default_action: str) -> list[dict[str, Any]]:
    if rows:
        return rows
    return [{"signal": "none", "impact": "No immediate action impact.", "recommended_action": default_action}]


def _p0_recommended_action(issue: dict[str, Any]) -> str:
    issue_type = str(issue.get("issue_type") or "")
    if issue_type == "dynamic_exec":
        return "Stop and remove or isolate dynamic execution before trusting dependency evidence."
    if issue_type == "circular_import":
        return "Break the import cycle so module load order is stable."
    if issue.get("protected_surface"):
        return "Fix this protected-plane boundary first; it sits in routing, execution, orchestration, or safety."
    return "Route the dependency through an approved public surface or move the responsibility to the owning layer."


def _p0_landmine_name(issue: dict[str, Any]) -> str:
    issue_type = str(issue.get("issue_type") or "")
    return {
        "layer_violation": "Wrong-way layer import",
        "circular_import": "Circular import",
        "dynamic_exec": "Dynamic execution",
    }.get(issue_type, issue_type or "P0 issue")


def _p0_landmine_lens(p0_doc: dict[str, Any] | None) -> dict[str, Any]:
    if not p0_doc:
        return {
            "status": "missing",
            "why_it_matters": "P0 landmines are foundation cracks: if this artifact is missing, leaders cannot see whether the graph itself is structurally trustworthy.",
            "executive_read": "P0 wave-plan JSON was not loaded; do not claim there are no foundation cracks.",
            "summary": {
                "total_p0_issues": 0,
                "layer_violations": 0,
                "circular_imports": 0,
                "dynamic_exec": 0,
                "wrong_way_imports": 0,
                "protected_surfaces": 0,
            },
            "landmines": [],
            "action_impact_rows": _action_impact(None, "Load the emitted P0 wave-plan JSON before trusting this lens."),
        }

    rows: list[dict[str, Any]] = []
    for wave in p0_doc.get("waves", []) or []:
        for issue in wave.get("items", []) or []:
            if not isinstance(issue, dict):
                continue
            from_layer = str(issue.get("from_layer") or "")
            to_layer = str(issue.get("to_layer") or "")
            wrong_way = bool(issue.get("issue_type") == "layer_violation" and from_layer and to_layer)
            rows.append(
                {
                    "landmine": _p0_landmine_name(issue),
                    "issue_type": str(issue.get("issue_type") or ""),
                    "source_file": str(issue.get("source_file") or ""),
                    "line_no": int(issue.get("line_no") or 0),
                    "wrong_way_import": wrong_way,
                    "layer_path": f"{from_layer} -> {to_layer}" if from_layer or to_layer else "",
                    "protected_surface": bool(issue.get("protected_surface")),
                    "direct_fan_in": int(issue.get("direct_fan_in") or 0),
                    "recommended_action": _p0_recommended_action(issue),
                    "action_impact": "Fixing this improves trust in ADG ordering before ordinary gate cleanup.",
                }
            )
    rows.sort(key=lambda r: (-int(r["protected_surface"]), -int(r["direct_fan_in"]), r["source_file"], r["line_no"]))
    summary = dict(p0_doc.get("summary") or {})
    summary.setdefault("total_p0_issues", len(rows))
    summary["wrong_way_imports"] = sum(1 for r in rows if r["wrong_way_import"])
    summary["protected_surfaces"] = sum(1 for r in rows if r["protected_surface"])
    summary["max_direct_fan_in"] = max((int(r["direct_fan_in"]) for r in rows), default=0)
    return {
        "status": "present",
        "why_it_matters": "P0 landmines are foundation cracks: they can make the graph incomplete, unstable, or misleading before ordinary gate counts are even interpreted.",
        "executive_read": "Clear dynamic execution, circular imports, protected-surface boundary breaks, and high fan-in wrong-way imports before treating lower-priority cleanup as reliable.",
        "summary": summary,
        "landmines": rows[:25],
        "top_files": p0_doc.get("top_files", []),
        "action_impact_rows": _action_impact(
            [
                {
                    "signal": r["landmine"],
                    "impact": r["action_impact"],
                    "recommended_action": r["recommended_action"],
                }
                for r in rows[:5]
            ],
            "No P0 landmine action required.",
        ),
    }


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
        prod = str(row.get("file") or row.get("path") or row.get("file_path") or row.get("module_path") or row.get("scope") or row.get("production_scope") or "unknown")
        scope = prod[:-3] if prod.endswith(".py") else prod
        parent_scope = scope.rsplit("/", 1)[0]
        current_tests = _test_paths_for_scope(prod, test_scope_inventory)
        mapped = set(scope_map.get(scope, set())) | set(scope_map.get(parent_scope, set())) | {k for k, v in current_tests.items() if v and k != "mock_only"}
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
            "current_tests_found": current_tests,
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
    return {
        "status": "present",
        "why_it_matters": "Tests are the control that prove a risky fix actually works; missing mapped tests turn every red-gate fix into a repeat-risk.",
        "executive_read": _testing_read(rows),
        "summary": summary,
        "test_scope_inventory": {"scanned_tests_root": "tests", "folders": test_scope_inventory.get("folders", [])},
        "investment_map": rows,
        "action_impact_rows": _action_impact(
            [
                {
                    "signal": r["production_scope"],
                    "impact": "Fix confidence improves when this scope has mapped tests.",
                    "recommended_action": r.get("recommended_test_investment", "Add mapped tests."),
                }
                for r in rows[:5]
            ],
            "No test investment promoted.",
        ),
        "testing_rules": ["If a fix touches a P1_URGENT / CRITICAL / ABSENT hotspot, the fix is not complete without mapped tests or an explicit waiver.", "Do not create a generic testing mega-project unless systemic gaps affect multiple high-blast-radius scopes.", "Attach tests to the current fix slice whenever overlap exists."],
    }


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
    fix_gate_ids = [str(g.get("gate_id", "")) for g in gate_rows if display_verdict(g) == "FIX"]
    fix_text = json.dumps([g for g in gate_rows if display_verdict(g) == "FIX"]).lower()
    action_text = json.dumps(action_queue or {}).lower()

    # --- Actually STUDY the structural graph (centrality / blast radius / reverse deps /
    #     cones / chokepoints / SCC / newly-introduced critical paths), not just count MVs.
    structural = _query_structural_mvs(sqlite_path)
    mv_status = structural["mv_status"]
    ranked_scopes = structural["ranked_scopes"]
    hotspot_scopes = {str(r.get("file") or r.get("path") or "").strip() for r in _table_rows(sqlite_path, "mv_hotspot_coverage_risk", 200)}
    hotspot_scopes.discard("")

    def _scope_overlap(scope: str) -> tuple[bool, bool, bool]:
        s = scope.lower()
        overlaps_fix = bool(s and (s in fix_text or any(scope in fid or fid in scope for fid in fix_gate_ids if fid)))
        in_hotspot = scope in hotspot_scopes
        in_action = bool(s and s in action_text)
        return overlaps_fix, in_hotspot, in_action

    structural_overlaps_blocker = any(any(_scope_overlap(r["scope"])[:2]) for r in ranked_scopes[:15])

    rows: list[dict[str, Any]] = []
    for name in tables:
        count = _table_count(sqlite_path, name)
        lname = name.lower()
        st = mv_status.get(name)
        studied = bool(st and st.get("queried") and st.get("rows_used"))
        linked = lname.replace("mv_", "") in fix_text or lname in fix_text or lname in action_text
        testing = "test" in lname or "coverage" in lname or "hotspot" in lname
        if linked:
            role = "used_now"
        elif studied:
            # Structural MV that was actually queried into the scope risk map.
            role = "used_now" if structural_overlaps_blocker else "diagnostic_monitor"
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
        why = _mv_why(role, count)
        if studied:
            why = f"Structural MV studied ({st['rows_used']} ranked rows on `{st['score_column']}`); " + (
                "a high-risk scope overlaps a current FIX gate or coverage hotspot, so it drives work now."
                if role == "used_now" else
                "no studied scope overlaps a blocker/hotspot yet, so it stays diagnostic until it does."
            )
        rows.append({
            "signal": name,
            "signal_type": "materialized_view",
            "row_count": count,
            "decision_role": role,
            "used_inline": role in {"used_now", "used_for_testing"} or studied,
            "why_or_why_not": why,
            "action": _mv_action(role),
            "related_gates": [g.get("gate_id") for g in gate_rows if str(g.get("gate_id", "")).lower() in lname or lname.replace("mv_", "") in str(g).lower()][:5],
            "related_scopes": [],
        })

    # --- Parse P7 artifacts (not blob-scan): real keys → real row counts + evidence-based role.
    for key, doc in p7_artifacts.items():
        if not doc:
            continue
        sig_type = "runtime_spine" if "runtime" in key else ("refactor_report" if "refactor" in key else ("graphdb_report" if "graph" in key else "structural_report"))
        count = _rough_count(doc)
        role = "diagnostic_monitor"
        why = "Parsed P7 structural context; promoted only when it overlaps a blocker, test gap, or planned slice."
        if "runtime" in key and isinstance(doc, dict):
            fails = doc.get("semantic_failures") or doc.get("failures") or []
            if isinstance(fails, list) and fails:
                role, why = "used_now", f"Runtime spine reports {len(fails)} semantic failure(s) — present-and-failing runtime proof, not a measurement gap."
        elif "refactor" in key and isinstance(doc, dict):
            cands = doc.get("candidates") or []
            if isinstance(cands, list) and any(str(c.get("file") or c.get("path") or c).lower() in fix_text for c in cands if isinstance(c, dict) or isinstance(c, str)):
                role, why = "used_now", "Refactor-accelerator candidate overlaps a current FIX gate; use it as the refactor target."
        elif key in {"graph_watchlist", "p0_wave_plan"}:
            role, why = "used_after_green", "Planned-slice / watchlist input for after-green burn-down ordering."
        rows.append({"signal": key, "signal_type": sig_type, "row_count": count, "decision_role": role, "used_inline": role in {"used_now", "used_after_green"}, "why_or_why_not": why, "action": "Use for blast-radius / refactor / runtime-path / after-green planning.", "related_gates": [], "related_scopes": []})

    # --- top_graph_risks carry REAL structural values (no NULL placeholders when data exists).
    top_graph: list[dict[str, Any]] = []
    for i, sc in enumerate(ranked_scopes[:5], 1):
        scope = sc["scope"]
        overlaps_fix, in_hotspot, _ = _scope_overlap(scope)
        reads = []
        if "newly_introduced" in sc.get("signals", []):
            reads.append("newly-introduced critical path (modified-area regression)")
        if overlaps_fix:
            reads.append("overlaps a current FIX gate")
        if in_hotspot:
            reads.append("overlaps an under-tested coverage hotspot")
        top_graph.append({
            "rank": i,
            "scope": scope,
            "layer": sc.get("layer"),
            "graph_signal": ", ".join(sc.get("signals", [])) or "structural",
            "centrality": sc.get("centrality"),
            "blast_radius": sc.get("blast_radius"),
            "reverse_dependency": sc.get("reverse_dependency"),
            "dependency_cone": sc.get("dependency_cone"),
            "chokepoint": sc.get("chokepoint"),
            "scc": sc.get("scc"),
            "executive_read": ("High structural risk — " + "; ".join(reads) + ".") if reads else f"High structural risk across {sc['signal_count']} graph view(s); monitor unless it overlaps a blocker or hotspot.",
            "action": ("Refactor/guard this seam in the current slice." if (overlaps_fix or in_hotspot) else "Monitor; promote when it overlaps a blocker or hotspot."),
            "testing_implication": ("Add mapped tests before refactoring this high-blast scope." if in_hotspot else "Verify mapped tests exist if this seam is touched."),
        })

    summary = _impact_summary(rows)
    summary["structural_mvs_queried"] = sum(1 for s in mv_status.values() if s.get("queried"))
    summary["structural_scopes_ranked"] = len(ranked_scopes)
    return {
        "status": "present",
        "why_it_matters": "Graph signals show where a change can ripple through the codebase; they should change priorities only when tied to a blocker, hotspot, or planned slice.",
        "executive_read": "GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.",
        "summary": summary,
        "decision_impact_rows": rows,
        "top_graph_risks": top_graph[:5],
        "structural_mv_status": mv_status,
        "action_impact_rows": _action_impact(
            [
                {
                    "signal": r["signal"],
                    "impact": r["why_or_why_not"],
                    "recommended_action": r["action"],
                }
                for r in rows
                if r.get("used_inline")
            ][:5],
            "Keep graph signals diagnostic until they overlap a blocker, hotspot, or planned slice.",
        ),
    }


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


def _artifact_stale(path: Path | None, doc: dict[str, Any] | None, run_ts: str) -> bool:
    """An artifact is stale when its embedded snapshot timestamp diverges from the run's.
    Conservative + format-aware: only compares tokens of the SAME shape as ``run_ts`` (the
    snapshot id), so a differently-formatted gate-results timestamp is never a false positive."""
    if not run_ts or not (path and path.is_file()):
        return False
    shape = re.fullmatch(r"(\d+)_(\d+)", run_ts)
    if shape:
        pat = r"(?<!\d)\d{%d}_\d{%d}(?!\d)" % (len(shape.group(1)), len(shape.group(2)))
        tokens = re.findall(pat, path.name)
        if tokens and run_ts not in tokens:
            return True
        embedded = str((doc or {}).get("snapshot") or (doc or {}).get("snapshot_ts") or "") if isinstance(doc, dict) else ""
        etoks = re.findall(pat, embedded)
        if etoks and run_ts not in etoks:
            return True
    return False


def build_artifact_usage_matrix(artifacts: dict[str, Path | None], loaded_docs: dict[str, Any], decision_inputs: dict[str, Any]) -> dict[str, Any]:
    rows = []
    used_keys = set(decision_inputs.get("used_artifact_keys", []))
    run_ts = str(decision_inputs.get("run_ts") or "")
    for key, path in artifacts.items():
        exists = bool(path and path.is_file())
        loaded = bool(exists and key in loaded_docs and loaded_docs.get(key) is not None)
        stale = _artifact_stale(path, loaded_docs.get(key), run_ts)
        used_for = []
        if exists and (key in used_keys or loaded):
            if key in {"gate_results", "action_queue"}:
                used_for.append("decision")
            elif key in {"sqlite_snapshot", "graphdb_queries", "structural_outputs", "refactor_accelerator", "runtime_spine", "graph_watchlist", "p0_wave_plan"}:
                used_for.append("graphdb")
            elif key in {"burndown_table", "burndown_report", "dead_code_report"}:
                used_for.append("audit")
            elif key == "review_template":
                used_for.append("evidence_only")
            elif key == "generation_manifest":
                used_for.append("consistency")
        if not used_for:
            used_for = ["none"]
        recommendation = "keep" if exists and used_for != ["none"] else ("keep_hide_inline" if exists else "refine")
        rationale = "Loaded and mapped to a decision lens." if loaded and used_for != ["none"] else "Available only as diagnostic/evidence context or missing from this run."
        if exists and used_for != ["none"] and not loaded:
            rationale = "Existing non-JSON artifact or SQLite snapshot mapped to a decision lens."
        if stale:
            rationale = "Artifact timestamp diverges from this run; may reflect a different run — verify before trusting. " + rationale
        rows.append({"artifact_key": key, "path": _repo_rel(path), "exists": exists, "loaded": loaded, "stale": stale, "used_for": used_for, "decision_impact": _artifact_impact(key, used_for), "recommendation": recommendation, "rationale": rationale})
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
        actions.append(
            _action(
                "repair_reporting",
                "Repair missing decision-grade ADG artifact",
                "ADG reporting",
                "A required artifact is missing, so the run is degraded.",
                "artifact",
                "Confirm artifacts emit and latest/docs copies exist.",
                "now",
                "high",
                business_reason="Decision-grade reporting is incomplete until the required artifact exists.",
                technical_reason="The run is missing a required artifact, so ADG cannot be treated as fully decision-grade.",
                why_this_rank="This sits ahead of all slice work because report integrity has to be repaired before ranking any fix slice.",
            )
        )
    fix = [g for g in gate_rows if display_verdict(g) == "FIX"]
    for g in sorted(fix, key=lambda r: (_fix_priority_family_rank(r), -_reg_delta(r), -int(r.get("violation_count") or 0), str(r.get("gate_id", ""))))[:3]:
        business_reason, technical_reason, why_this_rank = _fix_priority_copy(g)
        actions.append(
            _action(
                "fix_blocker",
                f"Clear red gate {g.get('gate_id')}",
                str(g.get("gate_id")),
                business_reason,
                "gate",
                "Add mapped tests when touched scope overlaps a hotspot.",
                "now",
                "high",
                business_reason=business_reason,
                technical_reason=technical_reason,
                why_this_rank=why_this_rank,
            )
        )
    tests = testing_investment_map.get("investment_map", [])
    if tests:
        top = tests[0]
        why = "Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down."
        actions.append(
            _action(
                "add_tests",
                f"Fund mapped tests for {top['production_scope']}",
                top["production_scope"],
                why,
                "testing_hotspot",
                top.get("recommended_test_investment", "Add mapped tests."),
                "now" if not fix else "if_touched",
                "medium",
                business_reason=why,
                technical_reason=top.get("recommended_test_investment", "Add mapped tests."),
                why_this_rank="This follows the blocker slice because mapped tests reduce repeat-risk after the failing surface is identified.",
            )
        )
    # Graph-driven refactor action: a studied high-blast-radius seam overlapping a blocker,
    # hotspot, or newly-introduced critical path is a codebase-wide action, not a sorted gate.
    graph_risks = graphdb_decision_impact.get("top_graph_risks", [])
    test_scopes = {str(r.get("production_scope") or "") for r in tests}
    fix_scope_text = (" ".join(str(g.get("gate_id", "")) for g in fix)).lower()
    for gr in graph_risks:
        scope = str(gr.get("scope") or "")
        signal = str(gr.get("graph_signal") or "")
        if scope and (scope in test_scopes or (scope.lower() and scope.lower() in fix_scope_text) or "newly_introduced" in signal):
            why = "Studied structural risk (blast radius / centrality / reverse-deps) on this scope overlaps a blocker, coverage hotspot, or newly-introduced critical path."
            actions.append(
                _action(
                    "refactor",
                    f"Refactor high-blast-radius seam {scope}",
                    scope,
                    why,
                    "graphdb",
                    "Add mapped tests before refactoring this seam.",
                    "if_touched" if fix else "after_green",
                    "medium",
                    business_reason=why,
                    technical_reason=why,
                    why_this_rank="This comes after the fix slice because the refactor is best handled once the blocker and test exposure are explicit.",
                )
            )
            break
    ratchets = [g for g in gate_rows if display_verdict(g) == "TRACK" and display_verdict_sub(g) == "floor"]
    if ratchets:
        g = sorted(ratchets, key=lambda r: (-int(r.get("violation_count") or 0), str(r.get("gate_id", ""))))[0]
        why = "Accepted baseline debt should fall after red gates are clear."
        actions.append(
            _action(
                "burn_down_ratchet",
                f"Burn down ratchet {g.get('gate_id')}",
                str(g.get("gate_id")),
                why,
                "gate",
                "Add tests only when touched scope overlaps hotspot.",
                "after_green",
                "medium",
                business_reason=why,
                technical_reason=f"{_fmt_int(g.get('violation_count'))} floor-row(s) remain on the ratchet gate.",
                why_this_rank="This is deferred until the current red gates clear because it is accepted baseline debt, not the immediate blocker slice.",
            )
        )
    low = [r for r in mv_usefulness_audit.get("rows", []) if r.get("recommendation") in {"refine", "deprecate_candidate"}]
    if low:
        why = "Suppress or retire signals that do not affect decisions."
        actions.append(
            _action(
                "refine",
                f"Refine/deprecate low-value ADG signal {low[0]['mv_name']}",
                low[0]["mv_name"],
                why,
                "mv",
                "No test required unless generator logic changes.",
                "deprecate",
                "low",
                business_reason=why,
                technical_reason=low[0].get("decision_impact", "No current decision effect."),
                why_this_rank="This is last because it is cleanup of decision noise, not a blocker or a high-risk exposure.",
            )
        )
    for i, row in enumerate(actions[:8], 1):
        row["rank"] = i
    return {"status": "present", "rows": actions[:8]}


def _reg_delta(g: dict[str, Any]) -> int:
    for key in ("regression_delta", "delta", "new_records", "new", "worsened"):
        value = g.get(key)
        if value not in (None, ""):
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    try:
        base = g.get("baseline_count")
        if base in (None, ""):
            base = g.get("baseline_records")
        if base in (None, ""):
            return 0
        return max(0, int(g.get("violation_count") or 0) - int(base))
    except (TypeError, ValueError):
        return 0


def _action(
    action_type: str,
    action: str,
    scope: str,
    why: str,
    signal_type: str,
    testing: str,
    timing: str,
    confidence: str,
    *,
    business_reason: str | None = None,
    technical_reason: str | None = None,
    why_this_rank: str | None = None,
) -> dict[str, Any]:
    return {
        "rank": None,
        "action_type": action_type,
        "action": action,
        "scope": scope,
        "why_now": why,
        "business_reason": business_reason or why,
        "technical_reason": technical_reason or testing,
        "why_this_rank": why_this_rank or why,
        "evidence_used": [{"signal_name": scope, "signal_type": signal_type, "decision_effect": why}],
        "testing_requirement": testing,
        "done_condition": "Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived.",
        "confidence": confidence,
        "timing": timing,
    }


def _fix_priority_family_rank(gate: dict[str, Any]) -> int:
    gate_class = str(gate.get("gate_class") or "").strip()
    gate_id = str(gate.get("gate_id") or "").strip()
    if gate_class in _FIX_PRIORITY_FAMILY_ORDER:
        return _FIX_PRIORITY_FAMILY_ORDER[gate_class]
    if gate_id.startswith("B2_"):
        return 0
    if gate_id.startswith("C2_"):
        return 1
    if gate_id.startswith("F1_"):
        return 2
    if gate_id.startswith("L2_"):
        return 3
    if gate_id.startswith("S4_"):
        return 4
    return 50


def _fix_priority_copy(gate: dict[str, Any]) -> tuple[str, str, str]:
    gate_id = str(gate.get("gate_id") or "").strip()
    gate_class = str(gate.get("gate_class") or "").strip()
    band = str(gate.get("band") or "P?")
    count = _fmt_int(gate.get("violation_count"))
    base = gate.get("baseline_count")
    base_text = _fmt_int(base) if base not in (None, "") else "none"
    delta = _reg_delta(gate)

    if gate_class == "LayerSkipGate" or gate_id.startswith("B2_"):
        return (
            "Broad architecture drift: layer skipping increases future change cost across the repo and weakens the authority model.",
            f"{gate_id}: {count} finding(s), +{delta} vs baseline {base_text}, {band}; imports are skipping more than one layer ordinal.",
            "Ranks first because a cross-cutting layer-hop pattern will keep generating rework in every later slice.",
        )
    if gate_class == "L5BypassGate" or gate_id.startswith("C2_"):
        return (
            "Zero-tolerance governance breach: a small number of L5 bypasses can invalidate control assurances even when the footprint is small.",
            f"{gate_id}: {count} finding(s), {band}; provider/tool calls are skipping the L5 gateway.",
            "Ranks second because the control breach is severe, but the affected surface is narrower than the broader layer-skip regression above.",
        )
    if gate_class == "UntypedSeamGate" or gate_id.startswith("F1_"):
        return (
            "Contract-seam debt: wide untyped seams slow safe change and increase integration risk across many callers.",
            f"{gate_id}: {count} finding(s), +{delta} vs baseline {base_text}, {band}; cross-layer imports land on empty type surfaces.",
            "Ranks third because it is broad technical debt, but not as cross-cutting as the layer-hop problem or as severe as the P0 control bypass.",
        )
    if gate_class == "LpgDriftRatchetGate" or gate_id.startswith("L2_"):
        return (
            "Boundary drift: even a small P0 ratchet at the L_PG boundary weakens the separation model and can spread if left alone.",
            f"{gate_id}: {count} finding(s), +{delta} vs baseline {base_text}, {band}; illegal or drifted imports touch the L_PG boundary.",
            "Ranks below the first three because the current slice is small and the regression surface is more localized.",
        )
    if gate_class == "UnusedImportsRatchetGate" or gate_id.startswith("S4_"):
        return (
            "Hygiene debt: unused imports are real cleanup, but they move the business needle less than boundary or control-plane failures.",
            f"{gate_id}: {count} finding(s), +{delta} vs baseline {base_text}, {band}; unused import edges remain in production modules.",
            "Ranks later because the work is valuable but mostly reduces clutter rather than decision-grade risk.",
        )
    return (
        "Current FIX gate blocks decision-grade green and should be fixed before the next slice proceeds.",
        f"{gate_id}: {count} finding(s), +{delta} vs baseline {base_text}, {band}.",
        "Ranks here because it is a current blocker in the next-slice plan.",
    )


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
    return {
        "status": "present",
        "why_it_matters": "Health gates tell leaders whether the run is green, blocked, or carrying accepted debt; they should not hide report inconsistency or runtime failures.",
        "summary": {"total_gates": len(gates), "clear_gates": buckets.get("CLEAR", 0), "track_gates": buckets.get("TRACK", 0), "fix_gates": buckets.get("FIX", 0), "overall_verdict": "BLOCKED" if buckets.get("FIX") else "PASS", "executive_read": "FIX blocks green; TRACK is accepted backlog/ratchet work; CLEAR needs no action."},
        "buckets": [{"bucket": k, "count": buckets.get(k, 0), "plain_meaning": {"CLEAR": "No action now.", "TRACK": "Known debt or advisory inventory; burn down after red gates.", "FIX": "Current blocker or regression requiring action before decision-grade green."}[k]} for k in ("CLEAR", "TRACK", "FIX")],
        "red_gates": red,
        "managed_debt": {"ratchet_floor_records": sum(int(g.get("violation_count") or 0) for g in ratchets), "open_non_ratchet_records": sum(int(g.get("violation_count") or 0) for g in open_non), "top_ratchets": [{"gate_id": str(g.get("gate_id", "")), "records": int(g.get("violation_count") or 0), "executive_read": "Accepted baseline debt, not current red.", "after_green_action": "Burn down after FIX rows clear."} for g in sorted(ratchets, key=lambda x: -int(x.get("violation_count") or 0))[:5]]},
        "key_interpretation": "A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.",
        "action_impact_rows": _action_impact(
            [
                {
                    "signal": r["gate_id"],
                    "impact": r["executive_read"],
                    "recommended_action": r["next_action"],
                }
                for r in red[:5]
            ],
            "No red-gate action required.",
        ),
    }


def _runtime_lens(p7: dict[str, Any], sqlite_path: Path) -> dict[str, Any]:
    signals = []
    quality_failure = False
    for key in ("runtime_spine", "graphdb_queries", "structural_outputs"):
        doc = p7.get(key)
        fails = 0
        if doc and key == "runtime_spine" and isinstance(doc, dict):
            f = doc.get("semantic_failures") or doc.get("failures") or []
            fails = len(f) if isinstance(f, list) else 0
            if fails:
                quality_failure = True
        if fails:
            status, read = "present_failing", f"Runtime proof present and FAILING: {fails} semantic failure(s) — a quality failure, not a measurement gap."
            action = "Fix the failing runtime path before relying on the trace."
        elif doc:
            status, read = "present", "Runtime/structural proof present and clean for interpretation."
            action = "Use to confirm runtime path risk."
        else:
            status, read = "missing", "Measurement blind spot; not automatically a product failure."
            action = "Enable or repair artifact emission if the decision needs runtime proof."
        signals.append({"signal": key, "status": status, "evidence_count": (fails or (_rough_count(doc) if doc else 0)), "executive_read": read, "action": action})
    # Replay / eval coverage gaps from MVs (present-but-empty = measurement gap).
    for mv, label in (("mv_eval_coverage_by_path", "replay/eval coverage"),):
        if _table_columns(sqlite_path, mv):
            cnt = _table_count(sqlite_path, mv)
            signals.append({"signal": mv, "status": "present" if cnt else "missing", "evidence_count": cnt, "executive_read": (f"{label} MV present with {cnt} rows; gaps here are replay/eval blind spots, not proven failures." if cnt else f"{label} MV empty — replay/eval measurement gap."), "action": ("Close replay/eval gaps for critical paths." if cnt else "Wire replay/eval evidence before trusting replay coverage.")})
    present = any(s["status"].startswith("present") for s in signals)
    mg = "Runtime proof is present and FAILING — treat as a quality failure to fix." if quality_failure else "Missing or empty runtime proof is a measurement gap (blind spot), not automatically a product failure, unless an artifact shows runtime failure evidence."
    return {
        "status": "present_failing" if quality_failure else ("present" if present else "missing"),
        "why_it_matters": "Runtime proof separates a real observed failure from a blind spot; leaders should not treat missing traces as proof of health.",
        "executive_read": "Runtime proof distinguishes observed quality failures from missing instrumentation.",
        "measurement_gap_vs_quality_failure": mg,
        "runtime_proof_signals": signals,
        "action_impact_rows": _action_impact(
            [
                {
                    "signal": s["signal"],
                    "impact": s["executive_read"],
                    "recommended_action": s["action"],
                }
                for s in signals
            ],
            "No runtime action promoted.",
        ),
        "blind_spots": [] if present else [{"blind_spot": "runtime proof artifacts", "why_it_matters": "Without runtime proof, ADG can flag structural risk but cannot prove production behavior.", "recommended_action": "Generate or wire runtime spine/replay/OTel evidence for critical paths."}],
    }


def _product_lens(testing: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    risks = []
    for row in testing.get("investment_map", []):
        if str(row.get("app_or_domain", "")).startswith("apps_"):
            risks.append({"app_or_scope": row["app_or_domain"], "risk": "Under-tested product hotspot", "evidence": [{"signal_name": row["production_scope"], "signal_type": "hotspot", "raw_count": row.get("risk", {}).get("violation_count"), "interpreted_meaning": row.get("reasoned_implication", "")}], "executive_read": "App risk is promoted because product surface and missing test scope overlap.", "next_action": row.get("recommended_test_investment", "Add mapped tests."), "priority_vs_gate_debt": "Can outrank after-green ratchet burn-down when it overlaps current work or high blast radius."})
    return {
        "status": "present",
        "why_it_matters": "Product risk shows whether a structural issue touches user-facing app behavior, not just internal cleanup.",
        "executive_read": "No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row." if not risks else "App/product risks were promoted only where hotspot or test evidence changes funding posture.",
        "app_risks": risks[:8],
        "promoted_product_gaps": [{"gap_id": f"product_gap_{i}", "title": r["risk"], "app_or_scope": r["app_or_scope"], "why_high_leverage": r["executive_read"], "action": r["next_action"], "done_condition": "Mapped app tests pass and ADG no longer reports the promoted gap."} for i, r in enumerate(risks[:5], 1)],
        "action_impact_rows": _action_impact(
            [
                {
                    "signal": r["app_or_scope"],
                    "impact": r["executive_read"],
                    "recommended_action": r["next_action"],
                }
                for r in risks[:5]
            ],
            "No product-scope action promoted.",
        ),
    }


def _verdict(health: dict[str, Any], runtime: dict[str, Any], testing: dict[str, Any], artifacts: dict[str, Any], consistency: dict[str, Any] | None = None) -> dict[str, Any]:
    consistency = consistency or {}
    missing_required = [r for r in artifacts.get("rows", []) if not r.get("exists") and r.get("artifact_key") in {"gate_results", "sqlite_snapshot"}]
    if missing_required:
        verdict = "DEGRADED"
        crisis = "measurement_gap"
        posture = "repair_reporting"
    elif consistency.get("status") == "FAIL":
        verdict = "REPORT_INCONSISTENT"
        crisis = "material_risk"
        posture = "repair_reporting"
    elif runtime.get("status") == "present_failing":
        verdict = "RUNTIME_PROOF_FAILING"
        crisis = "material_risk"
        posture = "repair_runtime"
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
    recommendation = "Fund the smallest slice that clears current blockers and attaches tests where hotspot evidence overlaps; keep ratchets after-green."
    if verdict == "REPORT_INCONSISTENT":
        recommendation = "Repair report consistency first; the executive order of work is not trustworthy until graph and report agree."
    elif verdict == "RUNTIME_PROOF_FAILING":
        recommendation = "Fix the failing runtime-proof path before treating ordinary gate cleanup as the highest-confidence next action."
    elif verdict == "DEGRADED":
        recommendation = "Repair missing decision-grade artifacts before relying on this summary."
    return {"verdict": verdict, "recommendation": recommendation, "funding_posture": posture, "why_now": "Decision combines artifact consistency, runtime proof, FIX status, regression/newness, GraphDB/MV linkage, and testing exposure.", "risk_if_ignored": "The organization may chase raw counts while missing a broken report, failing runtime proof, smaller blocker, or under-tested high-blast-radius surface.", "what_not_to_do": ["Do not rank work by raw MV row count alone.", "Do not let ordinary FIX gates hide report inconsistency or runtime failure.", "Do not start a generic testing mega-project when mapped tests can follow the current slice."], "crisis_level": crisis, "one_sentence_bottom_line": f"ADG is {verdict}: act on decision-linked blockers/testing gaps, defer diagnostic-only noise."}


def _base_doc(ts: str, sqlite_path: Path, gate_doc: dict[str, Any] | None, degraded: list[str]) -> dict[str, Any]:
    return {"schema_version": "1.0", "artifact_kind": "adg_bcg_executive_summary", "run": {"run_id": ts, "generated_at_utc": _now(), "snapshot_ts": (gate_doc or {}).get("timestamp") or ts, "commit_sha": _git_sha(), "repo_state_hash": "", "decision_grade_status": "DEGRADED" if degraded else "PASS", "degradation_reasons": degraded}, "plain_english_context": {"what_adg_is": {"summary": "ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.", "analogy": "ADG is the codebase X-ray: it sees dependency skeletons, health gates, and structural risk.", "measured_scope": {"connections": None, "gates": (gate_doc or {}).get("total_gates"), "files": None}, "caveats": []}}}


def build_bcg_executive_summary(adg_artifacts_dir: Path, ts: str, sqlite_path: Path, gate_results_path: Path | None, action_queue_path: Path | None, review_template_path: Path | None, burndown_path: Path | None, p7_paths: dict[str, Path | None]) -> dict[str, Any]:
    artifacts = {"gate_results": gate_results_path, "action_queue": action_queue_path, "review_template": review_template_path, "burndown_table": burndown_path, "burndown_report": adg_artifacts_dir / "adg_burndown_report.md", "sqlite_snapshot": sqlite_path, "generation_manifest": adg_artifacts_dir / f"adg_generation_manifest_{ts}.json", **p7_paths}
    loaded = {
        k: doc
        for k, v in artifacts.items()
        if v and v.suffix == ".json" and (doc := _read_json(v)) is not None
    }
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
    _snap_tokens = re.findall(r"(?<!\d)\d+_\d+(?!\d)", sqlite_path.name)
    run_ts = _snap_tokens[0] if _snap_tokens else str(ts)
    used_artifact_keys = list(loaded.keys())
    if sqlite_path.is_file():
        used_artifact_keys.append("sqlite_snapshot")
    artifact_matrix = build_artifact_usage_matrix(artifacts, loaded, {"used_artifact_keys": used_artifact_keys, "run_ts": run_ts})
    mv_audit = build_mv_usefulness_audit(sqlite_path, graph, gates)
    dead_code_report = loaded.get("dead_code_report") or {}
    deprecation_plan = build_deprecation_deletion_plan(dead_code_report, mv_audit, artifact_matrix)
    consistency = _artifact_consistency(sqlite_path)
    health = _health_lens(gates)
    runtime = _runtime_lens(p7_docs, sqlite_path)
    p0_landmines = _p0_landmine_lens(p7_docs.get("p0_wave_plan"))
    product = _product_lens(testing, graph)
    actions = build_canonical_next_best_actions(gates, graph, testing, artifact_matrix, mv_audit, action_queue)
    doc.update({"executive_decision": _verdict(health, runtime, testing, artifact_matrix, consistency), "prioritization_model": _prioritization_model(), "lens_0_p0_landmines": p0_landmines, "lens_1_health_gates": health, "lens_2_runtime_proof_observability": runtime, "lens_3_product_app_risk": product, "lens_4_testing_control_gaps": testing, "lens_5_graphdb_mv_decision_impact": graph, "canonical_next_best_actions": actions, "after_green_plan": _after_green(health, graph, testing), "artifact_usage_matrix": artifact_matrix, "mv_usefulness_audit": mv_audit, "dead_code_report": dead_code_report, "deprecation_deletion_plan": deprecation_plan, "defer_delete_deprecate": {"status": "present", "rows": deprecation_plan.get("cleanup_candidates", [])}, "audit_notes": _audit_notes(gates, loaded.get("burndown_table"), consistency), "honest_bottom_line": _bottom_line(health, runtime, testing, actions), "raw_inputs": _raw_inputs(artifacts, loaded), "evidence_trace": _evidence_trace(graph, artifact_matrix, degraded)})
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


def build_deprecation_deletion_plan(
    dead_code_report: dict[str, Any] | None,
    mv_usefulness_audit: dict[str, Any] | None,
    artifact_usage_matrix: dict[str, Any] | None,
) -> dict[str, Any]:
    return _build_deprecation_deletion_plan(dead_code_report, mv_usefulness_audit, artifact_usage_matrix)


def _audit_notes(gates: list[dict[str, Any]], burndown: dict[str, Any] | None, consistency: dict[str, Any] | None = None) -> dict[str, Any]:
    summary = (burndown or {}).get("summary") or {}
    consistency = consistency or {"status": "PASS", "errors": []}
    return {"status": "present", "guardian_summary": [{"band": band, "gross": (summary.get(band) or {}).get("gross"), "guardian": (summary.get(band) or {}).get("guardian"), "non_exempt": (summary.get(band) or {}).get("net"), "executive_read": "Guardian exception math is audit context; map to a failing gate before funding fixes."} for band in ("P0", "P1", "P2", "P3")], "severity_summary": {"executive_read": "Severity inventory is audit math unless tied to current FIX/action rows.", "rows": []}, "artifact_consistency": consistency, "notes": ["Guardian exceptions are audit math only; they do not automatically explain away real problems.", "Diagnostic-only MVs are not immediate work unless tied to a blocker, testing gap, critical path, or planned slice.", "Artifact consistency is derived from mv_graph_vs_report_mismatches (graph-vs-report truth), not assumed PASS."]}


def _bottom_line(health: dict[str, Any], runtime: dict[str, Any], testing: dict[str, Any], actions: dict[str, Any]) -> dict[str, list[str]]:
    return {"bullets": ["Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.", f"Actually blocking now: {health['summary'].get('fix_gates')} FIX gates; inspect regression delta before declaring a platform crisis.", "Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.", "Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.", (actions.get("rows") or [{"action": "Keep ADG green and monitor diagnostic signals."}])[0]["action"], "Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role."]}


def _raw_inputs(artifacts: dict[str, Path | None], loaded: dict[str, Any]) -> dict[str, Any]:
    return {"artifacts": {k: _repo_rel(v) for k, v in artifacts.items()}, "loaded_status": {"missing": [k for k, v in artifacts.items() if not (v and v.is_file())], "stale": [], "degraded": [], "used": list(loaded.keys())}}


def _evidence_trace(graph: dict[str, Any], artifacts: dict[str, Any], degraded: list[str]) -> dict[str, Any]:
    used = [{"signal_name": r["signal"], "signal_type": r["signal_type"], "used_for": r["decision_role"], "decision_effect": r["why_or_why_not"]} for r in graph.get("decision_impact_rows", []) if r.get("used_inline")]
    suppressed = [{"signal_name": r["signal"], "signal_type": r["signal_type"], "suppression_reason": r["why_or_why_not"], "revisit_condition": r["action"]} for r in graph.get("decision_impact_rows", []) if not r.get("used_inline")]
    missing = [{"signal_name": d.split(":", 1)[0], "why_needed": d, "decision_limitation": "Run is not fully decision-grade."} for d in degraded]
    for r in artifacts.get("rows", []):
        if not r.get("exists"):
            missing.append({"signal_name": r["artifact_key"], "why_needed": "Artifact not present this run.", "decision_limitation": _artifact_impact(r["artifact_key"], r.get("used_for", []))})
    stale = [{"signal_name": r["artifact_key"], "detected_timestamp": "", "expected_timestamp": "", "impact": r.get("rationale", "Artifact may reflect a different run; verify before trusting.")} for r in artifacts.get("rows", []) if r.get("stale")]
    return {"used_signals": used, "suppressed_signals": suppressed, "missing_signals": missing, "stale_signals": stale}


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---:" if h.lower() in {"count", "rank", "total records", "regression / new delta"} or h.startswith("Rank") else "---" for h in headers]) + "|"]
    for row in rows:
        out.append("| " + " | ".join(_md(c) for c in row) + " |")
    return "\n".join(out)


def _action_impact_markdown(lens: dict[str, Any]) -> str:
    rows = lens.get("action_impact_rows") or []
    return _table(
        ["Signal", "Action impact", "Recommended action"],
        [[r.get("signal", ""), r.get("impact", ""), r.get("recommended_action", "")] for r in rows],
    )


def _format_current_tests(current_tests: dict[str, Any]) -> str:
    paths = []
    for kind, values in (current_tests or {}).items():
        for value in values or []:
            paths.append(f"{kind}: {value}")
    return "; ".join(paths[:6]) or "none mapped"


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value or 0):,}"
    except (TypeError, ValueError):
        return "0"


def _executive_bcg_brief(doc: dict[str, Any]) -> dict[str, Any]:
    d = doc.get("executive_decision", {})
    health = doc.get("lens_1_health_gates", {})
    runtime = doc.get("lens_2_runtime_proof_observability", {})
    testing = doc.get("lens_4_testing_control_gaps", {})
    graph = doc.get("lens_5_graphdb_mv_decision_impact", {})
    actions = (doc.get("canonical_next_best_actions") or {}).get("rows") or []
    raw_inputs = doc.get("raw_inputs") or {}
    artifacts = raw_inputs.get("artifacts") or {}
    sqlite_snapshot = str(artifacts.get("sqlite_snapshot") or "").strip()
    snapshot_ts = _sqlite_ts(Path(sqlite_snapshot)) if sqlite_snapshot else ""
    priority_rows: list[dict[str, Any]] = []
    for row in actions[:4]:
        evidence = "; ".join(
            str(e.get("signal_type") or "").strip()
            for e in row.get("evidence_used", [])
            if isinstance(e, dict) and str(e.get("signal_type") or "").strip()
        )
        priority_rows.append(
            {
                "priority": row.get("rank"),
                "move": row.get("action"),
                "scope": row.get("scope"),
                "business_reason": row.get("business_reason") or row.get("why_now"),
                "technical_reason": row.get("technical_reason") or row.get("testing_requirement") or evidence or row.get("action"),
                "why_this_rank": row.get("why_this_rank") or row.get("why_now"),
                "decision": row.get("action_type"),
            }
        )
    return build_bcg_brief(
        title="BCG Executive Brief",
        status=str(doc.get("run", {}).get("decision_grade_status") or ""),
        business_read=(
            f"ADG is {d.get('verdict', 'UNKNOWN')}: {d.get('recommendation', 'no recommendation emitted')}. "
            "Spend executive time on blockers and test gaps before accepted debt."
        ),
        technical_read=[
            (
                f"ADG source: {sqlite_snapshot} (snapshot {snapshot_ts})"
                if sqlite_snapshot
                else f"ADG source: missing (snapshot {doc.get('run', {}).get('snapshot_ts') or doc.get('run', {}).get('run_id') or 'missing'})"
            ),
            f"FIX gates: {_fmt_int(health.get('summary', {}).get('fix_gates', 0))}; "
            f"TRACK gates: {_fmt_int(health.get('summary', {}).get('track_gates', 0))}",
            runtime.get("measurement_gap_vs_quality_failure") or runtime.get("executive_read", ""),
            testing.get("executive_read") or testing.get("why_it_matters", ""),
            graph.get("executive_read", ""),
            f"Action rows emitted: {_fmt_int(len(actions))}",
        ],
        priority_rule="Fix blockers first, then close testing exposure, then reduce accepted debt.",
        priority_rows=priority_rows,
        why_this_order=(doc.get("honest_bottom_line") or {}).get("bullets", [])[:4],
        next_step=(
            (actions[0].get("action") if actions else "Follow the next-best-actions table below.")
            if actions
            else "Follow the next-best-actions table below."
        ),
        table_limit=4,
    )


def render_bcg_inline_markdown(doc: dict[str, Any]) -> str:
    """Render the locked executive inline markdown structure exactly."""
    h = doc["lens_1_health_gates"]
    lines: list[str] = []
    a = lines.append
    a("## ADG Executive Brief")
    a("")
    for line in render_bcg_brief_md(_executive_bcg_brief(doc)).splitlines():
        a(line)
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
    p0 = doc.get("lens_0_p0_landmines", {})
    a("### 4. Lens 0 — P0 Landmines / Foundation Cracks")
    a("")
    a(p0.get("why_it_matters", "P0 landmine context was unavailable."))
    a("")
    p0_summary = p0.get("summary", {})
    a(_table(["P0 signal", "Count", "Plain-English meaning"], [
        ["Layer violations", p0_summary.get("layer_violations", 0), "Wrong-way dependencies across protected architecture layers."],
        ["Circular imports", p0_summary.get("circular_imports", 0), "Modules depend on each other in a loop, making load order brittle."],
        ["Dynamic execution", p0_summary.get("dynamic_exec", 0), "Code is executed dynamically, which can make graph evidence incomplete."],
        ["Protected surfaces", p0_summary.get("protected_surfaces", 0), "Cracks in routing, execution, orchestration, or safety surfaces."],
    ]))
    a("")
    landmines = p0.get("landmines") or [{"landmine": "None", "source_file": "", "line_no": 0, "layer_path": "", "wrong_way_import": False, "protected_surface": False, "direct_fan_in": 0, "recommended_action": "No P0 landmine action required."}]
    a(_table(["Landmine", "File", "Line", "Layer path", "Wrong-way?", "Protected?", "Fan-in", "Recommended action"], [[r.get("landmine"), r.get("source_file"), r.get("line_no"), r.get("layer_path"), r.get("wrong_way_import"), r.get("protected_surface"), r.get("direct_fan_in"), r.get("recommended_action")] for r in landmines[:8]]))
    a("")
    a("Action impact:")
    a("")
    a(_action_impact_markdown(p0))
    a("")
    a("### 5. Gap Analysis — Lens 1: Health Gates")
    a("")
    a(h.get("why_it_matters", "Health gates show whether the run is blocked or green."))
    a("")
    a(h["summary"]["executive_read"] + " " + h.get("key_interpretation", ""))
    a("")
    a(_table(["Bucket", "Count", "Executive meaning"], [[b["bucket"], b["count"], b["plain_meaning"]] for b in h.get("buckets", [])]))
    a("")
    red_rows = h.get("red_gates") or [{"gate_id": "None", "total_records": 0, "regression_delta": 0, "executive_read": "No red gates.", "next_action": "No blocker action."}]
    a(_table(["Red gate", "Total records", "Regression / new delta", "Executive read", "Next action"], [[r["gate_id"], r["total_records"], r.get("regression_delta"), r["executive_read"], r["next_action"]] for r in red_rows[:8]]))
    a("")
    a("Action impact:")
    a("")
    a(_action_impact_markdown(h))
    a("")
    a("### 6. Gap Analysis — Lens 2: Runtime Proof / Observability")
    a("")
    rt = doc["lens_2_runtime_proof_observability"]
    a(rt.get("why_it_matters", "Runtime proof distinguishes observed failures from blind spots."))
    a("")
    a(rt["measurement_gap_vs_quality_failure"])
    a("")
    a(_table(["Runtime proof signal", "Status", "Executive read", "Action"], [[r["signal"], r["status"], r["executive_read"], r["action"]] for r in rt.get("runtime_proof_signals", [])]))
    a("")
    a("Action impact:")
    a("")
    a(_action_impact_markdown(rt))
    a("")
    a("### 7. Gap Analysis — Lens 3: Product / App Risk")
    a("")
    pr = doc["lens_3_product_app_risk"]
    a(pr.get("why_it_matters", "Product risk ties structural findings to user-facing behavior."))
    a("")
    a(pr["executive_read"])
    a("")
    app_rows = pr.get("app_risks") or [{"app_or_scope": "None", "risk": "No app-specific product gap was promoted in this run", "evidence": [], "executive_read": "App risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row.", "next_action": "Monitor."}]
    a(_table(["App / product scope", "Risk", "Evidence", "Executive read", "Next action"], [[r["app_or_scope"], r["risk"], "; ".join(e.get("signal_name", "") for e in r.get("evidence", [])), r["executive_read"], r["next_action"]] for r in app_rows[:8]]))
    a("")
    a("Action impact:")
    a("")
    a(_action_impact_markdown(pr))
    a("")
    a("### 8. Gap Analysis — Lens 4: Testing Control Gaps")
    a("")
    tg = doc["lens_4_testing_control_gaps"]
    a(tg.get("why_it_matters", "Testing gaps reduce confidence in fixes."))
    a("")
    a(tg["executive_read"])
    a("")
    test_rows = tg.get("investment_map") or [{"rank": 0, "production_scope": "None", "current_tests_found": {}, "missing_test_scope": ["No mapped hotspot rows"], "risk": {}, "recommended_test_investment": "No test investment promoted.", "trigger": "No hotspot evidence"}]
    a(_table(["Rank", "Production scope", "Current tests found", "Missing test scope", "Risk", "Recommended investment", "Trigger"], [[r["rank"], r["production_scope"], _format_current_tests(r.get("current_tests_found", {})), ", ".join(r.get("missing_test_scope", [])), r.get("risk", {}).get("risk_band", "unknown"), r.get("recommended_test_investment"), r.get("trigger")] for r in test_rows[:10]]))
    a("")
    a("Action impact:")
    a("")
    a(_action_impact_markdown(tg))
    a("")
    a("### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact")
    a("")
    gr = doc["lens_5_graphdb_mv_decision_impact"]
    a(gr.get("why_it_matters", "Graph signals show blast radius and dependency risk."))
    a("")
    a(gr["executive_read"])
    a("")
    impact = sorted(gr.get("decision_impact_rows", []), key=lambda r: (not r.get("used_inline"), r.get("decision_role", "")))[:12]
    a(_table(["Signal", "Decision role", "Used now?", "Why / why not", "Action"], [[r["signal"], r["decision_role"], r["used_inline"], r["why_or_why_not"], r["action"]] for r in impact]))
    a("")
    a("Action impact:")
    a("")
    a(_action_impact_markdown(gr))
    a("")
    graph_risks = gr.get("top_graph_risks", [])
    if graph_risks:
        a("Top structural risks (studied from the graph MVs — centrality / blast radius / reverse deps / cones):")
        a("")
        a(_table(["Rank", "Scope", "Graph signal", "Centrality", "Blast radius", "Reverse dep", "Executive read"], [[r.get("rank"), r.get("scope"), r.get("graph_signal"), r.get("centrality"), r.get("blast_radius"), r.get("reverse_dependency"), r.get("executive_read")] for r in graph_risks]))
        a("")
    a("### 10. Next Best Actions")
    a("")
    a(_table(["Rank", "Action", "Scope", "Why now", "Evidence used", "Testing requirement", "Done condition"], [[r["rank"], r["action"], r["scope"], r["why_now"], "; ".join(e["signal_type"] for e in r.get("evidence_used", [])), r["testing_requirement"], r["done_condition"]] for r in doc["canonical_next_best_actions"].get("rows", [])]))
    a("")
    a("### 11. Defer / Delete / Deprecate")
    a("")
    plan = doc.get("deprecation_deletion_plan", {})
    brief = plan.get("brief") or build_bcg_brief(
        title="BCG Deletion Brief",
        status=str(doc.get("run", {}).get("decision_grade_status") or ""),
        business_read=(
            plan.get("summary", {}).get("executive_read")
            or "No deprecation/deletion plan was available for this run."
        ),
        technical_read=[
            f"Dead code candidates: {_fmt_int((plan.get('summary') or {}).get('dead_code_candidates', 0))}",
            f"Dead imports: {_fmt_int((plan.get('summary') or {}).get('dead_imports', 0))}",
            f"Unresolved imports: {_fmt_int((plan.get('summary') or {}).get('unresolved_imports', 0))}",
            (
                "First-party low-confidence ratio: "
                f"{float((plan.get('summary') or {}).get('first_party_low_confidence_ratio', 0) or 0):.2f}%"
            ),
            (
                "Inferred-symbol ratio: "
                f"{float((plan.get('summary') or {}).get('inferred_symbol_ratio', 0) or 0):.2f}%"
            ),
        ],
        priority_rule=(
            "Confirmed dead code first, then unresolved imports, then low-confidence noise, "
            "then low-value diagnostics."
        ),
        priority_rows=plan.get("priority_rows") or [],
        why_this_order=(plan.get("summary") or {}).get("why_this_order") or [],
        next_step="Deprecate first, then delete after the evidence stays clean.",
        table_limit=6,
    )
    for line in render_bcg_brief_md(brief).splitlines():
        a(line)
    cleanup = plan.get("cleanup_candidates") or doc["defer_delete_deprecate"].get("rows", [])
    if cleanup:
        a("")
        a("Current low-value cleanup candidates:")
        a("")
        a(_table(["Item", "Type", "Current value", "Recommendation", "Rationale"], [[r["item"], r["item_type"], r["current_value"], r["recommendation"], r["rationale"]] for r in cleanup[:12]]))
    a("")
    a("### 12. Honest Bottom Line")
    a("")
    for bullet in doc["honest_bottom_line"].get("bullets", [])[:6]:
        a(f"- {bullet}")
    a("")
    return "\n".join(lines)


def emit_bcg_executive_summary(adg_artifacts_dir: Path, ts: str, sqlite_path: Path, gate_results_path: Path | None, action_queue_path: Path | None, review_template_path: Path | None, burndown_path: Path | None, p7_paths: dict[str, Path | None], print_inline: bool = True, fail_closed: bool = False, docs_dir: Path | None = None) -> tuple[int, Path | None]:
    docs_target = docs_dir if docs_dir is not None else DOCS_ADG
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
            docs_latest = docs_target / f"adg_bcg_executive_summary_latest.{suffix}"
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


def emit_bcg_executive_summary_from_latest(
    *,
    print_inline: bool = True,
    fail_closed: bool = False,
    docs_dir: Path | None = None,
    adg_artifacts_dir: Path = ARTIFACTS_ADG,
) -> tuple[int, Path | None]:
    sqlite_path = _latest_by_glob(adg_artifacts_dir, "adg_indexed_*.sqlite")
    if sqlite_path is None:
        return (2 if fail_closed else 0), None

    ts = _sqlite_ts(sqlite_path)
    gate_results_path = _latest_by_glob(adg_artifacts_dir, "adg_gate_results_*.json")
    action_queue_path = _latest_by_glob(adg_artifacts_dir, f"adg_action_queue_{ts}.json") or _latest_by_glob(
        adg_artifacts_dir, "adg_action_queue_*.json"
    )
    review_template_path = _latest_by_glob(adg_artifacts_dir, f"adg_review_template_{ts}.json") or _latest_by_glob(
        adg_artifacts_dir, "adg_review_template_*.json"
    )
    p0_wave_plan = _latest_by_glob(adg_artifacts_dir / "issues", "p0_remediation_wave_plan_*.json")
    p7_paths = {
        "structural_outputs": _latest_by_glob(adg_artifacts_dir, "adg_structural_outputs_*.json"),
        "refactor_accelerator": _latest_by_glob(adg_artifacts_dir, "adg_refactor_accelerator_*.json"),
        "graphdb_queries": _latest_by_glob(adg_artifacts_dir, "adg_graphdb_queries_*.json"),
        "runtime_spine": _latest_by_glob(adg_artifacts_dir, "adg_runtime_spine_*.json"),
        "graphdb_projection": _latest_by_glob(adg_artifacts_dir, "adg_graphdb_projection_*.json"),
        "graphdb_metadata": _latest_by_glob(adg_artifacts_dir, "adg_graphdb_metadata_*.json"),
        "graphdb_index": _latest_by_glob(adg_artifacts_dir, "adg_graphdb_index_*.json"),
        "graph_watchlist": _latest_by_glob(adg_artifacts_dir, "adg_graph_watchlist_*.json"),
        "p0_wave_plan": p0_wave_plan,
        "dead_code_report": _latest_by_glob(adg_artifacts_dir, "dead_code_zone_control_report_*.json"),
    }
    return emit_bcg_executive_summary(
        adg_artifacts_dir=adg_artifacts_dir,
        ts=ts,
        sqlite_path=sqlite_path,
        gate_results_path=gate_results_path,
        action_queue_path=action_queue_path,
        review_template_path=review_template_path,
        burndown_path=adg_artifacts_dir / "adg_burndown_table.json",
        p7_paths=p7_paths,
        print_inline=print_inline,
        fail_closed=fail_closed,
        docs_dir=docs_dir,
    )
