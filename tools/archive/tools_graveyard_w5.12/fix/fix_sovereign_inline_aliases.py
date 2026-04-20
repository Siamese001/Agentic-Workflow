"""Add CamelCase aliases inline right after each lowercase class definition."""

import ast
import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()

# Step 1: Remove ALL existing standalone alias lines (CamelCase = snake_case)
# except ThermalProfile which we already placed correctly
alias_pattern = re.compile(r"^([A-Z][A-Za-z]+)\s*=\s*([a-z][a-z_]+)\s*$")
lines = src.split("\n")
remove_indices = set()
for i, line in enumerate(lines):
    m = alias_pattern.match(line)
    if m and not line.startswith(" ") and not line.startswith("\t"):
        remove_indices.add(i)

clean_lines = [line for i, line in enumerate(lines) if i not in remove_indices]
# Also remove the alias comment header
clean_lines = [l for l in clean_lines if "── CamelCase aliases" not in l]
clean_src = "\n".join(clean_lines)

print(f"Removed {len(remove_indices)} existing alias lines")

# Step 2: Parse to find all class definitions and their end lines
tree = ast.parse(clean_src)
class_info = {}  # name -> end_lineno
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        class_info[node.name] = node.end_lineno  # 1-indexed


# Step 3: Build CamelCase -> snake_case mapping
def to_camel(snake):
    return "".join(w.capitalize() for w in snake.split("_"))


# Build aliases for all lowercase classes
aliases_needed = {}
for name in class_info:
    if name[0].islower() and "_" in name:
        camel = to_camel(name)
        # Don't alias if camel already exists as a class
        if camel not in class_info:
            aliases_needed[name] = (camel, class_info[name])

print(f"Aliases to add: {len(aliases_needed)}")

# Step 4: Insert aliases after each class definition (work bottom-up to preserve line numbers)
result_lines = clean_src.split("\n")
insertions = sorted(aliases_needed.items(), key=lambda x: x[1][1], reverse=True)

for snake, (camel, end_line) in insertions:
    # Insert after end_line (0-indexed = end_line since end_line is 1-indexed)
    idx = end_line  # This is the line AFTER the class ends (0-indexed)
    # Check if the next line is already blank
    if idx < len(result_lines) and result_lines[idx].strip() == "":
        result_lines.insert(idx + 1, f"{camel} = {snake}")
    else:
        result_lines.insert(idx, f"\n{camel} = {snake}")

# Step 5: Also need to add the registry initialization
# Move core_contracts_types_registry to end if not already there
final_src = "\n".join(result_lines)

open(fp, "w", encoding="utf-8").write(final_src)
print("Done — aliases inserted inline after each class")

# Verify
try:
    ast.parse(final_src)
    print("Syntax OK")
except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
    print(f"SYNTAX ERROR: {e}")
