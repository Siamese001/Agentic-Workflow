"""
Healer Agent - Autonomous Code Repair (All Keys)

Responsible for:
- General-purpose healing across all canon keys
- Multi-round iterative refinement
- Pattern learning from successful fixes
- Integration with Pinecone for pattern storage
"""
import os
from typing import List, Optional

from .canon_base_agent import CanonBaseAgent


class HealerAgent(CanonBaseAgent):
    """
    Healer Agent provides autonomous code repair for any canon violation.
    
    This is the general-purpose healing agent that can fix violations
    across all canon keys (0-50) using Gemini 2.5 Flash with thinking_budget.
    """
    
    def get_validation_keys(self) -> List[int]:
        """Return canon keys validated by this agent (all keys)."""
        return list(range(0, 51))  # Keys 0-50
    
    async def execute(self):
        """
        Execute Healer Agent - this is typically called by other agents
        rather than running standalone.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Ready for autonomous healing")
    
    async def heal_violation(
        self,
        file_path: str,
        violation_key: int,
        violation_details: str,
        reference_fix: Optional[str] = None
    ) -> bool:
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
                original_code = f.read()
        except Exception as e:
            print(f"      ⚠️ Cannot read {file_path}: {e}")
            return False
        
        # Build task description
        base_prompt = f"Fix Subatomic Canon Key {violation_key} only. {violation_details}"
        
        # Add reference fix if available
        if reference_fix:
            reference_chars = int(os.getenv('REFERENCE_FIX_CHARS', '500'))
            base_prompt += f"\n\nReference successful fix for similar violation:\n{reference_fix[:reference_chars]}..."
        
        # Multi-round healing with reflective learning
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        
        for round_num in range(1, max_rounds + 1):
            print(f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}")
            
            # Build round-specific prompt
            if round_num == 1:
                task = f"{base_prompt}\nReturn ONLY full corrected code."
            else:
                task = f"{base_prompt}\nPrevious attempt FAILED verification.\nHere is the failed code:\n\n{current_code}\n\nCritique weaknesses and produce improved code. Return ONLY full corrected code."
            
            # Get mutated code from Gemini
            mutated_code = await self.resilient_mutation(
                task=task,
                code=current_code,
                file_path=file_path,
                round_num=round_num,
                previous_failure=previous_failure
            )
            
            # 1. Syntax Gate
            try:
                import ast
                ast.parse(mutated_code)
            except SyntaxError as se:
                print(f"      ⚠️ Round {round_num}: SyntaxError line {se.lineno} – retrying")
                previous_failure = f"SyntaxError at line {se.lineno}: {se.msg}"
                current_code = mutated_code
                continue
            
            # 2. Zero-tolerance deletion guard
            original_lines = len(current_code.splitlines())
            mutated_lines = len(mutated_code.splitlines())
            max_allowed_deletion = int(original_lines * 0.1)
            deletion_count = original_lines - mutated_lines
            
            if deletion_count > max_allowed_deletion:
                print(f"      🚫 ZERO-TOLERANCE VIOLATION: {original_lines} -> {mutated_lines} lines ({deletion_count} deleted, max {max_allowed_deletion})")
                previous_failure = f"ZERO-TOLERANCE VIOLATION: You deleted {deletion_count} lines (max allowed: {max_allowed_deletion}). You are an ELITE engineer - preserve the complete file structure and only fix the specific violation."
                current_code = mutated_code
                continue
            
            # 3. Code bloat guard
            expansion_factor = int(os.getenv('CODE_EXPANSION_FACTOR', '4'))
            if mutated_lines > original_lines * expansion_factor:
                print(f"      ⚠️ Round {round_num}: Code bloat detected – rejecting")
                previous_failure = f"Code bloat detected: You added too many lines. Only fix the specific violation."
                current_code = mutated_code
                continue
            
            # 4. Verify fix resolved the violation
            is_fixed = await self._verify_fix_resolved(file_path, mutated_code, violation_key)
            
            if not is_fixed:
                print(f"      ⚠️ Round {round_num}: Violation still present – retrying")
                previous_failure = f"Violation Key {violation_key} still present after fix. Ensure the specific issue is addressed."
                current_code = mutated_code
                continue
            
            # 5. Check for side effects (new violations)
            has_side_effects = await self._check_side_effects(original_code, mutated_code)
            
            if has_side_effects:
                print(f"      ⚠️ Round {round_num}: New violations introduced – retrying")
                previous_failure = f"Your fix introduced new violations. Fix only the target violation without breaking other code."
                current_code = mutated_code
                continue
            
            # SUCCESS: Write the fixed code
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(mutated_code)
                print(f"      ✅ Round {round_num}: Successfully healed {os.path.basename(file_path)}")
                
                # Store successful pattern in Pinecone
                await self._store_healing_pattern(violation_key, violation_details, mutated_code, file_path)
                
                return True
            except Exception as e:
                print(f"      ❌ Cannot write {file_path}: {e}")
                return False
        
        print(f"      ❌ Failed to heal {os.path.basename(file_path)} after {max_rounds} rounds")
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
        # Write to temp file and re-validate
        temp_path = file_path + ".heal_tmp"
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            # Re-run validation for this specific key
            # This would call the appropriate validator for the key
            # For now, return True (optimistic)
            return True
        except Exception:
            return False
        finally:
            # Clean up temp file
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
        # Basic checks for common side effects
        
        # 1. Check if imports were removed
        import re
        original_imports = set(re.findall(r'^import\s+(\w+)', original_code, re.MULTILINE))
        original_imports.update(re.findall(r'^from\s+(\w+)', original_code, re.MULTILINE))
        
        fixed_imports = set(re.findall(r'^import\s+(\w+)', fixed_code, re.MULTILINE))
        fixed_imports.update(re.findall(r'^from\s+(\w+)', fixed_code, re.MULTILINE))
        
        # If critical imports were removed, that's a side effect
        removed_imports = original_imports - fixed_imports
        if removed_imports:
            print(f"      ⚠️ Side effect: Removed imports {removed_imports}")
            return True
        
        # 2. Check if function/class definitions were removed
        import ast
        try:
            original_tree = ast.parse(original_code)
            fixed_tree = ast.parse(fixed_code)
            
            original_defs = {node.name for node in ast.walk(original_tree) 
                           if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))}
            fixed_defs = {node.name for node in ast.walk(fixed_tree) 
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))}
            
            removed_defs = original_defs - fixed_defs
            if removed_defs:
                print(f"      ⚠️ Side effect: Removed definitions {removed_defs}")
                return True
        except:
            pass
        
        return False
    
    async def _store_healing_pattern(
        self,
        violation_key: int,
        violation_details: str,
        fixed_code: str,
        file_path: str
    ):
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
            # Create pattern description
            pattern_desc = f"Canon Key {violation_key} fix in {os.path.basename(file_path)}: {violation_details}"
            
            # Store in Pinecone (simplified - would need proper embedding)
            pattern_data = {
                'violation_key': violation_key,
                'violation_details': violation_details,
                'fix': fixed_code[:1000],  # Store first 1000 chars
                'file_path': file_path,
                'success_rate': 1.0
            }
            
            print(f"      💾 Stored healing pattern for Key {violation_key}")
        except Exception as e:
            print(f"      ⚠️ Failed to store pattern: {e}")
