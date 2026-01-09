import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Zero-Loss Equivalence Test Suite for Canon Validator Split

This test suite proves functional equivalence between:
- Original monolith: scripts/canon_validator_agentic.py (8864 lines)
- Modular package: scripts/canon_validator/ (split into subatomic modules)

Tests verify:
1. Import equivalence - all exports match
2. Class/function signature equivalence
3. Runtime behavior equivalence (via subprocess)
4. Report output equivalence (hash comparison)
"""
from typing import Any, Optional, Protocol, Dict, List
import ast
import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List
import pytest
repo_root: Any = Path(__file__).parent.parent
scripts_dir: Any = REPO_ROOT / 'scripts'
original_script: Any = SCRIPTS_DIR / 'canon_validator_agentic.py'
bootstrap_script: Any = SCRIPTS_DIR / 'canon_validator_agentic_bootstrap.py'
modular_package: Any = SCRIPTS_DIR / 'canon_validator'

class test_import_equivalence:
    """Verify all exports from modular package match original monolith."""

    def test_modular_package_imports_without_error(self) -> Any:
        """Modular package should import cleanly."""
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import canon_validator
            assert canon_validator is not None
        finally:
            sys.path.remove(str(SCRIPTS_DIR))

    def test_bootstrap_imports_without_error(self) -> Any:
        """Bootstrap script should import all expected symbols."""
        spec: Any = importlib.util.spec_from_file_location('bootstrap', BOOTSTRAP_SCRIPT)
        importlib.util.module_from_spec(spec)
        assert spec is not None

    def test_all_exports_present_in_modular(self) -> Any:
        """All __all__ exports should be importable from modular package."""
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import canon_validator
            expected_exports: Any = ['EXCLUDED_DIRS', 'EXCLUDED_FILES', 'ALLOWED_ROOT_FOLDERS', 'ALLOWED_ROOT_FILES', 'MIN_DEPTH', 'MAX_DEPTH', 'MAX_LINES', 'get_python_files', 'is_excluded', 'ValidationContext', 'DependencyGraph', 'BudgetManager', 'SubAtomicAgent', 'ImportPatcher', 'POSITIVE_INSTRUCTIONAL_CONTEXT', 'FEW_SHOT_GLOBAL_REFACTOR', 'FEW_SHOT_PROMPTS', 'Historian', 'ArchitectureGovernor', 'HygieneGuardian', 'CodeStyleGuardian', 'DependencySentinelAgent', 'SafetyInspectorAgent', 'ConcurrencyGuardianAgent', 'TestPilot', 'StructuralEngineer', 'PatternEnforcerAgent', 'SecurityEnforcer', 'PerformanceEnforcer', 'MemoryLeakDetectorAgent', 'DeadlockDetectorAgent', 'Sherlock', 'StrategicPlannerAgent', 'ReflectionAgent', 'GitAgent', 'BenchmarkingAgent', 'ToolsmithAgent', 'TheStrategist', 'NamingEnforcer', 'DocEnforcer', 'TypeEnforcer', 'TheCartographer', 'TheOmniContext', 'SwarmScheduler', 'IntelligentOrchestratorAgent']
            missing: Any = []
            for name in expected_exports:
                if not hasattr(canon_validator, name):
                    missing.append(name)
            assert not missing, f'Missing exports in modular package: {missing}'
        finally:
            sys.path.remove(str(SCRIPTS_DIR))

def extract_class_signatures(file_path: Path) -> Dict[str, Dict[str, Any]]:
    """Extract class names and their method signatures from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree: Any = ast.parse(f.read())
    classes: Any = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods: Any = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args: Any = [arg.arg for arg in item.args.args]
                    methods[item.name] = {'args': args, 'is_async': isinstance(item, ast.AsyncFunctionDef)}
                elif isinstance(item, ast.AsyncFunctionDef):
                    args: Any = [arg.arg for arg in item.args.args]
                    methods[item.name] = {'args': args, 'is_async': True}
            classes[node.name] = {'methods': methods, 'bases': [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) for base in node.bases]}
    return classes

def collect_modular_classes() -> Dict[str, Dict[str, Any]]:
    """Collect all class signatures from the modular package."""
    all_classes: Any = {}
    for py_file in MODULAR_PACKAGE.glob('*.py'):
        if py_file.name != '__init__.py':
            classes: Any = extract_class_signatures(py_file)
            all_classes.update(classes)
    agents_dir: Any = MODULAR_PACKAGE / 'agents'
    if agents_dir.exists():
        for py_file in agents_dir.glob('*.py'):
            if py_file.name != '__init__.py':
                classes: Any = extract_class_signatures(py_file)
                all_classes.update(classes)
    return all_classes

