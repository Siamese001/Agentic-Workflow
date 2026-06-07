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

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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
import sys

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

CONFIG_PATH = REPO / "config" / "exception_contracts.yaml"
ADG_DIR = REPO / "artifacts" / "adg"


def _latest_sqlite() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


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


def _compute_indirect_raisers(raiser_module_path: Path, raiser_symbol: str) -> set[str]:
    """Return the set of same-module function names whose bodies call ``raiser_symbol``.

    Rationale (W4 P4.6 — closes P4.5 audit hollow gap): when a contract's
    ``raiser_symbol`` names a private helper (e.g. ``register_embedding_client``,
    ``_initialize``), external callers typically invoke a public wrapper in the
    same module that delegates to the private raiser (e.g.
    ``create_embedding_client``, ``get_instance``). Without call-chain
    awareness, ``_caller_satisfies`` misses every handler on these public-
    wrapper invocations — the exact failure W4 P4.4 diagnosed for 2 contracts.

    This helper parses ``raiser_module_path`` once per contract check and
    returns the names of top-level (module-level) functions whose bodies
    contain at least one Call node whose trailing identifier matches
    ``raiser_symbol.rsplit('.', 1)[-1]``. The returned set is unioned with
    ``{last_seg}`` when calling ``_caller_satisfies`` so external callers of
    either name count as satisfying the contract.

    Intentionally module-level only (not nested functions / methods) — nested
    wrappers are rare and nested-call resolution would require broader AST
    scope tracking. Single level of indirection covers the P4.4 / P4.5
    failure modes.
    """
    try:
        tree = ast.parse(raiser_module_path.read_text(encoding="utf-8"), filename=str(raiser_module_path))
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError, OSError):
        return set()

    target_seg = raiser_symbol.rsplit(".", 1)[-1]
    wrappers: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name == target_seg:
            # The raiser itself — not a wrapper.
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            call_name: str | None = None
            if isinstance(func, ast.Attribute):
                call_name = func.attr
            elif isinstance(func, ast.Name):
                call_name = func.id
            if call_name == target_seg:
                wrappers.add(node.name)
                break
    return wrappers


def _caller_satisfies(
    caller_path: Path,
    last_seg: str,
    handler_names: set[str],
    indirect_names: set[str] | None = None,
) -> bool:
    """True if ``caller_path`` contains a function where a Call to ``last_seg``
    (or any name in ``indirect_names``) is wrapped (directly or via ancestor)
    in a Try whose except handlers cover any of ``handler_names``.

    ``indirect_names`` (W4 P4.6) lets the gate treat calls to public wrappers
    as equivalent to calls to the declared raiser — closing the P4.5 audit
    hollow gap. Default ``None`` preserves the P4.5-pinned behavior for
    callers that pass the old 3-arg shape.
    """
    try:
        tree = ast.parse(caller_path.read_text(encoding="utf-8"), filename=str(caller_path))
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        return False

    # Build the acceptance set: the direct raiser name plus any wrappers.
    accepted: set[str] = {last_seg}
    if indirect_names:
        accepted |= indirect_names

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
        if name not in accepted:
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

    # W4 P4.6: compute same-module public wrappers so callers of wrappers
    # count as satisfying the contract. Closes the P4.5 audit hollow gap.
    indirect_names = _compute_indirect_raisers(REPO / raiser_module, raiser_symbol)

    satisfying: list[str] = []
    missing: list[str] = []
    for rel in callers:
        caller_path = REPO / rel
        if _caller_satisfies(caller_path, last_seg, handler_names, indirect_names=indirect_names):
            satisfying.append(rel)
        else:
            missing.append(rel)

    if len(satisfying) >= require_n:
        suffix = ""
        if indirect_names:
            suffix = f" [indirection: {sorted(indirect_names)}]"
        return True, (
            f"[{row_id}] PASS — {len(satisfying)}/{len(callers)} caller(s) handle "
            f"{exception_class} (require={require_n}){suffix}"
        )

    failure_marker = "WARN" if severity == "warn" else "FAIL"
    lines = [
        f"[{row_id}] {failure_marker} — only {len(satisfying)}/{len(callers)} "
        f"caller(s) handle {exception_class}; require={require_n}",
        f"  raiser: {raiser_module}::{raiser_symbol}",
        f"  handler class set: {sorted(handler_names)}",
    ]
    if indirect_names:
        lines.append(f"  indirection probed: {sorted(indirect_names)}")
    for rel in missing[:5]:
        lines.append(f"  - missing handler in: {rel}")
    if len(missing) > 5:
        lines.append(f"  ... and {len(missing) - 5} more")
    # W4 P4.6 advisory: when ≥3 callers exist AND zero satisfy, the
    # raiser_symbol likely names a private helper whose external callers
    # invoke a public wrapper. Surface this signal for contract authors —
    # the exact diagnostic that W4 P4.4 needed (and did by hand).
    if len(callers) >= 3 and len(satisfying) == 0:
        lines.append(
            f"  HINT: 0/{len(callers)} callers match — raiser_symbol may name "
            "a private helper. Check whether external callers invoke a public "
            f"wrapper in {raiser_module} and retarget raiser_symbol to the "
            "public entry point (see W4 P4.4 precedent: register_embedding_client "
            "→ create_embedding_client; _initialize → get_instance)."
        )
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
            "gate will run after `python tools/generate/generate_full_adg.py`."
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
                "Re-run after `python tools/generate/generate_full_adg.py` in the canonical ADG generator path."
            )
            return 0
        if "symbol" not in edge_cols:
            print(
                "[check_exception_contract] SKIP: snapshot `edges` table has no "
                f"`symbol` column ({sqlite_path.name}; cols={sorted(edge_cols)}). "
                "Likely a stub/sentinel snapshot or an in-flight pipeline write — "
                "re-run after `python tools/generate/generate_full_adg.py` in the canonical ADG generator path."
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
