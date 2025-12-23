"""
SubAtomicAgent base class and ImportPatcher mixin.
All validation agents inherit from SubAtomicAgent.
"""

import ast
import os
import time
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from agentic_core.types import ValidationContext


class SubAtomicAgent:
    """Base class for all validation agents with async support."""

    def __init__(self, context: "ValidationContext"):
        self.ctx = context
        self.name = self.__class__.__name__

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return "CRITICAL_FAIL" not in self.ctx.signals

    async def execute(self):
        """Execute agent's validation logic asynchronously."""
        raise NotImplementedError

    async def run_with_broadcast(self):
        """Wrapper that broadcasts agent lifecycle events to the L5 Streamer."""
        self.ctx.set_current_agent(self.name)

        await self.ctx.broadcast({
            "type": "agent_start",
            "agent": self.name,
            "cycle": getattr(self.ctx, 'current_cycle', 1),
            "timestamp": time.time()
        })

        try:
            await self.execute()

            await self.ctx.broadcast({
                "type": "agent_complete",
                "agent": self.name,
                "modified": list(self.ctx.modified_files),
                "signals": list(self.ctx.signals),
                "timestamp": time.time()
            })
        except Exception as e:
            await self.ctx.broadcast({
                "type": "agent_error",
                "agent": self.name,
                "error": str(e)[:200],
                "timestamp": time.time()
            })
            raise


class ImportPatcher:
    """Mixin class providing unified import patching capabilities for Surgeon agents."""

    ctx: "ValidationContext"  # Type hint for mixin

    def build_import_dependency_map(self, moved_files: List[str]) -> Dict[str, List[str]]:
        """Build a map of which files import the moved modules."""
        import_map: Dict[str, List[str]] = {}

        for moved_file in moved_files:
            old_module = self.ctx._path_to_module(moved_file)
            import_map[old_module] = []

            for file_path in self.ctx.python_files:
                if file_path == moved_file:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and node.module.startswith(old_module):
                                import_map[old_module].append(file_path)
                                break
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.startswith(old_module):
                                    import_map[old_module].append(file_path)
                                    break
                except Exception:
                    continue

        return {k: v for k, v in import_map.items() if v}

    async def _patch_imports_after_changes(
        self,
        change_map: Dict[str, Any],
        source_agent: str
    ):
        """
        Unified import patching for file moves and splits.

        Args:
            change_map: Dict mapping old modules to new modules or lists of modules
                      For moves: {'old.module': 'new.module'}
                      For splits: {'old.module': ['new.module1', 'new.module2']}
            source_agent: Name of the agent performing the changes
        """
        if not change_map:
            return

        print(f"   🔧 Patching imports for {len(change_map)} module changes...")

        import_map = self.build_import_dependency_map(list(change_map.keys()))

        affected_files = set()
        for file_list in import_map.values():
            affected_files.update(file_list)

        if not affected_files:
            print("   ✅ No external imports to patch.")
            return

        for file_path in affected_files:
            await self._patch_file_imports(file_path, change_map, source_agent)

    async def _patch_file_imports(
        self,
        file_path: str,
        change_map: Dict[str, Any],
        source_agent: str
    ):
        """Patch imports in a single file based on the change map."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            patch_instructions = []
            for old_module, new_targets in change_map.items():
                if isinstance(new_targets, str):
                    patch_instructions.append(f"{old_module} → {new_targets}")
                elif isinstance(new_targets, list):
                    for new_target in new_targets:
                        patch_instructions.append(f"{old_module} → {new_target}")

            patch_text = "\n".join(patch_instructions)

            patch_task = (
                f"Update imports in this file to reflect module changes.\n"
                f"Required changes:\n{patch_text}\n\n"
                f"File content:\n{content}\n\n"
                "Rules:\n"
                "1. Update import statements to use new module paths\n"
                "2. For split modules, import specific symbols from new modules\n"
                "3. Preserve relative imports where possible\n"
                "4. Return ONLY the updated Python code with corrected imports"
            )

            updated_content = await self.ctx.request_mutation(
                source_agent, patch_task, content, reasoning_mode=False
            )

            if updated_content and updated_content != content:
                if self.ctx.write_compliant_file(file_path, updated_content):
                    print(f"   ✅ Imports patched: {os.path.basename(file_path)}")

        except Exception as e:
            print(f"   ❌ Failed to patch imports in {file_path}: {e}")
            self.ctx.signals.add("CRITICAL_WARNING")
