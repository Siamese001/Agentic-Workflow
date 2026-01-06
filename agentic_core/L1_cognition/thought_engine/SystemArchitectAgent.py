from __future__ import annotations
"""
SystemArchitectAgent - Core architectural integrity validator.

KEYS: 40 (Metaclasses), 41 (Deep Nesting), 49 (Directory Depth), 50 (Integrity)
ROLE: The Gatekeeper. If this fails, the system is unstable.
Extracted from CanonHealerAgent.py for one-file-per-agent pattern.
"""
import ast
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# [SSOT] Derive depth map from SOVEREIGN_REGISTRY
depth_map = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}

# Excluded directories for file scanning
excluded_dirs = [
    '.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules',
    'dist', 'build', '.vscode', '.idea', '.DS_Store', '.mypy_cache',
    '.pytest_cache', 'htmlcov', 'site-packages', 'docs', 'tests',
    'temp', 'tmp', 'log', 'logs'
]


def is_excluded(file_path: str) -> bool:
    """Checks if a file path or any of its parent directories are in the excluded list."""
    path_parts = Path(file_path).parts
    for part in path_parts:
        if part in excluded_dirs:
            return True
    return False


class NestVisitor(ast.NodeVisitor):
    """
    AST visitor to check nesting depth within a file.
    Moved to module level to reduce nesting depth in SystemArchitectAgent.
    """
    NESTERS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)

    def __init__(self, fp: str, max_nesting_depth: int):
        self.fp = fp
        self.depth = 0
        self.scope_stack: List[str] = ["global"]
        self.violations_in_file: List[str] = []
        self.MAX_NESTING_DEPTH = max_nesting_depth

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
    
    def _check_and_report_nesting(self, node: ast.AST):
        """Helper to check if current depth exceeds max and report violation."""
        if self.depth > self.MAX_NESTING_DEPTH:
            self.violations_in_file.append(
                f"{self.fp}:{node.lineno} {self.current_scope} depth {self.depth}"
            )

    def visit(self, node: ast.AST):
        """
        Generic visit method to track nesting depth for specific AST nodes.
        Reports violations if depth exceeds MAX_NESTING_DEPTH.
        """
        is_nest = isinstance(node, self.NESTERS)
        if not is_nest:
            super().visit(node)
            return

        # If it is a nester:
        self.depth += 1
        self._check_and_report_nesting(node)
        super().visit(node)
        self.depth -= 1


