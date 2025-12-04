#!/usr/bin/env python3
"""
Final Canonicalization Script for Phase 1 Migration
Converts hyphenated directory names to underscore format for SSoT compliance
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

class FinalCanonicalizer:
    def __init__(self, target_root: str):
        self.target_root = Path(target_root)
        self.corrections = []
        
    def find_hyphenated_dirs(self) -> List[Path]:
        """Find all directories with hyphens in their names"""
        hyphenated_dirs = []
        
        for item in self.target_root.rglob("*"):
            if item.is_dir() and "-" in item.name:
                hyphenated_dirs.append(item)
                
        return hyphenated_dirs
    
    def rename_hyphenated_to_underscore(self, hyphenated_dir: Path) -> bool:
        """Rename directory from hyphenated to underscore format"""
        try:
            parent = hyphenated_dir.parent
            old_name = hyphenated_dir.name
            new_name = old_name.replace("-", "_")
            new_path = parent / new_name
            
            print(f"Renaming: {hyphenated_dir} -> {new_path}")
            
            # Handle target exists
            if new_path.exists():
                print(f"Warning: Target {new_path} already exists, merging contents")
                # Merge contents
                for item in hyphenated_dir.iterdir():
                    target_item = new_path / item.name
                    if target_item.exists():
                        if item.is_file():
                            target_item.unlink()
                        elif item.is_dir():
                            # Recursively merge
                            for subitem in item.iterdir():
                                shutil.move(str(subitem), str(target_item / subitem.name))
                            item.rmdir()
                            continue
                    shutil.move(str(item), str(target_item))
                
                # Remove empty source directory
                try:
                    hyphenated_dir.rmdir()
                except OSError:
                    pass
                    
                self.corrections.append(f"MERGE_RENAME: {old_name} -> {new_name}")
            else:
                # Simple rename
                shutil.move(str(hyphenated_dir), str(new_path))
                self.corrections.append(f"RENAME: {old_name} -> {new_name}")
                
            return True
            
        except Exception as e:
            print(f"Error renaming {hyphenated_dir}: {e}")
            return False
    
    def verify_canonical_naming(self) -> Tuple[bool, List[str]]:
        """Verify no hyphenated directories remain"""
        issues = []
        
        hyphenated_dirs = self.find_hyphenated_dirs()
        if hyphenated_dirs:
            issues.extend([f"Remaining hyphenated: {d}" for d in hyphenated_dirs])
        
        # Verify required canonical structure
        required_patterns = [
            "L1_cognition", "L2_execution", "L3_orchestration", "L4_memory", "L5_safety",
            "P1_retrieve", "P2_inspect", "P3_aggregate", "P4_safety"
        ]
        
        for pattern in required_patterns:
            pattern_path = self.target_root / pattern
            if not pattern_path.exists():
                issues.append(f"Missing required structure: {pattern}")
        
        return len(issues) == 0, issues
    
    def execute_final_canonicalization(self):
        """Execute final canonicalization process"""
        try:
            print("=== FINAL CANONICALIZATION STARTING ===")
            
            # Find and fix hyphenated directories
            hyphenated_dirs = self.find_hyphenated_dirs()
            print(f"Found {len(hyphenated_dirs)} hyphenated directories")
            
            for hyphenated_dir in hyphenated_dirs:
                self.rename_hyphenated_to_underscore(hyphenated_dir)
            
            # Verify results
            success, issues = self.verify_canonical_naming()
            
            if success:
                print("=== FINAL CANONICALIZATION SUCCESSFUL ===")
                print(f"Total corrections performed: {len(self.corrections)}")
                return True
            else:
                print("=== FINAL CANONICALIZATION ISSUES REMAIN ===")
                for issue in issues:
                    print(f"ISSUE: {issue}")
                return False
                
        except Exception as e:
            print(f"=== FINAL CANONICALIZATION FAILED: {e} ===")
            return False

if __name__ == "__main__":
    canonicalizer = FinalCanonicalizer("01_agentic_core")
    success = canonicalizer.execute_final_canonicalization()
    exit(0 if success else 1)
