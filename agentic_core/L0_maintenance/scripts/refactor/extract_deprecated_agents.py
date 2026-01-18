"""
Extract deprecated agents to their own sovereign files.
Extracts OutreachTestPilotDeprecatedAgent and StateValidatorDeprecatedAgent.
"""
import ast
import re
from pathlib import Path
from typing import List, Tuple

# Agents to extract
EXTRACTIONS = [
    {
        "source_file": Path("apps_lic/engines/outreach_engine/autonomous/LeadQualityAgent.py"),
        "class_name": "OutreachTestPilotDeprecatedAgent",
        "target_dir": Path("apps_lic/engines/outreach_engine/autonomous"),
    },
    {
        "source_file": Path("apps_shared/utils/StateManagerAgent.py"),
        "class_name": "StateValidatorDeprecatedAgent",
        "target_dir": Path("apps_shared/utils"),
    }
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

def get_imports_from_source(source_file: Path) -> List[str]:
    """Extract import statements from source file."""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            names = ', '.join([alias.name for alias in node.names])
            imports.append(f"from {module} import {names}")
    
    return imports[:10]  # Get first 10 imports as context

def create_agent_file(extraction: dict, class_source: str, imports: List[str]):
    """Create a new file for the extracted agent."""
    class_name = extraction["class_name"]
    target_file = extraction["target_dir"] / f"{class_name}.py"
    
    # Build the new file content
    content = f'''"""
{class_name} - Extracted for 1:1 sovereign file structure.
Deprecated agent preserved for backward compatibility.
"""
{chr(10).join(imports[:5])}

{class_source}
'''
    
    print(f"Creating {target_file}")
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return target_file

def update_source_file(source_file: Path, class_name: str) -> None:
    """Remove extracted agent from source file."""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find line range to remove
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before the class
            while start_line > 0 and (lines[start_line - 1].strip().startswith('#') or not lines[start_line - 1].strip()):
                start_line -= 1
                if lines[start_line].strip().startswith('#'):
                    break
            
            # Remove the class
            del lines[start_line:end_line]
            
            # Add a comment indicating the extraction
            lines.insert(start_line, f"# {class_name} extracted to {class_name}.py (Phase B Task 2)")
            lines.insert(start_line + 1, "")
            break
    
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
    print("DEPRECATED AGENT EXTRACTION - PHASE B TASK 2")
    print("=" * 60)
    
    extracted_files = []
    
    for extraction in EXTRACTIONS:
        source_file = extraction["source_file"]
        class_name = extraction["class_name"]
        
        print(f"\n📦 Extracting {class_name} from {source_file.name}...")
        
        try:
            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract class source
            class_source, start, end = extract_class_source(content, class_name)
            print(f"  Found {class_name} at lines {start}-{end}")
            
            # Get imports from source
            imports = get_imports_from_source(source_file)
            
            # Create new file
            target_file = create_agent_file(extraction, class_source, imports)
            extracted_files.append(target_file)
            print(f"  ✅ Created {target_file}")
            
            # Update source file
            update_source_file(source_file, class_name)
            print(f"  ✅ Updated {source_file}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\nExtracted {len(extracted_files)} deprecated agents:")
    for f in extracted_files:
        print(f"  ✅ {f}")
    
    print(f"\n⚠️  Next steps:")
    print(f"  1. Run discovery to verify 278 agents")
    print(f"  2. Check for any import references to update")
    print(f"  3. Verify zero filename mismatch violations")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
