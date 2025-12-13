"""Automated cognitive density fixer - splits files with >5 top-level definitions."""

import ast
from pathlib import Path
from typing import List, Tuple

def count_top_level_defs(filepath: Path) -> int:
    """Count top-level definitions in a Python file."""
    try:
        tree = ast.parse(filepath.read_text(encoding='utf-8'))
        return sum(1 for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)))
    except:
        return 0

def split_file_by_type(filepath: Path) -> None:
    """Split a file into submodules by grouping enums, dataclasses, classes, and functions."""
    content = filepath.read_text(encoding='utf-8')
    tree = ast.parse(content)
    
    # Group definitions by type
    enums = []
    dataclasses = []
    classes = []
    functions = []
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Check if it's an Enum
            if any(base.id == 'Enum' for base in node.bases if isinstance(base, ast.Name)):
                enums.append(node)
            # Check if it has @dataclass decorator
            elif any(d.id == 'dataclass' or (isinstance(d, ast.Call) and d.func.id == 'dataclass') 
                    for d in node.decorator_list if isinstance(d, (ast.Name, ast.Call)) and hasattr(d if isinstance(d, ast.Name) else d.func, 'id')):
                dataclasses.append(node)
            else:
                classes.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node)
    
    total_defs = len(enums) + len(dataclasses) + len(classes) + len(functions)
    
    if total_defs <= 5:
        return  # No need to split
    
    print(f"Splitting {filepath.name}: {total_defs} defs ({len(enums)} enums, {len(dataclasses)} dataclasses, {len(classes)} classes, {len(functions)} functions)")
    
    # Create submodules
    parent_dir = filepath.parent
    stem = filepath.stem
    
    # Create types module (enums + dataclasses)
    if enums or dataclasses:
        types_content = f'"""Types and models for {stem}."""\n\n'
        types_content += "from dataclasses import dataclass, field\n"
        types_content += "from typing import Any, Dict, List, Optional\n"
        types_content += "from enum import Enum\n\n"
        
        for node in enums + dataclasses:
            types_content += ast.unparse(node) + "\n\n"
        
        types_file = parent_dir / f"{stem}_types.py"
        types_file.write_text(types_content, encoding='utf-8')
        print(f"  Created {types_file.name}")
    
    # Create implementation module (classes + functions)
    if classes or functions:
        impl_content = f'"""Implementation for {stem}."""\n\n'
        impl_content += "from typing import Any, Dict, List, Optional\n"
        if enums or dataclasses:
            impl_content += f"from .{stem}_types import *\n"
        impl_content += "\n"
        
        for node in classes + functions:
            impl_content += ast.unparse(node) + "\n\n"
        
        impl_file = parent_dir / f"{stem}_impl.py"
        impl_file.write_text(impl_content, encoding='utf-8')
        print(f"  Created {impl_file.name}")
    
    # Update original file to re-export
    shim_content = f'"""Backward compatibility shim for {stem}."""\n\n'
    if enums or dataclasses:
        shim_content += f"from .{stem}_types import *\n"
    if classes or functions:
        shim_content += f"from .{stem}_impl import *\n"
    
    filepath.write_text(shim_content, encoding='utf-8')
    print(f"  Updated {filepath.name} as compatibility shim")

# Files to fix
files_to_fix = [
    "apps_rg/L3_orchestration/orchestrate_workflow.py",
    "apps_rg/L1_cognition/k25_research_models.py",
    "apps_rg/L3_orchestration/resume_orchestration_config.py",
    "apps_rg/L2_execution/rg_provenance_tracker.py",
    "apps_rg/L3_orchestration/kx_nodes_resume.py",
    "apps_rg/L2_execution/achv_bullet_synthesizer.py",
    "apps_rg/L3_orchestration/titanium_integration.py",
    "apps_rg/L2_execution/peer_intelligence_auditor.py",
    "apps_rg/L3_orchestration/state/resume_state.py",
    "apps_rg/L3_orchestration/subatomic_orchestrator.py",
]

root = Path("c:/Git/Agentic-Workflow")

for file_path in files_to_fix:
    full_path = root / file_path
    if full_path.exists():
        defs = count_top_level_defs(full_path)
        if defs > 5:
            split_file_by_type(full_path)

print("\nDone! Re-run canon_validator.py to verify.")
