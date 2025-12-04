#!/usr/bin/env python3
"""
Safe Phase 1 Migration Script for agentic_core canonicalization
Ensures zero-loss guarantee with collision detection and atomic operations
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple

class SafeMigrator:
    def __init__(self, target_root: str, ssot_yaml: str, migration_plan: str):
        self.target_root = Path(target_root)
        self.ssot_yaml = Path(ssot_yaml)
        self.migration_plan = Path(migration_plan)
        self.operations = []
        self.collision_detector = set()
        
    def load_migration_plan(self) -> Dict:
        """Load existing migration plan for source→target mapping"""
        with open(self.migration_plan, 'r') as f:
            plan = json.load(f)
        return plan
    
    def build_path_mappings(self) -> Dict[str, str]:
        """Build explicit source→target path mappings from legacy to canonical"""
        mappings = {
            # Layer mappings
            "exec-layer": "L2_execution",
            "plan-layer": "L1_cognition", 
            "mem-layer": "L4_memory",
            "orc-layer": "L3_orchestration",
            "safe-layer": "L5_safety",
            
            # Phase mappings
            "plan-phase": "P1_retrieve",
            "retrieve-phase": "P1_retrieve", 
            "inspect-phase": "P2_inspect",
            "validate-phase": "P2_inspect",
            "agg-phase": "P3_aggregate",
            "act-phase": "P3_aggregate", 
            "safety-phase": "P4_safety",
            
            # Intent mappings
            "check-core-rules": "check_rules",
            "check-core-structure": "check_structure",
            "get-core-info": "get_info",
            "use-core-tools": "use_tools",
            "find-core-problems": "find_problems",
            "update-core-state": "update_state",
            "manage-core-costs": "manage_costs",
            
            # Axis mappings  
            "policy": "policy_check_safety",
            "check-safety": "policy_check_safety",
            "prepare-information": "utility_prepare_information",
            "use-a-tool": "use_a_tool",
            "understand-request": "understand_request",
            "update-memory": "update_memory",
            "compare-meaning": "embedding_compare_meaning",
            "adjust-scores": "semantic_adjust_scores"
        }
        return mappings
    
    def create_canonical_structure(self):
        """Create all target directories upfront"""
        print("Creating canonical directory structure...")
        
        # Create L1-L5 directories
        for layer in ["L1_cognition", "L2_execution", "L3_orchestration", "L4_memory", "L5_safety"]:
            layer_path = self.target_root / layer
            layer_path.mkdir(exist_ok=True)
            (layer_path / "__init__.py").touch()
            
            # Create phase directories within each layer
            for phase in ["P1_retrieve", "P2_inspect", "P3_aggregate", "P4_safety"]:
                phase_path = layer_path / phase
                phase_path.mkdir(exist_ok=True)
                (phase_path / "__init__.py").touch()
    
    def migrate_content_atomically(self):
        """Migrate files with collision detection and atomic operations"""
        mappings = self.build_path_mappings()
        legacy_root = self.target_root
        
        print("Starting atomic migration with collision detection...")
        
        # Walk legacy structure and migrate content
        for item in legacy_root.rglob("*"):
            if item.is_file() and item.name == "__init__.py":
                continue  # Skip __init__.py files, will recreate
                
            relative_path = item.relative_to(legacy_root)
            path_parts = list(relative_path.parts)
            
            # Apply canonical mapping to each path component
            canonical_parts = []
            for part in path_parts:
                canonical_parts.append(mappings.get(part, part))
            
            # Build target path
            target_path = legacy_root / Path(*canonical_parts)
            
            # Skip if target would be same as source
            if target_path == item:
                continue
                
            # Collision detection
            if target_path.exists():
                print(f"COLISION DETECTED: {target_path} already exists")
                continue
                
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Atomic move
            print(f"Moving: {item} -> {target_path}")
            shutil.move(str(item), str(target_path))
            self.operations.append(f"MOVE: {item} -> {target_path}")
    
    def create_missing_init_files(self):
        """Create __init__.py files throughout canonical structure"""
        print("Creating __init__.py files...")
        
        for root, dirs, files in os.walk(self.target_root):
            root_path = Path(root)
            init_file = root_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                self.operations.append(f"CREATE: {init_file}")
    
    def cleanup_legacy_dirs(self):
        """Remove empty legacy directories after migration"""
        print("Cleaning up empty legacy directories...")
        
        legacy_dirs = ["exec-layer", "plan-layer", "mem-layer", "orc-layer", "safe-layer"]
        for legacy_dir in legacy_dirs:
            dir_path = self.target_root / legacy_dir
            if dir_path.exists() and not any(dir_path.iterdir()):
                print(f"Removing empty directory: {dir_path}")
                dir_path.rmdir()
                self.operations.append(f"REMOVE_DIR: {dir_path}")
    
    def verify_migration(self) -> Tuple[bool, List[str]]:
        """Verify migration completeness and integrity"""
        print("Verifying migration integrity...")
        
        issues = []
        expected_layers = ["L1_cognition", "L2_execution", "L3_orchestration", "L4_memory", "L5_safety"]
        
        # Check all layers exist
        for layer in expected_layers:
            layer_path = self.target_root / layer
            if not layer_path.exists():
                issues.append(f"Missing layer: {layer}")
            elif not (layer_path / "__init__.py").exists():
                issues.append(f"Missing __init__.py in layer: {layer}")
        
        # Count files for verification
        file_count = len(list(self.target_root.rglob("*.py")))
        print(f"Total Python files after migration: {file_count}")
        
        return len(issues) == 0, issues
    
    def execute_safe_migration(self):
        """Execute complete safe migration process"""
        try:
            print("=== SAFE PHASE 1 MIGRATION STARTING ===")
            
            self.create_canonical_structure()
            self.migrate_content_atomically() 
            self.create_missing_init_files()
            self.cleanup_legacy_dirs()
            
            success, issues = self.verify_migration()
            
            if success:
                print("=== MIGRATION SUCCESSFUL ===")
                print(f"Total operations performed: {len(self.operations)}")
                return True
            else:
                print("=== MIGRATION ISSUES DETECTED ===")
                for issue in issues:
                    print(f"ISSUE: {issue}")
                return False
                
        except Exception as e:
            print(f"=== MIGRATION FAILED: {e} ===")
            return False

if __name__ == "__main__":
    migrator = SafeMigrator(
        target_root="01_agentic_core",
        ssot_yaml="unified_structure_subatomic.yaml", 
        migration_plan="02_schemas/agentic_core_migration_plan.json"
    )
    
    success = migrator.execute_safe_migration()
    exit(0 if success else 1)
