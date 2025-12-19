"""
agentic_core/agents/base.py
Depth: 3
Role: Abstract Base Class for all SubAtomic Agents.
"""
import time
import asyncio
from agentic_core.domain.context import ValidationContext

class SubAtomicAgent:
    """Base class for all validation agents with async support."""

    def __init__(self, context: ValidationContext):
        self.ctx = context
        self.name = self.__class__.__name__

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return "CRITICAL_FAIL" not in self.ctx.signals

    async def execute(self):
        """Execute agent's validation logic asynchronously."""
        raise NotImplementedError
    
    async def run_with_broadcast(self):
        """Wrapper that broadcasts agent lifecycle events."""
        # Set current agent context
        self.ctx._current_agent = self.name
        
        try:
            # Execute the actual agent logic
            await self.execute()
            
        except Exception as e:
            print(f"   ❌ [{self.name}] Error: {e}")
            raise


class ImportPatcher:
    """Mixin class providing unified import patching capabilities for Surgeon agents."""
    
    def build_import_dependency_map(self, moved_files):
        """Build a map of which files import the moved modules."""
        import ast
        import_map = {}
        
        for moved_file in moved_files:
            old_module = self.ctx._path_to_module(moved_file)
            import_map[old_module] = []
            
            # Scan all Python files for imports of this module
            for file_path in self.ctx.python_files:
                if file_path == moved_file: continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    
                    # Check for ImportFrom and Import nodes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            # Check if this import matches our moved module
                            if node.module and node.module.startswith(old_module):
                                import_map[old_module].append(file_path)
                                break
                        elif isinstance(node, ast.Import):
                            # Check for direct imports
                            for alias in node.names:
                                if alias.name.startswith(old_module):
                                    import_map[old_module].append(file_path)
                                    break
                except Exception:
                    continue
        
        # Remove empty entries
        return {k: v for k, v in import_map.items() if v}
    
    async def _patch_imports_after_changes(self, change_map, source_agent):
        """
        Unified import patching for file moves and splits.
        
        Args:
            change_map: Dict mapping old modules to new modules or lists of modules
                      For moves: {'old.module': 'new.module'}
                      For splits: {'old.module': ['new.module1', 'new.module2']}
            source_agent: Name of the agent performing the changes
        """
        import os
        if not change_map:
            return
        
        print(f"   🔧 Patching imports for {len(change_map)} module changes...")
        
        # Build import dependency map using ValidationContext helper
        import_map = self.ctx.build_import_dependency_map(change_map.keys())
        
        # Group affected files by unique set
        affected_files = set()
        for file_list in import_map.values():
            affected_files.update(file_list)
        
        if not affected_files:
            print("   ✅ No external imports to patch.")
            return
        
        # Build patch instructions for each affected file
        for file_path in affected_files:
            await self._patch_file_imports(file_path, change_map, source_agent)
    
    async def _patch_file_imports(self, file_path, change_map, source_agent):
        """Patch imports in a single file based on the change map."""
        import os
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Build patch instructions specific to this file
            patch_instructions = []
            
            for old_module, new_targets in change_map.items():
                if isinstance(new_targets, str):
                    # Simple move: old -> new
                    patch_instructions.append(f"{old_module} → {new_targets}")
                elif isinstance(new_targets, list):
                    # Split: old -> [new1, new2, ...]
                    for new_target in new_targets:
                        patch_instructions.append(f"{old_module} → {new_target}")
            
            patch_text = "\n".join(patch_instructions)
            
            # Generate patch task
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
            
            # Request patch from Gemini
            updated_content = await self.ctx.request_mutation(
                source_agent, patch_task, content, reasoning_mode=False
            )
            
            # Apply patch if changed
            if updated_content and updated_content != content:
                if self.ctx.write_compliant_file(file_path, updated_content):
                    print(f"   ✅ Imports patched: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"   ❌ Failed to patch imports in {file_path}: {e}")
            self.ctx.signals.add("CRITICAL_WARNING")
