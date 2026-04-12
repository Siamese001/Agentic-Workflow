"""Find ALL capitalized names used at runtime in sovereign_severity_types.py
and add aliases for any that map to lowercase class definitions."""

import ast
import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()

# Get all class names defined in the file
tree = ast.parse(src)
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


# Build CamelCase -> snake_case map
def to_snake(name):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    return s.lower()


# Find all Name references that are CamelCase and NOT defined as classes
all_names = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and node.id[0].isupper():
        all_names.add(node.id)
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id[0].isupper():
        all_names.add(node.value.id)

# Filter to only those that need aliases
existing_aliases = set(re.findall(r"^(\w+)\s*=\s*\w+", src, re.MULTILINE))
existing_classes = classes | existing_aliases

# Also include known stdlib/pydantic names to exclude
stdlib_names = {
    "Enum",
    "BaseModel",
    "Field",
    "Optional",
    "Any",
    "Path",
    "Dict",
    "List",
    "ClassVar",
    "ConfigDict",
    "Generic",
    "TypeVar",
    "Callable",
    "dataclass",
    "field",
    "True",
    "False",
    "None",
    "Exception",
    "ValueError",
    "TypeError",
    "KeyError",
    "RuntimeError",
    "AttributeError",
    "NotImplementedError",
    "LayerSegment",
    "AGENTIC_CORE_DIR",
    "validator",
    "field_validator",
    "Builder",
    "Config",
}

needs_alias = {}
for name in sorted(all_names):
    if name in existing_classes or name in stdlib_names:
        continue
    # Check if there's a snake_case class
    snake = to_snake(name)
    if snake in classes:
        needs_alias[name] = snake
    else:
        # Try simple lowercase
        if name.lower() in classes:
            needs_alias[name] = name.lower()

print(f"Classes defined: {len(classes)}")
print(f"CamelCase names used: {len(all_names)}")
print(f"Already aliased/defined: {len(existing_classes)}")
print(f"Need aliases: {len(needs_alias)}")
for camel, snake in sorted(needs_alias.items()):
    print(f"  {camel} = {snake}")

# Now find where each alias needs to be placed (before first usage)
# For simplicity, add all aliases right after the InjectionPattern alias block
if needs_alias:
    alias_block = "\n".join(f"{camel} = {snake}" for camel, snake in sorted(needs_alias.items()))
    # Insert after the existing alias block (after "InjectionPattern = injection_pattern")
    marker = "InjectionPattern = injection_pattern"
    if marker in src:
        src = src.replace(marker, marker + "\n" + alias_block)
        open(fp, "w", encoding="utf-8").write(src)
        print(f"\nInserted {len(needs_alias)} aliases after '{marker}'")
    else:
        print("\nERROR: Could not find insertion point")
