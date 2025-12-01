#!/usr/bin/env python3
"""
CREATE IMPORTABLE PYTHON PACKAGE STRUCTURE
Maintains YAML compliance while enabling Python imports
"""

import shutil
from pathlib import Path

def create_importable_structure():
    """Create importable Python package structure that mirrors hyphenated directories"""
    
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow")
    agentic_core_path = base_path / "agentic_core"
    importable_path = base_path / "agentic_core_pkg"
    
    # Remove existing importable structure if it exists
    if importable_path.exists():
        shutil.rmtree(importable_path)
    
    print("🏗️  Creating importable Python package structure...")
    
    # Create root __init__.py
    importable_path.mkdir(exist_ok=True)
    (importable_path / "__init__.py").write_text('"""Agentic Core L5 Package Importable Interface"""\n')
    
    # Map hyphenated directories to underscored Python packages
    layer_mappings = {
        "plan-layer": "plan_layer",
        "orc-layer": "orc_layer", 
        "exec-layer": "exec_layer",
        "mem-layer": "mem_layer",
        "safe-layer": "safe_layer"
    }
    
    phase_mappings = {
        "plan-phase": "plan_phase",
        "act-phase": "act_phase",
        "safety-phase": "safety_phase",
        "validate-phase": "validate_phase",
        "retrieve-phase": "retrieve_phase",
        "expand-phase": "expand_phase",
        "refine-phase": "refine_phase",
        "inspect-phase": "inspect_phase",
        "agg-phase": "agg_phase"
    }
    
    function_mappings = {
        "get-core-info": "get_core_info",
        "use-core-tools": "use_core_tools",
        "check-core-rules": "check_core_rules",
        "convert-core-content": "convert_core_content",
        "pick-best-result": "pick_best_result",
        "check-core-structure": "check_core_structure",
        "find-core-problems": "find_core_problems",
        "update-core-state": "update_core_state",
        "manage-core-costs": "manage_core_costs"
    }
    
    type_mappings = {
        "understand-request": "understand_request",
        "prepare-information": "prepare_information",
        "check-safety": "check_safety",
        "use-a-tool": "use_a_tool",
        "retry-task": "retry_task",
        "update-memory": "update_memory",
        "compare-meaning": "compare_meaning",
        "embedding": "embedding",
        "semantic": "semantic",
        "adjust-scores": "adjust_scores",
        "policy": "policy",
        "general": "general",
        "utility": "utility",
        "routing": "routing"
    }
    
    # Create the importable structure
    for hyphenated_layer in agentic_core_path.iterdir():
        if not hyphenated_layer.is_dir() or not hyphenated_layer.name.endswith("-layer"):
            continue
            
        layer_name = layer_mappings.get(hyphenated_layer.name, hyphenated_layer.name.replace("-", "_"))
        layer_path = importable_path / layer_name
        layer_path.mkdir(exist_ok=True)
        (layer_path / "__init__.py").write_text(f'"""{layer_name.title()} Package"""\n')
        
        # Process phases
        for hyphenated_phase in hyphenated_layer.iterdir():
            if not hyphenated_phase.is_dir() or not hyphenated_phase.name.endswith("-phase"):
                continue
                
            phase_name = phase_mappings.get(hyphenated_phase.name, hyphenated_phase.name.replace("-", "_"))
            phase_path = layer_path / phase_name
            phase_path.mkdir(exist_ok=True)
            (phase_path / "__init__.py").write_text(f'"""{phase_name.title()} Package"""\n')
            
            # Process function groups
            for hyphenated_function in hyphenated_phase.iterdir():
                if not hyphenated_function.is_dir():
                    continue
                    
                function_name = function_mappings.get(hyphenated_function.name, hyphenated_function.name.replace("-", "_"))
                function_path = phase_path / function_name
                function_path.mkdir(exist_ok=True)
                (function_path / "__init__.py").write_text(f'"""{function_name.title()} Package"""\n')
                
                # Process types
                for hyphenated_type in hyphenated_function.iterdir():
                    if not hyphenated_type.is_dir():
                        continue
                        
                    type_name = type_mappings.get(hyphenated_type.name, hyphenated_type.name.replace("-", "_"))
                    type_path = function_path / type_name
                    type_path.mkdir(exist_ok=True)
                    (type_path / "__init__.py").write_text(f'"""{type_name.title()} Package"""\n')
                    
                    # Copy Python files and create importable modules
                    for py_file in hyphenated_type.rglob("*.py"):
                        if py_file.is_file():
                            # Read original file
                            with open(py_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Write to importable structure
                            target_file = type_path / py_file.name
                            with open(target_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            print(f"✅ Copied: {py_file.relative_to(agentic_core_path)} -> {target_file.relative_to(importable_path)}")
    
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
