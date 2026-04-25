"""Part A final scope — join violations with edges to get pattern kind."""

import sqlite3
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04212026_1441.sqlite")
REPO = Path(r"C:\Git\Agentic-Workflow")
con = sqlite3.connect(str(DB))

# Full pattern-kind distribution on surface files
q = """
SELECT e.edge_kind, e.semantic_type, v.severity, COUNT(*)
FROM violations v
JOIN edges e ON e.id = v.edge_id
WHERE v.file_path LIKE 'agentic_core/L0_routing/%'
   OR v.file_path LIKE 'agentic_core/L4_state/%'
   OR v.file_path LIKE 'agentic_core/L5_safety/%'
GROUP BY e.edge_kind, e.semantic_type, v.severity
ORDER BY COUNT(*) DESC
"""
print("edge_kind | semantic_type | severity | count")
for row in con.execute(q):
    print(f"  {row[0]!s:<30s} {row[1]!s:<25s} {row[2]!s:<8s} {row[3]:>4d}")

# ADR-024 Part B target pattern kinds
TARGET_KINDS = {
    "broad_exception_catch",
    "silent_exception_swallow",
    "log_and_swallow",
    "partial_side_effects",
    "default_fallback_masking",
    "retry_without_backoff",
    "return_none_swallow",
}

print()
print("=== ADR-024 Part A candidate sites (target kinds × L0/L4/L5) ===")
q2 = """
SELECT v.id, e.edge_kind, v.file_path, v.line_no, v.severity, v.disposition
FROM violations v
JOIN edges e ON e.id = v.edge_id
WHERE e.edge_kind IN ({})
  AND (v.file_path LIKE 'agentic_core/L0_routing/%'
    OR v.file_path LIKE 'agentic_core/L4_state/%'
    OR v.file_path LIKE 'agentic_core/L5_safety/%')
ORDER BY v.file_path, v.line_no
""".format(",".join("?" * len(TARGET_KINDS)))

rows = list(con.execute(q2, tuple(TARGET_KINDS)))
print(f"Total: {len(rows)} sites")
by_kind = Counter(r[1] for r in rows)
print("By kind:")
for k, c in by_kind.most_common():
    print(f"  {k:<30s} {c:>4d}")

# Check guardian coverage per site
guardian_rx = re.compile(r"#\s*guardian:\s*allow-([\w-]+)(?:\s*--\s*(\S.*))?")
needs_work: list[dict] = []
for vid, kind, fp, ln, sev, disp in rows:
    p = REPO / fp
    if not p.exists():
        continue
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    covered = False
    for check_ln in (ln, ln - 1, ln + 1, ln + 2, ln + 3):
        if 1 <= check_ln <= len(lines):
            m = guardian_rx.search(lines[check_ln - 1])
            if m and m.group(2):
                covered = True
                break
    if not covered:
        needs_work.append({"id": vid, "kind": kind, "file": fp, "line": ln, "sev": sev})

print()
print(f"=== Uncovered (needs guardian+justification): {len(needs_work)} ===")
by_file: dict[str, list[dict]] = defaultdict(list)
for s in needs_work:
    by_file[s["file"]].append(s)

print(f"Files: {len(by_file)}")
print()
print("Top 20 files by uncovered count:")
for fp, sites in sorted(by_file.items(), key=lambda x: -len(x[1]))[:20]:
    kinds = Counter(s["kind"] for s in sites)
    print(f"  {len(sites):>3d}  {fp}  {dict(kinds)}")

out = REPO / "tools/debug/_adg_part_a_final_scope.json"
out.write_text(
    json.dumps(
        {
            "snapshot": "04212026_1441",
            "total_candidate_sites": len(rows),
            "uncovered_sites": len(needs_work),
            "by_file": {fp: [s for s in sites] for fp, sites in by_file.items()},
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"\nWrote: {out}")
