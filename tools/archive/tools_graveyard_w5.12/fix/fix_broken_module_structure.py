"""Fix files where batch wiring broke the module structure.

The batch wiring scripts inserted lifecycle_trace_contract imports at the
top of files, BEFORE the module docstring and standard library imports.
This causes the docstring to become a bare string literal, and the real
imports to appear after symbol usage.

Detection: Look for files where 'from agentic_core.runtime.lifecycle_trace_contract'
appears BEFORE the first 'import' of standard library modules (like 'from typing',
'from dataclasses', etc.), AND the file has a NameError-inducing pattern where
standard library names are used after the lifecycle block.

Fix: Move the lifecycle import block to AFTER all other imports.
"""

import os

ROOT = r"C:\Git\Agentic-Workflow"
LTC = "agentic_core.runtime.lifecycle_trace_contract"

fixed = 0

for base_dir in ["agentic_core", "apps_shared", "apps_lic", "apps_rg", "system_learning"]:
    scan_dir = os.path.join(ROOT, base_dir)
    if not os.path.isdir(scan_dir):
        continue
    for dirpath, _, filenames in os.walk(scan_dir):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
            except (ValueError, TypeError, RuntimeError) as e:
                continue

            if LTC not in content:
                continue

            lines = content.split("\n")

            # Find the FIRST lifecycle_trace_contract import block
            ltc_block_start = -1
            ltc_block_end = -1
            for i, line in enumerate(lines):
                if LTC in line and "import" in line:
                    ltc_block_start = i
                    if "(" in line:
                        # Multi-line import - find closing ')'
                        j = i + 1
                        while j < len(lines):
                            if lines[j].strip() == ")":
                                ltc_block_end = j
                                break
                            j += 1
                    else:
                        ltc_block_end = i
                    break  # Only fix the FIRST block

            if ltc_block_start < 0:
                continue

            # Check if there's a standard library import AFTER the LTC block
            # that should have been BEFORE it
            has_stdlib_after = False
            first_stdlib_after = -1
            for i in range(ltc_block_end + 1, min(ltc_block_end + 50, len(lines))):
                s = lines[i].strip()
                if s.startswith("from __future__") or s.startswith("import ") or s.startswith("from "):
                    # Check if it's a stdlib/third-party import
                    if any(
                        s.startswith(p)
                        for p in [
                            "from __future__",
                            "import os",
                            "import re",
                            "import sys",
                            "import logging",
                            "import json",
                            "import time",
                            "import uuid",
                            "from typing",
                            "from dataclasses",
                            "from pathlib",
                            "from enum",
                            "from collections",
                            "from abc",
                            "from functools",
                            "from datetime",
                            "import hashlib",
                            "import hmac",
                            "from contextlib",
                            "import ast",
                            "import math",
                            "import statistics",
                            "from pydantic",
                        ]
                    ):
                        has_stdlib_after = True
                        first_stdlib_after = i
                        break

            if not has_stdlib_after:
                continue

            # Check if there's a bare string literal (broken docstring) before LTC block
            # or if the LTC import is before the module's actual docstring
            has_bare_string = False
            for i in range(ltc_block_end + 1, min(ltc_block_end + 5, len(lines))):
                s = lines[i].strip()
                if s.startswith('"""') or s.startswith("'") or s.startswith('"'):
                    has_bare_string = True
                    break

            if not has_bare_string and first_stdlib_after <= ltc_block_end:
                continue

            # Extract the LTC block
            ltc_lines = lines[ltc_block_start : ltc_block_end + 1]

            # Also extract any _emit_* call lines immediately after the block
            emit_calls_end = ltc_block_end + 1
            while emit_calls_end < len(lines):
                s = lines[emit_calls_end].strip()
                if s.startswith("_emit_") or s.startswith("emit_") or s == "":
                    emit_calls_end += 1
                else:
                    break

            emit_call_lines = lines[ltc_block_end + 1 : emit_calls_end]

            # Remove the LTC block + emit calls from their current position
            new_lines = lines[:ltc_block_start] + lines[emit_calls_end:]

            # Find the last import line in the new content
            last_import = 0
            in_import = False
            for i, line in enumerate(new_lines):
                s = line.strip()
                if s.startswith("from ") or s.startswith("import "):
                    if "(" in s and ")" not in s:
                        in_import = True
                    last_import = i
                elif in_import:
                    last_import = i
                    if s == ")":
                        in_import = False

            # Insert LTC block after last import
            insert_pos = last_import + 1
            insert_block = [""] + ltc_lines + emit_call_lines

            for k, il in enumerate(insert_block):
                new_lines.insert(insert_pos + k, il)

            new_content = "\n".join(new_lines)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fpath, ROOT)
            if fixed <= 30:
                print(f"  Fixed: {rel}")

if fixed > 30:
    print(f"  ... and {fixed - 30} more")
print(f"\nTotal: {fixed} files fixed")
