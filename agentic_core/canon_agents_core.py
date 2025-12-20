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
from config.canon_validator_config import EXCLUDED_DIRS, is_excluded


class SystemArchitect(SubAtomicAgent):
    """
    KEYS: 40 (Metaclasses), 41 (Deep Nesting), 50 (Integrity)
    ROLE: The Gatekeeper. If this fails, the system is unstable.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...")

        passed, details = self.check_key_40_no_metaclasses()
        self.ctx.report(self.name, 40, passed, details)

        passed, details = self.check_key_41_scoped_nesting()
        if not passed and self.ctx.intelligence_enabled:
            details_list = list(details) if isinstance(details, (set, tuple)) else details
            for fp in list(set(v.split(":")[0] for v in details_list))[:3]:
                await self.smart_fix(fp, 41)
            passed, details = self.check_key_41_scoped_nesting()
        self.ctx.report(self.name, 41, passed, details)

        passed, details = self.check_key_49_directory_depth()
        self.ctx.report(self.name, 49, passed, details)
        if not passed:
            self.ctx.signal_critical_failure()
        
        passed, details = self.check_key_50_law_of_void()
        self.ctx.report(self.name, 50, passed, details)

    def check_key_40_no_metaclasses(self) -> Tuple[bool, List[str]]:
        """Check for metaclass usage."""
        metaclass_violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if any(kw.arg == "metaclass" for kw in node.keywords):
                            metaclass_violations.append(f"{file_path}:{node.lineno}")
            except:
                continue
        
        return (len(metaclass_violations) == 0, metaclass_violations)

    def check_key_41_scoped_nesting(self) -> Tuple[bool, List[str]]:
        """Max nesting depth from environment with scope awareness."""
        max_depth = int(os.getenv('MAX_NESTING_DEPTH', '4'))
        violations = []
        NESTERS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)

        class NestVisitor(ast.NodeVisitor):
            def __init__(self, fp):
                self.fp = fp
                self.depth = 0
                self.scope = "global"
            
            def visit_FunctionDef(self, node):
                old, self.scope = self.scope, f"func {node.name}"
                self.generic_visit(node)
                self.scope = old
            
            def visit_ClassDef(self, node):
                old, self.scope = self.scope, f"class {node.name}"
                self.generic_visit(node)
                self.scope = old
            
            def visit(self, node):
                is_nest = isinstance(node, NESTERS)
                if is_nest:
                    self.depth += 1
                    if self.depth > max_depth:
                        violations.append(f"{self.fp}:{node.lineno} {self.scope} depth {self.depth}")
                super().visit(node)
                if is_nest:
                    self.depth -= 1

        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                NestVisitor(fp).visit(tree)
            except:
                continue
        return len(violations) == 0, violations

    def check_key_49_directory_depth(self) -> Tuple[bool, List[str]]:
        violations = []
        warnings = []
        for file_path in self.ctx.python_files:
            parts = Path(file_path).parts
            depth = len(parts)
            if depth > 5:
                violations.append(f"{file_path} (Invalid depth: {depth})")
            elif depth == 1:
                warnings.append(f"{file_path} (Depth 1 — move to package recommended)")
        return len(violations) == 0, violations + warnings

    def check_key_50_law_of_void(self) -> Tuple[bool, List[str]]:
        root_violations = []
        for file_path in self.ctx.python_files:
            parts = Path(file_path).parts
            if len(parts) == 1:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        ast_tree = ast.parse(content)
                        for node in ast_tree.body:
                            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                root_violations.append(file_path)
                                break
                except:
                    root_violations.append(file_path)
        return len(root_violations) == 0, root_violations


class HealerAgent(SubAtomicAgent):
    """
    KEYS: 48 (Syntax Repair), 49 (Structural Alignment)
    ROLE: The Ultimate Repair Agent. Uses Gemini 3 Flash with thinking_level=HIGH.
    """
    MAX_HEALING_ROUNDS = int(os.getenv('MAX_HEALING_ROUNDS', '3'))

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Investigating Failures...")
        healed_this_round = True
        round_num = 0

        while healed_this_round and round_num < self.MAX_HEALING_ROUNDS:
            round_num += 1
            syntax_errors = []
            for file_path in self.ctx.python_files:
                if not is_excluded(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            ast.parse(f.read())
                    except SyntaxError as e:
                        syntax_errors.append((file_path, e))

            if not syntax_errors:
                healed_this_round = False
                break

            print(f"   🚨 Round {round_num}: Found {len(syntax_errors)} Syntax Blockers. Healing...")
            for file_path, error in syntax_errors:
                print(f"      🔍 Fixing {file_path}:{error.lineno} – {error.msg}")
                success = await self.smart_fix(file_path, 48)
                if not success:
                    healed_this_round = False

        remaining = []
        for file_path in self.ctx.python_files:
            try:
                ast.parse(open(file_path, "r", encoding="utf-8").read())
            except SyntaxError:
                remaining.append(file_path)

        if not remaining:
            print("   ✅ Architecture verified. Core integrity intact.")
            self.ctx.report(self.name, 48, True, [])
            self.ctx.signal_ast_valid()
        else:
            self.ctx.report(self.name, 48, False, remaining)
            self.ctx.signal_critical_failure()


class GenerativeGuard(SubAtomicAgent):
    """
    KEYS: 45 (Dead Code/Runaway Generation)
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.
    """

    GENERATIVE_PATTERNS = [
        r"\_impl\_impl\_",
        r"\_v\d+\_v\d+",
        r"\_copy\_\d+",
    ]

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Generative Policy...")
        violations = []

        all_files = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)

        for file_path in all_files:
            for pattern in self.GENERATIVE_PATTERNS:
                if re.search(pattern, file_path):
                    violations.append(file_path)
                    break

        if violations:
            print(f"   🛑 RUNAWAY GENERATION DETECTED ({len(violations)} files).")
            self.ctx.report(self.name, 45, False, violations)

            purge_runaway = "--purge-runaway" in sys.argv
            if not purge_runaway:
                self.ctx.signals.add("GENERATIVE_FAIL")
            else:
                for file_path in violations:
                    try:
                        os.remove(file_path)
                        print(f"      🗑️  DELETED: {file_path}")
                    except Exception as e:
                        print(f"      ❌ Failed to delete {file_path}: {e}")
                self.ctx.signals.add("GENERATIVE_CLEAN")
        else:
            self.ctx.report(self.name, 45, True, [])
            self.ctx.signals.add("GENERATIVE_CLEAN")
