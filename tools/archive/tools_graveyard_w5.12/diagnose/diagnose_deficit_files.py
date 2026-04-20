"""Diagnose the exact state of each deficit file.

Categories:
A) emit funcs in AST calls (already wired correctly — ADG gap is due to stale scan)
B) emit funcs in docstring text only (wirer placed inside docstring)
C) emit funcs as truncated/damaged import lines (wirer broke the file)
D) emit funcs completely absent (never wired)
"""

import ast
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAPS_CSV = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"

CONTRACT = "agentic_core.runtime.lifecycle_trace_contract"
EMIT_FUNCS = [
    "emit_replay_key",
    "emit_determinism_digest",
    "_emit_applies_guardrail",
    "_emit_snapshots_state",
    "_emit_signs_execution_trace",
    "_emit_records_execution_trace",
    "_emit_reads_policy_state",
]


def get_module_docstring_text(lines):
    """Get the raw text inside the module docstring."""
    i = 0
    while i < len(lines) and (lines[i].strip() == "" or lines[i].strip().startswith("#!")):
        i += 1
    if i >= len(lines):
        return ""
    s = lines[i].strip()
    if not (s.startswith('"""') or s.startswith("'''")):
        return ""
    quote = s[:3]
    rest = s[3:]
    if rest.endswith(quote) and len(rest) > len(quote):
        return rest  # single-line
    doc_lines = []
    j = i + 1
    while j < len(lines):
        if quote in lines[j]:
            break
        doc_lines.append(lines[j])
        j += 1
    return "\n".join(doc_lines)


def ast_called_funcs(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:  # guardian: allow-silent-swallow - acceptable exception handling
        return set()
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                called.add(f.id)
            elif isinstance(f, ast.Attribute):
                called.add(f.attr)
    return called


rows = list(csv.DictReader(open(GAPS_CSV)))
print(f"Diagnosing {len(rows)} deficit modules\n")

counts = {"A_in_ast": 0, "B_in_docstring": 0, "C_damaged": 0, "D_absent": 0}
cat_B = []
cat_C = []
cat_D = []

for row in rows:
    fp = PROJECT_ROOT / row["source_file"]
    if not fp.exists():
        continue
    missing = row["missing_dimensions"].split("|")
    src = fp.read_text(encoding="utf-8", errors="ignore")
    lines = src.split("\n")
    doc_text = get_module_docstring_text(lines)
    called = ast_called_funcs(src)

    for dim in missing:
        # Map dim to func name
        func_map = {
            "emits_replay_key": "emit_replay_key",
            "emits_determinism_digest": "emit_determinism_digest",
            "applies_guardrail": "_emit_applies_guardrail",
            "snapshots_state": "_emit_snapshots_state",
            "signs_execution_trace": "_emit_signs_execution_trace",
            "records_execution_trace": "_emit_records_execution_trace",
            "reads_policy_state": "_emit_reads_policy_state",
        }
        func = func_map.get(dim)
        if not func:
            continue

        if func in called:
            counts["A_in_ast"] += 1
        elif func in doc_text:
            counts["B_in_docstring"] += 1
            if (row["source_file"], dim) not in [(x[0], x[1]) for x in cat_B]:
                cat_B.append((row["source_file"], dim, func))
        elif func in src:
            # In source but not in docstring and not in AST — damaged line
            counts["C_damaged"] += 1
            # Find the line
            for i, line in enumerate(lines):
                if func in line and "import" in line and CONTRACT in line:
                    cat_C.append((row["source_file"], dim, func, f"line {i}: {repr(line[:100])}"))
                    break
        else:
            counts["D_absent"] += 1
            cat_D.append((row["source_file"], dim, func))

print(f"A (in AST — fine):       {counts['A_in_ast']}")
print(f"B (in docstring — bad):  {counts['B_in_docstring']}")
print(f"C (damaged import):      {counts['C_damaged']}")
print(f"D (absent — never wired): {counts['D_absent']}")

print("\n--- Category B (first 10 unique files) ---")
seen = set()
for path, dim, func in cat_B[:30]:
    if path not in seen:
        print(f"  {path}")
        seen.add(path)
    if len(seen) >= 10:
        break

print("\n--- Category C (damaged) ---")
for path, dim, func, info in cat_C[:20]:
    print(f"  {path}  [{dim}]  {info}")

print("\n--- Category D (absent) ---")
for path, dim, func in cat_D[:20]:
    print(f"  {path}  [{dim}]")
