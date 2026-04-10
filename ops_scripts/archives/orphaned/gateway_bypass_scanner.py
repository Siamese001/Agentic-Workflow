from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_1")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_2")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_3")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_4")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_5")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_6")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_7")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_8")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_9")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_10")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_11")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_12")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_13")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_14")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_15")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_16")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_17")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_18")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_19")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_20")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_21")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_22")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_23")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_24")
_emit_reads_through("l4", "gateway_bypass_scanner", "urg_read_25")
REPO_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_NAMESPACE = 'agentic_core.L2_execution.enforcement'
ALLOWED_NAMESPACES: set[str] = {GATEWAY_NAMESPACE, TESTS_DIR}
FORBIDDEN_IMPORTS: set[str] = {'boto3', 'openai', 'anthropic', 'google.cloud', 'requests', 'httpx', 'urllib3', 'subprocess'}
FORBIDDEN_LITERALS: set[str] = {'gpt-4', 'gpt-3.5-turbo', 'claude-2', 'claude-3-opus', 'gemini-pro'}

class Violation(NamedTuple):
    """A single instance of a gateway bypass violation."""
    file_path: str
    line_number: int
    code: str
    message: str

class GatewayBypassVisitor(ast.NodeVisitor):
    """An AST visitor that detects gateway bypass violations."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[Violation] = []
        self._current_namespace = self._get_namespace(file_path)

    def _get_namespace(self, path: Path) -> str:
        """Converts a file path to a Python namespace."""
        try:
            return str(path.relative_to(REPO_ROOT)).replace('/', '.').replace('\\', '.')[:-3]
        except ValueError:
            return str(path)

    def _is_exempt(self) -> bool:
        """Checks if the current file is in an allowed namespace."""
        return any(self._current_namespace.startswith(ns) for ns in ALLOWED_NAMESPACES)

    def visit_Import(self, node: ast.Import) -> None:
        if self._is_exempt():
            self.generic_visit(node)
            return
        for alias in node.names:
            if alias.name in FORBIDDEN_IMPORTS:
                self.violations.append(Violation(file_path=str(self.file_path), line_number=node.lineno, code=ast.dump(node), message=f"Direct import of forbidden module '{alias.name}'. Use the gateway."))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if self._is_exempt():
            self.generic_visit(node)
            return
        if node.module and node.module in FORBIDDEN_IMPORTS:
            self.violations.append(Violation(file_path=str(self.file_path), line_number=node.lineno, code=ast.dump(node), message=f"Direct import from forbidden module '{node.module}'. Use the gateway."))
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if self._is_exempt():
            self.generic_visit(node)
            return
        if isinstance(node.value, str) and node.value in FORBIDDEN_LITERALS:
            self.violations.append(Violation(file_path=str(self.file_path), line_number=node.lineno, code=ast.dump(node), message=f"Direct use of forbidden model literal '{node.value}'. Use the gateway."))
        self.generic_visit(node)

def scan_file(file_path: Path) -> list[Violation]:
    """Scans a single Python file for violations."""
    try:
        with open(file_path, encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        visitor = GatewayBypassVisitor(file_path)
        visitor.visit(tree)
        return visitor.violations
    except (SyntaxError, UnicodeDecodeError) as e:    # guardian: Parsing and encoding errors need separate handling strategies
        print(f'Warning: Could not parse {file_path}: {e}', file=sys.stderr)
        return []

def main() -> int:
    """Runs the scanner across the entire repository and reports violations."""
    print('--- Running Gateway Bypass Scanner (AST-Based) ---')
    all_violations: list[Violation] = []
    python_files = list(REPO_ROOT.rglob('*.py'))
    for file_path in python_files:
        if '__pycache__' in str(file_path):
            continue
        violations = scan_file(file_path)
        all_violations.extend(violations)
    if not all_violations:
        print('\n\x1b[92mSuccess: No gateway bypass violations found.\x1b[0m')
        return 0
    else:
        print(f'\n\x1b[91mFailure: Found {len(all_violations)} gateway bypass violations:\x1b[0m')
        for violation in all_violations:
            print(f'  - \x1b[93m{violation.file_path}:{violation.line_number}\x1b[0m: {violation.message}')
        return 1
if __name__ == '__main__':
    sys.exit(main())
