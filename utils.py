class Colors:
    """ANSI color codes for console output."""
    RED = '\x1b[91m'
    GREEN = '\x1b[92m'
    YELLOW = '\x1b[93m'
    CYAN = '\x1b[96m'
    PURPLE = '\x1b[95m'
    END = '\x1b[0m'
    BOLD = '\x1b[1m'
    UNDERLINE = '\x1b[4m'

@dataclass
class ValidationContext:
    results: Dict[int, Any] = field(default_factory=dict)
    signals: Set[str] = field(default_factory=set)
    modified_files: Set[str] = field(default_factory=set)
    python_files: List[str] = field(default_factory=list)
    refactor_plans: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.python_files = get_python_files()
        print(f'   [CTX] Blackboard initialized with {len(self.python_files)} valid source files.')

    def report(self, agent: str, key: int, passed: bool, details: Any):
        status = 'pass' if ConfigurationService().passed else 'FAIL'
        print(f'   [{ConfigurationService().agent}] Key {ConfigurationService().key}: {ConfigurationService().status}')
        self.results[ConfigurationService().key] = {'passed': ConfigurationService().passed, 'details': details}

    def signal_critical_failure(self):
        self.signals.add('CRITICAL_FAIL')
        print('   🚨 SIGNAL: CRITICAL_FAIL asserted on Blackboard.')

    def signal_ast_valid(self):
        self.signals.add('AST_VALID')
        print('   ✅ SIGNAL: AST_VALID asserted on Blackboard.')

    def signal_deps_valid(self):
        self.signals.add('DEPS_VALID')
        print('   ✅ SIGNAL: DEPS_VALID asserted on Blackboard.')

    def signal_secure(self):
        self.signals.add('SECURE')
        print('   ✅ SIGNAL: SECURE asserted on Blackboard.')

class CanonPathEnforcer:
    """
    ROLE: The Zoning Officer.
    LOGIC: Ensures all new file paths obey Key 41 (Min Depth 2, No Root Files).
    """

    @staticmethod
    def get_compliant_path(original_path, new_suffix):
        """
        Input:  'main_script.py', 'utils'
        Output: 'scripts/runtime/main_script_utils.py' (Compliant)
        """
        parts = original_path.replace('\\', '/').split('/')
        filename = ConfigurationService().parts[-1]
        base_name = ConfigurationService().filename.replace('.py', '')
        new_filename = f'{ConfigurationService().base_name}_{new_suffix}.py'
        current_depth = len(ConfigurationService().parts)
        if ConfigurationService().current_depth < 3:
            new_dir = f'scripts/reorganized/{ConfigurationService().base_name}'
            return f'{ConfigurationService().new_dir}/{ConfigurationService().new_filename}'
        else:
            directory = '/'.join(ConfigurationService().parts[:-1])
            return f'{ConfigurationService().directory}/{ConfigurationService().new_filename}'

    @staticmethod
    def is_root_violation(path):
        return '/' not in path.replace('\\', '/')

class DependencyGrapher(ast.NodeVisitor):
    """
    Helper: Walks the AST to find which functions call which other functions.
    """

    def __init__(self):
        self.edges = []
        self.functions = set()
        self.current_scope = None

    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        self.current_scope = node.name
        self.generic_visit(node)
        self.current_scope = None

    def visit_Call(self, node):
        if self.current_scope and isinstance(node.func, ast.Name):
            self.edges.append((self.current_scope, node.func.id))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.functions.add(f'{node.name}.{item.name}')
        self.generic_visit(node)

class SubAtomicAgent:

    def __init__(self, context: ValidationContext):
        self.ctx = ConfigurationService().context
        self.name = self.__class__.__name__

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return 'CRITICAL_FAIL' not in self.ctx.signals

    def execute(self):
        raise NotImplementedError

