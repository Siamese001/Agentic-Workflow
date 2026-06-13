"""ADG Debt-Overlay Detector — proof-of-concept for RCA enhancements R1-R4.

Reads the latest canonical ADG snapshot + the working tree, runs seven detector
passes, and emits a derived overlay SQLite + JSON summary.

This module DOES NOT MODIFY the canonical ADG. It is a strict reader of:
  * artifacts/adg/adg_indexed_<latest>.sqlite (read-only)
  * the .py files in the working tree
and a writer of:
  * artifacts/adg/adg_debt_overlay_<UTC>.sqlite
  * artifacts/adg/adg_debt_overlay_<UTC>.json

Detection passes implement RCA tiers A1, A2, A3, A4, A5 simultaneously
(import resolution, ImportError-fallback stubs, body hashes, stale __all__,
module-load action calls), and categorize the findings into B1-B7 violation
categories.

CLI:
    python tools/analysis/adg_overlay_detector.py
"""

from __future__ import annotations

import ast
import glob
import hashlib
import importlib.util
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------- paths
REPO = Path(__file__).resolve().parents[2]
SNAPSHOTS = sorted(
    glob.glob(str(REPO / "artifacts/adg/adg_indexed_*.sqlite")),
    key=os.path.getmtime,
)
if not SNAPSHOTS:
    print("FATAL: no adg_indexed_*.sqlite snapshot found", file=sys.stderr)
    sys.exit(2)
CANONICAL_SNAPSHOT = Path(SNAPSHOTS[-1])

UTC_TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
OVERLAY_DB = REPO / f"artifacts/adg/adg_debt_overlay_{UTC_TS}.sqlite"
OVERLAY_JSON = REPO / f"artifacts/adg/adg_debt_overlay_{UTC_TS}.json"

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


# ----------------------------------------------------------- progress reporter
class Progress:
    def __init__(self, total: int, label: str) -> None:
        self.total = max(total, 1)
        self.n = 0
        self.label = label
        self.t0 = time.time()
        self.last_print = 0.0

    def tick(self, by: int = 1) -> None:
        self.n += by
        now = time.time()
        if now - self.last_print < 1.0 and self.n < self.total:
            return
        self.last_print = now
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
            f"\r{color}[{bar}]\033[0m {pct:5.1f}% ({self.n}/{self.total}) - ETA: {eta:5.1f}s - {self.label}"
        )
        sys.stderr.flush()

    def done(self) -> None:
        sys.stderr.write(
            f"\r\033[92m[{'█' * 40}]\033[0m 100.0% ({self.total}/{self.total}) - {self.label} done\n"
        )


# ---------------------------------------------------------------- file walker
def iter_py_files() -> list[Path]:
    out: list[Path] = []
    for py in REPO.rglob("*.py"):
        rel = py.relative_to(REPO).parts
        if set(rel) & EXCLUDE_DIRS:
            continue
        out.append(py)
    return out


