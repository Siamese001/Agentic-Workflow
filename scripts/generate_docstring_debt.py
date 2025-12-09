#!/usr/bin/env python3
"""Generate the docstring debt registry for canon_validator.py."""

import ast
from pathlib import Path

root = Path(".")
missing = set()

for f in root.rglob("*.py"):
    if not any(a in str(f) for a in ["agentic_core", "apps_lic", "apps_rg"]):
        continue
    if "__pycache__" in str(f):
        continue
    if f.name.startswith("__"):
        continue

    try:
        content = f.read_text(encoding="utf-8")
        tree = ast.parse(content)
        rel = str(f.relative_to(root)).replace("\\", "/")

        # Check module docstring
        module_doc = ast.get_docstring(tree)
        if not module_doc or len(module_doc.strip()) < 10:
            missing.add(rel)

        # Check function/class docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
                if name.startswith("_"):
                    continue
                if not ast.get_docstring(node):
                    missing.add(f"{rel}:{name}")
    except (ValueError, TypeError, KeyError):
        pass

print('"""')
print("DOCSTRING DEBT REGISTRY")
print("Generated: 2025-12-08")
print("These symbols lack proper docstrings and are acknowledged as technical debt.")
print("No NEW missing docstrings will be allowed. This list can only shrink.")
print('"""')
print("")
print("DOCSTRING_DEBT = {")
for m in sorted(missing):
    print(f'    "{m}",')
print("}")
