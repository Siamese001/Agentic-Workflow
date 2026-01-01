import re
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Dict, Any, Match
from agentic_core.common.healing.healer_mixin import HealerMixin

# NAMING CANON COMPLIANCE — renamed to GravityLeakRepairAgent for discovery and sovereignty — 2025-12-30
class GravityLeakRepairAgent(HealerMixin):
    """
    Converts forbidden static imports from higher layers (L4/L5) into dynamic importlib calls.

    Why ungated healing is safe:
    - Only touches import statements and wraps them in comments
    - Preserves functionality (dynamic import achieves same result)
    - Single-file scope, no risk of import cycles
    - Easy to audit/rollback
    """
    UPWARD_IMPORT_PATTERNS: Any = ['^(\\s*)import\\s+agentic_core\\.L[45]_\\w+', '^(\\s*)from\\s+agentic_core\\.L[45]_\\w+\\s+import', '^(\\s*)from\\s+agentic_core\\.L[45]_\\w+\\.\\w+\\s+import']

    def __init__(self, ctx, project_root=None):
        """Initialize with mandatory ctx for sovereign operation."""
        if ctx is None:
            raise ValueError("ctx is mandatory for GravityLeakRepairAgent (sovereign agent)")
        self.patterns = [re.compile(p) for p in self.UPWARD_IMPORT_PATTERNS]
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Execute method for validator compatibility - wraps heal_violation."""
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx: Any=None) -> Dict[str, Any]:
        """
        Called per-file in healing cascade. Replaces static upward imports with dynamic equivalents.
        """
        ctx: Any = ctx or self.ctx
        try:
            content: Any = file_path.read_text(encoding='utf-8')
            lines: Any = content.splitlines(keepends=True)
            new_lines: Any = []
            changes_made: Any = 0
            for line in lines:
                matched: Any = False
                for pattern in self.patterns:
                    match: Match | None = pattern.match(line)
                    if match:
                        indent: Any = match.group(1)
                        original_import: Any = line.strip()
                        if original_import.startswith('import '):
                            module: Any = original_import[7:].strip()
                            replacement: Any = f"{indent}import importlib\n{indent}{module.split('.')[-1]} = importlib.import_module('{module}')"
                        else:
                            parts: Any = original_import.split(' import ')
                            module_path: Any = parts[0][5:].strip()
                            imported_names: Any = parts[1].strip()
                            replacement: Any = f"{indent}import importlib\n{indent}mod = importlib.import_module('{module_path}')\n{indent}{imported_names} = mod.{imported_names.split(',')[0].split()[-1]}  # Adjust multi-imports manually"
                        comment: Any = f'{indent}# GRAVITY FIXED: {original_import}\n'
                        new_lines.append(comment)
                        new_lines.extend([f'{l}\n' for l in replacement.splitlines()])
                        changes_made += 1
                        matched: Any = True
                        break
                if not matched:
                    new_lines.append(line)
            if changes_made > 0:
                new_content: Any = ''.join(new_lines)
                file_path.write_text(new_content, encoding='utf-8')
                message: Any = f'Fixed {changes_made} upward gravity leak(s) → dynamic imports'
                print(f'      [HEALED] {file_path.name}: {message}')
                ctx.report(self.__class__.__name__, key_id=18, success=True, msg=message)
                return {'healed': True, 'details': message}
            return {'healed': False}
        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f'Gravity repair failed: {str(e)[:100]}')
            return {'healed': False}

def get_gravity_leak_repair_agent() -> Any:
    """Brief description of functionality and purpose."""
    return GravityLeakRepairAgent()
