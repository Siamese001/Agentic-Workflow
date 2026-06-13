"""Debt-Overlay Enricher — post-process step for the canonical ADG generator.

This module is the upstream form of `tools/analysis/adg_overlay_detector.py`.
It accepts a path to the canonical ADG SQLite snapshot and writes additional
columns + violation rows into it, ADDITIVELY (no schema migration of existing
tables, no modification of existing rows).

Six upstream priorities (RCA `RCA_ADG_TECH_DEBT_BLINDSPOTS_2026-04-24.md`):

  U1  A1  import resolution — emit `dead_import_resolved` violations and
                              populate `nodes.body_hash` lazily for downstream
                              duplicate detection
  U2  A4  stale __all__ — emit `stale_all_export` violations
  U3  A2  ImportError stub tag — emit `import_error_fallback_stub` violations
  U4  A3  body_hash on nodes — additive ALTER TABLE, populate, build
                              `mv_module_duplicate_clusters` view
  U5  A5  module-load action call — emit `module_load_action_call` violations
                              (ADVISORY severity, architecture-decision pending)
  U6  B7  rename shim — emit `rename_shim_module` violations

All new violations land in a SIBLING table `overlay_violations` in the same
canonical SQLite snapshot. They are deliberately NOT inserted into the
canonical `violations` table because:

  1. `violations.edge_id` has a NOT NULL FK to `edges(id)`. Overlay diagnostics
     are module-level facts, not edge-level facts — they have no natural edge
     to reference.
  2. Existing CI gates that count rows in `violations` would get noisy.
  3. A separate table is easier to drop / regenerate without churn.

Downstream consumers query `overlay_violations` directly. The
`overlay_violations.violation_class` column is hard-coded to
`'overlay_enrichment'` for marker symmetry with the canonical conventions.

Severity hierarchy (new):
  HIGH      → dead_import_resolved, module_duplicate
  MEDIUM    → import_error_fallback_stub, stale_all_export
  LOW       → rename_shim_module
  ADVISORY  → namespace_pkg_import, module_load_action_call

Entry point:
    enrich(sqlite_path: Path) -> dict[str, int]

Returns a per-category insertion count for telemetry.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

# ----------------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[2]

EXCLUDE_DIRS = {
    "archives",
    "tools_graveyard_w5.12",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "_smoke_v1_coerce_e9aa09",
    ".backup",
    ".git",
    "site-packages",
    "build",
    "dist",
}
INTERNAL_TOP_PKGS = {
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "system_learning",
    "tools",
    "ops_scripts",
    "infrastructure",
    "config",
}
EMIT_CALL_RE = re.compile(r"^\s*_emit_\w+\(")
SHIM_MARKER_RE = re.compile(
    r"(Backwards Compatibility Shim|Backwards-compat alias|"
    r"compat alias|Use \w+ directly for new code|Legacy mixin|"
    r"legacy alias|deprecated alias|use [A-Z]\w+ instead)",
    re.IGNORECASE,
)
EMPTY_BODY_HASH = "da39a3ee5e6b4b0d3255bfef95601890afd80709"  # SHA-1 of "" body
EMPTY_BODY_HASH_SHORT = EMPTY_BODY_HASH[:12]


# --------------------------------------------------------------- file walking
def _iter_py_files() -> list[Path]:
    out: list[Path] = []
    for py in ROOT.rglob("*.py"):
        rel = py.relative_to(ROOT).parts
        if set(rel) & EXCLUDE_DIRS:
            continue
        out.append(py)
    return out


def _safe_read(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _safe_parse(txt: str) -> ast.Module | None:
    try:
        return ast.parse(txt)
    except SyntaxError:
        return None


# ---------------------------------------------------- import resolution (A1)
def _module_path_status(dotted: str) -> str:
    """Resolve dotted import name against disk.

    Returns: "exists" | "namespace_pkg" | "missing"
    """
    if not dotted:
        return "missing"
    top = dotted.split(".", 1)[0]
    if top not in INTERNAL_TOP_PKGS:
        try:
            spec = importlib.util.find_spec(dotted)
            return "exists" if spec else "missing"
        except (ImportError, ValueError, ModuleNotFoundError):
            return "missing"
    parts = dotted.split(".")
    base = ROOT
    last = len(parts) - 1
    saw_namespace = False
    for i, part in enumerate(parts):
        as_pkg = base / part
        as_mod = base / f"{part}.py"
        if as_pkg.is_dir():
            if (as_pkg / "__init__.py").exists():
                base = as_pkg
                continue
            saw_namespace = True
            base = as_pkg
            continue
        if i == last and as_mod.exists():
            return "namespace_pkg" if saw_namespace else "exists"
        return "missing"
    return "namespace_pkg" if saw_namespace else "exists"


# ---------------------------------------------------- AST visitor
class _DebtVisitor(ast.NodeVisitor):
    """Single-pass visitor capturing all six debt signals."""

    def __init__(self) -> None:
        self._try_stack: list[bool] = []
        self.imports: list[dict] = []
        self.fallback_stubs: list[dict] = []
        self.module_top_emit_calls: list[dict] = []

    @staticmethod
    def _handler_catches_import_error(handlers: list[ast.ExceptHandler]) -> bool:
        for h in handlers:
            t = h.type
            if t is None:
                continue
            names: list[str] = []
            if isinstance(t, ast.Name):
                names = [t.id]
            elif isinstance(t, ast.Tuple):
                names = [el.id for el in t.elts if isinstance(el, ast.Name)]
            elif isinstance(t, ast.Attribute):
                names = [t.attr]
            if any(n in {"ImportError", "ModuleNotFoundError"} for n in names):
                return True
        return False

    def visit_Try(self, node: ast.Try) -> None:
        guarded = self._handler_catches_import_error(node.handlers)
        self._try_stack.append(guarded)
        for sub in node.body:
            self.visit(sub)
        if guarded:
            for h in node.handlers:
                for stmt in h.body:
                    if isinstance(stmt, ast.ClassDef) and len(stmt.body) <= 2:
                        self.fallback_stubs.append(
                            {
                                "class": stmt.name,
                                "line": stmt.lineno,
                                "body_size": len(stmt.body),
                                "via": "class",
                            }
                        )
                    if isinstance(stmt, ast.Assign):
                        for t in stmt.targets:
                            if isinstance(t, ast.Name) and isinstance(stmt.value, ast.Call):
                                fn = stmt.value.func
                                if isinstance(fn, ast.Name) and fn.id.startswith("_missing"):
                                    self.fallback_stubs.append(
                                        {
                                            "class": t.id,
                                            "line": stmt.lineno,
                                            "body_size": 0,
                                            "via": "missing_dependency_alias",
                                        }
                                    )
        for sub in node.finalbody:
            self.visit(sub)
        for sub in node.orelse:
            self.visit(sub)
        self._try_stack.pop()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            return
        guarded = bool(self._try_stack and any(self._try_stack))
        for a in node.names:
            self.imports.append(
                {
                    "module": node.module,
                    "name": a.name,
                    "line": node.lineno,
                    "guarded": guarded,
                }
            )

    def visit_Import(self, node: ast.Import) -> None:
        guarded = bool(self._try_stack and any(self._try_stack))
        for a in node.names:
            self.imports.append(
                {
                    "module": a.name,
                    "name": a.name,
                    "line": node.lineno,
                    "guarded": guarded,
                }
            )

    def visit_Module(self, node: ast.Module) -> None:
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                fn = stmt.value.func
                fn_name = None
                if isinstance(fn, ast.Name):
                    fn_name = fn.id
                elif isinstance(fn, ast.Attribute):
                    fn_name = fn.attr
                if fn_name and fn_name.startswith("_emit_"):
                    self.module_top_emit_calls.append(
                        {
                            "function": fn_name,
                            "line": stmt.lineno,
                        }
                    )
        self.generic_visit(node)


# ---------------------------------------------------- A4 stale __all__
def _detect_stale_all(tree: ast.Module) -> list[str]:
    declared: list[str] = []
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if (
                    isinstance(t, ast.Name)
                    and t.id == "__all__"
                    and isinstance(n.value, (ast.List, ast.Tuple))
                ):
                    for el in n.value.elts:
                        if isinstance(el, ast.Constant) and isinstance(el.value, str):
                            declared.append(el.value)
    if not declared:
        return []
    present: set[str] = set()
    for sub in ast.walk(tree):
        if isinstance(sub, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            present.add(sub.name)
        if isinstance(sub, ast.ImportFrom):
            for a in sub.names:
                present.add(a.asname or a.name)
        if isinstance(sub, ast.Import):
            for a in sub.names:
                present.add((a.asname or a.name).split(".")[0])
        if isinstance(sub, ast.Assign):
            for t in sub.targets:
                if isinstance(t, ast.Name):
                    present.add(t.id)
    return [d for d in declared if d not in present]


# ---------------------------------------------------- A3 body fingerprint
def _normalized_body_hash(txt: str) -> str:
    lines: list[str] = []
    in_doc = False
    doc_quote: str | None = None
    for ln in txt.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if EMIT_CALL_RE.match(ln):
            continue
        if not in_doc:
            for q in ('"""', "'''"):
                if s.startswith(q):
                    if s.count(q) >= 2 and len(s) > 3:
                        s = ""
                        break
                    in_doc = True
                    doc_quote = q
                    s = ""
                    break
        else:
            if doc_quote and doc_quote in s:
                in_doc = False
                doc_quote = None
                s = ""
        if not s:
            continue
        lines.append(s)
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()


