#!/usr/bin/env python3
"""
Structural Correction Script for Phase 1 Migration
Fixes double-nested directories created by axis mapping bug
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

class StructuralCorrector:
    def __init__(self, target_root: str):
        self.target_root = Path(target_root)
        self.corrections = []
        
    def find_double_nested_dirs(self) -> List[Path]:
        """Find directories where parent and child have same name"""
        doubled_dirs = []
        
        for item in self.target_root.rglob("*"):
            if item.is_dir():
                parent_name = item.parent.name
                child_name = item.name
                
                # Check for double nesting (parent and child have same name)
                if parent_name == child_name and parent_name != "":
                    doubled_dirs.append(item)
                    
        return doubled_dirs
    
    def flatten_double_nested_dir(self, doubled_dir: Path) -> bool:
        """Move contents from double-nested dir up one level"""
        try:
            parent = doubled_dir.parent
            grandparent = parent.parent
            
            print(f"Flattening: {grandparent}/{parent.name}/{doubled_dir.name} -> {grandparent}/{doubled_dir.name}")
            
            # Move all contents from doubled dir to parent
            for item in doubled_dir.iterdir():
                target_path = parent / item.name
                
                # Handle name conflicts
                if target_path.exists():
                    if item.is_file():
                        # For files, we'll overwrite (should be same content)
                        target_path.unlink()
                    elif item.is_dir():
                        # For directories, merge contents recursively
                        for subitem in item.iterdir():
                            shutil.move(str(subitem), str(target_path / subitem.name))
                        item.rmdir()
                        continue
                
                shutil.move(str(item), str(target_path))
            
            # Remove the now-empty doubled directory
            doubled_dir.rmdir()
            
            self.corrections.append(f"FLATTEN: {doubled_dir}")
            return True
            
        except Exception as e:
            print(f"Error flattening {doubled_dir}: {e}")
            return False
    
    def fix_legacy_phase_names(self):
        """Fix any remaining legacy phase names that weren't migrated"""
        legacy_fixes = {
            "expand-phase": "P2_inspect",
            "refine-phase": "P3_aggregate"
        }
        
        for legacy_name, canonical_name in legacy_fixes.items():
            for item in list(self.target_root.rglob(legacy_name)):  # Use list() to avoid modification during iteration
                if item.is_dir():
                    canonical_path = item.parent / canonical_name
                    print(f"Merging legacy phase: {item} -> {canonical_path}")
                    
                    # Ensure target directory exists
                    canonical_path.mkdir(exist_ok=True)
                    
                    # Merge contents from legacy to canonical
                    for subitem in item.iterdir():
                        target_subpath = canonical_path / subitem.name
                        
                        # Handle conflicts
                        if target_subpath.exists():
                            if subitem.is_file():
                                # For conflicting files, remove target and move source
                                target_subpath.unlink()
                                shutil.move(str(subitem), str(target_subpath))
                            elif subitem.is_dir():
                                # For directories, recursively merge contents
                                for subsubitem in subitem.iterdir():
                                    target_subsubpath = target_subpath / subsubitem.name
                                    if target_subsubpath.exists():
                                        if subsubitem.is_file():
                                            target_subsubpath.unlink()
                                    shutil.move(str(subsubitem), str(target_subsubpath))
                                # Remove empty source directory
                                try:
                                    subitem.rmdir()
                                except OSError:
                                    # Directory not empty, continue (may have subdirs we couldn't merge)
                                    pass
                        else:
                            shutil.move(str(subitem), str(target_subpath))
                    
                    # Remove the now-empty legacy directory
                    try:
                        item.rmdir()
                        self.corrections.append(f"MERGE_PHASE: {item} -> {canonical_path}")
                    except OSError as e:
                        print(f"Warning: Could not remove {item}: {e}")
                        self.corrections.append(f"PARTIAL_MERGE: {item} -> {canonical_path}")
    
    def verify_canonical_structure(self) -> Tuple[bool, List[str]]:
        """Verify structure matches SSoT canonical requirements"""
        issues = []
        
        # Check for any remaining double-nested dirs
        doubled_dirs = self.find_double_nested_dirs()
        if doubled_dirs:
            issues.extend([f"Remaining double-nested: {d}" for d in doubled_dirs])
        
        # Check for legacy names
        legacy_patterns = ["-", "core-", "check-"]
        for item in self.target_root.rglob("*"):
            if item.is_dir():
                if any(pattern in item.name for pattern in legacy_patterns):
                    issues.append(f"Legacy naming: {item}")
        
        # Verify required structure exists
        required_layers = ["L1_cognition", "L2_execution", "L3_orchestration", "L4_memory", "L5_safety"]
        for layer in required_layers:
            layer_path = self.target_root / layer
            if not layer_path.exists():
                issues.append(f"Missing layer: {layer}")
            
            # Check phases within each layer
            required_phases = ["P1_retrieve", "P2_inspect", "P3_aggregate", "P4_safety"]
            for phase in required_phases:
                phase_path = layer_path / phase
                if not phase_path.exists():
                    issues.append(f"Missing phase: {layer}/{phase}")
        
        return len(issues) == 0, issues
    
    def execute_corrections(self):
        """Execute all structural corrections"""
        try:
            print("=== STRUCTURAL CORRECTION STARTING ===")
            
            # Find and fix double-nested directories
            doubled_dirs = self.find_double_nested_dirs()
            print(f"Found {len(doubled_dirs)} double-nested directories")
            
            for doubled_dir in doubled_dirs:
                self.flatten_double_nested_dir(doubled_dir)
            
            # Fix remaining legacy phase names
            self.fix_legacy_phase_names()
            
            # Verify corrections
            success, issues = self.verify_canonical_structure()
            
            if success:
                print("=== CORRECTION SUCCESSFUL ===")
                print(f"Total corrections performed: {len(self.corrections)}")
                return True
            else:
                print("=== CORRECTION ISSUES REMAIN ===")
                for issue in issues:
                    print(f"ISSUE: {issue}")
                return False
                
        except Exception as e:
            print(f"=== CORRECTION FAILED: {e} ===")
            return False

if __name__ == "__main__":
    corrector = StructuralCorrector("01_agentic_core")
    success = corrector.execute_corrections()
    exit(0 if success else 1)
