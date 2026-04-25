"""Code-based ADG redundancy audit (v2).

V1 was topic-based pattern-matching — it flagged gates whose docstring
mentioned "hotspot" or "dead" without checking what the gate's code
actually does. v2 inspects the code:

A gate is a TRUE redundancy candidate only if ALL of:
  1. Its body imports from `_adg_wiring_gate_base` (it's a graph-DB consumer)
  2. Its `run()` body executes ONE SELECT against an MV / P-view
  3. There is NO additional Python policy code (no thresholds, allowlists,
     prior-snapshot diffs, regex extractions, computed ratios, etc.)
     beyond direct row→Violation translation.

A gate that adds policy on top of the MV is NOT redundant — it's correctly
layered: the MV is the input, the gate is the policy.

This audit is empirical: it parses each gate's AST, classifies, and
produces a markdown report.
"""

from __future__ import annotations

import ast
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"
CI_DIR = REPO / "ops_scripts" / "ci"


# Markers that indicate the gate adds policy beyond a single MV select.
POLICY_MARKERS = (
    # Numeric thresholds → policy
    re.compile(r"\bTHRESHOLD\b"),
    re.compile(r"\bRATIO\b"),
    re.compile(r"\bMIN_\w+\b"),
    re.compile(r"\bMAX_\w+\b"),
    re.compile(r"\bTOP_N\b"),
    re.compile(r"\bCOLLAPSE_FRACTION\b"),
    # Allowlists / exclusion sets → policy
    re.compile(r"\bALLOWLIST\b"),
    re.compile(r"\bEXCLUDE_\w+\b"),
    re.compile(r"\bSKIP_\w+\b"),
    re.compile(r"\bPRODUCTION_ROOTS\b"),
    # Temporal / delta operations → policy
    re.compile(r"\bconnect_prior\b"),
    re.compile(r"\bprior_snapshot\b"),
    re.compile(r"\bbaseline\b", re.IGNORECASE),
    re.compile(r"\bratchet\b", re.IGNORECASE),
    re.compile(r"\bcompute_deltas\b"),
    # Ratio / derivation → policy
    re.compile(r"\btrace_ratio\b"),
    re.compile(r"\bfan_in\s*[><=]"),  # comparison on fan-in
    re.compile(r"\bfan_out\s*[><=]"),
)

# Markers that indicate the gate is a thin MV consumer.
THIN_MARKERS = (
    re.compile(r"FROM\s+mv_\w+", re.IGNORECASE),
    re.compile(r"FROM\s+v_p[0-3]_\w+", re.IGNORECASE),
)


@dataclass
class GateAnalysis:
    path: Path
    has_wiring_gate_base: bool = False
    sql_queries: list[str] = field(default_factory=list)
    references_mv: bool = False
    references_pview: bool = False
    policy_evidence: list[str] = field(default_factory=list)
    loc: int = 0

    @property
    def classification(self) -> str:
        # 1. No SQL → not a graph-DB gate
        if not self.sql_queries:
            return "NON_GRAPH"  # legitimate non-graph concern
        # 2. Has policy markers → gate adds value beyond MV
        if self.policy_evidence:
            return "POLICY_LAYER"
        # 3. Pure MV/P-view consumer with no policy → potential thin
        if (self.references_mv or self.references_pview) and self.has_wiring_gate_base:
            return "THIN_CANDIDATE"
        # 4. Uses raw edges/violations tables, no MV → could become MV
        return "RAW_CONSUMER"

    @property
    def actionable_finding(self) -> str:
        """One-line user-facing recommendation."""
        c = self.classification
        if c == "NON_GRAPH":
            return "KEEP — non-graph gate (config/format/process check)"
        if c == "POLICY_LAYER":
            sample = self.policy_evidence[0] if self.policy_evidence else ""
            return f"KEEP — policy layer on top of ADG (e.g., {sample})"
        if c == "THIN_CANDIDATE":
            return "REVIEW — thin MV consumer; verify if policy is implicit in the MV itself"
        return "CONSIDER MV PROMOTION — uses raw edges/violations; an MV could pre-compute"


def _extract_sql_strings(tree: ast.AST) -> list[str]:
    """Return all string constants that look like SQL."""
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value
            # Heuristic: contains SELECT and FROM (or DELETE/INSERT etc.)
            if re.search(r"\bSELECT\b", v, re.IGNORECASE) and re.search(r"\bFROM\b", v, re.IGNORECASE):
                out.append(v)
    return out