def safe_read(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def safe_parse(txt: str) -> ast.Module | None:
    try:
        return ast.parse(txt)
    except SyntaxError:
        return None


# ---------------------------------------------------- A1 — import resolution
def module_path_status(dotted: str) -> str:
    """Resolve a dotted import name against disk.

    Returns:
        "exists"        — .py file or proper package with __init__.py
        "namespace_pkg" — folder structure exists but lacks __init__.py
        "missing"       — neither file nor folder exists
    """
    if not dotted:
        return "missing"
    top = dotted.split(".", 1)[0]
    if top not in INTERNAL_TOP_PKGS:
        # External — assume importable; the gate is for repo-internal stale paths
        try:
            spec = importlib.util.find_spec(dotted)
            return "exists" if spec else "missing"
        except (ImportError, ValueError, ModuleNotFoundError):
            return "missing"
    parts = dotted.split(".")
    base = REPO
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


# ---------------------------------------------------- A2 — try/except detector
class ImportContextVisitor(ast.NodeVisitor):
    """Tracks whether each ImportFrom/Import is inside a try-block whose
    handlers catch ImportError or ModuleNotFoundError."""

    def __init__(self) -> None:
        self._try_stack: list[bool] = []  # True == importerror-guarded
        self.import_records: list[dict] = []
        self.fallback_stubs: list[dict] = []  # A2 / B3
        self.module_top_emit_calls: list[dict] = []  # A5 / B6
        self.shim_markers_in_doc = False
        self.compat_aliases: list[dict] = []  # B7

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
        # Walk try body
        for sub in node.body:
            self.visit(sub)
        # Walk handlers — record stub classes inside ImportError handlers
        if guarded:
            for h in node.handlers:
                for stmt in h.body:
                    if isinstance(stmt, ast.ClassDef) and len(stmt.body) <= 2:
                        self.fallback_stubs.append(
                            {
                                "class": stmt.name,
                                "line": stmt.lineno,
                                "body_size": len(stmt.body),
                                "handler_at_line": h.lineno,
                            }
                        )
                    if isinstance(stmt, ast.Assign):
                        # Pattern: HealerMixin = _missing_dependency(...)
                        for t in stmt.targets:
                            if isinstance(t, ast.Name) and isinstance(stmt.value, ast.Call):
                                fn = stmt.value.func
                                if isinstance(fn, ast.Name) and fn.id.startswith("_missing"):
                                    self.fallback_stubs.append(
                                        {
                                            "class": t.id,
                                            "line": stmt.lineno,
                                            "body_size": 0,
                                            "handler_at_line": h.lineno,
                                            "via": "missing_dependency_alias",
                                        }
                                    )
        # Walk finally + orelse
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
            self.import_records.append(
                {
                    "kind": "from",
                    "module": node.module,
                    "name": a.name,
                    "asname": a.asname,
                    "line": node.lineno,
                    "guarded": guarded,
                }
            )

    def visit_Import(self, node: ast.Import) -> None:
        guarded = bool(self._try_stack and any(self._try_stack))
        for a in node.names:
            self.import_records.append(
                {
                    "kind": "plain",
                    "module": a.name,
                    "name": a.name,
                    "asname": a.asname,
                    "line": node.lineno,
                    "guarded": guarded,
                }
            )

    # A5: module-top _emit_*(...) calls
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
                    args = []
                    for a in stmt.value.args:
                        if isinstance(a, ast.Constant):
                            args.append(repr(a.value))
                        else:
                            args.append("<expr>")
                    self.module_top_emit_calls.append(
                        {
                            "function": fn_name,
                            "line": stmt.lineno,
                            "args": args[:3],
                        }
                    )
        self.generic_visit(node)


# ---------------------------------------------------- A4 — stale __all__
def detect_stale_all(tree: ast.Module) -> list[str]:
    """Return names listed in __all__ but not defined or imported."""
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


# ---------------------------------------------------- A3 — body fingerprint
def normalized_body_hash(txt: str) -> str:
    """SHA-1 over a normalized form of the file body.

    Strips: blank lines, comments, docstrings, _emit_*(...) module-load calls.
    The remaining content is meant to capture the executable behavior.
    """
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
        # Docstring tracker — best-effort, not perfect
        if not in_doc:
            for q in ('"""', "'''"):
                if s.startswith(q):
                    if s.count(q) >= 2 and len(s) > 3:
                        # single-line docstring
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


# ---------------------------------------------------- B7 — rename-shim file
def is_rename_shim(txt: str, tree: ast.Module) -> bool:
    head = txt[:1500]
    if not SHIM_MARKER_RE.search(head):
        return False
    # Body should be small and mostly trivial
    n_classes = sum(1 for n in tree.body if isinstance(n, ast.ClassDef))
    n_assigns = sum(1 for n in tree.body if isinstance(n, ast.Assign))
    n_imports = sum(1 for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)))
    body_ratio = (n_classes + n_assigns + n_imports) / max(len(tree.body), 1)
    # A rename shim is mostly imports + assigns + tiny class re-exports
    return body_ratio >= 0.6 and len(tree.body) <= 30


# ----------------------------------------------------------- main scan
def scan_repo() -> dict:
    files = iter_py_files()
    pr = Progress(len(files), label="scanning .py files")

    findings: dict = {
        "imports": [],  # all import records, with status
        "fallback_stubs": [],  # A2 / B3
        "module_load_emits": [],  # A5 / B6
        "stale_all": [],  # A4 / B5
        "module_hashes": [],  # A3 / B4
        "rename_shims": [],  # B7
    }
    snapshot_module_paths: dict[str, str] = {}  # for cross-ref later

    for py in files:
        rel = str(py.relative_to(REPO)).replace("\\", "/")
        txt = safe_read(py)
        if txt is None:
            pr.tick()
            continue
        tree = safe_parse(txt)
        pr.tick()
        if tree is None:
            continue

        v = ImportContextVisitor()
        v.visit(tree)

        # A1 — resolve every import target
        for rec in v.import_records:
            mod = rec["module"]
            top = mod.split(".", 1)[0]
            if top not in INTERNAL_TOP_PKGS:
                continue  # only audit repo-internal imports
            status = module_path_status(mod)
            findings["imports"].append(
                {
                    "file": rel,
                    "line": rec["line"],
                    "module": mod,
                    "name": rec["name"],
                    "guarded": rec["guarded"],
                    "status": status,
                }
            )

        # A2 — fallback stubs
        for s in v.fallback_stubs:
            findings["fallback_stubs"].append({"file": rel, **s})

        # A4 — stale __all__
        miss = detect_stale_all(tree)
        if miss:
            findings["stale_all"].append({"file": rel, "missing": miss})

        # A5 — module-top _emit_* calls
        if v.module_top_emit_calls:
            findings["module_load_emits"].append(
                {
                    "file": rel,
                    "n_calls": len(v.module_top_emit_calls),
                    "calls": v.module_top_emit_calls[:5],
                }
            )

        # A3 — body fingerprint
        h = normalized_body_hash(txt)
        if h:
            findings["module_hashes"].append({"file": rel, "hash": h, "lines": txt.count("\n") + 1})

        # B7 — rename shim
        if is_rename_shim(txt, tree):
            findings["rename_shims"].append(
                {
                    "file": rel,
                    "marker": (SHIM_MARKER_RE.search(txt) or [None, ""])[0]
                    if SHIM_MARKER_RE.search(txt)
                    else "",
                }
            )

    pr.done()
    return findings


