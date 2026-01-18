"""
Manual extraction script for SubAtomicAgent.py agents.
Extracts TypeMechanicAgent, BudgetAgent, and StructuralEngineerAgent to individual files.
"""
import ast
import re
from pathlib import Path
from typing import List, Tuple

# Target file
SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/SubAtomicAgent.py")
TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")

# Agents to extract
AGENTS_TO_EXTRACT = [
    "TypeMechanicAgent",
    "BudgetAgent", 
    "StructuralEngineerAgent"
]

def extract_class_source(content: str, class_name: str) -> Tuple[str, int, int]:
    """Extract the source code for a specific class."""
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            # Get line numbers
            start_line = node.lineno
            end_line = node.end_lineno
            
            # Extract the source
            lines = content.split('\n')
            
            # Include any comments immediately before the class
            actual_start = start_line - 1
            while actual_start > 0 and (lines[actual_start - 1].strip().startswith('#') or not lines[actual_start - 1].strip()):
                actual_start -= 1
                if lines[actual_start].strip().startswith('#'):
                    break
            
            class_source = '\n'.join(lines[actual_start:end_line])
            return class_source, actual_start + 1, end_line
    
    raise ValueError(f"Class {class_name} not found")

def create_agent_file(class_name: str, class_source: str):
    """Create a new file for the extracted agent."""
    target_file = TARGET_DIR / f"{class_name}.py"
    
    # Build the new file content
    content = f'''"""
{class_name} - Extracted from SubAtomicAgent.py
Part of the SubAtomic agent family for code quality enforcement.
"""
from typing import Any
from agentic_core.L3_orchestration.fission_logic.SubAtomicAgent import SubAtomicAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

{class_source}
'''
    
    print(f"Creating {target_file}")
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return target_file

def update_source_file(content: str, agents_extracted: List[str]) -> str:
    """Remove extracted agents from source file."""
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find line ranges to remove
    ranges_to_remove = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in agents_extracted:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before the class
            while start_line > 0 and (lines[start_line - 1].strip().startswith('#') or not lines[start_line - 1].strip()):
                start_line -= 1
                if lines[start_line].strip().startswith('#'):
                    break
            
            ranges_to_remove.append((start_line, end_line))
    
    # Sort ranges in reverse order to remove from bottom up
    ranges_to_remove.sort(reverse=True)
    
    # Remove the ranges
    for start, end in ranges_to_remove:
        del lines[start:end]
    
    return '\n'.join(lines)

def main():
    print("=" * 60)
    print("SUBATOMIC AGENT EXTRACTION")
    print("=" * 60)
    
    # Read source file
    print(f"\nReading {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract each agent
    extracted_files = []
    for agent_name in AGENTS_TO_EXTRACT:
        print(f"\nExtracting {agent_name}...")
        try:
            class_source, start, end = extract_class_source(content, agent_name)
            target_file = create_agent_file(agent_name, class_source)
            extracted_files.append(target_file)
            print(f"  ✅ Created {target_file} (lines {start}-{end})")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    # Update source file
    print(f"\nUpdating {SOURCE_FILE}...")
    updated_content = update_source_file(content, AGENTS_TO_EXTRACT)
    
    # Backup original
    backup_file = SOURCE_FILE.with_suffix('.py.bak')
    print(f"  Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write updated file
    with open(SOURCE_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"  ✅ Updated {SOURCE_FILE}")
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\nExtracted {len(extracted_files)} agents:")
    for f in extracted_files:
        print(f"  ✅ {f}")
    
    print(f"\n⚠️  Next steps:")
    print(f"  1. Run discovery to verify 276 agents")
    print(f"  2. Update imports across the codebase")
    print(f"  3. Test that all agents still work correctly")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
