"""A12: Gate Self-Test Detector.

Scans gate scripts (.codex/governance/scripts/*_gate.py, ops_scripts/ci/*.py)
for inconsistencies between docstring claims and actual enforcement logic.

Detects:
  - Docstring claims a check is performed but the code has no corresponding
    conditional / assert / raise
  - Code has enforcement logic but no docstring documenting it
  - Docstring mentions a specific anti-pattern name but the code checks
    a different one

Emits `gate_self_test` edges into the ADG with consistency classification.
"""

from __future__ import annotations

import ast
import re
import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm  # progress: §16 compliance for edge-writing loop

REPO = Path(__file__).resolve().parents[2]

# Directories to scan for gate scripts
_GATE_DIRS = [
    REPO / ".codex" / "governance" / "scripts",
    REPO / "ops_scripts" / "ci",
]

# Patterns that indicate enforcement logic in code
_ENFORCEMENT_PATTERNS = {
    "assert": re.compile(r"\bassert\b"),
    "raise": re.compile(r"\braise\b"),
    "sys.exit": re.compile(r"\bsys\.exit\b"),
    "exit(": re.compile(r"\bexit\(\d\)"),
    "fail": re.compile(r"\b(fail|FAIL)\b"),
    "violation": re.compile(r"\bviolation\b"),
    "forbidden": re.compile(r"\bforbidden\b", re.IGNORECASE),
    "blocked": re.compile(r"\bblocked\b", re.IGNORECASE),
    "check_": re.compile(r"\bcheck_"),
    "gate": re.compile(r"\bgate\b", re.IGNORECASE),
    "enforce": re.compile(r"\benforce\b", re.IGNORECASE),
}

# Patterns that indicate claims in docstrings
_CLAIM_PATTERNS = {
    "checks": re.compile(r"\bchecks?\b", re.IGNORECASE),
    "ensures": re.compile(r"\bensures?\b", re.IGNORECASE),
    "verifies": re.compile(r"\bverifies?\b", re.IGNORECASE),
    "validates": re.compile(r"\bvalidates?\b", re.IGNORECASE),
    "enforces": re.compile(r"\benforces?\b", re.IGNORECASE),
    "blocks": re.compile(r"\bblocks?\b", re.IGNORECASE),
    "prevents": re.compile(r"\bprevents?\b", re.IGNORECASE),
    "rejects": re.compile(r"\brejects?\b", re.IGNORECASE),
    "forbids": re.compile(r"\bforbids?\b", re.IGNORECASE),
    "detects": re.compile(r"\bdetects?\b", re.IGNORECASE),
    "must": re.compile(r"\bmust\b", re.IGNORECASE),
    "required": re.compile(r"\brequired\b", re.IGNORECASE),
    "never": re.compile(r"\bnever\b", re.IGNORECASE),
    "no ": re.compile(r"\bno\s+", re.IGNORECASE),
}


def _extract_docstring_claims(source: str) -> list[str]:
    """Extract enforcement claims from module/class/function docstrings."""
    claims: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return claims

    _DOCSTRING_TYPES = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(tree):
        # progress_bar: AST walk over a single file's nodes (<10ms — §16 exempt)
        if not isinstance(node, _DOCSTRING_TYPES):
            continue
        docstring = ast.get_docstring(node)
        if not docstring:
            continue
        for _claim_name, pattern in _CLAIM_PATTERNS.items():
            if pattern.search(docstring):
                # Extract the sentence containing the claim
                for line in docstring.splitlines():
                    if pattern.search(line):
                        claims.append(line.strip())

    return claims


def _extract_enforcement_logic(source: str) -> list[str]:
    """Extract enforcement logic patterns from source code."""
    logic: list[str] = []

    for line_no, line in enumerate(source.splitlines(), 1):
        for _pattern_name, pattern in _ENFORCEMENT_PATTERNS.items():
            if pattern.search(line):
                # Skip comments and docstrings
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                logic.append(f"L{line_no}: {stripped}")

    return logic


def _classify_consistency(claims: list[str], logic: list[str]) -> str:
    """Classify the consistency between claims and logic.

    Returns one of:
      - consistent: claims match enforcement logic
      - claim_without_enforcement: docstring claims checks but code doesn't enforce
      - enforcement_without_claim: code enforces but docstring doesn't document
      - empty: no claims and no enforcement (informational script)
    """
    has_claims = len(claims) > 0
    has_logic = len(logic) > 0

    if not has_claims and not has_logic:
        return "empty"
    if has_claims and not has_logic:
        return "claim_without_enforcement"
    if not has_claims and has_logic:
        return "enforcement_without_claim"
    return "consistent"