# ---------------------------------------------------- B7 rename shim
def _is_rename_shim(txt: str, tree: ast.Module) -> tuple[bool, str]:
    head = txt[:1500]
    m = SHIM_MARKER_RE.search(head)
    if not m:
        return False, ""
    n_classes = sum(1 for n in tree.body if isinstance(n, ast.ClassDef))
    n_assigns = sum(1 for n in tree.body if isinstance(n, ast.Assign))
    n_imports = sum(1 for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)))
    body_ratio = (n_classes + n_assigns + n_imports) / max(len(tree.body), 1)
    return (body_ratio >= 0.6 and len(tree.body) <= 30), m.group(0)


# ---------------------------------------------------- schema additions
ALTER_STATEMENTS = [
    # U4 — body_hash on nodes (additive ALTER TABLE)
    "ALTER TABLE nodes ADD COLUMN body_hash TEXT",
    # U1 — import resolution status on edges (already exists in schema as
    # `dynamic_resolution`; we populate it for the first time)
]

VIEW_STATEMENTS = [
    # D1 — dead-import hotspots
    """
    CREATE VIEW IF NOT EXISTS mv_dead_import_hotspots_overlay AS
    SELECT v.file_path AS file, COUNT(*) AS dead_count
    FROM overlay_violations v
    WHERE v.category = 'dead_import_resolved'
    GROUP BY v.file_path
    ORDER BY dead_count DESC
    """,
    # D2 — duplicate module clusters using body_hash
    """
    CREATE VIEW IF NOT EXISTS mv_module_duplicate_clusters_overlay AS
    SELECT body_hash, COUNT(*) AS cluster_size,
           GROUP_CONCAT(resolved_path, '|') AS files
    FROM nodes
    WHERE entity_type = 'module' AND body_hash IS NOT NULL
      AND body_hash != 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    GROUP BY body_hash
    HAVING COUNT(*) >= 2
    ORDER BY cluster_size DESC
    """,
    # D3 — module-load action calls
    """
    CREATE VIEW IF NOT EXISTS mv_module_load_action_calls_overlay AS
    SELECT v.file_path AS file, v.evidence AS detail
    FROM overlay_violations v
    WHERE v.category = 'module_load_action_call'
    ORDER BY v.file_path
    """,
    # combined: refactoring backlog with severity ordering
    """
    CREATE VIEW IF NOT EXISTS mv_overlay_debt_summary AS
    SELECT category, severity, COUNT(*) AS n_rows
    FROM overlay_violations
    GROUP BY category, severity
    ORDER BY
        CASE severity
            WHEN 'CRITICAL' THEN 0
            WHEN 'HIGH' THEN 1
            WHEN 'MEDIUM' THEN 2
            WHEN 'LOW' THEN 3
            WHEN 'ADVISORY' THEN 4
            ELSE 5
        END,
        n_rows DESC
    """,
]


