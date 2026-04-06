"""Embedding Surface Exhaustive Audit - Hardening Sweep

Programmatically enumerates all modules referencing:
- AutoModel
- AutoTokenizer
- sentence_transformers
- OpenAI embeddings
- Other embedding primitives

Asserts all calls occur inside embedding factory only.
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
EMBEDDING_PRIMITIVES = {'AutoModel', 'AutoTokenizer', 'AutoModelForSeq2SeqLM', 'AutoModelForMaskedLM', 'sentence_transformers', 'SentenceTransformer', 'OpenAI', 'EmbeddingServiceFactory', 'EmbeddingResult', 'text-embedding-3', 'all-MiniLM'}
EMBEDDING_FACTORY_PATH = 'system_learning/engines/embedding_service_factory.py'
ALLOWLIST_MODULES = {'infrastructure/sdks_mcps/client_wrappers', 'system_learning/engines/embedding_service_factory', TESTS_DIR, 'ops_scripts/ci'}

class EmbeddingUsageViolation:
    """Represents an embedding usage violation."""

    def __init__(self, file_path: str, line: int, violation_type: str, details: str):
        self.file_path = file_path
        self.line = line
        self.violation_type = violation_type
        self.details = details

    def __str__(self):
        return f'{self.file_path}:{self.line} - {self.violation_type}: {self.details}'

class EmbeddingUsageScanner(ast.NodeVisitor):
    """AST scanner for embedding usage violations."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[EmbeddingUsageViolation] = []
        self.is_in_factory = self._check_if_factory()
        self.is_in_allowlist = self._check_allowlist()

    def _check_if_factory(self) -> bool:
        """Check if current file is the embedding factory."""
        return 'embedding_service_factory.py' in self.file_path

    def _check_allowlist(self) -> bool:
        """Check if current file is in allowlist modules."""
        abs_path = Path(self.file_path).resolve()
        for allowed in ALLOWLIST_MODULES:
            if allowed in str(abs_path):
                return True
        return False

    def visit_Import(self, node: ast.Import) -> Any:
        """Check for imports of embedding primitives."""
        if self.is_in_factory or self.is_in_allowlist:
            return self.generic_visit(node)
        for alias in node.names:
            if any(primitive in alias.name for primitive in EMBEDDING_PRIMITIVES):
                self.violations.append(EmbeddingUsageViolation(self.file_path, node.lineno, 'EMBEDDING_IMPORT', f"Import of '{alias.name}' outside factory"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Check for from imports of embedding primitives."""
        if self.is_in_factory or self.is_in_allowlist:
            return self.generic_visit(node)
        if node.module:
            if 'transformers' in node.module:
                for alias in node.names:
                    if any(primitive in alias.name for primitive in EMBEDDING_PRIMITIVES):
                        self.violations.append(EmbeddingUsageViolation(self.file_path, node.lineno, 'EMBEDDING_IMPORT', f"From import '{alias.name}' from transformers outside factory"))
            if 'sentence_transformers' in node.module:
                self.violations.append(EmbeddingUsageViolation(self.file_path, node.lineno, 'EMBEDDING_IMPORT', 'From import from sentence_transformers outside factory'))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for direct usage of embedding primitives."""
        if self.is_in_factory or self.is_in_allowlist:
            return self.generic_visit(node)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in EMBEDDING_PRIMITIVES:
                self.violations.append(EmbeddingUsageViolation(self.file_path, node.lineno, 'EMBEDDING_USAGE', f"Direct usage of '{func_name}' outside factory"))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in {'ChatCompletion', 'Embedding'}:
                self.violations.append(EmbeddingUsageViolation(self.file_path, node.lineno, 'EMBEDDING_USAGE', f"Direct usage of '{node.func.attr}' API outside factory"))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        """Check for attribute access to embedding primitives."""
        if self.is_in_factory or self.is_in_allowlist:
            return self.generic_visit(node)
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            if var_name in EMBEDDING_PRIMITIVES:
                self.violations.append(EmbeddingUsageViolation(self.file_path, node.lineno, 'EMBEDDING_ACCESS', f'Access to {var_name}.{node.attr} outside factory'))
        self.generic_visit(node)

def scan_file(file_path: Path) -> list[EmbeddingUsageViolation]:
    """Scan a single Python file for embedding usage violations."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        scanner = EmbeddingUsageScanner(str(file_path))
        scanner.visit(tree)
        return scanner.violations
    except Exception as e:
        raise
        print(f'Error scanning {file_path}: {e}', file=sys.stderr)
        return []

def scan_directory(root_dir: Path) -> list[EmbeddingUsageViolation]:
    """Scan all Python files in directory recursively."""
    violations = []
    for py_file in root_dir.rglob('*.py'):
        if '__pycache__' in str(py_file) or '.git' in str(py_file):
            continue
        file_violations = scan_file(py_file)
        violations.extend(file_violations)
    return violations

def verify_factory_implementation():
    """Verify that embedding factory is properly implemented."""
    factory_path = Path('system_learning/engines/embedding_service_factory.py')
    if not factory_path.exists():
        print('ERROR: Embedding factory not found!')
        return False
    with open(factory_path) as f:
        content = f.read()
    required_patterns = ['class EmbeddingServiceFactory', 'def get_or_disabled', 'EMBEDDING_ENABLED', 'class _DisabledEmbeddingService']
    missing = []
    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)
    if missing:
        print(f'ERROR: Factory missing required components: {missing}')
        return False
    print('OK: Embedding factory implementation verified')
    return True

def main():
    """Main entry point for the audit."""
    if len(sys.argv) > 1:
        scan_path = Path(sys.argv[1])
    else:
        scan_path = Path(__file__).parent.parent.parent
    if not scan_path.exists():
        print(f'Error: Path {scan_path} does not exist', file=sys.stderr)
        sys.exit(1)
    print(f'Auditing {scan_path} for embedding surface violations...')
    if not verify_factory_implementation():
        sys.exit(1)
    if scan_path.is_file():
        violations = scan_file(scan_path)
    else:
        violations = scan_directory(scan_path)
    by_type = {}
    for v in violations:
        by_type.setdefault(v.violation_type, []).append(v)
    total = len(violations)
    print(f'\nAudit complete. Found {total} embedding surface violations.')
    if total > 0:
        print('\nViolations by type:')
        for vtype, vlist in sorted(by_type.items()):
            print(f'\n{vtype} ({len(vlist)}):')
            for v in sorted(vlist, key=lambda x: (x.file_path, x.line)):
                print(f'  {v}')
        print(f'\nREMEDIATION: All embedding usage should flow through {EMBEDDING_FACTORY_PATH}')
        sys.exit(1)
    else:
        print('OK: All embedding usage properly contained in factory!')
        sys.exit(0)
if __name__ == '__main__':
    main()