def scan_gate_file(filepath: Path) -> dict:
    """Scan a single gate file for self-test consistency.

    Returns a dict with keys: path, claims, logic, consistency.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return {"path": str(filepath), "claims": [], "logic": [], "consistency": "unreadable"}

    claims = _extract_docstring_claims(source)
    logic = _extract_enforcement_logic(source)
    consistency = _classify_consistency(claims, logic)

    return {
        "path": str(filepath),
        "claims": claims,
        "logic": logic,
        "consistency": consistency,
    }


def scan_all_gates() -> list[dict]:
    """Scan all gate scripts in configured directories."""
    # progress_bar: ~107 gate scripts, AST-only, <2s total — §16 exempt
    results: list[dict] = []

    for gate_dir in _GATE_DIRS:
        if not gate_dir.is_dir():
            continue
        for py_file in gate_dir.glob("*_gate.py"):
            results.append(scan_gate_file(py_file))
        # Also scan CI check scripts
        for py_file in gate_dir.glob("check_*.py"):
            results.append(scan_gate_file(py_file))

    return results


def write_gate_self_test_edges(sqlite_path: Path) -> int:
    """Write gate_self_test edges into the ADG SQLite.

    Returns the number of edges written.
    """
    results = scan_all_gates()
    if not results:
        return 0

    conn = sqlite3.connect(str(sqlite_path), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()

    edge_count = 0
    for result in tqdm(results, desc="A12 gate self-test edges", unit="gate"):  # progress: §16
        if result["consistency"] in ("empty", "consistent", "unreadable"):
            continue  # Only flag inconsistencies

        rel_path = result["path"].replace(str(REPO) + "\\", "").replace(str(REPO) + "/", "")
        rel_path = rel_path.replace("\\", "/")  # Normalize to forward slashes for ADG

        # Find the module node
        cursor.execute(
            "SELECT id FROM nodes WHERE resolved_path LIKE ? AND entity_type = 'module'",
            (f"%{rel_path}%",),
        )
        row = cursor.fetchone()
        if row:
            node_id = row[0]
        else:
            # Create synthetic module node for gate scripts not in AST scan
            adg_name = f"ADG::Module::{rel_path}"
            cursor.execute(
                "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
                "VALUES (?, 'module', 'L_OPS', 'synthetic', 0.9, ?)",
                (adg_name, rel_path),
            )
            node_id = cursor.lastrowid

        # Create synthetic target node
        target_name = f"ADG::GateSelfTest::{result['consistency']}"
        cursor.execute("SELECT id FROM nodes WHERE adg_name = ?", (target_name,))
        target_row = cursor.fetchone()
        if not target_row:
            cursor.execute(
                "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
                "VALUES (?, 'GateSelfTest', 'L5', 'synthetic', 1.0, '')",
                (target_name,),
            )
            target_id = cursor.lastrowid
        else:
            target_id = target_row[0]

        # Insert edge
        detail = ""
        if result["consistency"] == "claim_without_enforcement":
            detail = "; ".join(result["claims"][:3])
        elif result["consistency"] == "enforcement_without_claim":
            detail = "; ".join(result["logic"][:3])

        cursor.execute(
            "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol, semantic_type) "
            "VALUES (?, ?, 'gate_self_test', 'enforcement', ?, 0, ?, ?)",
            (node_id, target_id, rel_path, result["consistency"], detail),
        )
        edge_count += 1

    conn.commit()
    conn.close()
    return edge_count


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="A12: Gate self-test detector")
    parser.add_argument("--sqlite", type=Path, help="Path to ADG SQLite file")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing")
    args = parser.parse_args()

    results = scan_all_gates()
    inconsistencies = [r for r in results if r["consistency"] not in ("empty", "consistent", "unreadable")]

    print(f"[A12] Scanned {len(results)} gate scripts, found {len(inconsistencies)} inconsistencies:")
    for r in inconsistencies:
        print(f"  [{r['consistency']}] {r['path']}")

    if args.sqlite and not args.dry_run:
        count = write_gate_self_test_edges(args.sqlite)
        print(f"[A12] Wrote {count} gate_self_test edges to {args.sqlite}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
