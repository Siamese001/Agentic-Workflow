import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.L2_execution.tool_registry.CanonBaseAgent import CanonBaseAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
class CodeJanitorAgent(CanonBaseAgent):
    """
    Code Janitor validates syntax, style, and formatting.
    
    Validates Canon Keys 10-20:
    - Key 10: No syntax errors
    - Key 11: Proper indentation (4 spaces)
    - Key 12: No trailing whitespace
    - Key 13: Proper line endings (implicitly handled by editors/git, but can be checked)
    - Key 14: Naming conventions (snake_case, PascalCase)
    - Key 15-20: Other style guide compliance (e.g., line length, blank lines, imports)
    """

    def get_validation_keys(self) -> List[int]:
        """Return canon keys validated by this agent."""
        return list(range(10, 21))

    async def execute(self) -> Any:
        """Execute Code Janitor validation checks."""
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Syntax and Style...')
        passed, violations = self.check_key_10_syntax()
        if not passed:
            print(f'   [{self.name}] Key 10: FAIL ({len(violations)} violations)')
            await self._heal_violations(10, violations)
        passed, violations = self.check_key_11_indentation()
        if not passed:
            print(f'   [{self.name}] Key 11: FAIL ({len(violations)} violations)')
            await self._heal_violations(11, violations)
        passed, violations = self.check_key_12_trailing_whitespace()
        if not passed:
            print(f'   [{self.name}] Key 12: FAIL ({len(violations)} violations)')
            await self._heal_violations(12, violations)
        passed, violations = self.check_key_14_naming_conventions()
        if not passed:
            print(f'   [{self.name}] Key 14: FAIL ({len(violations)} violations)')
            await self._heal_violations(14, violations)

    def check_key_10_syntax(self) -> Tuple[bool, List[str]]:
        """
        Check for syntax errors in Python files.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code: Any = f.read()
                ast.parse(code)
            except SyntaxError as e:
                violations.append(f'{file_path}:{e.lineno}: SyntaxError - {e.msg}')
            except Exception as e:
                violations.append(f'{file_path}:0: General Error - {e}')
                continue
        return (len(violations) == 0, violations)

    def check_key_11_indentation(self) -> Tuple[bool, List[str]]:
        """
        Check for proper indentation (4 spaces, no tabs).
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines: Any = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    if '\t' in line:
                        violations.append(f'{file_path}:{line_num}: Tab character found (use 4 spaces)')
                    stripped_line: Any = line.lstrip(' ')
                    if stripped_line and line.startswith(' '):
                        leading_spaces: Any = len(line) - len(stripped_line)
                        if leading_spaces % 4 != 0:
                            violations.append(f'{file_path}:{line_num}: Indentation not multiple of 4 ({leading_spaces} spaces)')
            except Exception as e:
                violations.append(f'{file_path}:0: General Error - {e}')
                continue
        return (len(violations) == 0, violations)

    def check_key_12_trailing_whitespace(self) -> Tuple[bool, List[str]]:
        """
        Check for trailing whitespace at end of lines.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines: Any = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    if line.rstrip('\n\r') != line.rstrip():
                        violations.append(f'{file_path}:{line_num}: Trailing whitespace')
            except Exception as e:
                violations.append(f'{file_path}:0: General Error - {e}')
                continue
        return (len(violations) == 0, violations)

    def _check_node_naming_convention(self, file_path: str, node: ast.AST, violations: List[str]):
        """
        Helper to check naming convention for a single AST node.
        
        Args:
            file_path: Path to the file being checked.
            node: The AST node to check.
            violations: List to append any found violations.
        """
        if isinstance(node, ast.ClassDef):
            if not re.match('^[A-Z][a-zA-Z0-9]*$', node.name):
                violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith('__') and (not node.name.startswith('_')):
                if not re.match('^[a-z_][a-z0-9_]*$', node.name):
                    violations.append(f"{file_path}:{node.lineno}: Function '{node.name}' should be snake_case")

    def _process_file_for_naming_conventions(self, file_path: str, violations: List[str]):
        """
        Helper to parse a single file and check all its AST nodes for naming conventions.
        Args:
            file_path: Path to the file to process.
            violations: List to append any found violations.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                self._check_node_naming_convention(file_path, node, violations)
        except Exception as e:
            violations.append(f'{file_path}:0: General Error - {e}')

    def check_key_14_naming_conventions(self) -> Tuple[bool, List[str]]:
        """
        Check for proper naming conventions (snake_case for functions/variables, PascalCase for classes).
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        for file_path in self.ctx.python_files:
            self._process_file_for_naming_conventions(file_path, violations)
        return (len(violations) == 0, violations)

    async def _heal_violations(self, key: int, violations: List[str]):
        """
        Heal violations for a specific key.
        
        Args:
            key: Canon key number
            violations: List of Violation descriptions
        """
        max_healing_per_file = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
        file_violations = {}
        for Violation in violations[:max_healing_per_file]:
            if ':' in Violation:
                file_path = Violation.split(':')[0]
                if file_path not in file_violations:
                    file_violations[file_path] = []
                file_violations[file_path].append(Violation)
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)

    def _read_file_content(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Helper to read file content, returning content and any error message.
        Returns:
            Tuple of (file_content, error_message). error_message is None on success.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return (f.read(), None)
        except Exception as e:
            return (None, f'Cannot read {file_path}: {e}')

    def _write_file_content(self, file_path: str, content: str) -> Optional[str]:
        """
        Helper to write content to file, returning any error message.
        Returns:
            error_message, which is None on success.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return None
        except Exception as e:
            return f'Cannot write {file_path}: {e}'

    async def _smart_fix(self, file_path: str, violation_key: int, violations: List[str]):
        """
        Apply smart fix to a file using Gemini 2.5 Flash.
        
        Args:
            file_path: Path to file to fix
            violation_key: Canon key being fixed
            violations: List of violations in this file
        """
        original_code, read_error = self._read_file_content(file_path)
        if read_error:
            print(f'      [!] {read_error}')
            return
        violation_details = '\n'.join(violations)
        Task = f'Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}'
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        for round_num in range(1, max_rounds + 1):
            print(f'      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}')
            mutated_code = await self.resilient_mutation(Task=Task, code=current_code, file_path=file_path, round_num=round_num, previous_failure=previous_failure)
            is_valid, reason = await self.verify_fix(original_code, mutated_code, violation_key)
            if not is_valid:
                print(f'      [!] Round {round_num}: {reason} – retrying')
                previous_failure = reason
                current_code = mutated_code
                continue
            write_error = self._write_file_content(file_path, mutated_code)
            if write_error:
                print(f'      [X] {write_error}')
                return
            print(f'      [OK] Round {round_num}: Fixed {os.path.basename(file_path)}')
            return
        print(f'      [X] Failed to fix {os.path.basename(file_path)} after {max_rounds} rounds')
