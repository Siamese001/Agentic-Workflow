from __future__ import annotations
#!/usr/bin/env python3
"""
File Cleanup Agent
Batch agent: Identifies and removes files with repeated strings in filenames.
Handles cases like 'data_models_enums_enums_enums' -> keeps only 'data_models_enums'
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from collections import defaultdict
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


class FileCleanupAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Batch agent: Identifies and removes files with repeated strings in filenames.
    Detects patterns like 'word_word', 'word_word_word', etc.
    """

    def __init__(self, project_root: Path, ctx, dry_run: bool = True) -> None:
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.dry_run = dry_run
        self.files_to_remove: List[Path] = []
        self.files_to_keep: Dict[str, Path] = {}
        self.removed_count = 0

    def _has_repeated_strings(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Check if filename has repeated consecutive strings OR repeated substrings.
        Returns (has_repeats, pattern) where pattern is the repeated part.
        
        Examples:
            'enums_enums' -> (True, 'enums')
            'impl_impl_impl' -> (True, 'impl')
            'data_models_enums_enums' -> (True, 'enums')
            'test_data' -> (False, None)
        """
        # Split by underscore
        parts = filename.split('_')
        
        # Check for consecutive repeated parts
        for i in range(len(parts) - 1):
            if parts[i] == parts[i + 1] and parts[i]:
                return True, parts[i]
        
        # Check for repeated substrings (e.g., 'data_models_enums_enums')
        # Look for any part that appears more than once
        from collections import Counter
        part_counts = Counter(parts)
        for part, count in part_counts.items():
            if count > 1 and part:  # Part appears multiple times
                return True, part
        
        return False, None

    def _get_canonical_name(self, filename: str) -> str:
        """
        Get the canonical (de-duplicated) version of a filename.
        
        Examples:
            'enums_enums_enums' -> 'enums'
            'impl_impl' -> 'impl'
            'test_test_data' -> 'test_data'
        """
        parts = filename.split('_')
        canonical_parts = []
        
        for part in parts:
            # Only add if not same as previous part
            if not canonical_parts or canonical_parts[-1] != part:
                canonical_parts.append(part)
        
        return '_'.join(canonical_parts)

    def _count_repetitions(self, filename: str) -> int:
        """Count how many times strings are repeated in filename."""
        parts = filename.split('_')
        max_reps = 0
        
        i = 0
        while i < len(parts):
            current_part = parts[i]
            reps = 1
            j = i + 1
            
            # Count consecutive repetitions
            while j < len(parts) and parts[j] == current_part:
                reps += 1
                j += 1
            
            max_reps = max(max_reps, reps)
            i = j if j > i + 1 else i + 1
        
        return max_reps

    def scan_for_repeated_filenames(self, directories: List[str]) -> Dict:
        """
        Scan directories for files with repeated strings in filenames.
        Groups files by their canonical name.
        """
        print('\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[*] FileCleanupAgent: Scanning for files with repeated strings...')
        
        # Group files by canonical name
        canonical_groups = defaultdict(list)
        
        for dir_str in directories:
            dir_path = Path(dir_str)
            if not dir_path.exists():
                continue
            
            # Recursively find all files
            for file_path in dir_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip __pycache__ and other system files
                if '__pycache__' in str(file_path) or file_path.name.startswith('.'):
                    continue
                
                filename = file_path.stem  # Without extension
                has_repeats, pattern = self._has_repeated_strings(filename)
                
                if has_repeats:
                    canonical = self._get_canonical_name(filename)
                    repetitions = self._count_repetitions(filename)
                    
                    canonical_groups[canonical].append({
                        'path': file_path,
                        'original_name': filename,
                        'repetitions': repetitions,
                        'pattern': pattern
                    })
        
        # Analyze groups and decide what to keep/remove
        for canonical, files in canonical_groups.items():
            if len(files) == 0:
                continue
            
            # Sort by repetition count (fewer repetitions = better)
            files.sort(key=lambda x: x['repetitions'])
            
            # Keep the file with fewest repetitions
            best_file = files[0]
            self.files_to_keep[canonical] = best_file['path']
            
            # Mark others for removal
            for file_info in files[1:]:
                self.files_to_remove.append(file_info['path'])
                print(f"   [!] DUPLICATE: {file_info['path'].name} "
                      f"(reps: {file_info['repetitions']}, pattern: '{file_info['pattern']}')")
            
            if len(files) > 1:
                print(f"   [✓] KEEPING: {best_file['path'].name} "
                      f"(reps: {best_file['repetitions']})")
        
        return {
            'total_files_scanned': sum(len(files) for files in canonical_groups.values()),
            'canonical_groups': len(canonical_groups),
            'files_to_remove': len(self.files_to_remove),
            'files_to_keep': len(self.files_to_keep)
        }

    def execute_cleanup(self) -> Dict:
        """
        Execute the cleanup by removing duplicate files.
        Respects dry_run flag.
        """
        if self.dry_run:
            print(f'\n[DRY RUN] Would remove {len(self.files_to_remove)} files')
            for file_path in self.files_to_remove[:10]:  # Show first 10
                print(f'   - {file_path}')
            if len(self.files_to_remove) > 10:
                print(f'   ... and {len(self.files_to_remove) - 10} more')
            return {
                'dry_run': True,
                'would_remove': len(self.files_to_remove)
            }
        
        # Actually remove files
        print(f'\n[*] Removing {len(self.files_to_remove)} duplicate files...')
        
        for file_path in self.files_to_remove:
            try:
                file_path.unlink()
                self.removed_count += 1
                print(f'   [✓] Removed: {file_path}')
            except Exception as e:
                print(f'   [✗] Failed to remove {file_path}: {e}')
        
        print(f'\n[✓] Cleanup complete: {self.removed_count} files removed')
        
        return {
            'dry_run': False,
            'removed': self.removed_count,
            'failed': len(self.files_to_remove) - self.removed_count
        }

    async def execute(self) -> Dict:
        """Main execution method for batch agent interface."""
        if not hasattr(self.ctx, 'scan_directories'):
            # Default to project root subdirectories
            scan_dirs = [
                str(self.project_root / 'agentic_core'),
                str(self.project_root / 'data')
            ]
        else:
            scan_dirs = self.ctx.scan_directories
        
        # Scan for files
        scan_results = self.scan_for_repeated_filenames(scan_dirs)
        
        # Execute cleanup if files found
        if self.files_to_remove:
            cleanup_results = self.execute_cleanup()
            return {**scan_results, **cleanup_results}
        else:
            print('   [OK] No files with repeated strings found.')
            return scan_results

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[Set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def get_file_cleanup_agent(project_root: Path, ctx, dry_run=True) -> Any:
    """Factory function"""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    return FileCleanupAgent(project_root, ctx, dry_run)
