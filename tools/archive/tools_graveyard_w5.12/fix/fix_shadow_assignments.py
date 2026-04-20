"""Fix shadowed constant assignments like ARCHIVES_DIR = PROJECT_ROOT / ARCHIVES_DIR.

The pattern X = PROJECT_ROOT / X shadows the imported X with a local assignment,
causing NameError because Python sees the LHS assignment and treats RHS as
referencing a not-yet-defined local.

Fix: rename LHS to _X_PATH to avoid shadowing.
"""

import ast
import os
import re

ROOT = r"C:\Git\Agentic-Workflow"

# Pattern: CONST = something / CONST  (self-shadowing assignment)
SHADOW_PATTERN = re.compile(
    r"^(\s*)(\w+)\s*=\s*(\w+)\s*/\s*\2\s*$",
    re.MULTILINE,
)


def fix_file(filepath):
    """Fix self-shadowing constant assignments in a file."""
    src = open(filepath, encoding="utf-8").read()

    matches = list(SHADOW_PATTERN.finditer(src))
    if not matches:
        return 0

    fixed = 0
    for m in reversed(matches):  # reverse to maintain positions
        indent = m.group(1)
        const_name = m.group(2)
        rhs_prefix = m.group(3)

        new_name = f"_{const_name}_PATH"
        old_line = m.group(0)
        new_line = f"{indent}{new_name} = {rhs_prefix} / {const_name}"

        # Replace the assignment
        src = src[: m.start()] + new_line + src[m.end() :]

        # Replace all subsequent uses of the old name that referred to the path
        # (but NOT the import at the top)
        # This is tricky - we need to replace uses after this line
        # Actually, let's check if the shadowed name is used later
        rest = src[m.start() + len(new_line) :]
        if const_name in rest:
            # Replace uses of const_name that are path-like (after this point)
            src = src[: m.start() + len(new_line)] + rest.replace(const_name, new_name)

        fixed += 1

    # Verify syntax
    try:
        ast.parse(src)
    except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
        print(f"  SYNTAX ERROR in {filepath}: {e}")
        return 0

    open(filepath, "w", encoding="utf-8").write(src)
    return fixed


# Find all source files with self-shadowing assignments

# Get list of source files with NameErrors
SOURCE_FILES = [
    "agentic_core/L0_routing/scripts/class_info.py",
]

# Actually let's find all files with this pattern
count = 0
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "agentic_core")):
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            src = open(fp, encoding="utf-8").read()
        except (ValueError, TypeError, RuntimeError) as e:
            continue
        if SHADOW_PATTERN.search(src):
            rel = os.path.relpath(fp, ROOT)
            n = fix_file(fp)
            if n:
                print(f"  FIXED {n} shadow(s) in {rel}")
                count += n

print(f"\nTotal fixed: {count}")
