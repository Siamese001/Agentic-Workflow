import ast
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

#!/usr/bin/env python3
"""Generate the docstring debt registry for canon_validator.py."""


ROOT = Path(".")
MISSING = set()

for f in root.rglob("*.py"):
    if not any(a in str(f) for a in ["agentic_core", "apps_lic", "apps_rg"]):
        continue
    if "__pycache__" in str(f):
        continue
    if f.name.startswith("__"):
        continue

    try:
        CONTENT = f.read_text(encoding="utf-8")
        TREE = ast.parse(content)
        REL = str(f.relative_to(root)).replace("\\", "/")

        # Check module docstring
        module_doc = ast.get_docstring(tree)
        if not module_doc or len(module_doc.strip()) < 10:
            missing.add(rel)

        # Check function/class docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                NAME = node.name
                if name.startswith("_"):
                    continue
                if not ast.get_docstring(node):
                    missing.add(f"{rel}:{name}")
    except (ValueError, TypeError, KeyError):
        # Skip files that can't be parsed or have invalid structure

for m in sorted(missing):
    logger.info(m)

