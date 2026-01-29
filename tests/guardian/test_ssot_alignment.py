"""
Phase 3: The SSOT & Structure Guard

Enforces that the file system strictly mirrors structure_blueprint.py.
Detects "Rogue Agents" and enforces naming conventions.

Test Plan:
1. test_blueprint_physical_verification - Verify blueprint files exist on disk
2. test_rogue_file_detection - Detect unregistered .py files in apps_rg/ and apps_lic/
3. test_naming_convention_enforcer - Enforce PascalCase/suffix rules for agents
"""
import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any
import pytest


def get_ssot_registry() -> Dict[str, Any]:
    """
    Get the SSOT registry from structure_blueprint.py.
    Handles broken imports by parsing the file directly if needed.
    """
    try:
        # Try direct import first
        from agentic_core.L5_safety.validators.structure_blueprint import (
            SOVEREIGN_TERRITORIES,
            CORE_SUBFOLDER_MAP,
            APPS_RG_SUBFOLDER_MAP,
            APPS_LIC_SUBFOLDER_MAP,
            APPS_SHARED_SUBFOLDER_MAP,
        )
        return {
            "territories": SOVEREIGN_TERRITORIES,
            "core_subfolders": CORE_SUBFOLDER_MAP,
            "apps_rg_subfolders": APPS_RG_SUBFOLDER_MAP,
            "apps_lic_subfolders": APPS_LIC_SUBFOLDER_MAP,
            "apps_shared_subfolders": APPS_SHARED_SUBFOLDER_MAP,
        }
    except ImportError as e:
        # Fallback: Parse the file directly
        blueprint_path = Path("agentic_core/L5_safety/validators/structure_blueprint.py")
        if not blueprint_path.exists():
            pytest.fail(f"structure_blueprint.py not found at {blueprint_path}")
        
        with open(blueprint_path, 'r') as f:
            content = f.read()
        
        # Extract the registry using regex (fallback for broken imports)
        try:
            tree = ast.parse(content)
            registry = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            if name in [
                                "SOVEREIGN_TERRITORIES",
                                "CORE_SUBFOLDER_MAP", 
                                "APPS_RG_SUBFOLDER_MAP",
                                "APPS_LIC_SUBFOLDER_MAP",
                                "APPS_SHARED_SUBFOLDER_MAP"
                            ]:
                                # Evaluate the assigned value
                                value = ast.literal_eval(node.value)
                                registry[name.lower()] = value
            
            return {
                "territories": registry.get("sovereign_territories", {}),
                "core_subfolders": registry.get("core_subfolder_map", {}),
                "apps_rg_subfolders": registry.get("apps_rg_subfolder_map", {}),
                "apps_lic_subfolders": registry.get("apps_lic_subfolder_map", {}),
                "apps_shared_subfolders": registry.get("apps_shared_subfolder_map", {}),
            }
        except (SyntaxError, ValueError) as parse_error:
            pytest.fail(f"Failed to parse structure_blueprint.py: {parse_error}")


def get_all_blueprint_files(ssot_registry: Dict[str, Any]) -> Set[Path]:
    """
    Extract all file paths that should exist according to the blueprint.
    """
    blueprint_files = set()
    project_root = Path(".")
    
    # Get all territories and their expected structure
    territories = ssot_registry["territories"]
    
    for territory_name, territory_def in territories.items():
        territory_path = project_root / territory_name
        
        # Add territory root if it should exist
        if territory_path.exists():
            blueprint_files.add(territory_path)
        
        # Process subfolders
        subfolders = territory_def.get("subfolders", {})
        
        if isinstance(subfolders, dict):
            for subfolder_name, subfolder_def in subfolders.items():
                subfolder_path = territory_path / subfolder_name
                
                # Add subfolder directory
                blueprint_files.add(subfolder_path)
                
                # If subfolder has further definition, process it
                if isinstance(subfolder_def, dict):
                    nested_subfolders = subfolder_def.get("subfolders", {})
                    if nested_subfolders:
                        for nested_name in nested_subfolders:
                            nested_path = subfolder_path / nested_name
                            blueprint_files.add(nested_path)
        elif isinstance(subfolders, list):
            # Simple list of subfolder names
            for subfolder_name in subfolders:
                subfolder_path = territory_path / subfolder_name
                blueprint_files.add(subfolder_path)
    
    return blueprint_files


def get_all_python_files(directory: Path) -> Set[Path]:
    """
    Walk a directory and return all .py files.
    """
    python_files = set()
    if not directory.exists():
        return python_files
    
    for file_path in directory.rglob("*.py"):
        if file_path.is_file():
            python_files.add(file_path)
    
    return python_files


def get_blueprint_python_files(ssot_registry: Dict[str, Any]) -> Set[Path]:
    """
    Get all .py files that are registered in the blueprint.
    Since blueprint defines directories but not individual files,
    we'll consider all .py files within blueprint directories as registered.
    """
    blueprint_files = set()
    project_root = Path(".")
    
    territories = ssot_registry["territories"]
    
    for territory_name, territory_def in territories.items():
        territory_path = project_root / territory_name
        
        if not territory_path.exists():
            continue
            
        # Get all subfolders defined in blueprint
        subfolders = territory_def.get("subfolders", {})
        
        if isinstance(subfolders, dict):
            subfolder_names = subfolders.keys()
        elif isinstance(subfolders, list):
            subfolder_names = subfolders
        else:
            continue
        
        # Add all .py files in blueprint-defined directories
        for subfolder_name in subfolder_names:
            subfolder_path = territory_path / subfolder_name
            if subfolder_path.exists():
                blueprint_files.update(get_all_python_files(subfolder_path))
    
    return blueprint_files


