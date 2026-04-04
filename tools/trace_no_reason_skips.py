#!/usr/bin/env python3
"""Trace the 2,381 no-reason skip calls to understand their actual pattern."""

import ast
from collections import Counter
from pathlib import Path


class SkipCallVisitor(ast.NodeVisitor):
    def __init__(self, filepath, source_lines):
        self.filepath = filepath
        self.source_lines = source_lines
        self.findings = []
        self.current_func = None
        self.current_class = None

    def visit_ClassDef(self, node):
        old = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old

    def visit_FunctionDef(self, node):
        old = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        func_name = None
        if isinstance(node.func, ast.Attribute) and node.func.attr == "skip":
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest":
                func_name = "pytest.skip"
        elif isinstance(node.func, ast.Name) and node.func.id == "skip":
            func_name = "skip"

        if func_name:
            # Get reason
            reason = ""
            if node.args and isinstance(node.args[0], ast.Constant):
                reason = str(node.args[0].value)
            for kw in node.keywords:
                if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                    reason = str(kw.value.value)

            # Get context (lines around the skip call)
            line = node.lineno
            start = max(0, line - 4)
            end = min(len(self.source_lines), line + 1)
            context = "\n".join(self.source_lines[start:end])

            # Detect the condition
            condition = "unknown"
            if "_mod is None" in context:
                condition = "_mod_is_None"
            elif "is None" in context:
                condition = "something_is_None"
            elif "not available" in context.lower():
                condition = "not_available_check"
            elif "ImportError" in context:
                condition = "import_error_catch"

            self.findings.append({
                "file": self.filepath,
                "line": line,
                "func": f"{self.current_class}::{self.current_func}" if self.current_class else self.current_func,
                "reason": reason,
                "condition": condition,
                "context_snippet": context[:200],
            })

        self.generic_visit(node)


all_findings = []
for p in sorted(Path("tests").rglob("*.py")):
    try:
        source = p.read_text("utf-8")
        tree = ast.parse(source)
        source_lines = source.splitlines()
        visitor = SkipCallVisitor(str(p).replace("\\", "/"), source_lines)
        visitor.visit(tree)
        all_findings.extend(visitor.findings)
    except Exception:
        pass

# Separate no-reason vs with-reason
no_reason = [f for f in all_findings if not f["reason"]]
with_reason = [f for f in all_findings if f["reason"]]

print(f"Total skip calls found: {len(all_findings)}")
print(f"  With reason: {len(with_reason)}")
print(f"  Without reason: {len(no_reason)}")

# Analyze conditions for no-reason skips
condition_counter = Counter()
for f in no_reason:
    condition_counter[f["condition"]] += 1

print("\nNo-reason skip conditions:")
for c, count in condition_counter.most_common():
    print(f"  {c}: {count}")

# Show samples of each condition type
print("\n" + "=" * 70)
print("SAMPLE: _mod_is_None pattern (first 3)")
print("=" * 70)
for f in [x for x in no_reason if x["condition"] == "_mod_is_None"][:3]:
    print(f"\n  {f['file']}:{f['line']} in {f['func']}")
    print(f"  Context:\n    {f['context_snippet'][:300]}")

print("\n" + "=" * 70)
print("SAMPLE: something_is_None pattern (first 5)")
print("=" * 70)
for f in [x for x in no_reason if x["condition"] == "something_is_None"][:5]:
    print(f"\n  {f['file']}:{f['line']} in {f['func']}")
    print(f"  Context:\n    {f['context_snippet'][:300]}")

print("\n" + "=" * 70)
print("SAMPLE: unknown condition (first 5)")
print("=" * 70)
for f in [x for x in no_reason if x["condition"] == "unknown"][:5]:
    print(f"\n  {f['file']}:{f['line']} in {f['func']}")
    print(f"  Context:\n    {f['context_snippet'][:300]}")

# Count unique files for no-reason skips
no_reason_files = Counter()
for f in no_reason:
    no_reason_files[f["file"]] += 1

print(f"\n\nUnique files with no-reason skips: {len(no_reason_files)}")
print("Top 20:")
for filepath, count in no_reason_files.most_common(20):
    print(f"  {count:3d}  {filepath}")

# Check: are the "unknown" ones actually in conftest or module-level?
unknown_skips = [f for f in no_reason if f["condition"] == "unknown"]
funcs_counter = Counter()
for f in unknown_skips:
    funcs_counter[f["func"] or "<module-level>"] += 1

print("\nUnknown-condition skips by function name (top 20):")
for func, count in funcs_counter.most_common(20):
    print(f"  {count:3d}  {func}")
