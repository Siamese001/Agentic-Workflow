"""
Analyse the hardcoded SSOT violations JSON and categorise findings.
Outputs a structured report to artifacts/adg/ssot_violation_report.md
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "artifacts" / "adg" / "hardcoded_ssot_violations.json"
OUT = ROOT / "artifacts" / "adg" / "ssot_violation_report.md"
data: dict = json.loads(DATA.read_text(encoding="utf-8"))
by_const: dict = defaultdict(list)
genuine: list = []
path_prefix: list = []
for fpath, hits in data.items():
    for h in hits:
        lit = h["literal"]
        text = h["text"]
        pat_standalone = re.compile("['\"]" + re.escape(lit) + "['\"]")
        # guardian: allow-path-string
        pat_prefix = re.compile("['\"]" + re.escape(lit) + "/")
        is_standalone = bool(pat_standalone.search(text))
        is_prefix = bool(pat_prefix.search(text))
        entry = {"file": fpath, "line": h["line"], "const": h["const"], "lit": lit, "text": text[:120]}
        by_const[h["const"]].append(entry)
        if is_prefix and (not is_standalone):
            path_prefix.append(entry)
        else:
            genuine.append(entry)
total_files = len(data)
total_hits = sum(len(v) for v in data.values())
const_counts = {c: len(v) for c, v in by_const.items()}
lines: list[str] = []
a = lines.append
a("# SSOT Hardcoded Path Violations Report")
a("")
a(
    f"**Total files:** {total_files}  |  **Total hits:** {total_hits}  |  **Standalone (clear):** {len(genuine)}  |  **Path-prefix (ambiguous):** {len(path_prefix)}"
)
a("")
a("## Hit Count by Constant")
a("")
a("| Constant | Files |")
a("|----------|-------|")
for c, cnt in sorted(const_counts.items(), key=lambda x: -x[1]):
    a(f"| `{c}` | {cnt} |")
a("")
a("## Genuine Standalone Violations (top 60)")
a("")
a("These lines use a bare quoted string that exactly matches an SSOT constant value.  ")
a("**Fix:** import the constant and replace the literal.")
a("")
a("| File | Line | Constant | Text |")
a("|------|------|----------|------|")
for e in genuine[:60]:
    safe = e["text"].replace("|", "\\|")
    a(f"| `{e['file']}` | {e['line']} | `{e['const']}` | `{safe}` |")
a("")
a("## Path-Prefix Violations (top 40)")
a("")
a(
    'These lines use a hardcoded path that begins with the SSOT literal, e.g. `"agentic_core/L2_execution/foo.py"`.  '
)
a("**Fix:** use `Path(AGENTIC_CORE_DIR) / 'L2_execution/foo.py'` or import the appropriate sub-dir constant.")
a("")
a("| File | Line | Constant | Text |")
a("|------|------|----------|------|")
for e in path_prefix[:40]:
    safe = e["text"].replace("|", "\\|")
    a(f"| `{e['file']}` | {e['line']} | `{e['const']}` | `{safe}` |")
a("")
a("## ARCHIVES_DIR Violations (all)")
a("")
a('Files referencing `"archives"` without importing `ARCHIVES_DIR`:')
a("")
for e in by_const.get("ARCHIVES_DIR", []):
    a(f"- `{e['file']}:{e['line']}` — `{e['text'][:100]}`")
a("")
a("## DOCS_REPORTS_PLANS Violations (all)")
a("")
for e in by_const.get("DOCS_REPORTS_PLANS", []):
    a(f"- `{e['file']}:{e['line']}` — `{e['text'][:100]}`")
a("")
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Report written to: {OUT}")
print(f"Total files: {total_files}  hits: {total_hits}")
print(f"Genuine standalone: {len(genuine)}  Path-prefix: {len(path_prefix)}")
print()
print("BY CONSTANT (files):")
for c, cnt in sorted(const_counts.items(), key=lambda x: -x[1]):
    print(f"  {c:<30s} {cnt}")
