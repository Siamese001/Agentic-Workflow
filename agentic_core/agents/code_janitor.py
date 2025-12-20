"""
Code Janitor Agent - Syntax and Style Validation (Keys 10-20)

Responsible for:
- Key 10: Syntax errors and basic Python validity
- Key 11-15: Whitespace, indentation, formatting
- Key 16-20: Linting, style guide compliance, naming conventions
"""
import os
import ast
import re
from typing import List, Tuple

from .canon_base_agent import CanonBaseAgent


class CodeJanitor(CanonBaseAgent):
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
        return list(range(10, 21))  # Keys 10-20
    
    async def execute(self):
        """Execute Code Janitor validation checks."""
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Syntax and Style...")
        
        # Check Key 10: Syntax errors
        passed, violations = self.check_key_10_syntax()
        if not passed:
            print(f"   [{self.name}] Key 10: FAIL ({len(violations)} violations)")
            await self._heal_violations(10, violations)
        
        # Check Key 11: Indentation
        passed, violations = self.check_key_11_indentation()
        if not passed:
            print(f"   [{self.name}] Key 11: FAIL ({len(violations)} violations)")
            await self._heal_violations(11, violations)
        
        # Check Key 12: Trailing whitespace
        passed, violations = self.check_key_12_trailing_whitespace()
        if not passed:
            print(f"   [{self.name}] Key 12: FAIL ({len(violations)} violations)")
            await self._heal_violations(12, violations)

        # Check Key 14: Naming conventions (Note: Renamed from Key 13 to align with docstring)
        passed, violations = self.check_key_14_naming_conventions()
        if not passed:
            print(f"   [{self.name}] Key 14: FAIL ({len(violations)} violations)")
            await self._heal_violations(14, violations)
        
        # Key 13 (Proper line endings) and Keys 15-20 (other style guide compliance)
        # are not explicitly implemented as separate check methods in this version.
        # They might be covered by broader linting tools or future dedicated checks.
    
    def check_key_10_syntax(self) -> Tuple[bool, List[str]]:
        """
        Check for syntax errors in Python files.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations = []
        
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                ast.parse(code)
            except SyntaxError as e:
                violations.append(f"{file_path}:{e.lineno}: SyntaxError - {e.msg}")
            except Exception as e:
                # Catch other potential errors during file reading or parsing (e.g., UnicodeDecodeError)
                violations.append(f"{file_path}:0: General Error - {e}")
                continue
        
        return len(violations) == 0, violations
    
    def check_key_11_indentation(self) -> Tuple[bool, List[str]]:
        """
        Check for proper indentation (4 spaces, no tabs).
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations = []
        
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Check for tabs
                    if '\t' in line:
                        violations.append(f"{file_path}:{line_num}: Tab character found (use 4 spaces)")
                    
                    # Check for incorrect indentation (not multiple of 4)
                    stripped_line = line.lstrip(' ')
                    if stripped_line and line.startswith(' '):  # If line is not empty and starts with spaces
                        leading_spaces = len(line) - len(stripped_line)
                        if leading_spaces % 4 != 0:
                            violations.append(f"{file_path}:{line_num}: Indentation not multiple of 4 ({leading_spaces} spaces)")
            except Exception as e:
                # Catch potential errors during file reading
                violations.append(f"{file_path}:0: General Error - {e}")
                continue
        
        return len(violations) == 0, violations
    
    def check_key_12_trailing_whitespace(self) -> Tuple[bool, List[str]]:
        """
        Check for trailing whitespace at end of lines.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations = []
        
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Check for trailing whitespace (but not empty lines)
                    # rstrip('\n\r') removes only newlines, rstrip() removes all trailing whitespace
                    if line.rstrip('\n\r') != line.rstrip():
                        violations.append(f"{file_path}:{line_num}: Trailing whitespace")
            except Exception as e:
                # Catch potential errors during file reading
                violations.append(f"{file_path}:0: General Error - {e}")
                continue
        
        return len(violations) == 0, violations
    
    def check_key_14_naming_conventions(self) -> Tuple[bool, List[str]]:
        """
        Check for proper naming conventions (snake_case for functions/variables, PascalCase for classes).
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations = []
        
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    # Check class names (should be PascalCase)
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase")
                    
                    # Check function names (should be snake_case)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Exclude dunder methods (e.g., __init__) and private methods (e.g., _helper)
                        # as their naming conventions are slightly different or context-dependent.
                        if not node.name.startswith('__') and not node.name.startswith('_'):
                            if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                                violations.append(f"{file_path}:{node.lineno}: Function '{node.name}' should be snake_case")
                    
                    # TODO: Add checks for variable names if desired (e.g., local variables, global constants)
            except Exception as e:
                # Catch potential errors during file reading or AST parsing
                violations.append(f"{file_path}:0: General Error - {e}")
                continue
        
        return len(violations) == 0, violations
    
    async def _heal_violations(self, key: int, violations: List[str]):
        """
        Heal violations for a specific key.
        
        Args:
            key: Canon key number
            violations: List of violation descriptions
        """
        max_healing_per_file = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
        
        # Group violations by file
        file_violations = {}
        # Limit the total number of violations processed to avoid overwhelming the LLM
        for violation in violations[:max_healing_per_file]: 
            if ':' in violation:
                file_path = violation.split(':')[0]
                if file_path not in file_violations:
                    file_violations[file_path] = []
                file_violations[file_path].append(violation)
        
        # Heal each file
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)
    
    async def _smart_fix(self, file_path: str, violation_key: int, violations: List[str]):
        """
        Apply smart fix to a file using Gemini 2.5 Flash.
        
        Args:
            file_path: Path to file to fix
            violation_key: Canon key being fixed
            violations: List of violations in this file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f"      ⚠️ Cannot read {file_path}: {e}")
            return
        
        # Build task description
        violation_details = "\n".join(violations)
        task = f"Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}"
        
        # Multi-round healing
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        
        for round_num in range(1, max_rounds + 1):
            print(f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}")
            
            # Get mutated code from Gemini
            mutated_code = await self.resilient_mutation(
                task=task,
                code=current_code,
                file_path=file_path,
                round_num=round_num,
                previous_failure=previous_failure
            )
            
            # Verify the fix
            is_valid, reason = await self.verify_fix(original_code, mutated_code, violation_key)
            
            if not is_valid:
                print(f"      ⚠️ Round {round_num}: {reason} – retrying")
                previous_failure = reason
                current_code = mutated_code
                continue
            
            # Write the fixed code
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(mutated_code)
                print(f"      ✅ Round {round_num}: Fixed {os.path.basename(file_path)}")
                return
            except Exception as e:
                print(f"      ❌ Cannot write {file_path}: {e}")
                return
        
        print(f"      ❌ Failed to fix {os.path.basename(file_path)} after {max_rounds} rounds")
