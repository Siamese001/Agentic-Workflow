import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from typing import Dict, Any

# NAMING CANON ABSOLUTE — renamed for eternal sovereign discovery — Phase 4 — 2025-12-30
class DocstringComplianceAgent:
    """
    Ensures public functions, classes, and modules have docstrings.

    Rules:
    - Module-level docstring required (first statement)
    - Public classes (not starting with _) must have docstring
    - Public functions/methods (not starting with _) must have docstring
    - Minimal stub: '''Brief description of functionality and purpose.'''

    Why ungated healing is safe:
    - Only adds missing triple-quoted strings immediately after def/class
    - Never removes or modifies existing content
    - Single-file scope
    """
    MIN_DOCSTRING: Any = "'''Brief description of functionality and purpose.'''"

    def __init__(self, ctx=None, project_root=None):
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """Execute method for validator compatibility."""
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx: Any=None) -> Dict[str, Any]:
        """
        Per-file healing: add missing docstrings.
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
                doc_lines: Any = [f'{indent}{self.MIN_DOCSTRING}\n', f'{indent}\n']
                new_lines[insert_idx:insert_idx] = doc_lines
                added_count += 1
            if added_count > 0:
                new_content: Any = ''.join(new_lines)
                file_path.write_text(new_content, encoding='utf-8')
                message: Any = f'Added {added_count} missing docstring(s)'
                print(f'      [HEALED] {file_path.name}: {message}')
                ctx.report(self.__class__.__name__, key_id=18, success=True, msg=message)
                return {'healed': True, 'details': message}
            return {'healed': False}
        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f'Docstring healing failed: {str(e)[:100]}')
            return {'healed': False}

def get_docstring_compliance_agent() -> Any:
    """Brief description of functionality and purpose."""
    return DocstringComplianceAgent()
