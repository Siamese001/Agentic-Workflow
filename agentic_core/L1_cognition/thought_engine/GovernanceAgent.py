"""
L6 Sovereign Code Graph & Governance Infrastructure

Implements the DependencyGraph class and impact radius analysis
for calculating blast radius of file modifications.

Features:
- AST-based dependency extraction
- Impact radius calculation
- Architecture governance laws enforcement
- Blast radius visualization
"""
import ast
import glob
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
logger: Any = logging.getLogger(__name__)

class dependency_graph:
    """
    Builds a directed graph of imports and class hierarchies.

    Used for calculating blast radius when files are modified,
    ensuring comprehensive impact analysis for governance.
    """

    def __init__(self):
        """Initialize the dependency graph."""
        self.graph: Dict[str, Dict[str, List[str]]] = {}
        self.reverse_graph: Dict[str, List[str]] = {}
        self.class_map: Dict[str, str] = {}
        self.module_map: Dict[str, str] = {}
        self._built: bool = False

    def build(self, files: List[str], root_dir: str=None) -> Any:
        """
        Build the dependency graph from a list of Python files.

        Args:
            files: List of Python file paths
            root_dir: Root directory for relative path calculation
        """
        LOGGER.info(f'🕸️ Building Holistic Code Graph from {len(files)} files...')
        if root_dir:
            root_path: Any = Path(root_dir).resolve()
        else:
            root_path: Any = Path.cwd()
        self.graph.clear()
        self.reverse_graph.clear()
        self.class_map.clear()
        self.module_map.clear()
        for file_path in files:
            file_path: Any = str(Path(file_path).relative_to(root_path))
            self.graph[file_path] = {'imports': [], 'from_imports': [], 'classes': [], 'functions': [], 'dependencies': []}
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]['imports'].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]['from_imports'].append({'module': node.module, 'names': [n.name for n in node.names]})
                    elif isinstance(node, ast.ClassDef):
                        self.graph[file_path]['classes'].append(node.name)
                        self.class_map[node.name] = file_path
                    elif isinstance(node, ast.FunctionDef):
                        self.graph[file_path]['functions'].append(node.name)
                module_name: Any = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                self.module_map[module_name] = file_path
            except SyntaxError as e:
                LOGGER.warning(f'Syntax error in {file_path}: {e}')
            except Exception as e:
                LOGGER.error(f'Error parsing {file_path}: {e}')
        self._build_reverse_index()
        self._calculate_dependencies()
        self._built = True
        LOGGER.info(f'[OK] Code graph built: {len(self.graph)} files, {len(self.class_map)} classes')

    def _build_reverse_index(self):
        """Build reverse lookup indices."""
        for file_path, data in self.graph.items():
            for imp in data['imports']:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file_path)
            for from_imp in data['from_imports']:
                module = from_imp['module']
                if module not in self.reverse_graph:
                    self.reverse_graph[module] = []
                self.reverse_graph[module].append(file_path)

    def _calculate_dependencies(self):
        """Calculate transitive dependencies for each file."""
        for file_path in self.graph:
            deps = set()
            for imp in self.graph[file_path]['imports']:
                if imp in self.module_map:
                    deps.add(self.module_map[imp])
            for from_imp in self.graph[file_path]['from_imports']:
                module = from_imp['module']
                if module in self.module_map:
                    deps.add(self.module_map[module])
            self.graph[file_path]['dependencies'] = list(deps)

    def get_impact_radius(self, file_path: str, include_transitive: bool=True) -> List[str]:
        """
        Get files impacted by modifications to the given file.

        Args:
            file_path: Path to the modified file
            include_transitive: Whether to include transitive dependencies

        Returns:
            List of file paths that may be impacted
        """
        if not self._built:
            LOGGER.warning('Dependency graph not built yet')
            return []
        impacted: Any = set()
        module_name: Any = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        for key, dependents in self.reverse_graph.items():
            if key.startswith(module_name + '.'):
                impacted.update(dependents)
        classes: Any = self.graph.get(file_path, {}).get('classes', [])
        for class_name in classes:
            if class_name in self.reverse_graph:
                impacted.update(self.reverse_graph[class_name])
        if include_transitive:
            to_check: Any = list(impacted)
            checked: Any = set()
            while to_check:
                current: Any = to_check.pop()
                if current in checked:
                    continue
                checked.add(current)
                current_module: Any = current.replace('/', '.').replace('\\', '.').replace('.py', '')
                if current_module in self.reverse_graph:
                    for dependent in self.reverse_graph[current_module]:
                        if dependent not in impacted:
                            impacted.add(dependent)
                            to_check.append(dependent)
        return sorted(list(impacted))

    def get_dependency_tree(self, file_path: str) -> Dict[str, List[str]]:
        """
        Get the full dependency tree for a file.

        Returns:
            Dictionary with 'direct' and 'transitive' dependencies
        """
        if not self._built:
            return {'direct': [], 'transitive': []}
        direct: Any = self.graph.get(file_path, {}).get('dependencies', [])
        transitive: Any = set()
        to_check: Any = list(direct)
        checked: Any = set()
        while to_check:
            current: Any = to_check.pop()
            if current in checked or current == file_path:
                continue
            checked.add(current)
            transitive.add(current)
            current_deps: Any = self.graph.get(current, {}).get('dependencies', [])
            for dep in current_deps:
                if dep not in checked and dep != file_path:
                    to_check.append(dep)
        return {'direct': direct, 'transitive': sorted(list(transitive))}

    def visualize_graph(self, output_file: str=None) -> str:
        """
        Generate a DOT format visualization of the graph.

        Args:
            output_file: Optional file to save the DOT graph

        Returns:
            DOT format string
        """
        dot: Any = ['digraph DependencyGraph {']
        dot.append('  rankdir=LR;')
        dot.append('  node [shape=box];')
        for file_path in self.graph:
            safe_name: Any = file_path.replace('/', '_').replace('\\', '_').replace('.py', '')
            dot.append(f'  "{safe_name}" [label="{file_path}"];')
        for file_path, data in self.graph.items():
            from_name: Any = file_path.replace('/', '_').replace('\\', '_').replace('.py', '')
            for dep in data['dependencies']:
                to_name: Any = dep.replace('/', '_').replace('\\', '_').replace('.py', '')
                dot.append(f'  "{from_name}" -> "{to_name}";')
        dot.append('}')
        dot_str: Any = '\n'.join(dot)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(dot_str)
            LOGGER.info(f'Graph visualization saved to {output_file}')
        return dot_str

