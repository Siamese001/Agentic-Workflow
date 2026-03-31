"""Fix production files missing standard library imports.

The batch wiring scripts generated/modified files that use type annotations
like `Any`, `dataclass`, etc. but lack the corresponding stdlib imports.
This script detects usage of common symbols and adds missing imports.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"

# Map: symbol_regex -> import_statement
# We match at word boundary to avoid false positives
SYMBOL_IMPORTS = {
    r'\bAny\b': 'from typing import Any',
    r'\bOptional\b': 'from typing import Optional',
    r'\bList\b(?!\s*=)': 'from typing import List',
    r'\bDict\b(?!\s*=)': 'from typing import Dict',
    r'\bTuple\b(?!\s*=)': 'from typing import Tuple',
    r'\bUnion\b': 'from typing import Union',
    r'\bCallable\b': 'from typing import Callable',
    r'\b@dataclass\b': 'from dataclasses import dataclass',
    r'\bdataclass\b': 'from dataclasses import dataclass',
    r'\bfield\(': 'from dataclasses import field',
    r'\bEnum\b': 'from enum import Enum',
    r'\bPath\b(?!\s*=)': 'from pathlib import Path',
    r'\bBaseModel\b': 'from pydantic import BaseModel',
    r'\bConfigDict\b': 'from pydantic import ConfigDict',
    r'\bField\b': 'from pydantic import Field',
}

# Group by module for cleaner imports
MODULE_SYMBOLS = {
    'typing': ['Any', 'Optional', 'List', 'Dict', 'Tuple', 'Union', 'Callable'],
    'dataclasses': ['dataclass', 'field'],
    'enum': ['Enum'],
    'pathlib': ['Path'],
    'pydantic': ['BaseModel', 'ConfigDict', 'Field'],
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

            lines = content.split("\n")

            # For each module, find which symbols are used but not imported
            needed = {}  # module -> set of symbols
            for module, symbols in MODULE_SYMBOLS.items():
                for sym in symbols:
                    # Check if symbol is used in the file (not just in strings/comments)
                    # Simple heuristic: appears as a word boundary
                    if sym == 'field':
                        pattern = r'\bfield\s*\('
                    elif sym == 'Path':
                        # Avoid matching PathConstants etc
                        pattern = r'\bPath\b(?![A-Za-z])'
                    elif sym == 'Field':
                        pattern = r'\bField\s*\('
                    else:
                        pattern = r'\b' + re.escape(sym) + r'\b'

                    if not re.search(pattern, content):
                        continue

                    # Check if already imported
                    already_imported = False
                    for line in lines:
                        s = line.strip()
                        if s.startswith("#"):
                            continue
                        # Direct import checks
                        if re.search(r'import\s+' + re.escape(sym) + r'\b', s):
                            already_imported = True
                            break
                        if re.search(r'import\s+\(', s):
                            # Will be caught in multiline check
                            continue
                        if f"import {sym}," in s or f"import {sym}" in s.rstrip(")"):
                            already_imported = True
                            break

                    # Also check multiline import blocks
                    in_block = False
                    for line in lines:
                        s = line.strip()
                        if re.match(r'^from\s+\S+\s+import\s+\(', s):
                            in_block = True
                            if re.search(r'\b' + re.escape(sym) + r'\b', s):
                                already_imported = True
                                break
                            continue
                        if in_block:
                            if s == ")":
                                in_block = False
                                continue
                            if re.search(r'\b' + re.escape(sym) + r'\b', s):
                                already_imported = True
                                break

                    # Check for local definitions
                    if not already_imported:
                        if f"class {sym}" in content or f"def {sym}" in content or f"{sym} =" in content:
                            if sym not in ('Any', 'Optional', 'List', 'Dict', 'Tuple',
                                           'Union', 'Callable', 'dataclass', 'Enum', 'BaseModel'):
                                already_imported = True

                    if not already_imported:
                        needed.setdefault(module, set()).add(sym)

            if not needed:
                continue

            # Find the right insertion point - after last import but before code
            last_import = -1
            in_imp = False
            for i, line in enumerate(lines):
                s = line.strip()
                if s.startswith("from ") or s.startswith("import "):
                    if "(" in s and ")" not in s:
                        in_imp = True
                    last_import = i
                elif in_imp:
                    last_import = i
                    if s == ")":
                        in_imp = False

            if last_import < 0:
                # Find end of docstring
                for i, line in enumerate(lines):
                    s = line.strip()
                    if i > 0 and (s == '"""' or (s.endswith('"""') and s.startswith('"""'))):
                        last_import = i
                        break
                if last_import < 0:
                    last_import = 0

            # Check if we can merge with existing import from same module
            insert_lines = []
            for module, syms in sorted(needed.items()):
                # Check if there's an existing 'from module import' line
                merged = False
                for i, line in enumerate(lines):
                    s = line.strip()
                    if re.match(r'^from\s+' + re.escape(module) + r'\s+import\s+', s) and '(' not in s:
                        # Single-line import - extend it
                        existing = s.rstrip()
                        for sym in sorted(syms):
                            existing += f", {sym}"
                        lines[i] = existing
                        merged = True
                        break
                    elif re.match(r'^from\s+' + re.escape(module) + r'\s+import\s+\(', s):
                        # Multi-line import - add before closing ')'
                        j = i + 1
                        while j < len(lines):
                            if lines[j].strip() == ")":
                                for k, sym in enumerate(sorted(syms)):
                                    lines.insert(j + k, f"    {sym},")
                                merged = True
                                break
                            j += 1
                        break

                if not merged:
                    syms_str = ", ".join(sorted(syms))
                    insert_lines.append(f"from {module} import {syms_str}")

            # Insert new import lines
            if insert_lines:
                insert_pos = last_import + 1
                for k, il in enumerate(insert_lines):
                    lines.insert(insert_pos + k, il)

            new_content = "\n".join(lines)
            if new_content != content:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(new_content)
                fixed += 1
                rel = os.path.relpath(fp, ROOT)
                syms_desc = "; ".join(f"{m}: {','.join(sorted(s))}" for m, s in sorted(needed.items()))
                if fixed <= 25:
                    print(f"  Fixed: {rel} ({syms_desc})")

if fixed > 25:
    print(f"  ... and {fixed - 25} more")
print(f"\nTotal: {fixed} files fixed")
