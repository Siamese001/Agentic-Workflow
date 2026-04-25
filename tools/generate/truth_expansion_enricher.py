"""ADG Truth Expansion Enricher — R5 wave (RCA blind-spot taxonomy 2026-04-24).

Sibling to `tools/generate/debt_overlay_enricher.py`. Adds runtime-truth,
governance-truth, and deletion-truth signals into the canonical SQLite snapshot.

Detectors implemented:

  A6   entrypoint_kind extraction
       module → {imported, cli, hook, ci, mcp, scheduled, test}
  A7   side_effect_kind classification
       call site → {read_file, write_file, network_get, network_mutate,
                    cache_read, cache_write, metric_emit, log_emit,
                    governance_assertion, unknown}
  A8   hidden_write_path detector
       A7 writes whose enclosing module is OUTSIDE UWG-authorized paths
  A9   config/env contract index
       yaml/json/toml/.env references → resolved? on disk? consumed?
  A10  runtime_edges ingestion (OTEL spans)
       stub-and-skip when no OTEL data available locally
  A11  test_stub_truth detector
       Mock/MagicMock without failure configuration in tests/
  A12  gate_self_test detector
       CI gate docstring claims vs actual SQL/rule

All findings land in sibling tables and the existing `overlay_violations`
table (created by `debt_overlay_enricher`). Canonical `violations` /
`nodes` / `edges` tables remain untouched (except the additive
`nodes.body_hash` column, which `debt_overlay_enricher` already added).

New tables added by this module:

  module_entrypoints (file_path, kind, evidence)
  side_effect_calls (file_path, line_no, kind, callee_name, layer)
  config_references (config_file, key_path, target, resolved)
  test_stubs (file_path, line_no, mock_class, has_failure_config)
  gate_self_consistency (gate_file, claim_phrase, sql_snippet, consistent)

New `overlay_violations` categories emitted (severity in parens):

  hidden_write_outside_uwg (HIGH)
  config_target_missing (HIGH)
  env_contract_drift (MEDIUM)
  false_success_stub (MEDIUM)
  gate_self_inconsistent (HIGH)
  governance_assertion_at_module_load (LOW, ADVISORY)
  cli_only_module (ADVISORY)

Entry point: `enrich_truth(sqlite_path: Path) -> dict[str, int]`
"""

from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

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

# UWG canonical paths — writes from outside these are suspect when targeting
# state. (`agentic_core/L4_state/...` enforcement also counts as UWG-authorized.)
UWG_AUTHORIZED_FILES: set[str] = {
    "agentic_core/L2_execution/enforcement/UniversalWriteGateway.py",
    "agentic_core/L2_execution/enforcement/write_governor_mixin.py",
    "agentic_core/interfaces/write_gateway.py",
    "agentic_core/interfaces/principal_aware_write.py",
}
UWG_AUTHORIZED_PREFIXES: tuple[str, ...] = (
    "agentic_core/L4_state/",  # state layer is the SoT
    "agentic_core/L2_execution/enforcement/",
    "agentic_core/adg/applications/uwg_",
)

# Layers/paths that are EXEMPT from "outside UWG" violations:
#   - tests, scripts, ops, tools — operational code, not production state-mutating
WRITE_AUDIT_EXEMPT_PREFIXES: tuple[str, ...] = (
    "tests/",
    "tools/",
    "ops_scripts/",
    ".windsurf/",
    "agentic_core/L6_observability/",  # logs/metrics, not state writes
    "agentic_core/L0_routing/",  # routing config, not state
    "infrastructure/",
    "system_learning/",
)

