"""apps_* completeness review combining AST stub-scan + ADG enrichment.

Outputs JSON + Markdown summarizing per-app:
  - file_count, py_file_count
  - stub_function_count (NotImplementedError / pass-only / ellipsis-only / TODO docstring)
  - total_function_count
  - stub_pct
  - zero_caller_node_count (from ADG mv_zero_caller_modules-style query)
  - layer breakdown
"""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import ast
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

REPO = Path(".")


def _select_snapshot() -> Path:
    """Pick the most recent ADG snapshot that contains the gap-MVs.

    "Lite" snapshots from quick regenerations skip the gap-MV stage and
    have only 4 MVs (mv_critical_path_segments, mv_edges_*). Those
    snapshots break the gap-counting probes — fall back to the most
    recent snapshot that has `mv_task_contract_gaps` (a witness MV
    for the full set).
    """
    snaps = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
    if not snaps:
        return Path("artifacts/adg/adg_indexed_05022026_1651.sqlite")
    for snap in reversed(snaps):
        try:
            con = sqlite3.connect(str(snap))
            cur = con.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
                "AND name = 'mv_task_contract_gaps'"
            )
            if cur.fetchone():
                con.close()
                return snap
            con.close()
        except sqlite3.OperationalError:
            continue
    return snaps[-1]


SNAP = _select_snapshot()
APPS = [p for p in REPO.iterdir() if p.is_dir() and p.name.startswith("apps_")]


def is_stub_body(body: list[ast.stmt]) -> str | None:
    """Return stub kind label or None."""
    # Strip docstring
    stmts = body
    if stmts and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, ast.Constant) and isinstance(stmts[0].value.value, str):
        doc = stmts[0].value.value
        rest = stmts[1:]
        if not rest:
            return "docstring_only"
        if "TODO" in doc.upper() or "STUB" in doc.upper() or "NOT IMPLEMENTED" in doc.upper():
            stmts = rest  # treat docstring marker as hint
            # fall through
        else:
            stmts = rest
    if len(stmts) == 1:
        s = stmts[0]
        if isinstance(s, ast.Pass):
            return "pass_only"
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis:
            return "ellipsis_only"
        if isinstance(s, ast.Raise):
            exc = s.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                return "raise_notimpl"
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return "raise_notimpl"
        if isinstance(s, ast.Return) and (s.value is None or (isinstance(s.value, ast.Constant) and s.value.value is None)):
            return "return_none_only"
    return None


def scan_app(app_dir: Path) -> dict:
    py_files = sorted(app_dir.rglob("*.py"))
    funcs_total = 0
    funcs_stub = 0
    stub_breakdown: dict[str, int] = defaultdict(int)
    stub_examples: list[tuple[str, str, int, str]] = []  # (file, name, line, kind)
    todo_files: list[str] = []
    parse_failures: list[str] = []
    for py in py_files:
        try:
            src = py.read_text(encoding="utf-8")
        except Exception as e:
            parse_failures.append(f"{py}: {e}")
            continue
        if "TODO" in src.upper() or "FIXME" in src.upper():
            todo_files.append(str(py))
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            parse_failures.append(f"{py}: SyntaxError {e}")
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs_total += 1
                k = is_stub_body(n.body)
                if k:
                    funcs_stub += 1
                    stub_breakdown[k] += 1
                    if len(stub_examples) < 20:
                        stub_examples.append((str(py.relative_to(REPO)), n.name, n.lineno, k))
    return {
        "app": app_dir.name,
        "py_files": len(py_files),
        "funcs_total": funcs_total,
        "funcs_stub": funcs_stub,
        "stub_pct": round(100 * funcs_stub / funcs_total, 1) if funcs_total else 0.0,
        "stub_breakdown": dict(stub_breakdown),
        "stub_examples": stub_examples,
        "todo_file_count": len(todo_files),
        "parse_failures": parse_failures,
    }


