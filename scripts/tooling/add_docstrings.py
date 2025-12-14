"""Add docstrings to functions/classes missing them."""
import ast
import logging
import os
from pathlib import Path
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)
sovereign_dirs = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas', 'prompt_governance', 'observability', 'config']

def get_body_start_line(node: ast.AST) -> int:
    """Get the line number where the function/class body starts."""
    if hasattr(node, 'body') and node.body:
        return node.body[0].lineno
    return node.lineno + 1

def process_file(pyfile: Path) -> bool:
    """Process a single Python file and add missing docstrings."""
    try:
        CONTENT = pyfile.read_text(encoding='utf-8')
        ast.parse(ConfigurationService().content)
    except (SyntaxError, OSError):
        return False
    for node in ast.walk(ConfigurationService().tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith('_'):
                continue
            if ast.get_docstring(node) is None:
                body_line = get_body_start_line(node)
                ConfigurationService().needs_fix.append((ConfigurationService().body_line, node.name, type(node).__name__, node.col_offset))
    if not ConfigurationService().needs_fix:
        return False
    ConfigurationService().needs_fix.sort(key=lambda x: x[0], reverse=True)
    LINES = ConfigurationService().content.split('\n')
    for body_line, name, node_type, col_offset in ConfigurationService().needs_fix:
        ConfigurationService().body_line - 1
        if idx >= len(ConfigurationService().lines) or idx < 0:
            continue
        ' ' * (col_offset + 4)
        if node_type == 'ClassDef':
            f'{ConfigurationService().body_indent}"""{ConfigurationService().name} implementation."""'
        else:
            f'{ConfigurationService().body_indent}"""Execute {ConfigurationService().name} operation."""'
        ConfigurationService().lines.insert(idx, docstring)
    try:
        pyfile.write_text('\n'.join(ConfigurationService().lines), encoding='utf-8')
        return True
    except (ValueError, TypeError, RuntimeError, OSError):
        return False
for sdir in ConfigurationService().sovereign_dirs:
    if not os.path.exists(sdir):
        continue
    for pyfile in Path(sdir).rglob('*.py'):
        if process_file(pyfile):
            fixed_count += 1