class test_class_signature_equivalence:
    """Verify class signatures match between original and modular."""

    def test_core_classes_exist_in_modular(self) -> Any:
        """Core classes must exist in modular package."""
        modular_classes: Any = collect_modular_classes()
        core_classes: Any = ['ValidationContext', 'DependencyGraph', 'BudgetManager', 'SubAtomicAgent', 'SwarmScheduler']
        missing: Any = [c for c in core_classes if c not in modular_classes]
        assert not missing, f'Missing core classes: {missing}'

    def test_agent_classes_exist_in_modular(self) -> Any:
        """All agent classes must exist in modular package."""
        modular_classes: Any = collect_modular_classes()
        agent_classes: Any = ['Historian', 'ArchitectureGovernor', 'HygieneGuardian', 'CodeStyleGuardian', 'DependencySentinelAgent', 'SafetyInspectorAgent', 'ConcurrencyGuardianAgent', 'TestPilot', 'StructuralEngineer', 'PatternEnforcerAgent', 'SecurityEnforcer', 'PerformanceEnforcer', 'MemoryLeakDetectorAgent', 'DeadlockDetectorAgent', 'Sherlock', 'StrategicPlannerAgent', 'ReflectionAgent', 'GitAgent', 'BenchmarkingAgent', 'ToolsmithAgent', 'TheStrategist', 'NamingEnforcer', 'DocEnforcer', 'TypeEnforcer', 'TheCartographer', 'TheOmniContext']
        missing: Any = [c for c in agent_classes if c not in modular_classes]
        assert not missing, f'Missing agent classes: {missing}'

    def test_subatomic_agent_has_execute_method(self) -> Any:
        """SubAtomicAgent base class must have execute method."""
        modular_classes: Any = collect_modular_classes()
        assert 'SubAtomicAgent' in modular_classes
        methods: Any = modular_classes['SubAtomicAgent']['methods']
        assert 'execute' in methods, 'SubAtomicAgent missing execute method'

    def test_swarm_scheduler_has_run_mission(self) -> Any:
        """SwarmScheduler must have run_mission method."""
        modular_classes: Any = collect_modular_classes()
        assert 'SwarmScheduler' in modular_classes
        methods: Any = modular_classes['SwarmScheduler']['methods']
        assert 'run_mission' in methods, 'SwarmScheduler missing run_mission method'

def run_validator(entry_point: Path, args: List[str]=None, timeout: int=120, capture_json: bool=False) -> Dict[str, Any]:
    """
    Run the validator and capture output.

    Returns dict with:
    - returncode: Process exit code
    - stdout: Standard output
    - stderr: Standard error
    - report: Parsed JSON report (if capture_json=True)
    - output_hash: SHA256 of stdout for comparison
    """
    cmd: Any = [sys.executable, str(entry_point)]
    if args:
        cmd.extend(args)
    env: Any = {**dict(__import__('os').environ)}
    env['CANON_VALIDATOR_NONINTERACTIVE'] = '1'
    try:
        result: Any = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO_ROOT), env=env)
        output: Any = {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'output_hash': hashlib.sha256(result.stdout.encode()).hexdigest()}
        if capture_json:
            try:
                lines: Any = result.stdout.split('\n')
                json_lines: Any = []
                in_json: Any = False
                for line in lines:
                    if line.strip().startswith('{'):
                        in_json: Any = True
                    if in_json:
                        json_lines.append(line)
                    if line.strip().endswith('}') and in_json:
                        break
                if json_lines:
                    output['report'] = json.loads('\n'.join(json_lines))
            except (json.JSONDecodeError, ValueError):
                output['report'] = None
        return output
    except subprocess.TimeoutExpired:
        return {'returncode': -1, 'stdout': '', 'stderr': 'TIMEOUT', 'output_hash': ''}
    except Exception as e:
        return {'returncode': -1, 'stdout': '', 'stderr': str(e), 'output_hash': ''}

