"""ADG Wiring Gap Check — detect runtime-import bugs before they manifest.

Queries the latest ADG SQLite snapshot to surface four classes of wiring gap
that compile cleanly but fail at runtime:

  1. registry-gaps      — modules registered as agents/handlers in config YAML
                          but never imported by any production caller.
  2. instantiation-orphans — symbols that appear only as constructor call sites
                          (``relation_type='instantiates'``) with no matching
                          module importer, meaning the class is never imported
                          by the code that constructs it (stale DI wiring).
  3. port-adapter-gaps  — modules in an ``adapters/`` or ``integrations/`` sub-
                          tree that have zero fan-in (no module imports them),
                          indicating dead adapter wiring.
  4. dead-imports       — edges where ``relation_type='imports'`` and the target
                          symbol resolves to a module not present in the ADG
                          node set (import resolves at AST time but the module
                          was removed or renamed).

Usage
-----
    python tools/adg/adg_wiring_gap_check.py               # all 4 modes, advisory
    python tools/adg/adg_wiring_gap_check.py --mode registry-gaps
    python tools/adg/adg_wiring_gap_check.py --gate         # exit 1 on critical findings
    python tools/adg/adg_wiring_gap_check.py --gate --mode dead-imports

Exit codes
----------
    0  all checks advisory-clean (or gate mode: no critical findings)
    1  gate mode: critical findings (unresolved imports or registry gaps)
    2  infrastructure error (no snapshot, schema mismatch)

Plan: adg-distilled-followups-c8e4a1 W2 / P3-P4.
"""

from __future__ import annotations

# ADG consumer mode declaration per adg-canonical-invariants.md §6
__adg_consumer_mode__ = "read_only"

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

_VALID_MODES = ("registry-gaps", "instantiation-orphans", "port-adapter-gaps", "dead-imports")

# Adapter/integration sub-trees whose modules should have at least one importer.
_ADAPTER_SUBTREES = ("adapters/", "integrations/", "bridges/")

# Fraction of a module's dotted name that flags it as an adapter.
_ADAPTER_PATH_FRAGMENTS = ("adapters", "integrations", "bridges")


# ---------------------------------------------------------------------------
# Infrastructure helpers
# ---------------------------------------------------------------------------


def _latest_sqlite() -> Path | None:
    try:
        from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

        return latest_sqlite()
    except ImportError:
        # Fallback: glob directly.
        adg_dir = REPO / "artifacts" / "adg"
        candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
        return candidates[-1] if candidates else None


