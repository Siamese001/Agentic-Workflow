"""File Cleanup Agent - Identifies and removes files with repeated strings in filenames.

This module provides a batch agent that identifies and removes files with
repeated strings in their filenames (e.g., 'data_models_enums_enums_enums').
It keeps the canonical version and removes duplicates.

Typical usage:
    agent = FileCleanupAgent(project_root=Path("/path/to/project"), ctx=context)
    result = await agent.execute()
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from agentic_core.L5_safety.validators.structure_blueprint_2 import AGENTIC_CORE_DIR
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class FileCleanupAgent(SubatomicTestingMixin, HealerMixin):
    """L5 Safety agent that identifies and removes files with repeated filename strings.
    
    This batch agent detects patterns like 'word_word', 'word_word_word' in filenames
    and removes duplicates while keeping the canonical (least-repeated) version.
    
    Attributes:
        project_root: Root directory of the project.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be removed (default: True).
        files_to_remove: List of file paths marked for removal.
        files_to_keep: Dictionary mapping canonical names to their paths.
        removed_count: Count of files actually removed.
        
    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, project_root: Path, ctx: Any, dry_run: bool = True) -> None:
        """Initialize the file cleanup agent.
        
        Args:
            project_root: Root directory of the project.
            ctx: Execution context with optional scan_directories attribute.
            dry_run: If True, only report what would be removed (default: True).
        """
        self.project_root: Path = Path(project_root)
        self.ctx: Any = ctx
        self.dry_run: bool = dry_run
        self.files_to_remove: List[Path] = []
        self.files_to_keep: Dict[str, Path] = {}
        self.removed_count: int = 0

    def _has_repeated_strings(self, filename: str) -> Tuple[bool, Optional[str]]:
        """Check if filename has repeated consecutive strings or repeated substrings.
        
        Args:
            filename: Filename to check (without extension).
            
        Returns:
            Tuple of (has_repeats, pattern) where pattern is the repeated part,
            or (False, None) if no repetition found.
            
        Examples:
            'enums_enums' -> (True, 'enums')
            'impl_impl_impl' -> (True, 'impl')
            'data_models_enums_enums' -> (True, 'enums')
            'test_data' -> (False, None)
        """
        parts: List[str] = filename.split('_')
        
        # Check for consecutive repeated parts
        for i in range(len(parts) - 1):
            if parts[i] == parts[i + 1] and parts[i]:
                return True, parts[i]
        
        # Check for repeated substrings
        part_counts: Counter[str] = Counter(parts)
        for part, count in part_counts.items():
            if count > 1 and part:
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
        print('\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[*] FileCleanupAgent: Scanning for files with repeated strings...')
        
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
                str(self.project_root / AGENTIC_CORE_DIR),
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
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """Execute L5 safety healing operations.
        
        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.
        
        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.
            
        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        super().heal_repository()
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


def get_file_cleanup_agent(project_root: Path, ctx: Any, dry_run: bool = True) -> FileCleanupAgent:
    """Factory function to create a FileCleanupAgent instance.
    
    Args:
        project_root: Root directory of the project.
        ctx: Execution context.
        dry_run: If True, only report what would be removed (default: True).
        
    Returns:
        Configured FileCleanupAgent instance.
    """
    return FileCleanupAgent(project_root, ctx, dry_run)