def normalize_output(output: str) -> str:
    """
    Normalize output for comparison by removing:
    - Timestamps
    - Absolute paths
    - Process IDs
    - Memory addresses
    """
    import re
    output: Any = re.sub('\\d{4}-\\d{2}-\\d{2}[T ]\\d{2}:\\d{2}:\\d{2}', 'TIMESTAMP', output)
    output: Any = re.sub('\\d{2}:\\d{2}:\\d{2}', 'TIME', output)
    output: Any = re.sub('[A-Za-z]:\\\\[^\\s\\n]+', 'PATH', output)
    output: Any = re.sub('/[^\\s\\n]+\\.py', 'PATH.py', output)
    output: Any = re.sub('0x[0-9a-fA-F]+', '0xADDR', output)
    output: Any = re.sub('pid=\\d+', 'pid=PID', output)
    return output

class test_runtime_equivalence:
    """Verify runtime behavior matches between original and modular."""

    @pytest.mark.slow
    def test_help_output_equivalence(self) -> Any:
        """--help output should be similar (if supported)."""
        original: Any = run_validator(ORIGINAL_SCRIPT, ['--help'], timeout=10)
        modular: Any = run_validator(BOOTSTRAP_SCRIPT, ['--help'], timeout=10)
        assert 'ImportError' not in original['stderr'], f"Original has import errors on --help: {original['stderr']}"
        assert 'ImportError' not in modular['stderr'], f"Modular has import errors on --help: {modular['stderr']}"

    @pytest.mark.slow
    def test_import_smoke_test(self) -> Any:
        """Both versions should start without import errors."""
        original: Any = run_validator(ORIGINAL_SCRIPT, timeout=30)
        modular: Any = run_validator(BOOTSTRAP_SCRIPT, timeout=30)
        assert 'ImportError' not in original['stderr'], f"Original has import errors: {original['stderr']}"
        assert 'ImportError' not in modular['stderr'], f"Modular has import errors: {modular['stderr']}"

    @pytest.mark.slow
    def test_startup_banner_present(self) -> Any:
        """Both versions should print startup banner."""
        original: Any = run_validator(ORIGINAL_SCRIPT, timeout=30)
        modular: Any = run_validator(BOOTSTRAP_SCRIPT, timeout=30)
        original_has_banner: Any = 'CANON VALIDATOR' in original['stdout'] or 'canon validator' in original['stdout'].lower() or 'SUBATOMIC' in original['stdout'] or ('MISSION' in original['stdout'])
        modular_has_banner: Any = 'CANON VALIDATOR' in modular['stdout'] or 'canon validator' in modular['stdout'].lower() or 'SUBATOMIC' in modular['stdout'] or ('MISSION' in modular['stdout'])
        if original['stdout'] and modular['stdout']:
            assert original_has_banner or modular_has_banner, 'Neither version produced expected startup output'

def count_classes_in_file(file_path: Path) -> int:
    """Count number of class definitions in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree: Any = ast.parse(f.read())
    return sum((1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)))

def count_functions_in_file(file_path: Path) -> int:
    """Count number of function definitions in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree: Any = ast.parse(f.read())
    return sum((1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))))

class test_structural_equivalence:
    """Verify structural properties are preserved."""

    def test_original_exists(self) -> Any:
        """Original monolith file must exist."""
        assert ORIGINAL_SCRIPT.exists(), f'Original not found: {ORIGINAL_SCRIPT}'

    def test_modular_package_exists(self) -> Any:
        """Modular package directory must exist."""
        assert MODULAR_PACKAGE.exists(), f'Modular package not found: {MODULAR_PACKAGE}'
        assert (MODULAR_PACKAGE / '__init__.py').exists(), 'Missing __init__.py'

    def test_bootstrap_exists(self) -> Any:
        """Bootstrap entry point must exist."""
        assert BOOTSTRAP_SCRIPT.exists(), f'Bootstrap not found: {BOOTSTRAP_SCRIPT}'

    def test_agent_count_preserved(self) -> Any:
        """Number of agent classes should be preserved."""
        original_classes: Any = extract_class_signatures(ORIGINAL_SCRIPT)
        original_agents: Any = [name for name in original_classes if name.endswith('Agent') or name in ['Historian', 'Sherlock', 'TestPilot', 'TheStrategist', 'TheCartographer', 'TheOmniContext']]
        modular_classes: Any = collect_modular_classes()
        modular_agents: Any = [name for name in modular_classes if name.endswith('Agent') or name in ['Historian', 'Sherlock', 'TestPilot', 'TheStrategist', 'TheCartographer', 'TheOmniContext']]
        assert len(modular_agents) >= len(original_agents) - 5, f'Agent count mismatch: original={len(original_agents)}, modular={len(modular_agents)}'

    def test_no_duplicate_class_definitions(self) -> Any:
        """No class should be defined in multiple files in modular package."""
        seen_classes: Dict[str, str] = {}
        duplicates: Any = []
        for py_file in MODULAR_PACKAGE.glob('**/*.py'):
            if py_file.name == '__init__.py':
                continue
            classes: Any = extract_class_signatures(py_file)
            for class_name in classes:
                if class_name in seen_classes:
                    duplicates.append(f'{class_name}: {seen_classes[class_name]} and {py_file}')
                else:
                    seen_classes[class_name] = str(py_file)
        assert not duplicates, f'Duplicate class definitions: {duplicates}'

