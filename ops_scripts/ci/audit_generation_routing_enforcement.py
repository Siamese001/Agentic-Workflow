"""AST-based Generation Routing Enforcement Scanner

Phase 4: Enforces that all LLM generation flows through SovereignLLMGateway.
Scans for:
- Forbidden provider SDK imports outside allowlist modules
- Model string literals outside allowed configurations
- Direct provider client instantiation in agents
"""
import ast
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
ALLOWLIST_MODULES = {'infrastructure/sdks_mcps/client_wrappers', 'agentic_core/L2_execution/enforcement/SovereignLLMGateway', 'agentic_core/config/core', 'ops_scripts/ci', TESTS_DIR}
FORBIDDEN_IMPORTS = {'openai', 'anthropic', 'vertexai', 'google.generativeai', 'transformers', 'torch'}
ALLOWED_MODEL_CONFIGS = {'agentic_core/config/core/gateway_config.py', 'agentic_core/config/core/sovereign_config.py', 'infrastructure/sdks_mcps/client_wrappers', 'agentic_core/L2_execution/enforcement/SovereignLLMGateway.py'}

class RoutingViolation:
    """Represents a routing enforcement violation."""

    def __init__(self, file_path: str, line: int, violation_type: str, details: str):
        self.file_path = file_path
        self.line = line
        self.violation_type = violation_type
        self.details = details

    def __str__(self):
        return f'{self.file_path}:{self.line} - {self.violation_type}: {self.details}'

class GenerationRoutingScanner(ast.NodeVisitor):
    """AST scanner for generation routing violations."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[RoutingViolation] = []
        self.imports: dict[str, str] = {}
        self.is_in_allowlist = self._check_allowlist()

    def _check_allowlist(self) -> bool:
        """Check if current file is in allowlist modules."""
        abs_path = Path(self.file_path).resolve()
        for allowed in ALLOWLIST_MODULES:
            if allowed in str(abs_path):
                return True
        if TESTS_DIR in str(abs_path):
            return True
        return False

    def visit_Import(self, node: ast.Import) -> Any:
        """Check for forbidden imports."""
        if self.is_in_allowlist:
            return
        for alias in node.names:
            module = alias.name
            if any(module.startswith(forbidden) for forbidden in FORBIDDEN_IMPORTS):
                self.violations.append(RoutingViolation(self.file_path, node.lineno, 'FORBIDDEN_IMPORT', f"Import of '{module}' not allowed outside allowlist modules"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Check for forbidden from imports."""
        if self.is_in_allowlist:
            return
        if node.module:
            if any(node.module.startswith(forbidden) for forbidden in FORBIDDEN_IMPORTS):
                self.violations.append(RoutingViolation(self.file_path, node.lineno, 'FORBIDDEN_IMPORT', f"Import from '{node.module}' not allowed outside allowlist modules"))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for direct provider client instantiation."""
        if self.is_in_allowlist:
            return
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in {'OpenAI', 'Anthropic', 'VertexAI'}:
                self.violations.append(RoutingViolation(self.file_path, node.lineno, 'DIRECT_CLIENT_INSTANTIATION', f"Direct instantiation of '{func_name}' not allowed"))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in {'ChatCompletion', 'Messages', 'GenerativeModel'}:
                self.violations.append(RoutingViolation(self.file_path, node.lineno, 'DIRECT_API_USAGE', f"Direct usage of '{node.func.attr}' API not allowed"))
        self.generic_visit(node)

    def visit_Str(self, node: ast.Str) -> Any:
        """Check for model string literals."""
        self._check_model_literal(node.s, node.lineno)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Check for model string literals."""
        if isinstance(node.value, str):
            self._check_model_literal(node.value, node.lineno)
        self.generic_visit(node)

    def _check_model_literal(self, value: str, line: int):
        """Check if a string literal is a model name."""
        if self.is_in_allowlist:
            return
        model_patterns = {'gpt-4', 'gpt-4o', 'gpt-3.5', 'gpt-4-turbo', 'claude-3', 'claude-2', 'claude-instant', 'gemini', 'gemini-pro', 'gemini-3', 'text-embedding-3', 'text-davinci', 'text-curie'}
        value_lower = value.lower()
        if any(pattern in value_lower for pattern in model_patterns):
            if not any(allowed in self.file_path for allowed in ALLOWED_MODEL_CONFIGS):
                self.violations.append(RoutingViolation(self.file_path, line, 'MODEL_LITERAL', f"Model string literal '{value}' not allowed outside config files"))

def scan_file(file_path: Path) -> list[RoutingViolation]:
    """Scan a single Python file for routing violations."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        scanner = GenerationRoutingScanner(str(file_path))
        scanner.visit(tree)
        return scanner.violations
    except Exception as e:
        raise
        print(f'Error scanning {file_path}: {e}', file=sys.stderr)
        return []

def scan_directory(root_dir: Path) -> list[RoutingViolation]:
    """Scan all Python files in directory recursively."""
    violations = []
    for py_file in root_dir.rglob('*.py'):
        if '__pycache__' in str(py_file) or '.git' in str(py_file):
            continue
        file_violations = scan_file(py_file)
        violations.extend(file_violations)
    return violations

def main():
    """Main entry point for the scanner."""
    if len(sys.argv) > 1:
        scan_path = Path(sys.argv[1])
    else:
        scan_path = Path(__file__).parent.parent.parent
    if not scan_path.exists():
        print(f'Error: Path {scan_path} does not exist', file=sys.stderr)
        sys.exit(1)
    print(f'Scanning {scan_path} for generation routing violations...')
    if scan_path.is_file():
        violations = scan_file(scan_path)
    else:
        violations = scan_directory(scan_path)
    by_type = {}
    for v in violations:
        by_type.setdefault(v.violation_type, []).append(v)
    total = len(violations)
    print(f'\nScan complete. Found {total} violations.')
    if total > 0:
        print('\nViolations by type:')
        for vtype, vlist in sorted(by_type.items()):
            print(f'\n{vtype} ({len(vlist)}):')
            for v in sorted(vlist, key=lambda x: (x.file_path, x.line)):
                details = v.details.replace('→', '->')
                print(f'  {v.file_path}:{v.line} - {v.violation_type}: {details}')
        sys.exit(1)
    else:
        print('OK: No routing violations found!')
        sys.exit(0)
if __name__ == '__main__':
    main()
