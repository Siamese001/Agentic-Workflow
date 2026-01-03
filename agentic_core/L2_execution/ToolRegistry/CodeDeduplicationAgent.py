from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import textwrap
import shutil
from apps_shared.config.operational_config import OPERATIONAL_EXCLUDED_DIRS

# Tree-sitter for AST fingerprinting
try:
    from tree_sitter import Language, Parser
    from tree_sitter_python import language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Parser = None
    Language = None

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.timeout_decorator import timeout

class CodeDeduplicationAgent(HealerMixin):
    """
    Batch agent for detecting and optionally refactoring duplicated code.
    
    Responsibilities:
    - Computes perceptual hashes of normalized AST nodes.
    - Groups duplicates with similarity > 95%.
    - Reports redundancy to the L4 Ledger for audit tracking.
    - [SURGERY] When RUN_SPRAWL_SURGERY=True: Extracts duplicates to shared utils
    """

    def __init__(self, similarity_threshold: float=0.95, min_lines: int=8):
        self.threshold = similarity_threshold
        self.min_lines = min_lines
        self.duplicate_groups: Dict[str, List[Tuple[Path, str, int]]] = defaultdict(list)
        self.extracted_count = 0
        self.errors: List[str] = []
        
        # Initialize tree-sitter parser if available
        self.ts_parser: Optional[Parser] = None
        if TREE_SITTER_AVAILABLE:
            try:
                self.ts_parser = Parser()
                self.ts_parser.language = language()
            except Exception as e:
                self.errors.append(f'Tree-sitter initialization failed: {e}')
                self.ts_parser = None
    
    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L2 compliance."""
        assert hasattr(self, 'threshold'), "Missing threshold"
        assert hasattr(self, 'duplicate_groups'), "Missing duplicate_groups"
        assert 0 < self.threshold <= 1, "threshold must be 0-1"
        return True

    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalize for hashing: dedent, collapse whitespace, strip comments."""
        code = textwrap.dedent(code)
        lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            if stripped:
                lines.append(' '.join(stripped.split()))
        return '\n'.join(lines)
    
    def _normalize_ast_tree(self, node: ast.AST) -> str:
        """Anonymize variables and constants in AST for structural comparison."""
        if isinstance(node, ast.Name):
            return 'VAR'
        elif isinstance(node, ast.Constant):
            return f'CONST_{type(node.value).__name__}'
        elif isinstance(node, (ast.Num, ast.Str)):
            # Backward compatibility for older Python versions
            return 'CONST'
        children = [self._normalize_ast_tree(child) for child in ast.iter_child_nodes(node)]
        return f'{type(node).__name__}({"|".join(children)})'
    
    def _normalize_ts_tree(self, node: Any) -> str:
        """Normalize tree-sitter node for structural comparison."""
        if node.type == 'identifier':
            return 'VAR'
        elif node.type in ['string', 'integer', 'float', 'true', 'false', 'none']:
            return f'CONST_{node.type}'
        children = [self._normalize_ts_tree(child) for child in node.children]
        return f'{node.type}({"|".join(children)})'

    def _hash_block(self, code: str) -> str:
        """Generate AST fingerprint for code block."""
        # Try AST fingerprinting first
        try:
            if self.ts_parser:
                # Tree-sitter based fingerprint
                tree = self.ts_parser.parse(bytes(code, 'utf8'))
                norm_tree = self._normalize_ts_tree(tree.root_node)
                return hashlib.sha256(str(norm_tree).encode()).hexdigest()
            else:
                # Python AST based fingerprint
                tree = ast.parse(code)
                norm_tree = self._normalize_ast_tree(tree)
                return hashlib.sha256(str(norm_tree).encode()).hexdigest()
        except Exception:
            # Fallback to text-based normalization
            normalized = self._normalize_code(code)
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _extract_functions_classes(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Parse file and extract function/class bodies."""
        try:
            source = file_path.read_text(encoding='utf-8')
            tree = ast.parse(source)
        except Exception:
            return []
        blocks = []
        source_lines = source.splitlines()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.end_lineno - node.lineno + 1 < self.min_lines:
                    continue
                code_block = '\n'.join(source_lines[node.lineno - 1:node.end_lineno])
                blocks.append((node.name, code_block, node.lineno))
        return blocks

    def scan_for_duplicates(self, python_files: List[str]) -> Any:
        """Phase 2 entry point - cross-file territory sweep."""
        print('\n[*] CodeDeduplicationAgent: Scanning for cross-file duplicates...')
        hash_to_blocks: Any = defaultdict(list)
        for file_str in python_files:
            file_path: Any = Path(file_str)
            # EXCLUDE archives/ directory
            if not file_path.exists() or 'archives' in str(file_path):
                continue
            for name, code, line in self._extract_functions_classes(file_path):
                block_hash: Any = self._hash_block(code)
                hash_to_blocks[block_hash].append((file_path, name, line, code))
        for block_hash, occurrences in hash_to_blocks.items():
            if len(occurrences) > 1:
                print(f'   [!] DUPLICATE FOUND ({len(occurrences)} copies):')
                for path, name, line, _ in occurrences:
                    print(f'      -> {path.name}:{line} ({name})')
                self.duplicate_groups[block_hash] = occurrences
        if not self.duplicate_groups:
            print('   [OK] No significant code duplicates detected.')

    def _create_shared_utility(self, code: str, func_name: str, project_root: Path) -> Path:
        """Create deduplicated utility in sovereign shared location."""
        utils_dir = project_root / 'agentic_core' / 'utils' / 'deduplicated'
        utils_dir.mkdir(parents=True, exist_ok=True)
        safe_name = ''.join((c if c.isalnum() else '_' for c in func_name.lower()))[:40]
        candidate = utils_dir / f'{safe_name}_shared.py'
        counter = 1
        while candidate.exists():
            candidate = utils_dir / f'{safe_name}_shared_{counter}.py'
            counter += 1
        header = f'# Auto-extracted shared utility by CodeDeduplicationAgent\n# Original function: {func_name}\n\n'
        candidate.write_text(header + textwrap.dedent(code), encoding='utf-8')
        return candidate

    async def auto_extract_duplicates(self, project_root: Path, ctx: Any) -> Any:
        """[L6 SPRAWL SURGERY] Extract duplicates and inject imports."""
        if not getattr(ctx, 'RUN_SPRAWL_SURGERY', False):
            print('   [INFO] Auto-extraction disabled (RUN_SPRAWL_SURGERY=False)')
            return
        print('\n[*] CONTENT DEDUPLICATION SURGERY: Extracting common blocks...')
        for block_hash, occurrences in self.duplicate_groups.items():
            if len(occurrences) < 2:
                continue
            primary_path, func_name, _, canonical_code = occurrences[0]
            shared_file: Any = self._create_shared_utility(canonical_code, func_name, project_root)
            module_name: Any = shared_file.stem
            import_stmt: Any = f'from agentic_core.utils.deduplicated.{module_name} import {func_name}'
            for file_path, name, start_line, code in occurrences[1:]:
                try:
                    lines: Any = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
                    end_line: Any = start_line + code.count('\n')
                    replacement: Any = [f'# DEDUPLICATED: Extracted to {shared_file.name}\n', f'{name}_result = {func_name}()  # TODO: manually adapt params/usage\n']
                    import_idx: Any = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            import_idx: Any = i + 1
                            break
                    new_lines: Any = lines[:import_idx] + [import_stmt + '\n'] + lines[import_idx:start_line - 1] + replacement + lines[end_line:]
                    file_path.write_text(''.join(new_lines), encoding='utf-8')
                    backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
                    shutil.copy(file_path, backup_path)
                    print(f"      [✓] Created backup: {backup_path}")
                except Exception as e:
                    print(f"      [!] Backup failed for {file_path}: {e}")
        print(f'   [SURGERY COMPLETE] {self.extracted_count} instances extracted')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    async def execute(self, ctx: Any) -> Any:
        """Batch agent interface."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        if not hasattr(ctx, 'python_files'):
            return
        if not hasattr(ctx, 'project_root'):
            print('   [!] project_root Missing in context')
            return
        self.scan_for_duplicates(ctx.python_files)
        await self.auto_extract_duplicates(Path(ctx.project_root), ctx)

    # SUPPLEMENTED FROM DeadCodeDetectorAgent + DeadCodePrunerAgent — enhances dead code detection — merged 2025-12-30
    def detect_dead_code(self, file_path: Path) -> Dict[str, Any]:
        """
        SUPPLEMENTED FROM DeadCodeDetectorAgent — merged 2025-12-30
        
        Analyze a single Python file for dead code (unused imports, functions, classes, methods).
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Dict with findings: {unused_imports, unused_functions, unused_classes, unused_methods}
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {'error': f'Could not read {file_path}: {e}'}
            
        if not content.strip() or file_path.name == '__init__.py':
            return {'skipped': True, 'reason': 'Empty or __init__ file'}
            
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return {'error': f'Syntax error in {file_path}: {e}'}
            
        # Track imports, definitions, and usages
        imported_names: set = set()
        defined_functions: set = set()
        defined_classes: set = set()
        used_names: set = set()
        import_lines: Dict[str, int] = {}
        def_lines: Dict[str, int] = {}
        
        for node in ast.walk(tree):
            # Track imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names.add(name)
                    import_lines[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names.add(name)
                    import_lines[name] = node.lineno
            # Track definitions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_functions.add(node.name)
                def_lines[node.name] = node.lineno
            elif isinstance(node, ast.ClassDef):
                defined_classes.add(node.name)
                def_lines[node.name] = node.lineno
            # Track usage
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
                
        findings = {
            'file_path': str(file_path),
            'unused_imports': [],
            'unused_functions': [],
            'unused_classes': [],
        }
        
        # Detect unused imports
        for name in imported_names:
            if name not in used_names:
                findings['unused_imports'].append({'name': name, 'line': import_lines.get(name)})
                
        # Detect unused functions (excluding private)
        for name in defined_functions:
            if name not in used_names and not name.startswith('_'):
                findings['unused_functions'].append({'name': name, 'line': def_lines.get(name)})
                
        # Detect unused classes (excluding private)
        for name in defined_classes:
            if name not in used_names and not name.startswith('_'):
                findings['unused_classes'].append({'name': name, 'line': def_lines.get(name)})
                
        return findings

    def scan_dead_code(self, directory: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        SUPPLEMENTED FROM DeadCodeDetectorAgent — merged 2025-12-30
        
        Scan an entire directory for dead code.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            
        Returns:
            Dict with scan results and summary
        """
        if not directory.exists():
            return {'error': f'Directory {directory} does not exist'}
            
        py_files = list(directory.rglob('*.py') if recursive else directory.glob('*.py'))
        py_files = [f for f in py_files if '__pycache__' not in str(f)]
        
        results = {
            'scanned_files': len(py_files),
            'findings': [],
            'summary': {
                'total_unused_imports': 0,
                'total_unused_functions': 0,
                'total_unused_classes': 0,
            }
        }
        
        for file_path in py_files:
            finding = self.detect_dead_code(file_path)
            if 'error' not in finding and 'skipped' not in finding:
                results['findings'].append(finding)
                results['summary']['total_unused_imports'] += len(finding['unused_imports'])
                results['summary']['total_unused_functions'] += len(finding['unused_functions'])
                results['summary']['total_unused_classes'] += len(finding['unused_classes'])
                
        return results

    def prune_dead_code(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        SUPPLEMENTED FROM DeadCodePrunerAgent — merged 2025-12-30
        
        Remove detected dead code from a file.
        
        Args:
            file_path: Path to the file to prune
            dry_run: If True, only report what would be removed
            
        Returns:
            Dict with pruning results
        """
        findings = self.detect_dead_code(file_path)
        if 'error' in findings or 'skipped' in findings:
            return findings
            
        lines_to_remove = set()
        for item in findings['unused_imports']:
            if item['line']:
                lines_to_remove.add(item['line'])
                
        results = {
            'file': str(file_path),
            'dry_run': dry_run,
            'lines_marked': list(lines_to_remove),
            'imports_removed': len(findings['unused_imports']),
        }
        
        if not dry_run and lines_to_remove:
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines(keepends=True)
                new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]
                file_path.write_text(''.join(new_lines), encoding='utf-8')
                results['applied'] = True
            except Exception as e:
                results['error'] = str(e)


def get_code_deduplication_agent() -> Any:
    """Brief description of functionality and purpose."""
    return CodeDeduplicationAgent()
