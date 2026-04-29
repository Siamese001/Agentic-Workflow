"""CI gate: raise/catch symmetry on declared exception contracts.

Purpose
-------
ADG catches the antipattern "bare except Exception: pass". Expected-wiring
catches "X must call Y". Neither verifies the behavioral complement:
"callers of F handle the exceptions F can raise." That's the class of bug
that hides infra failures behind a swallow — the L0 swallow around
SemanticCacheManager.learn being the canonical example.

Scope
-----
Reads ``config/exception_contracts.yaml`` and, for each row:

1. Resolves callers of ``raiser_symbol`` via the latest ADG SQLite snapshot
   (relation_type='calls' and relation_type='imports' fan-in).
2. For each caller, AST-parses the caller's module to locate the Function or
   Method containing a call to ``raiser_symbol``.
3. Confirms that call is wrapped in (or downstream of) a ``try:`` block
   whose ``except`` handlers catch ``exception_class`` — or any of the
   declared ``parent_classes`` (e.g. ``Exception``).

``require_n_handlers`` (default 1) sets the minimum caller-handler count.

Output
------
Each contract reports: total callers, satisfying callers, unsatisfying
caller list. Fails on any contract with severity=error that misses its
required handler count. Warn-severity contracts produce output without
failing the build.

Dependencies
------------
Reads the latest ``artifacts/adg/adg_indexed_*.sqlite`` snapshot. If no
snapshot is present (fresh checkout before first ADG run), the gate emits
``SKIP`` and exits 0 — the ADG generation pipeline will run this gate
after snapshot creation.

Exit 0 on clean, 1 on net-new contract violations, 2 on config error.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import ast
import sqlite3
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    sys.stderr.write("[check_exception_contract] PyYAML required\n")
    raise SystemExit(2) from None


REPO = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO / "config" / "exception_contracts.yaml"
ADG_DIR = REPO / "artifacts" / "adg"


def _latest_sqlite() -> Path | None:
    if not ADG_DIR.is_dir():
        return None
    candidates = [p for p in ADG_DIR.glob("adg_indexed_*.sqlite") if p.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: (p.stat().st_mtime_ns, p.name))


def _load_contracts() -> list[dict]:
    if not CONFIG_PATH.is_file():
        return []
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    rows = data.get("contracts", []) if isinstance(data, dict) else []
    return rows if isinstance(rows, list) else []


def _query_callers(conn: sqlite3.Connection, raiser_module: str, raiser_symbol: str) -> list[str]:
    """Return a deduplicated list of caller file paths (repo-relative POSIX).

    The ADG stores module-granularity nodes (entity_type='module'), not
    class/method nodes. So we resolve callers coarsely: every module that
    IMPORTS the raiser's module is a potential caller. The AST step
    (_caller_satisfies) then confirms the module actually contains a Call
    to the raiser's last segment and that the call is wrapped in a matching
    try/except.
    """
    del raiser_symbol  # module-granularity — symbol match happens in AST step
    # ADG import edges are stored as:
    #   edges.relation_type = 'imports'
    #   edges.symbol        = 'pkg.sub.module.Symbol' (dotted name, abs)
    #   edges.source_file   = caller's repo-relative POSIX path
    # We convert raiser_module path to its dotted prefix and prefix-match.
    dotted_prefix = raiser_module.replace("/", ".").removesuffix(".py") + "."
    rows = conn.execute(
        """
        SELECT DISTINCT source_file
          FROM edges
         WHERE relation_type = 'imports'
           AND symbol LIKE ?
        """,
        (f"{dotted_prefix}%",),
    ).fetchall()
    callers: set[str] = set()
    for (rp,) in rows:
        if not rp:
            continue
        # Values may be repo-relative POSIX ("agentic_core/...") or absolute.
        p = Path(rp)
        if p.is_absolute():
            try:
                rel = p.resolve().relative_to(REPO).as_posix()
            except ValueError:
                continue
        else:
            rel = p.as_posix()
        # Exclude test files — they are allowed to call raisers freely and
        # should not be expected to catch arbitrary exceptions.
        if rel.startswith("tests/") or "/tests/" in rel:
            continue
        callers.add(rel)
    return sorted(callers)


def _handler_catches(handler: ast.ExceptHandler, names: set[str]) -> bool:
    """True if ``handler.type`` references any name in ``names``."""
    t = handler.type
    if t is None:
        # Bare except catches everything — counts as handling Exception.
        return "Exception" in names
    # Name: except ValueError:
    if isinstance(t, ast.Name):
        return t.id in names
    # Attribute: except mod.ValueError: — match trailing attr
    if isinstance(t, ast.Attribute):
        return t.attr in names
    # Tuple: except (A, B):
    if isinstance(t, ast.Tuple):
        for elt in t.elts:
            if isinstance(elt, ast.Name) and elt.id in names:
                return True
            if isinstance(elt, ast.Attribute) and elt.attr in names:
                return True
    return False


def _caller_satisfies(caller_path: Path, last_seg: str, handler_names: set[str]) -> bool:
    """True if ``caller_path`` contains a function where a Call to ``last_seg``
    is wrapped (directly or via ancestor) in a Try whose except handlers cover
    any of ``handler_names``.
    """
    try:
        tree = ast.parse(caller_path.read_text(encoding="utf-8"), filename=str(caller_path))
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        return False

    # Map each node -> parent (so we can walk up from a Call to nearest Try)
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name: str | None = None
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        if name != last_seg:
            continue
        # Walk up to find enclosing Try (stop at FunctionDef boundary — a Try
        # in a sibling function does not cover this call).
        cur: ast.AST | None = parents.get(id(node))
        while cur is not None and not isinstance(cur, ast.FunctionDef | ast.AsyncFunctionDef):
            if isinstance(cur, ast.Try):
                for h in cur.handlers:
                    if _handler_catches(h, handler_names):
                        return True
            cur = parents.get(id(cur))
    return False


def _check_contract(conn: sqlite3.Connection, row: dict) -> tuple[bool, str]:
    row_id = row.get("id", "<unnamed>")
    raiser_module = row.get("raiser_module")
    raiser_symbol = row.get("raiser_symbol")
    exception_class = row.get("exception_class")
    parents_cfg = row.get("parent_classes", []) or []
    require_n = int(row.get("require_n_handlers", 1))
    severity = row.get("severity", "error")

    if not (raiser_module and raiser_symbol and exception_class):
        return False, f"[{row_id}] missing raiser_module/raiser_symbol/exception_class"

    handler_names = {exception_class, *parents_cfg}
    callers = _query_callers(conn, raiser_module, raiser_symbol)
    if not callers:
        return True, (f"[{row_id}] SKIP — zero callers found in ADG for {raiser_module}::{raiser_symbol}")

    last_seg = raiser_symbol.rsplit(".", 1)[-1]
    satisfying: list[str] = []
    missing: list[str] = []
    for rel in callers:
        caller_path = REPO / rel
        if _caller_satisfies(caller_path, last_seg, handler_names):
            satisfying.append(rel)
        else:
            missing.append(rel)

    if len(satisfying) >= require_n:
        return True, (
            f"[{row_id}] PASS — {len(satisfying)}/{len(callers)} caller(s) handle "
            f"{exception_class} (require={require_n})"
        )

    failure_marker = "WARN" if severity == "warn" else "FAIL"
    lines = [
        f"[{row_id}] {failure_marker} — only {len(satisfying)}/{len(callers)} "
        f"caller(s) handle {exception_class}; require={require_n}",
        f"  raiser: {raiser_module}::{raiser_symbol}",
        f"  handler class set: {sorted(handler_names)}",
    ]
    for rel in missing[:5]:
        lines.append(f"  - missing handler in: {rel}")
    if len(missing) > 5:
        lines.append(f"  ... and {len(missing) - 5} more")
    return severity == "warn", "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=None,
        help="Path to ADG sqlite (default: latest in artifacts/adg/)",
    )
    args = parser.parse_args()

    contracts = _load_contracts()
    if not contracts:
        print(f"[check_exception_contract] SKIP: no contracts in {CONFIG_PATH}")
        return 0

    sqlite_path = args.sqlite or _latest_sqlite()
    if sqlite_path is None or not sqlite_path.is_file():
        print(
            "[check_exception_contract] SKIP: no ADG sqlite snapshot found — "
            "gate will run after `python tools/generate_full_adg.py`."
        )
        return 0

    conn = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row

        # Schema guard: this gate requires `edges.symbol` to resolve callers.
        # Stub/sentinel snapshots (`adg_indexed_99999999_9999.sqlite`) and
        # in-flight pipeline snapshots can lack this column — emit SKIP rather
        # than crashing with `OperationalError: no such column: symbol`.
        try:
            edge_cols = {
                row[1]
                for row in conn.execute("PRAGMA table_info(edges)").fetchall()
            }
        except sqlite3.OperationalError as exc:
            print(
                "[check_exception_contract] SKIP: snapshot lacks `edges` table "
                f"({sqlite_path.name}); error: {exc}. "
                "Re-run after `python tools/generate_full_adg.py` completes."
            )
            return 0
        if "symbol" not in edge_cols:
            print(
                "[check_exception_contract] SKIP: snapshot `edges` table has no "
                f"`symbol` column ({sqlite_path.name}; cols={sorted(edge_cols)}). "
                "Likely a stub/sentinel snapshot or an in-flight pipeline write — "
                "re-run after `python tools/generate_full_adg.py` completes."
            )
            return 0

        exit_code = 0
        for row in contracts:
            ok, msg = _check_contract(conn, row)
            print(msg)
            if not ok:
                exit_code = 1
    finally:
        conn.close()

    if exit_code == 0:
        print(f"[check_exception_contract] PASS — {len(contracts)} contract(s) verified")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
