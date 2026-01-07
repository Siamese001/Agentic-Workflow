from __future__ import annotations
import asyncio
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import hashlib
import logging
import os
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.L1_cognition.thought_engine.validation_protocol import ValidationProtocol

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
Logger: Any = logging.getLogger(__name__)

class CanonBaseAgent(HealerMixin):
    """Base class for all validation agents."""
    VERIFICATION_REGISTRY: dict = {}
    _registry_built: bool = False

    @classmethod
    def _init_registry(cls, ctx: ValidationProtocol):
        """
        Builds the registry once to avoid repetitive agent instantiation.
        
        GRAVITY COMPLIANCE: Uses dynamic import for L2 StructuralEngineerAgent
        to avoid L1→L2 static import violation.
        """
        if cls._registry_built:
            return
        from agentic_core.canon_agents_core import SystemArchitect
        from agentic_core.L1_cognition.thought_engine.PatternEnforcerAgent import PatternEnforcerAgent
        from agentic_core.L1_cognition.thought_engine.DocumentationAgent import DocumentationAgent
        from agentic_core.canon_agents_quality import NamingAgent, SafetyInspectorAgent
        from agentic_core.L1_cognition.thought_engine.BudgetAgent import BudgetAgent
        from agentic_core.L1_cognition.thought_engine.TypeMechanicAgent import TypeMechanicAgent
        from agentic_core.canon_agents_syntax import CodeJanitor, DependencySentinelAgent
        
        # GRAVITY FIXED (Intra-Core): Dynamic import for L2 dependency
        import importlib
        _struct_mod = importlib.import_module('agentic_core.L2_execution.ToolRegistry.StructuralEngineerAgent')
        StructuralEngineerAgent = getattr(_struct_mod, 'StructuralEngineerAgent')
        arch = SystemArchitect(ctx)
        budget = BudgetAgent(ctx)
        janitor = CodeJanitor(ctx)
        deps = DependencySentinelAgent(ctx)
        docs = DocumentationAgent(ctx)
        naming = NamingAgent(ctx)
        pattern = PatternEnforcerAgent(ctx)
        safety = SafetyInspectorAgent(ctx)
        struct = StructuralEngineerAgent(ctx)
        type_mech = TypeMechanicAgent(ctx)
        cls.VERIFICATION_REGISTRY = {0: safety.check_key_00_no_hardcoded_secrets, 1: safety.check_key_01_no_todo_fixme, 2: safety.check_key_02_no_print_statements, 3: safety.check_key_03_no_debugger_statements, 4: safety.check_key_04_no_empty_except_blocks, 5: safety.check_key_05_no_bare_except, 6: safety.check_key_06_no_eval_exec, 7: deps.check_key_07_no_star_imports, 8: deps.check_key_08_no_relative_imports, 10: janitor.check_key_10_no_long_lines, 11: janitor.check_key_11_no_trailing_whitespace, 12: janitor.check_key_12_no_missing_newline, 13: janitor.check_key_13_no_tabs, 14: deps.check_key_14_no_duplicate_imports, 15: janitor.check_key_15_no_magic_numbers, 16: janitor.check_key_16_no_deep_nesting, 17: budget.check_key_17_no_large_functions, 18: struct.check_key_18_no_many_parameters, 19: budget.check_key_19_no_complex_functions, 20: struct.check_key_20_no_large_classes, 21: docs.check_key_21_no_missing_docstrings, 22: type_mech.check_key_22_no_missing_type_hints, 23: type_mech.check_key_23_no_unreachable_code, 24: type_mech.check_key_24_no_unused_variables, 25: struct.check_key_25_no_global_variables, 26: pattern.check_key_26_no_mutable_defaults, 27: pattern.check_key_27_prefer_str_join, 28: pattern.check_key_28_no_bare_except, 29: pattern.check_key_29_no_assert_in_prod, 30: pattern.check_key_30_prefer_fstrings, 31: pattern.check_key_31_no_complex_comprehensions, 32: pattern.check_key_32_no_dict_keys_check, 33: pattern.check_key_33_no_float_equality, 34: pattern.check_key_34_use_is_for_none, 36: pattern.check_key_36_no_shadowed_builtins, 37: pattern.check_key_37_no_redundant_self, 38: pattern.check_key_38_prefer_comprehensions, 39: pattern.check_key_39_no_useless_return, 40: arch.check_key_40_no_metaclasses, 41: arch.check_key_41_scoped_nesting, 42: struct.check_key_42_no_large_files, 43: struct.check_key_43_class_density, 44: deps.check_key_44_no_circular_imports, 45: deps.check_key_45_no_unused_imports, 46: struct.check_key_46_no_duplicate_code, 47: naming.check_key_47_naming_conventions, 49: arch.check_key_49_directory_depth, 50: arch.check_key_50_law_of_void}
        cls._registry_built = True

    def __init__(self, context: ValidationProtocol = None, name: str = None, layer: str = None):
        self.ctx = context
        self.name = name or self.__class__.__name__
        self.layer = layer

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return 'CRITICAL_FAIL' not in self.ctx.signals

    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except IOError as e:
            Logger.warning(f'Could not read file {file_path} for hashing: {e}')
            return ''

    def check_cache(self, file_path: str, key: int) -> Optional[dict]:
        """Check Redis cache for validation result."""
        file_hash: Any = self.get_file_hash(file_path)
        if not file_hash:
            return None
        cache_key: Any = f'{self.name}:{key}:{file_hash}'
        return self.ctx.services.get_cached_result(cache_key)

    def store_cache(self, file_path: str, key: int, result: dict) -> Any:
        """Store validation result in Redis cache."""
        file_hash: Any = self.get_file_hash(file_path)
        if not file_hash:
            return
        cache_key: Any = f'{self.name}:{key}:{file_hash}'
        self.ctx.services.cache_result(cache_key, result)

    async def smart_fix(self, file_path: str, violation_key: int) -> bool:
        """Trigger an LLM-based fix for a specific Violation."""
        if not self.ctx.intelligence_enabled:
            Logger.debug('Intelligence not enabled, skipping smart fix.')
            return False
        if not self.ctx.can_attempt_healing(file_path):
            Logger.debug(f'Cannot attempt healing for {file_path}.')
            return False
        self.__class__._init_registry(self.ctx)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code: Any = f.read()
            current_code: Any = original_code
            check_func: Any = self.VERIFICATION_REGISTRY.get(violation_key)
            if not check_func:
                Logger.warning(f'No check function found for Violation key {violation_key}.')
                return False
            violation_details: Any = ''
            res: Any = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
            if not res[0]:
                relevant: Any = [d for d in res[1] if str(d).startswith(file_path)]
                if relevant:
                    max_violations_shown: Any = int(os.getenv('MAX_VIOLATIONS_SHOWN', '8'))
                    violation_details: Any = '\nSpecific Violations:\n' + '\n'.join(map(str, relevant[:max_violations_shown]))
            violation_desc: Any = f'{self.name} Key {violation_key} Violation in {file_path}'
            similar_patterns: Any = self.ctx.services.find_similar_patterns(violation_desc)
            reference_fix: Any = None
            if similar_patterns:
                best_match: Any = similar_patterns[0]
                if best_match['similarity'] > 0.85:
                    reference_fix: Any = f"\n\nReference Fix (similarity: {best_match['similarity']:.2f}):\n{best_match['fix']}"
            max_rounds: Any = int(os.getenv('MAX_HEALING_ROUNDS', '5'))
            previous_failure: Any = None
            for round_num in range(1, max_rounds + 1):
                print(f'      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}', flush=True)
                task_parts: Any = [f'Fix Key {violation_key} Violation in {file_path}.']
                if violation_details:
                    task_parts.append(violation_details)
                if reference_fix:
                    task_parts.append(reference_fix)
                Task: Any = '\n'.join(task_parts)
                fixed_code: Any = await self.ctx.resilient_mutation(agent_name=self.name, Task=Task, code=current_code, file_path=file_path, round_num=round_num, previous_failure=previous_failure)
                if fixed_code == current_code:
                    print(f'      [!] No changes made in Round {round_num}', flush=True)
                    previous_failure: Any = 'No changes were made to the code.'
                    continue
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                res: Any = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                if res[0]:
                    print(f'      [OK] Healing successful in Round {round_num}', flush=True)
                    self.ctx.record_healing_attempt(file_path, success=True)
                    self.ctx.modified_files.add(file_path)
                    if file_path not in self.ctx.healing_history:
                        self.ctx.healing_history[file_path] = []
                    self.ctx.healing_history[file_path].append(f'Key{violation_key}')
                    self.ctx.services.store_healing_pattern(Violation=violation_desc, fix=fixed_code[:500], success_rate=1.0)
                    return True
                else:
                    relevant: Any = [d for d in res[1] if str(d).startswith(file_path)]
                    if relevant:
                        previous_failure: Any = 'Fix attempt failed. Remaining violations:\n' + '\n'.join(map(str, relevant[:3]))
                    else:
                        previous_failure: Any = 'Fix attempt did not resolve the Violation (no specific file violations found).'
                current_code: Any = fixed_code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            print(f'      [X] Healing failed after {max_rounds} rounds - reverting {os.path.basename(file_path)}', flush=True)
            self.ctx.record_healing_attempt(file_path, success=False)
            return False
        except Exception as e:
            Logger.error(f'Healing error for {file_path}, key {violation_key}: {e}', exc_info=True)
            print(f'      [ALERT] Healing error for {os.path.basename(file_path)}: {e}', flush=True)
            return False

    def execute(self) -> Any:
        """Override in subclass."""
        raise NotImplementedError(f'{self.name}.execute() not implemented')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L1 cognition agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
