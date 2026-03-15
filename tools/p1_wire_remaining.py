"""Wire the 4 remaining files that were skipped by the P1 wirer."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES_TO_WIRE = {
    "agentic_core/L0_routing/config/path_constants.py": "L0",
    "agentic_core/L0_routing/config/ssot_tier_constants.py": "L0",
    "agentic_core/L5_safety/config/structure_blueprint/_constants.py": "L5",
    "agentic_core/L5_safety/config/structure_blueprint_config.py": "L5",
}

IMPORTS = [
    "from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_policy_state  # noqa: E402",
    "from agentic_core.runtime.lifecycle_trace_contract import _emit_escalates_to_human  # noqa: E402",
    "from agentic_core.runtime.lifecycle_trace_contract import _emit_routes_through  # noqa: E402",
    "from agentic_core.runtime.lifecycle_trace_contract import _emit_dispatches_healing_run  # noqa: E402",
]


def wire_file(relpath, layer):
    fp = str(ROOT / relpath)
    basename = Path(relpath).stem

    with open(fp, encoding="utf-8", errors="replace") as f:
        src = f.read()

    calls = [
        f'_emit_reads_policy_state("p1", "{basename}", "{layer}")',
        f'_emit_escalates_to_human("p1", "{basename}", "{layer}")',
        f'_emit_routes_through("p1", "{basename}", "{layer}")',
        f'_emit_dispatches_healing_run("p1", "{basename}", "{layer}")',
    ]

    lines = src.split("\n")

    # Find end of docstring or imports
    in_triple = False
    triple_char = None
    last_import = -1
    docstring_end = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_triple:
            for q in ('"""', "'''"):
                if stripped.startswith(q):
                    triple_char = q
                    rest = stripped[3:]
                    if triple_char in rest:
                        if docstring_end < 0:
                            docstring_end = i
                        break
                    else:
                        in_triple = True
                    break
            if not in_triple and stripped.startswith(("import ", "from ")):
                last_import = i
        else:
            if triple_char in stripped:
                in_triple = False
                docstring_end = i

    insert_idx = max(last_import, docstring_end) + 1
    if insert_idx <= 0:
        insert_idx = 0

    insert_lines = IMPORTS + calls
    for j, il in enumerate(insert_lines):
        lines.insert(insert_idx + j, il)

    new_src = "\n".join(lines)

    try:
        ast.parse(new_src)
    except SyntaxError as e:
        return "ERROR", f"line {e.lineno}: {e.msg}"

    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_src)

    return "WIRED", f"8 lines inserted at line {insert_idx + 1}"


def main():
    for relpath, layer in FILES_TO_WIRE.items():
        status, detail = wire_file(relpath, layer)
        print(f"  {status}: {relpath} ({detail})")


if __name__ == "__main__":
    main()
