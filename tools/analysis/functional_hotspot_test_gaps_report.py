"""Generate functional hotspot test-gap report.

This report is the contract-first companion to the existing structural hotspot
reports. It intentionally does not treat basename matches, imports, or ADG
test-reachability edges as functional coverage.

Usage:
    python tools/analysis/functional_hotspot_test_gaps_report.py
    python tools/analysis/functional_hotspot_test_gaps_report.py --app apps_rg --top 50
    python tools/analysis/functional_hotspot_test_gaps_report.py --execution-report pytest_report.json
"""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import argparse
import ast
import fnmatch
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "test_inventory" / "functional_hotspot_test_gaps.md"
ARCHIVE_MARKER = "_archived_obsolete"


@dataclass(frozen=True)
class RequiredTestGroup:
    group_id: str
    description: str
    nodeid_terms: tuple[str, ...]


@dataclass(frozen=True)
class FunctionalContract:
    contract_id: str
    app: str
    section_id: str
    description: str
    hotspot_globs: tuple[str, ...]
    nodeid_scope_terms: tuple[str, ...]
    required_groups: tuple[RequiredTestGroup, ...]


DEFAULT_CONTRACTS: tuple[FunctionalContract, ...] = (
    FunctionalContract(
        contract_id="apps_rg.executive_summary.functional_chain",
        app="apps_rg",
        section_id="executive_summary",
        description="Executive summary same-run proof chain, evidence authority, X2, and X1D gates.",
        hotspot_globs=(
            "apps_rg/runtime/sections/executive_summary*.py",
            "apps_rg/runtime/validators/executive_summary*.py",
            "apps_rg/runtime/judges/executive_summary*.py",
            "apps_rg/fact_inventory/exec_summary*.py",
        ),
        nodeid_scope_terms=("executive_summary", "exec_summary"),
        required_groups=(
            RequiredTestGroup("section_runtime", "section lane or runtime behavior", ("executive_summary_lane", "executive_summary_section", "exec_summary")),
            RequiredTestGroup("proof_authority", "proof-pool/evidence authority", ("proof_pool", "evidence_capsule", "allowed_fact", "source_fact", "proof_authority")),
            RequiredTestGroup("x2_gate", "deterministic X2 gate", ("x2", "product_shape", "composition")),
            RequiredTestGroup("x1d_or_judge", "judge/X1D arbitration", ("x1d", "judge")),
        ),
    ),
    FunctionalContract(
        contract_id="apps_rg.headline.functional_chain",
        app="apps_rg",
        section_id="headline",
        description="Headline positioning, graph evidence binding, X2, and judge gate.",
        hotspot_globs=(
            "apps_rg/runtime/sections/headline*.py",
            "apps_rg/runtime/validators/headline*.py",
            "apps_rg/runtime/judges/headline*.py",
        ),
        nodeid_scope_terms=("headline",),
        required_groups=(
            RequiredTestGroup("section_runtime", "headline section behavior", ("headline_lane", "headline_section", "headline")),
            RequiredTestGroup("graph_binding", "graph/plan evidence binding", ("graph", "planmatch", "skilltext", "evidence")),
            RequiredTestGroup("x2_gate", "deterministic X2 gate", ("x2", "quality_x2", "positioning")),
            RequiredTestGroup("x1d_or_judge", "judge/X1D arbitration", ("x1d", "judge")),
        ),
    ),
    FunctionalContract(
        contract_id="apps_rg.competencies.functional_chain",
        app="apps_rg",
        section_id="competencies",
        description="Competencies graph traversal, proof-pool authority, and deterministic rigor gates.",
        hotspot_globs=(
            "apps_rg/runtime/sections/competencies*.py",
            "apps_rg/runtime/validators/competencies*.py",
            "apps_rg/runtime/judges/competencies*.py",
            "apps_rg/fact_inventory/competencies*.py",
        ),
        nodeid_scope_terms=("competencies", "competency"),
        required_groups=(
            RequiredTestGroup("section_runtime", "competencies section behavior", ("competencies", "competency")),
            RequiredTestGroup("graph_traversal", "graph traversal/proof pool", ("graph", "proof_pool", "capability_bundle")),
            RequiredTestGroup("x2_gate", "deterministic X2/rigor gate", ("x2", "rigor", "proof_quality")),
        ),
    ),
    FunctionalContract(
        contract_id="apps_rg.role_episode.functional_chain",
        app="apps_rg",
        section_id="role_episode_sections",
        description="Role-episode bullets/narratives consume eligible graph evidence and section-scoped proof.",
        hotspot_globs=(
            "apps_rg/runtime/sections/role_episode*.py",
            "apps_rg/runtime/sections/graph_role_episode*.py",
            "apps_rg/runtime/sections/unify_*.py",
            "apps_rg/runtime/sections/ibm_*.py",
            "apps_rg/runtime/sections/insurtech_*.py",
            "apps_rg/runtime/sections/ey_*.py",
            "apps_rg/runtime/validators/*narrative*.py",
            "apps_rg/runtime/validators/*bullet*.py",
        ),
        nodeid_scope_terms=("role_episode", "unify", "ibm", "insurtech", "ey", "bullet", "narrative"),
        required_groups=(
            RequiredTestGroup("section_runtime", "bullet or narrative section behavior", ("role_episode", "bullets", "narrative", "section")),
            RequiredTestGroup("graph_authority", "eligible graph evidence authority", ("graph", "proof", "authority", "allowed_fact")),
            RequiredTestGroup("x2_or_judge", "X2 or judge gate", ("x2", "x1d", "judge")),
            RequiredTestGroup("same_run_binding", "same-run companion artifact binding", ("fingerprint", "companion", "finalization", "aggregation")),
        ),
    ),
    FunctionalContract(
        contract_id="apps_rg.final_aggregation.functional_chain",
        app="apps_rg",
        section_id="final_aggregation",
        description="Final aggregation uses explicit same-run receipts rather than latest-successful inference.",
        hotspot_globs=(
            "apps_rg/runtime/aggregation/*.py",
            "apps_rg/runtime/internal/generated_lane_rollup.py",
            "apps_rg/l2_recipe/modular_lane_adapter.py",
            "apps_rg/l2_recipe/modular_resume_generation.py",
        ),
        nodeid_scope_terms=("aggregation", "final_resume", "aggregate", "modular"),
        required_groups=(
            RequiredTestGroup("aggregation_contract", "final aggregation behavior", ("aggregation", "final_resume", "aggregate")),
            RequiredTestGroup("same_run_fingerprint", "same-run fingerprint binding", ("fingerprint", "current_run", "same_run")),
            RequiredTestGroup("no_latest_successful", "no latest-successful inference", ("latest_successful", "no_latest", "manifest")),
        ),
    ),
)