def _ensure_schema(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    # U4 — additive ALTER TABLE: body_hash on nodes
    existing_cols = {r[1] for r in cur.execute("PRAGMA table_info(nodes)").fetchall()}
    if "body_hash" not in existing_cols:
        cur.execute("ALTER TABLE nodes ADD COLUMN body_hash TEXT")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS ix_nodes_body_hash ON nodes(body_hash) WHERE body_hash IS NOT NULL"
    )
    # U1-U6 — sibling overlay_violations table (no FK to edges)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS overlay_violations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            category        TEXT NOT NULL,
            severity        TEXT NOT NULL DEFAULT 'MEDIUM',
            file_path       TEXT NOT NULL DEFAULT '',
            line_no         INTEGER,
            evidence        TEXT NOT NULL DEFAULT '',
            violation_class TEXT NOT NULL DEFAULT 'overlay_enrichment',
            disposition     TEXT NOT NULL DEFAULT 'untriaged'
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS ix_overlay_violations_cat ON overlay_violations(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_overlay_violations_file ON overlay_violations(file_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_overlay_violations_sev ON overlay_violations(severity)")
    con.commit()


def _ensure_views(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    # Drop and recreate to ensure freshness
    for view_name in (
        "mv_dead_import_hotspots_overlay",
        "mv_module_duplicate_clusters_overlay",
        "mv_module_load_action_calls_overlay",
        "mv_overlay_debt_summary",
    ):
        cur.execute(f"DROP VIEW IF EXISTS {view_name}")
    for stmt in VIEW_STATEMENTS:
        cur.execute(stmt)
    con.commit()


# ---------------------------------------------------- progress bar
class _Progress:
    def __init__(self, total: int, label: str) -> None:
        self.total = max(total, 1)
        self.n = 0
        self.label = label
        self.t0 = time.time()
        self.last = 0.0

    def tick(self) -> None:
        self.n += 1
        now = time.time()
        if now - self.last < 1.0 and self.n < self.total:
            return
        self.last = now
        pct = 100 * self.n / self.total
        bar_w = 40
        fill = int(pct * bar_w / 100)
        bar = "█" * fill + "░" * (bar_w - fill)
        elapsed = now - self.t0
        eta = (elapsed / max(self.n, 1)) * (self.total - self.n)
        if pct >= 90:
            color = "\033[92m"
        elif pct >= 70:
            color = "\033[94m"
        elif pct >= 40:
            color = "\033[93m"
        else:
            color = "\033[91m"
        sys.stderr.write(
            f"\r{color}[{bar}]\033[0m {pct:5.1f}% ({self.n}/{self.total}) - ETA: {eta:5.0f}s - {self.label}"
        )
        sys.stderr.flush()

    def done(self) -> None:
        sys.stderr.write(
            f"\r\033[92m[{'█' * 40}]\033[0m 100.0% ({self.total}/{self.total}) - {self.label} done\n"
        )


# ---------------------------------------------------- main entrypoint
def enrich(sqlite_path: Path) -> dict[str, int]:
    """Apply all six debt-overlay enhancements to the given snapshot.

    Returns a per-category insertion count.
    """
    if not sqlite_path.exists():
        raise FileNotFoundError(sqlite_path)

    con = sqlite3.connect(str(sqlite_path))
    try:
        _ensure_schema(con)

        # Build a fast lookup of (resolved_path -> node_id) for body_hash population
        cur = con.cursor()
        path_to_node: dict[str, int] = {
            r[1]: r[0]
            for r in cur.execute(
                "SELECT id, resolved_path FROM nodes "
                "WHERE entity_type = 'module' AND resolved_path IS NOT NULL "
                "  AND resolved_path != ''"
            )
        }

        files = _iter_py_files()
        pr = _Progress(len(files), label="overlay enrich (6 detectors)")

        violations_to_insert: list[tuple] = []
        # (category, severity, file_path, line_no, evidence, violation_class)
        # The canonical schema has no `detail` column — supplemental info
        # is folded into the `evidence` field.

        body_hashes: list[tuple[str, str]] = []  # (file, hash) for batch update

        for py in files:
            rel = str(py.relative_to(ROOT)).replace("\\", "/")
            txt = _safe_read(py)
            if txt is None:
                pr.tick()
                continue
            tree = _safe_parse(txt)
            pr.tick()
            if tree is None:
                continue

            v = _DebtVisitor()
            v.visit(tree)

            # U1 — import resolution
            for rec in v.imports:
                top = rec["module"].split(".", 1)[0]
                if top not in INTERNAL_TOP_PKGS:
                    continue
                status = _module_path_status(rec["module"])
                if status == "missing":
                    ev = f"{rec['module']} (name={rec['name']} guarded={rec['guarded']})"
                    violations_to_insert.append(
                        (
                            "dead_import_resolved",
                            "HIGH",
                            rel,
                            rec["line"],
                            ev,
                            "overlay_enrichment",
                        )
                    )
                elif status == "namespace_pkg":
                    ev = f"{rec['module']} (name={rec['name']})"
                    violations_to_insert.append(
                        (
                            "namespace_pkg_import",
                            "ADVISORY",
                            rel,
                            rec["line"],
                            ev,
                            "overlay_enrichment",
                        )
                    )

            # U3 — fallback stubs
            for s in v.fallback_stubs:
                ev = f"{s['class']} (body_size={s['body_size']} via={s.get('via', 'class')})"
                violations_to_insert.append(
                    (
                        "import_error_fallback_stub",
                        "MEDIUM",
                        rel,
                        s["line"],
                        ev,
                        "overlay_enrichment",
                    )
                )

            # U2 — stale __all__
            miss = _detect_stale_all(tree)
            for missing_name in miss:
                ev = f"{missing_name} (declared in __all__ but not defined or imported)"
                violations_to_insert.append(
                    (
                        "stale_all_export",
                        "MEDIUM",
                        rel,
                        None,
                        ev,
                        "overlay_enrichment",
                    )
                )

            # U5 — module-load action calls (ADVISORY)
            if v.module_top_emit_calls:
                ev = (
                    f"n_calls={len(v.module_top_emit_calls)} "
                    f"(module-top _emit_* calls; architecture decision pending)"
                )
                violations_to_insert.append(
                    (
                        "module_load_action_call",
                        "ADVISORY",
                        rel,
                        None,
                        ev,
                        "overlay_enrichment",
                    )
                )

            # U4 — body hash
            h = _normalized_body_hash(txt)
            body_hashes.append((rel, h))

            # U6 — rename shim
            is_shim, marker = _is_rename_shim(txt, tree)
            if is_shim:
                ev = f"{marker} (rename-compat shim file)"
                violations_to_insert.append(
                    (
                        "rename_shim_module",
                        "LOW",
                        rel,
                        None,
                        ev,
                        "overlay_enrichment",
                    )
                )

        pr.done()

        # Wipe prior overlay violations (re-runnable)
        cur.execute("DELETE FROM overlay_violations")

        # Batch insert into the overlay_violations sibling table
        cur.executemany(
            "INSERT INTO overlay_violations "
            "(category, severity, file_path, line_no, evidence, "
            " violation_class) VALUES (?, ?, ?, ?, ?, ?)",
            violations_to_insert,
        )

        # Batch update body_hash
        update_pairs: list[tuple[str, int]] = []
        for rel_path, h in body_hashes:
            node_id = path_to_node.get(rel_path)
            if node_id is not None:
                update_pairs.append((h, node_id))
        cur.executemany(
            "UPDATE nodes SET body_hash = ? WHERE id = ?",
            update_pairs,
        )

        con.commit()

        # Build views (after data inserted)
        _ensure_views(con)

        # Summary
        summary: dict[str, int] = {}
        for cat in (
            "dead_import_resolved",
            "namespace_pkg_import",
            "import_error_fallback_stub",
            "stale_all_export",
            "module_load_action_call",
            "rename_shim_module",
        ):
            summary[cat] = cur.execute(
                "SELECT COUNT(*) FROM overlay_violations WHERE category = ?",
                (cat,),
            ).fetchone()[0]
        # module_duplicate is derived from body_hash via the view
        summary["module_duplicate_clusters"] = cur.execute(
            "SELECT COUNT(*) FROM mv_module_duplicate_clusters_overlay"
        ).fetchone()[0]
        summary["body_hashes_populated"] = len(update_pairs)

        return summary
    finally:
        con.close()


# ----------------------------------------------------------- CLI
def main() -> int:
    """Run as a standalone post-process step."""
    import argparse
    import glob
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", help="Path to ADG snapshot. Defaults to the latest in artifacts/adg/")
    args = parser.parse_args()

    if args.sqlite:
        path = Path(args.sqlite)
    else:
        snaps = sorted(
            glob.glob(str(ROOT / "artifacts/adg/adg_indexed_*.sqlite")),
            key=os.path.getmtime,
        )
        if not snaps:
            print("FATAL: no adg_indexed_*.sqlite snapshot found", file=sys.stderr)
            return 2
        path = Path(snaps[-1])

    print(f"# enriching: {path.name}", file=sys.stderr)
    summary = enrich(path)
    import json as _json

    print(_json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