def test_blueprint_physical_verification():
    """
    Test 1: Verify that every file/directory listed in the blueprint actually exists.
    """
    print("\n=== PHASE 3: Blueprint Physical Verification ===")
    
    ssot_registry = get_ssot_registry()
    blueprint_paths = get_all_blueprint_files(ssot_registry)
    
    missing_files = []
    for blueprint_path in blueprint_paths:
        if not blueprint_path.exists():
            missing_files.append(str(blueprint_path))
    
    if missing_files:
        error_msg = "Blueprint claims these paths exist but they are missing:\n"
        for missing in sorted(missing_files):
            error_msg += f"  - {missing}\n"
        pytest.fail(error_msg)
    
    print(f"✅ Verified {len(blueprint_paths)} blueprint paths exist on disk")


def test_rogue_file_detection():
    """
    Test 2: Detect .py files that exist on disk but are NOT in the blueprint.
    """
    print("\n=== PHASE 3: Rogue File Detection ===")
    
    ssot_registry = get_ssot_registry()
    blueprint_python_files = get_blueprint_python_files(ssot_registry)
    
    # Check apps_rg and apps_lic for rogue files
    rogue_files = []
    
    for app_dir in [Path("apps_rg"), Path("apps_lic")]:
        if not app_dir.exists():
            continue
            
        actual_python_files = get_all_python_files(app_dir)
        
        for actual_file in actual_python_files:
            if actual_file not in blueprint_python_files:
                rogue_files.append(str(actual_file))
    
    if rogue_files:
        error_msg = "ROGUE FILES DETECTED - These .py files exist but are not in blueprint:\n"
        for rogue in sorted(rogue_files):
            error_msg += f"  - {rogue}\n"
        pytest.fail(error_msg)
    
    print(f"✅ No rogue files found in apps_rg/ and apps_lic/")


def check_agent_class_naming(file_path: Path) -> List[str]:
    """
    Check if Agent classes in a file follow naming conventions.
    Returns list of violations.
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                
                # Check if it's an Agent class (inherits from something with "Agent")
                is_agent_class = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and "Agent" in base.id:
                        is_agent_class = True
                        break
                    elif isinstance(base, ast.Attribute) and "Agent" in str(base):
                        is_agent_class = True
                        break
                
                if is_agent_class:
                    # Agent classes must end with "Agent" suffix
                    if not class_name.endswith("Agent"):
                        violations.append(
                            f"Agent class '{class_name}' must end with 'Agent' suffix"
                        )
    
    except (SyntaxError, UnicodeDecodeError):
        # Skip files that can't be parsed
        pass
    
    return violations


def test_naming_convention_enforcer():
    """
    Test 3: Enforce naming conventions for files and classes.
    """
    print("\n=== PHASE 3: Naming Convention Enforcement ===")
    
    violations = []
    
    # Check apps_rg (Business Logic)
    apps_rg = Path("apps_rg")
    if apps_rg.exists():
        for file_path in get_all_python_files(apps_rg):
            relative_path = file_path.relative_to(Path("."))
            path_parts = relative_path.parts
            
            # Assertion A: Files in agents/ or engines/ MUST use PascalCase
            if any(part in ["agents", "engines"] for part in path_parts[:-1]):
                filename = file_path.stem
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', filename):
                    violations.append(
                        f"File in agents/engines must use PascalCase: {relative_path}"
                    )
            
            # Check Agent class naming
            agent_violations = check_agent_class_naming(file_path)
            for violation in agent_violations:
                violations.append(f"{relative_path}: {violation}")
    
    # Check apps_lic as well
    apps_lic = Path("apps_lic")
    if apps_lic.exists():
        for file_path in get_all_python_files(apps_lic):
            relative_path = file_path.relative_to(Path("."))
            path_parts = relative_path.parts
            
            # Assertion A: Files in agents/ or engines/ MUST use PascalCase
            if any(part in ["agents", "engines"] for part in path_parts[:-1]):
                filename = file_path.stem
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', filename):
                    violations.append(
                        f"File in agents/engines must use PascalCase: {relative_path}"
                    )
            
            # Assertion B: Files in utils/ or scripts/ MUST use snake_case
            if any(part in ["utils", "scripts"] for part in path_parts[:-1]):
                filename = file_path.stem
                if not re.match(r'^[a-z][a-z0-9_]*$', filename):
                    violations.append(
                        f"File in utils/scripts must use snake_case: {relative_path}"
                    )
            
            # Check Agent class naming
            agent_violations = check_agent_class_naming(file_path)
            for violation in agent_violations:
                violations.append(f"{relative_path}: {violation}")
    
    if violations:
        error_msg = "NAMING CONVENTION VIOLATIONS:\n"
        for violation in sorted(violations):
            error_msg += f"  - {violation}\n"
        pytest.fail(error_msg)
    
    print("✅ All naming conventions enforced successfully")


if __name__ == "__main__":
    # Run tests manually for debugging
    test_blueprint_physical_verification()
    test_rogue_file_detection()
    test_naming_convention_enforcer()
    print("\n🎉 PHASE 3 COMPLETE: All SSOT & Structure Guard tests passed!")