def _resolve_snapshot(adg: Path | None) -> Path:
    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.exists():
            raise FileNotFoundError(f"ADG_SNAPSHOT not found: {p}")
        return p.resolve()
    if adg is not None:
        p = adg if adg.is_absolute() else REPO_ROOT / adg
        if not p.exists():
            raise FileNotFoundError(f"--adg not found: {p}")
        return p.resolve()
    candidates = [
        c
        for c in ADG_DIR.glob("adg_indexed_*.sqlite")
        if "99999999" not in c.name and c.stat().st_size > 50_000_000
    ]
    if not candidates:
        raise FileNotFoundError("no adg_indexed_*.sqlite under artifacts/adg/")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _table_exists(con: sqlite3.Connection, table: str) -> bool:
    row = con.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def _read_hotspots(con: sqlite3.Connection, *, app: str, top: int) -> list[dict[str, Any]]:
    if not _table_exists(con, "mv_hotspot_coverage_risk"):
        return []
    prefix = f"{app}/%"
    rows = con.execute(
        """
        SELECT file, layer, priority_band, risk_band, coverage_band, coverage_pct,
               criticality_score, combined_risk_score, fan_in, fan_out, violation_count
        FROM mv_hotspot_coverage_risk
        WHERE file LIKE ?
        ORDER BY
          CASE priority_band
            WHEN 'P1_URGENT' THEN 0
            WHEN 'P2_GAP' THEN 1
            WHEN 'P3_OK' THEN 2
            WHEN 'P4_LOW' THEN 3
            ELSE 4
          END,
          criticality_score DESC,
          combined_risk_score DESC,
          file ASC
        LIMIT ?
        """,
        (prefix, int(top)),
    ).fetchall()
    return [dict(row) for row in rows]