# ----------------------------------------------------- emit overlay sqlite
SCHEMA = """
PRAGMA foreign_keys = OFF;

CREATE TABLE IF NOT EXISTS overlay_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS overlay_imports (
    id INTEGER PRIMARY KEY,
    source_file TEXT NOT NULL,
    line_no INTEGER NOT NULL,
    module TEXT NOT NULL,
    name TEXT,
    guarded INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL  -- exists | namespace_pkg | missing
);
CREATE INDEX IF NOT EXISTS ix_imports_status ON overlay_imports(status);
CREATE INDEX IF NOT EXISTS ix_imports_file ON overlay_imports(source_file);

CREATE TABLE IF NOT EXISTS overlay_module_hashes (
    file TEXT PRIMARY KEY,
    hash TEXT NOT NULL,
    lines INTEGER
);
CREATE INDEX IF NOT EXISTS ix_module_hashes_hash ON overlay_module_hashes(hash);

CREATE TABLE IF NOT EXISTS overlay_violations (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_no INTEGER,
    evidence TEXT,
    detail TEXT
);
CREATE INDEX IF NOT EXISTS ix_v_category ON overlay_violations(category);
CREATE INDEX IF NOT EXISTS ix_v_file ON overlay_violations(file_path);

-- D1 — dead-import hotspots
CREATE VIEW IF NOT EXISTS mv_dead_import_hotspots AS
SELECT source_file AS file, COUNT(*) AS dead_count
FROM overlay_imports
WHERE status = 'missing'
GROUP BY source_file
ORDER BY dead_count DESC;

-- D2 — duplicate module clusters
CREATE VIEW IF NOT EXISTS mv_duplicate_module_clusters AS
SELECT hash, COUNT(*) AS cluster_size,
       GROUP_CONCAT(file, '|') AS files
FROM overlay_module_hashes
GROUP BY hash
HAVING COUNT(*) >= 2
ORDER BY cluster_size DESC;

-- D3 — module-load action calls (powered by violations)
CREATE VIEW IF NOT EXISTS mv_module_load_action_calls AS
SELECT file_path AS file, COUNT(*) AS n_calls,
       MAX(CASE WHEN evidence LIKE 'n_calls=%'
                THEN CAST(SUBSTR(evidence, 9) AS INTEGER)
                ELSE 0 END) AS reported_n
FROM overlay_violations
WHERE category = 'module_load_action_call'
GROUP BY file_path
ORDER BY reported_n DESC;
"""


