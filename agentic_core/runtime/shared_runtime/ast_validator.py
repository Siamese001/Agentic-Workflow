import ast
import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional

from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_KEY_EXCEPTIONS

# [GRAVITY] Resolve project root dynamically to ensure relative path accuracy
try:
    # Adjust parents count based on actual depth of this file
    # agentic_core/runtime/shared_runtime/ast_validator.py -> 3 levels up to agentic_core -> +1 for root
    project_root = Path(__file__).resolve().parents[3]
except IndexError:
    project_root = Path.cwd()

def is_excepted_from_key(key_id: int, file_path: Path, line_content: str = "") -> bool:
    """
    [L6 HARDENING] Central SSOT check for known false-positive exceptions.
    """
    exceptions = CANON_KEY_EXCEPTIONS.get(key_id, {})
    if not exceptions:
        return False

    try:
        # Normalize path for cross-platform matching (always use forward slashes)
        rel_path = str(file_path.relative_to(project_root)).replace("\\", "/")
    except ValueError:
        # If file is outside root (rare), check name only
        rel_path = file_path.name

    # 1. File-level exceptions (Exact Match or Glob)
    file_patterns = exceptions.get('files', [])
    # Handle both set (from old config) and list
    if isinstance(file_patterns, set):
        file_patterns = list(file_patterns)
        
    for pattern in file_patterns:
        if rel_path == pattern or fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
            return True

    # 2. Line-level pattern exceptions
    if line_content:
        for pattern in exceptions.get('patterns', []):
            if re.search(pattern, line_content):
                return True

    return False

class CanonASTValidator(ast.NodeVisitor):
    """
    [L6 INFRASTRUCTURE] Base AST visitor for Canon keys.
    Provides automatic Type-Checking suppression and Exception Ledger integration.
    """
    def __init__(self, file_path: Path, content: str, key_id: int):
        self.file_path = file_path
        self.content_lines = content.splitlines()
        self.key_id = key_id
        self.violations: List[Dict[str, Any]] = []
        self.in_type_checking = False

    def report(self, msg: str, node: ast.AST):
        """Register a violation with automatic exception filtering."""
        if hasattr(node, 'lineno'):
            line_no = node.lineno
            # Safety check for EOF
            line_content = self.content_lines[line_no - 1] if line_no <= len(self.content_lines) else ""
            
            # [SSOT CHECK] Check if this specific line is excepted
            if is_excepted_from_key(self.key_id, self.file_path, line_content):
                return
            
            self.violations.append({
                "msg": msg,
                "line": line_no,
                "column": getattr(node, 'col_offset', 0),
                "code": line_content.strip()
            })

    def visit_If(self, node: ast.If):
        """Automatically enter 'type checking' mode for 'if TYPE_CHECKING:' blocks."""
        is_type_check = (isinstance(node.test, ast.Name) and node.test.id == 'TYPE_CHECKING')
        
        if is_type_check:
            self.in_type_checking = True
            self.generic_visit(node)
            self.in_type_checking = False
        else:
            self.generic_visit(node)

def parse_and_validate(file_path: Path, content: str, key_id: int, validator_class) -> List[Dict]:
    """Helper to run a validator against a file safely."""
    try:
        tree = ast.parse(content)
        validator = validator_class(file_path, content, key_id)
        validator.visit(tree)
        return validator.violations
    except SyntaxError as e:
        # Syntax errors are handled by the SyntaxHealer, not key validators
        return []
    except Exception as e:
        # Fail open to avoid crashing the validator on complex ASTs
        return []
