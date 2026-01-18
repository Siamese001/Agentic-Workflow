"""
Extract quality agents from canon_agents_quality.py.
Extracts DocumentationAgent and _LegacyNamingAgent to sovereign files.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: memory, orchestrator, prompt, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

import ast
from pathlib import Path
from typing import List, Tuple
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/canon_agents_quality.py")
TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")

AGENTS_TO_EXTRACT = [
    "DocumentationAgent",
    "_LegacyNamingAgent"
]

def extract_class_with_context(content: str, class_name: str) -> Tuple[str, int, int]:
    """Extract class source with preceding comments."""
    lines = content.split('\n')
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith('#') or not prev_line:
                    start_line -= 1
                else:
                    break
            
            class_source = '\n'.join(lines[start_line:end_line])
            return class_source, start_line + 1, end_line
    
    raise ValueError(f"Class {class_name} not found")

def create_agent_file(class_name: str, class_source: str):
    """Create sovereign file for extracted agent."""
    target_file = TARGET_DIR / f"{class_name}.py"
    
    # Get imports from source
    imports = """from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.L3_orchestration.fission_logic.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class SubAtomicAgent:
    \"\"\"Stub base class for quality agents.\"\"\"
    def __init__(self, *args, **kwargs) -> None:
        self.agent = type('Agent', (), {'name': 'QualityAgent', 'ctx': type('Ctx', (), {'python_files': [], 'report': lambda *a: None})()})()
"""
    
    content = f'''"""
{class_name} - Extracted from canon_agents_quality.py
Part of the quality enforcement agent family.
"""
{imports}

{class_source}
'''
    
    print(f"Creating {target_file}")
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return target_file

def remove_classes_from_source(source_file: Path, classes_to_remove: List[str]):
    """Remove extracted classes from source file."""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find all class ranges to remove
    ranges_to_remove = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in classes_to_remove:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith('#') or not prev_line:
                    start_line -= 1
                else:
                    break
            
            ranges_to_remove.append((start_line, end_line, node.name))
    
    # Sort in reverse to remove from bottom up
    ranges_to_remove.sort(reverse=True)
    
    # Remove classes and add extraction notes
    for start, end, name in ranges_to_remove:
        del lines[start:end]
        lines.insert(start, f"# {name} extracted to {name}.py (Phase B Task 3)")
        lines.insert(start + 1, "")
    
    # Backup original
    backup_file = source_file.with_suffix('.py.bak')
    print(f"  Creating backup: {backup_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        with open(backup_file, 'w', encoding='utf-8') as b:
            b.write(f.read())
    
    # Write updated file
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    print("=" * 60)
    print("QUALITY AGENT EXTRACTION - PHASE B TASK 3")
    print("=" * 60)
    
    # Read source file
    print(f"\nReading {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract each agent
    extracted_files = []
    for agent_name in AGENTS_TO_EXTRACT:
        print(f"\n📦 Extracting {agent_name}...")
        try:
            class_source, start, end = extract_class_with_context(content, agent_name)
            target_file = create_agent_file(agent_name, class_source)
            extracted_files.append(target_file)
            print(f"  ✅ Created {target_file} (lines {start}-{end})")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    # Update source file
    print(f"\nUpdating {SOURCE_FILE}...")
    remove_classes_from_source(SOURCE_FILE, AGENTS_TO_EXTRACT)
    print(f"  ✅ Updated {SOURCE_FILE}")
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\nExtracted {len(extracted_files)} quality agents:")
    for f in extracted_files:
        print(f"  ✅ {f}")
    
    print(f"\n⚠️  Next steps:")
    print(f"  1. Rename sovereign_cognitive_plane_with_streamer.py")
    print(f"  2. Update imports for DocumentationAgent")
    print(f"  3. Run discovery to verify 280 agents")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
