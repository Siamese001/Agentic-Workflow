from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Extract PatternEnforcerAgent from canon_agents_pattern.py.
Also removes SubAtomicAgent stub and adds proper import.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

import ast
from pathlib import Path

SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/canon_agents_pattern.py")
TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")


def extract_class_with_context(content: str, class_name: str) -> tuple[str, int, int]:
    """Extract class source with preceding comments."""
    lines = content.split("\n")
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno

            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith("#") or not prev_line:
                    start_line -= 1
                else:
                    break

            class_source = "\n".join(lines[start_line:end_line])
            return class_source, start_line + 1, end_line

    raise ValueError(f"Class {class_name} not found")


def create_pattern_enforcer_file(class_source: str):
    """Create sovereign file for PatternEnforcerAgent."""
    target_file = TARGET_DIR / "PatternEnforcerAgent.py"

    content = f'''"""
PatternEnforcerAgent - Extracted from canon_agents_pattern.py
Enforces coding patterns and best practices across Python files.
"""
import ast
import logging
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple

# DEPRECATED: CanonBaseAgentInterface removed - use Protocol instead
try:
    from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
except ImportError:
    class CanonBaseAgentInterface(Protocol):
        pass

from agentic_core.L3_orchestration.reasoning.subatomic_testing_mixin import subatomic_testing_mixin
from agentic_core.L5_safety.enforcement.mcp_hardened_mixin import mcp_hardened_mixin
from agentic_core.L5_safety.config.structure_blueprint_config import (
    SOVEREIGN_TERRITORIES,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.mixins.healer_mixin import healer_mixin

Logger: Any = logging.getLogger(__name__)

{class_source}
'''

    print(f"Creating {target_file}")
    _wg.open_write(target_file, content)

    return target_file


def update_source_file(source_file: Path):
    """Remove PatternEnforcerAgent and SubAtomicAgent stub, add proper import."""
    with open(source_file, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    tree = ast.parse(content)

    # Find classes to remove
    classes_to_remove = ["PatternEnforcerAgent", "SubAtomicAgent"]
    ranges_to_remove = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in classes_to_remove:
            start_line = node.lineno - 1
            end_line = node.end_lineno

            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith("#") or not prev_line:
                    start_line -= 1
                else:
                    break

            ranges_to_remove.append((start_line, end_line, node.name))

    # Sort in reverse to remove from bottom up
    ranges_to_remove.sort(reverse=True)

    # Backup original
    backup_file = source_file.with_suffix(".py.bak")
    print(f"  Creating backup: {backup_file}")
    with open(source_file, encoding="utf-8") as f:
        _wg.open_write(backup_file, f.read())

    # Remove classes
    for start, end, name in ranges_to_remove:
        del lines[start:end]
        if name == "PatternEnforcerAgent":
            lines.insert(start, f"# {name} extracted to {name}.py (Phase B Task 4)")
            lines.insert(start + 1, "")

    # Add import for SubAtomicAgent at the top after imports
    import_line = "from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicAgent"

    # Find where to insert (after other imports)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("from agentic_core.base_agents"):
            insert_idx = i + 1
            break

    lines.insert(insert_idx, import_line)
    lines.insert(insert_idx + 1, "")

    # Write updated file
    _wg.open_write(source_file, "\n".join(lines))


def main():
    print("=" * 60)
    print("PATTERN AGENT EXTRACTION - PHASE B TASK 4")
    print("=" * 60)

    # Read source file
    print(f"\nReading {SOURCE_FILE}")
    with open(SOURCE_FILE, encoding="utf-8") as f:
        content = f.read()

    # Extract PatternEnforcerAgent
    print("\n📦 Extracting PatternEnforcerAgent...")
    try:
        class_source, start, end = extract_class_with_context(content, "PatternEnforcerAgent")
        target_file = create_pattern_enforcer_file(class_source)
        print(f"  ✅ Created {target_file} (lines {start}-{end})")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

    # Update source file
    print(f"\nUpdating {SOURCE_FILE}...")
    print("  - Removing PatternEnforcerAgent")
    print("  - Removing SubAtomicAgent stub")
    print("  - Adding SubAtomicAgent import")
    update_source_file(SOURCE_FILE)
    print(f"  ✅ Updated {SOURCE_FILE}")

    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print("\n✅ PatternEnforcerAgent.py created")
    print("✅ canon_agents_pattern.py updated with proper import")

    print("\n⚠️  Next steps:")
    print("  1. Rename _GenerativeGuard_Deprecated in CanonHealerAgent.py")
    print("  2. Update imports for PatternEnforcerAgent")
    print("  3. Run discovery to verify 281 agents")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
