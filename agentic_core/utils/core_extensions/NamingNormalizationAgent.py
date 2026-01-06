from __future__ import annotations
"""
[DEPRECATED] NamingNormalizationAgent - ABSORBED INTO NamingAgent

As of 2025-12-31 (P1 Consolidation), all naming normalization logic has been
centralized into NamingAgent. This file is kept for backward compatibility only.

Use instead:
    from agentic_core.utils.core_extensions.NamingAgent import NamingAgent, get_naming_agent
    naming = get_naming_agent(project_root)
    result = naming.normalize_filename(file_path, dry_run=False)

This file will be removed in a future release.
"""
import warnings
import re
import shutil
from pathlib import Path
from typing import Dict, Any

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    ALLOWED_DUPLICATE_FILENAMES,
)

# Emit deprecation warning on import
warnings.warn(
    "NamingNormalizationAgent is deprecated. Use NamingAgent.normalize_filename() instead.",
    DeprecationWarning,
    stacklevel=2
)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# DEPRECATED — Logic absorbed into NamingAgent — 2025-12-31
class NamingNormalizationAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Normalizes filenames and public symbols to snake_case.

    Why ungated healing is safe:
    - Filename rename: only affects current file + updates imports in same file
    - Symbol renames: limited to public definitions (functions/classes/constants)
    - All changes bounded to one file
    """
    SNAKE_CASE_PATTERN: Any = re.compile('^[a-z0-9_]+$')
    CAMEL_OR_PASCAL: Any = re.compile('^[A-Z][a-zA-Z0-9]*$|^[a-z]+([A-Z][a-z]+)+')

    def __init__(self, ctx=None, project_root=None) -> None:
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Execute method for validator compatibility."""
        from pathlib import Path
        return await self.heal_violation(Path(file_path), self.ctx)

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase/PascalCase/kebab-case to snake_case."""
        s1 = re.sub('([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    def timeout(seconds=0, minutes=0, hours=0):
        """
        Add a signal-based timeout to any function.
        Usage:
        @timeout(seconds=5)
        def my_slow_function(...)
        Args:
        - seconds: The time limit, in seconds.
        - minutes: The time limit, in minutes.
        - hours: The time limit, in hours.
        """
        limit = seconds + 60 * minutes + 3600 * hours

        def decorator(func):
            def wrapper(*args, **kwargs):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(asyncio.wait_for(func(*args, **kwargs), limit))
                except asyncio.TimeoutError:
                    raise TimeoutError(f'Timeout after {limit} seconds')
            return wrapper
        return decorator

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Deprecated naming agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Deprecated/utils - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    async def heal_violation(self, file_path: Path, ctx: Any=None) -> Dict[str, Any]:
        """
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Per-file healing: fix filename + public symbols.
        """
        ctx: Any = ctx or self.ctx
        changes: Any = {'filename': False, 'symbols': 0}
        try:
            # Skip files allowed to exist in multiple directories (from SSOT) - don't rename these
            if file_path.name in ALLOWED_DUPLICATE_FILENAMES:
                return {'healed': False, 'reason': 'File in ALLOWED_DUPLICATE_FILENAMES - exempt from renaming'}
            if not self.SNAKE_CASE_PATTERN.match(file_path.stem):
                new_name: Any = self._to_snake_case(file_path.stem) + file_path.suffix
                new_path: Any = file_path.with_name(new_name)
                if new_path != file_path and (not new_path.exists()):
                    shutil.move(str(file_path), str(new_path))
                    print(f'      [HEALED] Renamed file: {file_path.name} → {new_name}')
                    changes['filename'] = True
                    if hasattr(ctx, 'python_files'):
                        ctx.python_files = [str(new_path) if f == str(file_path) else f for f in ctx.python_files]
                    file_path: Any = new_path
            content: Any = file_path.read_text(encoding='utf-8')
            lines: Any = content.splitlines(keepends=True)
            new_lines: Any = []
            symbol_changes: Any = 0
            for line in lines:
                def_match: Any = re.search('^(async\\s+def|def|class)\\s+([A-Za-z0-9_]+)', line)
                const_match: Any = re.search('^([A-Z0-9_]{2,})\\s*=', line)
                if def_match:
                    old_name: Any = def_match.group(2)
                    if self.CAMEL_OR_PASCAL.match(old_name):
                        new_name: Any = self._to_snake_case(old_name)
                        new_line: Any = line.replace(old_name, new_name, 1)
                        new_lines.append(f'# NAMING FIXED: {old_name} → {new_name}\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n')
                        new_lines.append(new_line)
                        symbol_changes += 1
                        continue
                elif const_match and (not self.SNAKE_CASE_PATTERN.match(const_match.group(1))):
                    old_name: Any = const_match.group(1)
                    new_name: Any = self._to_snake_case(old_name)
                    new_line: Any = line.replace(old_name, new_name, 1)
                    new_lines.append(f'# NAMING FIXED: {old_name} → {new_name}\n')
                    new_lines.append(new_line)
                    symbol_changes += 1
                    continue
                new_lines.append(line)
            if symbol_changes > 0:
                file_path.write_text(''.join(new_lines), encoding='utf-8')
                changes['symbols'] = symbol_changes
            if changes['filename'] or changes['symbols'] > 0:
                msg: Any = f"Filename fixed: {changes['filename']}, symbols fixed: {changes['symbols']}"
                print(f'      [HEALED] {file_path.name}: {msg}')
                ctx.report(self.__class__.__name__, 18, True, msg)
                return {'healed': True, 'details': msg}
            return {'healed': False}
        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f'Naming fix failed: {str(e)[:100]}')
            return {'healed': False}

def get_naming_normalization_agent() -> Any:
    """Brief description of functionality and purpose."""
    return NamingNormalizationAgent()
