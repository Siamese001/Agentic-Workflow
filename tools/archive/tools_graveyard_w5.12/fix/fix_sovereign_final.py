"""Move ALL CamelCase aliases to after the last class definition in sovereign_severity_types.py."""
import ast
import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()

# Step 1: Remove all existing alias lines (CamelCase = snake_case at module level)
alias_pattern = re.compile(r'^([A-Z][A-Za-z]+)\s*=\s*([a-z][a-z_]+)\s*$', re.MULTILINE)
lines = src.split('\n')
alias_indices = set()
aliases_to_restore = []
for i, line in enumerate(lines):
    m = alias_pattern.match(line)
    if m and not line.startswith(' ') and not line.startswith('\t'):
        aliases_to_restore.append(line)
        alias_indices.add(i)

# Remove alias lines
clean_lines = [line for i, line in enumerate(lines) if i not in alias_indices]
clean_src = '\n'.join(clean_lines)

# Step 2: Parse to find last class definition end line
tree = ast.parse(clean_src)
last_class_end = 0
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        end = node.end_lineno or 0
        if end > last_class_end:
            last_class_end = end

# Step 3: Also find which CamelCase names are actually needed
# Find all CamelCase names used in the file
all_classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

def to_snake(name):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    return s.lower()

# Find all CamelCase names referenced
all_camel_refs = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and node.id[0].isupper():
        all_camel_refs.add(node.id)
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id[0].isupper():
        all_camel_refs.add(node.value.id)

# Build needed aliases
stdlib_skip = {'Enum', 'BaseModel', 'Field', 'Optional', 'Any', 'Path', 'Dict', 'List',
               'ClassVar', 'ConfigDict', 'Generic', 'TypeVar', 'Callable', 'Builder', 'Config',
               'LayerSegment', 'AGENTIC_CORE_DIR', 'validator', 'field_validator',
               'True', 'False', 'None', 'Exception', 'ValueError', 'TypeError',
               'KeyError', 'RuntimeError', 'AttributeError', 'NotImplementedError',
               'Final', 'Union', 'Set', 'Tuple', 'Mapping', 'Sequence', 'Iterator'}

needed_aliases = {}
for name in sorted(all_camel_refs):
    if name in all_classes or name in stdlib_skip:
        continue
    snake = to_snake(name)
    if snake in all_classes:
        needed_aliases[name] = snake
    elif name.lower() in all_classes:
        needed_aliases[name] = name.lower()

print(f"Removed {len(alias_indices)} existing alias lines")
print(f"Last class ends at line {last_class_end}")
print(f"Need {len(needed_aliases)} aliases")

# Step 4: Insert aliases at last_class_end
clean_lines_list = clean_src.split('\n')
alias_block = '\n\n# ── CamelCase aliases for lowercase class names ──\n'
for camel, snake in sorted(needed_aliases.items()):
    alias_block += f'{camel} = {snake}\n'

clean_lines_list.insert(last_class_end, alias_block)
final_src = '\n'.join(clean_lines_list)

open(fp, "w", encoding="utf-8").write(final_src)
print("Done — aliases inserted after all class definitions")
