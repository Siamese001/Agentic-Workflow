from __future__ import annotations
from dataclasses import dataclass
#!/usr/bin/env python3
"""
Import Healer - Fixes broken imports after file relocations
Prevents import breakage when enforcing strict depth policies
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin


@dataclass
class ImportHealerAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Automatically fixes import statements when files are moved.
    Critical for preventing breakage during structural refactoring.
    """
    
    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        self.project_root = project_root
        self.relocation_map: Dict[str, str] = {}  # old_path -> new_path
    
    def register_relocation(self, old_path: str, new_path: str) -> Any:
        """Track a file relocation for import healing."""
        self.relocation_map[old_path] = new_path
    
    def heal_imports_in_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Fix all imports in a file that reference relocated modules.
        
        Args:
            file_path: Path to file to heal
            
        Returns:
            Tuple of (was_healed, message)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Parse the file to find all imports
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return False, "Syntax error - cannot parse imports"
            
            imports_fixed = 0
            
            # Find all import statements
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        old_module = alias.name
                        new_module = self._get_relocated_module(old_module)
                        if new_module and new_module != old_module:
                            content = content.replace(f"import {old_module}", f"import {new_module}")
                            imports_fixed += 1
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        old_module = node.module
                        new_module = self._get_relocated_module(old_module)
                        if new_module and new_module != old_module:
                            content = content.replace(f"from {old_module}", f"from {new_module}")
                            imports_fixed += 1
            
            # Also fix relative imports when file itself is moved
            content = self._fix_relative_imports(file_path, content)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True, f"Fixed {imports_fixed} import(s)"
            
            return False, "No imports needed healing"
            
        except Exception as e:
            return False, f"Healing failed: {e}"
    
    def _get_relocated_module(self, module_path: str) -> str:
        """Convert old module path to new module path based on relocations."""
        # Check if any registered relocation affects this import
        for old_path, new_path in self.relocation_map.items():
            old_module = self._path_to_module(old_path)
            new_module = self._path_to_module(new_path)
            
            if module_path == old_module:
                return new_module
            elif module_path.startswith(old_module + "."):
                # Handle submodule imports
                suffix = module_path[len(old_module):]
                return new_module + suffix
        
        return module_path
    
    def _path_to_module(self, file_path: str) -> str:
        """Convert file path to Python module path."""
        # Remove .py extension and convert path separators to dots
        module = file_path.replace('\\', '/').replace('/', '.')
        if module.endswith('.py'):
            module = module[:-3]
        return module
    
    def _fix_relative_imports(self, file_path: Path, content: str) -> str:
        """
        Fix relative imports when the file itself has been moved.
        
        For example, if tests/e2e/core/test_admin.py imports from .core,
        and it's moved to tests/e2e/test_admin.py, the import breaks.
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
            depth = len(rel_path.parts)
            
            # Pattern: from .something import ...
            # Pattern: from ..something import ...
            relative_import_pattern = r'from (\.+)(\w+)? import'
            
            def fix_relative(match) -> Any:
                """Execute fix_relative operation."""
                dots = match.group(1)
                module = match.group(2) or ''
                num_dots = len(dots)
                
                # Calculate what the import should be based on current depth
                # This is a simplified heuristic - may need refinement
                if num_dots > depth - 1:
                    # Too many dots for current depth - convert to absolute
                    parts = list(rel_path.parts[:-1])  # Exclude filename
                    if module:
                        parts.append(module)
                    absolute_module = '.'.join(parts)
                    return f'from {absolute_module} import'
                
                return match.group(0)  # Keep as-is
            
            content = re.sub(relative_import_pattern, fix_relative, content)
            
        except Exception:
            pass  # If fixing fails, return content unchanged
        
        return content
    
    def heal_all_imports_in_directory(self, directory: Path) -> Dict[str, str]:
        """
        Heal imports in all Python files in a directory.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Dict of {file_path: heal_message}
        """
        results = {}
        
        for py_file in directory.rglob("*.py"):
            if py_file.is_file():
                was_healed, message = self.heal_imports_in_file(py_file)
                if was_healed:
                    results[str(py_file)] = message
        
        return results

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


def get_sovereign_ignore_list() -> Set[str]:
    """
    Helper for all agents to respect the .gitignore boundaries.
    Provides a unified source of truth for protected patterns.
    """
    ignore_list = {'.git', 'venv', '__pycache__', '.env', 'node_modules'}
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        try:
            for line in gitignore_path.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # Clean pattern
                    pattern = line.rstrip('/')
                    if '/' in pattern:
                        pattern = pattern.split('/')[0]
                    pattern = pattern.replace('*', '').strip()
                    if pattern:
                        ignore_list.add(pattern)
        except Exception:
            pass  # If reading fails, use defaults
    
    return ignore_list