def _read_structural_reachability(con: sqlite3.Connection, *, app: str) -> dict[str, dict[str, Any]]:
    if not (_table_exists(con, "edges") and _table_exists(con, "nodes")):
        return {}
    prefix = f"{app}/%.py"
    rows = con.execute(
        """
        SELECT dst.resolved_path AS path,
               COUNT(*) AS edge_count,
               COUNT(DISTINCT e.source_file) AS test_count
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type IN ('covers', 'imports')
          AND e.source_file LIKE 'tests/%'
          AND dst.resolved_path LIKE ?
        GROUP BY dst.resolved_path
        """,
        (prefix,),
    ).fetchall()
    return {
        str(row["path"]): {
            "test_reachability_edges": int(row["edge_count"] or 0),
            "structural_test_count": int(row["test_count"] or 0),
        }
        for row in rows
    }


def _read_meta_commit(con: sqlite3.Connection) -> str:
    if not _table_exists(con, "meta"):
        return "unknown"
    row = con.execute("SELECT value FROM meta WHERE key='commit_sha' LIMIT 1").fetchone()
    return str(row[0]) if row else "unknown"


def read_adg_inputs(snapshot: Path, *, app: str, top: int) -> dict[str, Any]:
    con = sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        return {
            "snapshot": snapshot,
            "commit_sha": _read_meta_commit(con),
            "hotspots": _read_hotspots(con, app=app, top=top),
            "structural_reachability": _read_structural_reachability(con, app=app),
            "missing_hotspot_mv": not _table_exists(con, "mv_hotspot_coverage_risk"),
        }
    finally:
        con.close()


def collect_pytest_nodeids(tests_root: Path) -> list[str]:
    if not tests_root.exists():
        return []
    nodeids: list[str] = []
    for path in sorted(tests_root.rglob("test_*.py")):
        if ARCHIVE_MARKER in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = path.relative_to(tests_root.parent).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                nodeids.append(f"{rel}::{node.name}")
            elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                        nodeids.append(f"{rel}::{node.name}::{child.name}")
    return nodeids


def load_execution_results(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("tests"), list):
        results: dict[str, str] = {}
        for row in payload["tests"]:
            if not isinstance(row, dict):
                continue
            nodeid = str(row.get("nodeid") or row.get("id") or "").strip()
            outcome = str(row.get("outcome") or row.get("result") or row.get("status") or "").strip()
            if nodeid:
                results[nodeid] = outcome or "unknown"
        return results
    if isinstance(payload, dict):
        return {str(k): str(v) for k, v in payload.items()}
    raise ValueError(f"Unsupported execution report shape: {path}")


def _contracts_for_path(path: str, contracts: tuple[FunctionalContract, ...]) -> list[FunctionalContract]:
    normalized = path.replace("\\", "/")
    return [
        contract
        for contract in contracts
        if any(fnmatch.fnmatch(normalized, pattern) for pattern in contract.hotspot_globs)
    ]


def _nodeids_for_group(nodeids: list[str], contract: FunctionalContract, group: RequiredTestGroup) -> list[str]:
    lowered_terms = tuple(term.lower() for term in group.nodeid_terms)
    scope_terms = tuple(term.lower() for term in contract.nodeid_scope_terms)
    return [
        nodeid
        for nodeid in nodeids
        if any(scope in nodeid.lower() for scope in scope_terms)
        and any(term in nodeid.lower() for term in lowered_terms)
    ]


def _execution_status(matched_nodeids: list[str], execution_results: dict[str, str]) -> tuple[str, list[str]]:
    if not matched_nodeids:
        return "not_collected", []
    if not execution_results:
        return "not_proven", matched_nodeids
    missing = [nodeid for nodeid in matched_nodeids if nodeid not in execution_results]
    failed = [
        nodeid
        for nodeid in matched_nodeids
        if execution_results.get(nodeid, "").lower() not in {"passed", "pass", "success", "ok"}
    ]
    if failed:
        return "failed", failed
    if missing:
        return "partial_execution", missing
    return "passed", []


