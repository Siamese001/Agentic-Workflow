"""
System Architect Agent - Core Architecture Validation (Keys 40-50)

Responsible for:
- Key 40: Core architecture integrity
- Key 41-47: Import dependencies, module structure
- Key 48-50: Architectural patterns and design
"""
from typing import Any, Optional, Protocol, Dict, List
import re

import ast
import os
from pathlib import Path
from typing import List, Tuple

from .canon_base_agent import CanonBaseAgent


class SystemArchitect(CanonBaseAgent):
    """
    System Architect validates core architecture and import dependencies.
    
    Validates Canon Keys 40-50:
    - Key 40: Core modules exist and are accessible
    - Key 41: No deep nesting (max 4 levels)
    - Key 42: No large files (>1000 lines)
    - Key 43-50: Import structure, dependencies, architecture
    """
    
    def get_validation_keys(self) -> List[int]:
        """Return canon keys validated by this agent."""
        return list(range(40, 51))  # Keys 40-50
    
    async def execute(self):
        """Execute System Architect validation checks."""
        print(f"\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...")
        
        # Check Key 40: Core architecture
        print(f"   [{self.name}] 🔍 Checking Key 40: Core Architecture...")
        passed, violations = self.check_key_40_core_architecture()
        if passed:
            print(f"   [{self.name}] ✅ Key 40: PASS - Core architecture valid")
        else:
            print(f"   [{self.name}] ❌ Key 40: FAIL ({len(violations)} violations)")
            await self._heal_violations(40, violations)
        
        # Check Key 41: Deep nesting
        print(f"   [{self.name}] 🔍 Checking Key 41: Deep Nesting...")
        passed, violations = self.check_key_41_no_deep_nesting()
        if not passed:
            print(f"   [{self.name}] ❌ Key 41: FAIL ({len(violations)} violations)")
            await self._heal_violations(41, violations)
        else:
            print(f"   [{self.name}] ✅ Key 41: PASS - No deep nesting detected")
        
        # Check Key 42: Large files
        print(f"   [{self.name}] 🔍 Checking Key 42: Large Files...")
        passed, violations = self.check_key_42_no_large_files()
        if not passed:
            print(f"   [{self.name}] ❌ Key 42: FAIL ({len(violations)} violations)")
            await self._heal_violations(42, violations)
        else:
            print(f"   [{self.name}] ✅ Key 42: PASS - All files within size limits")
    
    def check_key_40_core_architecture(self) -> Tuple[bool, List[str]]:
        """
        [KEY 40 HARDENING] Comprehensive Hierarchy Verification.
        Verifies all layers defined in CANONICAL_HIERARCHY exist as valid packages.
       
        """
        violations = []
        
        # Force import of SSOT from project root
        import void_compliance
        from void_compliance import CANONICAL_HIERARCHY
        
        project_root = Path(os.getcwd())
        
        # Traverse hierarchy levels to identify missing packages or init files
        for root_folder, layers in CANONICAL_HIERARCHY.items():
            root_path = project_root / root_folder
            if not root_path.exists():
                violations.append(f"{root_folder}: Sovereign root directory missing")
                continue
                
            if not (root_path / '__init__.py').exists():
                violations.append(f"{root_folder}: Missing __init__.py")

            # Check L1 and L2 layers recursively
            for l1_name, l2_list in layers.items():
                l1_path = root_path / l1_name
                if l1_path.exists():
                    if not (l1_path / '__init__.py').exists():
                        violations.append(f"{root_folder}/{l1_name}: Missing __init__.py")
                    
                    for l2_name in l2_list:
                        l2_path = l1_path / l2_name
                        if l2_path.exists() and not (l2_path / '__init__.py').exists():
                            violations.append(f"{root_folder}/{l1_name}/{l2_name}: Missing __init__.py")
        
        return len(violations) == 0, violations
    
    def check_key_41_no_deep_nesting(self) -> Tuple[bool, List[str]]:
        """
        Check for excessive nesting depth (>4 levels).
        
        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path
        violations = []
        max_depth = int(os.getenv('MAX_NESTING_DEPTH', '4'))
        
        for file_path in self.ctx.python_files:
            try:
                # FIX: Use pathlib.Path to handle Windows paths correctly
                resolved_path = Path(file_path).resolve()
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                # Check nesting depth
                max_file_depth = self._get_max_nesting_depth(tree)
                if max_file_depth > max_depth:
                    violations.append(f"{file_path}: Nesting depth {max_file_depth} exceeds max {max_depth}")
            except Exception:
                continue
        
        return len(violations) == 0, violations
    
    def check_key_42_no_large_files(self) -> Tuple[bool, List[str]]:
        """
        Check for files exceeding 1000 lines.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path
        violations = []
        max_lines = int(os.getenv('MAX_FILE_LINES', '1000'))
        
        for file_path in self.ctx.python_files:
            try:
                # FIX: Use pathlib.Path to handle Windows paths correctly
                resolved_path = Path(file_path).resolve()
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                
                if line_count > max_lines:
                    violations.append(f"{file_path}: {line_count} lines exceeds max {max_lines}")
            except Exception:
                continue
        
        return len(violations) == 0, violations
    
    def _get_max_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in AST."""
        max_depth = 0
        
        def visit_node(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            # Nodes that increase nesting depth
            nesting_nodes = (
                ast.If, ast.For, ast.While, ast.With,
                ast.Try, ast.ExceptHandler, ast.FunctionDef,
                ast.AsyncFunctionDef, ast.ClassDef
            )
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, nesting_nodes):
                    visit_node(child, depth + 1)
                else:
                    visit_node(child, depth)
        
        visit_node(tree)
        return max_depth
    
    async def _heal_violations(self, key: int, violations: List[str]):
        """
        [KEY 40 HARDENING] Structural & Strategy Healing.
        Handles both physical package initialization and logic mutation.
        """
        # 1. Structural Healing: Auto-initialize Python packages (L6 Integrity)
        # Any violation containing "Missing __init__.py" triggers a physical write.
        structural_fixes = [v for v in violations if "Missing __init__.py" in v]
        for fix in structural_fixes:
            # Extract path from violation string (e.g., 'agentic_core/L1_cognition: Missing __init__.py')
            folder_rel = fix.split(":")[0].strip()
            folder_path = Path(os.getcwd()) / folder_rel
            if folder_path.exists():
                init_file = folder_path / "__init__.py"
                with open(init_file, 'w', encoding='utf-8') as f:
                    # High-signal docstring identifying the package
                    f.write(f'"""\n{folder_rel.replace("/", ".")} package initialization.\n"""\n')
                print(f"      [✓] {self.name}: INITIALIZED {folder_rel}/__init__.py")
        
        # 2. Strategy Healing: Hand off remaining logic violations to smart_fix
        remaining_violations = [v for v in violations if "Missing __init__.py" not in v]
        if not remaining_violations:
            return

        max_healing_per_file = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
        
        # Group violations by file
        file_violations = {}
        for violation in remaining_violations[:max_healing_per_file]:
            if ':' in violation:
                parts = violation.split(': ', 1)
                if len(parts) >= 1:
                    file_path = parts[0]
                    if file_path not in file_violations:
                        file_violations[file_path] = []
                    file_violations[file_path].append(violation)
        
        # Heal each file using LLM resilient mutation
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)
    
    async def _smart_fix(self, file_path: str, violation_key: int, violations: List[str]):
        """
        Apply smart fix to a file using Gemini 2.5 Flash.
        
        Args:
            file_path: Path to file to fix
            violation_key: Canon key being fixed
            violations: List of violations in this file
        """
        from pathlib import Path
        try:
            # FIX: Use pathlib.Path to handle Windows paths correctly
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f"      [!] Cannot read {file_path}: {e}")
            return
        
        # Build task description
        violation_details = "\n".join(violations)
        task = f"Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}"
        
        # Multi-round healing
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        
        for round_num in range(1, max_rounds + 1):
            print(f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}")
            
            # Get mutated code from Gemini
            mutated_code = await self.resilient_mutation(
                task=task,
                code=current_code,
                file_path=file_path,
                round_num=round_num,
                previous_failure=previous_failure
            )
            
            # Verify the fix
            is_valid, reason = await self.verify_fix(original_code, mutated_code, violation_key)
            
            if not is_valid:
                print(f"      [!] Round {round_num}: {reason} – retrying")
                previous_failure = reason
                current_code = mutated_code
                continue
            
            # Write the fixed code
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(mutated_code)
                print(f"      [OK] Round {round_num}: Fixed {os.path.basename(file_path)}")
                return
            except Exception as e:
                print(f"      [X] Cannot write {file_path}: {e}")
                return
        
        print(f"      [X] Failed to fix {os.path.basename(file_path)} after {max_rounds} rounds")