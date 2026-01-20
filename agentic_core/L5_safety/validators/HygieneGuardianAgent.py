"""
HygieneGuardianAgent - Repository Hygiene Enforcement

Consolidates hygiene checks:
- Empty file detection and cleanup
- Orphaned __init__.py files
- Stale backup files (.bak, .orig, .backup)
- Temporary files cleanup (.tmp, .temp, ~)
- Debug print statement detection
- Commented-out code detection

Territory: agentic_core/L5_safety/validators/
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
from agentic_core.L5_safety.validators.decorators import standard_heal


@dataclass
class HygieneViolation:
    """Structured violation for hygiene issues."""
    file_path: Path
    violation_type: str
    message: str
    line_number: Optional[int] = None
    severity: int = 5  # 1-10, 10 being critical
    auto_fixable: bool = False


class HygieneGuardianAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Repository hygiene enforcement agent.
    
    Detects and optionally fixes:
    - Empty files (0 bytes or only whitespace)
    - Orphaned __init__.py files (in directories with no other Python files)
    - Stale backup files (.bak, .orig, .backup)
    - Temporary files (.tmp, .temp, ~)
    - Debug print statements
    - Large blocks of commented-out code
    
    Inherits:
        SubatomicTestingMixin: Testing utilities
        HealerMixin: Healing chain support
        MCPHardenedMixin: MCP integration
    """
    
    # File extensions to check
    PYTHON_EXTENSIONS = {'.py', '.pyi'}
    BACKUP_EXTENSIONS = {'.bak', '.orig', '.backup', '.old'}
    TEMP_EXTENSIONS = {'.tmp', '.temp', '.swp', '.swo'}
    
    # Patterns for detection
    DEBUG_PRINT_PATTERN = re.compile(r'^\s*print\s*\(', re.MULTILINE)
    COMMENTED_CODE_PATTERN = re.compile(r'^\s*#\s*(def|class|import|from|if|for|while|try)\s+', re.MULTILINE)
    
    def __init__(self, project_root: Path, ctx: Any = None, dry_run: bool = True):
        """
        Initialize the hygiene guardian.
        
        Args:
            project_root: Root directory of the project
            ctx: Execution context (optional)
            dry_run: If True, only report violations without fixing
        """
        self.project_root = Path(project_root).resolve()
        self.ctx = ctx
        self.dry_run = dry_run
        self.violations: List[HygieneViolation] = []
        
    def _is_empty_file(self, file_path: Path) -> bool:
        """Check if file is empty or contains only whitespace."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return len(content.strip()) == 0
        except Exception:
            return False
    
    def _is_orphaned_init(self, file_path: Path) -> bool:
        """Check if __init__.py is orphaned (no other Python files in directory)."""
        if file_path.name != '__init__.py':
            return False
        
        parent_dir = file_path.parent
        python_files = [
            f for f in parent_dir.glob('*.py')
            if f.name != '__init__.py' and not f.name.startswith('.')
        ]
        
        return len(python_files) == 0
    
    def _has_debug_prints(self, file_path: Path) -> List[int]:
        """Detect debug print statements and return line numbers."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            debug_lines = []
            
            for i, line in enumerate(lines, 1):
                # Skip docstrings and comments
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                
                # Detect print statements (simple heuristic)
                if self.DEBUG_PRINT_PATTERN.search(line):
                    # Exclude logging-style prints
                    if 'logger' not in line.lower() and 'log(' not in line.lower():
                        debug_lines.append(i)
            
            return debug_lines
        except Exception:
            return []
    
    def _has_commented_code(self, file_path: Path) -> Tuple[bool, int]:
        """
        Detect large blocks of commented-out code.
        
        Returns:
            (has_commented_code, num_lines)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            matches = self.COMMENTED_CODE_PATTERN.findall(content)
            
            # If more than 5 lines of commented code patterns, flag it
            if len(matches) > 5:
                return True, len(matches)
            
            return False, 0
        except Exception:
            return False, 0
    
    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for hygiene violations."""
        # Skip common ignore directories
        ignore_dirs = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 
                      '.pytest_cache', '.mypy_cache', 'archives', '.sovereign_healing_backup'}
        
        for item in directory.rglob('*'):
            # Skip ignored directories
            if any(ignored in item.parts for ignored in ignore_dirs):
                continue
            
            if not item.is_file():
                continue
            
            # Check for backup files
            if item.suffix in self.BACKUP_EXTENSIONS:
                self.violations.append(HygieneViolation(
                    file_path=item,
                    violation_type='stale_backup',
                    message=f'Stale backup file: {item.suffix}',
                    severity=3,
                    auto_fixable=True
                ))
            
            # Check for temp files
            if item.suffix in self.TEMP_EXTENSIONS or item.name.endswith('~'):
                self.violations.append(HygieneViolation(
                    file_path=item,
                    violation_type='temp_file',
                    message='Temporary file should be removed',
                    severity=4,
                    auto_fixable=True
                ))
            
            # Python file checks
            if item.suffix in self.PYTHON_EXTENSIONS:
                # Empty file check
                if self._is_empty_file(item):
                    self.violations.append(HygieneViolation(
                        file_path=item,
                        violation_type='empty_file',
                        message='Empty Python file',
                        severity=5,
                        auto_fixable=True
                    ))
                
                # Orphaned __init__.py check
                if self._is_orphaned_init(item):
                    self.violations.append(HygieneViolation(
                        file_path=item,
                        violation_type='orphaned_init',
                        message='Orphaned __init__.py with no other Python files',
                        severity=4,
                        auto_fixable=True
                    ))
                
                # Debug print check
                debug_lines = self._has_debug_prints(item)
                if debug_lines:
                    self.violations.append(HygieneViolation(
                        file_path=item,
                        violation_type='debug_print',
                        message=f'Debug print statements found on lines: {debug_lines[:5]}',
                        line_number=debug_lines[0],
                        severity=2,
                        auto_fixable=False
                    ))
                
                # Commented code check
                has_commented, num_lines = self._has_commented_code(item)
                if has_commented:
                    self.violations.append(HygieneViolation(
                        file_path=item,
                        violation_type='commented_code',
                        message=f'Large block of commented-out code ({num_lines} lines)',
                        severity=2,
                        auto_fixable=False
                    ))
    
    def _fix_violations(self) -> int:
        """
        Attempt to auto-fix violations where possible.
        
        Returns:
            Number of violations fixed
        """
        fixed_count = 0
        
        for violation in self.violations:
            if not violation.auto_fixable or self.dry_run:
                continue
            
            try:
                if violation.violation_type in ['stale_backup', 'temp_file', 'empty_file', 'orphaned_init']:
                    # Delete the file
                    violation.file_path.unlink()
                    print(f'   [FIXED] Deleted {violation.violation_type}: {violation.file_path}')
                    fixed_count += 1
            except Exception as e:
                print(f'   [ERROR] Failed to fix {violation.file_path}: {e}')
        
        return fixed_count
    
    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """
        Autonomous healing method for repository hygiene.
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute fixes (overrides dry_run)
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with healing results
        """
        self.dry_run = dry_run and not execute
        self.violations = []
        
        print(f'\n[*] HYGIENE GUARDIAN - Scanning {self.project_root}')
        print(f'    Mode: {"DRY RUN" if self.dry_run else "EXECUTE"}')
        
        # Scan for violations
        self._scan_directory(self.project_root)
        
        # Report violations
        if self.violations:
            print(f'\n   [!] Found {len(self.violations)} hygiene violations:')
            
            # Group by type
            by_type: Dict[str, List[HygieneViolation]] = {}
            for v in self.violations:
                by_type.setdefault(v.violation_type, []).append(v)
            
            for vtype, viols in sorted(by_type.items()):
                print(f'\n   [{vtype.upper()}] {len(viols)} violations:')
                for v in viols[:5]:  # Show first 5
                    rel_path = v.file_path.relative_to(self.project_root)
                    print(f'      - {rel_path}: {v.message}')
                if len(viols) > 5:
                    print(f'      ... and {len(viols) - 5} more')
        else:
            print('   [OK] No hygiene violations detected')
        
        # Fix violations if not dry run
        fixed_count = 0
        if not self.dry_run:
            fixed_count = self._fix_violations()
            print(f'\n   [FIXED] {fixed_count} violations auto-fixed')
        
        return {
            'total_violations': len(self.violations),
            'violations_by_type': {k: len(v) for k, v in by_type.items()} if self.violations else {},
            'fixed_count': fixed_count,
            'dry_run': self.dry_run,
        }
    
    async def execute(self) -> Dict[str, Any]:
        """Execute hygiene checks (async wrapper)."""
        return self.heal_repository(dry_run=self.dry_run)
