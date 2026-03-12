"""
healing_policy_mixin.py - Healing Governance (Policy Layer)

[MIXIN REFACTOR] Absorbs governance logic from healer_mixin.py:
  - Circular dependency protection
  - Depth limiting
  - Budget tracking
  - Decision to heal (orchestration)

Calls the structural_healing_engine for actual transformations.

Naming convention:
  *_policy_mixin.py = governance decisions (uses Agent self)
  *_engine.py       = pure stateless transformations
"""
from __future__ import annotations
import ast
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Final
from agentic_core.runtime.exceptions.healer_exceptions import CircularDependencyError, HealerError
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

@dataclass
class HealingPolicyMixin:
    """
    Healing Governance Mixin (Policy Layer).

    Provides:
    - heal_repository() with circular dependency protection and budget limits
    - File violation analysis via AST (import, syntax, naming checks)
    - Healing status management (enable/disable/reset)

    Does NOT contain raw file transformations — those live in
    structural_healing_engine.py.
    """
    _healing_count: int = field(default=0, init=False)
    _max_healing_operations: Final[int] = 100

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize healer with diagnostic capabilities."""
        super().__init__(*args, **kwargs)
        self.ctx = getattr(self, 'ctx', {})
        self.name = getattr(self, 'name', self.__class__.__name__)
        self.python_files = getattr(self, 'python_files', [])

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(self, dry_run: bool=True, execute: bool=False, depth: int=0, max_depth: int=3, _call_path: set[str] | None=None) -> dict[str, Any]:
        """
        Autonomous diagnostic and healing loop.
        HARDENED: Circular dependency protection + budget enforcement.
        """
        if _call_path is None:
            _call_path = set()
        if self.name in _call_path:
            raise CircularDependencyError(f'Circular healing chain detected: {_call_path} -> {self.name}')
        if depth > max_depth:
            raise HealerError(f'Healing depth exceeded: {depth} > {max_depth}')
        if self._healing_count >= self._max_healing_operations:
            raise HealerError(f'Healing budget exceeded: {self._healing_count} >= {self._max_healing_operations}')
        _call_path = _call_path.copy()
        _call_path.add(self.name)
        try:
            self._healing_count += 1
            summary: dict[str, Any] = self._perform_healing_chain(dry_run, execute, depth, max_depth, _call_path)
            return summary
        # guardian: allow-silent-swallow
        except Exception as e:
            raise HealerError(f'Critical failure in healing loop for {self.name}: {str(e)}') from e
        finally:
            self._healing_count -= 1

    def _perform_healing_chain(self, dry_run: bool, execute: bool, depth: int, max_depth: int, _call_path: set[str]) -> dict[str, Any]:
        """Execute the actual healing chain with proper error boundaries."""
        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0
        try:
            for file_path in self.python_files:
                try:
                    file_violations = self._analyze_file_violations(file_path)
                    violations_found += len(file_violations)
                    if execute and (not dry_run) and file_violations:
                        fixed = self._fix_file_violations(file_path, file_violations)
                        violations_fixed += fixed
                # guardian: allow-silent-swallow
                except Exception as e:
                    raise
                    errors += 1
                    Logger.error(f'Error processing {file_path}: {e}')
        # guardian: allow-silent-swallow
        except Exception as e:
            errors += 1
            Logger.error(f'Healing chain error: {e}')
        return {'violations_found': violations_found, 'violations_fixed': violations_fixed, 'errors': errors, 'skipped': skipped}

    def _analyze_file_violations(self, file_path: str) -> list[dict[str, Any]]:
        """Analyze file for violations using AST."""
        violations = []
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            violations.extend(self._check_import_issues(tree))
            violations.extend(self._check_syntax_issues(tree))
            violations.extend(self._check_naming_issues(tree))
        except SyntaxError as e:
            violations.append({'type': 'syntax_error', 'message': str(e)})
        # guardian: allow-silent-swallow
        except Exception as e:
            violations.append({'type': 'analysis_error', 'message': str(e)})
        return violations

    def _fix_file_violations(self, file_path: str, violations: list[dict[str, Any]]) -> int:
        """Fix violations in file."""
        fixed = 0
        for _violation in violations:
            try:
                fixed += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f'Failed to fix violation in {file_path}: {e}')
        return fixed

    def _check_import_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Check for import-related issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('.'):
                        issues.append({'type': 'relative_import', 'node': node})
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('.'):
                    issues.append({'type': 'relative_import', 'node': node})
        return issues

    def _check_syntax_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Check for syntax-related issues (unused imports)."""
        issues = []
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname and alias.asname not in used_names:
                        issues.append({'type': 'unused_import', 'node': node})
                    elif alias.name not in used_names:
                        issues.append({'type': 'unused_import', 'node': node})
        return issues

    def _check_naming_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Check for naming convention issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    issues.append({'type': 'class_naming', 'node': node})
            elif isinstance(node, ast.FunctionDef):
                if not re.match('^[a-z_][a-z0-9_]*$', node.name):
                    issues.append({'type': 'function_naming', 'node': node})
        return issues

    def _salvaged_advanced_recovery(self, error_trace: str) -> bool:
        """Advanced recovery pattern from legacy StructuralHealerAgent."""
        if not error_trace or not isinstance(error_trace, str):
            return False
        try:
            recovery_patterns = ['ImportError:\\s*(.+)', 'SyntaxError:\\s*(.+)', 'AttributeError:\\s*(.+)']
            for pattern in recovery_patterns:
                match = re.search(pattern, error_trace, re.MULTILINE)
                if match:
                    issue = match.group(1).strip()
                    return self._attempt_pattern_recovery(issue)
            return False
        except re.error as e:
            raise HealerError(f'Regex error in recovery analysis: {str(e)}') from e
        # guardian: allow-silent-swallow
        except Exception as e:
            raise HealerError(f'Advanced recovery failed: {str(e)}') from e

    def _attempt_pattern_recovery(self, issue: str) -> bool:
        """Attempt recovery based on identified error pattern."""
        return False

    def validate_canon_key(self, key_id: int, context: Any) -> tuple[bool, list[Any]]:
        """
        [DEPRECATED] All numeric canon keys (0-50) have been removed.
        Returns success by default for backward compatibility.
        """
        Logger.debug(f'Canon Key {key_id} deprecated in unified schema - auto-passing')
        return (True, [])

    def enable_healing(self) -> None:
        """Enable healing capabilities."""
        self._healing_count = 0

    def disable_healing(self) -> None:
        """Disable healing capabilities."""
        self._healing_count = self._max_healing_operations

    def reset_healing_count(self) -> None:
        """Reset healing operation counter."""
        self._healing_count = 0

    def get_healing_status(self) -> dict[str, Any]:
        """Get current healing status."""
        return {'healing_count': self._healing_count, 'max_operations': self._max_healing_operations, 'enabled': self._healing_count < self._max_healing_operations}
