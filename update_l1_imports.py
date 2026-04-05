"""Update import paths for L1_cognition refactoring."""

import re
from pathlib import Path

root = Path(r"C:\Git\Agentic-Workflow")

replacements = [
    # validators -> enforcement
    (r"from agentic_core\.L1_cognition\.validators", "from agentic_core.L1_cognition.enforcement"),
    (r"import agentic_core\.L1_cognition\.validators", "import agentic_core.L1_cognition.enforcement"),
    # engines -> reasoning
    (r"from agentic_core\.L1_cognition\.engines", "from agentic_core.L1_cognition.reasoning"),
    (r"import agentic_core\.L1_cognition\.engines", "import agentic_core.L1_cognition.reasoning"),
    # context -> reasoning
    (r"from agentic_core\.L1_cognition\.context", "from agentic_core.L1_cognition.reasoning"),
    (r"import agentic_core\.L1_cognition\.context", "import agentic_core.L1_cognition.reasoning"),
    # evaluation -> reasoning
    (r"from agentic_core\.L1_cognition\.evaluation", "from agentic_core.L1_cognition.reasoning"),
    (r"import agentic_core\.L1_cognition\.evaluation", "import agentic_core.L1_cognition.reasoning"),
    # knowledge -> reasoning
    (r"from agentic_core\.L1_cognition\.knowledge", "from agentic_core.L1_cognition.reasoning"),
    (r"import agentic_core\.L1_cognition\.knowledge", "import agentic_core.L1_cognition.reasoning"),
    # memory -> reasoning
    (r"from agentic_core\.L1_cognition\.memory", "from agentic_core.L1_cognition.reasoning"),
    (r"import agentic_core\.L1_cognition\.memory", "import agentic_core.L1_cognition.reasoning"),
    # planning -> reasoning
    (r"from agentic_core\.L1_cognition\.planning", "from agentic_core.L1_cognition.reasoning"),
    (r"import agentic_core\.L1_cognition\.planning", "import agentic_core.L1_cognition.reasoning"),
    # providers -> utils
    (r"from agentic_core\.L1_cognition\.providers", "from agentic_core.L1_cognition.utils"),
    (r"import agentic_core\.L1_cognition\.providers", "import agentic_core.L1_cognition.utils"),
    # telemetry -> L6_observability/utils
    (r"from agentic_core\.L1_cognition\.telemetry", "from agentic_core.L6_observability.utils"),
    (r"import agentic_core\.L1_cognition\.telemetry", "import agentic_core.L6_observability.utils"),
]

def update_file(file_path: Path) -> int:
    """Update a single file, return number of changes."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return 0
    
    changes = 0
    for pattern, replacement in replacements:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            changes += count
    
    if changes > 0:
        file_path.write_text(content, encoding="utf-8")
        print(f"Updated {file_path}: {changes} changes")
    
    return changes

total_changes = 0
for py_file in root.rglob("*.py"):
    # Skip __pycache__
    if "__pycache__" in py_file.parts:
        continue
    total_changes += update_file(py_file)

print(f"\nTotal changes: {total_changes}")
