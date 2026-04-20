"""Check if wired emit calls are inside docstrings (bad placement)."""

import ast
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
gaps_csv = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"

EMIT_FUNCS = {
    "emit_replay_key",
    "emit_determinism_digest",
    "_emit_applies_guardrail",
    "_emit_snapshots_state",
    "_emit_signs_execution_trace",
    "_emit_records_execution_trace",
    "_emit_reads_policy_state",
}

bad_placement = []
good_placement = []
no_emits = []

rows = list(csv.DictReader(open(gaps_csv)))
print(f"Checking {len(rows)} deficit modules...\n")

for row in rows:
    src_path = PROJECT_ROOT / row["source_file"]
    if not src_path.exists():
        continue

    src = src_path.read_text(encoding="utf-8", errors="ignore")
    missing = row["missing_dimensions"].split("|")

    # Check which missing dims are in source text
    present_in_text = {f for f in EMIT_FUNCS if f in src}
    missing_funcs = set()
    for dim in missing:
        if dim == "emits_replay_key":
            missing_funcs.add("emit_replay_key")
        elif dim == "emits_determinism_digest":
            missing_funcs.add("emit_determinism_digest")
        elif dim == "applies_guardrail":
            missing_funcs.add("_emit_applies_guardrail")
        elif dim == "snapshots_state":
            missing_funcs.add("_emit_snapshots_state")
        elif dim == "signs_execution_trace":
            missing_funcs.add("_emit_signs_execution_trace")
        elif dim == "records_execution_trace":
            missing_funcs.add("_emit_records_execution_trace")

    if not missing_funcs & present_in_text:
        no_emits.append(row["source_file"])
        continue

    # Parse AST and check if emits appear as actual call statements
    try:
        tree = ast.parse(src)
    except SyntaxError:  # guardian: allow-silent-swallow - acceptable exception handling
        bad_placement.append((row["source_file"], "SYNTAX_ERROR"))
        continue

    # Walk all call nodes and collect function names
    called_funcs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                called_funcs.add(func.id)
            elif isinstance(func, ast.Attribute):
                called_funcs.add(func.attr)

    # Check if missing dims are called in AST
    not_in_ast = missing_funcs & present_in_text - called_funcs
    if not_in_ast:
        bad_placement.append((row["source_file"], f"in_text_not_in_ast: {sorted(not_in_ast)}"))
    else:
        good_placement.append(row["source_file"])

print(f"BAD PLACEMENT (in source text but NOT in AST calls): {len(bad_placement)}")
for path, reason in bad_placement[:30]:
    print(f"  {path}  [{reason}]")

print(f"\nGOOD PLACEMENT (in AST calls): {len(good_placement)}")
print(f"\nNO EMITS IN SOURCE: {len(no_emits)}")
for p in no_emits[:20]:
    print(f"  {p}")
