import ast
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

#!/usr/bin/env python3
"""Generate the docstring debt registry for canon_validator.py."""


ROOT = Path(".")
MISSING = set()

for f in ROOT.rglob("*.py"):
    if not any(a in str(f) for a in ["agentic_core", "apps_lic", "apps_rg"]):
        continue
    if "__pycache__" in str(f):
        continue
    if f.name.startswith("__"):
        continue

    try:
        CONTENT = f.read_text(encoding="utf-8")
        TREE = ast.parse(CONTENT)
        REL = str(f.relative_to(ROOT)).replace("\\", "/")

        # Check module docstring
        module_doc = ast.get_docstring(TREE)
        if not module_doc or len(module_doc.strip()) < 10:
            MISSING.add(REL)

        # Check function/class docstrings
        for node in ast.walk(TREE):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                NAME = node.name
                if NAME.startswith("_"):
                    continue
                if not ast.get_docstring(node):
                    MISSING.add(f"{REL}:{NAME}")
    except (ValueError, TypeError, KeyError):
        # Skip files that can't be parsed or have invalid structure
        pass

for m in sorted(MISSING):
    LOGGER.info(m)