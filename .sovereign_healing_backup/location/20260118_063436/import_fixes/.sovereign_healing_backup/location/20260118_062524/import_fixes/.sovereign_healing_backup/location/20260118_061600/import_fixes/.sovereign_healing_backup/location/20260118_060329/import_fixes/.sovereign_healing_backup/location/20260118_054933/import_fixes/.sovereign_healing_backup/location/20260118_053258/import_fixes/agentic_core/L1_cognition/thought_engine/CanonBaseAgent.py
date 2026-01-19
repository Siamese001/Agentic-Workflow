"""CanonBaseAgent - Base class for all validation agents.

Provides shared infrastructure for Canon validation agents including:
- Verification registry management
- File hashing and caching
- LLM-based smart fix capabilities
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from typing import Any, Dict, List, Optional, Set

from agentic_core.L1_cognition.thought_engine.validation_protocol import ValidationProtocol

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
Logger = logging.getLogger(__name__)

class CanonBaseAgent(HealerMixin):
    """
    Base class for all Canon validation agents.
    
    Provides shared infrastructure for validation including:
        - Verification registry with check functions for all Canon keys.
        - File hashing for cache invalidation.
        - Redis caching for validation results.
        - LLM-based smart fix capabilities with retry logic.
    
    Class Attributes:
        VERIFICATION_REGISTRY: Dict mapping Canon keys to check functions.
        _registry_built: Flag indicating if registry has been initialized.
    
    Instance Attributes:
        ctx: ValidationContext for file access and reporting.
        name: Agent name for logging and reporting.
        layer: Optional layer identifier.
    """
    VERIFICATION_REGISTRY: Dict[int, Any] = {}
    _registry_built: bool = False

    @classmethod
    def _init_registry(cls, ctx: ValidationProtocol) -> None:
        """
        Build the verification registry once.
        
        Initializes VERIFICATION_REGISTRY with check functions for all Canon keys.
        Uses dynamic import for L2 StructuralEngineerAgent to avoid gravity violation.
        
        Args:
            ctx: ValidationContext for agent initialization.
        """
        if cls._registry_built:
            return
        from agentic_core.canon_agents_core import SystemArchitect
        from agentic_core.L1_cognition.thought_engine.PatternEnforcerAgent import PatternEnforcerAgent
        from agentic_core.L1_cognition.thought_engine.DocumentationAgent import DocumentationAgent
        from agentic_core.canon_agents_quality import NamingAgent, SafetyInspectorAgent
        from archives.void_violations.BudgetAgent import BudgetAgent
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

    def __init__(
        self,
        context: Optional[ValidationProtocol] = None,
        name: Optional[str] = None,
        layer: Optional[str] = None
    ) -> None:
        """
        Initialize the Canon base agent.
        
        Args:
            context: ValidationContext for file access and reporting.
            name: Agent name (defaults to class name).
            layer: Optional layer identifier for logging.
        """
        self.ctx = context
        self.name = name or self.__class__.__name__
        self.layer = layer

    def can_run(self) -> bool:
        """
        Check if agent can run.
        
        Returns:
            True unless CRITICAL_FAIL signal is present in context.
        """
        return 'CRITICAL_FAIL' not in self.ctx.signals

    def get_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to file to hash.
            
        Returns:
            Hex digest of SHA-256 hash, or empty string on error.
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except IOError as e:
            Logger.warning(f'Could not read file {file_path} for hashing: {e}')
            return ''

    def check_cache(self, file_path: str, key: int) -> Optional[Dict[str, Any]]:
        """
        Check Redis cache for validation result.
        
        Args:
            file_path: Path to file being validated.
            key: Canon key number.
            
        Returns:
            Cached result dict or None if not cached.
        """
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return None
        cache_key: Any = f'{self.name}:{key}:{file_hash}'
        return self.ctx.services.get_cached_result(cache_key)

    def store_cache(self, file_path: str, key: int, result: Dict[str, Any]) -> None:
        """
        Store validation result in Redis cache.
        
        Args:
            file_path: Path to file being validated.
            key: Canon key number.
            result: Validation result to cache.
        """
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return
        cache_key: Any = f'{self.name}:{key}:{file_hash}'
        self.ctx.services.cache_result(cache_key, result)

    async def _run_check_func(self, check_func: Any) -> Tuple[bool, List[Any]]:
        """Run a check function (sync or async) and return result."""
        if asyncio.iscoroutinefunction(check_func):
            return await check_func()
        return check_func()

    def _get_violation_details(self, res: Tuple[bool, List[Any]], file_path: str) -> str:
        """Extract violation details relevant to a specific file."""
        if res[0]:
            return ''
        relevant = [d for d in res[1] if str(d).startswith(file_path)]
        if not relevant:
            return ''
        max_shown = int(os.getenv('MAX_VIOLATIONS_SHOWN', '8'))
        return '\nSpecific Violations:\n' + '\n'.join(map(str, relevant[:max_shown]))

    def _get_reference_fix(self, violation_desc: str) -> Optional[str]:
        """Find similar patterns and return reference fix if available."""
        similar = self.ctx.services.find_similar_patterns(violation_desc)
        if similar and similar[0]['similarity'] > 0.85:
            best = similar[0]
            return f"\n\nReference Fix (similarity: {best['similarity']:.2f}):\n{best['fix']}"
        return None

    def _build_task(self, violation_key: int, file_path: str, details: str, ref_fix: Optional[str]) -> str:
        """Build the task description for LLM healing."""
        parts = [f'Fix Key {violation_key} Violation in {file_path}.']
        if details:
            parts.append(details)
        if ref_fix:
            parts.append(ref_fix)
        return '\n'.join(parts)

    def _record_success(self, file_path: str, violation_key: int, violation_desc: str, fixed_code: str) -> None:
        """Record a successful healing attempt."""
        self.ctx.record_healing_attempt(file_path, success=True)
        self.ctx.modified_files.add(file_path)
        if file_path not in self.ctx.healing_history:
            self.ctx.healing_history[file_path] = []
        self.ctx.healing_history[file_path].append(f'Key{violation_key}')
        self.ctx.services.store_healing_pattern(Violation=violation_desc, fix=fixed_code[:500], success_rate=1.0)

    async def smart_fix(self, file_path: str, violation_key: int) -> bool:
        """Trigger LLM-based fix for a specific violation.
        
        Uses resilient mutation with retry logic to fix violations.
        Records healing attempts and stores successful patterns.
        
        Args:
            file_path: Path to file with violation.
            violation_key: Canon key number of the violation.
            
        Returns:
            True if fix was successful, False otherwise.
        """
        if not self.ctx.intelligence_enabled:
            Logger.debug('Intelligence not enabled, skipping smart fix.')
            return False
        if not self.ctx.can_attempt_healing(file_path):
            Logger.debug(f'Cannot attempt healing for {file_path}.')
            return False
        
        self.__class__._init_registry(self.ctx)
        check_func = self.VERIFICATION_REGISTRY.get(violation_key)
        if not check_func:
            Logger.warning(f'No check function found for Violation key {violation_key}.')
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            res = await self._run_check_func(check_func)
            violation_details = self._get_violation_details(res, file_path)
            violation_desc = f'{self.name} Key {violation_key} Violation in {file_path}'
            reference_fix = self._get_reference_fix(violation_desc)
            
            max_rounds = int(os.getenv('MAX_HEALING_ROUNDS', '5'))
            current_code = original_code
            previous_failure: Optional[str] = None

            for round_num in range(1, max_rounds + 1):
                print(f'      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}', flush=True)
                
                task = self._build_task(violation_key, file_path, violation_details, reference_fix)
                fixed_code = await self.ctx.resilient_mutation(
                    agent_name=self.name, Task=task, code=current_code,
                    file_path=file_path, round_num=round_num, previous_failure=previous_failure
                )
                
                if fixed_code == current_code:
                    print(f'      [!] No changes made in Round {round_num}', flush=True)
                    previous_failure = 'No changes were made to the code.'
                    continue
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                
                res = await self._run_check_func(check_func)
                if res[0]:
                    print(f'      [OK] Healing successful in Round {round_num}', flush=True)
                    self._record_success(file_path, violation_key, violation_desc, fixed_code)
                    return True
                
                relevant = [d for d in res[1] if str(d).startswith(file_path)]
                previous_failure = ('Fix attempt failed. Remaining violations:\n' + '\n'.join(map(str, relevant[:3]))
                                   if relevant else 'Fix attempt did not resolve the Violation.')
                current_code = fixed_code

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            print(f'      [X] Healing failed after {max_rounds} rounds - reverting {os.path.basename(file_path)}', flush=True)
            self.ctx.record_healing_attempt(file_path, success=False)
            return False

        except Exception as e:
            Logger.error(f'Healing error for {file_path}, key {violation_key}: {e}', exc_info=True)
            print(f'      [ALERT] Healing error for {os.path.basename(file_path)}: {e}', flush=True)
            return False

    def execute(self) -> None:
        """
        Execute validation checks.
        
        Must be overridden in subclass to implement specific checks.
        
        Raises:
            NotImplementedError: Always, as this is abstract.
        """
        raise NotImplementedError(f'{self.name}.execute() not implemented')

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """
        Execute L1 cognition healing operations.
        
        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum allowed recursion depth.
            _call_path: Set of agent names already in call chain.
            
        Returns:
            Dict with keys: violations, fixed, errors, skipped.
        """
        super().heal_repository()

        if _call_path is None:
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