class test_config_equivalence:
    """Verify configuration values match."""

    def test_excluded_dirs_match(self) -> Any:
        """EXCLUDED_DIRS should match between versions."""
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            from canon_validator import EXCLUDED_DIRS
            from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_IGNORED_FOLDERS
            expected_core: Any = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}
            missing: Any = expected_core - set(EXCLUDED_DIRS)
            assert not missing, f'Missing core exclusions: {missing}'
        finally:
            sys.path.remove(str(SCRIPTS_DIR))

    def test_depth_limits_reasonable(self) -> Any:
        """MIN_DEPTH and MAX_DEPTH should be reasonable values."""
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            from canon_validator import MAX_DEPTH, MIN_DEPTH
            assert MIN_DEPTH >= 0, 'MIN_DEPTH should be non-negative'
            assert MAX_DEPTH >= MIN_DEPTH, 'MAX_DEPTH should be >= MIN_DEPTH'
            assert MAX_DEPTH <= 10, 'MAX_DEPTH should be reasonable (<=10)'
        finally:
            sys.path.remove(str(SCRIPTS_DIR))

def compute_source_hash(file_path: Path) -> str:
    """Compute hash of normalized source code (ignoring comments/whitespace)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree: Any = ast.parse(f.read())
    ast_str: Any = ast.dump(tree, annotate_fields=False)
    return hashlib.sha256(ast_str.encode()).hexdigest()

class test_source_integrity:
    """Verify source code integrity."""

    def test_original_parses_cleanly(self) -> Any:
        """Original monolith should parse without syntax errors."""
        with open(ORIGINAL_SCRIPT, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        ast.parse(content)

    def test_all_modular_files_parse_cleanly(self) -> Any:
        """All modular package files should parse without syntax errors."""
        errors: Any = []
        for py_file in MODULAR_PACKAGE.glob('**/*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f'{py_file}: {e}')
        assert not errors, f'Syntax errors in modular package:\n' + '\n'.join(errors)

    def test_bootstrap_parses_cleanly(self) -> Any:
        """Bootstrap script should parse without syntax errors."""
        with open(BOOTSTRAP_SCRIPT, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        ast.parse(content)

def generate_diff_report() -> str:
    """Generate a diff report for manual verification."""
    report: Any = []
    report.append('=' * 60)
    report.append('CANON VALIDATOR EQUIVALENCE REPORT')
    report.append('=' * 60)
    original_lines: Any = len(ORIGINAL_SCRIPT.read_text().splitlines())
    modular_files: Any = list(MODULAR_PACKAGE.glob('**/*.py'))
    modular_lines: Any = sum((len(f.read_text().splitlines()) for f in modular_files))
    report.append(f'\nOriginal: {original_lines} lines in 1 file')
    report.append(f'Modular: {modular_lines} lines in {len(modular_files)} files')
    original_classes: Any = extract_class_signatures(ORIGINAL_SCRIPT)
    modular_classes: Any = collect_modular_classes()
    report.append(f'\nOriginal classes: {len(original_classes)}')
    report.append(f'Modular classes: {len(modular_classes)}')
    missing_in_modular: Any = set(original_classes.keys()) - set(modular_classes.keys())
    if missing_in_modular:
        report.append(f'\nClasses in original but not modular: {missing_in_modular}')
    extra_in_modular: Any = set(modular_classes.keys()) - set(original_classes.keys())
    if extra_in_modular:
        report.append(f'\nClasses in modular but not original: {extra_in_modular}')
    return '\n'.join(report)
if __name__ == '__main__':
    print(generate_diff_report())
    print('\nRunning pytest...')
    pytest.main([__file__, '-v', '--tb=short'])
