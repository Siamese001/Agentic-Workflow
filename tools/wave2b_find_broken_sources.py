#!/usr/bin/env python3
"""
Wave 2b: Find all source modules with IndentationError/SyntaxError and extract
the exact broken lines for surgical repair.
"""

from pathlib import Path

# Source modules from the error report
INDENT_ERROR_MODULES = [
    ("agentic_core/L5_safety/reasoning/FileClassificationAgent.py", 178),
    ("agentic_core/L0_routing/scripts/execute_ssot.py", 129),
    ("agentic_core/L0_routing/scripts/execution_context.py", 188),
    ("agentic_core/L0_routing/scripts/forensic_discovery_prep.py", 234),
    ("agentic_core/L0_routing/utils/complexity_visitor_util.py", 122),
    ("agentic_core/L2_execution/healers/healing_provider_adapters.py", 110),
    ("agentic_core/L2_execution/tools/file_io_impl.py", 96),
    ("agentic_core/L3_orchestration/engines/dag_manager.py", 10),
    ("agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py", 182),
]

SYNTAX_ERROR_MODULES = [
    ("agentic_core/L0_routing/utils/component_util.py", 230),
    ("agentic_core/prompt_governance/security/validators/output_schema_validator.py", 219),
    ("agentic_core/L5_safety/enforcement/AdapterBase.py", 286),
    ("agentic_core/L5_safety/reasoning/hierarchy_healer.py", 377),
]


def analyze_broken_except(filepath, error_line):
    """Look at the broken except block and show context."""
    p = Path(filepath)
    if not p.exists():
        return None

    lines = p.read_text("utf-8").splitlines()
    # Show 10 lines around the error
    start = max(0, error_line - 6)
    end = min(len(lines), error_line + 5)

    context = []
    for i in range(start, end):
        marker = ">>>" if i + 1 == error_line else "   "
        context.append(f"{marker} {i + 1:4d} | {lines[i]}")

    return {
        "file": filepath,
        "error_line": error_line,
        "total_lines": len(lines),
        "context": "\n".join(context),
    }


# Also scan for ALL broken source files systematically
def find_all_broken_sources():
    """Compile-check every .py in agentic_core/ to find all syntax issues."""
    broken = []
    root = Path("agentic_core")
    for p in sorted(root.rglob("*.py")):
        try:
            source = p.read_text("utf-8")
            compile(source, str(p), "exec")
        except SyntaxError as e:
            broken.append(
                {
                    "file": str(p).replace("\\", "/"),
                    "line": e.lineno,
                    "error": str(e),
                    "type": type(e).__name__,
                }
            )
    return broken


print("=" * 70)
print("KNOWN INDENTATION ERRORS")
print("=" * 70)
for filepath, line in INDENT_ERROR_MODULES:
    result = analyze_broken_except(filepath, line)
    if result:
        print(f"\n{result['file']}:{result['error_line']} ({result['total_lines']} lines)")
        print(result["context"])

print("\n" + "=" * 70)
print("KNOWN SYNTAX ERRORS")
print("=" * 70)
for filepath, line in SYNTAX_ERROR_MODULES:
    result = analyze_broken_except(filepath, line)
    if result:
        print(f"\n{result['file']}:{result['error_line']} ({result['total_lines']} lines)")
        print(result["context"])

print("\n" + "=" * 70)
print("FULL SCAN: ALL BROKEN SOURCE FILES IN agentic_core/")
print("=" * 70)
all_broken = find_all_broken_sources()
print(f"Total broken source files: {len(all_broken)}")
for b in all_broken:
    print(f"  {b['file']}:{b['line']} [{b['type']}] {b['error'][:80]}")