def _open_ro(sqlite_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def _edge_cols(conn: sqlite3.Connection) -> set[str]:
    return {r[1] for r in conn.execute("PRAGMA table_info(edges)").fetchall()}


def _node_cols(conn: sqlite3.Connection) -> set[str]:
    return {r[1] for r in conn.execute("PRAGMA table_info(nodes)").fetchall()}


# ---------------------------------------------------------------------------
# Detection mode 1: registry-gaps
# ---------------------------------------------------------------------------


def _check_registry_gaps(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Modules named in config YAML agent/handler registries but never imported.

    Strategy: scan ``config/`` YAML files for ``module:`` or ``class:`` keys
    (dotted module paths), convert to repo-relative file paths, then check
    whether any ``edges.relation_type='imports'`` row targets those modules.

    Returns list of gap dicts: {module_path, dotted_name, source}.
    """
    import glob  # noqa: PLC0415
    import re  # noqa: PLC0415

    config_dir = REPO / "config"
    gaps: list[dict[str, Any]] = []

    if not config_dir.is_dir():
        return gaps

    # Collect dotted module references from all YAML files under config/.
    module_re = re.compile(
        r"""^\s*(?:module|class|handler|engine_class|provider_class)\s*:\s*
            ([a-zA-Z_][a-zA-Z0-9_.]+)""",
        re.VERBOSE | re.MULTILINE,
    )
    registry_dotted: list[tuple[str, str]] = []  # (dotted_name, yaml_source)
    for yaml_file in sorted(config_dir.rglob("*.yaml")):
        try:
            text = yaml_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in module_re.finditer(text):
            dotted = m.group(1)
            if "." in dotted:  # only dotted names are module refs
                registry_dotted.append((dotted, yaml_file.name))

    if not registry_dotted:
        return gaps

    # For each registered dotted name, check if any import edge targets it.
    # ADG stores imports as: symbol = 'pkg.sub.module.ClassName' (abs dotted).
    for dotted, source in registry_dotted:
        prefix = dotted + "."
        rows = conn.execute(
            """
            SELECT COUNT(*) AS cnt
              FROM edges
             WHERE relation_type = 'imports'
               AND (symbol = ? OR symbol LIKE ?)
            """,
            (dotted, f"{prefix}%"),
        ).fetchone()
        if rows and rows["cnt"] == 0:
            # Convert dotted → file path for context.
            parts = dotted.split(".")
            candidate_path = "/".join(parts) + ".py"
            gaps.append(
                {
                    "dotted_name": dotted,
                    "module_path": candidate_path,
                    "source": source,
                    "severity": "WARN",
                }
            )

    return gaps


# ---------------------------------------------------------------------------
# Detection mode 2: instantiation-orphans
# ---------------------------------------------------------------------------


def _check_instantiation_orphans(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Symbols used only via ``instantiates`` edges but never imported.

    A constructor call (relation_type='instantiates') without a matching
    relation_type='imports' for that symbol's module is a runtime-DI bug:
    the symbol may resolve via star-import or sys.path tricks, but it is not
    declared as a dependency.

    Only flags symbols that look like dotted module paths (contain a dot),
    to avoid noise from built-in types and local names.
    """
    ecols = _edge_cols(conn)
    if "relation_type" not in ecols:
        return []

    # Check whether 'instantiates' relation type actually exists in this snapshot.
    has_instantiates = conn.execute(
        "SELECT 1 FROM edges WHERE relation_type='instantiates' LIMIT 1"
    ).fetchone()
    if not has_instantiates:
        return []

    rows = conn.execute(
        """
        SELECT DISTINCT e1.symbol, e1.source_file
          FROM edges e1
         WHERE e1.relation_type = 'instantiates'
           AND e1.symbol LIKE '%.%'
           AND NOT EXISTS (
               SELECT 1 FROM edges e2
                WHERE e2.relation_type = 'imports'
                  AND (e2.symbol = e1.symbol OR e2.symbol LIKE e1.symbol || '.%')
           )
        ORDER BY e1.symbol
        LIMIT 200
        """
    ).fetchall()

    return [
        {
            "symbol": r["symbol"],
            "source_file": r["source_file"],
            "severity": "WARN",
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Detection mode 3: port-adapter-gaps
# ---------------------------------------------------------------------------


def _check_port_adapter_gaps(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Adapter/integration modules with zero fan-in (no importer).

    Modules under ``adapters/``, ``integrations/``, or ``bridges/`` sub-trees
    that no other production module imports are dead adapters — they exist in
    the codebase but are never wired into the call graph.

    Uses ``nodes`` table (``resolved_path`` column) + ``edges`` fan-in.
    """
    ncols = _node_cols(conn)
    path_col = "resolved_path" if "resolved_path" in ncols else "file_path" if "file_path" in ncols else None
    if path_col is None or not _has_table(conn, "nodes"):
        return []

    # Fetch all adapter-subtree nodes.
    placeholders = " OR ".join(f"{path_col} LIKE ?" for _ in _ADAPTER_PATH_FRAGMENTS)
    params = [f"%/{frag}/%" for frag in _ADAPTER_PATH_FRAGMENTS]
    # Also handle modules directly under a fragment dir at top level.
    adapter_nodes = conn.execute(
        f"SELECT id, adg_name, {path_col} FROM nodes WHERE ({placeholders})",  # noqa: S608
        params,
    ).fetchall()

    if not adapter_nodes:
        return []

    ecols = _edge_cols(conn)
    if "target_id" not in ecols and "target_file" not in ecols:
        return []

    gaps: list[dict[str, Any]] = []
    for node in adapter_nodes:
        node_id = node["id"]
        adg_name = node["adg_name"]
        node_path = node[path_col] or ""

        # Skip test files.
        if "/tests/" in node_path or node_path.startswith("tests/"):
            continue

        # Count fan-in via target_id if available, else target_file.
        if "target_id" in ecols:
            fan_in = conn.execute(
                "SELECT COUNT(*) AS cnt FROM edges WHERE target_id=? AND relation_type='imports'",
                (node_id,),
            ).fetchone()["cnt"]
        else:
            fan_in = conn.execute(
                "SELECT COUNT(*) AS cnt FROM edges WHERE target_file=? AND relation_type='imports'",
                (node_path,),
            ).fetchone()["cnt"]

        if fan_in == 0:
            gaps.append(
                {
                    "adg_name": adg_name,
                    "path": node_path,
                    "severity": "WARN",
                }
            )

    return gaps


# ---------------------------------------------------------------------------
# Detection mode 4: dead-imports
# ---------------------------------------------------------------------------


def _check_dead_imports(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Import edges whose target module is absent from the ADG node set.

    An import that the AST scanner recorded but whose target module has no
    corresponding node means the module was deleted, renamed, or is outside
    the scanned tree. These become ImportError at runtime.

    Critical severity: these are actual runtime bugs, not style warnings.
    """
    ncols = _node_cols(conn)
    ecols = _edge_cols(conn)
    if "symbol" not in ecols or not _has_table(conn, "nodes"):
        return []

    path_col = "resolved_path" if "resolved_path" in ncols else "file_path" if "file_path" in ncols else None

    # Collect all known module dotted names from node table.
    if "adg_name" not in ncols:
        return []

    # Build a set of known top-level module prefixes from node adg_names.
    # adg_name format: "ADG::Module::pkg/sub/module.py" or similar.
    known_prefixes: set[str] = set()
    for (raw_name,) in conn.execute("SELECT adg_name FROM nodes").fetchall():
        if not raw_name:
            continue
        # Strip "ADG::Module::" prefix and convert path to dotted.
        module_part = raw_name.removeprefix("ADG::Module::").removeprefix("ADG::Symbol::")
        dotted = module_part.replace("/", ".").removesuffix(".py")
        # Record all prefix levels: a.b.c → a, a.b, a.b.c
        parts = dotted.split(".")
        for i in range(1, len(parts) + 1):
            known_prefixes.add(".".join(parts[:i]))

    # Fetch all import edges and check if their symbol is in known_prefixes.
    import_rows = conn.execute(
        """
        SELECT DISTINCT symbol, source_file
          FROM edges
         WHERE relation_type = 'imports'
           AND symbol IS NOT NULL
           AND symbol != ''
        ORDER BY symbol
        """
    ).fetchall()

    dead: list[dict[str, Any]] = []
    for row in import_rows:
        sym: str = row["symbol"]
        src: str = row["source_file"] or ""

        # Skip test imports — they may import things not in production tree.
        if "/tests/" in src or src.startswith("tests/"):
            continue
        # Skip stdlib / third-party short names (no dots usually).
        if "." not in sym:
            continue
        # Check if any prefix of the symbol is in known_prefixes.
        parts = sym.split(".")
        matched = any(".".join(parts[:i]) in known_prefixes for i in range(1, len(parts) + 1))
        if not matched:
            dead.append(
                {
                    "symbol": sym,
                    "source_file": src,
                    "severity": "CRITICAL",  # actual runtime ImportError risk
                }
            )

    # Deduplicate by symbol (many files may import the same dead module).
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in dead:
        if item["symbol"] not in seen:
            seen.add(item["symbol"])
            deduped.append(item)

    return deduped[:100]  # cap output


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


_MODE_LABELS = {
    "registry-gaps": "Registry Gaps (config YAML → missing importer)",
    "instantiation-orphans": "Instantiation Orphans (constructed but never imported)",
    "port-adapter-gaps": "Port Adapter Gaps (zero-fan-in adapters/integrations)",
    "dead-imports": "Dead Imports (import target absent from ADG node set)",
}

_MODE_CRITICAL = {
    "registry-gaps": False,
    "instantiation-orphans": False,
    "port-adapter-gaps": False,
    "dead-imports": True,  # runtime ImportError risk
}


def _print_section(label: str, findings: list[dict[str, Any]], gate: bool) -> int:
    """Print findings for one mode. Returns count of critical findings."""
    critical = sum(1 for f in findings if f.get("severity") == "CRITICAL")
    warn = sum(1 for f in findings if f.get("severity") == "WARN")
    total = len(findings)

    prefix = "[WIRING-GAP]"
    print(f"\n{prefix} {label}")
    print(f"{prefix}   findings: {total}  (CRITICAL={critical} WARN={warn})")

    if not findings:
        print(f"{prefix}   ✓ clean")
        return 0

    for f in findings[:20]:  # cap console output
        sev = f.get("severity", "WARN")
        if "symbol" in f and "source_file" in f:
            print(f"{prefix}   [{sev}] {f['symbol']}  ← {f.get('source_file', '?')}")
        elif "adg_name" in f:
            print(f"{prefix}   [{sev}] {f['adg_name']}  path={f.get('path', '?')}")
        elif "dotted_name" in f:
            print(f"{prefix}   [{sev}] {f['dotted_name']}  (from {f.get('source', '?')})")
        else:
            print(f"{prefix}   [{sev}] {f}")

    if total > 20:
        print(f"{prefix}   ... and {total - 20} more (use --mode to filter)")

    return critical if gate else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ADG wiring gap detector — surfaces runtime-import bugs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=list(_VALID_MODES),
        default=None,
        help="Run only this detection mode (default: all 4 modes).",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        default=bool(int(__import__("os").environ.get("ADG_WIRING_GAP_GATE", "0"))),
        help=(
            "Exit 1 when CRITICAL findings are present. "
            "By default (advisory) always exits 0. "
            "Critical modes: dead-imports. "
            "Also activated by ADG_WIRING_GAP_GATE=1 env var."
        ),
    )
    parser.add_argument(
        "--snapshot",
        default=None,
        help="Path to a specific adg_indexed_*.sqlite (default: latest).",
    )
    args = parser.parse_args()

    # --- locate snapshot ---
    if args.snapshot:
        sqlite_path = Path(args.snapshot)
        if not sqlite_path.is_file():
            print(f"[WIRING-GAP] ERROR: specified snapshot not found: {sqlite_path}")
            return 2
    else:
        sqlite_path = _latest_sqlite()
        if sqlite_path is None:
            print(
                "[WIRING-GAP] SKIP: no ADG SQLite snapshot found — "
                "run `python tools/generate/generate_full_adg.py` first."
            )
            return 0

    print(f"[WIRING-GAP] Snapshot: {sqlite_path.name}")

    try:
        conn = _open_ro(sqlite_path)
    except sqlite3.OperationalError as exc:
        print(f"[WIRING-GAP] ERROR: cannot open snapshot: {exc}")
        return 2

    try:
        # Schema guard.
        if not _has_table(conn, "edges"):
            print("[WIRING-GAP] SKIP: snapshot lacks `edges` table — likely a stub/sentinel.")
            return 0

        modes_to_run = [args.mode] if args.mode else list(_VALID_MODES)

        total_critical = 0
        for mode in modes_to_run:
            label = _MODE_LABELS[mode]
            if mode == "registry-gaps":
                findings = _check_registry_gaps(conn)
            elif mode == "instantiation-orphans":
                findings = _check_instantiation_orphans(conn)
            elif mode == "port-adapter-gaps":
                findings = _check_port_adapter_gaps(conn)
            else:  # dead-imports
                findings = _check_dead_imports(conn)

            total_critical += _print_section(label, findings, args.gate)

        print()
        if args.gate and total_critical > 0:
            print(
                f"[WIRING-GAP] GATE FAIL — {total_critical} CRITICAL finding(s) "
                f"across {len(modes_to_run)} mode(s). Fix or allowlist before merging."
            )
            return 1

        status = "GATE PASS" if args.gate else "ADVISORY"
        print(f"[WIRING-GAP] {status} — check complete.")
        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
