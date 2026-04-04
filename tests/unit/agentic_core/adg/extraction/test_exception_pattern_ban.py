"""
Wave 3: Exception Pattern Ban Test
Bans exception-based control flow for StopIteration and GeneratorExit in core algorithms.
"""

import ast
import inspect
from pathlib import Path

import pytest

from agentic_core.adg.extraction import static_scanner


class TestExceptionControlFlowBan:
    """Ban using StopIteration/GeneratorExit as control flow in core algorithms."""

    BANNED_EXCEPTIONS = {'StopIteration', 'GeneratorExit'}

    def test_no_stopiteration_in_detect_cycles(self):
        """Verify _detect_cycles doesn't use StopIteration exception handling."""
        source = inspect.getsource(static_scanner._detect_cycles)
        tree = ast.parse(source)

        violations = self._find_exception_control_flow(tree, self.BANNED_EXCEPTIONS)

        assert not violations, (
            f"_detect_cycles uses banned exception-based control flow: {violations}\n"
            "Use next(iterator, default) instead of try/except StopIteration"
        )

    def test_no_stopiteration_in_scan_file(self):
        """Verify _scan_file doesn't use StopIteration for iteration control."""
        source = inspect.getsource(static_scanner._scan_file)
        tree = ast.parse(source)

        violations = self._find_exception_control_flow(tree, self.BANNED_EXCEPTIONS)

        assert not violations, (
            f"_scan_file uses banned exception-based control flow: {violations}\n"
            "Exception handling for iterators is an anti-pattern"
        )

    def test_all_visitor_classes_no_generator_exit(self):
        """Verify all AST visitor classes don't use GeneratorExit handling."""
        scanner_file = Path(static_scanner.__file__)
        source = scanner_file.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source)

        visitor_classes = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and 'Visitor' in node.name
        ]

        all_violations = []
        for visitor in visitor_classes:
            violations = self._find_exception_control_flow_in_node(visitor, self.BANNED_EXCEPTIONS)
            if violations:
                all_violations.append(f"{visitor.name}: {violations}")

        assert not all_violations, (
            "Visitor classes use banned exception control flow:\n" +
            "\n".join(all_violations)
        )

    def _find_exception_control_flow(self, tree: ast.AST, banned: set) -> list[str]:
        """Find try/except blocks catching banned exceptions for control flow."""
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    # Check if handler catches a banned exception
                    if isinstance(handler.type, ast.Name):
                        if handler.type.id in banned:
                            # Check if the try block contains iterator operations
                            if self._contains_iterator_operation(node.body):
                                violations.append(
                                    f"Catches {handler.type.id} near line {handler.lineno} "
                                    "(iterator control flow anti-pattern)"
                                )
                    elif isinstance(handler.type, ast.Tuple):
                        # Multiple exception types: except (StopIteration, X):
                        for elt in handler.type.elts:
                            if isinstance(elt, ast.Name) and elt.id in banned:
                                if self._contains_iterator_operation(node.body):
                                    violations.append(
                                        f"Catches {elt.id} near line {handler.lineno}"
                                    )

        return violations

    def _find_exception_control_flow_in_node(self, node: ast.AST, banned: set) -> list[str]:
        """Find banned exception handling within a specific node."""
        violations = []

        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                for handler in child.handlers:
                    if isinstance(handler.type, ast.Name) and handler.type.id in banned:
                        violations.append(
                            f"Line {handler.lineno}: catches {handler.type.id}"
                        )

        return violations

    def _contains_iterator_operation(self, body: list[ast.AST]) -> bool:
        """Check if code block contains next() calls or iterator operations."""
        for node in ast.walk(ast.Module(body=body, type_ignores=[])):
            if isinstance(node, ast.Call):
                # Check for next() calls
                if isinstance(node.func, ast.Name) and node.func.id == 'next':
                    return True
                # Check for .__next__() or .next() method calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ('__next__', 'next'):
                        return True
        return False


class TestNextWithDefaultPattern:
    """Enforce next(iterator, default) pattern over exception handling."""

    def test_detect_cycles_uses_next_with_default(self):
        """Verify _detect_cycles uses next(children, None) pattern."""
        source = inspect.getsource(static_scanner._detect_cycles)

        # Should use next(..., None) or next(..., default)
        has_next_with_default = 'next(children, None)' in source or 'next(iter' in source

        assert has_next_with_default, (
            "_detect_cycles should use next(iterator, default) pattern. "
            "Found manual StopIteration handling instead."
        )

    def test_no_bare_next_without_default(self):
        """Flag bare next() calls without default value."""
        scanner_file = Path(static_scanner.__file__)
        source = scanner_file.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source)

        bare_next_calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'next':
                    # Check if it has a second argument (default)
                    if len(node.args) < 2 and not node.keywords:
                        # Get line number from parent Try node if available
                        line_no = getattr(node, 'lineno', 'unknown')
                        bare_next_calls.append(line_no)

        # Allow some bare next() calls if they're in proper exception handling
        # But flag them for review
        if bare_next_calls:
            pytest.warns(
                UserWarning,
                message=f"Found {len(bare_next_calls)} bare next() calls without default at lines: {bare_next_calls[:5]}"
            )


class TestExceptionHandlingDocumentation:
    """Require justification for any exception handling in core loops."""

    def test_all_try_blocks_have_guardian_comments(self):
        """All try/except blocks must have # guardian: comments justifying the exception."""
        scanner_file = Path(static_scanner.__file__)
        source_lines = scanner_file.read_text(encoding='utf-8', errors='replace').split('\n')

        tree = ast.parse('\n'.join(source_lines))

        undocumented_exceptions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Check if previous line or same line has guardian comment
                line_idx = node.lineno - 1  # 0-indexed

                # Look for guardian comment on same line or previous line
                has_guardian = False
                for offset in [0, -1]:
                    check_idx = line_idx + offset
                    if 0 <= check_idx < len(source_lines):
                        if '# guardian:' in source_lines[check_idx]:
                            has_guardian = True
                            break

                if not has_guardian:
                    # Get the exception types being caught
                    exc_types = []
                    for handler in node.handlers:
                        if isinstance(handler.type, ast.Name):
                            exc_types.append(handler.type.id)
                        elif isinstance(handler.type, ast.Tuple):
                            for elt in handler.type.elts:
                                if isinstance(elt, ast.Name):
                                    exc_types.append(elt.id)

                    undocumented_exceptions.append({
                        'line': node.lineno,
                        'exceptions': exc_types
                    })

        # Filter to only critical exceptions (not ValueError, TypeError etc)
        critical_undocumented = [
            e for e in undocumented_exceptions
            if any(exc in {'StopIteration', 'GeneratorExit', 'RuntimeError'} for exc in e['exceptions'])
        ]

        assert not critical_undocumented, (
            "Found undocumented exception handling for critical exceptions:\n" +
            "\n".join(f"  Line {e['line']}: catches {e['exceptions']} without # guardian:"
                     for e in critical_undocumented[:10])
        )
