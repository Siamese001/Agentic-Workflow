"""Add 'from __future__ import annotations' to files that have undefined type annotations.

This defers ALL annotation evaluation, preventing NameErrors for type hints that
reference undefined symbols (RefinementResult, ScoreResult, FormatResult, etc.).

Safe: inserts as FIRST statement after docstring. Never modifies existing code.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"

# Known undefined type annotation symbols from the error analysis
UNDEFINED_TYPES = {
    "RefinementResult", "ScoreResult", "ExecutionResult", "FormatResult",
    "DiagnosticReport", "OperationResult", "RetrievalResult", "ValidationResult",
    "SystemEvent", "RoutingPolicy", "RGFlowRouter", "Provider", "AgentRole",
    "RateLimitMixin", "RetryResult", "SignalAssessment", "CircuitBreaker",
    "WorkflowOrchestrator", "SubatomicHopConfig", "EngineType", "ReasoningMode",
}

fixed = 0

for base in ["agentic_core", "apps_shared", "apps_lic", "apps_rg", "system_learning"]:
    scan = os.path.join(ROOT, base)
    if not os.path.isdir(scan):
        continue
    for dp, _, fns in os.walk(scan):
        for fn in fns:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dp, fn)
            try:
                with open(fp, encoding="utf-8") as f:
                    content = f.read()
            except (ValueError, TypeError, RuntimeError) as e:
                continue

            # Skip if already has from __future__ import annotations
            if "from __future__ import annotations" in content:
                continue

            # Check if any undefined type is used as annotation
            needs_fix = False
            for sym in UNDEFINED_TYPES:
                # Type annotation patterns: -> Sym, : Sym, : Sym =
                if re.search(r'(?:->|:)\s*' + re.escape(sym) + r'\b', content):
                    # Make sure it's not imported or defined
                    if f"import {sym}" in content or f"class {sym}" in content:
                        continue
                    if re.search(r'^\s+' + re.escape(sym) + r'\s*[,)]', content, re.MULTILINE):
                        continue
                    needs_fix = True
                    break

            if not needs_fix:
                continue

            lines = content.split("\n")

            # Find insertion point: right after docstring, before anything else
            insert_pos = 0
            in_docstring = False
            for i, line in enumerate(lines):
                s = line.strip()
                if s.startswith('"""'):
                    if in_docstring:
                        insert_pos = i + 1
                        break
                    elif s.count('"""') >= 2:
                        insert_pos = i + 1
                        break
                    else:
                        in_docstring = True
                elif s.endswith('"""') and in_docstring:
                    insert_pos = i + 1
                    break

            # Insert the future import
            lines.insert(insert_pos, "")
            lines.insert(insert_pos + 1, "from __future__ import annotations")

            new_content = "\n".join(lines)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fp, ROOT)
            if fixed <= 15:
                print(f"  Fixed: {rel}")

if fixed > 15:
    print(f"  ... and {fixed - 15} more")
print(f"\nTotal: {fixed} files fixed")
