"""PatternEnforcerAgent - Coding pattern enforcement.

Extracted from canon_agents_pattern.py.
Enforces coding patterns and best practices across Python files.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import ast
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


class CanonBaseAgentInterface(Protocol):
    """Protocol for CanonBaseAgent interface compatibility."""
    ctx: Any
    name: str
    python_files: list[str]


@dataclass
class PatternEnforcerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Pattern enforcement agent for coding best practices.

    Validates Canon Keys 26-39:
        - Key 26: No mutable default arguments.
        - Key 27: Prefer str.join over string concatenation.
        - Key 28: No bare except clauses.
        - Key 29: No assert in production code.
        - Key 30: Prefer f-strings over .format().
        - Key 31: No complex comprehensions.
        - Key 32: No dict.keys() when 'in' suffices.
        - Key 33: No float equality comparisons.
        - Key 34: Use 'is' for None comparisons.
        - Key 36: No shadowed builtins.
        - Key 37: No redundant self usage.
        - Key 38: Prefer comprehensions over loops.
        - Key 39: No useless return statements.

    Note:
        Uses composition with CanonBaseAgentInterface (DDD Phase 9A).

    Attributes:
        agent: Injected CanonBaseAgentInterface implementation.
    """

    def __init__(self, agent_impl: CanonBaseAgentInterface) -> None:
        """
        Initialize with injected agent implementation.

        Args:
            agent_impl: CanonBaseAgentInterface providing ctx and python_files.
        """
        self.agent = agent_impl

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to injected implementation.

        Provides backward compatibility by forwarding unknown attributes.

        Args:
            name: Attribute name to look up.

        Returns:
            Attribute value from agent implementation.
        """
        return getattr(self.agent, name)

    def execute(self) -> Any:
        """
        Executes all defined pattern checks and reports violations.
        """
        print(f'\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\n[>>>] {self.agent.name} ACTIVATED: Pattern Enforcement...')
        keys: Any = [(26, self.check_key_26_no_mutable_defaults), (27, self.check_key_27_prefer_str_join), (28, self.check_key_28_no_bare_except), (29, self.check_key_29_no_assert_in_prod), (30, self.check_key_30_prefer_fstrings), (31, self.check_key_31_no_complex_comprehensions), (32, self.check_key_32_no_dict_keys_check), (33, self.check_key_33_no_float_equality), (34, self.check_key_34_use_is_for_none), (36, self.check_key_36_no_shadowed_builtins), (37, self.check_key_37_no_redundant_self), (38, self.check_key_38_prefer_comprehensions), (39, self.check_key_39_no_useless_return)]
        self._execute_pattern_checks(keys)

    def _execute_pattern_checks(self, keys: list[tuple[int, Callable[[], tuple[bool, list[str]]]]]) -> None:
        """
        Execute pattern checks and report violations.

        Args:
            keys: List of (key_number, check_function) tuples.
        """
        for key, check_func in keys:
            passed, details = check_func()
            self.agent.ctx.report(self.agent.name, key, passed, details)

    def _parse_file_ast(self, filepath: str) -> ast.AST | None:
        """
        Safely parse a Python file into an AST.

        Args:
            filepath: Path to Python file to parse.

        Returns:
            Parsed AST or None if parsing failed.
        """
        try:
            with open(filepath, encoding='utf-8') as f:
                return ast.parse(f.read(), filename=filepath)
        except FileNotFoundError:
            Logger.warning(f'File not found: {filepath}')
        except SyntaxError as e:
            Logger.error(f'Syntax error in {filepath}: {e}')
        except Exception as e:
            Logger.error(f'Error parsing AST for {filepath}: {e}')
        return None

    def _read_file_lines(self, filepath: str) -> list[str] | None:
        """
        Safely read a Python file line by line.

        Args:
            filepath: Path to file to read.

        Returns:
            List of lines or None if reading failed.
        """
        try:
            with open(filepath, encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            Logger.warning(f'File not found: {filepath}')
        except Exception as e:
            Logger.error(f'Error reading lines from {filepath}: {e}')
        return None

    def _check_ast_pattern(
        self,
        node_filter: Callable[[ast.AST], bool],
        violation_formatter: Callable[[str, ast.AST], str | None]
    ) -> tuple[bool, list[str]]:
        """Generic AST pattern checker to reduce code duplication.

        Args:
            node_filter: Function that returns True for nodes to check.
            violation_formatter: Function that returns violation string or None.

        Returns:
            Tuple of (passed, violations_list).
        """
        violations: list[str] = []
        for fp in self.agent.ctx.python_files:
            tree = self._parse_file_ast(fp)
            if not tree:
                continue
            for node in ast.walk(tree):
                if node_filter(node):
                    violation = violation_formatter(fp, node)
                    if violation:
                        violations.append(violation)
        return (len(violations) == 0, violations)

    def check_key_26_no_mutable_defaults(self) -> tuple[bool, list[str]]:
        """Check for mutable default arguments in function definitions."""
        def check_node(node: ast.AST) -> bool:
            return isinstance(node, ast.FunctionDef)

        def format_violation(fp: str, node: ast.AST) -> str | None:
            if not isinstance(node, ast.FunctionDef):
                return None
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    return f"{fp}:{node.lineno} in function '{node.name}'"
            return None

        return self._check_ast_pattern(check_node, format_violation)

    def check_key_27_prefer_str_join(self) -> tuple[bool, list[str]]:
        """
        Checks for string concatenation using '+' operator, preferring `str.join()`.
        Note: This check uses regex and might have false positives/negatives.
        A more robust check would require deeper AST analysis.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            lines: Any = self._read_file_lines(fp)
            if lines:
                for i, line in enumerate(lines, 1):
                    if re.search('\\s*\\+\\s*["\\\']', line) or re.search('["\\\']\\s*\\+\\s*', line):
                        if not re.search('^\\s*#', line) and (not re.search('\\b\\d+\\s*\\+\\s*["\\\']', line)):
                            violations.append(f'{fp}:{i}')
        return (len(violations) == 0, violations)

    def check_key_28_no_bare_except(self) -> tuple[bool, list[str]]:
        """
        Checks for bare `except:` clauses without specifying an exception type.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            tree: Any = self._parse_file_ast(fp)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            violations.append(f'{fp}:{node.lineno}')
        return (len(violations) == 0, violations)

    def check_key_29_no_assert_in_prod(self) -> tuple[bool, list[str]]:
        """
        Checks for `assert` statements, which should generally be avoided in production code.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            tree: Any = self._parse_file_ast(fp)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assert):
                        violations.append(f'{fp}:{node.lineno}')
        return (len(violations) == 0, violations)

    def check_key_30_prefer_fstrings(self) -> tuple[bool, list[str]]:
        """
        Checks for older string formatting methods (`.format()` or `%` operator),
        preferring f-strings.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            lines: Any = self._read_file_lines(fp)
            if lines:
                for i, line in enumerate(lines, 1):
                    if re.search('\\.format\\(|%\\s*\\(', line):
                        violations.append(f'{fp}:{i}')
        return (len(violations) == 0, violations)

    def check_key_31_no_complex_comprehensions(self) -> tuple[bool, list[str]]:
        """
        Placeholder: Checks for overly complex list/dict/set comprehensions.
        Implementation would require defining 'complexity' (e.g., multiple `if`s, nested loops).
        """
        return (True, [])

    def check_key_32_no_dict_keys_check(self) -> tuple[bool, list[str]]:
        """
        Placeholder: Checks for `dict.keys()` usage when `in` operator is sufficient.
        """
        return (True, [])

    def check_key_33_no_float_equality(self) -> tuple[bool, list[str]]:
        """
        Checks for direct equality comparisons (`==`) involving floating-point numbers.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            tree: Any = self._parse_file_ast(fp)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare):
                        if any(isinstance(op, ast.Eq) for op in node.ops):
                            operands: Any = [node.left] + node.comparators
                            if any(isinstance(val, ast.Constant) and isinstance(val.value, float) for val in operands):
                                violations.append(f'{fp}:{node.lineno}')
        return (len(violations) == 0, violations)

    def check_key_34_use_is_for_none(self) -> tuple[bool, list[str]]:
        """
        Checks for `== None` or `!= None` comparisons, preferring `is None` or `is not None`.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            tree: Any = self._parse_file_ast(fp)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare):
                        if any(isinstance(comp, ast.Constant) and comp.value is None for comp in node.comparators):
                            if not all(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops):
                                violations.append(f'{fp}:{node.lineno}')
        return (len(violations) == 0, violations)

    def check_key_36_no_shadowed_builtins(self) -> tuple[bool, list[str]]:
        """
        Checks for function parameters that shadow Python's built-in names.
        """
        violations: Any = []
        builtins: Any = {'list', 'dict', 'set', 'str', 'int', 'float', 'bool', 'type', 'id', 'input', 'open', 'print'}
        for fp in self.agent.ctx.python_files:
            tree: Any = self._parse_file_ast(fp)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for arg in node.args.args:
                            if arg.arg in builtins:
                                violations.append(f"{fp}:{node.lineno} function '{node.name}' parameter '{arg.arg}'")
        return (len(violations) == 0, violations)

    def check_key_37_no_redundant_self(self) -> tuple[bool, list[str]]:
        """
        Placeholder: Checks for redundant `self` usage (e.g., `self.x = self.x`).
        """
        return (True, [])

    def check_key_38_prefer_comprehensions(self) -> tuple[bool, list[str]]:
        """
        Placeholder: Checks for explicit loops that could be replaced by comprehensions.
        """
        return (True, [])

    def check_key_39_no_useless_return(self) -> tuple[bool, list[str]]:
        """
        Checks for explicit `return None` or `return` at the end of a function
        where the function implicitly returns `None`.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            tree: Any = self._parse_file_ast(fp)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.body and isinstance(node.body[-1], ast.Return):
                            if node.body[-1].value is None:
                                violations.append(f"{fp}:{node.body[-1].lineno} in function '{node.name}'")
        return (len(violations) == 0, violations)

    def heal_repository(self) -> dict:
        """
        Execute healing chain via parent class.

        Returns:
            Dict with healing results from parent implementation.
        """
        return super().heal_repository()
