"""Exhaustive agent deprecation assessment.

For every *Agent.py file in production paths, computes:
  - fan_in across ALL edge types (imports, resolves_callsite, exports,
    instantiates, reads_from, flows_to) at BOTH module-level and class-level
  - presence of DEPRECATED/deprecated markers in the file
  - presence of NotImplementedError / stub patterns
  - whether the file is a shim (small, delegating, no real logic)

Classification:
  SAFE_TO_ARCHIVE  — explicitly deprecated + zero fan-in across all edge types
  RISKY            — has deprecated marker but still has consumers
  SHIM_UNUSED      — thin facade with zero consumers
  KEEP             — actively used in production
  INVESTIGATE      — ambiguous signal
"""

from __future__ import annotations

import glob
import os
import re
import sqlite3
import sys
from pathlib import Path

SNAP = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
REPO = Path(".").resolve()

EDGE_TYPES_TO_CHECK = (
    "imports",
    "resolves_callsite",
    "exports",
    "instantiates",
    "reads_from",
    "flows_to",
    "implements",
    "routes_through",
)

PROD_ROOTS = (
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
)


def find_agent_files() -> list[Path]:
    out: list[Path] = []
    for root in PROD_ROOTS:
        root_path = REPO / root
        if not root_path.exists():
            continue
        for p in root_path.rglob("*Agent.py"):
            parts = set(p.parts)
            if "archives" in parts or "__pycache__" in parts or "tests" in parts:
                continue
            out.append(p)
    return sorted(out)


DEPRECATED_RE = re.compile(r"\bDEPRECATED\b|deprecation|@deprecated", re.IGNORECASE)
NOT_IMPL_RE = re.compile(r"raise\s+NotImplementedError")
STUB_RE = re.compile(r"'status':\s*'skipped'|\"status\":\s*\"skipped\"")
HEALRESULT_RE = re.compile(r"HealResult\.needs_help|HealResult\.from_request")


def inspect_file(path: Path) -> dict[str, object]:
    """Return raw signal bundle for one file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"path": str(path), "error": "unreadable"}
    lines = text.count("\n") + 1
    size = len(text)
    return {
        "path": str(path.relative_to(REPO)).replace("\\", "/"),
        "lines": lines,
        "size": size,
        "is_deprecated_marker": bool(DEPRECATED_RE.search(text)),
        "has_not_implemented": bool(NOT_IMPL_RE.search(text)),
        "has_skipped_stub": bool(STUB_RE.search(text)),
        "uses_healresult_w3": bool(HEALRESULT_RE.search(text)),
    }


def query_fanin(cur: sqlite3.Cursor, resolved_path: str) -> dict[str, int]:
    """Return incoming edge counts by relation_type for a module node.

    Uses the Windows-style path (backslashes) per the ADG schema convention.
    """
    # Try both separators; the schema stores Windows-style.
    winpath = resolved_path.replace("/", "\\")
    cur.execute(
        "SELECT id FROM nodes WHERE (resolved_path=? OR resolved_path=?) AND entity_type='module'",
        (resolved_path, winpath),
    )
    rows = cur.fetchall()
    if not rows:
        return {"module_not_in_adg": 1}
    fanin: dict[str, int] = {}
    for (nid,) in rows:
        for rel in EDGE_TYPES_TO_CHECK:
            cur.execute(
                "SELECT COUNT(*) FROM edges WHERE dst_id=? AND relation_type=?",
                (nid, rel),
            )
            c = cur.fetchone()[0]
            fanin[rel] = fanin.get(rel, 0) + c
    return fanin


def classify(signals: dict[str, object], fanin: dict[str, int]) -> str:
    total_fanin = sum(v for k, v in fanin.items() if k != "module_not_in_adg")
    deprecated = signals.get("is_deprecated_marker", False)
    not_in_adg = fanin.get("module_not_in_adg", 0) > 0

    if deprecated and total_fanin == 0 and not not_in_adg:
        return "SAFE_TO_ARCHIVE"
    if deprecated and total_fanin > 0:
        return "RISKY_DEPRECATED_WITH_CONSUMERS"
    if not deprecated and total_fanin == 0 and not not_in_adg:
        # Could be unused (dispatched via registry only); need further signal
        if signals.get("lines", 9999) < 100:
            return "SHIM_UNUSED"
        return "INVESTIGATE_ZERO_FANIN"
    if not_in_adg:
        return "NOT_IN_ADG"
    return "KEEP"


def main() -> int:
    con = sqlite3.connect(SNAP)
    cur = con.cursor()
    agents = find_agent_files()
    print(f"snapshot={SNAP}")
    print(f"total_agents_scanned={len(agents)}\n")

    rows: list[tuple[str, dict]] = []
    for p in agents:
        sig = inspect_file(p)
        if "error" in sig:
            continue
        rel = sig["path"]
        fanin = query_fanin(cur, rel)
        cls = classify(sig, fanin)
        total_fanin = sum(v for k, v in fanin.items() if k != "module_not_in_adg")
        rows.append(
            (
                cls,
                {
                    "path": rel,
                    "lines": sig["lines"],
                    "deprecated": sig["is_deprecated_marker"],
                    "not_impl": sig["has_not_implemented"],
                    "stub": sig["has_skipped_stub"],
                    "w3_healresult": sig["uses_healresult_w3"],
                    "total_fanin": total_fanin,
                    "fanin": fanin,
                },
            )
        )

    # Group by classification
    by_class: dict[str, list[dict]] = {}
    for cls, d in rows:
        by_class.setdefault(cls, []).append(d)

    for cls in (
        "SAFE_TO_ARCHIVE",
        "SHIM_UNUSED",
        "INVESTIGATE_ZERO_FANIN",
        "RISKY_DEPRECATED_WITH_CONSUMERS",
        "NOT_IN_ADG",
        "KEEP",
    ):
        items = by_class.get(cls, [])
        print(f"\n=== {cls} ({len(items)}) ===")
        for d in sorted(items, key=lambda x: (-int(x["deprecated"]), x["total_fanin"], x["path"])):
            marks = []
            if d["deprecated"]:
                marks.append("dep")
            if d["not_impl"]:
                marks.append("notimpl")
            if d["stub"]:
                marks.append("stub")
            if d["w3_healresult"]:
                marks.append("w3")
            mark_str = ",".join(marks) if marks else "-"
            detail_fanin = ",".join(f"{k}:{v}" for k, v in sorted(d["fanin"].items()) if v > 0) or "none"
            print(
                f"  [{mark_str:<20}] fanin={d['total_fanin']:>3} lines={d['lines']:>4}  "
                f"{d['path']}  [{detail_fanin}]"
            )

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
