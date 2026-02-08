#!/usr/bin/env python3
"""
Add SubatomicTestingMixin to all agents that don't have test coverage.
This ensures 100% test coverage by adding the testing mixin to each agent.
"""

import json
import re
from pathlib import Path

# Load agent discovery data
with open("agent_discovery_full.json") as f:
    agents = json.load(f)

print(f"Total agents: {len(agents)}")

# Find agents without tests
agents_without_tests = [a for a in agents if not a.get("has_tests", False)]
print(f"Agents WITHOUT tests: {len(agents_without_tests)}")

# Process each agent
modified_count = 0
skipped_count = 0
error_count = 0

for agent in agents_without_tests:
    class_name = agent["class_name"]
    agent_path = Path(agent["path"])

    if not agent_path.exists():
        print(f"⚠️ File not found: {agent_path}")
        error_count += 1
        continue

    try:
        content = agent_path.read_text(encoding="utf-8")

        # Check if already has SubatomicTestingMixin
        if "SubatomicTestingMixin" in content:
            skipped_count += 1
            continue

        # Check if already has _run_self_tests
        if "_run_self_tests" in content:
            skipped_count += 1
            continue

        modified = False

        # Find the class definition and add SubatomicTestingMixin
        # Pattern: class ClassName(Base1, Base2):
        class_pattern = rf"class\s+{class_name}\s*\(([^)]+)\)\s*:"
        match = re.search(class_pattern, content)

        if match:
            bases = match.group(1)
            # Add SubatomicTestingMixin as first base (for proper MRO)
            new_bases = f"SubatomicTestingMixin, {bases}"
            new_class_def = f"class {class_name}({new_bases}):"
            content = content[: match.start()] + new_class_def + content[match.end() :]
            modified = True
        else:
            # Try pattern without parentheses: class ClassName:
            class_pattern_no_base = rf"class\s+{class_name}\s*:"
            match = re.search(class_pattern_no_base, content)
            if match:
                new_class_def = f"class {class_name}(SubatomicTestingMixin):"
                content = content[: match.start()] + new_class_def + content[match.end() :]
                modified = True

        if modified:
            # Add import if not present
            if "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin" not in content:
                # Find best place to add import
                if "from agentic_core" in content:
                    # Add after last agentic_core import
                    last_import = content.rfind("from agentic_core")
                    end_of_line = content.find("\n", last_import)
                    import_line = (
                        "\nfrom agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin"
                    )
                    content = content[:end_of_line] + import_line + content[end_of_line:]
                elif "import " in content:
                    # Add after last import
                    lines = content.split("\n")
                    last_import_idx = 0
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            last_import_idx = i
                    lines.insert(
                        last_import_idx + 1,
                        "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin",
                    )
                    content = "\n".join(lines)
                else:
                    # Add at top after docstring
                    if content.startswith('"""'):
                        end_docstring = content.find('"""', 3) + 3
                        content = (
                            content[:end_docstring]
                            + "\nfrom agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin\n"
                            + content[end_docstring:]
                        )
                    else:
                        content = (
                            "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin\n"
                            + content
                        )

            agent_path.write_text(content, encoding="utf-8")
            modified_count += 1
            print(f"✅ Modified: {agent_path}")
        else:
            print(f"⚠️ Could not find class definition: {class_name} in {agent_path}")
            error_count += 1

    except Exception as e:
        print(f"❌ Error processing {agent_path}: {e}")
        error_count += 1

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
print(f"Modified: {modified_count}")
print(f"Skipped (already has testing): {skipped_count}")
print(f"Errors: {error_count}")
print("\nNext step: Run full_agent_discovery.py to update test coverage stats")
