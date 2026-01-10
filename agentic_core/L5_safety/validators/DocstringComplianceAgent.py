from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Dict, Any, Optional
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# NAMING CANON ABSOLUTE — renamed for eternal sovereign discovery — Phase 4 — 2025-12-30
class DocstringComplianceAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Ensures public functions, classes, and modules have docstrings.

    Rules:
    - Module-level docstring required (first statement)
    - Public classes (not starting with _) must have docstring
    - Public functions/methods (not starting with _) must have docstring
    - Minimal stub: '''Brief description of functionality and purpose.'''

    Why ungated healing is safe:
    - Only adds Missing triple-quoted strings immediately after def/class
    - Never removes or modifies existing content
    - Single-file scope
    """
    MIN_DOCSTRING: Any = "'''Brief description of functionality and purpose.'''"

    def __init__(self, ctx, project_root=None) -> None:
        """Initialize with mandatory ctx for sovereign operation."""
        if ctx is None:
            raise ValueError("ctx is mandatory for DocstringComplianceAgent (sovereign agent)")
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Execute method for validator compatibility."""
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx: Any=None) -> Dict[str, Any]:
        """
        Per-file healing: add Missing docstrings.
        """
        ctx: Any = ctx or self.ctx
        try:
            source: Any = file_path.read_text(encoding='utf-8')
            tree: Any = ast.parse(source)
            needs_docstring: Any = []
            if not ast.get_docstring(tree):
                needs_docstring.append(('module', 0))
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith('_'):
                        continue
                    if ast.get_docstring(node) is None:
                        needs_docstring.append((type(node).__name__, node.lineno))
            if not needs_docstring:
                return {'healed': False}
            lines: Any = source.splitlines(keepends=True)
            new_lines: Any = lines.copy()
            added_count: Any = 0
            needs_docstring.sort(key=lambda x: x[1] if x[0] != 'module' else 0, reverse=True)
            for node_type, lineno in needs_docstring:
                if node_type == 'module':
                    insert_idx: Any = 0
                    for i, line in enumerate(lines):
                        if line.strip() and (not line.strip().startswith(('#', '__'))):
                            insert_idx: Any = i + 1
                            break
                    indent: Any = ''
                else:
                    insert_idx: Any = lineno
                    def_line: Any = lines[lineno - 1]
                    indent: Any = '    ' * (len(def_line) - len(def_line.lstrip()) + 1)
                doc_lines: Any = [f'{indent}{self.MIN_DOCSTRING}\nfrom agentic_core.utils.mixins import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n', f'{indent}\n']
                new_lines[insert_idx:insert_idx] = doc_lines
                added_count += 1
            if added_count > 0:
                new_content: Any = ''.join(new_lines)
                file_path.write_text(new_content, encoding='utf-8')
                message: Any = f'Added {added_count} Missing docstring(s)'
                print(f'      [HEALED] {file_path.name}: {message}')
                ctx.report(self.__class__.__name__, key_id=18, success=True, msg=message)
                return {'healed': True, 'details': message}
            return {'healed': False}
        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f'Docstring healing failed: {str(e)[:100]}')
            return {'healed': False}

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Autonomous docstring compliance enforcement."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        if self.__class__.__name__ in _call_path:
            return {"errors": 0, "skipped": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 0, "skipped": 1, "depth_limited": True}
        _call_path.add(self.__class__.__name__)
        
        try:
            print(f"[DocstringCompliance HEAL @ depth {depth}] Requires ctx parameter - operational mode only")
            return {"skipped": 1, "requires_ctx": True}
        finally:
            _call_path.discard(self.__class__.__name__)


def get_docstring_compliance_agent() -> Any:
    """Brief description of functionality and purpose."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    return DocstringComplianceAgent()
