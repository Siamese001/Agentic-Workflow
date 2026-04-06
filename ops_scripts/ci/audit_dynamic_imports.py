"""Dynamic Import Detection Scanner - Hardening Sweep

Detects dangerous dynamic import patterns that could bypass static analysis:
- importlib.import_module
- __import__
- getattr on provider modules
- eval/exec constructing provider clients
"""
import ast
import sys
from pathlib import Path
from typing import Any


# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
DANGEROUS_FUNCTIONS = {'importlib.import_module', '__import__', 'eval', 'exec', 'getattr', 'hasattr', 'setattr'}
PROVIDER_MODULES = {'openai', 'anthropic', 'vertexai', 'transformers', 'torch', 'sentence_transformers'}
ALLOWLIST_MODULES = {'infrastructure/sdks_mcps/client_wrappers', 'agentic_core/L2_execution/enforcement', TESTS_DIR, 'ops_scripts/ci', 'system_learning/engines/embedding_service_factory'}

class DynamicImportViolation:
    """Represents a dynamic import violation."""

    def __init__(self, file_path: str, line: int, violation_type: str, details: str):
        self.file_path = file_path
        self.line = line
        self.violation_type = violation_type
        self.details = details

    def __str__(self):
        return f'{self.file_path}:{self.line} - {self.violation_type}: {self.details}'

class DynamicImportScanner(ast.NodeVisitor):
    """AST scanner for dynamic import violations."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[DynamicImportViolation] = []
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

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for dangerous function calls."""
        if self.is_in_allowlist:
            return self.generic_visit(node)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in DANGEROUS_FUNCTIONS:
                self._check_dangerous_call(node, func_name)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in {'import_module'}:
                self.violations.append(DynamicImportViolation(self.file_path, node.lineno, 'DYNAMIC_IMPORT', f'Direct call to {node.func.attr} detected'))
        self.generic_visit(node)

    def _check_dangerous_call(self, node: ast.Call, func_name: str):
        """Check if dangerous call involves provider modules."""
        for arg in node.args:
            if isinstance(arg, ast.Str) or (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                value = arg.value if isinstance(arg, ast.Constant) else arg.s
                if any(provider in value for provider in PROVIDER_MODULES):
                    self.violations.append(DynamicImportViolation(self.file_path, node.lineno, 'DYNAMIC_IMPORT', f"{func_name} with provider module '{value}'"))
        if func_name in {'eval', 'exec'}:
            self.violations.append(DynamicImportViolation(self.file_path, node.lineno, 'CODE_EXECUTION', f'Use of {func_name} - potential bypass vector'))

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        """Check for dangerous attribute access."""
        if self.is_in_allowlist:
            return self.generic_visit(node)
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            if var_name in PROVIDER_MODULES and node.attr in {'ChatCompletion', 'Messages', 'GenerativeModel'}:
                self.violations.append(DynamicImportViolation(self.file_path, node.lineno, 'PROVIDER_ACCESS', f'Direct access to {var_name}.{node.attr}'))
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        """Check for dynamic imports."""
        if self.is_in_allowlist:
            return self.generic_visit(node)
        for alias in node.names:
            if alias.name.startswith('importlib'):
                self.violations.append(DynamicImportViolation(self.file_path, node.lineno, 'DYNAMIC_IMPORT', f"Import of '{alias.name}' - potential dynamic import"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Check for from imports of dangerous modules."""
        if self.is_in_allowlist:
            return self.generic_visit(node)
        if node.module and node.module in {'importlib'}:
            self.violations.append(DynamicImportViolation(self.file_path, node.lineno, 'DYNAMIC_IMPORT', f"From import of '{node.module}' - potential dynamic import"))
        self.generic_visit(node)

def scan_file(file_path: Path) -> list[DynamicImportViolation]:
    """Scan a single Python file for dynamic import violations."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        scanner = DynamicImportScanner(str(file_path))
        scanner.visit(tree)
        return scanner.violations
    except Exception as e:
        raise
        print(f'Error scanning {file_path}: {e}', file=sys.stderr)
        return []

def scan_directory(root_dir: Path) -> list[DynamicImportViolation]:
    """Scan all Python files in directory recursively, restricted to first-party code."""
    violations = []
    first_party_prefixes = ['agentic_core/', 'system_learning/', 'apps_rg/', 'apps_shared/', 'data/', 'tests/', 'ops_scripts/']
    third_party_patterns = ['.nox/', 'venv/', 'env/', '__pycache__/', '.git/', 'site-packages/', 'build/', 'dist/', '.pytest_cache/']
    for py_file in root_dir.rglob('*.py'):
        file_str = str(py_file)
        if any(pattern in file_str for pattern in third_party_patterns):
            continue
        if not any(py_file.is_relative_to(Path(p)) if Path(p).exists() else file_str.startswith(p) for p in first_party_prefixes):
            if not any(file_str.startswith(p) for p in first_party_prefixes):
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
    print(f'Scanning {scan_path} for dynamic import violations...')
    if scan_path.is_file():
        violations = scan_file(scan_path)
    else:
        violations = scan_directory(scan_path)
    by_type = {}
    for v in violations:
        by_type.setdefault(v.violation_type, []).append(v)
    total = len(violations)
    print(f'\nScan complete. Found {total} dynamic import violations.')
    if total > 0:
        print('\nViolations by type:')
        for vtype, vlist in sorted(by_type.items()):
            print(f'\n{vtype} ({len(vlist)}):')
            for v in sorted(vlist, key=lambda x: (x.file_path, x.line)):
                print(f'  {v}')
        sys.exit(1)
    else:
        print('OK: No dynamic import violations found!')
        sys.exit(0)
if __name__ == '__main__':
    main()
