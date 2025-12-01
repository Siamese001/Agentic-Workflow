#!/usr/bin/env python3
"""
CREATE IMPORTABLE PYTHON PACKAGE STRUCTURE - FIXED VERSION
Simple recursive approach that preserves full directory hierarchy
"""

import shutil
from pathlib import Path

def create_importable_structure():
    """Create importable Python package structure by recursively renaming hyphens to underscores"""
    
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow")
    agentic_core_path = base_path / "agentic_core"
    importable_path = base_path / "agentic_core_pkg"
    
    # Remove existing importable structure if it exists
    if importable_path.exists():
        shutil.rmtree(importable_path)
    
    print("🏗️  Creating importable Python package structure (recursive approach)...")
    
    # Create root __init__.py
    importable_path.mkdir(exist_ok=True)
    (importable_path / "__init__.py").write_text('"""Agentic Core L5 Package Importable Interface"""\n')
    
    # Recursively copy and rename directories
    def copy_and_rename_structure(src_path: Path, dst_path: Path):
        """Recursively copy structure, renaming hyphens to underscores in path components"""
        
        if src_path.is_file() and src_path.suffix == ".py":
            # Copy Python file
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"✅ Copied: {src_path.relative_to(agentic_core_path)} -> {dst_path.relative_to(importable_path)}")
            
        elif src_path.is_dir():
            # Create corresponding directory with renamed path
            renamed_dir_name = src_path.name.replace("-", "_")
            renamed_dst_path = dst_path / renamed_dir_name
            
            # Create __init__.py for this directory
            renamed_dst_path.mkdir(parents=True, exist_ok=True)
            (renamed_dst_path / "__init__.py").write_text(f'"""{renamed_dir_name.title()} Package"""\n')
            
            # Recursively process all children
            for child in src_path.iterdir():
                copy_and_rename_structure(child, renamed_dst_path)
    
    # Start recursive copy from agentic_core root
    copy_and_rename_structure(agentic_core_path, importable_path)
    
    # Create main import interface
    create_import_interface(importable_path)
    
    print(f"\n🎯 Importable structure created at: {importable_path}")
    print("📦 You can now import using:")
    print("   from agentic_core_pkg.plan_layer.plan_phase.get_core_info.general.understand_request.build_core_query import BuildCoreQuery")

def create_import_interface(importable_path: Path):
    """Create convenient import interface"""
    
    interface_content = '''"""
Agentic Core L5 Importable Package Interface

This package provides importable access to the L5 agentic architecture
while maintaining the original hyphenated directory structure for
YAML compliance.

Usage:
    from agentic_core_pkg.plan_layer.plan_phase.get_core_info.general.understand_request.build_core_query import BuildCoreQuery
    from agentic_core_pkg.exec_layer.act_phase.use_core_tools.general.use_a_tool import ExecuteCoreExecution
    from agentic_core_pkg.safe_layer.safety_phase.check_core_rules.policy.check_safety import ApplySafetyPolicy
"""

# Version and metadata
__version__ = "1.0.0"
__description__ = "L5 Agentic Architecture Importable Package"
__author__ = "Agentic Core Reconstruction Team"

# Convenience imports for common components
try:
    from .plan_layer.plan_phase.get_core_info.general.understand_request.build_core_query import BuildCoreQuery
    from .orc_layer.plan_phase.get_core_info.general.understand_request.orchestrate_core_planning import OrchestrateCorePlanning
    from .exec_layer.act_phase.use_core_tools.general.use_a_tool import ExecuteCoreExecution
    from .mem_layer.retrieve_phase.get_core_info.general.understand_request.retrieve_core_memory import RetrieveCoreMemory
    from .safe_layer.safety_phase.check_core_rules.policy.check_safety import ApplySafetyPolicy
    
    __all__ = [
        "BuildCoreQuery",
        "OrchestrateCorePlanning", 
        "ExecuteCoreExecution",
        "RetrieveCoreMemory",
        "ApplySafetyPolicy"
    ]
except ImportError as e:
    print(f"Warning: Could not import convenience components: {e}")
    __all__ = []
'''
    
    with open(importable_path / "__init__.py", 'w', encoding='utf-8') as f:
        f.write(interface_content)

if __name__ == "__main__":
    create_importable_structure()
