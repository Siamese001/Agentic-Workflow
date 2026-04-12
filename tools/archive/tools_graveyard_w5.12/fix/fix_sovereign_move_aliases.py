"""Move all CamelCase aliases in sovereign_severity_types.py to the end of the file,
after all class definitions, to avoid forward reference errors."""

import re

fp = r"C:\Git\Agentic-Workflow\apps_shared\types\sovereign_severity_types.py"
src = open(fp, encoding="utf-8").read()

# Pattern: standalone alias lines like "AgentResponse = agent_response"
# These are simple assignments where both sides are identifiers
alias_pattern = re.compile(r"^([A-Z]\w+)\s*=\s*([a-z]\w+)\s*$", re.MULTILINE)

# Collect all alias lines and their positions
aliases = []
lines = src.split("\n")
alias_indices = set()
for i, line in enumerate(lines):
    m = alias_pattern.match(line)
    if m:
        # Verify this isn't inside a class or function (check indentation)
        if not line.startswith(" ") and not line.startswith("\t"):
            aliases.append(line)
            alias_indices.add(i)

print(f"Found {len(aliases)} alias lines to move")

# Remove alias lines from their current positions
new_lines = [line for i, line in enumerate(lines) if i not in alias_indices]

# Find the position just before 'CORE_CONTRACTS_REGISTRY' or at the end
# We want aliases AFTER all class definitions but BEFORE the registry dict
insert_text = "\n".join(aliases)

# Find the registry position in the cleaned content
new_src = "\n".join(new_lines)
registry_pos = new_src.find("core_contracts_types_registry = {")
if registry_pos >= 0:
    new_src = new_src[:registry_pos] + insert_text + "\n\n" + new_src[registry_pos:]
    print(f"Inserted {len(aliases)} aliases before core_contracts_types_registry")
else:
    # Fallback: append at end
    new_src += "\n\n" + insert_text + "\n"
    print(f"Appended {len(aliases)} aliases at end of file")

open(fp, "w", encoding="utf-8").write(new_src)
print("Done")
