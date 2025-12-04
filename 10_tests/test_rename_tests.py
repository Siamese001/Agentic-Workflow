#!/usr/bin/env python3
"""
Semantic-Fitness Test Renamer for Agentic-Workflow
Converts operational verb filenames to high-signal test intent names
Zero-loss, fully reversible, structure-preserving
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class TestRenamer:
    def __init__(self, tests_root: str = "10_tests", data_dir: str = "06_data"):
        self.tests_root = Path(tests_root).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.backup_dir = self.data_dir / f"10_tests_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.rename_log_file = self.data_dir / "test_rename_log.json"
        self.rename_log = []
        self.dry_run = True  # Safety first
        
        # Semantic rewrite rules - ordered from most specific to least specific
        # Rules return ONLY the new filename (not full paths) to preserve directory structure
        self.semantic_rules = [
            # Safety-specific rules first (safety context)
            (r'/P4_safety/.*/policy/test_apply\.py$', 'test_apply_safety_policies.py'),
            (r'/P4_safety/.*/policy/test_enforce\.py$', 'test_enforce_safety_thresholds.py'),
            (r'/P4_safety/.*/policy/test_validate\.py$', 'test_safety_policy_schema_validation.py'),
            (r'/P4_safety/.*/update/test_enforce\.py$', 'test_enforce_resource_limits.py'),
            (r'/P4_safety/.*/update/test_track\.py$', 'test_track_resource_usage.py'),
            (r'/P4_safety/.*/update/test_update\.py$', 'test_update_safety_state.py'),
            
            # General policy rules (safety context handled above)
            (r'/policy/test_check\.py$', 'test_policy_rule_selection.py'),
            (r'/policy/test_enforce\.py$', 'test_policy_enforcement_paths.py'),
            (r'/policy/test_validate\.py$', 'test_policy_schema_validation.py'),
            (r'/policy/test_apply\.py$', 'test_apply_safety_policies.py'),  # fallback for non-safety context
            
            # Embedding/vector-related files
            (r'/embedding/test_match\.py$', 'test_match_embedding_neighbors.py'),
            (r'/embedding/test_retrieve_similarity\.py$', 'test_retrieve_similarity_topk.py'),
            (r'/embedding/test_search\.py$', 'test_search_fallback_mechanism.py'),
            (r'/embedding/test_compute\.py$', 'test_embedding_compute_determinism.py'),
            (r'/embedding/test_normalize\.py$', 'test_embedding_normalization_invariants.py'),
            
            # Understand/input-parsing tests
            (r'/understand/test_extract\.py$', 'test_extract_input_fields.py'),
            (r'/understand/test_fetch\.py$', 'test_fetch_remote_resources.py'),
            (r'/understand/test_load\.py$', 'test_load_config_and_state.py'),
            (r'/understand/test_parse\.py$', 'test_parse_user_queries.py'),
            (r'/understand/test_query\.py$', 'test_query_routing_logic.py'),
            (r'/understand/test_retrieve\.py$', 'test_retrieve_context_documents.py'),
            
            # Utility folder upgrades
            (r'/utility/test_build\.py$', 'test_build_context_object.py'),
            (r'/utility/test_format\.py$', 'test_format_context_payload.py'),
            (r'/utility/test_prepare\.py$', 'test_prepare_normalized_inputs.py'),
            (r'/utility/test_snapshot\.py$', 'test_prepare_status_snapshots.py'),
            
            # Semantic evaluation/transform layer
            (r'/semantic/test_assess\.py$', 'test_semantic_assessment_scores.py'),
            (r'/semantic/test_evaluate\.py$', 'test_semantic_compute_consistency.py'),
            (r'/semantic/test_score\.py$', 'test_semantic_threshold_scoring.py'),
            (r'/semantic/test_apply\.py$', 'test_semantic_apply_transforms.py'),
            (r'/semantic/test_compute\.py$', 'test_semantic_compute_features.py'),
            (r'/semantic/test_normalize\.py$', 'test_semantic_normalize_outputs.py'),
            
            # Routing/orchestration tests
            (r'/routing/test_apply\.py$', 'test_apply_routing_decisions.py'),
            (r'/routing/test_handle\.py$', 'test_handle_routing_errors.py'),
            (r'/routing/test_implement\.py$', 'test_implement_retry_logic.py'),
            (r'/routing/test_retry\.py$', 'test_retry_failure_modes.py'),
            
            # Refinement layer
            (r'/refinement/test_adjust\.py$', 'test_adjust_rankings_on_feedback.py'),
            (r'/refinement/test_optimize\.py$', 'test_optimize_candidate_set.py'),
            (r'/refinement/test_refine\.py$', 'regression_guard_refinement_regressions.py'),
            
            # Status/merge/aggregate behaviors
            (r'/update/test_aggregate\.py$', 'test_aggregate_status_across_sources.py'),
            (r'/update/test_consolidate\.py$', 'test_consolidate_state_transitions.py'),
            (r'/update/test_merge\.py$', 'test_merge_status_records.py'),
            (r'/update/test_enforce\.py$', 'test_enforce_resource_limits.py'),  # fallback for non-safety
            (r'/update/test_track\.py$', 'test_track_resource_usage.py'),     # fallback for non-safety
            (r'/update/test_update\.py$', 'test_update_safety_state.py'),    # fallback for non-safety
        ]
    
    def validate_environment(self) -> bool:
        """Red flag detection: ensure we're in the right place"""
        if not self.tests_root.exists():
            print(f"ERROR: Tests directory {self.tests_root} not found")
            return False
        
        if not str(self.tests_root).endswith("10_tests"):
            print(f"ERROR: Directory must be named '10_tests', found: {self.tests_root}")
            return False
        
        return True
    
    def create_backup(self) -> bool:
        """Create full backup before any operations"""
        if not self.dry_run:
            print(f"Creating backup at: {self.backup_dir}")
            try:
                shutil.copytree(self.tests_root, self.backup_dir)
                print(f"Backup created successfully")
                return True
            except Exception as e:
                print(f"ERROR: Failed to create backup: {e}")
                return False
        else:
            print(f"DRY RUN: Would create backup at: {self.backup_dir}")
            return True
    
    def find_test_files(self) -> List[Path]:
        """Find all Python files in tests directory"""
        test_files = []
        for py_file in self.tests_root.rglob("*.py"):
            # Skip __init__.py files
            if py_file.name == "__init__.py":
                continue
            # Ensure we're under tests directory ( safety check)
            if str(py_file).startswith(str(self.tests_root)):
                test_files.append(py_file)
        return test_files
    
    def apply_master_rewrite(self, relative_path: str) -> str:
        """Apply master rewrite rule: add test_ prefix"""
        # Skip if already has test_ prefix
        filename = relative_path.split('/')[-1]
        if filename.startswith("test_"):
            return relative_path
        
        # Apply master rewrite: add test_ prefix
        parts = relative_path.split('/')
        if len(parts) >= 1:
            if filename.endswith('.py'):
                new_filename = f"test_{filename}"
                parts[-1] = new_filename
                return '/'.join(parts)
        
        return relative_path
    
    def apply_semantic_rules(self, path: str) -> str:
        """Apply semantic category rewrites - returns updated path with new filename only"""
        for pattern, replacement in self.semantic_rules:
            if re.search(pattern, path):
                # Replace just the filename part, preserve directory structure
                parts = path.split('/')
                parts[-1] = replacement  # Replace only the filename
                return '/'.join(parts)
        return path
    
    def check_collision(self, new_path: str) -> bool:
        """Check if target file already exists"""
        full_new_path = self.tests_root / new_path
        return full_new_path.exists()
    
    def plan_renames(self) -> List[Tuple[Path, str]]:
        """Plan all renames with validation"""
        test_files = self.find_test_files()
        rename_plan = []
        
        print(f"Found {len(test_files)} test files to process")
        
        for file_path in test_files:
            # Convert to relative path with forward slashes for regex matching
            relative_path = str(file_path.relative_to(self.tests_root)).replace('\\', '/')
            
            # Apply master rewrite
            master_path = self.apply_master_rewrite(relative_path)
            
            # Apply semantic rules
            final_path = self.apply_semantic_rules(master_path)
            
            # Check if rename is needed
            original_path = relative_path
            if final_path != original_path:
                # Check for collisions (convert back to OS path)
                if self.check_collision(final_path.replace('/', os.sep)):
                    print(f"WARNING: Collision detected - {final_path} already exists")
                    continue
                
                rename_plan.append((file_path, final_path))
        
        return rename_plan
    
    def execute_renames(self, rename_plan: List[Tuple[Path, str]]) -> bool:
        """Execute the rename plan"""
        print(f"\n{'DRY RUN: ' if self.dry_run else ''}Executing {len(rename_plan)} renames...")
        
        for old_path, new_relative_path in rename_plan:
            new_path = self.tests_root / new_relative_path
            
            # Ensure target directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.dry_run:
                print(f"  Would rename: {old_path.relative_to(self.tests_root)} -> {new_relative_path}")
            else:
                try:
                    # NEW SAFE RENAME LOGIC - preserve directory structure
                    old_resolved = old_path.resolve()
                    
                    # Ensure file is inside tests directory
                    try:
                        rel_path = old_resolved.relative_to(self.tests_root)
                    except ValueError:
                        print(f"[ERROR] File not under tests/: {old_resolved}")
                        continue
                    
                    # Build new path: SAME PARENTS, new filename only
                    new_path = self.tests_root / rel_path.parent / new_relative_path.split('/')[-1]
                    
                    # Safety: prevent overwrite
                    if new_path.exists():
                        print(f"[SKIP] Would not overwrite: {new_path}")
                        continue
                    
                    # Ensure target directory exists
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Execute rename
                    old_resolved.rename(new_path)
                    print(f"  Renamed (preserve dirs): {old_path.relative_to(self.tests_root)} -> {new_relative_path}")
                    
                    # Log the rename for reversibility
                    self.rename_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'old_path': str(old_path.relative_to(self.tests_root)),
                        'new_path': new_relative_path
                    })
                except Exception as e:
                    print(f"ERROR: Failed to rename {old_path}: {e}")
                    return False
        
        return True
    
    def save_rename_log(self) -> bool:
        """Save rename log for reversibility"""
        if not self.rename_log:
            return True
        
        log_file = self.rename_log_file
        try:
            with open(log_file, 'w') as f:
                json.dump(self.rename_log, f, indent=2)
            print(f"Rename log saved to: {log_file}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to save rename log: {e}")
            return False
    
    def run(self, dry_run: bool = True) -> bool:
        """Main execution method"""
        self.dry_run = dry_run
        
        print("=== Semantic Test File Renamer ===")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print(f"Tests directory: {self.tests_root}")
        
        # Validation
        if not self.validate_environment():
            return False
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Plan renames
        rename_plan = self.plan_renames()
        
        if not rename_plan:
            print("No files need renaming")
            return True
        
        print(f"\nPlanned renames:")
        for old_path, new_path in rename_plan:
            print(f"  {old_path.relative_to(self.tests_root)} -> {new_path}")
        
        # Execute renames
        if not self.execute_renames(rename_plan):
            return False
        
        # Save log
        if not dry_run:
            if not self.save_rename_log():
                return False
        
        print(f"\n{'DRY RUN completed successfully' if dry_run else 'Renaming completed successfully'}")
        return True

def main():
    renamer = TestRenamer()
    
    # Run dry run first
    print("=== DRY RUN MODE ===")
    if not renamer.run(dry_run=True):
        print("Dry run failed, aborting")
        return
    
    print("\n=== EXECUTION MODE ===")
    response = input("Proceed with actual renaming? (y/N): ")
    if response.lower() in ['y', 'yes']:
        if not renamer.run(dry_run=False):
            print("Renaming failed")
        else:
            print("All renames completed successfully!")
    else:
        print("Renaming cancelled by user")

if __name__ == "__main__":
    main()