class SystemArchitectAgent(HealerMixin, CanonBaseAgentInterface):
    """
    KEYS: 40 (Metaclasses), 41 (Deep Nesting), 49 (Directory Depth), 50 (Integrity)
    ROLE: The Gatekeeper. If this fails, the system is unstable.
    
    Validates:
    - No metaclass usage (Key 40)
    - Scoped nesting depth ≤4 (Key 41)
    - Directory depth compliance (Key 49)
    - Law of Void - no root-level definitions (Key 50)
    """

    def __init__(self, ctx: Any = None):
        self.impl = None  # CanonBaseAgent is abstract, skip instantiation
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def execute(self, goal: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute validation checks - maintains backward compatibility."""
        await self._execute_validation()
        return {"status": "completed", "agent": self.name}

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities."""
        return ["metaclass_detection", "nesting_validation", "depth_validation", "void_law_enforcement"]

    def validate_state(self) -> bool:
        """Validate agent state."""
        return self.ctx is not None

    async def _execute_validation(self):
        """
        Executes the SystemArchitectAgent's checks for core architectural integrity.
        Reports on metaclass usage, nesting depth, directory depth, and root-level file content.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...")

        # Key 40: No Metaclasses
        passed_40, details_40 = self.check_key_40_no_metaclasses()
        self.ctx.report(self.name, 40, passed_40, details_40)
        
        # Key 41: Scoped Nesting
        passed_41, details_41 = self.check_key_41_scoped_nesting()
        if not passed_41 and self.ctx.intelligence_enabled:
            await self._handle_key_41_fix_attempts(details_41)
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

    def _parse_python_file(self, file_path: str) -> Optional[ast.AST]:
        """Helper to safely parse a Python file into an AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return ast.parse(f.read(), filename=file_path)
        except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as e:
            print(
                f"Warning: Could not parse {file_path} for check: {e}",
                file=sys.stderr
            )
            return None

    def _has_metaclass_keyword(self, node: ast.ClassDef) -> bool:
        """Helper to check if a ClassDef node has a metaclass keyword."""
        return any(kw.arg == "metaclass" for kw in node.keywords)

    def _check_tree_for_metaclasses(self, tree: ast.AST, file_path: str) -> List[str]:
        """
        Helper method to check an AST tree for metaclass definitions.
        Reduces nesting depth in the main check_key_40_no_metaclasses method.
        """
        violations_in_tree = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self._has_metaclass_keyword(node):
                    violations_in_tree.append(f"{file_path}:{node.lineno}")
        return violations_in_tree

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
            tree = self._parse_python_file(file_path)
            if tree:
                metaclass_violations.extend(self._check_tree_for_metaclasses(tree, file_path))
        
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

        for fp in self.ctx.python_files:
            tree = self._parse_python_file(fp)
            if tree:
                visitor = NestVisitor(fp, MAX_NESTING_DEPTH) 
                visitor.visit(tree)
                violations.extend(visitor.violations_in_file)
        return len(violations) == 0, violations

    def check_key_49_directory_depth(self) -> Tuple[bool, List[str]]:
        """
        Checks the directory depth of Python files within the project.
        Enforces depth requirements from SOVEREIGN_REGISTRY.

        Returns:
            A tuple containing:
            - bool: True if no critical directory depth violations are found, False otherwise.
            - List[str]: A list of strings, each indicating a file path and its depth
                          for both violations and warnings.
        """
        violations = []
        for file_path in self.ctx.python_files:
            parts = Path(file_path).parts
            depth = len(parts)
            
            # Skip __init__.py files
            if file_path.endswith("__init__.py"):
                continue
            
            # [SSOT] Check against per-root required depth from SOVEREIGN_REGISTRY
            if parts and parts[0] in depth_map:
                root_folder = parts[0]
                required_depth = depth_map[root_folder]
                if depth != required_depth:
                    violations.append(f"{file_path} (Invalid depth: {depth} - {root_folder} requires depth {required_depth})")
        return len(violations) == 0, violations

    def _has_definitions_in_tree(self, ast_tree: ast.AST) -> bool:
        """Helper to check if an AST tree contains class or function definitions."""
        for node in ast_tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                return True
        return False

    def _check_file_for_definitions(self, file_path: str) -> bool:
        """Helper to check if a file contains class or function definitions."""
        tree = self._parse_python_file(file_path)
        if tree:
            return self._has_definitions_in_tree(tree)
        # Treat unparseable as a violation for safety if parsing failed
        return True 

    def _is_root_file_with_definitions(self, file_path: str) -> bool:
        """Helper to check if a file is at root depth and contains definitions."""
        if len(Path(file_path).parts) == 1:
            if self._check_file_for_definitions(file_path):
                return True
        return False

    def check_key_50_law_of_void(self) -> Tuple[bool, List[str]]:
        """
        Checks for Python files directly in the project root (depth 1) that contain
        class or function definitions. Such files should ideally be minimal or
        serve as entry points without complex logic, adhering to the "Law of Void".

        Returns:
            A tuple containing:
            - bool: True if no root-level files contain class/function definitions, False otherwise.
            - List[str]: A list of file paths that violate the "Law of Void".
        """
        root_violations = []
        for file_path in self.ctx.python_files:
            if self._is_root_file_with_definitions(file_path):
                root_violations.append(file_path)
        return len(root_violations) == 0, root_violations

    async def _handle_key_41_fix_attempts(self, details_41: List[str]):
        """Helper to attempt smart fixes for Key 41 violations."""
        unique_fps_to_fix = list(
            {v.split(":")[0] for v in details_41}
        )
        # Limit fixes to the first 3 files to avoid excessive calls
        for fp in unique_fps_to_fix[:3]:
            await self.smart_fix(fp, 41)

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L1 cognition agent - operational only."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
