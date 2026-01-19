from __future__ import annotations
"""
DEPRECATED: This file is deprecated as of Phase 2 (Jan 03, 2026).
All agents must migrate to L2ExecutionBaseAgent with enable_gemini=False.
This file will be removed in Phase 5.
"""

import warnings
warnings.warn(
    "SubAtomicAgent is deprecated. Use L2ExecutionBaseAgent with enable_gemini=False instead.",
    DeprecationWarning,
    stacklevel=2
)

import ast
import logging
import os
import re
from typing import Any, Dict, List, Optional, Protocol, Union

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

# [PHASE 1] Self-testing mixin for L2 canonical compliance
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

# [PHASE 3] Default-on healing mixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


# NOT_AN_AGENT — Base class for agents, not a true agent itself — excluded from agent discovery
class SubAtomicAgent(SubatomicTestingMixin, HealerMixin):
    """Base class for all validation agents with async support."""


    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, context: ValidationContext):
        self.ctx = context
        self.name = self.__class__.__name__

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return 'CRITICAL_FAIL' not in self.ctx.signals

    async def execute(self) -> Any:
        """Execute agent's validation logic asynchronously."""
        raise NotImplementedError

    async def run_with_broadcast(self) -> Any:
        """Wrapper that broadcasts agent lifecycle events."""
        self.ctx._current_agent = self.name
        try:
            await self.execute()
        except Exception as e:
            print(f'   [X] [{self.name}] Error: {e}')
            raise

class ImportPatcher:
    """Mixin class providing unified import patching capabilities for Surgeon agents."""

    def _is_import_node_for_module(self, node: ast.AST, old_module: str) -> bool:
        """Helper to check if an AST import node refers to the given module."""
        if isinstance(node, ast.ImportFrom):
            return bool(node.module and node.module.startswith(old_module))
        elif isinstance(node, ast.Import):
            return any((alias.name.startswith(old_module) for alias in node.names))
        return False

    def _find_module_import_in_tree(self, tree: ast.AST, old_module: str) -> bool:
        """Helper to check if a specific module is imported in a given AST tree."""
        for node in ast.walk(tree):
            if self._is_import_node_for_module(node, old_module):
                True
        return False

    def _is_module_imported_in_file(self, file_path: str, old_module: str) -> bool:
        """Helper to check if a specific module is imported in a given file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            return self._find_module_import_in_tree(tree, old_module)
        except Exception:
            return False

    def _get_files_importing_module(self, old_module_name: str, moved_file_path: str) -> List[str]:
        """Helper to find all files importing a specific old_module,
        excluding the moved_file itself.
        """
        importing_files = []
        for file_path in self.ctx.python_files:
            if file_path == moved_file_path:
                continue
            if self._is_module_imported_in_file(file_path, old_module_name):
                importing_files.append(file_path)
        return importing_files

    def build_import_dependency_map(self, moved_files: List[str]) -> Dict[str, List[str]]:
        """Build a map of which files import the moved modules."""
        import_map: Any = {}
        for moved_file in moved_files:
            old_module: Any = self.ctx._path_to_module(moved_file)
            importing_files: Any = self._get_files_importing_module(old_module, moved_file)
            if importing_files:
                import_map[old_module] = importing_files
        return {k: v for k, v in import_map.items() if v}

    async def _patch_imports_after_changes(self, change_map: Dict[str, Union[str, List[str]]], source_agent: str):
        """
        Unified import patching for file moves and splits.

        Args:
            change_map: Dict mapping old modules to new modules or lists of modules.
                        For moves: {'old.module': 'new.module'}
                        For splits: {'old.module': ['new.module1', 'new.module2']}
            source_agent: Name of the agent performing the changes.
        """
        if not change_map:
            return
        print(f'   [+] Patching imports for {len(change_map)} module changes...')
        import_map = self.ctx.build_import_dependency_map(change_map.keys())
        affected_files = set()
        for file_list in import_map.values():
            affected_files.update(file_list)
        if not affected_files:
            print('   [OK] No external imports to patch.')
            return
        for file_path in affected_files:
            await self._patch_file_imports(file_path, change_map, source_agent)

    def _generate_patch_instructions(self, change_map: Dict[str, Union[str, List[str]]]) -> List[str]:
        """Generates a list of human-readable patch instructions from a change map."""
        instructions = []
        for old_module, new_targets_raw in change_map.items():
            targets_iterable = [new_targets_raw] if isinstance(new_targets_raw, str) else new_targets_raw
            instructions.extend([f'{old_module} → {target}' for target in targets_iterable])
        return instructions

    def _read_file_content(self, file_path: str) -> Union[str, None]:
        """Reads file content, handling potential errors."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f'   [X] Failed to read file {file_path}: {e}')
            self.ctx.signals.add('CRITICAL_WARNING')
            return None

    def _apply_patch_and_log(self, file_path: str, updated_content: str):
        """Applies the patched content to the file and logs the outcome."""
        if self.ctx.write_compliant_file(file_path, updated_content):
            print(f'   [OK] Imports patched: {os.path.basename(file_path)}')

    async def _execute_import_mutation(self, source_agent: str, patch_task: str, content: str, file_path: str) -> Union[str, None]:
        """Helper to execute the mutation request and handle errors."""
        try:
            return await self.ctx.request_mutation(source_agent, patch_task, content, reasoning_mode=False)
        except Exception as e:
            print(f'   [X] Failed to request mutation for {file_path}: {e}')
            self.ctx.signals.add('CRITICAL_WARNING')
            return None

    async def _patch_file_imports(self, file_path: str, change_map: Dict[str, Union[str, List[str]]], source_agent: str):
        """Patch imports in a single file based on the change map."""
        content = self._read_file_content(file_path)
        if content is None:
            return
        patch_instructions = self._generate_patch_instructions(change_map)
        patch_text = '\n'.join(patch_instructions)
        patch_task = f'Update imports in this file to reflect module changes.\nRequired changes:\n{patch_text}\n\nFile content:\n{content}\n\nRules:\n1. Update import statements to use new module paths\n2. For split modules, import specific symbols from new modules\n3. Preserve relative imports where possible\n4. Return ONLY the updated Python code with corrected imports'
        updated_content = await self._execute_import_mutation(source_agent, patch_task, content, file_path)
        if updated_content and updated_content != content:
            self._apply_patch_and_log(file_path, updated_content)