def adg_enrich(con: sqlite3.Connection, app: str) -> dict:
    cur = con.cursor()
    like = f"{app}/%"
    # node count + zero-caller
    cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE ?", (like,)
    )
    nodes_total = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*) FROM nodes n
        WHERE n.resolved_path LIKE ?
          AND n.entity_type IN ('function', 'method', 'class')
          AND NOT EXISTS (
            SELECT 1 FROM edges e
            WHERE e.dst_id = n.id AND e.relation_type IN ('imports','calls','resolves_callsite')
          )
        """,
        (like,),
    )
    zero_caller = cur.fetchone()[0]
    cur.execute(
        "SELECT layer, COUNT(*) FROM nodes WHERE resolved_path LIKE ? GROUP BY layer ORDER BY 2 DESC",
        (like,),
    )
    by_layer = {r[0]: r[1] for r in cur.fetchall()}
    # gaps from mv_*
    # mv_prompt_assembly_wiring_gaps keys on `target_file`, not `file` —
    # other MVs use `file`. Per-MV column resolution avoids -1 sentinel.
    gaps: dict[str, int] = {}
    for mv, label, col in [
        ("mv_task_contract_gaps", "task_contract_gaps", "file"),
        ("mv_structured_output_gaps", "structured_output_gaps", "file"),
        ("mv_prompt_assembly_wiring_gaps", "prompt_assembly_gaps", "target_file"),
        ("mv_replay_surface_gaps", "replay_surface_gaps", "file"),
        ("mv_trace_replay_eval_gaps", "trace_replay_eval_gaps", "file"),
    ]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {mv} WHERE {col} LIKE ?", (like,))
            gaps[label] = cur.fetchone()[0]
        except sqlite3.OperationalError:
            gaps[label] = -1
    # violations on this app
    try:
        cur.execute(
            "SELECT severity, COUNT(*) FROM violations WHERE file_path LIKE ? GROUP BY severity",
            (like,),
        )
        viol = {r[0] or "unknown": r[1] for r in cur.fetchall()}
    except sqlite3.OperationalError:
        viol = {}
    return {
        "adg_nodes": nodes_total,
        "adg_zero_caller_funcs": zero_caller,
        "adg_layers": by_layer,
        "adg_gaps": gaps,
        "adg_violations_by_severity": viol,
    }


def _load_real_gaps_by_app() -> tuple[dict[str, int], set[str]]:
    """Return ({app_name: real_gap_count}, {audited_apps}).

    Plan ``apps-shared-stub-audit-7dfe16`` W4 enrichment. The second
    set carries which apps have been audited so callers can distinguish
    "audited, zero gaps" (show ``0``) from "not audited" (show ``?``).
    """
    census_path = Path("artifacts/analysis/apps_shared_stub_census.json")
    if not census_path.exists():
        return {}, set()
    try:
        payload = json.loads(census_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, set()
    counts: dict[str, int] = defaultdict(int)
    audited: set[str] = set()
    for stub in payload.get("stubs", ()):
        fp = stub.get("file_path", "")
        # "apps_shared/x/y.py" → "apps_shared"
        app = fp.split("/", 1)[0] if "/" in fp else fp
        audited.add(app)
        if stub.get("category") == "RealGap":
            counts[app] += 1
    return dict(counts), audited


def main() -> None:
    with sqlite3.connect(str(SNAP)) as con:
        results = []
        for app in sorted(APPS):
            s = scan_app(app)
            s.update(adg_enrich(con, app.name))
            results.append(s)
        real_gaps_by_app, audited_apps = _load_real_gaps_by_app()
        out = {
            "snapshot": str(SNAP),
            "apps": results,
            "real_gaps_by_app": real_gaps_by_app,
            "audited_apps": sorted(audited_apps),
        }
        Path("artifacts/analysis").mkdir(parents=True, exist_ok=True)
        Path("artifacts/analysis/apps_completeness_review.json").write_text(
            json.dumps(out, indent=2, default=str), encoding="utf-8"
        )
        lines = []
        lines.append(
            "| App | Files | Funcs | Stubs | Stub% | RealGaps | NotImpl | Pass | Ellipsis | RetNone | DocOnly | ADG Nodes | Zero-Caller | TaskGap | StructGap | PromptGap | ReplayGap | TraceGap | TODO Files |"
        )
        lines.append(
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
        )
        for r in results:
            b = r["stub_breakdown"]
            g = r["adg_gaps"]
            if r["app"] in audited_apps:
                real_gaps = real_gaps_by_app.get(r["app"], 0)
            else:
                real_gaps = "?"
            lines.append(
                f"| {r['app']} | {r['py_files']} | {r['funcs_total']} | {r['funcs_stub']} | {r['stub_pct']} | "
                f"{real_gaps} | "
                f"{b.get('raise_notimpl',0)} | {b.get('pass_only',0)} | {b.get('ellipsis_only',0)} | "
                f"{b.get('return_none_only',0)} | {b.get('docstring_only',0)} | "
                f"{r['adg_nodes']} | {r['adg_zero_caller_funcs']} | "
                f"{g.get('task_contract_gaps','-')} | {g.get('structured_output_gaps','-')} | "
                f"{g.get('prompt_assembly_gaps','-')} | {g.get('replay_surface_gaps','-')} | "
                f"{g.get('trace_replay_eval_gaps','-')} | {r['todo_file_count']} |"
            )
        Path("artifacts/analysis/apps_completeness_review.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        print("\n".join(lines))


if __name__ == "__main__":
    main()
