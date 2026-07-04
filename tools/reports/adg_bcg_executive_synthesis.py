"""BCG-grade executive synthesis for completed ADG runs.

This module is intentionally generic: it synthesizes the artifacts produced by
``tools/generate/generate_full_adg.py`` without hard-coding a particular run,
application, gate, timestamp, or current defect count. The output contract is a
stable JSON/YAML document plus a concise board-ready markdown brief.
"""

from __future__ import annotations

import ast
import datetime as _dt
from dataclasses import asdict
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
    build_bcg_gate_adapter,
    build_bcg_brief,
    build_deprecation_deletion_plan as _build_deprecation_deletion_plan,
    render_bcg_brief_md,
)
from tools.reports.adg_evidence_breakouts import build_gate_breakout, format_evidence_line
from tools.reports.gate_signal_catalog import (
    display_verdict,
    display_verdict_sub,
    executive_gate_copy,
    executive_next_step_options,
    recommended_next_step,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"
BCG_INLINE_CONTRACT_PATH = Path(__file__).with_name("adg_bcg_inline_contract.locked.json")
TEST_FOLDERS = ("unit", "e2e", "regression", "integration", "smoke", "golden", "contract", "fixtures", "unknown")
TEST_TYPE_BY_FOLDER = {"fixtures": "fixture"}
VERDICTS = {"BLOCKED", "GREEN_WITH_DEBT", "REPORT_INCONSISTENT", "DEGRADED", "CLEAN", "NEEDS_RUNTIME_PROOF", "TESTING_CONTROL_GAP", "RUNTIME_PROOF_FAILING"}

_EXECUTIVE_GATE_OVERRIDES: dict[str, dict[str, str]] = {
    "10_infra_wiring": {
        "move": "Clear infra wiring P0 block",
        "why_it_matters": "Small P0 infra-wiring hard stops are usually the fastest path to remove a red ADG gate without broad refactor.",
        "next_step": "Inspect the infra-wiring rows and remove or route the invalid pipeline/spine wiring. Do not re-baseline a P0 block.",
    },
    "13_core_imports_apps": {
        "move": "Stop core importing apps",
        "why_it_matters": "Core importing apps breaks the core/app boundary and directly weakens provider-agnostic core.",
        "next_step": "Move app-specific bindings behind an adapter or app-owned wiring surface; core should keep only generic contracts.",
    },
    "S2_uwg_bypass_ratchet": {
        "move": "Close UWG bypass regression",
        "why_it_matters": "New UWG bypass paths weaken write-governance correctness and can materially affect app run safety.",
        "next_step": "Investigate the new bypass delta and route writes through UWG or an approved adapter; re-baseline only with explicit sign-off.",
    },
    "C3_silent_writes_ratchet": {
        "move": "Close silent write regression",
        "why_it_matters": "Silent writes weaken replay, audit, and side-effect accountability.",
        "next_step": "Fix the new silent-write delta by emitting side-effect evidence or routing through the governed write path.",
    },
    "8_trace_replay_eval": {
        "move": "Repair trace/replay eval regression",
        "why_it_matters": "Trace/replay regressions reduce confidence that runtime behavior is actually proven.",
        "next_step": "Restore the failing trace/replay coverage before relying on runtime proof for the affected path.",
    },
    "S4_unused_imports_ratchet": {
        "move": "Remove unused-import regression only",
        "why_it_matters": "Unused imports are graph-noise hygiene; they should not outrank P0 safety or governance gates.",
        "next_step": "Fix only the new unused-import delta after P0/P1 blockers are clear, unless a row masks a current blocker.",
    },
    "Q2_cyclomatic_complexity_ratchet": {
        "move": "Reduce complexity in touched hotspots",
        "why_it_matters": "Complexity is maintainability risk; it should be scoped to touched or high-blast-radius code, not used as a blanket priority.",
        "next_step": "Refactor only the regressed or high-blast-radius functions tied to current work.",
    },
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


def _load_locked_inline_contract() -> dict[str, Any]:
    contract = _read_json(BCG_INLINE_CONTRACT_PATH)
    if not isinstance(contract, dict):
        raise ValueError(f"Missing locked BCG inline contract: {_repo_rel(BCG_INLINE_CONTRACT_PATH)}")
    return contract


def _validate_locked_bcg_inline_markdown(markdown: str, contract: dict[str, Any] | None = None) -> None:
    contract = contract or _load_locked_inline_contract()
    violations: list[str] = []
    starts_with = str(contract.get("starts_with") or "")
    if starts_with and not markdown.startswith(starts_with):
        violations.append(f"must start with {starts_with!r}")
    cursor = -1
    for section in contract.get("ordered_sections") or []:
        needle = str(section)
        idx = markdown.find(needle)
        if idx < 0:
            violations.append(f"missing required section/table {needle!r}")
            continue
        if idx <= cursor:
            violations.append(f"section/table out of order {needle!r}")
        cursor = idx
    for needle in contract.get("forbidden_substrings") or []:
        text = str(needle)
        if text and text in markdown:
            violations.append(f"forbidden legacy inline content {text!r}")
    if violations:
        raise ValueError("BCG inline contract violation: " + "; ".join(violations))


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


_SNAPSHOT_TOKEN_RE = re.compile(r"(?<!\d)(\d{8})_(\d{4,6})(?!\d)")


def _canonical_snapshot_minute(value: str | None) -> str:
    if not value:
        return ""
    match = _SNAPSHOT_TOKEN_RE.search(str(value))
    if match:
        date_part, time_part = match.groups()
        if date_part.startswith("20"):
            yyyymmdd = date_part
        else:
            yyyymmdd = f"{date_part[4:8]}{date_part[0:2]}{date_part[2:4]}"
        return f"{yyyymmdd}_{time_part[:4]}"
    try:
        parsed = _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return ""
    return parsed.strftime("%Y%m%d_%H%M")


def _artifact_snapshot_token(path: Path | None) -> str:
    return _canonical_snapshot_minute(path.name if path else "")


def _artifact_run_consistency(
    artifacts: dict[str, Path | None],
    loaded_docs: dict[str, Any],
    sqlite_path: Path,
    ts: str,
) -> dict[str, Any]:
    expected = _canonical_snapshot_minute(_sqlite_ts(sqlite_path)) or _canonical_snapshot_minute(ts)
    errors: list[dict[str, Any]] = []
    if not expected:
        return {"status": "DEGRADED", "errors": [], "note": "could not derive canonical run snapshot timestamp"}

    for key, path in artifacts.items():
        observed = _artifact_snapshot_token(path)
        if observed and observed != expected:
            errors.append(
                {
                    "mismatch_type": "artifact_timestamp_mismatch",
                    "artifact_key": key,
                    "file": _repo_rel(path),
                    "expected_snapshot_minute": expected,
                    "observed_snapshot_minute": observed,
                }
            )

    for key, doc in loaded_docs.items():
        if not isinstance(doc, dict):
            continue
        for field in ("snapshot", "snapshot_ts", "run_id", "sqlite_path", "snapshot_path"):
            observed = _canonical_snapshot_minute(str(doc.get(field) or ""))
            if observed and observed != expected:
                errors.append(
                    {
                        "mismatch_type": "artifact_embedded_snapshot_mismatch",
                        "artifact_key": key,
                        "field": field,
                        "expected_snapshot_minute": expected,
                        "observed_snapshot_minute": observed,
                    }
                )

    manifest = loaded_docs.get("generation_manifest")
    if isinstance(manifest, dict):
        cert_status = str(manifest.get("certification_status") or "").lower()
        if cert_status and cert_status not in {"passed", "pass"}:
            errors.append(
                {
                    "mismatch_type": "generation_manifest_not_certified",
                    "artifact_key": "generation_manifest",
                    "certification_status": manifest.get("certification_status"),
                }
            )
        if not manifest.get("sqlite_path") or not manifest.get("snapshot_path"):
            errors.append(
                {
                    "mismatch_type": "generation_manifest_missing_snapshot_binding",
                    "artifact_key": "generation_manifest",
                    "sqlite_path": manifest.get("sqlite_path"),
                    "snapshot_path": manifest.get("snapshot_path"),
                }
            )

    return {"status": "FAIL" if errors else "PASS", "errors": errors}


def _merge_consistency_checks(*checks: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    notes: list[str] = []
    status = "PASS"
    for check in checks:
        check_status = str((check or {}).get("status") or "PASS")
        errors.extend((check or {}).get("errors") or [])
        if (check or {}).get("note"):
            notes.append(str(check["note"]))
        if check_status == "FAIL":
            status = "FAIL"
        elif check_status == "DEGRADED" and status != "FAIL":
            status = "DEGRADED"
    result: dict[str, Any] = {"status": status, "errors": errors}
    if notes:
        result["notes"] = notes
    return result


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
            "display_name": "Foundation blockers",
            "legacy_name": "P0 landmines",
            "why_it_matters": "Foundation blockers are P0 trust hazards: if this artifact is missing, leaders cannot see whether the graph itself is structurally trustworthy.",
            "executive_read": "P0 wave-plan JSON was not loaded; do not claim there are no foundation blockers.",
            "summary": {
                "total_p0_issues": 0,
                "foundation_blockers": 0,
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
    summary["foundation_blockers"] = int(summary.get("total_p0_issues") or len(rows))
    summary["wrong_way_imports"] = sum(1 for r in rows if r["wrong_way_import"])
    summary["protected_surfaces"] = sum(1 for r in rows if r["protected_surface"])
    summary["max_direct_fan_in"] = max((int(r["direct_fan_in"]) for r in rows), default=0)
    return {
        "status": "present",
        "display_name": "Foundation blockers",
        "legacy_name": "P0 landmines",
        "why_it_matters": "Foundation blockers are P0 trust hazards: they can make the graph incomplete, unstable, or misleading before ordinary gate counts are even interpreted.",
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
            "No foundation-blocker action required.",
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


def build_canonical_next_best_actions(
    gate_rows: list[dict[str, Any]],
    graphdb_decision_impact: dict[str, Any],
    testing_investment_map: dict[str, Any],
    artifact_usage_matrix: dict[str, Any],
    mv_usefulness_audit: dict[str, Any],
    action_queue: dict[str, Any],
    *,
    sqlite_path: Path | None = None,
    run_id: str = "",
) -> dict[str, Any]:
    actions = []
    fix = [g for g in gate_rows if display_verdict(g) == "FIX"]
    for g in sorted(fix, key=_fix_work_order_key)[:3]:
        row = build_executive_priority_row(g, sqlite_path, run_id)
        actions.append(
            _action(
                "fix_blocker",
                row["move"],
                str(g.get("gate_id")),
                row["why_it_matters"],
                "gate",
                "Add mapped tests when touched scope overlaps a hotspot.",
                "now",
                "high",
                business_reason=row["why_it_matters"],
                technical_reason=row["evidence"],
                why_this_rank=row["next_step"],
                next_step=row["next_step"],
                move=row["move"],
                evidence=row["evidence"],
                why_it_matters=row["why_it_matters"],
                decision_options=row["decision_options"],
                done_condition=row["done_condition"],
                affected_system=row["affected_system"],
                affected_layers=row["affected_layers"],
                change_breakout=row["change_breakout"],
                diagram=row["diagram"],
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
                next_step="Add mapped tests before touching this surface again.",
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
                    next_step="Refactor after the blocker and test exposure are explicit.",
                )
            )
            break
    gate_adapter = build_bcg_gate_adapter({"gates": gate_rows})
    burn_down_gate_ids = {
        str(row.get("gate_id"))
        for row in gate_adapter.get("sections", {}).get("burn_down", {}).get("rows", [])
    }
    ratchets = [
        g
        for g in gate_rows
        if display_verdict(g) == "TRACK"
        and display_verdict_sub(g) == "floor"
        and str(g.get("gate_id")) in burn_down_gate_ids
    ]
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
                next_step="Burn down the ratchet after the current red gates clear.",
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
                next_step="Deprecate only after the higher-risk surfaces are handled.",
            )
    )
    for i, row in enumerate(actions[:8], 1):
        row["rank"] = i
        row["priority"] = i
    return {"status": "present", "rows": actions[:8]}


def _mece_gate_summary(
    *,
    verdict: dict[str, Any],
    consistency: dict[str, Any],
    runtime: dict[str, Any],
    gate_adapter: dict[str, Any],
    audit_notes: dict[str, Any],
) -> dict[str, Any]:
    sections = gate_adapter.get("sections") or {}
    decision_gates: list[dict[str, Any]] = []
    verdict_id = str(verdict.get("verdict") or "")
    if verdict_id == "REPORT_INCONSISTENT":
        errors = (consistency or {}).get("errors") or []
        decision_gates.append(
            {
                "bucket": "DECISION_GATE",
                "gate_id": "report_consistency",
                "move": "Repair graph/report consistency",
                "why_it_matters": "The executive order is not decision-grade until graph and report agree.",
                "evidence": f"{_fmt_int(len(errors))} graph/report mismatch row(s) block decision-grade ordering.",
                "next_step": "Repair report consistency, then rerun ADG before treating the ranked work queue as authoritative.",
                "scope": "mv_graph_vs_report_mismatches",
                "action_type": "decision_gate",
                "decision": "repair_reporting",
            }
        )
    elif verdict_id == "DEGRADED":
        reasons = "; ".join(str(v) for v in (verdict.get("degradation_reasons") or [])[:3])
        decision_gates.append(
            {
                "bucket": "DECISION_GATE",
                "gate_id": "required_report_inputs",
                "move": "Restore decision-grade artifacts",
                "why_it_matters": "Missing required inputs make lower-priority ordering unreliable.",
                "evidence": reasons or "Required artifacts are missing.",
                "next_step": "Restore required report inputs, then rerun the executive summary.",
                "scope": "required report inputs",
                "action_type": "decision_gate",
                "decision": "repair_reporting",
            }
        )
    elif verdict_id == "RUNTIME_PROOF_FAILING":
        decision_gates.append(
            {
                "bucket": "DECISION_GATE",
                "gate_id": "runtime_spine",
                "move": "Fix failing runtime proof",
                "why_it_matters": "Observed runtime failure is a quality failure, not a diagnostic detail.",
                "evidence": runtime.get("measurement_gap_vs_quality_failure") or "Runtime proof is failing.",
                "next_step": "Fix the failing runtime path before relying on ordinary gate cleanup ordering.",
                "scope": "runtime_spine",
                "action_type": "decision_gate",
                "decision": "repair_runtime",
            }
        )

    def _section_rows(section: str, bucket: str) -> list[dict[str, Any]]:
        rows = []
        for row in (sections.get(section) or {}).get("rows", []) or []:
            item = dict(row)
            item["bucket"] = bucket
            rows.append(item)
        return rows

    severity_rows = []
    for row in (audit_notes.get("guardian_summary") or []):
        item = dict(row)
        item["bucket"] = "SEVERITY_INVENTORY"
        severity_rows.append(item)

    summary = {
        "schema_version": "adg-report-mece/v1",
        "rule": (
            "Decision gates, fix work, burn-down backlog, KPI/watchlist, severity inventory, "
            "and clear gates are mutually exclusive ownership buckets."
        ),
        "decision_gates": decision_gates,
        "fix_now": _section_rows("fix_now", "FIX_NOW"),
        "burn_down_after_green": _section_rows("burn_down", "BURN_DOWN_AFTER_GREEN"),
        "kpi_watchlist": _section_rows("kpi_watchlist", "KPI_WATCHLIST"),
        "severity_inventory": severity_rows,
        "clear": _section_rows("clear", "CLEAR"),
    }
    summary["bucket_counts"] = {
        key: len(summary[key])
        for key in (
            "decision_gates",
            "fix_now",
            "burn_down_after_green",
            "kpi_watchlist",
            "severity_inventory",
            "clear",
        )
    }
    return summary


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
    next_step: str | None = None,
    move: str | None = None,
    evidence: str | None = None,
    why_it_matters: str | None = None,
    decision: str | None = None,
    decision_options: list[dict[str, Any]] | None = None,
    done_condition: str | None = None,
    affected_system: str | None = None,
    affected_layers: list[str] | None = None,
    change_breakout: list[dict[str, Any]] | None = None,
    diagram: dict[str, Any] | None = None,
) -> dict[str, Any]:
    move_text = move or action
    why_text = why_it_matters or business_reason or why
    evidence_text = evidence or technical_reason or testing
    next_step_text = next_step or why_this_rank or why
    decision_text = decision or action_type
    options = list(decision_options or [])
    return {
        "rank": None,
        "priority": None,
        "action_type": action_type,
        "action": action,
        "move": move_text,
        "scope": scope,
        "why_now": why,
        "why_it_matters": why_text,
        "business_reason": why_text,
        "evidence": evidence_text,
        "technical_reason": evidence_text,
        "next_step": next_step_text,
        "why_this_rank": next_step_text,
        "decision": decision_text,
        "evidence_used": [{"signal_name": scope, "signal_type": signal_type, "decision_effect": why}],
        "testing_requirement": testing,
        "done_condition": done_condition
        or "Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived.",
        "confidence": confidence,
        "timing": timing,
        "decision_options": options,
        "affected_system": affected_system or "",
        "affected_layers": list(affected_layers or []),
        "change_breakout": list(change_breakout or []),
        "diagram": diagram,
        "work": move_text,
    }


def _fix_work_order_key(gate: dict[str, Any]) -> tuple[int, int, int, int, str]:
    """Decision-grade FIX ordering for BCG/action output.

    This is deliberately not a hygiene sorter. A P3 gate with a large row count
    must not outrank a P0 blocker or P0 regression just because it is noisy.
    """
    gate_id = str(gate.get("gate_id") or "").strip()
    band = str(gate.get("band") or "").strip().upper()
    enforcement = str(gate.get("enforcement") or "").strip().lower()
    band_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(band, 9)
    enforcement_rank = 0 if enforcement == "block" else 1
    if enforcement == "block":
        # For hard stops at the same severity, take the smallest concrete block
        # first: it is usually the fastest path to remove a merge stopper.
        secondary = int(gate.get("violation_count") or gate.get("total_records") or 0)
    else:
        secondary = -_reg_delta(gate)
    materiality_rank = {
        "10_infra_wiring": 0,
        "13_core_imports_apps": 1,
        "S2_uwg_bypass_ratchet": 2,
        "C3_silent_writes_ratchet": 0,
        "8_trace_replay_eval": 1,
        "M_taint_actionable_ratchet": 2,
        "I2_replay_surface_gaps_ratchet": 0,
        "Q2_cyclomatic_complexity_ratchet": 0,
        "M1_module_loc_ratchet": 1,
        "S4_unused_imports_ratchet": 2,
    }.get(gate_id, 50)
    return (band_rank, enforcement_rank, materiality_rank, secondary, gate_id)


def _format_decision_options(gate: dict[str, Any], breakout: dict[str, Any]) -> list[dict[str, Any]]:
    return [asdict(option) for option in executive_next_step_options(gate, breakout)]


def _format_adversarial_next_step(copy: Any, breakout: dict[str, Any], decision_options: list[dict[str, Any]]) -> str:
    summary = str((breakout or {}).get("summary") or "").strip().rstrip(".")
    if summary and summary != "breakout unavailable":
        lead = f"Review the breakout: {summary}."
    else:
        lead = f"Review the {getattr(copy, 'finding_name', 'finding')} evidence."
    if (breakout or {}).get("status") == "present":
        return (
            f"{lead} Fix convenience coupling; introduce an adapter if the cross-layer call is intentional; "
            "grant an exemption only with owner, rationale, and retirement condition; re-baseline only with explicit architecture approval."
        )
    option_labels = ", ".join(opt.get("label", "") for opt in decision_options[:4] if opt.get("label"))
    if option_labels:
        return f"{lead} Investigate evidence before changing code; the current choices are {option_labels}."
    return f"{lead} Investigate evidence before changing code."


def build_executive_priority_row(
    gate: dict[str, Any],
    sqlite_path: Path | None,
    run_id: str,
) -> dict[str, Any]:
    gate_id = str(gate.get("gate_id") or "")
    copy = executive_gate_copy(gate)
    breakout = build_gate_breakout(gate, sqlite_path) if sqlite_path is not None else {
        "status": "missing",
        "finding_name": copy.finding_name,
        "summary": "breakout unavailable",
        "groups": [],
        "samples": [],
    }
    decision_options = _format_decision_options(gate, breakout)
    evidence = format_evidence_line(gate, run_id, breakout)
    if gate_id == "13_core_imports_apps":
        row_count = _fmt_int(gate.get("violation_count") or gate.get("total_records") or gate.get("records") or 0)
        evidence = f"ADG `{run_id}` found {row_count} core-to-app import row(s): `agentic_core` imports `apps_*`."
    next_step = _format_adversarial_next_step(copy, breakout, decision_options)
    affected_layers = [
        " -> ".join([part for part in (str(group.get("src_layer") or "").strip(), str(group.get("dst_layer") or "").strip()) if part])
        for group in (breakout.get("groups") or [])[:1]
        if group.get("src_layer") or group.get("dst_layer")
    ]
    if not affected_layers and breakout.get("summary") and breakout.get("summary") != "breakout unavailable":
        affected_layers = [str(breakout.get("summary"))]
    override = _EXECUTIVE_GATE_OVERRIDES.get(gate_id, {})
    move = override.get("move") or copy.move
    why_it_matters = override.get("why_it_matters") or copy.why_it_matters
    next_step = override.get("next_step") or next_step
    return {
        "rank": None,
        "priority": None,
        "action_type": "fix_blocker",
        "action": move,
        "move": move,
        "scope": gate_id,
        "why_now": why_it_matters,
        "why_it_matters": why_it_matters,
        "business_reason": why_it_matters,
        "evidence": evidence,
        "technical_reason": evidence,
        "next_step": next_step,
        "why_this_rank": next_step,
        "decision": "fix_blocker",
        "evidence_used": [{"signal_name": gate_id, "signal_type": "gate", "decision_effect": why_it_matters}],
        "testing_requirement": "Add mapped tests when touched scope overlaps a hotspot.",
        "done_condition": "Rerun ADG and confirm the gate returns to green or is explicitly waived.",
        "confidence": "high",
        "timing": "now",
        "decision_options": decision_options,
        "affected_system": copy.affected_system,
        "affected_layers": affected_layers,
        "change_breakout": list((breakout.get("groups") or [])),
        "diagram": copy.diagram or breakout.get("diagram"),
        "work": copy.move,
    }


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


def _health_lens(gates: list[dict[str, Any]], gate_adapter: dict[str, Any] | None = None) -> dict[str, Any]:
    adapter = gate_adapter or build_bcg_gate_adapter({"gates": gates})
    sections = adapter.get("sections", {})
    fix_rows = list(sections.get("fix_now", {}).get("rows", []))
    burn_rows = list(sections.get("burn_down", {}).get("rows", []))
    kpi_rows = list(sections.get("kpi_watchlist", {}).get("rows", []))
    clear_rows = list(sections.get("clear", {}).get("rows", []))
    buckets = {
        "CLEAR": len(clear_rows),
        "BURN": len(burn_rows),
        "KPI": len(kpi_rows),
        "FIX": len(fix_rows),
    }
    red = []
    for g in fix_rows:
        raw_gate = g.get("raw_gate") if isinstance(g.get("raw_gate"), dict) else g
        red.append({"gate_id": str(g.get("gate_id", "")), "band": str(g.get("band", "")), "enforcement": str(g.get("enforcement", "")), "total_records": int(g.get("rows") or 0), "baseline_records": g.get("baseline_count"), "regression_delta": _reg_delta(raw_gate), "record_type": str(g.get("signal") or "gate records"), "executive_read": "Current red gate. Treat as blocker, but inspect delta to distinguish tiny ratchet creep from structural failure.", "next_action": str(g.get("next_step") or recommended_next_step(raw_gate)), "done_condition": "Gate leaves the adapter FIX section."})
    ratchets = [g for g in burn_rows if str(g.get("sub")) == "floor"]
    open_non = [g for g in burn_rows if str(g.get("sub")) != "floor"]
    return {
        "status": "present",
        "why_it_matters": "Health gates tell leaders whether the run is green, blocked, carrying owned burn-down debt, or merely showing KPI/watchlist signals.",
        "summary": {"total_gates": len(gates), "clear_gates": buckets.get("CLEAR", 0), "track_gates": buckets.get("BURN", 0), "burn_down_gates": buckets.get("BURN", 0), "kpi_watchlist_gates": buckets.get("KPI", 0), "fix_gates": buckets.get("FIX", 0), "overall_verdict": "BLOCKED" if buckets.get("FIX") else "PASS", "executive_read": "FIX blocks green; BURN is accepted work; KPI is trend/watchlist; CLEAR needs no action."},
        "buckets": [{"bucket": k, "count": buckets.get(k, 0), "plain_meaning": {"CLEAR": "No action now.", "BURN": "Owned backlog; burn down after red gates.", "KPI": "Watchlist/trend only; no burn-down unless planned.", "FIX": "Current blocker or regression requiring action before decision-grade green."}[k]} for k in ("CLEAR", "BURN", "KPI", "FIX")],
        "red_gates": red,
        "managed_debt": {"ratchet_floor_records": sum(int(g.get("rows") or 0) for g in ratchets), "open_non_ratchet_records": sum(int(g.get("rows") or 0) for g in open_non), "top_ratchets": [{"gate_id": str(g.get("gate_id", "")), "records": int(g.get("rows") or 0), "executive_read": "Accepted baseline debt, not current red.", "after_green_action": "Burn down after FIX rows clear."} for g in sorted(ratchets, key=lambda x: -int(x.get("rows") or 0))[:5]]},
        "kpi_watchlist": {"gate_count": len(kpi_rows), "row_count": sum(int(g.get("rows") or 0) for g in kpi_rows), "top_signals": [{"gate_id": str(g.get("gate_id", "")), "records": int(g.get("rows") or 0), "executive_read": "Watchlist signal; do not treat as burn-down work without an owner and target.", "recommended_action": str(g.get("next_step") or "Watch trend.")} for g in sorted(kpi_rows, key=lambda x: -int(x.get("rows") or 0))[:8]]},
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
    fix_gates = int(health["summary"].get("fix_gates") or 0)
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
    elif fix_gates:
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
        if fix_gates:
            recommendation = "Treat report inconsistency as a decision-quality caveat, not the first engineering work item; clear concrete red FIX/P0 evidence first, then rerun ADG and repair report consistency if it persists."
        else:
            recommendation = "Repair report consistency before treating lower-severity ranking as authoritative."
    elif verdict == "RUNTIME_PROOF_FAILING":
        recommendation = "Fix the failing runtime-proof path before treating ordinary gate cleanup as the highest-confidence next action."
    elif verdict == "DEGRADED":
        recommendation = "Repair missing decision-grade artifacts before relying on this summary."
    return {"verdict": verdict, "recommendation": recommendation, "funding_posture": posture, "why_now": "Decision combines artifact consistency, runtime proof, FIX status, regression/newness, GraphDB/MV linkage, and testing exposure.", "risk_if_ignored": "The organization may chase raw counts while missing a broken report, failing runtime proof, smaller blocker, or under-tested high-blast-radius surface.", "what_not_to_do": ["Do not rank work by raw MV row count alone.", "Do not let ordinary FIX gates hide report inconsistency or runtime failure.", "Do not start a generic testing mega-project when mapped tests can follow the current slice."], "crisis_level": crisis, "one_sentence_bottom_line": f"ADG is {verdict}: act on decision-linked blockers/testing gaps, defer diagnostic-only noise."}


def _base_doc(ts: str, sqlite_path: Path, gate_doc: dict[str, Any] | None, degraded: list[str]) -> dict[str, Any]:
    emit_status = "DEGRADED" if degraded else "PASS"
    return {"schema_version": "1.0", "artifact_kind": "adg_bcg_executive_summary", "run": {"run_id": ts, "generated_at_utc": _now(), "snapshot_ts": (gate_doc or {}).get("timestamp") or ts, "commit_sha": _git_sha(), "repo_state_hash": "", "emit_status": emit_status, "decision_grade_status": "DEGRADED" if degraded else "PENDING", "degradation_reasons": degraded}, "plain_english_context": {"what_adg_is": {"summary": "ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.", "analogy": "ADG is the codebase X-ray: it sees dependency skeletons, health gates, and structural risk.", "measured_scope": {"connections": None, "gates": (gate_doc or {}).get("total_gates"), "files": None}, "caveats": []}}}


def build_bcg_executive_summary(adg_artifacts_dir: Path, ts: str, sqlite_path: Path, gate_results_path: Path | None, action_queue_path: Path | None, review_template_path: Path | None, burndown_path: Path | None, p7_paths: dict[str, Path | str | None]) -> dict[str, Any]:
    artifacts = {
        k: Path(v)
        for k, v in {"gate_results": gate_results_path, "bcg_adapter": adg_artifacts_dir / f"adg_bcg_adapter_{ts}.json", "action_queue": action_queue_path, "review_template": review_template_path, "burndown_table": burndown_path, "burndown_report": adg_artifacts_dir / "adg_burndown_report.md", "sqlite_snapshot": sqlite_path, "generation_manifest": adg_artifacts_dir / f"adg_generation_manifest_{ts}.json", **p7_paths}.items()
        if v is not None
    }
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
    gate_adapter = loaded.get("bcg_adapter")
    if not isinstance(gate_adapter, dict) or gate_adapter.get("artifact_kind") != "adg_bcg_gate_adapter":
        gate_adapter = build_bcg_gate_adapter(gate_doc or {"gates": gates}, loaded.get("burndown_table") or {})
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
    graph_consistency = _artifact_consistency(sqlite_path)
    run_consistency = _artifact_run_consistency(artifacts, loaded, sqlite_path, ts)
    consistency = _merge_consistency_checks(graph_consistency, run_consistency)
    health = _health_lens(gates, gate_adapter)
    runtime = _runtime_lens(p7_docs, sqlite_path)
    p0_landmines = _p0_landmine_lens(p7_docs.get("p0_wave_plan"))
    product = _product_lens(testing, graph)
    actions = build_canonical_next_best_actions(
        gates,
        graph,
        testing,
        artifact_matrix,
        mv_audit,
        action_queue,
        sqlite_path=sqlite_path,
        run_id=ts,
    )
    audit_notes = _audit_notes(gates, loaded.get("burndown_table"), consistency)
    kpi_scorecard = _p0_p3_reconciliation(p0_landmines, audit_notes, health)
    executive_decision = _verdict(health, runtime, testing, artifact_matrix, consistency)
    gate_mece_summary = _mece_gate_summary(
        verdict=executive_decision,
        consistency=consistency,
        runtime=runtime,
        gate_adapter=gate_adapter,
        audit_notes=audit_notes,
    )
    doc.update(
        {
            "executive_decision": executive_decision,
            "prioritization_model": _prioritization_model(),
            "bcg_gate_adapter": gate_adapter,
            "kpi_scorecard": kpi_scorecard,
            "p0_p3_reconciliation": kpi_scorecard,
            "p0_action_queue_summary": _p0_action_queue_summary(action_queue),
            "gate_mece_summary": gate_mece_summary,
            "lens_0_p0_landmines": p0_landmines,
            "lens_1_health_gates": health,
            "lens_2_runtime_proof_observability": runtime,
            "lens_3_product_app_risk": product,
            "lens_4_testing_control_gaps": testing,
            "lens_5_graphdb_mv_decision_impact": graph,
            "canonical_next_best_actions": actions,
            "after_green_plan": _after_green(health, graph, testing),
            "artifact_usage_matrix": artifact_matrix,
            "mv_usefulness_audit": mv_audit,
            "dead_code_report": dead_code_report,
            "deprecation_deletion_plan": deprecation_plan,
            "defer_delete_deprecate": {"status": "present", "rows": deprecation_plan.get("cleanup_candidates", [])},
            "audit_notes": audit_notes,
            "honest_bottom_line": _bottom_line(health, runtime, testing, actions),
            "raw_inputs": _raw_inputs(artifacts, loaded),
            "evidence_trace": _evidence_trace(graph, artifact_matrix, degraded),
        }
    )
    doc["bcg_findings"] = _executive_bcg_brief(doc)
    doc["run"]["repo_state_hash"] = _hash_repo_state([p for p in artifacts.values() if p])
    doc["run"]["decision_grade_status"] = doc["executive_decision"]["verdict"]
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


def _count_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _display_count(value: Any) -> str:
    coerced = _count_or_none(value)
    return "not loaded" if coerced is None else f"{coerced:,}"


def _audit_band_summary_rows(burndown: dict[str, Any] | None) -> list[dict[str, Any]]:
    summary = (burndown or {}).get("summary") or {}
    rows = []
    for band in ("P0", "P1", "P2", "P3"):
        raw = summary.get(band) or {}
        audit_net = _count_or_none(raw.get("net"))
        rows.append(
            {
                "band": band,
                "gross": _count_or_none(raw.get("gross")),
                "guardian": _count_or_none(raw.get("guardian")),
                "non_exempt": audit_net,
                "audit_net": audit_net,
                "meaning": (
                    "Severity audit inventory after guardian exemptions; not a live work order by itself."
                    if audit_net is not None
                    else "Burndown summary was not loaded for this band."
                ),
                "executive_read": "Audit context only until it maps to a failing gate, runtime failure, hotspot, or changed code.",
            }
        )
    return rows


def _red_gate_counts_by_band(health: dict[str, Any]) -> dict[str, int]:
    counts = {band: 0 for band in ("P0", "P1", "P2", "P3")}
    for row in health.get("red_gates", []) or []:
        band = str(row.get("band") or "").upper()
        if band in counts:
            counts[band] += 1
    return counts


def _p0_p3_reconciliation(p0_lens: dict[str, Any], audit_notes: dict[str, Any], health: dict[str, Any]) -> dict[str, Any]:
    foundation_count = None
    if p0_lens.get("status") == "present":
        foundation_count = _count_or_none((p0_lens.get("summary") or {}).get("foundation_blockers"))
        if foundation_count is None:
            foundation_count = _count_or_none((p0_lens.get("summary") or {}).get("total_p0_issues"))
    audit_rows = list(audit_notes.get("guardian_summary") or [])
    audit_by_band = {str(row.get("band") or ""): row for row in audit_rows}
    red_by_band = _red_gate_counts_by_band(health)
    p0_audit_net = (audit_by_band.get("P0") or {}).get("audit_net")
    p0_live_gate_drivers = red_by_band.get("P0", 0)
    band_rows = []
    for band in ("P0", "P1", "P2", "P3"):
        audit_row = audit_by_band.get(band) or {}
        band_rows.append(
            {
                "band": band,
                "audit_gross": audit_row.get("gross"),
                "guardian_exempted": audit_row.get("guardian"),
                "audit_net": audit_row.get("audit_net"),
                "audit_net_display": _display_count(audit_row.get("audit_net")),
                "foundation_blockers": foundation_count if band == "P0" else None,
                "foundation_blockers_display": _display_count(foundation_count) if band == "P0" else "n/a",
                "live_gate_drivers": red_by_band.get(band, 0),
                "action_role": (
                    "Stop-the-line only if foundation blockers are present; otherwise audit net is evidence to map."
                    if band == "P0"
                    else "Severity inventory to map to a failing gate, hotspot, changed code, or owner."
                ),
            }
        )
    return {
        "status": "present",
        "executive_read": "P0 is split into three ledgers: foundation blockers, audit inventory, and live gate drivers.",
        "rule": "Do not add these counts together. A P0 audit finding is not a foundation blocker unless it comes from the foundation-blocker wave plan.",
        "kpis": [
            {
                "id": "foundation_blockers",
                "kpi": "Foundation blockers",
                "value": foundation_count,
                "display_value": _display_count(foundation_count),
                "meaning": "P0 trust hazards that can make ADG evidence incomplete, unstable, or misleading.",
                "action_rule": "Stop the line if greater than zero; if not loaded, do not claim clean.",
            },
            {
                "id": "p0_audit_net",
                "kpi": "P0 audit net",
                "value": p0_audit_net,
                "display_value": _display_count(p0_audit_net),
                "meaning": "P0 severity audit inventory after guardian exemptions.",
                "action_rule": "Audit-only unless mapped to a failing gate, runtime failure, hotspot, or changed code.",
            },
            {
                "id": "p0_live_gate_drivers",
                "kpi": "P0 live gate drivers",
                "value": p0_live_gate_drivers,
                "display_value": _display_count(p0_live_gate_drivers),
                "meaning": "Current red P0 gates that can drive today's work order.",
                "action_rule": "Can drive priority when the gate is FIX/red and decision-linked.",
            },
        ],
        "p0_p3_audit_inventory": band_rows,
        "reconciliation_note": "Zero foundation blockers can coexist with nonzero P0 audit net because they measure different ledgers: run-trust hazards versus severity audit inventory.",
    }


def build_deprecation_deletion_plan(
    dead_code_report: dict[str, Any] | None,
    mv_usefulness_audit: dict[str, Any] | None,
    artifact_usage_matrix: dict[str, Any] | None,
) -> dict[str, Any]:
    return _build_deprecation_deletion_plan(dead_code_report, mv_usefulness_audit, artifact_usage_matrix)


def _audit_notes(gates: list[dict[str, Any]], burndown: dict[str, Any] | None, consistency: dict[str, Any] | None = None) -> dict[str, Any]:
    consistency = consistency or {"status": "PASS", "errors": []}
    return {"status": "present", "guardian_summary": _audit_band_summary_rows(burndown), "severity_summary": {"executive_read": "P0-P3 severity inventory is audit math unless tied to current FIX/action rows.", "rows": []}, "artifact_consistency": consistency, "notes": ["Guardian exceptions are audit math only; they do not automatically explain away real problems.", "Diagnostic-only MVs are not immediate work unless tied to a blocker, testing gap, critical path, or planned slice.", "Do not add foundation-blocker counts to audit-net counts; they come from different ledgers.", "Artifact consistency is derived from mv_graph_vs_report_mismatches (graph-vs-report truth), not assumed PASS."]}


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


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _action_queue_scope(row: dict[str, Any]) -> str:
    return str(
        row.get("file_path")
        or row.get("source_id")
        or row.get("gate_id")
        or row.get("scope")
        or row.get("symbol")
        or "unknown"
    )


def _p0_action_queue_summary(action_queue: dict[str, Any]) -> dict[str, Any]:
    actions = [row for row in action_queue.get("actions", []) or [] if isinstance(row, dict)]
    p0_fix: list[dict[str, Any]] = []
    p0_wave: list[dict[str, Any]] = []
    for row in actions:
        band = str(row.get("sort_band") or row.get("band") or "").upper()
        cluster = str(row.get("verdict_cluster") or "").upper()
        kind = str(row.get("action_kind") or "").lower()
        if band.startswith("P0") and cluster == "FIX":
            p0_fix.append(row)
        elif band.startswith("P0") or cluster == "P0_WAVE" or kind.startswith("p0_"):
            p0_wave.append(row)
    rows = p0_fix + p0_wave
    scopes = [_action_queue_scope(row) for row in rows]
    top_scopes = scopes[:3]
    if not rows:
        metric = "no P0 action-queue rows"
    elif p0_fix:
        metric = f"{_display_count(len(p0_fix))} P0 FIX row(s)"
        if p0_wave:
            metric += f"; {_display_count(len(p0_wave))} P0 wave row(s)"
    else:
        metric = f"{_display_count(len(p0_wave))} P0 wave file row(s)"
    if top_scopes:
        metric += ": " + ", ".join(top_scopes)
        if len(scopes) > len(top_scopes):
            metric += f", +{len(scopes) - len(top_scopes)} more"
    return {
        "p0_fix_count": len(p0_fix),
        "p0_wave_count": len(p0_wave),
        "total_p0_rows": len(rows),
        "top_scopes": top_scopes,
        "metric": metric,
        "rows": rows,
    }


def _kpis_by_id(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scorecard = doc.get("kpi_scorecard") or doc.get("p0_p3_reconciliation") or {}
    return {str(row.get("id") or ""): row for row in scorecard.get("kpis", []) or []}


def _kpi_int(doc: dict[str, Any], key: str) -> int:
    return _int_value((_kpis_by_id(doc).get(key) or {}).get("value"), 0)


def _p0_priority_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    p0_summary = doc.get("p0_action_queue_summary") or {}
    if _int_value(p0_summary.get("total_p0_rows")) <= 0:
        return []
    has_fix = _int_value(p0_summary.get("p0_fix_count")) > 0
    move = "Clear P0 FIX rows" if has_fix else "Clear P0 foundation wave"
    return [
        {
            "priority": 1,
            "move": move,
            "why_it_matters": "P0 work is the first severity lane; do not let a P1 ratchet or graph/report caveat jump ahead of it.",
            "evidence": p0_summary.get("metric"),
            "next_step": "Burn down the listed P0 rows first, then rerun ADG before ranking P1-P3.",
            "scope": "P0 action queue",
            "decision_options": [],
            "done_condition": "Rerun ADG and confirm P0 action rows/foundation blockers are zero or explicitly waived.",
            "affected_system": "ADG P0 lane",
            "affected_layers": [],
            "change_breakout": [],
            "diagram": None,
            "action_type": "p0_action_queue",
            "decision": "clear_p0_first",
        }
    ]


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
    kpi_scorecard = doc.get("kpi_scorecard") or {}
    kpi_by_id = {str(row.get("id") or ""): row for row in kpi_scorecard.get("kpis", []) or []}
    raw_inputs = doc.get("raw_inputs") or {}
    artifacts = raw_inputs.get("artifacts") or {}
    sqlite_snapshot = str(artifacts.get("sqlite_snapshot") or "").strip()
    snapshot_ts = _sqlite_ts(Path(sqlite_snapshot)) if sqlite_snapshot else ""
    decision_gate_rows = list((doc.get("gate_mece_summary") or {}).get("decision_gates") or [])
    priority_rows: list[dict[str, Any]] = _p0_priority_rows(doc)
    seen_scopes = {str(row.get("scope") or "") for row in priority_rows}
    verdict = str(d.get("verdict") or "UNKNOWN")
    recommendation = str(d.get("recommendation") or "no recommendation emitted").rstrip(".")
    for row in actions:
        if len(priority_rows) >= 4:
            break
        scope = str(row.get("scope") or "")
        if scope and scope in seen_scopes:
            continue
        priority_rows.append(
            {
                "priority": int(row.get("rank") or len(priority_rows) + 1),
                "move": row.get("move") or row.get("action"),
                "why_it_matters": row.get("why_it_matters") or row.get("business_reason") or row.get("why_now"),
                "evidence": row.get("evidence") or row.get("technical_reason") or row.get("testing_requirement") or row.get("action"),
                "next_step": row.get("next_step") or row.get("why_this_rank") or row.get("why_now"),
                "scope": row.get("scope"),
                "decision_options": row.get("decision_options") or [],
                "done_condition": row.get("done_condition") or "",
                "affected_system": row.get("affected_system") or "",
                "affected_layers": row.get("affected_layers") or [],
                "change_breakout": row.get("change_breakout") or [],
                "diagram": row.get("diagram"),
                "action_type": row.get("action_type"),
                "decision": row.get("decision"),
            }
        )
        if scope:
            seen_scopes.add(scope)
    first_priority = priority_rows[0] if priority_rows else {}
    first_move = str(first_priority.get("move") or first_priority.get("scope") or "the first P0 blocker")
    first_scope = str(first_priority.get("scope") or first_move)
    first_evidence = str(first_priority.get("evidence") or "ADG emitted a concrete P0 row").rstrip(".")
    red_gates_by_id = {str(row.get("gate_id") or ""): row for row in health.get("red_gates", []) or []}
    first_gate = red_gates_by_id.get(first_scope, {})
    if first_scope == "P0 action queue":
        first_row_count = _display_count((doc.get("p0_action_queue_summary") or {}).get("total_p0_rows"))
    else:
        first_row_count = _fmt_int(first_gate.get("total_records") or first_gate.get("records") or first_gate.get("violation_count") or 0)
    fix_gate_count = _fmt_int(health.get("summary", {}).get("fix_gates", 0))
    runtime_signals = runtime.get("runtime_proof_signals") or []
    runtime_status = str((runtime_signals[0] if runtime_signals else {}).get("status") or runtime.get("status") or "unknown")
    testing_rows = testing.get("investment_map") or []
    testing_scope = str((testing_rows[0] if testing_rows else {}).get("production_scope") or "No promoted testing hotspot")
    testing_risk = str(((testing_rows[0] if testing_rows else {}).get("risk") or {}).get("risk_band") or "unknown")
    if verdict == "REPORT_INCONSISTENT":
        if priority_rows:
            business_suffix = (
                "ADG is giving one safe decision, not a full ranked roadmap: clear concrete P0 evidence "
                "before lower-severity work. The report inconsistency only limits confidence in the lower-priority "
                "ranking; it does not change the first engineering move."
            )
            priority_rule = (
                "Concrete P0 FIX rows first; graph/report mismatch is a decision-quality caveat, "
                "not the first engineering work item."
            )
            why_this_order = [
                "Concrete P0 FIX rows are actionable now and still outrank report-maintenance work.",
                "Graph/report mismatch makes lower-severity ordering provisional, not a reason to defer the P0 blocker.",
                "After the P0 fix, rerun ADG to prove both the gate and report consistency.",
            ]
        else:
            business_suffix = "Repair report consistency before treating lower-severity order as authoritative."
            priority_rule = (
                "Decision queue: repair consistency before ranking lower-severity backlog; "
                "do not let high-volume P3 hygiene outrank P0 safety/governance gates."
            )
            why_this_order = [
                "Graph/report mismatch means the lower-severity action order is not decision-grade yet.",
                "Once consistent, concrete P0 FIX gates outrank P3 hygiene even when the P3 row count is larger.",
                "Testing exposure should travel with the relevant fix slice.",
            ]
    elif verdict == "DEGRADED":
        business_suffix = "Restore required report inputs before using this summary for prioritization."
        priority_rule = "Restore missing evidence first, then rerun the executive summary."
        why_this_order = [
            "Missing required artifacts make the report incomplete.",
            "Once required inputs are present, rerun the summary before funding lower-priority work.",
        ]
    elif verdict == "RUNTIME_PROOF_FAILING":
        business_suffix = "Fix failing runtime proof before ordinary gate cleanup."
        priority_rule = (
            "Decision queue: fix runtime proof, then remove concrete P0 hard stops/regressions; "
            "defer high-volume P3 hygiene until safety/governance gates are clear."
        )
        why_this_order = [
            "Observed runtime failure is a quality failure, not a diagnostic detail.",
            "Once runtime proof is clean, ordinary FIX gates can drive the next slice.",
        ]
    else:
        business_suffix = "Spend executive time on blockers and test gaps before accepted debt."
        priority_rule = (
            "Decision queue: concrete FIX gates by materiality and severity first; "
            "P3 hygiene only wins when it is tied to the current blocker slice."
        )
        why_this_order = (doc.get("honest_bottom_line") or {}).get("bullets", [])[:4]
    if verdict == "REPORT_INCONSISTENT" and priority_rows:
        business_read = business_suffix
        technical_read = [
            f"First P0 evidence: `{first_scope}`; rows: {first_row_count}.",
            f"Source: ADG `{doc.get('run', {}).get('run_id') or 'unknown'}` emitted this as decision-linked queue evidence.",
            "Report caveat: graph/report consistency is FAIL; only lower-priority ranking is provisional.",
            f"Run context: {fix_gate_count} FIX gate(s); {_fmt_int(len(actions))} action rows emitted.",
            f"Runtime signal: {runtime_status}.",
            f"Testing signal: {testing_scope}; risk={testing_risk}.",
        ]
        rendered_decision_gates: list[dict[str, Any]] = []
    else:
        business_read = f"ADG is {d.get('verdict', 'UNKNOWN')}: {recommendation}. {business_suffix}"
        technical_read = [
            (
                f"ADG source: {sqlite_snapshot} (snapshot {snapshot_ts})"
                if sqlite_snapshot
                else f"ADG source: missing (snapshot {doc.get('run', {}).get('snapshot_ts') or doc.get('run', {}).get('run_id') or 'missing'})"
            ),
            f"FIX gates: {fix_gate_count}; "
            f"burn-down gates: {_fmt_int(health.get('summary', {}).get('burn_down_gates', health.get('summary', {}).get('track_gates', 0)))}; "
            f"KPI/watchlist gates: {_fmt_int(health.get('summary', {}).get('kpi_watchlist_gates', 0))}",
            "KPI split: "
            f"foundation blockers {kpi_by_id.get('foundation_blockers', {}).get('display_value', 'not loaded')}; "
            f"P0 audit net {kpi_by_id.get('p0_audit_net', {}).get('display_value', 'not loaded')}; "
            f"P0 live gate drivers {kpi_by_id.get('p0_live_gate_drivers', {}).get('display_value', 'not loaded')}",
            runtime.get("measurement_gap_vs_quality_failure") or runtime.get("executive_read", ""),
            testing.get("executive_read") or testing.get("why_it_matters", ""),
            graph.get("executive_read", ""),
            f"Action rows emitted: {_fmt_int(len(actions))}",
        ]
        rendered_decision_gates = decision_gate_rows
    return build_bcg_brief(
        title="BCG Executive Brief",
        status=verdict,
        status_label="Decision status",
        secondary_statuses={},
        business_read=business_read,
        technical_read=technical_read,
        decision_gates=rendered_decision_gates,
        priority_rule=priority_rule.replace("accepted debt", "owned burn-down debt").replace("ratchets", "owned burn-down backlog"),
        priority_rows=priority_rows,
        why_this_order=why_this_order,
        next_step=(
            (
                f"{priority_rows[0].get('move')}; rerun ADG and repair graph/report consistency before lower-severity ranking."
                if priority_rows
                else "Repair graph/report consistency before lower-severity ranking."
            )
            if verdict == "REPORT_INCONSISTENT"
            else "Restore required report inputs first."
            if verdict == "DEGRADED"
            else "Fix failing runtime proof first."
            if verdict == "RUNTIME_PROOF_FAILING"
            else (
                (actions[0].get("action") if actions else "Follow the next-best-actions table below.")
                if actions
                else "Follow the next-best-actions table below."
            )
        ),
        table_limit=4,
    )


def _compact_key_findings(doc: dict[str, Any]) -> list[list[Any]]:
    health = doc.get("lens_1_health_gates") or {}
    scorecard = doc.get("kpi_scorecard") or doc.get("p0_p3_reconciliation") or {}
    kpis = {str(row.get("id") or ""): row for row in scorecard.get("kpis", []) or []}
    p0 = doc.get("lens_0_p0_landmines") or {}
    runtime = doc.get("lens_2_runtime_proof_observability") or {}
    product = doc.get("lens_3_product_app_risk") or {}
    testing = doc.get("lens_4_testing_control_gaps") or {}
    graph = doc.get("lens_5_graphdb_mv_decision_impact") or {}
    plan = doc.get("deprecation_deletion_plan") or {}
    consistency = ((doc.get("audit_notes") or {}).get("artifact_consistency") or {})

    red_gates = health.get("red_gates") or []
    red_finding = "No red FIX gates."
    if red_gates:
        top = red_gates[0]
        red_finding = (
            f"{top.get('gate_id')} has {_fmt_int(top.get('total_records'))} blocking row(s)."
        )

    p0_summary = p0.get("summary") or {}
    foundation_count = p0_summary.get("foundation_blockers", 0)
    foundation_finding = (
        f"{_fmt_int(foundation_count)} foundation blocker(s): "
        f"{_fmt_int(p0_summary.get('layer_violations'))} layer, "
        f"{_fmt_int(p0_summary.get('protected_surfaces'))} protected-surface."
    )

    runtime_signals = runtime.get("runtime_proof_signals") or []
    runtime_row = next((r for r in runtime_signals if str(r.get("status")) != "present"), runtime_signals[0] if runtime_signals else {})
    testing_rows = testing.get("investment_map") or []
    testing_row = testing_rows[0] if testing_rows else {}
    graph_risks = graph.get("top_graph_risks") or []
    graph_row = graph_risks[0] if graph_risks else {}
    plan_summary = plan.get("summary") or {}

    return [
        [
            "Merge blocker",
            red_finding,
        ],
        [
            "P0 ledger definitions",
            (
                f"Foundation risk inventory={kpis.get('foundation_blockers', {}).get('display_value', 'not loaded')}; "
                f"audit net backlog after exemptions={kpis.get('p0_audit_net', {}).get('display_value', 'not loaded')}; "
                f"live merge-blocking drivers={kpis.get('p0_live_gate_drivers', {}).get('display_value', 'not loaded')}."
            ),
        ],
        [
            "Report consistency",
            f"{consistency.get('status', 'unknown')}; lower-priority ordering is provisional.",
        ],
        [
            "Foundation blockers",
            foundation_finding,
        ],
        [
            "Runtime proof",
            (
                f"{runtime_row.get('signal', 'runtime proof')}: "
                f"{runtime_row.get('status', runtime.get('status', 'unknown'))}."
            ),
        ],
        [
            "Testing",
            (
                f"{testing_row.get('production_scope', 'No mapped testing hotspot promoted')} "
                f"risk={((testing_row.get('risk') or {}).get('risk_band') or 'unknown')}."
            ),
        ],
        [
            "Graph / MV",
            (
                f"{graph_row.get('scope', 'No graph hotspot promoted')} "
                f"via {graph_row.get('graph_signal', 'diagnostic signals')}."
            ),
        ],
        [
            "Product / app",
            product.get("executive_read") or "No product/app risk promoted.",
        ],
        [
            "Defer / delete",
            plan_summary.get("executive_read") or "No deletion/deprecation plan loaded.",
        ],
    ]


def _step_action(row: dict[str, Any]) -> str:
    move = str(row.get("move") or row.get("action") or row.get("scope") or "No promoted action").rstrip(".")
    next_step = str(row.get("next_step") or row.get("why_this_rank") or row.get("why_now") or "").strip()
    if move.startswith("Refactor high-blast-radius seam"):
        scope = str(row.get("scope") or "the flagged seam")
        return (
            f"After P0 is green and mapped tests are decided, open a scoped refactor/test slice for {scope} "
            "only if ADG still flags it or the P0 fix touches it."
        )
    if not next_step:
        return move
    return f"{move}. {next_step}"


def _step_exit(row: dict[str, Any]) -> str:
    explicit = row.get("done_condition")
    if explicit:
        return str(explicit)
    scope = str(row.get("scope") or "")
    if scope == "13_core_imports_apps":
        return "Post-fix ADG shows this gate green and P0 FIX=0."
    return "Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived."


def _insert_step(steps: list[dict[str, Any]], index: int, action: str, evidence: str, exit_criterion: str) -> None:
    steps.insert(index, {"action": action, "evidence": evidence, "exit": exit_criterion})


def _append_step(steps: list[dict[str, Any]], action: str, evidence: str, exit_criterion: str) -> None:
    steps.append({"action": action, "evidence": evidence, "exit": exit_criterion})


def _compact_next_steps(doc: dict[str, Any], brief: dict[str, Any] | None = None) -> list[list[Any]]:
    source_rows = list((brief or {}).get("priority_rows") or [])
    table_limit = (brief or {}).get("table_limit")
    if isinstance(table_limit, int) and table_limit >= 0:
        source_rows = source_rows[:table_limit]
    actions = source_rows or list((doc.get("canonical_next_best_actions") or {}).get("rows") or [])[:5]
    steps: list[dict[str, Any]] = []
    for row in actions:
        steps.append(
            {
                "action": _step_action(row),
                "evidence": row.get("evidence") or row.get("technical_reason") or row.get("testing_requirement"),
                "exit": _step_exit(row),
            }
        )
    decision_rows = (doc.get("gate_mece_summary") or {}).get("decision_gates") or []
    if decision_rows and not steps:
        for row in decision_rows[:2]:
            steps.append(
                {
                    "action": _step_action(row),
                    "evidence": row.get("evidence") or row.get("technical_reason"),
                    "exit": "Rerun ADG and confirm the decision gate clears.",
                }
            )
    consistency = ((doc.get("audit_notes") or {}).get("artifact_consistency") or {})
    if str(consistency.get("status") or "").upper() == "FAIL":
        _insert_step(
            steps,
            1 if steps else 0,
            "Rerun ADG after the P0 fix; if report consistency still fails, repair the report pipeline before ranking P1-P3.",
            "Report consistency=FAIL.",
            "Post-P0 ADG has report consistency PASS or an explicit waiver.",
        )
    scorecard = doc.get("kpi_scorecard") or doc.get("p0_p3_reconciliation") or {}
    kpis = {str(row.get("id") or ""): row for row in scorecard.get("kpis", []) or []}
    if kpis:
        _insert_step(
            steps,
            min(2, len(steps)),
            "Classify remaining P0 counts after the rerun: live merge drivers block merge; foundation/audit net rows become follow-up backlog unless they still appear as live FIX gates.",
            (
                f"Foundation risk inventory={kpis.get('foundation_blockers', {}).get('display_value', 'not loaded')}; "
                f"audit net backlog={kpis.get('p0_audit_net', {}).get('display_value', 'not loaded')}; "
                f"live merge drivers={kpis.get('p0_live_gate_drivers', {}).get('display_value', 'not loaded')}."
            ),
            "Receipt shows P0 FIX=0, or any remaining foundation/audit row is attached to an explicit live FIX gate.",
        )
    runtime_status = _first_runtime_status(doc)
    if runtime_status not in {"present", "unknown"}:
        _insert_step(
            steps,
            min(3, len(steps)),
            "Repair runtime proof if it is still missing or failing after the P0 rerun; do not rely on runtime evidence until it is present and passing.",
            f"runtime_spine={runtime_status}.",
            "Runtime proof is present and passing, or the receipt explicitly scopes it out of the decision.",
        )
    product = doc.get("lens_3_product_app_risk") or {}
    product_read = product.get("executive_read") or "No product/app risk promoted."
    _append_step(
        steps,
        "Do not open a separate product/app workstream; validate app-owned wiring only if the P0 adapter fix touches it.",
        product_read,
        "Touched app wiring has targeted validation, or no app-owned surface was touched.",
    )
    plan = doc.get("deprecation_deletion_plan") or {}
    plan_summary = plan.get("summary") or {}
    if plan_summary:
        _append_step(
            steps,
            "Keep deletion/deprecation cleanup after P0, report consistency, and runtime proof are green unless cleanup blocks the P0 fix.",
            plan_summary.get("executive_read") or "Cleanup signal loaded.",
            "Cleanup is scheduled as a separate after-green wave or explicitly tied to the P0 fix.",
        )
    if not steps:
        steps = [{"action": "Keep ADG green.", "evidence": "No red gate evidence.", "exit": "No red gate remains."}]
    return [[idx, row["action"], row["evidence"], row["exit"]] for idx, row in enumerate(steps, start=1)]


def _first_runtime_status(doc: dict[str, Any]) -> str:
    runtime = doc.get("lens_2_runtime_proof_observability") or {}
    signals = runtime.get("runtime_proof_signals") or []
    return str((signals[0] if signals else {}).get("status") or runtime.get("status") or "unknown")


def _first_testing_signal(doc: dict[str, Any]) -> str:
    testing = doc.get("lens_4_testing_control_gaps") or {}
    rows = testing.get("investment_map") or []
    if not rows:
        return "none promoted"
    row = rows[0]
    risk = ((row.get("risk") or {}).get("risk_band") or "unknown")
    return f"{row.get('production_scope', 'unknown')}; risk={risk}"


def _p0_action_queue_metric(doc: dict[str, Any]) -> str:
    return str((doc.get("p0_action_queue_summary") or {}).get("metric") or "no P0 action-queue rows")


def _first_fix_gate_metric(doc: dict[str, Any], brief: dict[str, Any]) -> str:
    health = doc.get("lens_1_health_gates") or {}
    gates = {str(row.get("gate_id") or ""): row for row in health.get("red_gates", []) or []}
    scope = ""
    row: dict[str, Any] = {}
    for candidate in brief.get("priority_rows") or []:
        candidate_scope = str(candidate.get("scope") or "")
        if candidate_scope in gates:
            scope = candidate_scope
            row = gates[candidate_scope]
            break
    if not row and gates:
        scope, row = next(iter(gates.items()))
    if not row:
        return "none"
    count = _fmt_int(row.get("total_records") or row.get("records") or row.get("violation_count") or 0)
    return f"{scope}; rows={count}"


def _adg_run_metrics(doc: dict[str, Any], brief: dict[str, Any]) -> list[list[Any]]:
    health = doc.get("lens_1_health_gates") or {}
    summary = health.get("summary") or {}
    consistency = ((doc.get("audit_notes") or {}).get("artifact_consistency") or {})
    actions = (doc.get("canonical_next_best_actions") or {}).get("rows") or []
    raw_inputs = doc.get("raw_inputs") or {}
    artifacts = raw_inputs.get("artifacts") or {}
    scorecard = doc.get("kpi_scorecard") or doc.get("p0_p3_reconciliation") or {}
    kpis = {str(row.get("id") or ""): row for row in scorecard.get("kpis", []) or []}
    return [
        ["Run ID", (doc.get("run") or {}).get("run_id") or "unknown"],
        ["Snapshot", (doc.get("run") or {}).get("snapshot_ts") or "unknown"],
        ["SQLite snapshot", artifacts.get("sqlite_snapshot") or "unknown"],
        ["Audit caveat", f"{(doc.get('executive_decision') or {}).get('verdict') or 'UNKNOWN'}; report consistency={consistency.get('status') or 'unknown'}"],
        ["FIX gates (all bands)", _fmt_int(summary.get("fix_gates", 0))],
        ["Live P0 gate drivers", _display_count(_kpi_int(doc, "p0_live_gate_drivers"))],
        ["P0 action queue", _p0_action_queue_metric(doc)],
        ["Top FIX gate", _first_fix_gate_metric(doc, brief)],
        ["Action rows", _fmt_int(len(actions))],
        [
            "P0 ledgers",
            (
                f"foundation risk inventory={kpis.get('foundation_blockers', {}).get('display_value', 'not loaded')}; "
                f"audit net backlog={kpis.get('p0_audit_net', {}).get('display_value', 'not loaded')}; "
                f"live merge drivers={kpis.get('p0_live_gate_drivers', {}).get('display_value', 'not loaded')}"
            ),
        ],
        ["Runtime proof", _first_runtime_status(doc)],
        ["Testing hotspot", _first_testing_signal(doc)],
    ]


def _p0_p3_severity_inventory(doc: dict[str, Any]) -> list[list[Any]]:
    scorecard = doc.get("kpi_scorecard") or doc.get("p0_p3_reconciliation") or {}
    rows = scorecard.get("p0_p3_audit_inventory") or []
    if not rows:
        return [["P0", "not loaded", "not loaded", "not loaded", "not loaded", "not loaded"]]
    out: list[list[Any]] = []
    for row in rows:
        out.append(
            [
                row.get("band"),
                _display_count(row.get("audit_gross")),
                _display_count(row.get("guardian_exempted")),
                _display_count(row.get("audit_net")),
                row.get("foundation_blockers_display") or _display_count(row.get("foundation_blockers")),
                _display_count(row.get("live_gate_drivers")),
            ]
        )
    return out


def _executive_decision_rows(doc: dict[str, Any], brief: dict[str, Any]) -> list[list[Any]]:
    first = (brief.get("priority_rows") or [{}])[0]
    scope = str(first.get("scope") or "none")
    move = str(first.get("move") or first.get("action") or "No immediate action promoted")
    next_step = str(first.get("next_step") or brief.get("next_step") or "No next step promoted")
    health = doc.get("lens_1_health_gates") or {}
    gates = {str(row.get("gate_id") or ""): row for row in health.get("red_gates", []) or []}
    row = gates.get(scope, {})
    count = _fmt_int(row.get("total_records") or row.get("records") or row.get("violation_count") or 0)
    consistency = (((doc.get("audit_notes") or {}).get("artifact_consistency") or {}).get("status") or "unknown")
    p0_summary = doc.get("p0_action_queue_summary") or {}
    p0_queue_count = _int_value(p0_summary.get("total_p0_rows"))
    p0_live_drivers = _kpi_int(doc, "p0_live_gate_drivers")
    foundation_blockers = _kpi_int(doc, "foundation_blockers")
    if p0_live_drivers > 0:
        merge_status = "No. A live P0 gate driver is red."
    elif p0_queue_count > 0 or foundation_blockers > 0:
        merge_status = "No. ADG is red and P0 foundation/wave work remains before lower-severity lanes."
    elif gates:
        merge_status = "No. ADG has a red FIX gate."
    else:
        merge_status = "No. ADG report consistency/runtime proof is not decision-grade." if str(consistency).upper() == "FAIL" else "Yes, if no external release gate is red."
    if p0_queue_count > 0:
        p0_detail = str(p0_summary.get("metric") or "P0 action queue has rows.")
        non_p0_fix = _first_fix_gate_metric(doc, brief)
        blocker = f"{p0_detail}. Live P0 gate drivers={_display_count(p0_live_drivers)}; top red FIX gate={non_p0_fix}."
    elif scope == "13_core_imports_apps":
        blocker = f"`{scope}`: `agentic_core` imports `apps_*` in {count} row(s), violating the core/app boundary."
    elif gates:
        blocker = f"`{scope}` has {count} blocking row(s)."
    else:
        blocker = f"Report consistency is {consistency}; no red P0 live gate driver is present."
    return [
        ["Can we merge?", merge_status],
        ["What blocks merge?", blocker],
        ["First engineering move", f"{move}. {next_step}"],
        ["What waits?", "P1-P3 work, ratchets, dead-code cleanup, and broad graph ranking."],
        ["Audit caveat", f"Report consistency is {consistency}; this makes lower-priority ranking provisional, but does not change the P0 decision."],
    ]


def render_bcg_inline_markdown(doc: dict[str, Any]) -> str:
    """Render a compact executive markdown brief for inline chat."""
    lines: list[str] = []
    a = lines.append
    a("## ADG Executive Brief")
    a("")
    brief = _executive_bcg_brief(doc)
    a(_table(["Question", "Answer"], _executive_decision_rows(doc, brief)))
    a("")
    a("Decision gate:")
    a("")
    a(
        _table(
            ["Gate", "Status", "Evidence", "Required before ranking"],
            [
                ["Merge decision", row[1], row[0], "Resolve before lower-severity ranking."]
                for row in _executive_decision_rows(doc, brief)
            ],
        )
    )
    a("")
    a("Fix now:")
    a("")
    a(_table(["Rank", "Move", "Evidence", "Exit criterion"], _compact_next_steps(doc, brief)))
    a("")
    a("ADG Run Metrics")
    a("")
    a(_table(["Metric", "Value"], _adg_run_metrics(doc, brief)))
    a("")
    a("P0-P3 Severity Inventory")
    a("")
    a(_table(["Band", "Gross", "Guardian exempted", "Net", "Foundation blockers", "Live gate drivers"], _p0_p3_severity_inventory(doc)))
    a("")
    a("### Recommended Next Steps")
    a("")
    a(_table(["Priority", "Action", "Evidence", "Exit criterion"], _compact_next_steps(doc, brief)))
    a("")
    markdown = "\n".join(lines)
    _validate_locked_bcg_inline_markdown(markdown)
    return markdown


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
        return (0 if doc["run"].get("emit_status") != "FAIL" else 2), json_path
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
