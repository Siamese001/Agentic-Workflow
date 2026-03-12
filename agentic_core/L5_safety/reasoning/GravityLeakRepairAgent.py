from __future__ import annotations
from agentic_core.L2_execution.tools import write_gateway as _wg
'\nGravityLeakRepairAgent - Automated Gravity Violation Healer (Phase 2.3)\nTerritory: agentic_core/L5_safety/enforcement/\n\nRESPONSIBILITIES:\n- Automatically fix upward imports detected by StructureEnforcerAgent\n- Refactor code to eliminate gravity violations\n- Suggest architectural improvements\n- Generate import rewrite recommendations\n\nHEALING STRATEGIES:\n1. Move shared code to neutral utils/ layer\n2. Create abstraction layers for cross-layer dependencies\n3. Use dependency injection instead of direct imports\n4. Refactor to respect layer hierarchy\n\nCanon Key 51 Compliance: Includes heal_repository() method\n'
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config import ARCHIVES_DIR, OPS_SCRIPTS_DIR
from agentic_core.L4_state.utils.layer_gravity_util import LAYER_ORDER
from agentic_core.L5_safety.validators.context_validator import get_context_manager
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class GravityRepairProhibitedError(Exception):
    """Raised when mutation prohibition blocks a gravity fix after one retry."""

    def __init__(self, file_path: Path, layer: str, op: str) -> None:
        self.file_path = file_path
        self.layer = layer
        self.op = op
        super().__init__(f'GRAVITY_REPAIR_PROHIBITED: file={file_path} layer={layer} op={op} — downgraded to PLAN-ONLY')

@dataclass
class GravityFix:
    """Represents a gravity violation fix."""
    file_path: Path
    line_number: int
    old_import: str
    new_import: str
    fix_type: str
    rationale: str