def _has_wiring_gate_base(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if "_adg_wiring_gate_base" in node.module:
                return True
    return False


def analyze_gate(path: Path) -> GateAnalysis:
    # progress_bar: bounded loop — §16 exempt (small fixed-cost iteration)
    src = path.read_text(encoding="utf-8", errors="replace")
    a = GateAnalysis(path=path, loc=len(src.splitlines()))

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return a

    a.has_wiring_gate_base = _has_wiring_gate_base(tree)
    a.sql_queries = _extract_sql_strings(tree)

    # Look for MV / P-view references in source
    for sql in a.sql_queries:
        if any(p.search(sql) for p in THIN_MARKERS):
            if re.search(r"\bmv_\w+", sql, re.IGNORECASE):
                a.references_mv = True
            if re.search(r"\bv_p[0-3]_\w+", sql, re.IGNORECASE):
                a.references_pview = True

    # Look for policy markers anywhere in source
    for pat in POLICY_MARKERS:
        m = pat.search(src)
        if m:
            a.policy_evidence.append(m.group(0))
    # Dedupe
    a.policy_evidence = sorted(set(a.policy_evidence))

    return a


def main() -> int:
    print("# ADG Redundancy Audit v2 — code-based\n")

    gates = sorted(CI_DIR.rglob("check_*.py"))
    print(f"Total CI gates analyzed: {len(gates)}\n")

    results: list[GateAnalysis] = [analyze_gate(g) for g in gates]

    # Group by classification
    by_class: dict[str, list[GateAnalysis]] = {
        "NON_GRAPH": [],
        "POLICY_LAYER": [],
        "THIN_CANDIDATE": [],
        "RAW_CONSUMER": [],
    }
    for r in results:
        by_class[r.classification].append(r)

    print("## Summary\n")
    print("| Classification | Count | Action |")
    print("|----------------|-------|--------|")
    print(f"| NON_GRAPH | {len(by_class['NON_GRAPH'])} | KEEP — legitimate non-graph concern |")
    print(f"| POLICY_LAYER | {len(by_class['POLICY_LAYER'])} | KEEP — policy added on top of ADG |")
    print(f"| THIN_CANDIDATE | {len(by_class['THIN_CANDIDATE'])} | REVIEW — possibly truly redundant |")
    print(f"| RAW_CONSUMER | {len(by_class['RAW_CONSUMER'])} | CONSIDER promoting query to MV |")
    print()

    # Detailed lists
    if by_class["THIN_CANDIDATE"]:
        print("## THIN_CANDIDATE — verify each is actually redundant\n")
        print("These gates select from an MV/P-view and have NO detected policy markers.")
        print("Manual review: confirm the MV alone enforces what the gate enforces.\n")
        print("| Gate | LOC | MV/P-view |")
        print("|------|-----|-----------|")
        for r in sorted(by_class["THIN_CANDIDATE"], key=lambda x: x.path.name):
            rel = r.path.relative_to(REPO).as_posix()
            target = "MV" if r.references_mv else ("P-view" if r.references_pview else "?")
            print(f"| `{rel}` | {r.loc} | {target} |")
        print()

    if by_class["RAW_CONSUMER"]:
        print(f"## RAW_CONSUMER — {len(by_class['RAW_CONSUMER'])} gates query raw tables\n")
        print(
            "These gates use SELECT against `edges`/`violations`/`nodes` directly. "
            "An MV could pre-compute the join/aggregation. This is an ADG "
            "improvement opportunity, NOT a gate retirement.\n"
        )
        print("| Gate | LOC | Has Policy? |")
        print("|------|-----|-------------|")
        for r in sorted(by_class["RAW_CONSUMER"], key=lambda x: x.path.name):
            rel = r.path.relative_to(REPO).as_posix()
            policy = ", ".join(r.policy_evidence[:3]) if r.policy_evidence else "—"
            print(f"| `{rel}` | {r.loc} | {policy} |")
        print()

    print(f"## POLICY_LAYER — {len(by_class['POLICY_LAYER'])} gates correctly layered\n")
    print(
        "These gates consume ADG primitives AND add policy (thresholds, "
        "allowlists, ratchets, temporal deltas). Each retirement would be "
        "an enforcement loss.\n"
    )
    print("| Gate | Policy markers (sample) |")
    print("|------|--------------------------|")
    for r in sorted(by_class["POLICY_LAYER"], key=lambda x: x.path.name)[:50]:
        rel = r.path.relative_to(REPO).as_posix()
        sample = ", ".join(r.policy_evidence[:3])
        print(f"| `{rel}` | {sample} |")
    if len(by_class["POLICY_LAYER"]) > 50:
        print(f"| ... and {len(by_class['POLICY_LAYER']) - 50} more | — |")

    print(f"\n## NON_GRAPH — {len(by_class['NON_GRAPH'])} gates (no SQL)\n")
    print(
        "These gates do not execute SQL queries. They check config schema, "
        "file-format invariants, process lifecycles, or runtime behavior. "
        "Outside ADG scope by design.\n"
    )

    # ---- A12 self-check after the fix ----
    print("\n## A12 Self-Consistency After Fix\n")
    snap = next(
        (f for f in sorted(ADG_DIR.iterdir(), reverse=True) if f.suffix == ".sqlite" and "tmp" not in f.name),
        None,
    )
    if snap is not None:
        try:
            con = sqlite3.connect(snap)
            tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "gate_self_consistency" in tables:
                inconsistent = con.execute(
                    "SELECT COUNT(*) FROM gate_self_consistency WHERE consistent=0"
                ).fetchone()[0]
                total = con.execute("SELECT COUNT(*) FROM gate_self_consistency").fetchone()[0]
                print(f"Snapshot: {snap.name} — gates examined={total}, drift={inconsistent}")
                print(
                    "**Note**: A12 enricher was patched in this commit. Re-run "
                    "`python tools/generate_full_adg.py` to refresh the table; the "
                    "two prior false-positives "
                    "(`check_exception_contract.py`, `check_unused_imports_ratchet.py`) "
                    "should drop to zero."
                )
            con.close()
        except sqlite3.DatabaseError:
            print(f"Snapshot {snap.name} unreadable.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
