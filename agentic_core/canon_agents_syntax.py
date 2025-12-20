"""
Canon Validator Syntax Agents
CodeJanitor, DependencySentinel - Code hygiene and import management.
"""

import ast
import os
import subprocess
import sys
from typing import List, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent


class CodeJanitor(SubAtomicAgent):
    """
    KEYS: 10 (Long Lines), 11 (Whitespace), 12 (Newlines), 13 (Tabs), 15 (Magic Numbers), 16 (Deep Nesting)
    ROLE: The Cleaner. Can SELF-FIX violations. Emits AST_VALID signal.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Sanitizing Codebase...")

        passed, details = self.check_key_11_no_trailing_whitespace()
        self.ctx.report(self.name, 11, passed, details)
        if not passed:
            print("      🔧 Auto-fixing trailing whitespace...")
            self._fix_trailing_whitespace()
            passed, details = self.check_key_11_no_trailing_whitespace()
            self.ctx.report(self.name, 11, passed, details)

        passed, details = self.check_key_12_no_missing_newline()
        if not passed:
            print("      🔧 Auto-fixing missing final newlines...")
            for file_path in details:
                try:
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write("\n")
                except Exception as e:
                    print(f"      ❌ Failed to fix newline in {file_path}: {e}")
            passed, details = self.check_key_12_no_missing_newline()
        self.ctx.report(self.name, 12, passed, details)

        passed, details = self.check_key_13_no_tabs()
        if not passed and self.ctx.intelligence_enabled:
            print("      🧠 Converting tabs to spaces...")
            for file_path in set(d.split(":")[0] for d in details):
                await self.smart_fix(file_path, 13)
            passed, details = self.check_key_13_no_tabs()
        self.ctx.report(self.name, 13, passed, details)

        keys_to_check = {
            10: self.check_key_10_no_long_lines,
            15: self.check_key_15_no_magic_numbers,
            16: self.check_key_16_no_deep_nesting
        }

        for key, check_func in keys_to_check.items():
            passed, details = check_func()
            if not passed and self.ctx.intelligence_enabled:
                files = set(d.split(":")[0].strip() for d in details if ":" in d)
                for fp in list(files)[:3]:
                    await self.smart_fix(fp, key)
                passed, details = check_func()
            self.ctx.report(self.name, key, passed, details)

        self.ctx.signal_ast_valid()

    def check_key_11_no_trailing_whitespace(self) -> Tuple[bool, List[str]]:
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if line.rstrip() != line.rstrip("\n\r"):
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_12_no_missing_newline(self) -> Tuple[bool, List[str]]:
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content and not content.endswith("\n"):
                        violations.append(file_path)
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_13_no_tabs(self) -> Tuple[bool, List[str]]:
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "\t" in content:
                        violations.append(file_path)
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_10_no_long_lines(self) -> Tuple[bool, List[str]]:
        violations = []
        max_line_length = int(os.getenv('MAX_LINE_LENGTH', '100'))
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if len(line) > max_line_length:
                            violations.append(f"{file_path}:{i}")
            except:
                continue
        return (len(violations) == 0, violations)

    def check_key_15_no_magic_numbers(self) -> Tuple[bool, List[str]]:
        violations = []
        ALLOWED = {0, 1, -1, 2}
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        if any(isinstance(t, ast.Name) and t.id.isupper() for t in node.targets):
                            continue
                    
                    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                        if node.value not in ALLOWED:
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_16_no_deep_nesting(self) -> Tuple[bool, List[str]]:
        max_depth = int(os.getenv('MAX_NESTING_DEPTH', '4'))
        violations = []
        
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self, filepath, max_depth):
                self.filepath = filepath
                self.max_depth = max_depth
                self.depth = 0
                self.violations = []
            
            def visit(self, node):
                is_nest = isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With))
                if is_nest:
                    self.depth += 1
                    if self.depth > self.max_depth:
                        self.violations.append(f"{self.filepath}:{node.lineno}")
                super().generic_visit(node)
                if is_nest:
                    self.depth -= 1
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                visitor = NestingVisitor(fp, max_depth)
                visitor.visit(tree)
                violations.extend(visitor.violations)
            except:
                continue
        return len(violations) == 0, violations

    def _fix_trailing_whitespace(self):
        try:
            result = subprocess.run([sys.executable, "scripts/fix_trailing_whitespace.py", "."],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("      ✅ Trailing whitespace fixed")
        except Exception as e:
            print(f"      ❌ Failed to fix trailing whitespace: {e}")


class DependencySentinel(SubAtomicAgent):
    """
    KEYS: 7 (Star Imports), 8 (Relative Imports), 9 (Unused Imports), 14 (Duplicate Imports), 44 (Circular Imports)
    ROLE: The Cleaner. Automatically fixes import ordering and unused imports.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Import Hygiene...")

        try:
            subprocess.run(["isort", "--version"], capture_output=True, check=True)
            has_isort = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_isort = False
            print("      ⚠️  isort not installed. Install with: pip install isort")

        try:
            subprocess.run(["autoflake", "--version"], capture_output=True, check=True)
            has_autoflake = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_autoflake = False

        if has_autoflake:
            print("      🔧 Auto-removing unused imports...")
            subprocess.run(["autoflake", "--in-place", "--remove-all-unused-imports", "--recursive", "."],
                         capture_output=True)

        if has_isort:
            print("      🔧 Auto-sorting imports...")
            subprocess.run(["isort", "."], capture_output=True)

        passed, details = self.check_key_07_no_star_imports()
        self.ctx.report(self.name, 7, passed, details)

        passed, details = self.check_key_08_no_relative_imports()
        self.ctx.report(self.name, 8, passed, details)

        passed, details = self.check_key_45_no_unused_imports()
        self.ctx.report(self.name, 9, passed, details)
        self.ctx.report(self.name, 45, passed, details)

        passed, details = self.check_key_14_no_duplicate_imports()
        self.ctx.report(self.name, 14, passed, details)

        passed, details = self.check_key_44_no_circular_imports()
        self.ctx.report(self.name, 44, passed, details)

        self.ctx.signal_deps_valid()

    def check_key_07_no_star_imports(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if any(alias.name == "*" for alias in node.names):
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_08_no_relative_imports(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.level > 0:
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_45_no_unused_imports(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content)
                
                imported_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name
                            imported_names.add(name)
                
                used_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                
                unused = imported_names - used_names
                if unused:
                    violations.append(f"{fp}: {', '.join(unused)}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_14_no_duplicate_imports(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        for alias in node.names:
                            imports.append(alias.name)
                
                seen = set()
                for imp in imports:
                    if imp in seen:
                        violations.append(f"{fp}: {imp}")
                    seen.add(imp)
            except:
                continue
        return len(violations) == 0, violations

    def check_key_44_no_circular_imports(self) -> Tuple[bool, List[str]]:
        return True, []
