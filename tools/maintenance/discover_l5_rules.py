#!/usr/bin/env python3
"""
discover_l5_rules.py — Scaffold G15 hard-vs-remediable rule annotation.

Per ADR-070 G15 — every L5 enforcement rule must be tagged HARD or REMEDIABLE.
With ~700 candidate rules across 97 enforcement modules, manual annotation is
the right scope but the work needs a CSV scaffold. This tool:

1. Walks `agentic_core/L5_safety/enforcement/` and `v5/` rule modules
2. Discovers rule-like callables — functions/methods named:
     - check_*, validate_*, enforce_*, assert_*, verify_*
     - any function decorated with @rule, @enforcement_rule
3. Heuristically infers a starting disposition based on rule name keywords:
     - "block", "deny", "reject", "forbid", "halt", "fail" → HARD
     - "warn", "redact", "sanitize", "repair", "heal" → REMEDIABLE
     - else → UNTAGGED (annotator must decide)
4. Emits CSV at `docs/reports/maintenance/g15_rule_disposition_scaffold.csv`
   with columns: rule_id, module, function_name, family_guess, disposition_guess, rationale

The CSV is the human-editable artifact. After review, a sibling loader
populates a registry consumed by the runtime gates. The loader is a
follow-up phase; this script ships the SCAFFOLDING.

Exit codes:
    0 = scaffold written
    1 = no rules discovered (likely a path bug)
    2 = invalid environment (missing dirs)
"""

from __future__ import annotations

import argparse
import ast
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCAN_ROOTS = [
    REPO_ROOT / "agentic_core" / "L5_safety" / "enforcement",
    REPO_ROOT / "agentic_core" / "L5_safety" / "v5",
    REPO_ROOT / "agentic_core" / "L5_safety" / "runtime_gates",
    REPO_ROOT / "agentic_core" / "L5_safety" / "validators",
]
DEFAULT_OUT = REPO_ROOT / "docs" / "reports" / "maintenance" / "g15_rule_disposition_scaffold.csv"

_RULE_NAME_PATTERNS = [
    re.compile(r"^check_"),
    re.compile(r"^validate_"),
    re.compile(r"^enforce_"),
    re.compile(r"^assert_"),
    re.compile(r"^verify_"),
    re.compile(r"^ensure_"),
    re.compile(r"_rule$"),
    re.compile(r"_check$"),
]
_RULE_DECORATOR_NAMES = {"rule", "enforcement_rule", "guardrail_rule"}

# Heuristic keyword maps
_HARD_KW = ("block", "deny", "reject", "forbid", "halt", "fail_closed",
            "must_not", "abort", "panic", "kill")
_REMEDIABLE_KW = ("warn", "redact", "sanitize", "repair", "heal", "remediate",
                  "quarantine", "soft_fail", "advisory")

# G-id classification by path fragment (mirrors dump_l5_guardrail_catalog logic)
_G_ID_BY_PATH: tuple[tuple[str, str], ...] = (
    ("a2a", "G05"), ("permissions", "G06"), ("token_rotation", "G07"),
    ("egress", "G08"), ("redteam", "G11"), ("sanitization", "G13"),
    ("rules", "G15"), ("runtime_gates", "G01"), ("v5", "G16"),
    ("structure_blueprint", "G17"), ("validators", "G18"),
    ("contracts", "G19"), ("enforcement", "G02"),
)


def _is_rule_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    if any(p.search(node.name) for p in _RULE_NAME_PATTERNS):
        return True
    for dec in node.decorator_list:
        # @rule or @enforcement_rule (bare name)
        if isinstance(dec, ast.Name) and dec.id in _RULE_DECORATOR_NAMES:
            return True
        # @something.rule
        if isinstance(dec, ast.Attribute) and dec.attr in _RULE_DECORATOR_NAMES:
            return True
    return False


def _infer_family(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix().lower()
    for frag, gid in _G_ID_BY_PATH:
        if frag in rel:
            return gid
    return "G_UNCLASSIFIED"


def _infer_disposition(name: str, docstring: str) -> tuple[str, str]:
    """Returns (disposition_guess, rationale)."""
    haystack = (name + " " + (docstring or "")).lower()
    if any(kw in haystack for kw in _HARD_KW):
        return ("HARD", f"Name/doc contains hard-fail keyword in {_HARD_KW}")
    if any(kw in haystack for kw in _REMEDIABLE_KW):
        return ("REMEDIABLE", f"Name/doc contains remediation keyword in {_REMEDIABLE_KW}")
    return ("UNTAGGED", "No keyword match — human must decide")


def _scan_file(path: Path) -> list[dict[str, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []

    rows: list[dict[str, str]] = []
    family = _infer_family(path)
    rel = path.relative_to(REPO_ROOT).as_posix()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _is_rule_function(node):
            continue
        docstring = ast.get_docstring(node) or ""
        guess, rationale = _infer_disposition(node.name, docstring)
        rows.append({
            "rule_id": f"{family}-{path.stem}-{node.name}",
            "module": rel,
            "function_name": node.name,
            "line": str(node.lineno),
            "family_guess": family,
            "disposition_guess": guess,
            "rationale": rationale,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="G15 rule discovery scaffold")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary", action="store_true",
                        help="Print summary table by family + disposition")
    args = parser.parse_args()

    valid_roots = [r for r in DEFAULT_SCAN_ROOTS if r.exists()]
    if not valid_roots:
        print("ERROR: no scan roots exist on disk", file=sys.stderr)
        return 2

    all_rows: list[dict[str, str]] = []
    for root in valid_roots:
        for py_file in root.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            all_rows.extend(_scan_file(py_file))

    if not all_rows:
        print("ERROR: no rule-shaped functions discovered", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["rule_id", "module", "function_name", "line",
                  "family_guess", "disposition_guess", "rationale"]
    with args.out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(all_rows, key=lambda r: (r["family_guess"], r["module"], int(r["line"]))):
            writer.writerow(row)

    print(f"  Discovered {len(all_rows)} rule-shaped functions")
    print(f"  Scaffold written: {args.out.relative_to(REPO_ROOT)}")

    if args.summary:
        from collections import Counter
        fam_counts = Counter(r["family_guess"] for r in all_rows)
        disp_counts = Counter(r["disposition_guess"] for r in all_rows)
        print("\n  By family:")
        for fam, c in sorted(fam_counts.items(), key=lambda x: -x[1]):
            print(f"    {fam:20s} {c:>4d}")
        print("\n  By disposition guess:")
        for d, c in sorted(disp_counts.items(), key=lambda x: -x[1]):
            print(f"    {d:12s} {c:>4d}")
        untagged = disp_counts.get("UNTAGGED", 0)
        if untagged:
            print(f"\n  {untagged} rule(s) need human disposition decision.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