def _gap_type(
    *,
    contracts: list[FunctionalContract],
    structural_test_count: int,
    missing_groups: list[str],
    execution_status: str,
) -> str:
    if not contracts:
        return "structural_only" if structural_test_count else "missing_mapping"
    if missing_groups:
        return "not_collected"
    if execution_status in {"not_proven", "partial_execution"}:
        return "not_run"
    if execution_status == "failed":
        return "failing"
    if execution_status == "passed":
        return "passing"
    return "unknown"


def analyze_hotspots(
    hotspots: list[dict[str, Any]],
    *,
    nodeids: list[str],
    structural_reachability: dict[str, dict[str, Any]],
    execution_results: dict[str, str],
    contracts: tuple[FunctionalContract, ...] = DEFAULT_CONTRACTS,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for hotspot in hotspots:
        file_path = str(hotspot.get("file") or hotspot.get("path") or "")
        path_contracts = _contracts_for_path(file_path, contracts)
        structural = structural_reachability.get(file_path, {})
        structural_test_count = int(structural.get("structural_test_count") or 0)
        structural_edges = int(structural.get("test_reachability_edges") or 0)
        if not path_contracts:
            rows.append(
                {
                    **hotspot,
                    "file": file_path,
                    "contract_id": "",
                    "section_id": "",
                    "gap_type": _gap_type(
                        contracts=[],
                        structural_test_count=structural_test_count,
                        missing_groups=[],
                        execution_status="not_applicable",
                    ),
                    "structural_test_count": structural_test_count,
                    "test_reachability_edges": structural_edges,
                    "required_groups": [],
                    "missing_groups": [],
                    "matched_nodeids": [],
                    "execution_status": "not_applicable",
                    "execution_evidence": [],
                }
            )
            continue
        for contract in path_contracts:
            matched_by_group: dict[str, list[str]] = {
                group.group_id: _nodeids_for_group(nodeids, contract, group)
                for group in contract.required_groups
            }
            missing_groups = [
                group_id
                for group_id, matches in matched_by_group.items()
                if not matches
            ]
            matched_nodeids = sorted({nodeid for matches in matched_by_group.values() for nodeid in matches})
            exec_status, exec_evidence = _execution_status(matched_nodeids, execution_results)
            rows.append(
                {
                    **hotspot,
                    "file": file_path,
                    "contract_id": contract.contract_id,
                    "section_id": contract.section_id,
                    "gap_type": _gap_type(
                        contracts=[contract],
                        structural_test_count=structural_test_count,
                        missing_groups=missing_groups,
                        execution_status=exec_status,
                    ),
                    "structural_test_count": structural_test_count,
                    "test_reachability_edges": structural_edges,
                    "required_groups": [group.group_id for group in contract.required_groups],
                    "missing_groups": missing_groups,
                    "matched_nodeids": matched_nodeids,
                    "execution_status": exec_status,
                    "execution_evidence": exec_evidence,
                }
            )
    return rows


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _short_list(values: list[str], *, limit: int = 3) -> str:
    if not values:
        return ""
    shown = values[:limit]
    suffix = f"; +{len(values) - limit} more" if len(values) > limit else ""
    return "; ".join(shown) + suffix


def render_report(
    rows: list[dict[str, Any]],
    *,
    snapshot: Path,
    commit_sha: str,
    app: str,
    execution_report: Path | None,
    missing_hotspot_mv: bool = False,
) -> str:
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = []
    a = lines.append
    a("# Functional Hotspot Test Gap Report")
    a("")
    a(f"ADG Provenance: backend=sqlite, snapshot={snapshot.name}")
    a(f"Generated: {generated}")
    a(f"Commit SHA: `{commit_sha}`")
    a(f"App scope: `{app}`")
    a(f"Execution report: `{execution_report}`" if execution_report else "Execution report: _not provided_")
    a("")
    a(
        "> This report does not count basename matches, imports, or ADG test-reachability "
        "edges as functional coverage. Functional PASS requires required contract test "
        "groups to be collected and execution evidence to show they passed."
    )
    a("")
    if missing_hotspot_mv:
        a("## Missing ADG Hotspot MV")
        a("")
        a("`mv_hotspot_coverage_risk` was not present in the selected ADG snapshot.")
        a("")
        return "\n".join(lines) + "\n"

    a("## Summary")
    a("")
    a(f"- Hotspot rows analyzed: {len(rows)}")
    for gap, count in _count_by(rows, "gap_type").items():
        a(f"- `{gap}`: {count}")
    a("")
    a("## Hotspot Functional Gaps")
    a("")
    a(
        "| Gap | Priority | Hotspot | Section | Contract | Structural tests | "
        "Missing functional groups | Execution | Matched nodeids |"
    )
    a("|---|---|---|---|---|---:|---|---|---|")
    for row in rows:
        a(
            f"| `{row['gap_type']}` | `{row.get('priority_band', '')}` | `{row['file']}` | "
            f"`{row.get('section_id') or ''}` | `{row.get('contract_id') or ''}` | "
            f"{row.get('structural_test_count', 0)} | "
            f"{_short_list(row.get('missing_groups') or [], limit=6) or '-'} | "
            f"`{row.get('execution_status') or ''}` | "
            f"{_short_list(row.get('matched_nodeids') or [], limit=3) or '-'} |"
        )
    if not rows:
        a("| _(none)_ | - | - | - | - | 0 | - | - | - |")
    a("")
    a("## Gap Type Definitions")
    a("")
    a("- `missing_mapping`: hotspot has no functional contract mapping.")
    a("- `structural_only`: ADG sees structural tests, but no functional contract mapping exists.")
    a("- `not_collected`: a functional contract exists, but one or more required test groups has no collected nodeid.")
    a("- `not_run`: required groups are collected, but the execution report is missing or incomplete.")
    a("- `failing`: required nodeids were executed and at least one did not pass.")
    a("- `passing`: required groups were collected and all matched nodeids passed in the execution report.")
    a("")
    a("Renderer: `tools/analysis/functional_hotspot_test_gaps_report.py`.")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, rows: list[dict[str, Any]], *, snapshot: Path, commit_sha: str, app: str) -> None:
    payload = {
        "schema": "functional_hotspot_test_gaps_v1",
        "snapshot": snapshot.name,
        "commit_sha": commit_sha,
        "app": app,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "gap_type_counts": _count_by(rows, "gap_type"),
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--adg", type=Path, default=None, help="ADG snapshot path.")
    parser.add_argument("--app", default="apps_rg", help="App package to analyze.")
    parser.add_argument("--top", type=int, default=50, help="Maximum hotspot rows to analyze.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Markdown output path.")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional JSON output path.")
    parser.add_argument(
        "--execution-report",
        type=Path,
        default=None,
        help="Optional pytest JSON report or nodeid->outcome mapping.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    snapshot = _resolve_snapshot(args.adg)
    adg_inputs = read_adg_inputs(snapshot, app=args.app, top=args.top)
    nodeids = collect_pytest_nodeids(REPO_ROOT / "tests")
    execution_results = load_execution_results(args.execution_report)
    rows = analyze_hotspots(
        adg_inputs["hotspots"],
        nodeids=nodeids,
        structural_reachability=adg_inputs["structural_reachability"],
        execution_results=execution_results,
    )
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_report(
            rows,
            snapshot=snapshot,
            commit_sha=adg_inputs["commit_sha"],
            app=args.app,
            execution_report=args.execution_report,
            missing_hotspot_mv=bool(adg_inputs["missing_hotspot_mv"]),
        ),
        encoding="utf-8",
    )
    if args.json_out is not None:
        _write_json(
            args.json_out.resolve(),
            rows,
            snapshot=snapshot,
            commit_sha=adg_inputs["commit_sha"],
            app=args.app,
        )
    print(f"[functional_hotspot_test_gaps_report] snapshot={snapshot.name}")
    print(f"[functional_hotspot_test_gaps_report] hotspots={len(rows)}")
    print(f"[functional_hotspot_test_gaps_report] gap_types={_count_by(rows, 'gap_type')}")
    print(f"[functional_hotspot_test_gaps_report] wrote={out.relative_to(REPO_ROOT).as_posix() if out.is_relative_to(REPO_ROOT) else out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
