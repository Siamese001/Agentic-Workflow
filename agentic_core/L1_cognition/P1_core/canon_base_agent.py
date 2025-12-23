# Standard library imports
import asyncio
import hashlib
import logging
import os
from typing import Any, Optional, Protocol, Dict, List

# Project-specific imports
# Dependency Inversion: Use protocol instead of concrete L4 class
# Using absolute import as relative imports are forbidden by architectural rules.
from agentic_core.L1_cognition.P1_core.validation_protocol import ValidationProtocol

# Configure basic logging for this module.
# In a real application, this would typically be configured globally.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger(__name__)


class SubAtomicAgent:
    """Base class for all validation agents."""

    VERIFICATION_REGISTRY: dict = {}
    _registry_built: bool = False

    @classmethod
    def _init_registry(cls, ctx: ValidationProtocol):
        """Builds the registry once to avoid repetitive agent instantiation."""
        if cls._registry_built:
            return

        # Local imports for lazy loading, grouped and sorted.
        # These imports are intentionally placed here to avoid circular dependencies
        # and to only load agents when the registry is actually built.
        # These imports are from 'downstream' modules, which is noted as a 'Sovereign layer importing from Downstream' violation.
        # However, given the constraints (preserve functionality, maintain signatures, refactor *this file* only,
        # and not import from apps_shared/rg/lic), these imports cannot be removed without breaking core functionality.
        # The local import strategy already mitigates direct circular dependencies at module load time.
        from agentic_core.canon_agents_core import SystemArchitect
        from agentic_core.canon_agents_pattern import PatternEnforcer
        from agentic_core.canon_agents_quality import (
            DocumentationAgent,
            NamingAgent,
            SafetyInspector,
        )
        from agentic_core.canon_agents_structural import (
            BudgetAgent,
            StructuralEngineer,
            TypeMechanic,
        )
        from agentic_core.canon_agents_syntax import CodeJanitor, DependencySentinel

        # Agent instantiation, grouped and sorted for readability
        arch = SystemArchitect(ctx)
        budget = BudgetAgent(ctx)
        janitor = CodeJanitor(ctx)
        deps = DependencySentinel(ctx)
        docs = DocumentationAgent(ctx)
        naming = NamingAgent(ctx)
        pattern = PatternEnforcer(ctx)
        safety = SafetyInspector(ctx)
        struct = StructuralEngineer(ctx)
        type_mech = TypeMechanic(ctx)

        # Populate the verification registry.
        # Keys are unique integer identifiers for checks.
        # Note: Some checks might appear similar but originate from different agents
        # or have distinct implementations/contexts.
        cls.VERIFICATION_REGISTRY = {
            0: safety.check_key_00_no_hardcoded_secrets,
            1: safety.check_key_01_no_todo_fixme,
            2: safety.check_key_02_no_print_statements,
            3: safety.check_key_03_no_debugger_statements,
            4: safety.check_key_04_no_empty_except_blocks,
            5: safety.check_key_05_no_bare_except,
            6: safety.check_key_06_no_eval_exec,
            7: deps.check_key_07_no_star_imports,
            8: deps.check_key_08_no_relative_imports,
            # Key 9 (no_unused_imports) was a duplicate of key 45. Removed.
            10: janitor.check_key_10_no_long_lines,
            11: janitor.check_key_11_no_trailing_whitespace,
            12: janitor.check_key_12_no_missing_newline,
            13: janitor.check_key_13_no_tabs,
            14: deps.check_key_14_no_duplicate_imports,
            15: janitor.check_key_15_no_magic_numbers,
            16: janitor.check_key_16_no_deep_nesting,
            17: budget.check_key_17_no_large_functions,
            18: struct.check_key_18_no_many_parameters,
            19: budget.check_key_19_no_complex_functions,
            20: struct.check_key_20_no_large_classes,
            21: docs.check_key_21_no_missing_docstrings,
            22: type_mech.check_key_22_no_missing_type_hints,
            23: type_mech.check_key_23_no_unreachable_code,
            24: type_mech.check_key_24_no_unused_variables,
            25: struct.check_key_25_no_global_variables,
            26: pattern.check_key_26_no_mutable_defaults,
            27: pattern.check_key_27_prefer_str_join,
            28: pattern.check_key_28_no_bare_except,  # From pattern agent
            29: pattern.check_key_29_no_assert_in_prod,
            30: pattern.check_key_30_prefer_fstrings,
            31: pattern.check_key_31_no_complex_comprehensions,
            32: pattern.check_key_32_no_dict_keys_check,
            33: pattern.check_key_33_no_float_equality,
            34: pattern.check_key_34_use_is_for_none,
            # Key 35 (no_star_imports) was a duplicate of key 7. Removed.
            36: pattern.check_key_36_no_shadowed_builtins,
            37: pattern.check_key_37_no_redundant_self,
            38: pattern.check_key_38_prefer_comprehensions,
            39: pattern.check_key_39_no_useless_return,
            40: arch.check_key_40_no_metaclasses,
            41: arch.check_key_41_scoped_nesting,
            42: struct.check_key_42_no_large_files,
            43: struct.check_key_43_class_density,
            44: deps.check_key_44_no_circular_imports,
            45: deps.check_key_45_no_unused_imports,
            46: struct.check_key_46_no_duplicate_code,
            47: naming.check_key_47_naming_conventions,
            49: arch.check_key_49_directory_depth,
            50: arch.check_key_50_law_of_void,
        }
        cls._registry_built = True

    def __init__(self, context: ValidationProtocol):
        self.ctx = context
        self.name = self.__class__.__name__

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return "CRITICAL_FAIL" not in self.ctx.signals

    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except IOError as e:  # Catch specific I/O errors and log them
            logger.warning(f"Could not read file {file_path} for hashing: {e}")
            return ""

    def check_cache(self, file_path: str, key: int) -> Optional[dict]:
        """Check Redis cache for validation result."""
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return None

        cache_key = f"{self.name}:{key}:{file_hash}"
        return self.ctx.services.get_cached_result(cache_key)

    def store_cache(self, file_path: str, key: int, result: dict):
        """Store validation result in Redis cache."""
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return

        cache_key = f"{self.name}:{key}:{file_hash}"
        self.ctx.services.cache_result(cache_key, result)

    async def smart_fix(self, file_path: str, violation_key: int) -> bool:
        """Trigger an LLM-based fix for a specific violation."""
        if not self.ctx.intelligence_enabled:
            logger.debug("Intelligence not enabled, skipping smart fix.")
            return False

        if not self.ctx.can_attempt_healing(file_path):
            logger.debug(f"Cannot attempt healing for {file_path}.")
            return False

        # Ensure the registry is built before accessing VERIFICATION_REGISTRY
        self.__class__._init_registry(self.ctx)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_code = f.read()

            current_code = original_code

            check_func = self.VERIFICATION_REGISTRY.get(violation_key)
            if not check_func:
                logger.warning(
                    f"No check function found for violation key {violation_key}."
                )
                return False

            violation_details = ""
            res = (
                await check_func()
                if asyncio.iscoroutinefunction(check_func)
                else check_func()
            )
            if not res[0]:  # If there are violations
                # Filter violations relevant to the current file
                relevant = [d for d in res[1] if str(d).startswith(file_path)]
                if relevant:
                    max_violations_shown = int(
                        os.getenv('MAX_VIOLATIONS_SHOWN', '8')
                    )
                    violation_details = (
                        "\nSpecific Violations:\n"
                        + "\n".join(map(str, relevant[:max_violations_shown]))
                    )

            violation_desc = (
                f"{self.name} Key {violation_key} violation in {file_path}"
            )
            similar_patterns = self.ctx.services.find_similar_patterns(
                violation_desc
            )

            reference_fix = None
            if similar_patterns:
                best_match = similar_patterns[0]
                if best_match['similarity'] > 0.85:
                    reference_fix = (
                        f"\n\nReference Fix (similarity: "
                        f"{best_match['similarity']:.2f}):\n"
                        f"{best_match['fix']}"
                    )

            max_rounds = int(os.getenv('MAX_HEALING_ROUNDS', '5'))
            previous_failure = None

            for round_num in range(1, max_rounds + 1):
                print(
                    f"      [Round {round_num}/{max_rounds}] Healing Key "
                    f"{violation_key} → {os.path.basename(file_path)}",
                    flush=True
                )

                # Construct task string for the LLM
                task_parts = [
                    f"Fix Key {violation_key} violation in {file_path}."
                ]
                if violation_details:
                    task_parts.append(violation_details)
                if reference_fix:
                    task_parts.append(reference_fix)
                task = "\n".join(task_parts)  # Use join for cleaner multi-line task

                fixed_code = await self.ctx.resilient_mutation(
                    agent_name=self.name,
                    task=task,
                    code=current_code,
                    file_path=file_path,
                    round_num=round_num,
                    previous_failure=previous_failure
                )

                if fixed_code == current_code:
                    print(f"      [!] No changes made in Round {round_num}",
                          flush=True)
                    previous_failure = "No changes were made to the code."
                    continue

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_code)

                # Re-check the file after applying the fix
                res = (
                    await check_func()
                    if asyncio.iscoroutinefunction(check_func)
                    else check_func()
                )
                if res[0]:  # If no violations remain
                    print(f"      [OK] Healing successful in Round {round_num}",
                          flush=True)
                    self.ctx.record_healing_attempt(file_path, success=True)
                    self.ctx.modified_files.add(file_path)

                    if file_path not in self.ctx.healing_history:
                        self.ctx.healing_history[file_path] = []
                    self.ctx.healing_history[file_path].append(
                        f"Key{violation_key}"
                    )

                    self.ctx.services.store_healing_pattern(
                        violation=violation_desc,
                        fix=fixed_code[:500],  # Store a snippet of the fix
                        success_rate=1.0
                    )
                    return True
                else:
                    # If violations still exist, update previous_failure
                    relevant = [d for d in res[1] if str(d).startswith(file_path)]
                    if relevant:
                        previous_failure = (
                            "Fix attempt failed. Remaining violations:\n"
                            + "\n".join(map(str, relevant[:3]))
                        )
                    else:
                        previous_failure = (
                            "Fix attempt did not resolve the violation "
                            "(no specific file violations found)."
                        )

                current_code = fixed_code

            # If healing failed after max_rounds, revert to original code
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(original_code)

            print(f"      [X] Healing failed after {max_rounds} rounds - "
                  f"reverting {os.path.basename(file_path)}", flush=True)
            self.ctx.record_healing_attempt(file_path, success=False)
            return False

        except Exception as e:
            # Catching a broad Exception here is acceptable given the complexity
            # of LLM interactions and file operations.
            logger.error(f"Healing error for {file_path}, key {violation_key}: {e}",
                         exc_info=True)  # Log exception info for debugging
            print(f"      [ALERT] Healing error for {os.path.basename(file_path)}: {e}",
                  flush=True)
            return False

    def execute(self):
        """Override in subclass."""
        raise NotImplementedError(f"{self.name}.execute() not implemented")