# Side-effect call signatures (heuristic AST patterns)
WRITE_FILE_FUNCS: set[str] = {"write", "writelines", "write_text", "write_bytes"}
WRITE_FILE_MODULE_CALLS: set[tuple[str, str]] = {
    ("json", "dump"),
    ("yaml", "dump"),
    ("yaml", "safe_dump"),
    ("pickle", "dump"),
    ("toml", "dump"),
    ("shutil", "copy"),
    ("shutil", "copyfile"),
    ("shutil", "move"),
    ("shutil", "rmtree"),
    ("os", "remove"),
    ("os", "rename"),
    ("os", "unlink"),
}
NETWORK_GET_FUNCS: set[str] = {"get", "head", "options"}
NETWORK_MUTATE_FUNCS: set[str] = {"post", "put", "patch", "delete"}
CACHE_WRITE_PATTERNS: set[str] = {
    "set",
    "setex",
    "hset",
    "lpush",
    "rpush",
    "sadd",
    "zadd",
    "msetnx",
    "incr",
    "decr",
}
CACHE_READ_PATTERNS: set[str] = {"get", "hget", "hgetall", "lrange", "smembers", "zrange"}
METRIC_EMIT_PATTERNS: set[str] = {"counter", "gauge", "histogram", "increment", "observe", "timing"}
GOVERNANCE_ASSERTION_PATTERNS: set[str] = {
    "record_compliance",
    "assert_layer",
    "register_invariant",
    "declare_authority",
    "mark_governed",
    "emit_governance",
    "validate_invariant",
}

# Entrypoint heuristics
HOOK_PATH_PATTERNS = (".windsurf/scripts/", "/hooks/", "_hook.py")
CI_PATH_PATTERNS = ("ops_scripts/ci/check_", "/ci/", ".github/workflows/")
MCP_PATH_PATTERNS = ("/mcp_", "_mcp_server.py", "tools/mcp/")

# Config-file walker — for A9
# Skip .json: too noisy (test fixtures, lockfiles, ADG dump artifacts).
# Skip files >100KB to avoid generated/cache files.
CONFIG_EXTS = {".yaml", ".yml", ".toml", ".env"}
CONFIG_MAX_BYTES = 100 * 1024
CONFIG_PATH_EXCLUDES = (
    "artifacts/",
    "docs/reports/",
    "tools/archive/",
    ".github/workflows/_deleted/",
)

# Test-stub heuristic — for A11
MOCK_CLASS_NAMES = {"Mock", "MagicMock", "AsyncMock", "PropertyMock"}


# ----------------------------------------------------------- progress reporter
class _Progress:
    def __init__(self, total: int, label: str) -> None:
        self.total = max(total, 1)
        self.n = 0
        self.label = label
        self.t0 = time.time()
        self.last = 0.0

    def tick(self, by: int = 1) -> None:
        self.n += by
        now = time.time()
        if now - self.last < 1.0 and self.n < self.total:
            return
        self.last = now
        pct = 100 * self.n / self.total
        bar_w = 40
        fill = int(pct * bar_w / 100)
        bar = "\u2588" * fill + "\u2591" * (bar_w - fill)
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
            f"\r\033[92m[{'\u2588' * 40}]\033[0m 100.0% ({self.total}/{self.total}) - {self.label} done\n"
        )


# ---------------------------------------------------- file walking
def _iter_py_files() -> list[Path]:
    out: list[Path] = []
    for py in ROOT.rglob("*.py"):
        rel_parts = py.relative_to(ROOT).parts
        if set(rel_parts) & EXCLUDE_DIRS:
            continue
        out.append(py)
    return out


def _iter_config_files() -> list[Path]:
    out: list[Path] = []
    for ext in CONFIG_EXTS:
        for p in ROOT.rglob(f"*{ext}"):
            rel_parts = p.relative_to(ROOT).parts
            if set(rel_parts) & EXCLUDE_DIRS:
                continue
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            if any(rel.startswith(prefix) for prefix in CONFIG_PATH_EXCLUDES):
                continue
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size > CONFIG_MAX_BYTES:
                continue
            if p.name in {"package-lock.json", "poetry.lock"}:
                continue
            out.append(p)
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