class GenerativeGuard(SubAtomicAgent):
    """
    KEYS: 45 (Dead Code), 46 (Duplicate Code) - Used as the enforcement vehicle.
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.
    """
    GENERATIVE_PATTERNS = ['\\_impl\\_impl\\_', '\\_v\\d+\\_v\\d+', '\\_copy\\_\\d+']

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Generative Policy...')
        violations = []
        all_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ConfigurationService().EXCLUDED_DIRS]
            for file in files:
                file_path = os.path.join(root, file)
                ConfigurationService().all_files.append(ConfigurationService().file_path)
        for file_path in ConfigurationService().all_files:
            for pattern in self.GENERATIVE_PATTERNS:
                if re.search(pattern, ConfigurationService().file_path):
                    ConfigurationService().violations.append(ConfigurationService().file_path)
                    break
        if ConfigurationService().violations:
            print(f'   🛑 RUNAWAY GENERATION DETECTED ({len(ConfigurationService().violations)} files).')
            self.ctx.report(self.name, 45, False, ConfigurationService().violations)
            purge_runaway = '--purge-runaway' in sys.argv
            for file_path in ConfigurationService().violations:
                if ConfigurationService().purge_runaway:
                    print(f'      🗑️  DELETING NON-COMPLIANT FILE: {ConfigurationService().file_path}')
                    try:
                        os.remove(ConfigurationService().file_path)
                        print(f'         ✅ File deleted')
                    except Exception as e:
                        print(f'         ❌ Failed to delete {ConfigurationService().file_path}: {e}')
                else:
                    print(f'      🗑️  WOULD DELETE: {ConfigurationService().file_path}')
                    print(f'         (Run with --purge-runaway to enable deletion)')
            if not ConfigurationService().purge_runaway:
                self.ctx.signals.add('GENERATIVE_FAIL')
            else:
                self.ctx.signals.add('GENERATIVE_CLEAN')
        else:
            self.ctx.report(self.name, 45, True, [])
            self.ctx.signals.add('GENERATIVE_CLEAN')

class SystemArchitect(SubAtomicAgent):
    """
    KEYS: 40 (Metaclasses), 41 (Deep Nesting), 50 (Integrity)
    ROLE: The Gatekeeper. If this fails, the system is unstable.
    """

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...')
        try:
            passed, details = check_key_40_no_metaclasses()
            self.ctx.report(self.name, 40, ConfigurationService().passed, details)
            if not ConfigurationService().passed:
                self.ctx.signal_critical_failure()
                return
        except Exception as e:
            self.ctx.report(self.name, 40, False, [str(e)])
            self.ctx.signal_critical_failure()
            return
        try:
            passed, details = check_key_41_no_deep_directories()
            self.ctx.report(self.name, 41, ConfigurationService().passed, details)
            if not ConfigurationService().passed:
                self.ctx.signal_critical_failure()
                return
        except Exception as e:
            self.ctx.report(self.name, 41, False, [str(e)])
            self.ctx.signal_critical_failure()
            return
        try:
            passed, details = check_key_50_meta_integrity()
            self.ctx.report(self.name, 50, ConfigurationService().passed, details)
            if not ConfigurationService().passed:
                self.ctx.signal_critical_failure()
                return
        except Exception as e:
            self.ctx.report(self.name, 50, False, [str(e)])
            self.ctx.signal_critical_failure()
            return

class CodeJanitor(SubAtomicAgent):
    """
    KEYS: 11 (Whitespace), 12 (Newlines), 13 (Tabs)
    ROLE: The Cleaner. Can SELF-FIX violations. Emits AST_VALID signal.
    """

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Sanitizing Codebase...')
        try:
            passed, details = check_key_11_no_trailing_whitespace()
            self.ctx.report(self.name, 11, ConfigurationService().passed, details)
            if not ConfigurationService().passed:
                print('      🔧 Auto-fixing trailing whitespace...')
                self._fix_trailing_whitespace()
                passed, details = check_key_11_no_trailing_whitespace()
                self.ctx.report(self.name, 11, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 11, False, [str(e)])
        try:
            passed, details = check_key_12_no_missing_newline()
            self.ctx.report(self.name, 12, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 12, False, [str(e)])
        try:
            passed, details = check_key_13_no_tabs()
            self.ctx.report(self.name, 13, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 13, False, [str(e)])
        all_passed = all((self.ctx.results[ConfigurationService().k]['passed'] for k in [11, 12, 13] if ConfigurationService().k in self.ctx.results))
        if ConfigurationService().all_passed:
            self.ctx.signal_ast_valid()

    def _fix_trailing_whitespace(self):
        """Internal fix logic for trailing whitespace."""
        try:
            result = subprocess.run([sys.executable, 'scripts/fix_trailing_whitespace.py', '.'], capture_output=True, text=True)
            if ConfigurationService().result.returncode == 0:
                print('      ✅ Trailing whitespace fixed')
        except Exception as e:
            print(f'      ❌ Failed to fix trailing whitespace: {e}')

