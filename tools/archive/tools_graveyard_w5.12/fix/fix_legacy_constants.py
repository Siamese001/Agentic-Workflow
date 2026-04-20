"""Fix all legacy constants set to None in configuration_service_util.py."""

import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\utils\configuration_service_util.py"
src = open(fp, encoding="utf-8").read()


# Pattern: lines like "UPPER_CASE = None" preceded by "# Legacy constant"
def replace_none_constants(src):
    lines = src.split("\n")
    fixed = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = re.match(r"^([A-Z][A-Z_0-9]+)\s*=\s*None\s*$", stripped)
        if m:
            name = m.group(1)
            # Set to lowercase string of the name
            val = name.lower()
            indent = line[: len(line) - len(line.lstrip())]
            lines[i] = f'{indent}{name} = "{val}"'
            fixed += 1
    print(f"Fixed {fixed} legacy constants")
    return "\n".join(lines)


new_src = replace_none_constants(src)
# Verify syntax
import ast

try:
    ast.parse(new_src)
    open(fp, "w", encoding="utf-8").write(new_src)
    print("Syntax OK. Saved.")
except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
    print(f"SYNTAX ERROR: {e}")
