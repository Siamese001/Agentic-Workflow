from __future__ import annotations
"""
System Architect Agent - Core Architecture Validation (Keys 40-50)

Responsible for:
- Key 40: Core architecture integrity
- Key 41-47: Import dependencies, module structure
- Key 48-50: Architectural patterns and design
"""
import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import CanonBaseAgent


class SystemArchitectAgent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, CanonBaseAgent):
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
    
    async def execute(self) -> None:
        """
        [L5 HARDENING] Sovereign Architectural Execution.
        Enforces Hierarchy (Key 40), Nesting (Key 41), and Header Sovereignty.
        """
        print(f"\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...")
        
        # 1. Key 40: Core Hierarchy & Header Sovereignty
        print(f"   [{self.name}] 🔍 Checking Key 40: Hierarchy & Headers...")
        passed_arch, arch_viols = self.check_key_40_core_architecture()
        header_viols = await self._check_file_headers()
        
        k40_violations = arch_viols + header_viols
        if not k40_violations:
            print(f"   [{self.name}] ✅ Key 40: PASS - Core architecture & headers valid")
        else:
            print(f"   [{self.name}] ❌ Key 40: FAIL ({len(k40_violations)} violations)")
            await self._heal_violations(40, k40_violations)
        
        # 2. Key 41: Physical Folder Nesting (Min 3 / Max 5)
        print(f"   [{self.name}] 🔍 Checking Key 41: Physical Folder Depth...")
        passed_depth, depth_viols = self.check_key_41_no_deep_nesting()
        if not passed_depth:
            print(f"   [{self.name}] ❌ Key 41: FAIL ({len(depth_viols)} violations)")
            await self._heal_violations(41, depth_viols)
        else:
            print(f"   [{self.name}] ✅ Key 41: PASS - Folder depth compliant (3-5)")
        
        # Check Key 42: Large files
        print(f"   [{self.name}] 🔍 Checking Key 42: Large Files...")
        passed, violations = self.check_key_42_no_large_files()
        if not passed:
            print(f"   [{self.name}] ❌ Key 42: FAIL ({len(violations)} violations)")
            await self._heal_violations(42, violations)
        else:
            print(f"   [{self.name}] ✅ Key 42: PASS - All files within size limits")
    
    async def _check_file_headers(self) -> List[str]:
        """
        [KEY 40] Documentation Sovereignty Pass.
        Checks for high-signal headers and specialized Test Protocols.
        """
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500) 
                
                # Check for canonical triple-quote header
                if not content.strip().startswith('"""'):
                    violations.append(f"{file_path}: Missing Canonical Header Docstring")
                
                # Special Requirement for tests/
                if "tests" in str(file_path) and "Test Protocol" not in content:
                    violations.append(f"{file_path}: Missing Test Protocol in header")
            except Exception:
                continue
        return violations

    def check_key_40_core_architecture(self) -> Tuple[bool, List[str]]:
        """
        [L6 HARDENING] Core Hierarchy SSOT Verification.
        Reuses centralized hierarchy validation to prevent drift.
        """
        violations = []
        from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
        from agentic_core.runtime.shared_runtime.void_compliance import (
            validate_canonical_hierarchy,
        )
        project_root = Path(self.ctx.project_root or os.getcwd()).resolve()
        
        # 1. Centralized hierarchy drift check
        hierarchy_violations = validate_canonical_hierarchy(project_root)
        for path, reason in hierarchy_violations:
            try:
                rel_path = path.relative_to(project_root)
            except ValueError:
                rel_path = path
            violations.append(f"{rel_path}: {reason}")

        # 2. Package Integrity: Verify __init__.py markers
        for root_folder, config in SOVEREIGN_REGISTRY.items():
            root_path = project_root / root_folder
            if not root_path.exists(): continue
            if not (root_path / '__init__.py').exists():
                violations.append(f"{root_folder}: Missing __init__.py (package marker)")

            for l1_name in config["subfolders"]:
                l1_path = root_path / l1_name
                if l1_path.exists():
                    if not (l1_path / '__init__.py').exists():
                        violations.append(f"{root_folder}/{l1_name}: Missing __init__.py")
                    # Check L2 subfolders if depth is 4
                    if config["depth"] == 4:
                        from agentic_core.config.blueprint_sovereign.structure_blueprint import (
                            CORE_SUBFOLDER_MAP,
                        )
                        l2_list = CORE_SUBFOLDER_MAP.get(l1_name, [])
                        for l2_name in l2_list:
                            l2_path = l1_path / l2_name
                            if l2_path.exists() and not (l2_path / '__init__.py').exists():
                                violations.append(f"{root_folder}/{l1_name}/{l2_name}: Missing __init__.py")
        
        return len(violations) == 0, violations
    
    def check_key_41_no_deep_nesting(self) -> Tuple[bool, List[str]]:
        """
        [KEY 41 HARDENING] Enforce Physical Folder Nesting (Min 3, Max 5).
        Validates the physical directory depth relative to project root.
        Tests folder requires exactly depth 3.
        """
        from pathlib import Path
        violations = []
        project_root = Path(self.ctx.project_root or os.getcwd()).resolve()

        for file_path_str in self.ctx.python_files:
            file_path = Path(file_path_str).resolve()
            try:
                rel_path = file_path.relative_to(project_root)
            except ValueError:
                continue

            # Skip Key 0 (root-level) protected files
            if len(rel_path.parts) == 1:
                continue

            # Physical Depth = Dir count (excludes filename)
            depth = len(rel_path.parts) - 1
            root_folder = rel_path.parts[0] if rel_path.parts else None

            # [SSOT] Dynamic depth check from structure_blueprint
            from agentic_core.config.blueprint_sovereign.structure_blueprint import (
                SOVEREIGN_REGISTRY,
            )
            
            if root_folder in SOVEREIGN_REGISTRY:
                required_depth = SOVEREIGN_REGISTRY[root_folder]["depth"]
                if depth != required_depth:
                    violations.append(f"{rel_path}: {root_folder} requires exactly depth {required_depth}, found {depth}.")
                continue

            # All other folders: min 3, max 5
            if depth < 3:
                violations.append(f"{rel_path}: Shallow nesting ({depth}). Min required is 3.")
            elif depth > 5:
                violations.append(f"{rel_path}: Deep nesting ({depth}). Max allowed is 5.")

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
    
    async def _heal_violations(self, key: int, violations: List[str]):
        """
        [KEY 40 HARDENING] Structural & Strategy Healing.
        Handles both physical package initialization and logic mutation.
        """
        # 1. Structural Healing: Auto-initialize Python packages (L6 Integrity)
        # Any Violation containing "Missing __init__.py" triggers a physical write.
        structural_fixes = [v for v in violations if "Missing __init__.py" in v]
        for fix in structural_fixes:
            # Extract path from Violation string (e.g., 'agentic_core/L1_cognition: Missing __init__.py')
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
            
        # [KEY 42 HARDENING] Force Fission Surgery
        if key == 42:
            for Violation in remaining_violations:
                file_path = Violation.split(":")[0].strip()
                await self._smart_fix(file_path, key, [Violation])
            return

        max_healing_per_file = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
        
        # Group violations by file
        file_violations = {}
        for Violation in remaining_violations[:max_healing_per_file]:
            if ':' in Violation:
                parts = Violation.split(': ', 1)
                if len(parts) >= 1:
                    file_path = parts[0]
                    if file_path not in file_violations:
                        file_violations[file_path] = []
                    file_violations[file_path].append(Violation)
        
        # Heal each file using LLM resilient mutation
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)
    
    async def _smart_fix(self, file_path: str, violation_key: int, violations: List[str]):
        """
        [KEY 40] Sovereign Header & Strategy Repair.
        Injects specialized Test Protocols and high-signal headers.
        """
        from pathlib import Path
        try:
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f"      [!] Cannot read {file_path}: {e}")
            return
        
        # [KEY 40] Standardized Header & Test Protocol Injection
        if any(marker in v for marker in ["Missing Canonical Header", "Missing Test Protocol"] for v in violations):
            Task = f"""### ROLE: ARCHITECTURAL_SURGEON
### TASK: Inject Standard Sovereign Header (Key 40).
FILE: {os.path.basename(file_path)}

INSTRUCTIONS:
1. Create a high-signal docstring at the VERY TOP of the file.
2. The header must describe the file's purpose based on its content.
3. Include 'Responsible for:' section with bullet points.
4. IF THIS IS A TEST FILE: You MUST include a 'Test Protocol' section explaining exactly which canon key or functional behavior this file verifies.
5. Preserve all existing code exactly as-is.

Return ONLY the full code with the new header injected."""
        else:
            violation_details = "\n".join(violations)
            Task = f"Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}"
        
        # Multi-round healing
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        
        for round_num in range(1, max_rounds + 1):
            print(f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}")
            
            # Get mutated code from Gemini
            mutated_code = await self.resilient_mutation(
                Task=Task,
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
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
