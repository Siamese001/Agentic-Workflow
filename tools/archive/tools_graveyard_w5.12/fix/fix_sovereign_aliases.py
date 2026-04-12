"""Find all missing capitalized aliases in sovereign_severity_types.py and add them."""

import ast
import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()

# Find all capitalized names in the registry dict
registry_match = re.search(r"core_contracts_types_registry\s*=\s*\{(.*?)\}", src, re.DOTALL)
if registry_match:
    names = re.findall(r'"(\w+)":\s*(\w+)', registry_match.group(1))
    for key, val in names:
        if val[0].isupper() and f"class {val}" not in src and f"{val} = " not in src:
            print(f"MISSING: {val}")

# Also find all class names defined in the file
tree = ast.parse(src)
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
print(f"\nDefined classes: {len(classes)}")


# Build a map from CamelCase -> snake_case
def to_snake(name):
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
    return s.lower()


missing = []
for key, val in names:
    if val[0].isupper() and f"class {val}" not in src and f"{val} = " not in src:
        snake = to_snake(val)
        if snake in classes:
            missing.append((val, snake))
            print(f"  {val} -> {snake}")
        else:
            print(f"  {val} -> ??? (no match for {snake})")