# NAMING CANON COMPLIANCE — renamed to GovernanceAgent for discovery and sovereignty — 2025-12-30
class GovernanceAgent:
    """
    Enforces architectural governance laws and constraints.

    Implements the Three Laws:
    1. Law of The Void (Root hygiene)
    2. Law of Depth (Depth 3-5)
    3. Law of Impact (Blast radius awareness)
    """

    def __init__(self, root_dir: str=None):
        """
        Initialize the ArchitectureGovernor.
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.logger = logging.getLogger(__name__)
        self.dependency_graph = DependencyGraph()
        from agentic_core.config.blueprint_sovereign.structure_blueprint import ROOT_PROTECTED_FILES, SOVEREIGN_REGISTRY
        self.ALLOWED_ROOT_FILES = ROOT_PROTECTED_FILES
        self.ALLOWED_ROOT_FOLDERS = set(SOVEREIGN_REGISTRY.keys())
        self.DEPTH_MAP = {root: cfg['depth'] for root, cfg in SOVEREIGN_REGISTRY.items()}
        self.MAX_COMPLEXITY = 10
        self.MAX_FUNC_LINES = 50
        self.MAX_NESTING_SPACES = 40
        self.stats = {'files_checked': 0, 'violations_found': 0, 'files_sanitized': 0}
        self.sovereign_dirs = {'agentic_core', 'schemas', 'scripts', 'docs', 'tests', 'config', 'data', 'cache', 'observability', '.git', '__pycache__', '.pytest_cache', '.tox', 'venv', '.venv', 'node_modules', '.idea', '.vscode', 'dist', 'build', 'coverage', '.github', 'htmlcov', '.mypy_cache', '.coverage', 'eggs', '.eggs', '*.egg-info'}
        self.MAX_FILE_LINES = 200

    def build_graph(self, file_patterns: List[str]=['**/*.py']) -> Any:
        """
        Build the dependency graph for the project.

        Args:
            file_patterns: Glob patterns for Python files
        """
        all_files: Any = []
        for pattern in file_patterns:
            all_files.extend(glob.glob(pattern, recursive=True))
        all_files: Any = list(set(all_files))
        self.dependency_graph.build(all_files, str(self.root_dir))

    def check_root_hygiene(self, auto_sanitize: bool=True) -> List[str]:
        """
        Check Law of The Void - root directory hygiene.

        Args:
            auto_sanitize: Whether to automatically move/delete violations

        Returns:
            List of violations
        """
        violations: Any = []
        sanitized: Any = []
        for item in self.root_dir.iterdir():
            if item.is_file():
                if item.name not in self.ALLOWED_ROOT_FILES:
                    violations.append(f'Unauthorized file at root: {item.name}')
                    if auto_sanitize:
                        action: Any = self._sanitize_root_file(item)
                        sanitized.append(f'{item.name} -> {action}')
            if item.is_dir():
                if not item.name.startswith('.') and item.name not in self.ALLOWED_ROOT_FOLDERS:
                    violations.append(f'Unauthorized directory at root: {item.name}')
        if sanitized:
            LOGGER.info(f'Root sanitation completed: {len(sanitized)} items processed')
            for action in sanitized:
                LOGGER.info(f'  {action}')
        return violations

    def _sanitize_root_file(self, file_path: Path) -> str:
        """
        Sanitize an unauthorized file in the root directory.

        Args:
            file_path: Path to the unauthorized file

        Returns:
            Action taken
        """
        scripts_dir = self.root_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        noise_patterns = ['temp', 'tmp', 'debug', 'test', '.log', '.tmp', '.bak']
        is_noise = any((pattern in file_path.name.lower() for pattern in noise_patterns))
        if is_noise:
            try:
                file_path.unlink()
                return 'DELETED (noise)'
            except Exception as e:
                LOGGER.error(f'Failed to delete {file_path}: {e}')
                return 'FAILED to delete'
        else:
            try:
                target = scripts_dir / file_path.name
                counter = 1
                while target.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    target = scripts_dir / f'{stem}_{counter}{suffix}'
                    counter += 1
                shutil.move(str(file_path), str(target))
                return f'MOVED to scripts/{target.name}'
            except Exception as e:
                LOGGER.error(f'Failed to move {file_path}: {e}')
                return 'FAILED to move'

    def check_depth_law(self, file_path: str) -> Optional[str]:
        """
        Check Law of Depth - ensure proper nesting depth.
        [SSOT] Uses DEPTH_MAP derived from SOVEREIGN_REGISTRY for per-root depth enforcement.

        Args:
            file_path: Path to check
        Returns:
            Violation message or None
        """
        path: Any = Path(file_path)
        for part in path.parts:
            if part in self.sovereign_dirs:
                return None
        if len(path.parts) < 1:
            return None
        root_folder: Any = path.parts[0]
        required_depth: Any = self.DEPTH_MAP.get(root_folder)
        if required_depth is None:
            return None
        depth: Any = len(path.parts) - 1
        if depth != required_depth:
            reason: Any = 'SHALLOW' if depth < required_depth else 'DEEP'
            return f'{reason} Violation: {file_path} at depth {depth} (required: {required_depth})'
        return None

    def check_atomicity_law(self, file_path: str) -> Optional[str]:
        """
        Check Law of Atomicity - ensure files don't exceed line limit.

        Args:
            file_path: Path to check

        Returns:
            Violation message or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines: Any = f.readlines()
            line_count: Any = len(lines)
            if line_count > self.MAX_FILE_LINES:
                return f'Violation: {file_path} has {line_count} lines (max allowed: {self.MAX_FILE_LINES}) - SPLIT required'
            return None
        except Exception as e:
            LOGGER.error(f'Error checking file density for {file_path}: {e}')
            return f'Error: Could not check {file_path}'

    def enforce_depth_law(self, file_path: str) -> Optional[str]:
        """
        Enforce Law of Depth by moving file to correct location.

        Args:
            file_path: Path to enforce

        Returns:
            New path if moved, None if already compliant
        """
        path: Any = Path(file_path)
        violation: Any = self.check_depth_law(str(path))
        if not violation:
            return None
        for part in path.parts:
            if part in self.sovereign_dirs:
                return None
        if 'too shallow' in violation.lower():
            target_dir: Any = self.root_dir / 'agentic_core' / 'L1_cognition'
            target_dir.mkdir(parents=True, exist_ok=True)
            target: Any = target_dir / path.name
        else:
            target_dir: Any = self.root_dir / 'scripts'
            target_dir.mkdir(exist_ok=True)
            target: Any = target_dir / path.name
        try:
            counter: Any = 1
            while target.exists():
                stem: Any = path.stem
                suffix: Any = path.suffix
                target: Any = target_dir / f'{stem}_{counter}{suffix}'
                counter += 1
            shutil.move(str(path), str(target))
            LOGGER.info(f'Moved {file_path} to {target} (depth enforcement)')
            return str(target)
        except Exception as e:
            LOGGER.error(f'Failed to move {file_path}: {e}')
            return None

    def _calculate_mccabe(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity for an AST node.

        Args:
            node: AST node to analyze

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _check_nesting_depth(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Check for excessive nesting depth in a file.

        Args:
            file_path: Path to the file to check

        Returns:
            List of nesting violations
        """
        violations = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line_num, line in enumerate(lines, 1):
                if line.startswith(' '):
                    spaces = len(line) - len(line.lstrip(' '))
                    if spaces > self.MAX_NESTING_SPACES:
                        violations.append({'line': line_num, 'spaces': spaces, 'content': line.strip()[:100], 'message': f'Line {line_num}: Excessive nesting ({spaces} spaces > {self.MAX_NESTING_SPACES})'})
        except Exception as e:
            LOGGER.error(f'Error checking nesting depth in {file_path}: {e}')
        return violations

    def check_complexity(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Check complexity violations in a file.

        Args:
            file_path: Path to the file to check

        Returns:
            List of complexity violations
        """
        violations: Any = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content: Any = f.read()
            tree: Any = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity: Any = self._calculate_mccabe(node)
                    func_lines: Any = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                    if complexity > self.MAX_COMPLEXITY:
                        violations.append({'type': 'complexity', 'function': node.name, 'line': node.lineno, 'complexity': complexity, 'threshold': self.MAX_COMPLEXITY, 'message': f"Function '{node.name}' at line {node.lineno}: Complexity {complexity} > {self.MAX_COMPLEXITY}"})
                    if func_lines > self.MAX_FUNC_LINES:
                        violations.append({'type': 'length', 'function': node.name, 'line': node.lineno, 'lines': func_lines, 'threshold': self.MAX_FUNC_LINES, 'message': f"Function '{node.name}' at line {node.lineno}: {func_lines} lines > {self.MAX_FUNC_LINES}"})
        except SyntaxError as e:
            violations.append({'type': 'syntax', 'message': f'Syntax error in {file_path}: {e}'})
        except Exception as e:
            LOGGER.error(f'Error checking complexity in {file_path}: {e}')
        nesting_violations: Any = self._check_nesting_depth(file_path)
        for violation in nesting_violations:
            violation['type'] = 'nesting'
            violations.append(violation)
        return violations

    def get_blast_radius(self, modified_files: List[str]) -> Dict[str, Any]:
        """
        Calculate the blast radius for modified files.

        Args:
            modified_files: List of modified file paths

        Returns:
            Dictionary with impact analysis
        """
        if not self.dependency_graph._built:
            self.build_graph()
        total_impacted: Any = set()
        file_impacts: Any = {}
        for file_path in modified_files:
            impacted: Any = self.dependency_graph.get_impact_radius(file_path)
            total_impacted.update(impacted)
            file_impacts[file_path] = {'direct_count': len(impacted), 'impacted_files': impacted}
        return {'modified_count': len(modified_files), 'total_impacted': len(total_impacted), 'blast_radius': sorted(list(total_impacted)), 'file_details': file_impacts}

    def validate_architecture(self, file_paths: List[str]=None, enforce: bool=False) -> Dict[str, Any]:
        """
        Perform full architecture validation.

        Args:
            file_paths: Specific files to validate (all if None)
            enforce: Whether to automatically fix violations

        Returns:
            Validation report
        """
        report: Any = {'root_violations': [], 'depth_violations': [], 'atomicity_violations': [], 'complexity_violations': [], 'enforced_actions': [], 'blast_radius': None, 'overall_status': 'PASS'}
        report['root_violations'] = self.check_root_hygiene(auto_sanitize=enforce)
        if file_paths:
            for file_path in file_paths:
                violation: Any = self.check_depth_law(file_path)
                if violation:
                    report['depth_violations'].append(violation)
                    if enforce:
                        new_path: Any = self.enforce_depth_law(file_path)
                        if new_path:
                            report['enforced_actions'].append(f'Moved {file_path} to {new_path}')
                violation: Any = self.check_atomicity_law(file_path)
                if violation:
                    report['atomicity_violations'].append(violation)
                    complexity_violations: Any = self.check_complexity(file_path)
                    if complexity_violations:
                        report['complexity_violations'].extend(complexity_violations)
        if file_paths:
            report['blast_radius'] = self.get_blast_radius(file_paths)
        if report['root_violations'] or report['depth_violations'] or report['atomicity_violations'] or report['complexity_violations']:
            report['overall_status'] = 'FAIL'
        return report

def create_architecture_governor(root_dir: str=None) -> ArchitectureGovernor:
    """Create an architecture governor instance."""
    return ArchitectureGovernor(root_dir)
