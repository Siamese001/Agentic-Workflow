from __future__ import annotations
"""
Canon Key Validators using AST-based validation.
Replaces regex/string matching with proper AST analysis to eliminate false positives.
"""
import ast
from pathlib import Path
from typing import List, Dict, Any
from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator, parse_and_validate
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin

class PrintStatementValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 2: Detects print() statements using AST.
    Automatically ignores TYPE_CHECKING blocks via base class.
    """

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for print() function calls."""
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            if not self.in_type_checking:
                self.report('Forbidden print() statement detected', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class EvalExecValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 6: Detects eval() and exec() calls using AST.
    """

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for eval() or exec() function calls."""
        if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
            if not self.in_type_checking:
                self.report(f'Forbidden {node.func.id}() call detected', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class DebuggerValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 3: Detects breakpoint() and pdb.set_trace() using AST.
    """

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for debugger calls."""
        if isinstance(node.func, ast.Name) and node.func.id == 'breakpoint':
            if not self.in_type_checking:
                self.report('Debugger breakpoint() detected', node)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pdb' and (node.func.attr == 'set_trace'):
                if not self.in_type_checking:
                    self.report('Debugger pdb.set_trace() detected', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class EmptyExceptValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 4: Detects empty except blocks (except: pass).
    """

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
        """Check for empty except blocks."""
        is_empty: Any = not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass))
        if is_empty and (not self.in_type_checking):
            self.report('Empty except block detected (except: pass)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class BareExceptValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 5: Detects bare except: statements (catching all exceptions).
    """

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
        """Check for bare except statements."""
        if node.type is None and (not self.in_type_checking):
            self.report('Bare except: statement detected (should specify exception type)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class ExternalHttpValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 23: Detects forbidden HTTP library imports (requests, urllib, httpx).
    Automatically handles TYPE_CHECKING blocks and exception ledger.
    """
    FORBIDDEN_MODULES: Any = {'requests', 'urllib', 'urllib3', 'httpx', 'aiohttp'}

    def visit_Import(self, node: ast.Import) -> Any:
        """Check for forbidden HTTP library imports."""
        if not self.in_type_checking:
            for alias in node.names:
                module_root: Any = alias.name.split('.')[0]
                if module_root in self.FORBIDDEN_MODULES:
                    self.report(f'Forbidden HTTP library import: {alias.name} (use MCP fetch_client_sovereign instead)', node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Check for forbidden HTTP library imports in 'from X import Y'."""
        if not self.in_type_checking and node.module:
            module_root: Any = node.module.split('.')[0]
            if module_root in self.FORBIDDEN_MODULES:
                self.report(f'Forbidden HTTP library import: from {node.module} (use MCP fetch_client_sovereign instead)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class AsyncBlockingValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator, MCPHardenedMixin):
    """
    Key 31: Detects blocking calls in async functions (time.sleep, requests, etc).
    """

    def __init__(self, file_path: Path, content: str, key_id: int) -> None:
        super().__init__(file_path, content, key_id)
        self.in_async_function = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        """Track when we're inside an async function."""
        old_async: Any = self.in_async_function
        self.in_async_function = True
        self.generic_visit(node)
        self.in_async_function = old_async

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for blocking calls inside async functions."""
        if self.in_async_function and (not self.in_type_checking):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'time' and (node.func.attr == 'sleep'):
                    self.report('Blocking time.sleep() in async function (use asyncio.sleep())', node)
                elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'requests':
                    self.report(f'Blocking requests.{node.func.attr}() in async function (use httpx.AsyncClient or asyncio.to_thread())', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class DangerousBuiltinsValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 42: Detects dangerous builtin functions (compile, __import__, globals, locals).
    """
    DANGEROUS_BUILTINS: Any = {'compile', '__import__', 'globals', 'locals', 'vars'}

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for dangerous builtin calls."""
        if isinstance(node.func, ast.Name) and node.func.id in self.DANGEROUS_BUILTINS:
            if not self.in_type_checking:
                self.report(f'Dangerous builtin {node.func.id}() detected (potential security risk)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def validate_print_statements(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 2: No print statements."""
    return parse_and_validate(file_path, content, 2, PrintStatementValidatorAgent)

def validate_eval_exec(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 6: No eval/exec."""
    return parse_and_validate(file_path, content, 6, EvalExecValidatorAgent)

def validate_debugger(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 3: No debugger statements."""
    return parse_and_validate(file_path, content, 3, DebuggerValidatorAgent)

def validate_empty_except(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 4: No empty except blocks."""
    return parse_and_validate(file_path, content, 4, EmptyExceptValidatorAgent)

def validate_bare_except(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 5: No bare except statements."""
    return parse_and_validate(file_path, content, 5, BareExceptValidatorAgent)

def validate_external_http(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 23: No external HTTP imports."""
    return parse_and_validate(file_path, content, 23, ExternalHTTPValidator)

def validate_async_blocking(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 31: No blocking calls in async."""
    return parse_and_validate(file_path, content, 31, AsyncBlockingValidatorAgent)

def validate_dangerous_builtins(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Validate Key 42: No dangerous builtins."""
    return parse_and_validate(file_path, content, 42, DangerousBuiltinsValidatorAgent)