class GravityLeakRepairAgent(SovereignBaseAgent):
    """
    [L5 HEALER] Automated gravity violation repair agent.

    Works in tandem with StructureEnforcerAgent to automatically fix
    upward imports and architectural violations.

    Healing Strategies:
    1. RELOCATE: Move shared code to utils/ or appropriate layer
    2. ABSTRACT: Create abstraction layer for cross-layer dependencies
    3. INJECT: Use dependency injection instead of direct imports
    4. REMOVE: Remove unnecessary imports
    """
    LAYER_ORDER = LAYER_ORDER

    def __init__(self, project_root: Path=None) -> None:
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logger = Logger
        self.context = get_context_manager(self.project_root)
        self._prohibition_hits: dict[tuple[str, str], int] = {}

    def analyze_violation(self, file_path: Path, import_statement: str, file_layer: str, import_layer: str) -> GravityFix:
        """
        Analyze a gravity violation and recommend a fix.

        [META-LEARNING] Enhanced with caching and pattern recall:
        - Caches AST analysis results to prevent redundant parsing
        - Recalls successful fix strategies for similar violations
        - Stores successful patterns for future use

        Args:
            file_path: File with the violation
            import_statement: The problematic import
            file_layer: Layer of the file
            import_layer: Layer being imported

        Returns:
            GravityFix with recommended solution
        """
        violation = {'type': 'gravity_violation', 'file_path': str(file_path), 'import_statement': import_statement, 'file_layer': file_layer, 'import_layer': import_layer}
        cached_pattern = self.context.recall_healing_pattern(violation, agent='GravityLeakRepairAgent')
        if cached_pattern:
            self.logger.info(f"[GravityLeakRepairAgent] Using cached fix pattern from {cached_pattern.get('discovered_by')}")
            metadata = cached_pattern.get('metadata', {})
            return GravityFix(file_path=file_path, line_number=metadata.get('line_number', 0), old_import=import_statement, new_import=metadata.get('new_import', '# TODO: Create abstraction layer'), fix_type=cached_pattern.get('healing_strategy', 'ABSTRACT'), rationale=f"Pattern from {cached_pattern.get('discovered_by')} (used {cached_pattern.get('success_count')} times)")
        cache_key = f'gravity_analysis:{file_path}:{hash(import_statement)}'
        cached_analysis = self.context.cache_get(cache_key, agent='GravityLeakRepairAgent')
        if cached_analysis:
            self.logger.debug(f'[GravityLeakRepairAgent] Using cached analysis for {file_path}')
            return GravityFix(**cached_analysis)
        if import_statement and import_statement.strip().startswith(('import ', 'from ')):
            fix = GravityFix(file_path=file_path, line_number=0, old_import=import_statement, new_import=self._build_deferred_import(import_statement), fix_type='DEFERRED', rationale=f'Defer top-level {file_layer}→{import_layer} import into function scope to eliminate gravity violation at module-load time')
        elif import_layer == 'L0':
            fix = GravityFix(file_path=file_path, line_number=0, old_import=import_statement, new_import=self._suggest_utils_import(import_statement), fix_type='RELOCATE', rationale=f'Move shared L0 code to utils/ to avoid upward import from {file_layer}')
        else:
            fix = GravityFix(file_path=file_path, line_number=0, old_import=import_statement, new_import='# TODO: Create abstraction layer', fix_type='ABSTRACT', rationale=f'Create abstraction layer to decouple {file_layer} from {import_layer}')
        fix_dict = {'file_path': fix.file_path, 'line_number': fix.line_number, 'old_import': fix.old_import, 'new_import': fix.new_import, 'fix_type': fix.fix_type, 'rationale': fix.rationale}
        self.context.cache_set(cache_key, fix_dict, agent='GravityLeakRepairAgent', ttl=3600)
        return fix

    def _build_deferred_import(self, import_statement: str) -> str:
        """Return a 4-space-indented version of the import for placement inside a function body.

        The caller is responsible for finding the first function that uses the
        imported name and inserting this line at the top of that function body.
        When used via _apply_deferred_import_ast, the top-level import line is
        removed and the indented form is inserted.
        """
        return '    ' + import_statement.strip()

    def _suggest_utils_import(self, import_statement: str) -> str:
        """
        Suggest a utils/ import path for relocated code.

        Args:
            import_statement: Original import statement

        Returns:
            Suggested new import path
        """
        if 'from' in import_statement:
            parts = import_statement.split()
            if len(parts) >= 4:
                module_path = parts[1]
                imported_items = ' '.join(parts[3:])
                if 'mixins' in module_path:
                    return f'from agentic_core.mixins.subatomic_testing_mixin import {imported_items}'
                else:
                    return f'from agentic_core.utils import {imported_items}'
        return import_statement

    def generate_fix_report(self, violations: list[dict[str, Any]]) -> list[GravityFix]:
        """
        Generate fix recommendations for all violations.

        Args:
            violations: List of gravity violations from StructureEnforcerAgent

        Returns:
            List of GravityFix recommendations
        """
        fixes = []
        for violation in violations:
            fix = self.analyze_violation(file_path=violation.get('file_path'), import_statement=violation.get('import_statement', ''), file_layer=violation.get('file_layer', ''), import_layer=violation.get('import_layer', ''))
            fixes.append(fix)
        return fixes

    def _check_prohibition_circuit_breaker(self, file_path: Path, op: str) -> None:
        """Increment hit counter; raise GravityRepairProhibitedError on second hit."""
        key = (str(file_path), op)
        self._prohibition_hits[key] = self._prohibition_hits.get(key, 0) + 1
        if self._prohibition_hits[key] >= 2:
            raise GravityRepairProhibitedError(file_path, 'L0', op)

    # guardian: allow-type-erasure
    def _emit_plan_only(self, fix: GravityFix) -> dict[str, Any]:
        """Emit a PLAN-ONLY artifact without attempting any write."""
        self.logger.warning(f'[PLAN-ONLY] GRAVITY_REPAIR_PROHIBITED — requires privileged mutation context: file={fix.file_path} fix_type={fix.fix_type} old_import={fix.old_import!r} new_import={fix.new_import!r}')
        return {'status': 'plan_only', 'fix_type': fix.fix_type, 'file': str(fix.file_path), 'old_import': fix.old_import, 'new_import': fix.new_import, 'requires': 'privileged_mutation_context'}

    def _apply_deferred_import(self, file_path: Path, import_stmt: str) -> bool:
        """Move a top-level import to inside the first function/method body that follows it.

        Uses AST to:
          1. Find the import node at module level.
          2. Collect the names it introduces.
          3. Verify ALL usages of those names are inside function/method bodies
             (not at module level) — abort if any module-level usage found.
          4. Find the first function definition that follows the import.
          5. Determine insertion line = first statement line of that function body.
          6. Rewrite file: remove original import line, insert indented import.

        Returns True if the transformation was applied, False otherwise.
        Raises ValueError on catastrophic-replace guard.
        """
        import ast as _ast
        stripped = import_stmt.strip()
        if len(stripped) <= 1:
            raise ValueError(f'Refusing deferred import: statement too short ({stripped!r})')
        source = file_path.read_text(encoding='utf-8')
        try:
            tree = _ast.parse(source)
        except SyntaxError:
            return False
        import_node = None
        for node in tree.body:
            if isinstance(node, (_ast.Import, _ast.ImportFrom)):
                src_line = source.splitlines()[node.lineno - 1].strip()
                if src_line == stripped:
                    import_node = node
                    break
        if import_node is None:
            return False
        if isinstance(import_node, _ast.ImportFrom):
            introduced = {alias.asname or alias.name.split('.')[0] for alias in import_node.names}
        else:
            introduced = {alias.asname or alias.name.split('.')[0] for alias in import_node.names}

        class _UsageChecker(_ast.NodeVisitor):

            def __init__(self) -> None:
                self.module_level_uses: list[str] = []
                self._depth = 0

            def visit_FunctionDef(self, node: _ast.FunctionDef) -> None:
                self._depth += 1
                self.generic_visit(node)
                self._depth -= 1
            visit_AsyncFunctionDef = visit_FunctionDef

            def visit_ClassDef(self, node: _ast.ClassDef) -> None:
                self._depth += 1
                self.generic_visit(node)
                self._depth -= 1

            def visit_Name(self, node: _ast.Name) -> None:
                if self._depth == 0 and node.id in introduced:
                    if node.lineno != import_node.lineno:
                        self.module_level_uses.append(node.id)
                self.generic_visit(node)
        checker = _UsageChecker()
        checker.visit(tree)
        if checker.module_level_uses:
            return False
        target_func = None
        for node in tree.body:
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                if node.lineno > import_node.lineno:
                    target_func = node
                    break
            elif isinstance(node, _ast.ClassDef) and node.lineno > import_node.lineno:
                for item in node.body:
                    if isinstance(item, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                        target_func = item
                        break
                if target_func is not None:
                    break
        if target_func is None:
            return False
        if not target_func.body:
            return False
        first_stmt = target_func.body[0]
        insert_lineno = first_stmt.lineno
        if isinstance(first_stmt, _ast.Expr) and isinstance(getattr(first_stmt, 'value', None), (_ast.Constant,)) and isinstance(first_stmt.value.value, str) and (len(target_func.body) > 1):
            insert_lineno = target_func.body[1].lineno
        lines = source.splitlines(keepends=True)
        import_line_idx = import_node.lineno - 1
        insert_line_content = lines[insert_lineno - 1]
        body_indent = ' ' * (len(insert_line_content) - len(insert_line_content.lstrip()))
        deferred_line = body_indent + stripped + '\n'
        new_lines = [line for idx, line in enumerate(lines) if idx != import_line_idx]
        insert_idx = insert_lineno - 1
        if insert_idx > import_line_idx:
            insert_idx -= 1
        new_lines.insert(insert_idx, deferred_line)
        try:
            _ast.parse(''.join(new_lines))
        except SyntaxError:
            return False
        file_path.write_text(''.join(new_lines), encoding='utf-8')
        return True

    def _apply_import_replacement_ast(self, file_path: Path, old_import: str, new_import: str) -> bool:
        """Replace exactly the matching import line(s) using line-level comparison.

        Returns True if any replacement was made, False otherwise.
        Raises ValueError if old_import is empty or a single character (catastrophic replace guard).
        """
        stripped = old_import.strip()
        if len(stripped) <= 1:
            raise ValueError(f'Refusing content.replace: old_import is too short ({stripped!r}), would cause catastrophic file corruption.')
        lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)
        new_lines = []
        changed = False
        substitution_count = 0
        for line in lines:
            if line.rstrip('\n\r') == stripped or line.strip() == stripped:
                new_lines.append(new_import + '\n')
                changed = True
                substitution_count += 1
            else:
                new_lines.append(line)
        if changed:
            _wg.write_text(file_path, ''.join(new_lines), encoding='utf-8', substitution_count=substitution_count, expected_max_substitutions=1)
        return changed

    # guardian: allow-type-erasure
    def apply_fix(self, fix: GravityFix, dry_run: bool=True, privileged_mutation_context: bool=False) -> dict[str, Any]:
        """
        Apply a gravity fix to a file using Atomic Write Safety.
        Includes circuit breaker for mutation prohibition and catastrophic-replace guard.

        Wave 2: privileged_mutation_context=True bypasses L0 prohibition for approved callers
        (e.g. ops_scripts/, scripts/ that are not sovereign agents).
        """
        try:
            if dry_run:
                self.logger.info(f'[DRY RUN] Would fix {fix.file_path.name}: {fix.fix_type}')
                return {'status': 'simulated', 'fix_type': fix.fix_type}
            if not fix.file_path.exists():
                return {'status': 'error', 'error': 'File not found'}
            if fix.fix_type == 'DEFERRED':
                try:
                    changed = self._apply_deferred_import(fix.file_path, fix.old_import)
                    if changed:
                        self.logger.info(f'[DEFERRED] {fix.file_path.name}: moved import into function scope')
                        return {'status': 'fixed', 'fix_type': 'DEFERRED'}
                    return {'status': 'no_change', 'fix_type': 'DEFERRED'}
                # guardian: allow-silent-swallow
                except Exception as deferred_err:
                    self.logger.warning(f'[DEFERRED] Failed for {fix.file_path.name}: {deferred_err}')
                    return self._emit_plan_only(fix)
            if fix.fix_type in ('ABSTRACT', 'RELOCATE'):
                return self._emit_plan_only(fix)
            if not privileged_mutation_context:
                try:
                    from agentic_core.L4_state.utils.layer_gravity_util import extract_layer_from_path
                    file_layer = extract_layer_from_path(fix.file_path) or 'unknown'
                    if file_layer == 'L0':
                        self._check_prohibition_circuit_breaker(fix.file_path, 'shutil.mutate')
                        return self._emit_plan_only(fix)
                except GravityRepairProhibitedError:
                    return self._emit_plan_only(fix)
                except ImportError:
                    pass
            temp_fd, temp_path = tempfile.mkstemp(dir=fix.file_path.parent, text=True)
            try:
                content = fix.file_path.read_text(encoding='utf-8')
                stripped_old = fix.old_import.strip()
                if len(stripped_old) <= 1:
                    try:
                        os.close(temp_fd)
                    except OSError:
                        pass
                    temp_fd = None
                    # guardian: allow-path-string
                    if os.path.exists(temp_path):
                        try:
                            _wg.remove_file(temp_path)
                        # guardian: allow-silent-swallow
                        except Exception:
                            pass
                    self.logger.warning(f'[PLAN-ONLY] old_import too short ({stripped_old!r}), refusing replace to prevent corruption.')
                    return self._emit_plan_only(fix)
                lines = content.splitlines(keepends=True)
                new_lines = []
                changed = False
                for line in lines:
                    if line.rstrip('\n\r') == stripped_old or line.strip() == stripped_old:
                        new_lines.append(fix.new_import + '\n')
                        changed = True
                    else:
                        new_lines.append(line)
                if not changed:
                    _wg.remove_file(temp_path)
                    return {'status': 'no_change', 'fix_type': fix.fix_type}
                new_content = ''.join(new_lines)
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as tf:
                    tf.write(new_content)
                temp_fd = None
                backup_dir = self.project_root / ARCHIVES_DIR / 'healing_backups' / 'gravity'
                _wg.ensure_dir(backup_dir)
                backup_path = backup_dir / f'{fix.file_path.name}.{int(os.times().system)}.bak'
                _wg.copy_file(fix.file_path, backup_path)
                os.replace(temp_path, fix.file_path)
                self.logger.info(f'[FIXED] {fix.file_path.name} (Backup: {backup_path.name})')
                return {'status': 'fixed', 'fix_type': fix.fix_type}
            except PermissionError as perm_err:
                err_str = str(perm_err)
                if 'MUTATION_PROHIBITED' in err_str:
                    op = 'shutil.mutate'
                    self._check_prohibition_circuit_breaker(fix.file_path, op)
                    if temp_fd is not None and (not isinstance(temp_fd, int)):
                        pass
                    # guardian: allow-path-string
                    if os.path.exists(temp_path):
                        try:
                            _wg.remove_file(temp_path)
                        # guardian: allow-silent-swallow
                        except Exception:
                            pass
                    return self._emit_plan_only(fix)
                raise
            # guardian: allow-silent-swallow
            except Exception as write_err:
                raise
                # guardian: allow-path-string
                if os.path.exists(temp_path):
                    _wg.remove_file(temp_path)
                raise write_err
        except GravityRepairProhibitedError as prohibited:
            self.logger.warning(str(prohibited))
            return self._emit_plan_only(fix)
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f'Error applying fix to {fix.file_path}: {e}')
            return {'status': 'error', 'error': str(e)}

    # guardian: allow-type-erasure
    def heal_violations(self, violations: list, *, dry_run: bool=False) -> dict:
        """Pure healer: fix pre-computed gravity violations without re-scanning.

        Called by gravity_leak_healer (HEALER_REGISTRY) after GravityValidatorAgent
        has already performed the StructuralValidatorAgent scan.  This eliminates
        the duplicate scan that heal_repository() previously did internally.

        Args:
            violations: List of violation objects from StructuralValidatorAgent.
            dry_run: If True, only report fixes without applying them.

        Returns:
            Dictionary with violations_found, violations_fixed, fix_summary, status.
        """
        if not violations:
            return {'agent': 'GravityLeakRepairAgent', 'status': 'PASS', 'violations_found': 0, 'violations_fixed': 0, 'summary': 'no gravity violations to repair'}
        self.logger.info(f'[GravityLeakRepairAgent.heal_violations] {len(violations)} violations (dry_run={dry_run})')
        fix_summary = {'RELOCATE': 0, 'ABSTRACT': 0, 'INJECT': 0, 'REMOVE': 0, 'DEFERRED': 0}
        fixes_applied = 0
        for v in violations:
            if hasattr(v, 'file_path'):
                _import_stmt = ''
                try:
                    _lines = v.file_path.read_text(encoding='utf-8', errors='replace').splitlines()
                    _ln = getattr(v, 'line_number', 0) or 0
                    if 1 <= _ln <= len(_lines):
                        _import_stmt = _lines[_ln - 1].strip()
                except (OSError, UnicodeDecodeError, IndexError) as e:
                    self.logger.warning(f'Failed to extract import statement from {v.file_path.name}: {e}')
                    _import_stmt = ''
                fix = self.analyze_violation(file_path=v.file_path, import_statement=_import_stmt, file_layer=getattr(v, 'source_layer', ''), import_layer=getattr(v, 'target_layer', ''))
            else:
                _import_stmt = ''
                try:
                    _fp = v.get('file_path')
                    _ln = v.get('line_number', 0) or 0
                    if _fp and _ln:
                        from pathlib import Path as _Path
                        _lines = _Path(_fp).read_text(encoding='utf-8', errors='replace').splitlines()
                        if 1 <= _ln <= len(_lines):
                            _import_stmt = _lines[_ln - 1].strip()
                except (OSError, UnicodeDecodeError, IndexError, TypeError) as e:
                    self.logger.warning(f"Failed to extract import statement from {v.get('file_path', 'unknown')}: {e}")
                    _import_stmt = ''
                fix = self.analyze_violation(file_path=v.get('file_path'), import_statement=_import_stmt, file_layer=v.get('file_layer', ''), import_layer=v.get('import_layer', ''))
            fix_summary.setdefault(fix.fix_type, 0)
            fix_summary[fix.fix_type] += 1
            result = self.apply_fix(fix, dry_run=dry_run)
            if isinstance(result, dict) and result.get('status') == 'fixed':
                fixes_applied += 1
        return {'agent': 'GravityLeakRepairAgent', 'violations_found': len(violations), 'violations_fixed': fixes_applied, 'fix_summary': fix_summary, 'status': 'PASS' if fixes_applied == len(violations) else 'PARTIAL', 'dry_run': dry_run, 'summary': f'Analyzed {len(violations)} violations, applied {fixes_applied} fixes'}

    # guardian: allow-magic-config
    # guardian: allow-type-erasure
    # guardian: allow-magic-config
    def heal_repository(self, dry_run: bool=True, execute: bool=False, depth: int=0, max_depth: int=3, _call_path: list[str] | None=None) -> dict[str, Any]:
        """
        Canon Key 51 compliance: Detect and fix gravity violations.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking

        Returns:
            Dictionary with healing summary
        """
        super().heal_repository()
        if _call_path is None:
            _call_path = []
        self.logger.info(f'[GravityLeakRepairAgent] Starting gravity leak repair (dry_run={dry_run})')
        try:
            from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import StructuralValidatorAgent, StructureConfig
            config = StructureConfig(project_root=self.project_root, excluded_paths=(OPS_SCRIPTS_DIR, 'scripts'))
            enforcer = StructuralValidatorAgent(config=config)
            results = enforcer.validate_structure(self.project_root)
            _excluded = config.excluded_paths
            violations = [v for v in results.violations if not any(((str(getattr(v, 'file_path', v.get('file_path', '') if isinstance(v, dict) else '')).replace('\\', '/').split('/')[:2] or [''])[0] == ex or ex in str(getattr(v, 'file_path', v.get('file_path', '') if isinstance(v, dict) else '')).replace('\\', '/') for ex in _excluded))]
            import re as _re
            _LAYER_DIR_PATTERN = _re.compile('^L[0-6]_')
            from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST
            from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
            _APPS_ROOTS: frozenset[str] = frozenset((k for k in PROJECT_ROOT_WHITELIST if k.startswith('apps_')))

            def _in_sovereign_scope(v: object) -> bool:
                fp = str(getattr(v, 'file_path', v.get('file_path', '') if isinstance(v, dict) else '')).replace('\\', '/')
                try:
                    # guardian: allow-path-string
                    rel = fp.replace(str(self.project_root).replace('\\', '/') + '/', '', 1)
                except (ValueError, AttributeError) as e:
                    self.logger.debug(f'Failed to make path relative: {e}')
                    rel = fp
                parts = [p for p in rel.split('/') if p]
                if not parts:
                    return False
                root = parts[0]
                if root in _APPS_ROOTS:
                    return True
                if root == AGENTIC_CORE_DIR and len(parts) > 1:
                    return bool(_LAYER_DIR_PATTERN.match(parts[1]))
                return False
            violations = [v for v in violations if _in_sovereign_scope(v)]
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f'Failed to get violations from StructureEnforcerAgent: {e}')
            return {'agent': 'GravityLeakRepairAgent', 'status': 'ERROR', 'error': str(e), 'violations_found': 0, 'violations_fixed': 0}
        if not violations:
            self.logger.info('No gravity violations found - nothing to repair!')
            return {'agent': 'GravityLeakRepairAgent', 'status': 'PASS', 'violations_found': 0, 'violations_fixed': 0, 'summary': 'No gravity violations to repair'}
        self.logger.info(f'Analyzing {len(violations)} gravity violations...')
        fix_summary = {'RELOCATE': 0, 'ABSTRACT': 0, 'INJECT': 0, 'REMOVE': 0, 'DEFERRED': 0}
        fixes_applied = 0
        for v in violations:
            if hasattr(v, 'file_path'):
                _import_stmt = ''
                try:
                    _lines = Path(v.file_path).read_text(encoding='utf-8', errors='replace').splitlines()
                    _ln = getattr(v, 'line_number', 0) or 0
                    if 1 <= _ln <= len(_lines):
                        _import_stmt = _lines[_ln - 1].strip()
                except (OSError, UnicodeDecodeError, IndexError, AttributeError) as e:
                    self.logger.warning(f"Failed to extract import statement from {getattr(v.file_path, 'name', 'unknown')}: {e}")
                    _import_stmt = ''
                fix = self.analyze_violation(file_path=v.file_path, import_statement=_import_stmt, file_layer=getattr(v, 'source_layer', ''), import_layer=getattr(v, 'target_layer', ''))
            else:
                _import_stmt = ''
                try:
                    _fp = v.get('file_path')
                    _ln = v.get('line_number', 0) or 0
                    if _fp and _ln:
                        _lines = Path(_fp).read_text(encoding='utf-8', errors='replace').splitlines()
                        if 1 <= _ln <= len(_lines):
                            _import_stmt = _lines[_ln - 1].strip()
                except (OSError, UnicodeDecodeError, IndexError, TypeError) as e:
                    self.logger.warning(f"Failed to extract import statement from {v.get('file_path', 'unknown')}: {e}")
                    _import_stmt = ''
                fix = self.analyze_violation(file_path=v.get('file_path'), import_statement=_import_stmt, file_layer=v.get('file_layer', ''), import_layer=v.get('import_layer', ''))
            fix_summary.setdefault(fix.fix_type, 0)
            fix_summary[fix.fix_type] += 1
            result = self.apply_fix(fix, dry_run=dry_run, privileged_mutation_context=not dry_run)
            if isinstance(result, dict) and result.get('status') == 'fixed':
                fixes_applied += 1
        self.logger.info('\nGravity Leak Repair Summary:')
        self.logger.info(f'  Total violations: {len(violations)}')
        self.logger.info(f'  Analyzed: {len(violations)}')
        self.logger.info('  Fix types:')
        for fix_type, count in fix_summary.items():
            if count > 0:
                self.logger.info(f'    {fix_type}: {count}')
        self.logger.info(f'  Fixes applied: {fixes_applied}')
        return {'agent': 'GravityLeakRepairAgent', 'violations_found': len(violations), 'violations_fixed': fixes_applied, 'fix_summary': fix_summary, 'status': 'PASS' if fixes_applied == len(violations) else 'PARTIAL', 'dry_run': dry_run, 'execute': execute, 'summary': f'Analyzed {len(violations)} violations, applied {fixes_applied} fixes'}

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal gravity leak violations using meta-learning enhanced pattern.

        [META-LEARNING] Uses ml_enhanced_heal for:
        - Pattern recall from successful gravity fixes
        - Depth tracking to prevent infinite loops
        - Storage of successful patterns for future use

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, upward_import)
                - path: Path to the violating file
                - import_statement: The problematic import
                - file_layer: Layer of the file
                - import_layer: Layer being imported

        Returns:
            Dictionary with healing results following standard_heal format.
        """

        # guardian: allow-type-erasure
        def _heal_gravity_violation(violation: dict) -> dict:
            path = violation.get('path', '')
            import_statement = violation.get('import_statement', '')
            file_layer = violation.get('file_layer', '')
            import_layer = violation.get('import_layer', '')
            if path and import_statement:
                try:
                    fix = self.analyze_violation(file_path=Path(path), import_statement=import_statement, file_layer=file_layer, import_layer=import_layer)
                    result = self.apply_fix(fix, dry_run=False)
                    if result.get('status') == 'fixed':
                        healing_result = {'status': 'fixed', 'fix_type': fix.fix_type, 'new_import': fix.new_import, 'rationale': fix.rationale, 'line_number': fix.line_number}
                        self.context.store_healing_pattern(violation, healing_result, agent='GravityLeakRepairAgent')
                        return {'violations_fixed': 1, 'violations_found': 1, 'errors': 0, 'skipped': 0}
                # guardian: allow-silent-swallow
                except Exception as e:
                    self.logger.error(f'[GRAVITY_LEAK_REPAIR] Failed to heal: {e}')
                    return {'violations_fixed': 0, 'violations_found': 1, 'errors': 1, 'skipped': 0}
            return {'violations_fixed': 0, 'violations_found': 1, 'errors': 0, 'skipped': 1}
        return self.ml_enhanced_heal(violation, _heal_gravity_violation)

def get_GravityLeakRepairAgent(project_root: Path=None) -> GravityLeakRepairAgent:
    """Factory function for GravityLeakRepairAgent."""
    return GravityLeakRepairAgent(project_root=project_root)
