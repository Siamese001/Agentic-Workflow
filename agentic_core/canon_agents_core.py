"""
Canon Validator Core Agents
SystemArchitect, HealerAgent, GenerativeGuard - Critical infrastructure agents.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent
from apps_shared.canon_utils import EXCLUDED_DIRS, is_excluded


class SystemArchitect(SubAtomicAgent):
    """
    KEYS: 40 (Metaclasses), 41 (Deep Nesting), 49 (Directory Depth), 50 (Integrity)
    ROLE: The Gatekeeper. If this fails, the system is unstable.
    """

    async def execute(self):
        """
        Executes the SystemArchitect's checks for core architectural integrity.
        Reports on metaclass usage, nesting depth, directory depth, and root-level file content.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...")

        # Key 40: No Metaclasses
        passed_40, details_40 = self.check_key_40_no_metaclasses()
        self.ctx.report(self.name, 40, passed_40, details_40)

        # Key 41: Scoped Nesting
        passed_41, details_41 = self.check_key_41_scoped_nesting()
        if not passed_41 and self.ctx.intelligence_enabled:
            # Extract unique file paths from details for smart fixing
            unique_fps_to_fix = list(
                {v.split(":")[0] for v in details_41}
            )
            # Limit fixes to the first 3 files to avoid excessive calls
            for fp in unique_fps_to_fix[:3]:
                await self.smart_fix(fp, 41)
            # Re-check after attempted fixes
            passed_41, details_41 = self.check_key_41_scoped_nesting()
        self.ctx.report(self.name, 41, passed_41, details_41)

        # Key 49: Directory Depth
        passed_49, details_49 = self.check_key_49_directory_depth()
        self.ctx.report(self.name, 49, passed_49, details_49)
        if not passed_49:
            # Signal critical failure after reporting
            self.ctx.signal_critical_failure()
        
        # Key 50: Law of Void
        passed_50, details_50 = self.check_key_50_law_of_void()
        self.ctx.report(self.name, 50, passed_50, details_50)

    def check_key_40_no_metaclasses(self) -> Tuple[bool, List[str]]:
        """
        Checks for metaclass usage in Python files.

        Returns:
            A tuple containing:
            - bool: True if no metaclass violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path and line number
                          where a metaclass was found.
        """
        metaclass_violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    # Add filename for better error messages from ast.parse
                    tree = ast.parse(f.read(), filename=file_path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check for 'metaclass=...' in class definition keywords
                        if any(kw.arg == "metaclass" for kw in node.keywords):
                            metaclass_violations.append(f"{file_path}:{node.lineno}")
            except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as e:
                # Log a warning for files that cannot be parsed, but continue processing others.
                print(
                    f"Warning: Could not parse {file_path} for metaclass check: {e}",
                    file=sys.stderr
                )
                continue
        
        return len(metaclass_violations) == 0, metaclass_violations

    def check_key_41_scoped_nesting(self) -> Tuple[bool, List[str]]:
        """
        Checks for excessive nesting depth within functions and classes,
        considering a maximum depth from environment variable.

        Returns:
            A tuple containing:
            - bool: True if no nesting depth violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path, line number,
                          scope, and depth where a violation occurred.
        """
        MAX_NESTING_DEPTH = int(os.getenv('MAX_NESTING_DEPTH', '4'))
        violations = []
        NESTERS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)

        class NestVisitor(ast.NodeVisitor):
            """AST visitor to check nesting depth within a file."""
            def __init__(self, fp: str):
                self.fp = fp
                self.depth = 0
                self.scope_stack: List[str] = ["global"]  # Use a stack for managing scopes
                self.violations_in_file: List[str] = []  # Collect violations specific to this file

            @property
            def current_scope(self) -> str:
                """Returns the current scope name."""
                return self.scope_stack[-1]

            def visit_FunctionDef(self, node: ast.FunctionDef):
                """Visits a function definition, pushing its name onto the scope stack."""
                self.scope_stack.append(f"func {node.name}")
                self.generic_visit(node)
                self.scope_stack.pop()
            
            def visit_ClassDef(self, node: ast.ClassDef):
                """Visits a class definition, pushing its name onto the scope stack."""
                self.scope_stack.append(f"class {node.name}")
                self.generic_visit(node)
                self.scope_stack.pop()
            
            def visit(self, node: ast.AST):
                """
                Generic visit method to track nesting depth for specific AST nodes.
                Reports violations if depth exceeds MAX_NESTING_DEPTH.
                """
                is_nest = isinstance(node, NESTERS)
                if is_nest:
                    self.depth += 1
                    if self.depth > MAX_NESTING_DEPTH:
                        self.violations_in_file.append(
                            f"{self.fp}:{node.lineno} {self.current_scope} depth {self.depth}"
                        )
                super().visit(node)  # Continue traversal
                if is_nest:
                    self.depth -= 1

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                visitor = NestVisitor(fp)
                visitor.visit(tree)
                violations.extend(visitor.violations_in_file)  # Collect violations from each file
            except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as e:
                print(
                    f"Warning: Could not parse {fp} for nesting check: {e}",
                    file=sys.stderr
                )
                continue
        return len(violations) == 0, violations

    def check_key_49_directory_depth(self) -> Tuple[bool, List[str]]:
        """
        Checks the directory depth of Python files within the project.
        Files deeper than 5 are considered violations, while files at depth 1
        (directly in the project root) are considered warnings.

        Assumes `self.ctx.python_files` provides paths relative to the project root
        or that `Path(file_path).parts` provides the intended logical depth.

        Returns:
            A tuple containing:
            - bool: True if no critical directory depth violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path and its depth
                          for both violations and warnings.
        """
        violations = []
        warnings = []
        for file_path in self.ctx.python_files:
            # Path.parts includes all components. If file_path is relative to project root,
            # this gives the logical depth within the project.
            # E.g., "src/module/file.py" -> ('src', 'module', 'file.py'), depth 3.
            depth = len(Path(file_path).parts)
            
            if depth > 5:
                violations.append(f"{file_path} (Invalid depth: {depth})")
            elif depth == 1:  # A file directly in the assumed project root, e.g., `main.py`
                warnings.append(f"{file_path} (Depth 1 — move to package recommended)")
        return len(violations) == 0, violations + warnings

    def check_key_50_law_of_void(self) -> Tuple[bool, List[str]]:
        """
        Checks for Python files directly in the project root (depth 1) that contain
        class or function definitions. Such files should ideally be minimal or
        serve as entry points without complex logic, adhering to the "Law of Void".

        Assumes `self.ctx.python_files` provides paths relative to the project root.

        Returns:
            A tuple containing:
            - bool: True if no root-level files contain class/function definitions, False otherwise.
            - List[str]: A list of file paths that violate the "Law of Void".
        """
        root_violations = []
        for file_path in self.ctx.python_files:
            # Check if the file is directly in the assumed project root
            if len(Path(file_path).parts) == 1:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Add filename for better error messages from ast.parse
                        ast_tree = ast.parse(content, filename=file_path)
                        for node in ast_tree.body:
                            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                root_violations.append(file_path)
                                break  # Only need to find one such definition to flag it
                except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as e:
                    print(
                        f"Warning: Could not parse {file_path} for Law of Void check: {e}",
                        file=sys.stderr
                    )
                    # Consider unparseable files as violations for this key
                    root_violations.append(file_path)
        return len(root_violations) == 0, root_violations


