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

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper
from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HygieneViolation:
    """Structured violation for hygiene issues."""
    file_path: Path
    violation_type: str
    message: str
    line_number: int | None = None
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
    - Repeated filename strings (e.g., 'enums_enums_enums') [Merged from FileCleanupAgent]
    - Copy-pattern filenames (e.g., 'Copy of file.py', 'file (1).py')

    Uses ArchivalGatekeeper for all destructive operations (safe deletion).

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

    # Patterns for copy/duplicate filename detection (merged from FileCleanupAgent)
    COPY_PATTERNS = [
        re.compile(r'^Copy of (.+)$', re.IGNORECASE),  # "Copy of file.py"
        re.compile(r'^(.+) \(\d+\)$'),                  # "file (1).py", "file (2).py"
        re.compile(r'^(.+)_copy\d*$', re.IGNORECASE),   # "file_copy.py", "file_copy2.py"
    ]

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
        self.violations: list[HygieneViolation] = []
        self.agent_name = self.__class__.__name__

        # Initialize ArchivalGatekeeper for safe file operations
        self.gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)

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

    def _has_debug_prints(self, file_path: Path) -> list[int]:
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

    def _has_commented_code(self, file_path: Path) -> tuple[bool, int]:
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

    def _has_repeated_filename_parts(self, filename: str) -> tuple[bool, str | None]:
        """
        Check if filename has repeated consecutive strings (merged from FileCleanupAgent).

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (has_repeats, repeated_pattern) or (False, None)

        Examples:
            'enums_enums' -> (True, 'enums')
            'impl_impl_impl' -> (True, 'impl')
            'data_models_enums_enums' -> (True, 'enums')
            'test_data' -> (False, None)
        """
        parts = filename.split('_')

        # Check for consecutive repeated parts
        for i in range(len(parts) - 1):
            if parts[i] == parts[i + 1] and parts[i]:
                return True, parts[i]

        # Check for any repeated substrings (more than once)
        part_counts = Counter(parts)
        for part, count in part_counts.items():
            if count > 1 and part and len(part) > 2:  # Ignore short parts like 'a', 'to'
                return True, part

        return False, None

    def _is_copy_pattern_filename(self, filename: str) -> tuple[bool, str | None]:
        """
        Check if filename matches copy patterns.

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (is_copy, original_name) or (False, None)

        Examples:
            'Copy of report' -> (True, 'report')
            'report (1)' -> (True, 'report')
            'report_copy2' -> (True, 'report')
        """
        for pattern in self.COPY_PATTERNS:
            match = pattern.match(filename)
            if match:
                return True, match.group(1)

        return False, None

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

                # Repeated filename strings check (merged from FileCleanupAgent)
                has_repeats, pattern = self._has_repeated_filename_parts(item.stem)
                if has_repeats:
                    self.violations.append(HygieneViolation(
                        file_path=item,
                        violation_type='repeated_filename',
                        message=f'Repeated string in filename: "{pattern}"',
                        severity=4,
                        auto_fixable=True
                    ))

                # Copy-pattern filename check
                is_copy, original = self._is_copy_pattern_filename(item.stem)
                if is_copy:
                    self.violations.append(HygieneViolation(
                        file_path=item,
                        violation_type='copy_pattern',
                        message=f'Copy-pattern filename detected (original: "{original}")',
                        severity=5,
                        auto_fixable=True
                    ))

    def _fix_violations(self) -> int:
        """
        Attempt to auto-fix violations where possible.

        Uses ArchivalGatekeeper for all destructive operations (safe deletion).

        Returns:
            Number of violations fixed
        """
        fixed_count = 0

        # Violation types that can be safely archived
        archivable_types = {
            'stale_backup', 'temp_file', 'empty_file', 'orphaned_init',
            'repeated_filename', 'copy_pattern'
        }

        for violation in self.violations:
            if not violation.auto_fixable or self.dry_run:
                continue

            try:
                if violation.violation_type in archivable_types:
                    # Use ArchivalGatekeeper for safe deletion (soft delete to archive)
                    result = self.gatekeeper.safe_delete(
                        violation.file_path,
                        self.agent_name,
                        f'{violation.violation_type}: {violation.message}'
                    )

                    if result.success:
                        print(f'   [FIXED] Archived {violation.violation_type}: {violation.file_path}')
                        fixed_count += 1
                    else:
                        print(f'   [ERROR] Failed to archive {violation.file_path}: {result.error}')
            except Exception as e:
                print(f'   [ERROR] Failed to fix {violation.file_path}: {e}')

        return fixed_count

    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
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

        # Group violations by type
        by_type: dict[str, list[HygieneViolation]] = {}
        for v in self.violations:
            by_type.setdefault(v.violation_type, []).append(v)

        # Report violations
        if self.violations:
            print(f'\n   [!] Found {len(self.violations)} hygiene violations:')

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

        # Return using canonical keys that @standard_heal decorator recognizes
        # See LEGACY_KEY_MAPPINGS in decorators.py for mappings
        return {
            'violations_found': len(self.violations),  # Canonical key
            'violations_fixed': fixed_count,           # Canonical key (was 'fixed_count')
            'violations_by_type': {k: len(v) for k, v in by_type.items()},
            'dry_run': self.dry_run,
        }

    async def execute(self) -> dict[str, Any]:
        """Execute hygiene checks (async wrapper)."""
        return self.heal_repository(dry_run=self.dry_run)