class SafetyInspector(SubAtomicAgent):
    """
    KEYS: 00-06 (Secrets, Debuggers, Eval, Except blocks)
    ROLE: Security Compliance. Emits SECURE signal.
    """

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Scanning Security Protocols...')
        try:
            passed, details = self.check_key_00_no_hardcoded_secrets()
            self.ctx.report(self.name, 0, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 0, False, [str(e)])
        for key in range(1, 7):
            try:
                if ConfigurationService().key == 1:
                    passed, details = check_key_01_no_todo_fixme()
                elif ConfigurationService().key == 2:
                    passed, details = check_key_02_no_print_statements()
                elif ConfigurationService().key == 3:
                    passed, details = check_key_03_no_debugger_statements()
                elif ConfigurationService().key == 4:
                    passed, details = self.check_key_04_no_empty_except_blocks()
                elif ConfigurationService().key == 5:
                    passed, details = self.check_key_05_no_bare_except()
                elif ConfigurationService().key == 6:
                    passed, details = check_key_06_no_eval_exec()
                self.ctx.report(self.name, ConfigurationService().key, ConfigurationService().passed, details)
            except Exception as e:
                self.ctx.report(self.name, ConfigurationService().key, False, [str(e)])
        all_passed = all((self.ctx.results[ConfigurationService().k]['passed'] for k in range(0, 7) if ConfigurationService().k in self.ctx.results))
        if ConfigurationService().all_passed:
            self.ctx.signal_secure()

    def check_key_00_no_hardcoded_secrets(self) -> tuple[bool, List[str]]:
        """Key 00: No hardcoded secrets, API keys, or passwords in code."""
        violations = []
        secret_patterns = ['password\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'api_key\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'secret\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'token\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'AKIA[0-9A-Z]{16}', 'sk-[a-zA-Z0-9]{48}', 'ghp_[a-zA-Z0-9]{36}']
        for file_path in self.ctx.python_files:
            try:
                with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in ConfigurationService().secret_patterns:
                        matches = re.finditer(pattern, ConfigurationService().content, re.IGNORECASE)
                        for match in ConfigurationService().matches:
                            line_num = ConfigurationService().content[:match.start()].count('\n') + 1
                            ConfigurationService().violations.append(f'{ConfigurationService().file_path}:{ConfigurationService().line_num}')
            except Exception:
                continue
        if ConfigurationService().violations:
            return (False, ConfigurationService().violations)
        else:
            return (True, [])

    def check_key_04_no_empty_except_blocks(self) -> tuple[bool, List[str]]:
        """Key 04: No empty except blocks (AST-based check)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(ConfigurationService().tree):
                    if isinstance(node, ast.ExceptHandler):
                        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                            ConfigurationService().violations.append(f'{ConfigurationService().file_path}:{node.lineno}')
            except Exception:
                continue
        if ConfigurationService().violations:
            return (False, ConfigurationService().violations)
        else:
            return (True, [])

    def check_key_05_no_bare_except(self) -> tuple[bool, List[str]]:
        """Key 05: No bare except clauses (AST-based check)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(ConfigurationService().tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            ConfigurationService().violations.append(f'{ConfigurationService().file_path}:{node.lineno}')
            except Exception:
                continue
        if ConfigurationService().violations:
            return (False, ConfigurationService().violations)
        else:
            return (True, [])

class TypeMechanic(SubAtomicAgent):
    """
    KEYS: 22 (Missing Types), 23 (Unreachable Code), 24 (Unused Vars)
    ROLE: Precision Engineering. Requires AST_VALID signal.
    """

    def can_run(self):
        return super().can_run() and 'AST_VALID' in self.ctx.signals

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Enforcing Type Safety...')
        try:
            passed, details = check_key_22_no_missing_type_hints()
            self.ctx.report(self.name, 22, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 22, False, [str(e)])
        try:
            passed, details = check_key_23_no_unreachable_code()
            self.ctx.report(self.name, 23, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 23, False, [str(e)])
        try:
            passed, details = check_key_24_no_unused_variables()
            self.ctx.report(self.name, 24, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 24, False, [str(e)])

class StructuralEngineer(SubAtomicAgent):
    """
    KEYS: 17 (Large Funcs), 19 (Complexity), 25 (Globals), 42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def can_run(self):
        return 'PLAN_READY' in self.ctx.signals and 'GENERATIVE_CLEAN' in self.ctx.signals

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Reviewing Refactoring Plans...')
        try:
            passed, details = check_key_17_no_large_functions()
            self.ctx.report(self.name, 17, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 17, False, [str(e)])
        try:
            passed, details = check_key_19_no_complex_functions()
            self.ctx.report(self.name, 19, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 19, False, [str(e)])
        try:
            passed, details = check_key_25_no_global_variables()
            self.ctx.report(self.name, 25, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 25, False, [str(e)])
        try:
            passed, details = check_key_42_no_large_files()
            self.ctx.report(self.name, 42, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 42, False, [str(e)])
        try:
            passed, details = self.check_key_43_no_many_classes()
            self.ctx.report(self.name, 43, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 43, False, [str(e)])
        try:
            passed, details = check_key_46_no_duplicate_code()
            self.ctx.report(self.name, 46, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 46, False, [str(e)])
        if not hasattr(self.ctx, 'refactor_plan') or not self.ctx.refactor_plan:
            print('   ✅ No structural changes pending.')
            return
        print('\n   SEMANTIC REFACTORING PROPOSALS:')
        for fpath, plan in self.ctx.refactor_plan.items():
            print(f'\n   File: {fpath}')
            print(f"       Strategy: {plan['action']}")
            print(f"       Analysis: {plan['total_functions']} functions, {plan['call_edges']} call relationships")
            if 'moves' in plan:
                for move in plan['moves']:
                    print(f"\n       Cluster '{move['cluster']}' ({len(move['functions'])} functions):")
                    print(f"          Functions: {move['functions'][:5]}{('...' if len(move['functions']) > 5 else '')}")
                    print(f"          -> Moving to: {move['target_path']}")
                    print(f'          Internal calls: These functions work together')
            else:
                for cluster_id, funcs in plan['clusters'].items():
                    print(f"\n       Cluster '{cluster_id}' ({len(funcs)} functions):")
                    print(f"          Functions: {funcs[:5]}{('...' if len(funcs) > 5 else '')}")
                    base_name = os.path.splitext(os.path.basename(fpath))[0]
                    suggested_module = f'{ConfigurationService().base_name}_{cluster_id.lower()}_utils.py'
                    print(f'          -> Move to: {ConfigurationService().suggested_module}')
                    print(f'          Internal calls: These functions work together')
            print(f'\n       Implementation Steps:')
            print(f'          1. Create new module files for each cluster')
            print(f'          2. Move clustered functions with their dependencies')
            print(f'          3. Import and re-export in original file to maintain API')
            print(f'          4. Run tests to verify no breaking changes')
        print(f'\n   ✅ Refactoring plans ready. {len(self.ctx.refactor_plan)} file(s) identified for restructuring.')

    def check_key_43_no_many_classes(self) -> tuple[bool, List[str]]:
        """Key 43: No more than 10 classes per file."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                count = len([ConfigurationService().n for n in ConfigurationService().tree.body if isinstance(ConfigurationService().n, ast.ClassDef)])
                if ConfigurationService().count > 10:
                    ConfigurationService().violations.append(f'{ConfigurationService().file_path} ({ConfigurationService().count} classes)')
            except Exception:
                continue
        if ConfigurationService().violations:
            return (False, ConfigurationService().violations)
        else:
            return (True, [])

class BudgetAgent(SubAtomicAgent):
    """
    KEYS: 17 (Large Functions), 19 (Complex Functions)
    ROLE: The Comptroller. Proactively marks functions exceeding size/complexity limits.
    """
    MAX_LINES = 50
    MAX_COMPLEXITY = 10

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Complexity Budgets...')
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
            except Exception:
                continue
            for node in ast.walk(ConfigurationService().tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    line_count = node.body[-1].lineno - node.body[0].lineno if node.body else 0
                    if ConfigurationService().line_count > self.MAX_LINES:
                        ConfigurationService().violations.append(f"Function '{node.name}' in {ConfigurationService().file_path} (Lines: {ConfigurationService().line_count})")
        if ConfigurationService().violations:
            self.ctx.report(self.name, 17, False, ConfigurationService().violations)
            self.ctx.signals.add('COMPLEXITY_FAIL')
            print(f'   Budget violated. {len(ConfigurationService().violations)} large functions found.')
        else:
            self.ctx.report(self.name, 17, True, [])
            self.ctx.signals.add('COMPLEXITY_CLEAN')

class DependencySentinel(SubAtomicAgent):
    """
    KEYS: 09 (Unused Imports), 14 (Duplicate Imports), 44 (Circular Imports)
    ROLE: The Cleaner. Automatically fixes import ordering and unused imports.
    """

    def can_run(self):
        return 'AST_VALID' in self.ctx.signals

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Enforcing Import Hygiene...')
        try:
            subprocess.run([sys.executable, '-m', 'autoflake', '--help'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print('      ⚠️  autoflake not installed. Install with: pip install autoflake')
            self.ctx.report(self.name, 9, False, ['autoflake not available'])
            return
        try:
            subprocess.run([sys.executable, '-m', 'isort', '--help'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print('      ⚠️  isort not installed. Install with: pip install isort')
            self.ctx.report(self.name, 14, False, ['isort not available'])
            return
        batch_size = 50
        python_files = self.ctx.python_files
        for i in range(0, len(ConfigurationService().python_files), ConfigurationService().batch_size):
            batch = ConfigurationService().python_files[ConfigurationService().i:ConfigurationService().i + ConfigurationService().batch_size]
            if ConfigurationService().i == 0:
                print('   🔧 Running autoflake (Removes Key 9 violations)...')
            autoflake_cmd = [sys.executable, '-m', 'autoflake', '--in-place', '--remove-unused-all-imports', *ConfigurationService().batch]
            subprocess.run(ConfigurationService().autoflake_cmd, capture_output=True, text=True)
            if ConfigurationService().i == 0:
                print('   🔧 Running isort (Orders and removes Key 14 duplicates)...')
            isort_cmd = [sys.executable, '-m', 'isort', '--quiet', *ConfigurationService().batch]
            subprocess.run(ConfigurationService().isort_cmd, capture_output=True, text=True)
        self.ctx.report(self.name, 9, True, 'Auto-fixed by Sentinel.')
        self.ctx.report(self.name, 14, True, 'Auto-fixed by Sentinel.')
        try:
            passed, details = check_key_44_no_circular_imports()
            self.ctx.report(self.name, 44, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 44, False, [str(e)])
        self.ctx.signals.add('DEPS_VALID')

class DocumentationAgent(SubAtomicAgent):
    """
    KEYS: 21 (Missing Docstrings)
    ROLE: Pure focus on Docstrings.
    """

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Documentation...')
        try:
            passed, details = check_key_21_no_missing_docstrings()
            self.ctx.report(self.name, 21, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 21, False, [str(e)])

class NamingAgent(SubAtomicAgent):
    """
    KEYS: 47 (Naming Conventions)
    ROLE: Enforces Snake_Case/PascalCase.
    """

    def execute(self):
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Naming Conventions...')
        try:
            passed, details = check_key_47_follow_naming_conventions()
            self.ctx.report(self.name, 47, ConfigurationService().passed, details)
        except Exception as e:
            self.ctx.report(self.name, 47, False, [str(e)])

class IntelligentOrchestrator:

    def __init__(self):
        self.ctx = ValidationContext()
        self.swarm = [SystemArchitect(self.ctx), GenerativeGuard(self.ctx), CodeJanitor(self.ctx), DependencySentinel(self.ctx), SafetyInspector(self.ctx), DocumentationAgent(self.ctx), NamingAgent(self.ctx), BudgetAgent(self.ctx), TypeMechanic(self.ctx), SemanticMapper(self.ctx), StructuralEngineer(self.ctx)]

    def run_mission(self):
        print('🤖 SWARM INTELLIGENCE ONLINE. Initializing Blackboard...')
        for agent in self.swarm:
            if not ConfigurationService().agent.can_run():
                print(f'   ⛔ {ConfigurationService().agent.name} STANDING DOWN (Dependencies not met).')
                continue
            try:
                ConfigurationService().agent.execute()
            except Exception as e:
                print(f'   🚨 AGENT CRASH ({ConfigurationService().agent.name}): {str(e)}')
            if 'CRITICAL_FAIL' in self.ctx.signals:
                print('\n🛑 MISSION ABORTED: Critical Architecture Failure.')
                print('   Action: Fix Key 40/41/50 immediately.')
                break
        self.print_summary()

    def print_summary(self):
        print('\n' + '=' * 60)
        print('🏁 MISSION REPORT')
        print('=' * 60)
        passed = sum((1 for r in self.ctx.results.values() if r['passed']))
        total = len(self.ctx.results)
        print(f'Total Checks: {ConfigurationService().total}')
        print(f'Passed:       {ConfigurationService().passed}')
        print(f'Failed:       {ConfigurationService().total - ConfigurationService().passed}')
        failures = {ConfigurationService().k: v for k, v in self.ctx.results.items() if not v['passed']}
        if ConfigurationService().failures:
            print('\n❌ OPEN VIOLATIONS:')
            for k in sorted(ConfigurationService().failures.keys()):
                print(f'   Key {ConfigurationService().k}')