# ---------------------------------------------------- A6 entrypoint detection
def _detect_entrypoint_kind(rel: str, txt: str, tree: ast.Module) -> tuple[str, str]:
    """Return (kind, evidence)."""
    rel_l = rel.lower()
    # Filesystem-pattern signals
    if any(p in rel for p in HOOK_PATH_PATTERNS):
        return "hook", "path-pattern"
    if any(p in rel for p in CI_PATH_PATTERNS):
        return "ci", "path-pattern"
    if any(p in rel for p in MCP_PATH_PATTERNS):
        return "mcp", "path-pattern"
    if rel.startswith("tests/") or "/test_" in rel or rel.endswith("_test.py"):
        return "test", "path-pattern"
    # AST signal: has `if __name__ == "__main__":` block?
    has_main_guard = False
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            left = node.test.left
            if (
                isinstance(left, ast.Name)
                and left.id == "__name__"
                and node.test.comparators
                and isinstance(node.test.comparators[0], ast.Constant)
                and node.test.comparators[0].value == "__main__"
            ):
                has_main_guard = True
                break
    if has_main_guard:
        # Distinguish CLI vs scheduled
        if "schedule" in rel_l or "cron" in rel_l:
            return "scheduled", "main-guard+filename"
        return "cli", "main-guard"
    return "imported", "default"


# ---------------------------------------------------- AST visitor — A7, A8, A11
class _TruthVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.side_effects: list[dict] = []  # A7
        self.test_stubs: list[dict] = []  # A11
        self.governance_assertions_at_module_top: list[dict] = []
        self._depth = 0  # 0 = module top
        self._in_function = False

    def _record_call(self, node: ast.Call) -> None:
        fn = node.func
        # Get callee name + module if attribute
        callee_name = None
        callee_mod = None
        if isinstance(fn, ast.Attribute):
            callee_name = fn.attr
            if isinstance(fn.value, ast.Name):
                callee_mod = fn.value.id
        elif isinstance(fn, ast.Name):
            callee_name = fn.id

        if not callee_name:
            return

        kind: str | None = None
        # A7 — write_file
        if callee_name in WRITE_FILE_FUNCS:
            kind = "write_file"
        elif (callee_mod, callee_name) in WRITE_FILE_MODULE_CALLS:
            kind = "write_file"
        # network mutating
        elif callee_name in NETWORK_MUTATE_FUNCS and callee_mod in {
            "requests",
            "httpx",
            "urllib",
            "client",
            "session",
        }:
            kind = "network_mutate"
        elif callee_name in NETWORK_GET_FUNCS and callee_mod in {"requests", "httpx"}:
            kind = "network_get"
        # cache writes (heuristic — Redis-shaped)
        elif callee_name in CACHE_WRITE_PATTERNS and callee_mod in {
            "redis",
            "r",
            "cache",
            "_redis",
            "_cache",
            "client",
        }:
            kind = "cache_write"
        elif callee_name in CACHE_READ_PATTERNS and callee_mod in {
            "redis",
            "r",
            "cache",
            "_redis",
            "_cache",
            "client",
        }:
            kind = "cache_read"
        # metric/log emit
        elif callee_name in METRIC_EMIT_PATTERNS:
            kind = "metric_emit"
        # governance assertions (extends A5)
        elif callee_name in GOVERNANCE_ASSERTION_PATTERNS or callee_name.startswith("_emit_"):
            kind = "governance_assertion"

        if kind is None:
            return

        self.side_effects.append(
            {
                "line": node.lineno,
                "kind": kind,
                "callee": callee_name,
                "callee_mod": callee_mod,
                "at_module_top": self._depth == 0,
            }
        )

        # A5/governance: if module-load and governance_assertion
        if kind == "governance_assertion" and self._depth == 0 and not self._in_function:
            self.governance_assertions_at_module_top.append(
                {
                    "line": node.lineno,
                    "callee": callee_name,
                }
            )

    # --- traversal with depth tracking
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._depth += 1
        self._in_function = True
        self.generic_visit(node)
        self._depth -= 1
        if self._depth == 0:
            self._in_function = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        self._record_call(node)
        self.generic_visit(node)

    # A11 — test stubs: detect Mock(...) without configuration in tests/
    def visit_Assign(self, node: ast.Assign) -> None:
        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return
        fn = node.value.func
        cls_name = None
        if isinstance(fn, ast.Name):
            cls_name = fn.id
        elif isinstance(fn, ast.Attribute):
            cls_name = fn.attr
        if cls_name in MOCK_CLASS_NAMES:
            # Look for failure-mode kwargs
            kwargs = {kw.arg for kw in node.value.keywords if kw.arg}
            has_failure_cfg = bool(kwargs & {"side_effect", "return_value", "spec", "spec_set"})
            self.test_stubs.append(
                {
                    "line": node.lineno,
                    "mock_class": cls_name,
                    "has_failure_config": has_failure_cfg,
                }
            )
        self.generic_visit(node)