class HealerAgent(SubAtomicAgent):
    """
    KEYS: 48 (Syntax Repair), 49 (Structural Alignment)
    ROLE: The Ultimate Repair Agent. Uses Gemini 3 Flash with thinking_level=HIGH.
    """
    MAX_HEALING_ROUNDS = int(os.getenv('MAX_HEALING_ROUNDS', '3'))

    async def execute(self):
        """
        Executes the HealerAgent's repair process, attempting to fix syntax errors
        in Python files over multiple rounds.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Investigating Failures...")
        
        round_num = 0
        # Flag to track if any file was successfully fixed in the current round.
        # Initialize to True to ensure the loop runs at least once.
        any_file_healed_in_current_round = True 

        while any_file_healed_in_current_round and round_num < self.MAX_HEALING_ROUNDS:
            round_num += 1
            syntax_errors_found_this_round = []
            
            # Re-scan all python files for syntax errors in each round
            for file_path in self.ctx.python_files:
                if not is_excluded(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            # Add filename for better error messages from ast.parse
                            ast.parse(f.read(), filename=file_path)
                    except SyntaxError as e:
                        syntax_errors_found_this_round.append((file_path, e))
                    except (FileNotFoundError, UnicodeDecodeError) as e:
                        # Log warnings for files that cannot be read or decoded
                        print(
                            f"Warning: Could not read or decode {file_path} for healing: {e}",
                            file=sys.stderr
                        )
                        # These are not SyntaxErrors, so they won't trigger smart_fix directly,
                        # but might be reported as remaining issues later.

            if not syntax_errors_found_this_round:
                any_file_healed_in_current_round = False  # No errors found, stop healing attempts
                break

            print(f"   🚨 Round {round_num}: Found {len(syntax_errors_found_this_round)} Syntax Blockers. Healing...")
            
            # Reset flag for the current round
            any_file_healed_in_current_round = False 
            for file_path, error in syntax_errors_found_this_round:
                print(f"      🔍 Fixing {file_path}:{error.lineno} – {error.msg}")
                success = await self.smart_fix(file_path, 48)
                if success:
                    any_file_healed_in_current_round = True  # At least one file was fixed

        # After all healing rounds, perform a final check for any remaining syntax errors
        remaining_syntax_errors = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                remaining_syntax_errors.append(file_path)
            except (FileNotFoundError, UnicodeDecodeError) as e:
                print(
                    f"Warning: Could not read or decode {file_path} for final check: {e}",
                    file=sys.stderr
                )
                # Treat unreadable files as failures for the purpose of this report
                remaining_syntax_errors.append(file_path)

        if not remaining_syntax_errors:
            print("   ✅ Architecture verified. Core integrity intact.")
            self.ctx.report(self.name, 48, True, [])
            self.ctx.signal_ast_valid()
        else:
            print(f"   ❌ Critical Failure: {len(remaining_syntax_errors)} files still have syntax errors.")
            self.ctx.report(self.name, 48, False, remaining_syntax_errors)
            self.ctx.signal_critical_failure()


class GenerativeGuard(SubAtomicAgent):
    """
    KEYS: 45 (Dead Code/Runaway Generation)
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.
    """

    # Patterns to identify potentially runaway generated files
    GENERATIVE_PATTERNS = [
        r"\_impl\_impl\_",  # e.g., `my_module_impl_impl_v1.py`
        r"\_v\d+\_v\d+",    # e.g., `my_file_v1_v2.py`
        r"\_copy\_\d+",     # e.g., `my_file_copy_1.py`
    ]

    def execute(self):
        """
        Executes the GenerativeGuard's check for runaway generated files.
        Identifies files matching predefined patterns and optionally purges them.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Generative Policy...")
        violations = []

        # Use self.ctx.project_root if available, otherwise assume current directory
        project_root = getattr(self.ctx, 'project_root', '.') 
        
        for root, dirs, files in os.walk(project_root):
            # Modify dirs in-place to exclude specified directories from traversal
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                file_path = os.path.join(root, file)
                # Normalize path to use forward slashes for consistent pattern matching across OS
                normalized_file_path = Path(file_path).as_posix() 
                
                for pattern in self.GENERATIVE_PATTERNS:
                    if re.search(pattern, normalized_file_path):
                        violations.append(file_path)  # Store original path for reporting/deletion
                        break  # Found a pattern, no need to check other patterns for this file

        if violations:
            print(f"   🛑 RUNAWAY GENERATION DETECTED ({len(violations)} files).")
            self.ctx.report(self.name, 45, False, violations)

            # Check for --purge-runaway argument in sys.argv
            purge_runaway = "--purge-runaway" in sys.argv
            if not purge_runaway:
                self.ctx.signals.add("GENERATIVE_FAIL")
                print("      Hint: Run with '--purge-runaway' to delete these files.")
            else:
                print("      🗑️  Purging runaway generated files...")
                for file_path in violations:
                    try:
                        os.remove(file_path)
                        print(f"         DELETED: {file_path}")
                    except OSError as e:  # Catch specific OS errors for file operations
                        print(f"         ❌ Failed to delete {file_path}: {e}", file=sys.stderr)
                self.ctx.signals.add("GENERATIVE_CLEAN")  # Signal clean even if some failed to delete
        else:
            print("   ✅ No runaway generation detected.")
            self.ctx.report(self.name, 45, True, [])
            self.ctx.signals.add("GENERATIVE_CLEAN")
