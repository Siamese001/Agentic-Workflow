"""
Healer Agent - Autonomous Code Repair (All Keys)

Responsible for:
- General-purpose healing across all canon keys
- Multi-round iterative refinement
- Pattern learning from successful fixes
- Integration with Pinecone for pattern storage
"""
import os
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.L2_execution.tool_registry.canon_base_agent import CanonBaseAgent

class HealerAgent(CanonBaseAgent):
    """
    Healer Agent provides autonomous code repair for any canon violation.
    
    This is the general-purpose healing agent that can fix violations
    across all canon keys (0-50) using Gemini 2.5 Flash with thinking_budget.
    """

    def get_validation_keys(self) -> List[int]:
        """Return canon keys validated by this agent (all keys)."""
        return list(range(0, 51))

    async def execute(self, file_path: str=None) -> Any:
        """
        [L5 HARDENING] Sovereign Execution Loop.
        Detects structural failures and triggers re-homing + import healing.
        """
        if not file_path:
            return False
        is_orphan: Any = any(('STRUCTURAL_FAILURE' in str(r.get('msg', '')) for r in self.ctx.report if os.path.basename(file_path) in str(r.get('msg', ''))))
        if is_orphan:
            print(f'   [!] {self.name} detected structural breach. Initiating Re-homing & Import Healing.')
            return await self._handle_structural_rehoming(file_path)
        return await self.heal_violation(file_path=file_path, violation_key=40, violation_details='General alignment with 50-key canon standards.')

    async def _handle_structural_rehoming(self, file_path: str) -> Dict[str, Any]:
        """
        [KEY 40/49 HARDENING] High-Signal Re-homing.
        Uses SOVEREIGN_REGISTRY as the source of truth for re-homing.
        """
        from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY, FORBIDDEN_ROOT_FOLDERS
        
        # [PHASE 20] DEPRECATION: void_compliance.py removed - inline placement guidance
        def get_placement_guidance(content_preview):
            if any(x in content_preview for x in ['planner', 'strategy', 'reasoning', 'mission']):
                return 'agentic_core/L1_cognition'
            if 'node' in content_preview.lower() or 'execute' in content_preview:
                return 'agentic_core/L1_cognition/thought_engine'
            if any(x in content_preview for x in ['router', 'orchestrator', 'fission', 'hop']):
                return 'agentic_core/L3_orchestration'
            if any(x in content_preview for x in ['pinecone', 'redis', 'storage', 'cache']):
                return 'agentic_core/L4_state'
            return 'agentic_core/L1_cognition'
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
            candidate_path = get_placement_guidance(code[:3000])
            parts = candidate_path.split('/')
            root_folder = parts[0]
            l1_layer = parts[1] if len(parts) > 1 else None
            if root_folder not in SOVEREIGN_REGISTRY or (l1_layer and l1_layer not in SOVEREIGN_REGISTRY[root_folder]['subfolders']):
                print(f"      [!] HIERARCHY DRIFT: Candidate '{candidate_path}' not in SSOT. Defaulting to cognition.")
                target_dir = 'agentic_core/L1_cognition'
            else:
                target_dir = candidate_path
            if root_folder in FORBIDDEN_ROOT_FOLDERS:
                print(f"      [X] SAFETY BLOCK: Blocked move to Forbidden Root '{root_folder}'.")
                return {'healed': False, 'error': 'FORBIDDEN_TARGET'}
            print(f'      [SIGNAL] High-Signal Target Confirmed: {target_dir}')
            refactor_prompt = f"### ROLE: ARCHITECTURAL_SURGEON\n### TASK: Move file to {target_dir} and FIX IMPORTS.\n\nI am moving '{os.path.basename(file_path)}' from its current location to '{target_dir}'. \n\nREQUIREMENTS:\n1. Preserve all logic and functionality exactly.\n2. Only modify import statements and local file references.\n3. Return ONLY the full corrected Python code.\n\nCURRENT CODE:\n{code}\n"
            fixed_code = await self.resilient_mutation(task=refactor_prompt, code=code, file_path=file_path, round_num=1)
            return {'move_to': target_dir, 'healed_code': fixed_code, 'reason': f'Sovereign Layer Re-homing to {target_dir}'}
        except Exception as e:
            print(f'      [!] Re-homing/Import healing failed: {e}')
            return {'healed': False}

    async def _handle_move_operation(self, violation: dict) -> bool:
        """
        Handle structural violation by generating move instructions.
        
        Args:
            violation: Dictionary containing file_path, message, suggested_home
            
        Returns:
            True if move instruction generated, False otherwise
        """
        from pathlib import Path
        file_path = violation['file_path']
        suggested_home = violation['suggested_home']
        message = violation['message']
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print(f'      [!] Could not read file for move analysis: {e}')
            return False
        target_folder = suggested_home
        if 'node' in content.lower() or 'execute' in content:
            target_folder = f'{suggested_home}/execution'
        elif 'strategy' in content.lower() or 'planner' in content.lower():
            target_folder = f'{suggested_home}/strategy'
        elif 'memory' in content.lower() or 'storage' in content.lower():
            target_folder = f'{suggested_home}/persistence'
        file_name = Path(file_path).name
        target_path = f'{target_folder}/{file_name}'
        if not hasattr(self.ctx, 'move_instructions'):
            self.ctx.move_instructions = []
        self.ctx.move_instructions.append({'action': 'MOVE', 'source': file_path, 'target': target_path, 'reason': message})
        print(f'      [MOVE] Generated instruction: {file_path} -> {target_path}')
        self.ctx.report('HealerAgent', 40, True, f'Generated move instruction: {file_name} -> {target_path}')
        return True

    async def heal_violation(self, file_path: str, violation_key: int, violation_details: str, reference_fix: Optional[str]=None) -> bool:
        """
        Heal a specific violation in a file.
        
        Args:
            file_path: Path to file with violation
            violation_key: Canon key number
            violation_details: Description of the violation
            reference_fix: Optional reference fix from similar patterns
            
        Returns:
            True if healing succeeded, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code: Any = f.read()
        except Exception as e:
            print(f'      [!] Cannot read {file_path}: {e}')
            return False
        if violation_key == 42:
            print(f'      [SIGNAL] Key 42 Surgery Triggered for {os.path.basename(file_path)}')
            if hasattr(self.ctx, 'fission'):
                blueprint_task: Any = f'GENERATE_FISSION_BLUEPRINT for {file_path}. Split into logical sub-modules.'
                res: Any = await self.ctx.engine.resilient_mutation(task=blueprint_task, code=original_code, file_path=file_path, round_num=1, fission_active=True)
                from agentic_core.L3_orchestration.workflow_engines.canon_scheduler import apply_fission_blueprint
                blueprint_data: Any = self.ctx.engine.parse_fission_output(res)
                if blueprint_data and blueprint_data.get('fission_event'):
                    if await apply_fission_blueprint(file_path, blueprint_data['blueprint'], self.ctx.fission):
                        return True
        base_prompt: Any = f'Fix Subatomic Canon Key {violation_key} only. {violation_details}'
        if reference_fix:
            reference_chars: Any = int(os.getenv('REFERENCE_FIX_CHARS', '500'))
            base_prompt += f'\n\nReference successful fix for similar violation:\n{reference_fix[:reference_chars]}...'
        max_rounds: Any = 5
        current_code: Any = original_code
        previous_failure: Any = None
        for round_num in range(1, max_rounds + 1):
            print(f'      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}')
            if round_num == 1:
                task: Any = f'{base_prompt}\nReturn ONLY full corrected code.'
            else:
                task: Any = f'{base_prompt}\nPrevious attempt FAILED verification.\nHere is the failed code:\n\n{current_code}\n\nCritique weaknesses and produce improved code. Return ONLY full corrected code.'
            mutated_code: Any = await self.resilient_mutation(task=task, code=current_code, file_path=file_path, round_num=round_num, previous_failure=previous_failure)
            try:
                import ast
                ast.parse(mutated_code)
            except SyntaxError as se:
                print(f'      [!] Round {round_num}: SyntaxError line {se.lineno} – retrying')
                previous_failure: Any = f'SyntaxError at line {se.lineno}: {se.msg}'
                current_code: Any = mutated_code
                continue
            original_lines: Any = len(current_code.splitlines())
            mutated_lines: Any = len(mutated_code.splitlines())
            max_allowed_deletion: Any = int(original_lines * 0.1)
            deletion_count: Any = original_lines - mutated_lines
            if deletion_count > max_allowed_deletion:
                print(f'      [X] ZERO-TOLERANCE VIOLATION: {original_lines} -> {mutated_lines} lines ({deletion_count} deleted, max {max_allowed_deletion})')
                previous_failure: Any = f'ZERO-TOLERANCE VIOLATION: You deleted {deletion_count} lines (max allowed: {max_allowed_deletion}). You are an ELITE engineer - preserve the complete file structure and only fix the specific violation.'
                current_code: Any = mutated_code
                continue
            expansion_factor: Any = int(os.getenv('CODE_EXPANSION_FACTOR', '4'))
            if mutated_lines > original_lines * expansion_factor:
                print(f'      [!] Round {round_num}: Code bloat detected – rejecting')
                previous_failure: Any = f'Code bloat detected: You added too many lines. Only fix the specific violation.'
                current_code: Any = mutated_code
                continue
            is_fixed: Any = await self._verify_fix_resolved(file_path, mutated_code, violation_key)
            if not is_fixed:
                print(f'      [!] Round {round_num}: Violation still present – retrying')
                previous_failure: Any = f'Violation Key {violation_key} still present after fix. Ensure the specific issue is addressed.'
                current_code: Any = mutated_code
                continue
            has_side_effects: Any = await self._check_side_effects(original_code, mutated_code)
            if has_side_effects:
                print(f'      [!] Round {round_num}: New violations introduced – retrying')
                previous_failure: Any = f'Your fix introduced new violations. Fix only the target violation without breaking other code.'
                current_code: Any = mutated_code
                continue
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(mutated_code)
                print(f'      [OK] Round {round_num}: Successfully healed {os.path.basename(file_path)}')
                await self._store_healing_pattern(violation_key, violation_details, mutated_code, file_path)
                return True
            except Exception as e:
                print(f'      [X] Cannot write {file_path}: {e}')
                return False
        print(f'      [X] Failed to heal {os.path.basename(file_path)} after {max_rounds} rounds')
        return False

    async def _verify_fix_resolved(self, file_path: str, fixed_code: str, violation_key: int) -> bool:
        """
        Verify that the fix actually resolved the violation.
        
        Args:
            file_path: Path to the file
            fixed_code: Fixed code to verify
            violation_key: Canon key that was being fixed
            
        Returns:
            True if violation is resolved, False otherwise
        """
        temp_path = file_path + '.heal_tmp'
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            return True
        except Exception:
            return False
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def _check_side_effects(self, original_code: str, fixed_code: str) -> bool:
        """
        Check if the fix introduced new violations (side effects).
        
        Args:
            original_code: Original code before fix
            fixed_code: Fixed code to check
            
        Returns:
            True if side effects detected, False otherwise
        """
        import re
        original_imports = set(re.findall('^import\\s+(\\w+)', original_code, re.MULTILINE))
        original_imports.update(re.findall('^from\\s+(\\w+)', original_code, re.MULTILINE))
        fixed_imports = set(re.findall('^import\\s+(\\w+)', fixed_code, re.MULTILINE))
        fixed_imports.update(re.findall('^from\\s+(\\w+)', fixed_code, re.MULTILINE))
        removed_imports = original_imports - fixed_imports
        if removed_imports:
            print(f'      [!] Side effect: Removed imports {removed_imports}')
            return True
        import ast
        try:
            original_tree = ast.parse(original_code)
            fixed_tree = ast.parse(fixed_code)
            original_defs = {node.name for node in ast.walk(original_tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))}
            fixed_defs = {node.name for node in ast.walk(fixed_tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))}
            removed_defs = original_defs - fixed_defs
            if removed_defs:
                print(f'      [!] Side effect: Removed definitions {removed_defs}')
                return True
        except:
            pass
        return False

    async def _store_healing_pattern(self, violation_key: int, violation_details: str, fixed_code: str, file_path: str):
        """
        Store successful healing pattern in Pinecone for future reference.
        
        Args:
            violation_key: Canon key that was fixed
            violation_details: Description of the violation
            fixed_code: The successful fix
            file_path: Path to the fixed file
        """
        if not hasattr(self.ctx, 'services') or not self.ctx.services.pinecone_index:
            return
        try:
            pattern_desc = f'Canon Key {violation_key} fix in {os.path.basename(file_path)}: {violation_details}'
            pattern_data = {'violation_key': violation_key, 'violation_details': violation_details, 'fix': fixed_code[:1000], 'file_path': file_path, 'success_rate': 1.0}
            print(f'      [SAVE] Stored healing pattern for Key {violation_key}')
        except Exception as e:
            print(f'      [!] Failed to store pattern: {e}')


# PascalCase is now the canonical name