def write_overlay(findings: dict) -> sqlite3.Connection:
    if OVERLAY_DB.exists():
        OVERLAY_DB.unlink()
    con = sqlite3.connect(OVERLAY_DB)
    con.executescript(SCHEMA)

    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO overlay_meta(key, value) VALUES (?, ?)",
        ("source_snapshot", str(CANONICAL_SNAPSHOT.name)),
    )
    cur.execute("INSERT OR REPLACE INTO overlay_meta(key, value) VALUES (?, ?)", ("generated_utc", UTC_TS))
    cur.execute("INSERT OR REPLACE INTO overlay_meta(key, value) VALUES (?, ?)", ("repo_root", str(REPO)))

    # Imports
    for r in findings["imports"]:
        cur.execute(
            "INSERT INTO overlay_imports(source_file, line_no, module, name, "
            "guarded, status) VALUES (?, ?, ?, ?, ?, ?)",
            (r["file"], r["line"], r["module"], r.get("name"), 1 if r["guarded"] else 0, r["status"]),
        )

    # Module hashes
    for r in findings["module_hashes"]:
        cur.execute(
            "INSERT OR REPLACE INTO overlay_module_hashes(file, hash, lines) VALUES (?, ?, ?)",
            (r["file"], r["hash"], r.get("lines")),
        )

    # ----- Categorize → B1..B7 violation rows -----

    # B1 — dead_import (HIGH)
    for r in findings["imports"]:
        if r["status"] == "missing":
            cur.execute(
                "INSERT INTO overlay_violations(category, severity, file_path, "
                "line_no, evidence, detail) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    "dead_import",
                    "HIGH",
                    r["file"],
                    r["line"],
                    r["module"],
                    f"name={r.get('name')} guarded={r['guarded']}",
                ),
            )

    # B2 — namespace_pkg_import (LOW, advisory)
    for r in findings["imports"]:
        if r["status"] == "namespace_pkg":
            cur.execute(
                "INSERT INTO overlay_violations(category, severity, file_path, "
                "line_no, evidence, detail) VALUES (?, ?, ?, ?, ?, ?)",
                ("namespace_pkg_import", "LOW", r["file"], r["line"], r["module"], f"name={r.get('name')}"),
            )

    # B3 — import_error_fallback_stub (MEDIUM)
    for r in findings["fallback_stubs"]:
        cur.execute(
            "INSERT INTO overlay_violations(category, severity, file_path, "
            "line_no, evidence, detail) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "import_error_fallback_stub",
                "MEDIUM",
                r["file"],
                r["line"],
                r["class"],
                f"body_size={r['body_size']} via={r.get('via', 'class')}",
            ),
        )

    # B4 — module_duplicate (HIGH)
    by_hash: dict[str, list[str]] = defaultdict(list)
    for r in findings["module_hashes"]:
        by_hash[r["hash"]].append(r["file"])
    for h, files in by_hash.items():
        if len(files) >= 2:
            for f in files:
                cur.execute(
                    "INSERT INTO overlay_violations(category, severity, "
                    "file_path, line_no, evidence, detail) VALUES "
                    "(?, ?, ?, ?, ?, ?)",
                    (
                        "module_duplicate",
                        "HIGH",
                        f,
                        None,
                        h[:12],
                        f"cluster_size={len(files)} other={[x for x in files if x != f][:3]}",
                    ),
                )

    # B5 — stale_all_export (MEDIUM)
    for r in findings["stale_all"]:
        for missing_name in r["missing"]:
            cur.execute(
                "INSERT INTO overlay_violations(category, severity, file_path, "
                "line_no, evidence, detail) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    "stale_all_export",
                    "MEDIUM",
                    r["file"],
                    None,
                    missing_name,
                    f"declared in __all__ but not present",
                ),
            )

    # B6 — module_load_action_call (LOW initially)
    for r in findings["module_load_emits"]:
        cur.execute(
            "INSERT INTO overlay_violations(category, severity, file_path, "
            "line_no, evidence, detail) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "module_load_action_call",
                "LOW",
                r["file"],
                None,
                f"n_calls={r['n_calls']}",
                "module-top _emit_* calls",
            ),
        )

    # B7 — rename_shim_module (LOW)
    for r in findings["rename_shims"]:
        cur.execute(
            "INSERT INTO overlay_violations(category, severity, file_path, "
            "line_no, evidence, detail) VALUES (?, ?, ?, ?, ?, ?)",
            ("rename_shim_module", "LOW", r["file"], None, r["marker"], "compat shim file"),
        )

    con.commit()
    return con


# -------------------------------------------------------------- entrypoint
def main() -> int:
    print(f"# canonical snapshot: {CANONICAL_SNAPSHOT.name}", file=sys.stderr)
    print(f"# overlay output:     {OVERLAY_DB.name}", file=sys.stderr)
    findings = scan_repo()
    con = write_overlay(findings)

    cur = con.cursor()
    summary: dict = {}
    for cat, sev_default in [
        ("dead_import", "HIGH"),
        ("namespace_pkg_import", "LOW"),
        ("import_error_fallback_stub", "MEDIUM"),
        ("module_duplicate", "HIGH"),
        ("stale_all_export", "MEDIUM"),
        ("module_load_action_call", "LOW"),
        ("rename_shim_module", "LOW"),
    ]:
        n = cur.execute("SELECT COUNT(*) FROM overlay_violations WHERE category = ?", (cat,)).fetchone()[0]
        summary[cat] = n

    summary["_total_imports_seen"] = cur.execute("SELECT COUNT(*) FROM overlay_imports").fetchone()[0]
    summary["_total_module_hashes"] = cur.execute("SELECT COUNT(*) FROM overlay_module_hashes").fetchone()[0]
    summary["_canonical_snapshot"] = CANONICAL_SNAPSHOT.name
    summary["_overlay_db"] = str(OVERLAY_DB.relative_to(REPO))

    OVERLAY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"\n# wrote overlay DB:   {OVERLAY_DB}", file=sys.stderr)
    print(f"# wrote summary JSON: {OVERLAY_JSON}", file=sys.stderr)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
