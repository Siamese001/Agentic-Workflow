
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
from dataclasses import dataclass
"""
Canon Key Validators using AST-based validation.
Replaces regex/string matching with proper AST analysis to eliminate false positives.
"""
import ast
from pathlib import Path
from typing import List, Dict, Any
from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator, parse_and_validate
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

@dataclass
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