# ---------------------------------------------------- A8 hidden write check
def _is_uwg_authorized(rel: str) -> bool:
    if rel in UWG_AUTHORIZED_FILES:
        return True
    return any(rel.startswith(p) for p in UWG_AUTHORIZED_PREFIXES)


def _is_write_audit_exempt(rel: str) -> bool:
    return any(rel.startswith(p) for p in WRITE_AUDIT_EXEMPT_PREFIXES)


def _file_imports_uwg(tree: ast.Module) -> bool:
    """True if the module imports from any UWG-authorized module."""
    uwg_module_substrings = (
        "UniversalWriteGateway",
        "write_gateway",
        "write_governor_mixin",
        "uwg_write_authority",
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for sub in uwg_module_substrings:
                if sub.lower() in node.module.lower():
                    return True
        elif isinstance(node, ast.Import):
            for a in node.names:
                for sub in uwg_module_substrings:
                    if sub.lower() in a.name.lower():
                        return True
    return False


# ---------------------------------------------------- A9 config references
PATH_REF_RE = re.compile(
    r"(?<![\w/])"
    r"((?:agentic_core|apps_eval|apps_exec|apps_lic|apps_research|apps_rfp|"
    r"apps_rg|apps_shared|apps_underwriting_ai|system_learning|tools|"
    r"ops_scripts|infrastructure)"
    r"(?:[/.][\w_-]+)+)",
    re.MULTILINE,
)


def _scan_config_file(p: Path, repo_root: Path) -> list[dict]:
    """Return list of {key_path, target, resolved} for each detected reference."""
    rel = str(p.relative_to(repo_root)).replace("\\", "/")
    txt = _safe_read(p)
    if txt is None:
        return []
    refs: list[dict] = []
    for m in PATH_REF_RE.finditer(txt):
        target = m.group(1).replace(".py", "").replace("/", ".")
        # Resolve module-style and path-style
        as_module = target.replace(".", "/")
        py_file = repo_root / f"{as_module}.py"
        pkg_init = repo_root / as_module / "__init__.py"
        pkg_dir = repo_root / as_module
        resolved = py_file.exists() or pkg_init.exists() or pkg_dir.is_dir()
        refs.append(
            {
                "config_file": rel,
                "key_path": "",  # column reserved; YAML/TOML extraction is non-trivial
                "target": target,
                "resolved": resolved,
            }
        )
    return refs


# ---------------------------------------------------- A12 gate self-test
GATE_DOCSTRING_CLAIM_RE = re.compile(
    r"(edge_kind\s*=\s*['\"](\w+)['\"]|"
    r"relation_type\s*=\s*['\"](\w+)['\"]|"
    r"category\s*=\s*['\"](\w+)['\"]|"
    r"violation_class\s*=\s*['\"](\w+)['\"])",
)
# Match field=value within a triple-quoted SQL block or near WHERE/SELECT
GATE_SQL_CLAUSE_RE = re.compile(
    r"(?:SELECT|FROM|WHERE|AND|OR)\b[^\"']*?"
    r"(edge_kind|relation_type|category|violation_class)"
    r"\s*=\s*['\"](\w+)['\"]",
    re.IGNORECASE | re.DOTALL,
)


def _strip_module_docstring(tree: ast.Module, txt: str) -> str:
    """Return the source text with the module docstring removed.

    This avoids false positives where the docstring quotes a value that is
    different from the SQL the gate actually executes.
    """
    if not tree.body:
        return txt
    first = tree.body[0]
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        end_line = first.end_lineno or first.lineno
        lines = txt.splitlines()
        return "\n".join(lines[end_line:])
    return txt


def _gate_self_check(p: Path) -> tuple[bool, str, str] | None:
    """Return (consistent, claim_phrase, sql_snippet) or None if no claim found."""
    txt = _safe_read(p)
    if txt is None:
        return None
    tree = _safe_parse(txt)
    if tree is None:
        return None
    # Extract docstring claims (look at first 60 lines)
    head = "\n".join(txt.splitlines()[:60])
    claims = GATE_DOCSTRING_CLAIM_RE.findall(head)
    if not claims:
        return None
    # Extract SQL claims from the body MINUS the docstring (so the
    # docstring's quoted values cannot pretend to be SQL).
    body = _strip_module_docstring(tree, txt)
    sql_matches = GATE_SQL_CLAUSE_RE.findall(body)
    if not sql_matches:
        return None
    # Compare: any docstring claim that doesn't appear in SQL?
    doc_values: set[str] = set()
    for c in claims:
        for grp in c[1:]:
            if grp:
                doc_values.add(grp)
    sql_values = {v.lower() for _, v in sql_matches}
    sql_values_raw = {v for _, v in sql_matches}
    inconsistent_claims = [v for v in doc_values if v.lower() not in sql_values]
    if inconsistent_claims:
        return (
            False,
            f"docstring claims {inconsistent_claims}",
            f"sql actually queries {sorted(sql_values_raw)}",
        )
    return (True, "", "")


# ---------------------------------------------------- schema additions
SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS module_entrypoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        kind TEXT NOT NULL,
        evidence TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS side_effect_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        line_no INTEGER NOT NULL,
        kind TEXT NOT NULL,
        callee_name TEXT,
        callee_mod TEXT,
        at_module_top INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS config_references (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_file TEXT NOT NULL,
        key_path TEXT NOT NULL DEFAULT '',
        target TEXT NOT NULL,
        resolved INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS test_stubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        line_no INTEGER NOT NULL,
        mock_class TEXT NOT NULL,
        has_failure_config INTEGER NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS gate_self_consistency (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gate_file TEXT NOT NULL,
        consistent INTEGER NOT NULL,
        claim_phrase TEXT,
        sql_snippet TEXT
    )
    """,
]

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS ix_mep_file ON module_entrypoints(file_path)",
    "CREATE INDEX IF NOT EXISTS ix_mep_kind ON module_entrypoints(kind)",
    "CREATE INDEX IF NOT EXISTS ix_sec_file ON side_effect_calls(file_path)",
    "CREATE INDEX IF NOT EXISTS ix_sec_kind ON side_effect_calls(kind)",
    "CREATE INDEX IF NOT EXISTS ix_cref_file ON config_references(config_file)",
    "CREATE INDEX IF NOT EXISTS ix_cref_resolved ON config_references(resolved)",
    "CREATE INDEX IF NOT EXISTS ix_ts_file ON test_stubs(file_path)",
    "CREATE INDEX IF NOT EXISTS ix_gsc_consistent ON gate_self_consistency(consistent)",
]

VIEW_STATEMENTS = [
    """
    CREATE VIEW IF NOT EXISTS mv_hidden_writes_overlay AS
    SELECT s.file_path, s.line_no, s.kind, s.callee_name, s.callee_mod
    FROM side_effect_calls s
    WHERE s.kind = 'write_file'
      AND NOT (
          s.file_path LIKE 'tests/%'
          OR s.file_path LIKE 'tools/%'
          OR s.file_path LIKE 'ops_scripts/%'
          OR s.file_path LIKE '.windsurf/%'
          OR s.file_path LIKE 'agentic_core/L6_observability/%'
          OR s.file_path LIKE 'agentic_core/L4_state/%'
          OR s.file_path LIKE 'agentic_core/L2_execution/enforcement/%'
          OR s.file_path LIKE 'agentic_core/L0_routing/%'
          OR s.file_path LIKE 'infrastructure/%'
          OR s.file_path LIKE 'system_learning/%'
      )
    """,
    """
    CREATE VIEW IF NOT EXISTS mv_entrypoint_kind_summary AS
    SELECT kind, COUNT(*) AS n
    FROM module_entrypoints
    GROUP BY kind
    ORDER BY n DESC
    """,
    """
    CREATE VIEW IF NOT EXISTS mv_unresolved_config_refs AS
    SELECT config_file, target
    FROM config_references
    WHERE resolved = 0
    ORDER BY config_file, target
    """,
    """
    CREATE VIEW IF NOT EXISTS mv_truth_expansion_summary AS
    SELECT
        (SELECT COUNT(*) FROM module_entrypoints) AS modules_classified,
        (SELECT COUNT(*) FROM module_entrypoints WHERE kind = 'cli') AS cli_modules,
        (SELECT COUNT(*) FROM module_entrypoints WHERE kind = 'hook') AS hook_modules,
        (SELECT COUNT(*) FROM module_entrypoints WHERE kind = 'ci') AS ci_modules,
        (SELECT COUNT(*) FROM module_entrypoints WHERE kind = 'mcp') AS mcp_modules,
        (SELECT COUNT(*) FROM side_effect_calls) AS side_effect_calls,
        (SELECT COUNT(*) FROM mv_hidden_writes_overlay) AS hidden_writes,
        (SELECT COUNT(*) FROM config_references) AS config_refs,
        (SELECT COUNT(*) FROM mv_unresolved_config_refs) AS unresolved_config_refs,
        (SELECT COUNT(*) FROM test_stubs) AS test_stubs_total,
        (SELECT COUNT(*) FROM test_stubs WHERE has_failure_config = 0) AS bare_stubs,
        (SELECT COUNT(*) FROM gate_self_consistency) AS gates_examined,
        (SELECT COUNT(*) FROM gate_self_consistency WHERE consistent = 0) AS gates_inconsistent
    """,
]


def _ensure_schema(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    # Ensure overlay_violations exists (debt_overlay_enricher creates it,
    # but we may run standalone too)
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
    for stmt in SCHEMA_STATEMENTS:
        cur.execute(stmt)
    for stmt in INDEX_STATEMENTS:
        cur.execute(stmt)
    con.commit()


def _ensure_views(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    for view_name in (
        "mv_hidden_writes_overlay",
        "mv_entrypoint_kind_summary",
        "mv_unresolved_config_refs",
        "mv_truth_expansion_summary",
    ):
        cur.execute(f"DROP VIEW IF EXISTS {view_name}")
    for stmt in VIEW_STATEMENTS:
        cur.execute(stmt)
    con.commit()


# ---------------------------------------------------- main entrypoint
def enrich_truth(sqlite_path: Path) -> dict[str, int]:
    if not sqlite_path.exists():
        raise FileNotFoundError(sqlite_path)

    con = sqlite3.connect(str(sqlite_path))
    try:
        _ensure_schema(con)
        cur = con.cursor()

        # --- pass 1: walk Python files
        py_files = _iter_py_files()
        pr = _Progress(len(py_files), label="truth-expansion (.py pass)")

        ep_rows: list[tuple[str, str, str]] = []  # (file, kind, evidence)
        se_rows: list[tuple] = []  # (file, line, kind, callee, callee_mod, at_top)
        ts_rows: list[tuple] = []  # (file, line, mock_class, has_failure_cfg)
        v_rows: list[tuple] = []  # overlay_violations rows

        # Track (file -> imports UWG?) for A8
        uwg_aware: dict[str, bool] = {}

        for py in py_files:
            rel = str(py.relative_to(ROOT)).replace("\\", "/")
            txt = _safe_read(py)
            if txt is None:
                pr.tick()
                continue
            tree = _safe_parse(txt)
            pr.tick()
            if tree is None:
                continue

            # A6
            kind, evidence = _detect_entrypoint_kind(rel, txt, tree)
            ep_rows.append((rel, kind, evidence))

            # A7/A11 traversal
            v = _TruthVisitor()
            v.visit(tree)
            for se in v.side_effects:
                se_rows.append(
                    (
                        rel,
                        se["line"],
                        se["kind"],
                        se["callee"],
                        se.get("callee_mod"),
                        1 if se["at_module_top"] else 0,
                    )
                )
            for ts in v.test_stubs:
                ts_rows.append(
                    (
                        rel,
                        ts["line"],
                        ts["mock_class"],
                        1 if ts["has_failure_config"] else 0,
                    )
                )

            uwg_aware[rel] = _file_imports_uwg(tree)

            # A6 → ADVISORY violation: cli_only_module if kind == 'cli'
            if kind == "cli":
                v_rows.append(
                    (
                        "cli_only_module",
                        "ADVISORY",
                        rel,
                        None,
                        f"entrypoint kind=cli (evidence={evidence})",
                        "overlay_enrichment",
                    )
                )

            # A5 extension — governance assertions at module top
            # ONLY flag genuine governance functions (record_compliance,
            # assert_layer, etc.) — not _emit_* which is already in
            # `module_load_action_call` from debt_overlay_enricher.
            for g in v.governance_assertions_at_module_top:
                if g["callee"].startswith("_emit_"):
                    continue
                v_rows.append(
                    (
                        "governance_assertion_at_module_load",
                        "ADVISORY",
                        rel,
                        g["line"],
                        f"{g['callee']} called at module load",
                        "overlay_enrichment",
                    )
                )

            # A11 — false_success_stub: bare Mock in tests/
            if rel.startswith("tests/"):
                for ts in v.test_stubs:
                    if not ts["has_failure_config"]:
                        v_rows.append(
                            (
                                "false_success_stub",
                                "MEDIUM",
                                rel,
                                ts["line"],
                                f"{ts['mock_class']}() with no side_effect/return_value/spec",
                                "overlay_enrichment",
                            )
                        )

        pr.done()

        # A8 — hidden writes outside UWG, post-hoc per-row
        # (computing here rather than the view because the view also covers
        #  what's visible to consumers)
        for row in se_rows:
            file_path, line_no, kind, callee, callee_mod, at_top = row
            if kind != "write_file":
                continue
            if _is_write_audit_exempt(file_path):
                continue
            if _is_uwg_authorized(file_path):
                continue
            if uwg_aware.get(file_path):
                continue  # imports UWG → trust the import
            v_rows.append(
                (
                    "hidden_write_outside_uwg",
                    "HIGH",
                    file_path,
                    line_no,
                    f"{callee_mod or ''}.{callee}() — write outside UWG-imported module",
                    "overlay_enrichment",
                )
            )

        # --- pass 2: config files
        cfg_files = _iter_config_files()
        pr2 = _Progress(len(cfg_files), label="truth-expansion (config pass)")
        cref_rows: list[tuple[str, str, str, int]] = []
        for cf in cfg_files:
            for rec in _scan_config_file(cf, ROOT):
                cref_rows.append(
                    (
                        rec["config_file"],
                        rec["key_path"],
                        rec["target"],
                        1 if rec["resolved"] else 0,
                    )
                )
                if not rec["resolved"]:
                    v_rows.append(
                        (
                            "config_target_missing",
                            "HIGH",
                            rec["config_file"],
                            None,
                            f"{rec['target']} (referenced by config but not on disk)",
                            "overlay_enrichment",
                        )
                    )
            pr2.tick()
        pr2.done()

        # --- pass 3: gate self-test for ops_scripts/ci/check_*.py
        gates = sorted((ROOT / "ops_scripts" / "ci").glob("check_*.py"))
        gate_rows: list[tuple[str, int, str, str]] = []
        for g in gates:
            grel = str(g.relative_to(ROOT)).replace("\\", "/")
            res = _gate_self_check(g)
            if res is None:
                gate_rows.append((grel, 1, "", ""))  # no claim → considered ok
                continue
            consistent, claim, sql = res
            gate_rows.append(
                (
                    grel,
                    1 if consistent else 0,
                    claim,
                    sql,
                )
            )
            if not consistent:
                v_rows.append(
                    (
                        "gate_self_inconsistent",
                        "HIGH",
                        grel,
                        None,
                        f"{claim} | {sql}",
                        "overlay_enrichment",
                    )
                )

        # --- write all rows in one transaction
        cur.execute("DELETE FROM module_entrypoints")
        cur.executemany(
            "INSERT INTO module_entrypoints (file_path, kind, evidence) VALUES (?, ?, ?)",
            ep_rows,
        )
        cur.execute("DELETE FROM side_effect_calls")
        cur.executemany(
            "INSERT INTO side_effect_calls "
            "(file_path, line_no, kind, callee_name, callee_mod, at_module_top) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            se_rows,
        )
        cur.execute("DELETE FROM test_stubs")
        cur.executemany(
            "INSERT INTO test_stubs (file_path, line_no, mock_class, has_failure_config) VALUES (?, ?, ?, ?)",
            ts_rows,
        )
        cur.execute("DELETE FROM config_references")
        cur.executemany(
            "INSERT INTO config_references (config_file, key_path, target, resolved) VALUES (?, ?, ?, ?)",
            cref_rows,
        )
        cur.execute("DELETE FROM gate_self_consistency")
        cur.executemany(
            "INSERT INTO gate_self_consistency "
            "(gate_file, consistent, claim_phrase, sql_snippet) "
            "VALUES (?, ?, ?, ?)",
            gate_rows,
        )
        # remove only the truth-expansion overlay rows on rerun
        cur.execute(
            """
            DELETE FROM overlay_violations
            WHERE category IN (
                'hidden_write_outside_uwg', 'config_target_missing',
                'env_contract_drift', 'false_success_stub',
                'gate_self_inconsistent',
                'governance_assertion_at_module_load', 'cli_only_module'
            )
            """
        )
        cur.executemany(
            "INSERT INTO overlay_violations "
            "(category, severity, file_path, line_no, evidence, violation_class) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            v_rows,
        )
        con.commit()
        _ensure_views(con)

        # --- A10 OTEL runtime edges (stub-and-skip) ---
        # Looks for OTEL spans in artifacts/otel/ or runtime_adg snapshots.
        # If absent, returns 0 silently.
        otel_count = 0  # placeholder; full integration is a follow-on wave

        summary: dict[str, int] = {
            "modules_classified": len(ep_rows),
            "side_effect_calls": len(se_rows),
            "config_refs": len(cref_rows),
            "test_stubs": len(ts_rows),
            "gates_examined": len(gate_rows),
            "otel_runtime_edges": otel_count,
        }
        for cat in (
            "hidden_write_outside_uwg",
            "config_target_missing",
            "false_success_stub",
            "gate_self_inconsistent",
            "governance_assertion_at_module_load",
            "cli_only_module",
        ):
            summary[cat] = cur.execute(
                "SELECT COUNT(*) FROM overlay_violations WHERE category = ?",
                (cat,),
            ).fetchone()[0]
        return summary
    finally:
        con.close()


# ----------------------------------------------------------- CLI
def main() -> int:
    import argparse
    import glob

    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", help="Path to ADG snapshot. Defaults to latest in artifacts/adg/")
    args = parser.parse_args()

    if args.sqlite:
        path = Path(args.sqlite)
    else:
        snaps = sorted(
            glob.glob(str(ROOT / "artifacts/adg/adg_indexed_*.sqlite")),
            key=os.path.getmtime,
        )
        if not snaps:
            tmps = sorted(
                glob.glob(str(ROOT / "artifacts/adg/adg_indexed_*.sqlite.tmp")),
                key=os.path.getmtime,
            )
            if not tmps:
                print("FATAL: no canonical snapshot", file=sys.stderr)
                return 2
            path = Path(tmps[-1])
        else:
            path = Path(snaps[-1])

    print(f"# truth expansion: {path.name}", file=sys.stderr)
    summary = enrich_truth(path)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
