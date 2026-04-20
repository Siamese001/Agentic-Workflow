"""Find ALL missing CamelCase aliases in sovereign_severity_types.py registry blocks and add them."""

import ast
import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()
tree = ast.parse(src)

# Get all class names
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

# Get all existing aliases (CamelCase = snake_case at module level)
alias_pat = re.compile(r"^([A-Z][A-Za-z]+)\s*=\s*(\w+)\s*$", re.MULTILINE)
existing_aliases = {m.group(1) for m in alias_pat.finditer(src)}

# Find all CamelCase names used in CORE_CONTRACTS_REGISTRY and .update() blocks
registry_refs = re.findall(r'"(\w+)":\s*(\w+)', src)
needed = {}
for key, val in registry_refs:
    if val[0].isupper() and val not in classes and val not in existing_aliases:
        # Try to find a matching snake_case class
        def to_snake(name):
            s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
            return s.lower()

        snake = to_snake(val)
        if snake in classes:
            needed[val] = snake
        elif val.lower() in classes:
            needed[val] = val.lower()
        else:
            print(f"WARNING: No snake_case match for {val} (tried {snake})")

print(f"Existing aliases: {len(existing_aliases)}")
print(f"Need to add: {len(needed)}")
for camel, snake in sorted(needed.items()):
    print(f"  {camel} = {snake}")

if not needed:
    print("Nothing to fix!")
else:
    # Find each .update() block that references the missing name and add alias before it
    lines = src.split("\n")
    insertions = {}  # line_number -> alias_line

    for camel, snake in needed.items():
        # Find the snake_case class definition end line
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == snake:
                end_line = node.end_lineno  # 1-indexed
                insertions[end_line] = insertions.get(end_line, [])
                insertions[end_line].append(f"{camel} = {snake}")
                break

    # Insert aliases (bottom-up to preserve line numbers)
    for line_no in sorted(insertions.keys(), reverse=True):
        aliases = insertions[line_no]
        # Insert after the class end line
        idx = line_no  # 0-indexed position after end of class
        for alias in aliases:
            lines.insert(idx, alias)

    new_src = "\n".join(lines)
    # Verify syntax
    try:
        ast.parse(new_src)
        open(fp, "w", encoding="utf-8").write(new_src)
        print(f"\nInserted {sum(len(v) for v in insertions.values())} aliases. Syntax OK.")
    except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
        print(f"\nSYNTAX ERROR: {e}")
        print("NOT SAVED")
