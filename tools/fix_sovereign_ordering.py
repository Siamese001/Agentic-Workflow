"""Fix sovereign_severity_types.py: ensure aliases come before registry, both after all classes."""
import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()
lines = src.split('\n')

# Step 1: Find and extract the registry block + CORE_CONTRACTS_REGISTRY alias
registry_start = None
registry_end = None
in_registry = False
brace_depth = 0
for i, line in enumerate(lines):
    if 'core_contracts_types_registry' in line and '=' in line and '{' in line:
        registry_start = i
        in_registry = True
        brace_depth = line.count('{') - line.count('}')
        if brace_depth == 0:
            registry_end = i
            break
    elif in_registry:
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0:
            registry_end = i
            break

# Find CORE_CONTRACTS_REGISTRY line and any .update() blocks
update_start = None
update_end = None
core_line = None
for i in range(registry_end + 1 if registry_end else 0, len(lines)):
    if 'CORE_CONTRACTS_REGISTRY = core_contracts_types_registry' in lines[i]:
        core_line = i
    elif 'CORE_CONTRACTS_REGISTRY.update(' in lines[i]:
        update_start = i
        # Find end of update block
        depth = lines[i].count('(') - lines[i].count(')')
        for j in range(i + 1, len(lines)):
            depth += lines[j].count('(') - lines[j].count(')')
            if depth <= 0:
                update_end = j
                break

print(f"Registry: lines {registry_start}-{registry_end}")
print(f"CORE_CONTRACTS_REGISTRY: line {core_line}")
print(f"Update block: lines {update_start}-{update_end}")

# Step 2: Extract these blocks
registry_block = lines[registry_start:registry_end+1] if registry_start is not None else []
core_alias_line = [lines[core_line]] if core_line is not None else []
update_block = lines[update_start:update_end+1] if update_start is not None else []

# All lines to remove
remove_indices = set()
if registry_start is not None:
    for i in range(registry_start, registry_end + 1):
        remove_indices.add(i)
if core_line is not None:
    remove_indices.add(core_line)
if update_start is not None:
    for i in range(update_start, update_end + 1):
        remove_indices.add(i)

# Step 3: Remove these blocks
clean_lines = [line for i, line in enumerate(lines) if i not in remove_indices]

# Step 4: Now find the alias block (already at end after classes)
# The aliases start with "# ── CamelCase aliases"
alias_marker = None
for i, line in enumerate(clean_lines):
    if '── CamelCase aliases' in line:
        alias_marker = i
        break

if alias_marker is not None:
    # Find end of alias block (next blank line after aliases or end of file)
    alias_end = len(clean_lines) - 1
    for i in range(alias_marker + 1, len(clean_lines)):
        stripped = clean_lines[i].strip()
        if stripped and not re.match(r'^[A-Z]\w+\s*=\s*[a-z]\w+$', stripped):
            alias_end = i - 1
            break

    # Insert registry blocks AFTER the alias block
    insert_pos = alias_end + 1
    insert_lines = ['', ''] + registry_block + [''] + core_alias_line
    if update_block:
        insert_lines += [''] + update_block

    for j, line in enumerate(insert_lines):
        clean_lines.insert(insert_pos + j, line)

    print(f"Moved registry blocks after aliases at line {insert_pos}")
else:
    print("ERROR: Could not find alias block marker")

final_src = '\n'.join(clean_lines)
open(fp, "w", encoding="utf-8").write(final_src)
print("Done")
