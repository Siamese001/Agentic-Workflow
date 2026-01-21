
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
from dataclasses import dataclass
"""
System Architect Agent - Core Architecture Validation
CANONICAL: True - Consolidated 2026-01-06 (removed system_architect.py duplicate)

Responsible for:
- Core architecture integrity
- Import dependencies, module structure
- Architectural patterns and design
"""
import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import CanonBaseAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

# NAMING CANON ABSOLUTE — renamed for eternal sovereign discovery — Phase 4 — 2025-12-30
@dataclass
class SystemArchitectAgent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, CanonBaseAgent):
    """
    System Architect validates core architecture and import dependencies.

    Validates:
    - Core modules exist and are accessible
    - No deep nesting (max 4 levels)
    - No large files (>1000 lines)
    - Import structure, dependencies, architecture
    """

    def get_validation_keys(self) -> List[int]:
        """Return canon keys validated by this agent."""
        return list(range(40, 51))

    async def execute(self) -> Any:
        """
        [L5 HARDENING] Sovereign Architectural Execution.
        Enforces Hierarchy, Nesting, and Header Sovereignty.
        """
        print(f'\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.name} ACTIVATED: Verifying Core Architecture...')
        print(f'   [{self.name}] 🔍 Checking Architecture: Hierarchy & Headers...')
        passed_arch, arch_viols = self.check_core_architecture()
        header_viols: Any = await self._check_file_headers()
        arch_violations: Any = arch_viols + header_viols
        if not arch_violations:
            print(f'   [{self.name}] ✅ Architecture: PASS - Core architecture & headers valid')
        else:
            print(f'   [{self.name}] ❌ Architecture: FAIL ({len(arch_violations)} violations)')
            await self._heal_violations('architecture', arch_violations)
        print(f'   [{self.name}] 🔍 Checking Depth: Physical Folder Depth...')
        passed_depth, depth_viols = self.check_no_deep_nesting()
        if not passed_depth:
            print(f'   [{self.name}] ❌ Depth: FAIL ({len(depth_viols)} violations)')
            await self._heal_violations('depth', depth_viols)
        else:
            print(f'   [{self.name}] ✅ Depth: PASS - Folder depth compliant (3-5)')
        print(f'   [{self.name}] 🔍 Checking File Size: Large Files...')
        passed, violations = self.check_no_large_files()
        if not passed:
            print(f'   [{self.name}] ❌ File Size: FAIL ({len(violations)} violations)')
            await self._heal_violations('file_size', violations)
        else:
            print(f'   [{self.name}] ✅ File Size: PASS - All files within size limits')

    async def _check_file_headers(self) -> List[str]:
        """
        Documentation Sovereignty Pass.
        Checks for high-signal headers and specialized Test Protocols.
        """
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                if not content.strip().startswith('"""'):
                    violations.append(f'{file_path}: Missing Canonical Header Docstring')
                if 'tests' in str(file_path) and 'Test Protocol' not in content:
                    violations.append(f'{file_path}: Missing Test Protocol in header')
            except Exception:
                continue
        return violations

    def check_core_architecture(self) -> Tuple[bool, List[str]]:
        """
        [L6 HARDENING] Core Hierarchy SSOT Verification.
        Reuses centralized hierarchy validation to prevent drift.
        """
        violations: Any = []
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
        # [PHASE 20] DEPRECATION: void_compliance.py removed - using HierarchyAgent
        def validate_canonical_hierarchy(proj_root):
            return HierarchyAgent(proj_root).validate_hierarchy()
        project_root: Any = Path(self.ctx.project_root or os.getcwd()).resolve()
        hierarchy_violations: Any = validate_canonical_hierarchy(project_root)
        for path, reason in hierarchy_violations:
            try:
                rel_path: Any = path.relative_to(project_root)
            except ValueError:
                rel_path: Any = path
            violations.append(f'{rel_path}: {reason}')
        for root_folder, config in SOVEREIGN_REGISTRY.items():
            root_path: Any = project_root / root_folder
            if not root_path.exists():
                continue
            if not (root_path / '__init__.py').exists():
                violations.append(f'{root_folder}: Missing __init__.py (package marker)')
            for l1_name in config['subfolders']:
                l1_path: Any = root_path / l1_name
                if l1_path.exists():
                    if not (l1_path / '__init__.py').exists():
                        violations.append(f'{root_folder}/{l1_name}: Missing __init__.py')
                    if config['depth'] == 4:
                        from agentic_core.L5_safety.validators.structure_blueprint import CORE_SUBFOLDER_MAP
                        l2_list: Any = CORE_SUBFOLDER_MAP.get(l1_name, [])
                        for l2_name in l2_list:
                            l2_path: Any = l1_path / l2_name
                            if l2_path.exists() and (not (l2_path / '__init__.py').exists()):
                                violations.append(f'{root_folder}/{l1_name}/{l2_name}: Missing __init__.py')
        return (len(violations) == 0, violations)

    def check_no_deep_nesting(self) -> Tuple[bool, List[str]]:
        """
        Enforce Physical Folder Nesting (Min 3, Max 5).
        Validates the physical directory depth relative to project root.
        Tests folder requires exactly depth 3.
        """
        from pathlib import Path
        violations: Any = []
        project_root: Any = Path(self.ctx.project_root or os.getcwd()).resolve()
        for file_path_str in self.ctx.python_files:
            file_path: Any = Path(file_path_str).resolve()
            try:
                rel_path: Any = file_path.relative_to(project_root)
            except ValueError:
                continue
            if len(rel_path.parts) == 1:
                continue
            depth: Any = len(rel_path.parts) - 1
            root_folder: Any = rel_path.parts[0] if rel_path.parts else None
            from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
            if root_folder in SOVEREIGN_REGISTRY:
                required_depth: Any = SOVEREIGN_REGISTRY[root_folder]['depth']
                if depth != required_depth:
                    violations.append(f'{rel_path}: {root_folder} requires exactly depth {required_depth}, found {depth}.')
                continue
        return (len(violations) == 0, violations)

    def check_no_large_files(self) -> Tuple[bool, List[str]]:
        """
        Check for files exceeding 1000 lines.

        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path
        violations: Any = []
        max_lines: Any = int(os.getenv('MAX_FILE_LINES', '1000'))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    line_count: Any = len(f.readlines())
                if line_count > max_lines:
                    violations.append(f'{file_path}: {line_count} lines exceeds max {max_lines}')
            except Exception:
                continue
        return (len(violations) == 0, violations)

    async def _heal_violations(self, check_type: str, violations: List[str]):
        """
        Structural & Strategy Healing.
        Handles both physical package initialization and logic mutation.
        """
        structural_fixes = [v for v in violations if 'Missing __init__.py' in v]
        for fix in structural_fixes:
            folder_rel = fix.split(':')[0].strip()
            folder_path = Path(os.getcwd()) / folder_rel
            if folder_path.exists():
                init_file = folder_path / '__init__.py'
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(f'''"""\n{folder_rel.replace('/', '.')} package initialization.\n"""\n''')
                print(f'      [✓] {self.name}: INITIALIZED {folder_rel}/__init__.py')
        remaining_violations = [v for v in violations if 'Missing __init__.py' not in v]
        if not remaining_violations:
            return
        if check_type == 'architecture':
            for Violation in remaining_violations:
                file_path = Violation.split(':')[0].strip()
                await self._smart_fix(file_path, check_type, [Violation])
            return
        max_healing_per_file = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
        file_violations = {}
        for Violation in remaining_violations[:max_healing_per_file]:
            if ':' in Violation:
                parts = Violation.split(': ', 1)
                if len(parts) >= 1:
                    file_path = parts[0]
                    if file_path not in file_violations:
                        file_violations[file_path] = []
                    file_violations[file_path].append(Violation)
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, check_type, file_viols)

    async def _smart_fix(self, file_path: str, check_type: str, violations: List[str]):
        """
        Sovereign Header & Strategy Repair.
        Injects specialized Test Protocols and high-signal headers.
        """
        from pathlib import Path
        try:
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f'      [!] Cannot read {file_path}: {e}')
            return
        if any((marker in v for marker in ['Missing Canonical Header', 'Missing Test Protocol'] for v in violations)):
            Task = f"### ROLE: ARCHITECTURAL_SURGEON\n### TASK: Inject Standard Sovereign Header.\nFILE: {os.path.basename(file_path)}\n\nINSTRUCTIONS:\n1. Create a high-signal docstring at the VERY TOP of the file.\n2. The header must describe the file's purpose based on its content.\n3. Include 'Responsible for:' section with bullet points.\n4. IF THIS IS A TEST FILE: You MUST include a 'Test Protocol' section explaining exactly which functional behavior this file verifies.\n5. Preserve all existing code exactly as-is.\n\nReturn ONLY the full code with the new header injected."
        else:
            violation_details = '\n'.join(violations)
            Task = f'Fix {check_type} violations. Violations:\n{violation_details}'
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        for round_num in range(1, max_rounds + 1):
            print(f'      [Round {round_num}/{max_rounds}] Healing {check_type} → {os.path.basename(file_path)}')
            mutated_code = await self.resilient_mutation(Task=Task, code=current_code, file_path=file_path, round_num=round_num, previous_failure=previous_failure)
            is_valid, reason = await self.verify_fix(original_code, mutated_code, check_type)
            if not is_valid:
                print(f'      [!] Round {round_num}: {reason} – retrying')
                previous_failure = reason
                current_code = mutated_code
                continue
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(mutated_code)
                print(f'      [OK] Round {round_num}: Fixed {os.path.basename(file_path)}')
                return
            except Exception as e:
                print(f'      [X] Cannot write {file_path}: {e}')
                return
        print(f'      [X] Failed to fix {os.path.basename(file_path)} after {max_rounds} rounds')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
            print(f"[{agent_name}] L2 execution - healing chain invoked")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
